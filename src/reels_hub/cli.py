import argparse
import datetime as dt
import sys
from collections.abc import Sequence

from reels_hub import __version__
from reels_hub.config import ConfigError, Settings
from reels_hub.db import MigrationError, connect, migrate
from reels_hub.paths import ensure_media_marker, safe_rel
from reels_hub.projects import add_project_folder

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8787


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="reels-hub", description="Reels Hub")
    commands = parser.add_subparsers(dest="command", required=True)

    serve = commands.add_parser("serve", help="migrate the database, then run the web app")
    serve.add_argument("--host", default=DEFAULT_HOST)
    serve.add_argument("--port", type=int, default=DEFAULT_PORT)

    commands.add_parser("migrate", help="back up, then apply pending database migrations")
    project = commands.add_parser("project", help="register a project's media folder")
    project_commands = project.add_subparsers(dest="project_command", required=True)
    add = project_commands.add_parser("add", help="watch <folder> (relative to the media root)")
    add.add_argument("project_id")
    add.add_argument("--folder", required=True)
    commands.add_parser("version", help="print the version")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "version":
        print(__version__)
        return 0
    try:
        settings = Settings.from_env()
    except ConfigError as exc:
        print(f"reels-hub: {exc}", file=sys.stderr)
        return 1
    if args.command == "migrate":
        return _migrate(settings)
    if args.command == "project":
        return _project_add(settings, args.project_id, args.folder)
    return _serve(settings, args.host, args.port)


def _migrate(settings: Settings) -> int:
    if not ensure_media_marker(settings.media_root):
        print(
            f"reels-hub migrate: the media folder {settings.media_root} isn't mounted "
            "(no .reels-hub-root). Nothing was migrated.",
            file=sys.stderr,
        )
        return 1
    try:
        result = migrate(settings.db_path, settings.backup_dir)
    except (MigrationError, OSError) as exc:
        print(f"reels-hub migrate: {exc}", file=sys.stderr)
        return 1
    print(f"schema {result.from_version} -> {result.to_version}")
    if result.backup is not None:
        print(f"backup {result.backup}")
    return 0


def _project_add(settings: Settings, project_id: str, folder: str) -> int:
    if not ensure_media_marker(settings.media_root):
        print("reels-hub project add: the media folder isn't mounted.", file=sys.stderr)
        return 1
    try:
        rel = safe_rel(folder)
        migrate(settings.db_path, settings.backup_dir)
        conn = connect(settings.db_path)
        try:
            add_project_folder(conn, project_id, rel, dt.datetime.now(dt.UTC))
        finally:
            conn.close()
    except (ValueError, MigrationError, OSError) as exc:
        print(f"reels-hub project add: {exc}", file=sys.stderr)
        return 1
    if not settings.media.container_path(rel).is_dir():
        print(f"note: {rel} doesn't exist yet; the watcher will pick it up when it does")
    print(f"project {project_id} watches {rel}")
    return 0


def _serve(settings: Settings, host: str, port: int) -> int:
    import uvicorn

    from reels_hub.app import build_worker, create_app

    worker = build_worker(settings)
    if not worker.is_ready():
        print(
            f"reels-hub serve: media folder {settings.media_root} isn't mounted; the worker waits. "
            "/health reports it.",
            file=sys.stderr,
        )
    uvicorn.run(create_app(settings=settings, worker=worker), host=host, port=port)
    return 0
