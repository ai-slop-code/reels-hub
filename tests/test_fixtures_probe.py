"""Probes every generated fixture inside the image (spec §24.2). See make_fixtures.sh."""

from pathlib import Path

import pytest

from reels_hub.probe import probe

pytestmark = pytest.mark.container

RAW = Path(__file__).parent / "fixtures" / "generated" / "giro00" / "raw"


def clip(name: str) -> Path:
    matches = list(RAW.rglob(name))
    assert len(matches) == 1, f"fixture {name} missing; run tests/fixtures/make_fixtures.sh"
    return matches[0]


def test_every_fixture_is_under_five_megabytes() -> None:
    files = [path for path in RAW.rglob("*") if path.is_file()]
    assert len(files) >= 10
    assert all(path.stat().st_size < 5_000_000 for path in files)


def test_sony_clip_is_540p_25p_stereo_with_timecode() -> None:
    result = probe(clip("C0001.MP4"))
    assert result.duration_ms is not None and abs(result.duration_ms - 4000) < 100
    assert (result.width, result.height) == (960, 540)
    assert result.fps == 25.0
    assert result.audio_channels == 2
    assert result.start_tc == "10:00:00:00"
    assert result.camera == "Sony ILME-FX30"
    assert result.flags == {"vfr": False, "hdr_log": False}


def test_fifty_p_clip_reports_50_fps() -> None:
    assert probe(clip("C0002.MP4")).fps == 50.0


def test_dji_clip_has_camera_metadata_and_sidecars_next_to_it() -> None:
    main = clip("DJI_20261112120000_0001_D.MP4")
    assert probe(main).camera == "DJI Osmo_Action_5_Pro"
    assert clip("DJI_20261112120000_0001_D.LRF").stat().st_size > 0
    assert clip("DJI_20261112120000_0001_D.WAV").stat().st_size > 0


def test_phone_clip_is_flagged_variable_frame_rate() -> None:
    result = probe(clip("VFR_0006.MOV"))
    assert result.vfr is True
    assert result.flags["vfr"] is True


def test_hlg_clip_is_flagged_hdr_log() -> None:
    result = probe(clip("C0005.MP4"))
    assert result.color_transfer == "arib-std-b67"
    assert result.flags["hdr_log"] is True


def test_4k_hevc_clip_is_two_seconds() -> None:
    result = probe(clip("C0007.MP4"))
    assert (result.video_codec, result.width, result.height) == ("hevc", 3840, 2160)
    assert result.duration_ms is not None and abs(result.duration_ms - 2000) < 100
