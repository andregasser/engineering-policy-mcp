from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from pathlib import Path

from engineering_policy.application import PolicyService, parse_request
from engineering_policy.application.serialization import serialize_error, serialize_resolution
from engineering_policy.domain.errors import PolicyError


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="engineering-policy")
    subparsers = parser.add_subparsers(dest="command", required=True)
    resolve_parser = subparsers.add_parser("resolve")
    resolve_parser.add_argument("--event", required=True)
    resolve_parser.add_argument("--repository", required=True)
    resolve_parser.add_argument("--base", default="HEAD")
    resolve_parser.add_argument("--task-id")
    return parser


def run(arguments: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(arguments)
    try:
        request = parse_request(
            {
                "event": args.event,
                "repository_path": str(Path(args.repository).resolve()),
                "base_revision": args.base,
                "task_id": args.task_id,
            }
        )
        output = serialize_resolution(PolicyService().resolve(request))
        exit_code = 0
    except PolicyError as error:
        output = serialize_error(error)
        exit_code = 2
    except Exception:
        output = serialize_error(
            PolicyError("ANALYZER_FAILED", "Policy resolution failed unexpectedly.", {})
        )
        exit_code = 2
    sys.stdout.write(json.dumps(output, separators=(",", ":"), sort_keys=True) + "\n")
    return exit_code


def main() -> None:
    raise SystemExit(run())


if __name__ == "__main__":
    main()
