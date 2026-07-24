from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP

from engineering_policy.application import PolicyService, parse_request
from engineering_policy.application.serialization import serialize_error, serialize_resolution
from engineering_policy.domain.errors import PolicyError

mcp = FastMCP("engineering-policy")


@mcp.tool()
def resolve_policies(
    event: str,
    repository_path: str,
    base_revision: str = "HEAD",
    task_id: str | None = None,
) -> dict[str, Any]:
    """Resolve applicable engineering policies for the current Git worktree."""
    try:
        request = parse_request(
            {
                "event": event,
                "repository_path": repository_path,
                "base_revision": base_revision,
                "task_id": task_id,
            }
        )
        return serialize_resolution(PolicyService().resolve(request))
    except PolicyError as error:
        return serialize_error(error)
    except Exception:
        return serialize_error(
            PolicyError("ANALYZER_FAILED", "Policy resolution failed unexpectedly.", {})
        )


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
