from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

import pytest

from engineering_policy.application import PolicyService, ResolveRequest
from engineering_policy.application.serialization import serialize_resolution
from engineering_policy.domain.errors import PolicyError
from engineering_policy.mcp.server import resolve_policies


def resolve(repository: Path, revision: str = "HEAD") -> dict[str, Any]:
    result = PolicyService().resolve(
        ResolveRequest(
            event="before_completion",
            repository_path=str(repository),
            base_revision=revision,
        )
    )
    return serialize_resolution(result)


def policy_ids(result: dict[str, Any]) -> list[str]:
    policies = result["applicable_policies"]
    assert isinstance(policies, list)
    return [str(policy["id"]) for policy in policies]


def test_small_java_production_change(java_repository: Path) -> None:
    path = java_repository / "src/main/java/example/App.java"
    path.write_text("package example;\npublic class App { int value = 1; }\n", encoding="utf-8")

    result = resolve(java_repository)

    assert policy_ids(result) == ["team.java.test-production-change"]


def test_large_java_production_change(java_repository: Path) -> None:
    path = java_repository / "src/main/java/example/App.java"
    path.write_text("\n".join(f"// line {index}" for index in range(501)), encoding="utf-8")

    result = resolve(java_repository)

    assert policy_ids(result) == [
        "company.comprehensive-review",
        "team.java.test-production-change",
    ]
    review = result["applicable_policies"][0]
    assert review["matched_reasons"][0]["evidence"][0]["kind"] == "threshold"


def test_readme_only_change(java_repository: Path) -> None:
    (java_repository / "README.md").write_text("# Updated\n", encoding="utf-8")

    assert policy_ids(resolve(java_repository)) == []


def test_invalid_revision_is_structured(java_repository: Path) -> None:
    with pytest.raises(PolicyError) as raised:
        resolve(java_repository, "definitely-missing")
    assert raised.value.code == "INVALID_REVISION"
    assert "Traceback" not in raised.value.message


def test_cli_matches_service_semantics(java_repository: Path) -> None:
    path = java_repository / "src/main/java/example/App.java"
    path.write_text("package example;\npublic class App { int value = 1; }\n", encoding="utf-8")
    expected = resolve(java_repository)
    command = subprocess.run(
        [
            "engineering-policy",
            "resolve",
            "--event",
            "before_completion",
            "--repository",
            str(java_repository),
            "--base",
            "HEAD",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    actual = json.loads(command.stdout)
    for result in (expected, actual):
        for fact in result["facts"]:
            fact.pop("observed_at")
        for analyzer in result["analyzers_executed"]:
            analyzer.pop("duration_ms")
    assert actual == expected


def test_mcp_matches_service_semantics(java_repository: Path) -> None:
    path = java_repository / "src/main/java/example/App.java"
    path.write_text("package example;\npublic class App { int value = 1; }\n", encoding="utf-8")
    expected = resolve(java_repository)
    actual = resolve_policies("before_completion", str(java_repository))
    for result in (expected, actual):
        for fact in result["facts"]:
            fact.pop("observed_at")
        for analyzer in result["analyzers_executed"]:
            analyzer.pop("duration_ms")
    assert actual == expected
