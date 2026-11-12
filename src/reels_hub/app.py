from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from reels_hub import __version__
from reels_hub.config import Settings
from reels_hub.db import migrate
from reels_hub.health import health_report
from reels_hub.jobs import Worker
from reels_hub.paths import ensure_media_marker


def prepare_worker(settings: Settings) -> Worker | None:
    """Migrate the database and build the worker, unless the media folder isn't mounted."""
    if not ensure_media_marker(settings.media_root):
        return None
    migrate(settings.db_path, settings.backup_dir)
    return Worker(settings.db_path, settings.backup_dir)


def create_app(*, settings: Settings, worker: Worker | None = None) -> FastAPI:
    @asynccontextmanager
    async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
        if worker is not None:
            worker.start()
        try:
            yield
        finally:
            if worker is not None:
                worker.stop()

    app = FastAPI(title="Reels Hub", version=__version__, lifespan=lifespan)

    @app.get("/health")
    def health() -> JSONResponse:
        status, body = health_report(settings)
        return JSONResponse(body, status_code=status)

    return app
