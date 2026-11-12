from pathlib import Path

import pytest

from reels_hub.config import Settings
from reels_hub.paths import MEDIA_MARKER


@pytest.fixture
def settings(tmp_path: Path) -> Settings:
    media = tmp_path / "media"
    media.mkdir()
    (media / MEDIA_MARKER).write_text("test\n", encoding="utf-8")
    data = tmp_path / "data"
    data.mkdir()
    return Settings(
        host_media_root="/Users/test/ReelsHub",
        media_root=media,
        data_dir=data,
        git_sha="testsha",
    )
