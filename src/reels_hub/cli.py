import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from reels_hub import __version__
from reels_hub.db import (
    DEFAULT_BACKUP_DIR,
    DEFAULT_DB_PATH,
    MigrationError,
    migrate,
)

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8787


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="reels-hub", description="Reels Hub")
    commands = parser.add_subparsers(dest="command", required=True)

    serve = commands.add_parser(
        "serve", help="migrate the database, then run the web app and worker"
    )
    serve.add_argument("--host", default=DEFAULT_HOST)
    serve.add_argument("--port", type=int, default=DEFAULT_PORT)
    serve.add_argument("--db", type=Path, default=DEFAULT_DB_PATH)
    serve.add_argument("--backup-dir", type=Path, default=DEFAULT_BACKUP_DIR)

    db = commands.add_parser("migrate", help="back up, then apply pending database migrations")
    db.add_argument("--db", type=Path, default=DEFAULT_DB_PATH)
    db.add_argument("--backup-dir", type=Path, default=DEFAULT_BACKUP_DIR)

    commands.add_parser("version", help="print the version")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "version":
        print(__version__)
    elif args.command == "serve":
        import uvicorn

        from reels_hub.app import create_app
        from reels_hub.jobs import Worker

        try:
            migrate(args.db, args.backup_dir)
        except (MigrationError, OSError) as exc:
            print(f"reels-hub serve: {exc}", file=sys.stderr)
            return 1
        worker = Worker(args.db, args.backup_dir)
        uvicorn.run(create_app(worker=worker), host=args.host, port=args.port)
    elif args.command == "migrate":
        try:
            result = migrate(args.db, args.backup_dir)
        except MigrationError as exc:
            print(f"reels-hub migrate: {exc}", file=sys.stderr)
            return 1
        print(f"schema {result.from_version} -> {result.to_version}")
        if result.backup is not None:
            print(f"backup {result.backup}")
    return 0
