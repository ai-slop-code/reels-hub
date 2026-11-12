import unicodedata
from pathlib import Path

import pytest

from reels_hub.config import ConfigError, Settings
from reels_hub.paths import MediaPaths, ensure_media_marker, safe_rel

HOST = "/Users/lubos/Movies/ReelsHub"


def test_one_relative_path_maps_to_the_container_and_the_mac() -> None:
    paths = MediaPaths(Path("/media"), HOST)
    rel = "giro2027/raw/sony/C0031.MP4"
    assert paths.container_path(rel) == Path("/media/giro2027/raw/sony/C0031.MP4")
    assert paths.host_path(rel) == f"{HOST}/giro2027/raw/sony/C0031.MP4"
    assert paths.relative(Path("/media/giro2027/raw/sony/C0031.MP4")) == rel


def test_relative_paths_are_stored_in_nfc() -> None:
    decomposed = unicodedata.normalize("NFD", "giro/lízatko.MP4")
    assert safe_rel(decomposed) == unicodedata.normalize("NFC", "giro/lízatko.MP4")


@pytest.mark.parametrize("rel", ["", ".", "/etc/passwd", "../outside.mp4", "giro/../../x"])
def test_paths_outside_the_media_root_are_refused(rel: str) -> None:
    with pytest.raises(ValueError):
        safe_rel(rel)


def test_a_path_outside_the_root_cannot_be_turned_into_a_relative_path() -> None:
    with pytest.raises(ValueError):
        MediaPaths(Path("/media"), HOST).relative(Path("/data/reels-hub.sqlite"))


@pytest.mark.parametrize("raw", ["", "   ", "~/Movies/ReelsHub", "~", "Movies/ReelsHub", "./media"])
def test_the_host_media_root_must_be_absolute_and_never_tilde(raw: str) -> None:
    env = {"REELS_HUB_HOST_MEDIA_ROOT": raw}
    with pytest.raises(ConfigError, match="REELS_HUB_HOST_MEDIA_ROOT"):
        Settings.from_env(env)


def test_an_absolute_host_media_root_is_accepted_and_trimmed() -> None:
    settings = Settings.from_env({"REELS_HUB_HOST_MEDIA_ROOT": HOST + "/"})
    assert settings.host_media_root == HOST
    assert settings.media_root == Path("/media")
    assert settings.data_dir == Path("/data")
    assert settings.db_path == Path("/data/reels-hub.sqlite")
    assert settings.backup_dir == Path("/media/_backups/db")


def test_the_marker_is_only_written_into_an_empty_folder(tmp_path: Path) -> None:
    media = tmp_path / "media"
    media.mkdir()
    (media / "giro00").mkdir()
    assert ensure_media_marker(media) is False
    assert not (media / ".reels-hub-root").exists()
    (media / "giro00").rmdir()
    assert ensure_media_marker(media) is True
    assert ensure_media_marker(media) is True
