"""CLI entry for indexer: uv run python -m src.indexer [create-db|reset-db|update-db|build]"""
import argparse
import os
import sys

from src.config import DEFAULT_CHROMA_DIR, DEFAULT_SCHEMA_PATH

from .build import run, run_create, run_reset, run_update


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build YellowPages Chroma vector DB from an OpenAPI schema."
    )
    parser.add_argument(
        "command",
        nargs="?",
        default="build",
        choices=["create-db", "reset-db", "update-db", "build"],
        help="create-db: create DB only if missing; reset-db: clear and rebuild; update-db: add new tools only; build: full rebuild (default)",
    )
    parser.add_argument(
        "--schema-path",
        default=os.environ.get("YELLOW_PAGES_SCHEMA_PATH", DEFAULT_SCHEMA_PATH),
        help="Path to OpenAPI schema (JSON or YAML)",
    )
    parser.add_argument(
        "--chroma-dir",
        default=os.environ.get("YELLOW_PAGES_CHROMA_DIR", DEFAULT_CHROMA_DIR),
        help="Directory for Chroma persistence",
    )
    parser.add_argument("-q", "--quiet", action="store_true", help="Less output")
    args = parser.parse_args()

    verbose = not args.quiet
    common = {"schema_path": args.schema_path, "chroma_dir": args.chroma_dir, "verbose": verbose}

    runners = {
        "create-db": run_create,
        "reset-db": run_reset,
        "update-db": run_update,
        "build": run,
    }
    try:
        runners[args.command](**common)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
