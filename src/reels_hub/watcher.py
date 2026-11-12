"""Polling watcher for the media folders (spec §5.1, §23.2, §23.4; R27, R62).

A file is registered only when its size and mtime are unchanged across two polls at least
`stable_seconds` apart and ffprobe can read it. A file that moved is re-attached by hash and
duration; a copy of a known clip is reported as a duplicate. Clips whose file is gone are marked
offline. While the media marker is missing the watcher does nothing and marks nothing offline.
DJI `.LRF` and `.WAV` files next to a video are attached to it, not registered on their own.
"""

import datetime as dt
import json
import re
import sqlite3
from dataclasses import dataclass, field
from pathlib import Path

import xxhash

from reels_hub.config import Settings
from reels_hub.jobs import JobContext, enqueue
from reels_hub.probe import ProbeError, ProbeResult, probe
from reels_hub.proxies import PROXY_KIND

SCAN_KIND = "scan"
STABLE_SECONDS = 10.0
HASH_CHUNK = 1024 * 1024
VIDEO_SUFFIXES = frozenset({".mp4", ".mov", ".m4v"})
AUDIO_SUFFIXES = frozenset({".wav"})
PROXY_SUFFIXES = frozenset({".lrf"})
_RECORDED_DATE = re.compile(r"^(\d{4}-\d{2}-\d{2})")


def is_ignored(name: str) -> bool:
    return name.startswith(".") or name.endswith((".download", ".part"))


def file_digest(path: Path) -> str:
    """xxh3 over the first 1 MiB, the last 1 MiB and the size (spec §5.1 step 1)."""
    size = path.stat().st_size
    digest = xxhash.xxh3_64()
    with path.open("rb") as handle:
        digest.update(handle.read(HASH_CHUNK))
        if size > HASH_CHUNK:
            handle.seek(max(size - HASH_CHUNK, HASH_CHUNK))
            digest.update(handle.read(HASH_CHUNK))
    digest.update(str(size).encode("ascii"))
    return digest.hexdigest()


def slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def _sibling(path: Path, suffixes: frozenset[str]) -> Path | None:
    for other in path.parent.iterdir():
        if (
            other != path
            and other.stem.lower() == path.stem.lower()
            and other.suffix.lower() in suffixes
        ):
            return other
    return None


def _shoot_day(recorded_at: str | None, path: Path) -> str:
    match = _RECORDED_DATE.match(recorded_at or "")
    if match is not None:
        return match.group(1)
    return dt.datetime.fromtimestamp(path.stat().st_mtime, dt.UTC).date().isoformat()


def _folder_name(rel: str) -> str:
    parts = rel.split("/")
    if "raw" in parts and parts.index("raw") + 1 < len(parts) - 1:
        return parts[parts.index("raw") + 1]
    return parts[-2] if len(parts) > 1 else "media"


@dataclass
class _Seen:
    size: int
    mtime_ns: int
    since: dt.datetime


@dataclass
class ScanReport:
    paused: bool = False
    registered: list[str] = field(default_factory=list)
    moved: list[str] = field(default_factory=list)
    duplicates: list[str] = field(default_factory=list)
    offline: list[str] = field(default_factory=list)
    online: list[str] = field(default_factory=list)


class Watcher:
    def __init__(self, settings: Settings, *, stable_seconds: float = STABLE_SECONDS) -> None:
        self.settings = settings
        self._stable = dt.timedelta(seconds=stable_seconds)
        self._seen: dict[str, _Seen] = {}

    def handle(self, ctx: JobContext) -> None:
        self.scan(ctx.conn, ctx.now())

    def scan(self, conn: sqlite3.Connection, now: dt.datetime) -> ScanReport:
        report = ScanReport()
        if not self.settings.marker_path.is_file():
            report.paused = True
            return report
        volume = str(self.settings.media_root.stat().st_dev)
        folders = conn.execute(
            "SELECT project_id, rel_path FROM project_media_folder ORDER BY project_id, rel_path"
        ).fetchall()
        for project_id, folder in folders:
            root = self.settings.media.container_path(folder)
            if not root.is_dir():
                continue
            for path in sorted(root.rglob("*")):
                if not path.is_file() or is_ignored(path.name):
                    continue
                if path.suffix.lower() in VIDEO_SUFFIXES | AUDIO_SUFFIXES:
                    self._consider(conn, str(project_id), path, now, volume, report)
        self._update_availability(conn, [str(folder) for _, folder in folders], now, report)
        return report

    def _consider(
        self,
        conn: sqlite3.Connection,
        project_id: str,
        path: Path,
        now: dt.datetime,
        volume: str,
        report: ScanReport,
    ) -> None:
        rel = self.settings.media.relative(path)
        if conn.execute("SELECT 1 FROM clip WHERE rel_path = ?", (rel,)).fetchone() is not None:
            return
        if path.suffix.lower() in AUDIO_SUFFIXES and _sibling(path, VIDEO_SUFFIXES) is not None:
            return
        stat = path.stat()
        key = str(path)
        seen = self._seen.get(key)
        if seen is None or seen.size != stat.st_size or seen.mtime_ns != stat.st_mtime_ns:
            self._seen[key] = _Seen(stat.st_size, stat.st_mtime_ns, now)
            return
        if now - seen.since < self._stable:
            return
        try:
            facts = probe(path)
        except ProbeError:
            return
        del self._seen[key]
        self._register(conn, project_id, rel, path, facts, now, volume, report)

    def _register(
        self,
        conn: sqlite3.Connection,
        project_id: str,
        rel: str,
        path: Path,
        facts: ProbeResult,
        now: dt.datetime,
        volume: str,
        report: ScanReport,
    ) -> None:
        stamp = now.astimezone(dt.UTC).isoformat()
        digest = file_digest(path)
        known = conn.execute(
            "SELECT id, rel_path FROM clip WHERE hash = ? AND duration_ms IS ?",
            (digest, facts.duration_ms),
        ).fetchall()
        for clip_id, old_rel in known:
            if self.settings.media.container_path(old_rel).exists():
                report.duplicates.append(f"{rel} is a copy of {old_rel}")
                return
            conn.execute(
                "UPDATE clip SET rel_path = ?, availability = 'online', volume_id = ?, "
                "updated_at = ? WHERE id = ?",
                (rel, volume, stamp, clip_id),
            )
            report.moved.append(f"{old_rel} -> {rel}")
            return

        day = _shoot_day(facts.recorded_at, path)
        shoot_id = f"{project_id}-{day}"
        conn.execute(
            "INSERT OR IGNORE INTO shoot (id, project_id, recorded_on, created_at) "
            "VALUES (?, ?, ?, ?)",
            (shoot_id, project_id, day, stamp),
        )
        wav = _sibling(path, AUDIO_SUFFIXES)
        lrf = _sibling(path, PROXY_SUFFIXES)
        columns = (
            "id, rel_path, size_bytes, hash, origin, availability, volume_id, shoot_id, camera, "
            "duration_ms, fps, width, height, audio_channels, color_transfer, start_tc, flags, "
            "alt_audio_rel_path, lrf_rel_path, recorded_at, created_at, updated_at"
        )
        clip_id = self._new_clip_id(conn, project_id, rel, path)
        values = (
            clip_id,
            rel,
            path.stat().st_size,
            digest,
            "own",
            "online",
            volume,
            shoot_id,
            facts.camera,
            facts.duration_ms,
            facts.fps,
            facts.width,
            facts.height,
            facts.audio_channels,
            facts.color_transfer,
            facts.start_tc,
            json.dumps(facts.flags, sort_keys=True),
            self.settings.media.relative(wav) if wav is not None else None,
            self.settings.media.relative(lrf) if lrf is not None else None,
            facts.recorded_at,
            stamp,
            stamp,
        )
        placeholders = ", ".join("?" * len(values))
        conn.execute(f"INSERT INTO clip ({columns}) VALUES ({placeholders})", values)
        enqueue(conn, PROXY_KIND, now, {"clip_id": clip_id})
        report.registered.append(rel)

    def _new_clip_id(self, conn: sqlite3.Connection, project_id: str, rel: str, path: Path) -> str:
        base = slug(f"{project_id}-{_folder_name(rel)}-{path.stem}")
        candidate, number = base, 2
        while conn.execute("SELECT 1 FROM clip WHERE id = ?", (candidate,)).fetchone() is not None:
            candidate = f"{base}-{number}"
            number += 1
        return candidate

    def _update_availability(
        self, conn: sqlite3.Connection, folders: list[str], now: dt.datetime, report: ScanReport
    ) -> None:
        stamp = now.astimezone(dt.UTC).isoformat()
        for clip_id, rel, status in conn.execute(
            "SELECT id, rel_path, availability FROM clip"
        ).fetchall():
            if not any(rel.startswith(f"{folder}/") for folder in folders):
                continue
            present = self.settings.media.container_path(rel).exists()
            if present and status == "offline":
                conn.execute(
                    "UPDATE clip SET availability = 'online', updated_at = ? WHERE id = ?",
                    (stamp, clip_id),
                )
                report.online.append(rel)
            elif not present and status == "online":
                conn.execute(
                    "UPDATE clip SET availability = 'offline', updated_at = ? WHERE id = ?",
                    (stamp, clip_id),
                )
                report.offline.append(rel)
