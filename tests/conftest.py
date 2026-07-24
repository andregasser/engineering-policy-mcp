from __future__ import annotations

import subprocess
from collections.abc import Callable
from pathlib import Path

import pytest


def git(repository: Path, *arguments: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repository), *arguments],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout


@pytest.fixture
def java_repository(tmp_path: Path) -> Path:
    repository = tmp_path / "java-repository"
    repository.mkdir()
    git(repository, "init", "-q")
    git(repository, "config", "user.email", "tests@example.invalid")
    git(repository, "config", "user.name", "Tests")
    (repository / "src/main/java/example").mkdir(parents=True)
    (repository / "src/test/java/example").mkdir(parents=True)
    (repository / "src/main/java/example/App.java").write_text(
        "package example;\npublic class App {}\n", encoding="utf-8"
    )
    (repository / "src/test/java/example/AppTest.java").write_text(
        "package example;\npublic class AppTest {}\n", encoding="utf-8"
    )
    (repository / "pom.xml").write_text("<project></project>\n", encoding="utf-8")
    (repository / "README.md").write_text("# Fixture\n", encoding="utf-8")
    git(repository, "add", ".")
    git(repository, "commit", "-qm", "initial")
    return repository


@pytest.fixture
def write_file() -> Callable[[Path, str], None]:
    def write(path: Path, content: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    return write
