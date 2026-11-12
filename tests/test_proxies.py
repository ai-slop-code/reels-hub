import datetime as dt
import shutil
import sqlite3
from collections.abc import Iterator
from pathlib import Path

import pytest

from reels_hub.config import Settings
from reels_hub.db import connect, migrate
from reels_hub.jobs import Worker
from reels_hub.projects import add_project_folder
from reels_hub.proxies import (
    PROXY_KIND,
    contact_sheet_command,
    proxy_command,
    proxy_handler,
)
from reels_hub.watcher import Watcher

T0 = dt.datetime(2026, 11, 12, 18, 0, tzinfo=dt.UTC)
GENERATED = Path(__file__).parent / "fixtures" / "generated" / "giro00" / "raw"


def fixture(rel: str) -> Path:
    path = GENERATED / rel
    assert path.is_file(), f"{rel} is missing; run `make fixtures` first"
    return path


@pytest.fixture
def conn(settings: Settings) -> Iterator[sqlite3.Connection]:
    migrate(settings.db_path, settings.backup_dir, now=lambda: T0)
    database = connect(settings.db_path)
    add_project_folder(database, "giro00", "giro00/raw", T0)
    yield database
    database.close()


def register_c0001(settings: Settings, conn: sqlite3.Connection) -> str:
    target = settings.media_root / "giro00/raw/sony/C0001.MP4"
    target.parent.mkdir(parents=True)
    shutil.copy2(fixture("sony/C0001.MP4"), target)
    watcher = Watcher(settings)
    watcher.scan(conn, T0)
    watcher.scan(conn, T0 + dt.timedelta(seconds=10))
    return "giro00-sony-c0001"


def proxy_worker(settings: Settings) -> Worker:
    return Worker(
        settings.db_path,
        settings.backup_dir,
        handlers={PROXY_KIND: proxy_handler(settings)},
        clock=lambda: T0,
    )


def test_proxy_uses_the_spec_settings() -> None:
    command = proxy_command(Path("/m.MP4"), Path("/d/p.part.mp4"), 25.0, "10:00:00:00")
    joined = " ".join(command)
    assert "scale=-2:540" in joined
    assert "-profile:v high -crf 23" in joined
    assert "-g 12" in joined
    assert "-sc_threshold 0" in joined
    assert "force_key_frames" not in joined
    assert "-b:a 128k -ar 48000" in joined
    assert "-movflags +faststart" in joined
    assert "-timecode 10:00:00:00" in joined
    assert "-ac" not in command


def test_proxy_without_a_timecode_writes_none() -> None:
    assert "-timecode" not in proxy_command(Path("/m.MP4"), Path("/o.mp4"), 50.0, None)


@pytest.mark.parametrize(("duration_ms", "rows"), [(2000, 1), (4000, 1), (125_000, 7)])
def test_contact_sheet_grid_covers_one_frame_every_two_seconds(duration_ms: int, rows: int) -> None:
    command = contact_sheet_command(Path("/m.MP4"), Path("/o.jpg"), duration_ms)
    assert f"tile=10x{rows}" in command[command.index("-vf") + 1]


def test_the_job_writes_the_proxy_and_sheet_and_records_their_paths(
    settings: Settings, conn: sqlite3.Connection
) -> None:
    clip_id = register_c0001(settings, conn)
    assert proxy_worker(settings).run_once(connect(settings.db_path)) is True
    row = conn.execute(
        "SELECT proxy_rel_path, contact_sheet_rel_path FROM clip WHERE id = ?", (clip_id,)
    ).fetchone()
    assert row == (f"proxies/{clip_id}.mp4", f"contact/{clip_id}.jpg")
    assert (settings.data_dir / row[0]).stat().st_size > 0
    assert (settings.data_dir / row[1]).stat().st_size > 0
    assert list(settings.data_dir.rglob("*.part*")) == []


def test_a_failed_proxy_job_leaves_no_partial_file(
    settings: Settings, conn: sqlite3.Connection
) -> None:
    register_c0001(settings, conn)
    (settings.media_root / "giro00/raw/sony/C0001.MP4").unlink()
    proxy_worker(settings).run_once(connect(settings.db_path))
    status, error = conn.execute(
        "SELECT status, error FROM job WHERE kind = ?", (PROXY_KIND,)
    ).fetchone()
    assert status == "failed"
    assert "offline" in error
    assert list(settings.data_dir.rglob("*.part*")) == []
