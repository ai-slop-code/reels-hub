from fastapi.testclient import TestClient

from reels_hub import __version__
from reels_hub.app import app


def test_health_returns_200() -> None:
    response = TestClient(app).get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "version": __version__}
