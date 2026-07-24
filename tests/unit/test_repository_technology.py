from __future__ import annotations

from pathlib import Path

from engineering_policy.analyzers.repository_technology import RepositoryTechnologyAnalyzer
from engineering_policy.domain.facts import FactStore
from engineering_policy.domain.models import (
    AnalysisConfig,
    AppConfig,
    RepositoryContext,
    TelemetryConfig,
)


def context(root: Path) -> RepositoryContext:
    return RepositoryContext(
        root,
        "HEAD",
        AppConfig(
            1,
            (),
            AnalysisConfig(
                ("src/main/**",),
                ("src/test/**",),
                (".engineering-policy/**",),
                10,
                500,
            ),
            TelemetryConfig(False, ".engineering-policy/events.jsonl"),
        ),
    )


def test_scan_does_not_follow_symlink(tmp_path: Path) -> None:
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "Secret.java").write_text("secret", encoding="utf-8")
    repository = tmp_path / "repository"
    repository.mkdir()
    (repository / "linked").symlink_to(outside, target_is_directory=True)

    result = RepositoryTechnologyAnalyzer().analyze(context(repository), FactStore())

    java = next(fact for fact in result.facts if fact.key == "repository.language.java")
    assert java.value is False
    assert "Secret.java" not in repr(result)


def test_ambiguous_build_system_is_unavailable(tmp_path: Path) -> None:
    (tmp_path / "pom.xml").write_text("", encoding="utf-8")
    (tmp_path / "build.gradle").write_text("", encoding="utf-8")

    result = RepositoryTechnologyAnalyzer().analyze(context(tmp_path), FactStore())

    assert result.unavailable[0].key == "repository.build_system"
    assert result.warnings[0].code == "AMBIGUOUS_BUILD_SYSTEM"
