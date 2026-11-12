"""Database backups: VACUUM INTO, integrity check, then rename (spec §23.6, R61).

Times are UTC. Daily copies are `hub-YYYYMMDD-HHMM.sqlite` (14 kept); copies taken before an
update or migration are `pre-*.sqlite` and are kept.
"""

import datetime as dt
import re
import sqlite3
from pathlib import Path

DAILY_KEEP = 14
_DAILY_NAME = re.compile(r"^hub-(\d{8}-\d{4})\.sqlite$")


class BackupError(RuntimeError):
    """A backup couldn't be written. Nothing was renamed."""


def integrity_check(path: Path) -> str:
    check = sqlite3.connect(path)
    try:
        row = check.execute("PRAGMA integrity_check").fetchone()
    finally:
        check.close()
    return str(row[0])


def write_backup(conn: sqlite3.Connection, backup_dir: Path, name: str) -> Path:
    backup_dir.mkdir(parents=True, exist_ok=True)
    final = backup_dir / name
    if final.exists():
        raise BackupError(f"{name} already exists; wait a minute and try again")
    tmp = final.with_name(name + ".tmp")
    tmp.unlink(missing_ok=True)
    conn.execute("VACUUM INTO ?", (str(tmp),))
    verdict = integrity_check(tmp)
    if verdict != "ok":
        tmp.unlink(missing_ok=True)
        raise BackupError(f"backup failed PRAGMA integrity_check ({verdict}); nothing was renamed")
    tmp.replace(final)
    return final


def daily_name(when: dt.datetime) -> str:
    return f"hub-{when:%Y%m%d-%H%M}.sqlite"


def latest_daily_backup(backup_dir: Path) -> dt.datetime | None:
    if not backup_dir.is_dir():
        return None
    times = []
    for path in backup_dir.iterdir():
        match = _DAILY_NAME.match(path.name)
        if match is not None:
            stamp = dt.datetime.strptime(match.group(1), "%Y%m%d-%H%M")
            times.append(stamp.replace(tzinfo=dt.UTC))
    return max(times, default=None)


def prune_daily(backup_dir: Path, keep: int = DAILY_KEEP) -> list[Path]:
    if not backup_dir.is_dir():
        return []
    daily = sorted(p for p in backup_dir.iterdir() if _DAILY_NAME.match(p.name))
    removed = daily[: max(len(daily) - keep, 0)]
    for path in removed:
        path.unlink()
    return removed
