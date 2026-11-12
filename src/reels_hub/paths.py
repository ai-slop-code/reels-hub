"""Path mapping between the Mac, the container and the database (spec §23.2, R14).

The database stores paths relative to the media root. In the container the root is /media; on the
Mac it is REELS_HUB_HOST_MEDIA_ROOT (absolute, never `~`), so Edits and Claude get real Mac paths.
"""

import unicodedata
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

MEDIA_MARKER = ".reels-hub-root"


def safe_rel(rel: str) -> str:
    """Return a media-relative path in NFC form, or raise if it is absolute or escapes the root."""
    normalized = unicodedata.normalize("NFC", rel)
    pure = PurePosixPath(normalized)
    if not normalized or pure.is_absolute() or ".." in pure.parts or pure == PurePosixPath("."):
        raise ValueError(f"not a path relative to the media root: {rel!r}")
    return pure.as_posix()


def ensure_media_marker(media_root: Path) -> bool:
    """Write the marker on first setup (an existing, empty media folder). True if it is present."""
    marker = media_root / MEDIA_MARKER
    if marker.is_file():
        return True
    if not media_root.is_dir() or any(media_root.iterdir()):
        return False
    marker.write_text("Reels Hub media root. Do not delete.\n", encoding="utf-8")
    return True


@dataclass(frozen=True)
class MediaPaths:
    container_root: Path
    host_root: str

    def container_path(self, rel: str) -> Path:
        return self.container_root / safe_rel(rel)

    def host_path(self, rel: str) -> str:
        return f"{self.host_root.rstrip('/')}/{safe_rel(rel)}"

    def relative(self, container_path: Path) -> str:
        return safe_rel(container_path.relative_to(self.container_root).as_posix())
