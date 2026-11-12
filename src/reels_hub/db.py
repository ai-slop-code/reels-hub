"""SQLite access and forward-only numbered migrations (spec §18, §21, §23.6; R18, R61).

Times are integer milliseconds and timestamps UTC ISO-8601.
The database lives on /data, never on /media.
"""

import datetime as dt
import re
import sqlite3
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from importlib import resources
from pathlib import Path

from reels_hub.backup import BackupError, write_backup

DEFAULT_DB_PATH = Path("/data/reels-hub.sqlite")
DEFAULT_BACKUP_DIR = Path("/media/_backups/db")

_MIGRATION_FILE = re.compile(r"^(\d{4})_([a-z0-9_]+)\.sql$")
_SCHEMA_VERSION_TABLE = """
CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    applied_at TEXT NOT NULL
)
"""


class MigrationError(RuntimeError):
    """A backup or migration failed. No backup was renamed; a failed migration was rolled back."""


@dataclass(frozen=True)
class Migration:
    version: int
    name: str
    sql: str


@dataclass(frozen=True)
class MigrationResult:
    from_version: int
    to_version: int
    backup: Path | None


def bundled_migrations() -> list[Migration]:
    found = []
    for entry in resources.files("reels_hub.migrations").iterdir():
        match = _MIGRATION_FILE.match(entry.name)
        if match is not None:
            sql = entry.read_text(encoding="utf-8")
            found.append(Migration(int(match.group(1)), match.group(2), sql))
    return ensure_contiguous(found)


def ensure_contiguous(migrations: Iterable[Migration]) -> list[Migration]:
    ordered = sorted(migrations, key=lambda m: m.version)
    numbers = [m.version for m in ordered]
    if numbers != list(range(1, len(numbers) + 1)):
        raise MigrationError(f"migration numbers must be 1, 2, 3 … without gaps; found {numbers}")
    return ordered


def connect(path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(path, isolation_level=None)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    return conn


def migrate(
    db_path: Path,
    backup_dir: Path,
    *,
    migrations: Iterable[Migration] | None = None,
    now: Callable[[], dt.datetime] = lambda: dt.datetime.now(dt.UTC),
) -> MigrationResult:
    available = ensure_contiguous(migrations) if migrations is not None else bundled_migrations()
    latest = available[-1].version if available else 0
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = connect(db_path)
    try:
        conn.execute(_SCHEMA_VERSION_TABLE)
        current = int(
            conn.execute("SELECT COALESCE(MAX(version), 0) FROM schema_version").fetchone()[0]
        )
        pending = [m for m in available if m.version > current]
        if not pending:
            return MigrationResult(current, current, None)
        backup = None
        if current > 0:
            backup = _backup_before_migrating(conn, backup_dir, current, latest, now())
        for migration in pending:
            _apply(conn, migration, now())
        return MigrationResult(current, latest, backup)
    finally:
        conn.close()


def _backup_before_migrating(
    conn: sqlite3.Connection,
    backup_dir: Path,
    from_version: int,
    to_version: int,
    when: dt.datetime,
) -> Path:
    name = f"pre-migrate-{from_version}-{to_version}-{when:%Y%m%d-%H%M}.sqlite"
    try:
        return write_backup(conn, backup_dir, name)
    except BackupError as exc:
        raise MigrationError(f"no migration ran: {exc}") from exc


def _apply(conn: sqlite3.Connection, migration: Migration, when: dt.datetime) -> None:
    script = (
        "BEGIN;\n"
        f"{migration.sql}\n"
        "INSERT INTO schema_version (version, name, applied_at) "
        f"VALUES ({migration.version}, '{migration.name}', '{when.isoformat()}');\n"
        "COMMIT;"
    )
    try:
        conn.executescript(script)
    except sqlite3.Error as exc:
        if conn.in_transaction:
            conn.execute("ROLLBACK")
        raise MigrationError(
            f"migration {migration.version:04d}_{migration.name} failed and was rolled back: {exc}"
        ) from exc
