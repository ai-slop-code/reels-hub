import datetime as dt
import shutil
import sqlite3
from collections.abc import Iterator
from pathlib import Path

import pytest

from reels_hub.config import Settings
from reels_hub.db import connect, migrate
from reels_hub.paths import MEDIA_MARKER
from reels_hub.projects import add_project_folder
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


@pytest.fixture
def watcher(settings: Settings) -> Watcher:
    return Watcher(settings)


def put(settings: Settings, src: Path, rel: str) -> Path:
    target = settings.media_root / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, target)
    return target


def settle(watcher: Watcher, conn: sqlite3.Connection, start: dt.datetime):  # type: ignore[no-untyped-def]
    watcher.scan(conn, start)
    return watcher.scan(conn, start + dt.timedelta(seconds=10))


def clips(conn: sqlite3.Connection) -> list[tuple[str, str, str]]:
    rows = conn.execute("SELECT id, rel_path, availability FROM clip ORDER BY id").fetchall()
    return [(str(a), str(b), str(c)) for a, b, c in rows]


def test_a_file_is_registered_only_after_two_polls_ten_seconds_apart(
    settings: Settings, conn: sqlite3.Connection, watcher: Watcher
) -> None:
    put(settings, fixture("sony/C0001.MP4"), "giro00/raw/sony/C0001.MP4")
    assert watcher.scan(conn, T0).registered == []
    assert watcher.scan(conn, T0 + dt.timedelta(seconds=5)).registered == []
    assert watcher.scan(conn, T0 + dt.timedelta(seconds=10)).registered == [
        "giro00/raw/sony/C0001.MP4"
    ]


def test_a_file_that_is_still_growing_restarts_the_wait(
    settings: Settings, conn: sqlite3.Connection, watcher: Watcher
) -> None:
    target = put(settings, fixture("sony/C0001.MP4"), "giro00/raw/sony/C0001.MP4")
    watcher.scan(conn, T0)
    with target.open("ab") as handle:
        handle.write(b"\0" * 10)
    assert watcher.scan(conn, T0 + dt.timedelta(seconds=10)).registered == []
    assert watcher.scan(conn, T0 + dt.timedelta(seconds=15)).registered == []
    assert watcher.scan(conn, T0 + dt.timedelta(seconds=20)).registered == [
        "giro00/raw/sony/C0001.MP4"
    ]


def test_ignored_names_are_never_registered(
    settings: Settings, conn: sqlite3.Connection, watcher: Watcher
) -> None:
    src = fixture("sony/C0001.MP4")
    for name in ("._C0001.MP4", ".C0002.MP4", "C0003.MP4.part", "C0004.MP4.download", ".DS_Store"):
        put(settings, src, f"giro00/raw/sony/{name}")
    report = settle(watcher, conn, T0)
    assert report.registered == []
    assert clips(conn) == []


def test_a_registered_clip_keeps_its_facts_and_the_recording_day(
    settings: Settings, conn: sqlite3.Connection, watcher: Watcher
) -> None:
    put(settings, fixture("sony/C0001.MP4"), "giro00/raw/sony/C0001.MP4")
    settle(watcher, conn, T0)
    row = conn.execute(
        "SELECT id, rel_path, duration_ms, fps, camera, start_tc, flags, shoot_id, availability, "
        "hash, volume_id FROM clip"
    ).fetchone()
    assert row[0] == "giro00-sony-c0001"
    assert row[1] == "giro00/raw/sony/C0001.MP4"
    assert abs(row[2] - 4000) < 100
    assert (row[3], row[4], row[5]) == (25.0, "Sony ILME-FX30", "10:00:00:00")
    assert row[6] == '{"hdr_log": false, "vfr": false}'
    assert (row[7], row[8]) == ("giro00-2026-11-12", "online")
    assert row[9] and row[10]
    shoot = conn.execute("SELECT project_id, recorded_on FROM shoot").fetchall()
    assert shoot == [("giro00", "2026-11-12")]


def test_a_variable_frame_rate_phone_clip_is_flagged(
    settings: Settings, conn: sqlite3.Connection, watcher: Watcher
) -> None:
    put(settings, fixture("phone/VFR_0006.MOV"), "giro00/raw/phone/VFR_0006.MOV")
    settle(watcher, conn, T0)
    flags = conn.execute("SELECT flags FROM clip").fetchone()[0]
    assert '"vfr": true' in flags


def test_a_moved_file_is_reattached_and_not_registered_twice(
    settings: Settings, conn: sqlite3.Connection, watcher: Watcher
) -> None:
    target = put(settings, fixture("sony/C0001.MP4"), "giro00/raw/sony/C0001.MP4")
    settle(watcher, conn, T0)
    target.rename(settings.media_root / "giro00/raw/sony/RENAMED.MP4")
    later = T0 + dt.timedelta(seconds=20)
    settle(watcher, conn, later)
    assert clips(conn) == [("giro00-sony-c0001", "giro00/raw/sony/RENAMED.MP4", "online")]


def test_a_copy_of_a_known_clip_is_reported_as_a_duplicate(
    settings: Settings, conn: sqlite3.Connection, watcher: Watcher
) -> None:
    put(settings, fixture("sony/C0001.MP4"), "giro00/raw/sony/C0001.MP4")
    settle(watcher, conn, T0)
    put(settings, fixture("sony/C0001.MP4"), "giro00/raw/sony/copy.MP4")
    report = settle(watcher, conn, T0 + dt.timedelta(seconds=20))
    assert report.duplicates == ["giro00/raw/sony/copy.MP4 is a copy of giro00/raw/sony/C0001.MP4"]
    assert [row[1] for row in clips(conn)] == ["giro00/raw/sony/C0001.MP4"]


def test_a_missing_clip_goes_offline_and_comes_back_online(
    settings: Settings, conn: sqlite3.Connection, watcher: Watcher
) -> None:
    target = put(settings, fixture("sony/C0001.MP4"), "giro00/raw/sony/C0001.MP4")
    settle(watcher, conn, T0)
    target.unlink()
    assert watcher.scan(conn, T0 + dt.timedelta(seconds=20)).offline == [
        "giro00/raw/sony/C0001.MP4"
    ]
    assert clips(conn)[0][2] == "offline"
    put(settings, fixture("sony/C0001.MP4"), "giro00/raw/sony/C0001.MP4")
    assert watcher.scan(conn, T0 + dt.timedelta(seconds=30)).online == ["giro00/raw/sony/C0001.MP4"]
    assert clips(conn)[0][2] == "online"


def test_dji_lrf_and_wav_attach_to_the_video_and_are_not_clips(
    settings: Settings, conn: sqlite3.Connection, watcher: Watcher
) -> None:
    base = "DJI_20261112120000_0001_D"
    for suffix in (".MP4", ".LRF", ".WAV"):
        put(settings, fixture(f"dji/{base}{suffix}"), f"giro00/raw/dji/{base}{suffix}")
    settle(watcher, conn, T0)
    rows = conn.execute("SELECT rel_path, alt_audio_rel_path, lrf_rel_path FROM clip").fetchall()
    assert rows == [
        (
            f"giro00/raw/dji/{base}.MP4",
            f"giro00/raw/dji/{base}.WAV",
            f"giro00/raw/dji/{base}.LRF",
        )
    ]


def test_nothing_is_registered_or_marked_offline_while_the_marker_is_missing(
    settings: Settings, conn: sqlite3.Connection, watcher: Watcher
) -> None:
    target = put(settings, fixture("sony/C0001.MP4"), "giro00/raw/sony/C0001.MP4")
    settle(watcher, conn, T0)
    (settings.media_root / MEDIA_MARKER).unlink()
    target.unlink()
    report = watcher.scan(conn, T0 + dt.timedelta(seconds=20))
    assert report.paused is True
    assert report.offline == []
    assert clips(conn)[0][2] == "online"
