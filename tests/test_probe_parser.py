import json
from pathlib import Path
from typing import Any

from reels_hub.probe import parse_ffprobe

FIXTURES = Path(__file__).parent / "fixtures" / "ffprobe"


def load(name: str) -> dict[str, Any]:
    data: dict[str, Any] = json.loads((FIXTURES / name).read_text(encoding="utf-8"))
    return data


def test_sony_clip_facts_come_from_ffprobe() -> None:
    result = parse_ffprobe(load("sony_c0001.json"))
    assert result.duration_ms == 4000
    assert (result.video_codec, result.width, result.height) == ("h264", 960, 540)
    assert result.fps == 25.0
    assert result.audio_channels == 2
    assert result.camera == "Sony ILME-FX30"
    assert result.start_tc == "10:00:00:00"
    assert result.color_transfer is None
    assert result.flags == {"vfr": False, "hdr_log": False}


def test_a_variable_frame_rate_clip_is_flagged_vfr() -> None:
    result = parse_ffprobe(load("phone_vfr_0006.json"))
    assert result.vfr is True
    assert result.flags == {"vfr": True, "hdr_log": False}
    assert result.camera == "Apple iPhone"


def test_an_hlg_clip_is_flagged_as_hdr_or_log() -> None:
    result = parse_ffprobe(load("sony_c0005_hlg.json"))
    assert result.color_transfer == "arib-std-b67"
    assert result.hdr_log is True
    assert result.flags == {"vfr": False, "hdr_log": True}


def test_missing_fields_give_empty_facts_not_errors() -> None:
    result = parse_ffprobe({})
    assert result.duration_ms is None
    assert result.fps is None
    assert result.camera is None
    assert result.flags == {"vfr": False, "hdr_log": False}


def test_zero_frame_rates_are_not_compared() -> None:
    data = {"streams": [{"codec_type": "video", "r_frame_rate": "0/0", "avg_frame_rate": "25/1"}]}
    result = parse_ffprobe(data)
    assert result.fps is None
    assert result.vfr is False
