"""Settings from environment variables (spec §23.2, §23.3). A bad media root stops the start."""

import os
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

from reels_hub.paths import MEDIA_MARKER, MediaPaths


class ConfigError(ValueError):
    """A setting is missing or unusable. The message says what to change."""


@dataclass(frozen=True)
class Settings:
    host_media_root: str
    media_root: Path
    data_dir: Path
    git_sha: str

    @classmethod
    def from_env(cls, env: Mapping[str, str] | None = None) -> "Settings":
        source = os.environ if env is None else env
        return cls(
            host_media_root=check_host_media_root(source.get("REELS_HUB_HOST_MEDIA_ROOT", "")),
            media_root=Path(source.get("REELS_HUB_MEDIA_ROOT", "/media")),
            data_dir=Path(source.get("REELS_HUB_DATA_DIR", "/data")),
            git_sha=source.get("REELS_HUB_GIT_SHA", "unknown"),
        )

    @property
    def media(self) -> MediaPaths:
        return MediaPaths(self.media_root, self.host_media_root)

    @property
    def db_path(self) -> Path:
        return self.data_dir / "reels-hub.sqlite"

    @property
    def backup_dir(self) -> Path:
        return self.media_root / "_backups" / "db"

    @property
    def marker_path(self) -> Path:
        return self.media_root / MEDIA_MARKER


def check_host_media_root(raw: str) -> str:
    if not raw.strip():
        raise ConfigError(
            "REELS_HUB_HOST_MEDIA_ROOT is not set. Set it to the absolute Mac path of the media "
            "folder, for example /Users/lubos/Movies/ReelsHub."
        )
    if raw.startswith("~") or not PurePosixPath(raw).is_absolute():
        raise ConfigError(
            f"REELS_HUB_HOST_MEDIA_ROOT must be an absolute path, not {raw!r}. Edits can't read "
            "'~' or relative paths (spec §23.2)."
        )
    return raw.rstrip("/") or "/"
