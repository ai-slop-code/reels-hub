import datetime as dt
import sqlite3
from pathlib import Path

import pytest

from reels_hub import db
from reels_hub.cli import main
from reels_hub.db import Migration, MigrationError, bundled_migrations, connect, migrate

NOW = dt.datetime(2026, 11, 12, 17, 30, tzinfo=dt.UTC)
V1 = Migration(1, "first", "CREATE TABLE a (id INTEGER PRIMARY KEY);")
V2 = Migration(2, "second", "CREATE TABLE b (id INTEGER PRIMARY KEY);")
PHASE0_TABLES = {
    "project",
    "project_media_folder",
    "shoot",
    "take",
    "device",
    "clip",
    "job",
    "agent_log",
    "schema_version",
}


def tables(path: Path) -> set[str]:
    conn = sqlite3.connect(path)
    try:
        rows = conn.execute("SELECT name FROM sqlite_master WHERE type = 'table'").fetchall()
    finally:
        conn.close()
    return {str(row[0]) for row in rows} - {"sqlite_sequence"}


def test_bundled_schema_applies_to_an_empty_db(tmp_path: Path) -> None:
    db_path = tmp_path / "hub.sqlite"
    result = migrate(db_path, tmp_path / "backups", now=lambda: NOW)
    assert (result.from_version, result.to_version, result.backup) == (0, 1, None)
    assert tables(db_path) == PHASE0_TABLES


def test_second_start_is_a_no_op_and_writes_no_backup(tmp_path: Path) -> None:
    db_path, backups = tmp_path / "hub.sqlite", tmp_path / "backups"
    migrate(db_path, backups, now=lambda: NOW)
    result = migrate(db_path, backups, now=lambda: NOW)
    assert (result.from_version, result.to_version, result.backup) == (1, 1, None)
    assert not backups.exists()


def test_backup_is_written_before_a_pending_migration(tmp_path: Path) -> None:
    db_path, backups = tmp_path / "hub.sqlite", tmp_path / "backups"
    migrate(db_path, backups, migrations=[V1], now=lambda: NOW)
    result = migrate(db_path, backups, migrations=[V1, V2], now=lambda: NOW)
    assert result.backup == backups / "pre-migrate-1-2-20261112-1730.sqlite"
    assert result.backup is not None
    assert tables(result.backup) == {"a", "schema_version"}
    assert tables(db_path) == {"a", "b", "schema_version"}
    assert sorted(path.name for path in backups.iterdir()) == [result.backup.name]


def test_failed_integrity_check_renames_nothing_and_migrates_nothing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    db_path, backups = tmp_path / "hub.sqlite", tmp_path / "backups"
    migrate(db_path, backups, migrations=[V1], now=lambda: NOW)
    monkeypatch.setattr(db, "integrity_check", lambda path: "*** corrupt ***")
    with pytest.raises(MigrationError, match="integrity_check"):
        migrate(db_path, backups, migrations=[V1, V2], now=lambda: NOW)
    assert list(backups.iterdir()) == []
    assert tables(db_path) == {"a", "schema_version"}


def test_failing_migration_is_rolled_back(tmp_path: Path) -> None:
    db_path, backups = tmp_path / "hub.sqlite", tmp_path / "backups"
    migrate(db_path, backups, migrations=[V1], now=lambda: NOW)
    broken = Migration(2, "broken", "CREATE TABLE b (id INTEGER); CREATE TABLE a (id INTEGER);")
    with pytest.raises(MigrationError, match="rolled back"):
        migrate(db_path, backups, migrations=[V1, broken], now=lambda: NOW)
    assert tables(db_path) == {"a", "schema_version"}
    result = migrate(db_path, backups, migrations=[V1], now=lambda: NOW)
    assert result.to_version == 1


def test_migration_numbers_must_be_contiguous() -> None:
    with pytest.raises(MigrationError, match="without gaps"):
        db.ensure_contiguous([V1, Migration(3, "skipped", "SELECT 1;")])


def test_bundled_migrations_are_numbered_from_one() -> None:
    assert [(m.version, m.name) for m in bundled_migrations()] == [(1, "phase0")]


def test_connection_enforces_foreign_keys_and_wal(tmp_path: Path) -> None:
    conn = connect(tmp_path / "hub.sqlite")
    try:
        assert conn.execute("PRAGMA foreign_keys").fetchone()[0] == 1
        assert conn.execute("PRAGMA journal_mode").fetchone()[0] == "wal"
    finally:
        conn.close()


def test_fts5_is_available_with_diacritic_folding(tmp_path: Path) -> None:
    conn = connect(tmp_path / "hub.sqlite")
    try:
        conn.execute(
            "CREATE VIRTUAL TABLE t USING fts5(text, tokenize = 'unicode61 remove_diacritics 2')"
        )
        conn.execute("INSERT INTO t (text) VALUES ('lízatko')")
        hits = conn.execute("SELECT count(*) FROM t WHERE t MATCH 'lizatko'").fetchone()[0]
        assert hits == 1
    finally:
        conn.close()


def test_migrate_command_prints_the_schema_change(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    args = ["migrate", "--db", str(tmp_path / "hub.sqlite"), "--backup-dir", str(tmp_path / "b")]
    assert main(args) == 0
    assert capsys.readouterr().out.splitlines() == ["schema 0 -> 1"]
