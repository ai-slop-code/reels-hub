"""In-image checks: run inside the test stage by scripts/container-test.sh (spec §24.2, R64)."""

import shutil
import subprocess
from pathlib import Path

import pytest

pytestmark = pytest.mark.container


def test_hyperframes_doctor_passes() -> None:
    result = subprocess.run(
        ["hyperframes", "doctor"], capture_output=True, text=True, check=False, timeout=300
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_ffmpeg_and_ffprobe_are_on_path() -> None:
    assert shutil.which("ffmpeg") is not None
    assert shutil.which("ffprobe") is not None


def test_debian_chromium_is_used_for_hyperframes() -> None:
    assert Path("/usr/bin/chromium").exists()
