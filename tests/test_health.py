from fastapi.testclient import TestClient

from reels_hub import __version__
from reels_hub.app import build_worker, create_app
from reels_hub.config import Settings
from reels_hub.db import migrate
from reels_hub.paths import MEDIA_MARKER


def test_health_returns_200_with_the_report_fields(settings: Settings) -> None:
    migrate(settings.db_path, settings.backup_dir)
    response = TestClient(create_app(settings=settings)).get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["version"] == __version__
    assert body["git_sha"] == "testsha"
    assert body["schema_version"] == 2
    assert body["media_mounted"] is True
    assert body["jobs"] == {"queued": 0, "running": 0, "done": 0, "failed": 0}
    assert isinstance(body["media_free_gb"], float)
    assert isinstance(body["data_free_gb"], float)


def test_health_is_503_when_the_media_marker_is_missing(settings: Settings) -> None:
    migrate(settings.db_path, settings.backup_dir)
    (settings.media_root / MEDIA_MARKER).unlink()
    response = TestClient(create_app(settings=settings)).get("/health")
    assert response.status_code == 503
    assert response.json()["status"] == "unavailable"
    assert response.json()["media_mounted"] is False


def test_health_is_503_when_the_database_cannot_be_opened(settings: Settings) -> None:
    response = TestClient(create_app(settings=settings)).get("/health")
    assert response.status_code == 503
    body = response.json()
    assert body["schema_version"] is None
    assert body["jobs"] is None
    assert body["media_mounted"] is True
    assert not settings.db_path.exists()


def test_nothing_is_migrated_while_the_media_folder_is_not_mounted(settings: Settings) -> None:
    (settings.media_root / MEDIA_MARKER).unlink()
    settings.media_root.joinpath("giro00").mkdir()
    assert build_worker(settings).is_ready() is False
    assert not settings.db_path.exists()


def test_first_setup_writes_the_marker_into_an_empty_media_folder(settings: Settings) -> None:
    (settings.media_root / MEDIA_MARKER).unlink()
    assert build_worker(settings).is_ready() is True
    assert (settings.media_root / MEDIA_MARKER).is_file()
