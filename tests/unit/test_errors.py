from __future__ import annotations

import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest

from engineering_policy.analyzers.git import resolve_repository_root, run_git
from engineering_policy.application import PolicyService, ResolveRequest
from engineering_policy.domain.errors import PolicyError


def test_missing_git_is_structured(tmp_path: Path) -> None:
    with (
        patch("engineering_policy.analyzers.git.subprocess.run", side_effect=FileNotFoundError),
        pytest.raises(PolicyError) as raised,
    ):
        run_git(tmp_path, ["status"])
    assert raised.value.code == "DEPENDENCY_NOT_INSTALLED"


def test_non_repository_is_structured(tmp_path: Path) -> None:
    with pytest.raises(PolicyError) as raised:
        resolve_repository_root(tmp_path)
    assert raised.value.code == "NOT_A_GIT_REPOSITORY"


def test_missing_repository_path_is_not_reported_as_missing_git(tmp_path: Path) -> None:
    with pytest.raises(PolicyError) as raised:
        resolve_repository_root(tmp_path / "absent")
    assert raised.value.code == "NOT_A_GIT_REPOSITORY"


def test_unsupported_event_is_structured(tmp_path: Path) -> None:
    with pytest.raises(PolicyError) as raised:
        PolicyService().resolve(ResolveRequest(event="task_start", repository_path=str(tmp_path)))
    assert raised.value.code == "UNSUPPORTED_EVENT"


def test_git_timeout_is_structured(tmp_path: Path) -> None:
    with (
        patch(
            "engineering_policy.analyzers.git.subprocess.run",
            side_effect=subprocess.TimeoutExpired(["git"], 15),
        ),
        pytest.raises(PolicyError) as raised,
    ):
        run_git(tmp_path, ["status"])
    assert raised.value.code == "ANALYZER_FAILED"
