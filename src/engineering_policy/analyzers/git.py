from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass
from pathlib import Path

from engineering_policy.domain.errors import PolicyError

GIT_TIMEOUT_SECONDS = 15
MAX_GIT_OUTPUT_BYTES = 10 * 1024 * 1024


@dataclass(frozen=True)
class GitOutput:
    stdout: bytes
    stderr: bytes
    returncode: int


def run_git(root: Path, arguments: list[str], *, check: bool = True) -> GitOutput:
    try:
        completed = subprocess.run(
            ["git", "-C", os.fspath(root), *arguments],
            stdin=subprocess.DEVNULL,
            capture_output=True,
            timeout=GIT_TIMEOUT_SECONDS,
            check=False,
        )
    except FileNotFoundError as exc:
        raise PolicyError(
            "DEPENDENCY_NOT_INSTALLED", "Git executable is not installed.", {}
        ) from exc
    except subprocess.TimeoutExpired as exc:
        raise PolicyError("ANALYZER_FAILED", "Git command timed out.", {}) from exc
    if len(completed.stdout) > MAX_GIT_OUTPUT_BYTES or len(completed.stderr) > MAX_GIT_OUTPUT_BYTES:
        raise PolicyError("ANALYZER_FAILED", "Git command output exceeded the limit.", {})
    if check and completed.returncode != 0:
        raise PolicyError("ANALYZER_FAILED", "Git command failed.", {})
    return GitOutput(completed.stdout, completed.stderr, completed.returncode)


def resolve_repository_root(repository_path: Path) -> Path:
    normalized = repository_path.expanduser().resolve()
    if not normalized.is_dir():
        raise PolicyError(
            "NOT_A_GIT_REPOSITORY",
            "The repository path is not a directory in a Git worktree.",
            {"repository_path": str(normalized)},
        )
    output = run_git(normalized, ["rev-parse", "--show-toplevel"], check=False)
    if output.returncode != 0 or not output.stdout:
        raise PolicyError(
            "NOT_A_GIT_REPOSITORY",
            "The repository path is not inside a Git worktree.",
            {"repository_path": str(normalized)},
        )
    root = Path(os.fsdecode(output.stdout.rstrip(b"\n"))).resolve()
    if normalized != root and root not in normalized.parents:
        raise PolicyError(
            "NOT_A_GIT_REPOSITORY",
            "Git returned an invalid worktree root.",
            {"repository_path": str(normalized)},
        )
    return root


def validate_revision(root: Path, revision: str) -> None:
    output = run_git(
        root,
        ["rev-parse", "--verify", "--end-of-options", f"{revision}^{{commit}}"],
        check=False,
    )
    if output.returncode != 0 or not output.stdout:
        raise PolicyError(
            "INVALID_REVISION",
            f"Git revision '{revision}' could not be resolved.",
            {"revision": revision},
        )
