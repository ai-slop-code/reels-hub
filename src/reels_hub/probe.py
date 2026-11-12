"""ffprobe wrapper: the facts ingest needs about a clip (spec §5.1 step 2, R69, R70).

Flags never block: `vfr` (variable frame rate, typical for phones) and `hdr_log` (HDR or Log
transfer). The fps-mismatch flag needs a reel and comes with 9.3.
"""

import json
import subprocess
from collections.abc import Mapping
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Any

HDR_OR_LOG_TRANSFERS = frozenset({"arib-std-b67", "smpte2084"})
MAKE_TAGS = ("com.apple.quicktime.make", "make")
MODEL_TAGS = ("com.apple.quicktime.model", "model")


class ProbeError(RuntimeError):
    """ffprobe failed or could not read the file."""


@dataclass(frozen=True)
class ProbeResult:
    duration_ms: int | None
    video_codec: str | None
    width: int | None
    height: int | None
    fps: float | None
    vfr: bool
    audio_channels: int | None
    camera: str | None
    start_tc: str | None
    color_transfer: str | None

    @property
    def hdr_log(self) -> bool:
        return self.color_transfer in HDR_OR_LOG_TRANSFERS

    @property
    def flags(self) -> dict[str, bool]:
        return {"vfr": self.vfr, "hdr_log": self.hdr_log}


def probe(path: Path) -> ProbeResult:
    args = [
        "ffprobe",
        "-v",
        "error",
        "-print_format",
        "json",
        "-show_format",
        "-show_streams",
        str(path),
    ]
    result = subprocess.run(args, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise ProbeError(f"ffprobe could not read {path.name}: {result.stderr.strip()}")
    return parse_ffprobe(json.loads(result.stdout))


def parse_ffprobe(data: Mapping[str, Any]) -> ProbeResult:
    streams = [s for s in data.get("streams", []) if isinstance(s, dict)]
    fmt = data.get("format") or {}
    fmt_tags = _tags(fmt)
    video = _first(streams, "video")
    audio = _first(streams, "audio")
    timecode_stream = next((s for s in streams if s.get("codec_tag_string") == "tmcd"), None)

    frame_rate = _fraction(video.get("r_frame_rate")) if video else None
    average_rate = _fraction(video.get("avg_frame_rate")) if video else None
    vfr = frame_rate is not None and average_rate is not None and frame_rate != average_rate
    return ProbeResult(
        duration_ms=_duration_ms(fmt.get("duration")),
        video_codec=_str(video.get("codec_name")) if video else None,
        width=_int(video.get("width")) if video else None,
        height=_int(video.get("height")) if video else None,
        fps=float(frame_rate) if frame_rate is not None else None,
        vfr=vfr,
        audio_channels=_int(audio.get("channels")) if audio else None,
        camera=_camera(fmt_tags, _tags(video) if video else {}),
        start_tc=_timecode(fmt_tags, video, timecode_stream),
        color_transfer=_str(video.get("color_transfer")) if video else None,
    )


def _first(streams: list[dict[str, Any]], codec_type: str) -> dict[str, Any] | None:
    return next((s for s in streams if s.get("codec_type") == codec_type), None)


def _tags(obj: Mapping[str, Any] | None) -> dict[str, str]:
    raw = (obj or {}).get("tags") or {}
    return {str(k): str(v) for k, v in raw.items()} if isinstance(raw, dict) else {}


def _fraction(text: Any) -> Fraction | None:
    try:
        value = Fraction(str(text))
    except (ValueError, ZeroDivisionError):
        return None
    return value if value > 0 else None


def _duration_ms(text: Any) -> int | None:
    try:
        return round(float(text) * 1000)
    except (TypeError, ValueError):
        return None


def _int(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _str(value: Any) -> str | None:
    return str(value) if value not in (None, "") else None


def _camera(*tag_sets: Mapping[str, str]) -> str | None:
    make = _find(tag_sets, MAKE_TAGS)
    model = _find(tag_sets, MODEL_TAGS)
    if make and model and not model.lower().startswith(make.lower()):
        return f"{make} {model}"
    return model or make


def _timecode(
    fmt: Mapping[str, str], video: dict[str, Any] | None, timecode_stream: dict[str, Any] | None
) -> str | None:
    candidates = [fmt, _tags(video), _tags(timecode_stream)]
    return _find(candidates, ("timecode",))


def _find(tag_sets: Any, keys: tuple[str, ...]) -> str | None:
    for tags in tag_sets:
        for key in keys:
            value = tags.get(key)
            if value:
                return str(value)
    return None
