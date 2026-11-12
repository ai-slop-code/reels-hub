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
from reels_hub.watcher import SCAN_KIND, Watcher

SCAN_EVERY_SECONDS = 10.0


def build_worker(settings: Settings) -> Worker:
    """The worker waits while the media folder isn't mounted, then migrates and scans every 10 s."""
    watcher = Watcher(settings)

    def prepare() -> None:
        migrate(settings.db_path, settings.backup_dir)

    return Worker(
        settings.db_path,
        settings.backup_dir,
        handlers={SCAN_KIND: watcher.handle},
        ready=lambda: ensure_media_marker(settings.media_root),
        prepare=prepare,
        schedules={SCAN_KIND: SCAN_EVERY_SECONDS},
    )


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
