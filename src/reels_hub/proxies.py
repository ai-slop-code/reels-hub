"""Proxies, contact sheets and single frames (spec §5.1 step 3, §5.1b; R65).

The master is never changed. A proxy is 540 px high at the source aspect, H.264 High CRF 23 with a
keyframe every 0.5 s, the source frame rate and timecode, AAC 128 kbps 48 kHz for every source audio
stream, faststart. A contact sheet has one frame every 2 s. Both are written under the data folder
and renamed into place only when complete.
"""

import math
import subprocess
from collections.abc import Callable
from pathlib import Path

from reels_hub.config import Settings
from reels_hub.jobs import Handler, JobContext

PROXY_KIND = "proxy"
PROXY_HEIGHT = 540
KEYFRAME_SECONDS = 0.5
SHEET_EVERY_SECONDS = 2
SHEET_COLUMNS = 10
SHEET_WIDTH = 160
DEFAULT_FPS = 25.0

Run = Callable[[list[str]], subprocess.CompletedProcess[str]]


class ProxyError(RuntimeError):
    """A proxy, contact sheet or frame couldn't be made."""


def proxy_command(master: Path, out: Path, fps: float, start_tc: str | None) -> list[str]:
    keyint = max(1, round(fps * KEYFRAME_SECONDS))
    command = [
        "ffmpeg",
        "-hide_banner",
        "-loglevel",
        "error",
        "-y",
        "-i",
        str(master),
        "-map",
        "0:v:0",
        "-map",
        "0:a?",
        "-vf",
        f"scale=-2:{PROXY_HEIGHT}",
        "-c:v",
        "libx264",
        "-profile:v",
        "high",
        "-crf",
        "23",
        "-preset",
        "veryfast",
        "-g",
        str(keyint),
        "-sc_threshold",
        "0",
        "-c:a",
        "aac",
        "-b:a",
        "128k",
        "-ar",
        "48000",
        "-movflags",
        "+faststart",
        "-f",
        "mp4",
    ]
    if start_tc:
        command += ["-timecode", start_tc]
    return [*command, str(out)]


def contact_sheet_command(master: Path, out: Path, duration_ms: int | None) -> list[str]:
    frames = max(1, math.ceil((duration_ms or 0) / 1000 / SHEET_EVERY_SECONDS))
    rows = max(1, math.ceil(frames / SHEET_COLUMNS))
    tiles = f"fps=1/{SHEET_EVERY_SECONDS},scale={SHEET_WIDTH}:-2,tile={SHEET_COLUMNS}x{rows}"
    return [
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(master),
        "-vf", tiles, "-frames:v", "1", "-q:v", "5", "-f", "image2", str(out),
    ]  # fmt: skip


def frame_command(master: Path, at_ms: int, out: Path) -> list[str]:
    # The seek comes after the input, so it is frame-accurate (slower than a seek before it).
    return [
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(master),
        "-ss", f"{at_ms / 1000:.3f}", "-frames:v", "1", "-f", "image2", str(out),
    ]  # fmt: skip


def _subprocess_run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, capture_output=True, text=True, check=False)


def _render(run: Run, command: list[str], tmp: Path, final: Path) -> None:
    """Write to `tmp` and rename to `final` only when ffmpeg succeeded."""
    tmp.parent.mkdir(parents=True, exist_ok=True)
    tmp.unlink(missing_ok=True)
    try:
        result = run(command)
        if result.returncode != 0:
            raise ProxyError(f"ffmpeg failed: {result.stderr.strip()[-300:]}")
        tmp.replace(final)
    finally:
        tmp.unlink(missing_ok=True)


def extract_frame(master: Path, at_ms: int, out: Path) -> Path:
    """Write the frame at `at_ms` (integer milliseconds) of the master to `out`."""
    _render(_subprocess_run, frame_command(master, at_ms, _part(out)), _part(out), out)
    return out


def _part(path: Path) -> Path:
    return path.with_name(f"{path.stem}.part{path.suffix}")


def proxy_handler(settings: Settings) -> Handler:
    def handle(ctx: JobContext) -> None:
        clip_id = str(ctx.job.params["clip_id"])
        row = ctx.conn.execute(
            "SELECT rel_path, fps, start_tc, duration_ms FROM clip WHERE id = ?", (clip_id,)
        ).fetchone()
        if row is None:
            raise ProxyError(f"clip {clip_id} is not registered")
        rel, fps, start_tc, duration_ms = row
        master = settings.media.container_path(str(rel))
        if not master.is_file():
            raise ProxyError(f"{rel} is not on disk; its master is offline")

        proxy_rel, sheet_rel = f"proxies/{clip_id}.mp4", f"contact/{clip_id}.jpg"
        proxy = settings.data_dir / proxy_rel
        sheet = settings.data_dir / sheet_rel
        start = str(start_tc) if start_tc else None
        _render(
            ctx.run,
            proxy_command(master, _part(proxy), float(fps or DEFAULT_FPS), start),
            _part(proxy),
            proxy,
        )
        ctx.progress(70)
        _render(
            ctx.run,
            contact_sheet_command(master, _part(sheet), duration_ms),
            _part(sheet),
            sheet,
        )
        ctx.conn.execute(
            "UPDATE clip SET proxy_rel_path = ?, contact_sheet_rel_path = ? WHERE id = ?",
            (proxy_rel, sheet_rel, clip_id),
        )

    return handle
