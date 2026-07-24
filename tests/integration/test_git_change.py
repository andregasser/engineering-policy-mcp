from __future__ import annotations

from pathlib import Path
from typing import Any

from engineering_policy.analyzers.git_change import MAX_UNTRACKED_SIZE
from engineering_policy.application import PolicyService, ResolveRequest
from engineering_policy.application.serialization import serialize_resolution
from tests.conftest import git


def fact_values(repository: Path) -> dict[str, Any]:
    resolution = PolicyService().resolve(
        ResolveRequest(event="before_completion", repository_path=str(repository))
    )
    serialized = serialize_resolution(resolution)
    return {fact["key"]: fact["value"] for fact in serialized["facts"]}


def test_staged_unstaged_untracked_union_is_unique(java_repository: Path) -> None:
    main = java_repository / "src/main/java/example/App.java"
    main.write_text("package example;\npublic class App { int a = 1; }\n", encoding="utf-8")
    git(java_repository, "add", str(main.relative_to(java_repository)))
    main.write_text(
        "package example;\npublic class App { int a = 1; int b = 2; }\n", encoding="utf-8"
    )
    test = java_repository / "src/test/java/example/NewTest.java"
    test.write_text("package example;\npublic class NewTest {}\n", encoding="utf-8")

    facts = fact_values(java_repository)

    assert facts["change.changed_paths"] == [
        "src/main/java/example/App.java",
        "src/test/java/example/NewTest.java",
    ]
    assert facts["change.files.count"] == 2
    assert facts["change.production_files.count"] == 1
    assert facts["change.test_files.count"] == 1


def test_ignored_and_telemetry_paths_are_excluded(java_repository: Path) -> None:
    (java_repository / ".gitignore").write_text("ignored.txt\n", encoding="utf-8")
    (java_repository / "ignored.txt").write_text("ignored\n", encoding="utf-8")

    facts = fact_values(java_repository)

    assert "ignored.txt" not in facts["change.changed_paths"]
    assert all(
        not path.startswith(".engineering-policy/") for path in facts["change.changed_paths"]
    )


def test_rename_uses_destination_path(java_repository: Path) -> None:
    old = "src/main/java/example/App.java"
    new = "src/test/java/example/RenamedTest.java"
    git(java_repository, "mv", old, new)

    facts = fact_values(java_repository)

    assert facts["change.changed_paths"] == [new]
    assert facts["change.production_files.count"] == 0
    assert facts["change.test_files.count"] == 1


def test_deleted_file_keeps_former_classification(java_repository: Path) -> None:
    git(java_repository, "rm", "src/main/java/example/App.java")

    facts = fact_values(java_repository)

    assert facts["change.production_files.count"] == 1


def test_untracked_binary_contributes_no_lines(java_repository: Path) -> None:
    (java_repository / "src/main/binary.dat").parent.mkdir(parents=True, exist_ok=True)
    (java_repository / "src/main/binary.dat").write_bytes(b"\0binary\n")

    resolution = PolicyService().resolve(
        ResolveRequest(event="before_completion", repository_path=str(java_repository))
    )

    assert any(warning.code == "BINARY_FILE" for warning in resolution.warnings)
    assert next(fact for fact in resolution.facts if fact.key == "change.lines.total").value == 0


def test_oversized_untracked_file_contributes_no_lines(java_repository: Path) -> None:
    path = java_repository / "src/main/large.txt"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as stream:
        stream.seek(MAX_UNTRACKED_SIZE)
        stream.write(b"x")

    resolution = PolicyService().resolve(
        ResolveRequest(event="before_completion", repository_path=str(java_repository))
    )

    assert any(warning.code == "OVERSIZED_UNTRACKED_FILE" for warning in resolution.warnings)
