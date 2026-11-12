import subprocess
import sys

import pytest

from reels_hub import __version__
from reels_hub.cli import main


def test_version_prints_version(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["version"]) == 0
    assert capsys.readouterr().out.strip() == __version__


def test_console_script_version() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "reels_hub", "version"],
        capture_output=True,
        text=True,
        check=True,
    )
    assert result.stdout.strip() == __version__


def test_command_is_required() -> None:
    with pytest.raises(SystemExit) as excinfo:
        main([])
    assert excinfo.value.code == 2
