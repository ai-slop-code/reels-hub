"""The /health report (spec §23.3, R66). It returns 503 only if the DB can't be opened or the media
marker is missing; low disk space is reported, never a failure."""

import shutil
import sqlite3
from pathlib import Path
from typing import Any

from reels_hub import __version__
from reels_hub.config import Settings
from reels_hub.jobs import job_counts


def health_report(settings: Settings) -> tuple[int, dict[str, Any]]:
    schema = _schema_version(settings.db_path)
    mounted = settings.marker_path.is_file()
    healthy = schema is not None and mounted
    body: dict[str, Any] = {
        "status": "ok" if healthy else "unavailable",
        "version": __version__,
        "git_sha": settings.git_sha,
        "schema_version": schema,
        "media_mounted": mounted,
        "media_free_gb": _free_gb(settings.media_root),
        "data_free_gb": _free_gb(settings.data_dir),
        "jobs": _jobs(settings.db_path) if schema is not None else None,
    }
    return (200 if healthy else 503), body


def _open_read_only(path: Path) -> sqlite3.Connection | None:
    try:
        return sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    except sqlite3.Error:
        return None


def _schema_version(path: Path) -> int | None:
    conn = _open_read_only(path)
    if conn is None:
        return None
    try:
        return int(
            conn.execute("SELECT COALESCE(MAX(version), 0) FROM schema_version").fetchone()[0]
        )
    except sqlite3.Error:
        return None
    finally:
        conn.close()


def _jobs(path: Path) -> dict[str, int] | None:
    conn = _open_read_only(path)
    if conn is None:
        return None
    try:
        return job_counts(conn)
    except sqlite3.Error:
        return None
    finally:
        conn.close()


def _free_gb(path: Path) -> float | None:
    if not path.exists():
        return None
    return round(shutil.disk_usage(path).free / 1e9, 1)
