import argparse
from collections.abc import Sequence

from reels_hub import __version__

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8787


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="reels-hub", description="Reels Hub")
    commands = parser.add_subparsers(dest="command", required=True)

    serve = commands.add_parser("serve", help="run the web app")
    serve.add_argument("--host", default=DEFAULT_HOST)
    serve.add_argument("--port", type=int, default=DEFAULT_PORT)

    commands.add_parser("version", help="print the version")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "version":
        print(__version__)
    elif args.command == "serve":
        import uvicorn

        uvicorn.run("reels_hub.app:app", host=args.host, port=args.port)
    return 0
