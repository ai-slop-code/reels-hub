"""Checks the proxy's properties inside the test image (spec §5.1 step 3, R65)."""

import datetime as dt
import shutil
import subprocess
from pathlib import Path

import pytest

from reels_hub.config import Settings
from reels_hub.db import connect, migrate
from reels_hub.jobs import Worker
from reels_hub.probe import probe
from reels_hub.projects import add_project_folder
from reels_hub.proxies import PROXY_KIND, extract_frame, proxy_handler
from reels_hub.watcher import Watcher

pytestmark = pytest.mark.container

T0 = dt.datetime(2026, 11, 12, 18, 0, tzinfo=dt.UTC)
GENERATED = Path(__file__).parent / "fixtures" / "generated" / "giro00" / "raw"


@pytest.fixture
def proxy(settings: Settings) -> Path:
    source = GENERATED / "sony" / "C0001.MP4"
    assert source.is_file(), "run `make fixtures` first"
    migrate(settings.db_path, settings.backup_dir, now=lambda: T0)
    conn = connect(settings.db_path)
    add_project_folder(conn, "giro00", "giro00/raw", T0)
    target = settings.media_root / "giro00/raw/sony/C0001.MP4"
    target.parent.mkdir(parents=True)
    shutil.copy2(source, target)
    watcher = Watcher(settings)
    watcher.scan(conn, T0)
    watcher.scan(conn, T0 + dt.timedelta(seconds=10))
    Worker(
        settings.db_path,
        settings.backup_dir,
        handlers={PROXY_KIND: proxy_handler(settings)},
        clock=lambda: T0,
    ).run_once(connect(settings.db_path))
    conn.close()
    return settings.data_dir / "proxies" / "giro00-sony-c0001.mp4"


def ffprobe_json(path: Path) -> str:
    command = ["ffprobe", "-v", "error", "-print_format", "json", "-show_format", "-show_streams"]
    result = subprocess.run([*command, str(path)], capture_output=True, text=True, check=True)
    return result.stdout


def test_proxy_is_540_high_at_the_source_aspect(proxy: Path) -> None:
    facts = probe(proxy)
    assert facts.height == 540
    assert facts.width == 960
    assert facts.video_codec == "h264"
    assert facts.fps == 25.0


def test_proxy_has_a_keyframe_about_every_half_second(proxy: Path) -> None:
    command = ["ffprobe", "-v", "error", "-select_streams", "v:0", "-skip_frame", "nokey"]
    command += ["-show_entries", "frame=pts_time", "-of", "csv=p=0"]
    result = subprocess.run([*command, str(proxy)], capture_output=True, text=True, check=True)
    times = [float(line.strip(",")) for line in result.stdout.split()]
    gaps = [later - earlier for earlier, later in zip(times, times[1:], strict=False)]
    assert len(times) >= 6
    assert all(0.45 <= gap <= 0.55 for gap in gaps)


def test_proxy_keeps_every_audio_channel_as_aac_48k(proxy: Path) -> None:
    facts = probe(proxy)
    assert facts.audio_channels == 2
    assert '"codec_name": "aac"' in ffprobe_json(proxy)
    assert '"sample_rate": "48000"' in ffprobe_json(proxy)


def test_proxy_keeps_the_timecode(proxy: Path) -> None:
    assert probe(proxy).start_tc == "10:00:00:00"


def test_proxy_is_faststart(proxy: Path) -> None:
    data = proxy.read_bytes()
    assert data.index(b"moov") < data.index(b"mdat")


def test_contact_sheet_and_single_frame_are_images(proxy: Path, settings: Settings) -> None:
    sheet = settings.data_dir / "contact" / "giro00-sony-c0001.jpg"
    assert sheet.read_bytes()[:2] == b"\xff\xd8"
    frame = extract_frame(
        settings.media_root / "giro00/raw/sony/C0001.MP4", 1000, settings.data_dir / "frame.jpg"
    )
    assert frame.read_bytes()[:2] == b"\xff\xd8"
