from __future__ import annotations

import os
from datetime import UTC, datetime
from pathlib import Path

from engineering_policy.analyzers.base import AnalyzerCost, AnalyzerDescriptor
from engineering_policy.analyzers.paths import PathClassifier
from engineering_policy.domain.facts import FactStore
from engineering_policy.domain.models import (
    AnalysisResult,
    Evidence,
    Fact,
    RepositoryContext,
    UnavailableFact,
    ValueType,
    WarningMessage,
)


class RepositoryTechnologyAnalyzer:
    _descriptor = AnalyzerDescriptor(
        id="repository-technology",
        provides=frozenset(
            {
                "repository.language.java",
                "repository.language.kotlin",
                "repository.build_system",
            }
        ),
        requires=frozenset(),
        cost=AnalyzerCost.MEDIUM,
        priority=10,
    )

    def descriptor(self) -> AnalyzerDescriptor:
        return self._descriptor

    def supports(self, context: RepositoryContext) -> bool:
        return True

    def analyze(self, context: RepositoryContext, facts: FactStore) -> AnalysisResult:
        classifier = PathClassifier(context.config.analysis)
        java_paths: list[str] = []
        kotlin_paths: list[str] = []
        maven = False
        gradle = False
        for directory, names, filenames in os.walk(context.root, followlinks=False):
            current = Path(directory)
            relative_directory = current.relative_to(context.root)
            kept_names: list[str] = []
            for name in sorted(names):
                child = current / name
                relative = (relative_directory / name).as_posix()
                if name == ".git" or child.is_symlink() or classifier.is_excluded(f"{relative}/"):
                    continue
                kept_names.append(name)
            names[:] = kept_names
            for filename in sorted(filenames):
                path = current / filename
                relative = path.relative_to(context.root).as_posix()
                if path.is_symlink() or classifier.is_excluded(relative):
                    continue
                if filename.endswith(".java"):
                    java_paths.append(relative)
                elif filename.endswith(".kt"):
                    kotlin_paths.append(relative)
                if filename == "pom.xml":
                    maven = True
                elif filename in {
                    "build.gradle",
                    "build.gradle.kts",
                    "settings.gradle",
                    "settings.gradle.kts",
                }:
                    gradle = True

        observed_at = datetime.now(UTC)
        result_facts = [
            self._boolean_fact(
                "repository.language.java", bool(java_paths), java_paths, observed_at
            ),
            self._boolean_fact(
                "repository.language.kotlin", bool(kotlin_paths), kotlin_paths, observed_at
            ),
        ]
        unavailable: tuple[UnavailableFact, ...] = ()
        warnings: tuple[WarningMessage, ...] = ()
        if maven and gradle:
            unavailable = (
                UnavailableFact(
                    key="repository.build_system",
                    producer_id=self._descriptor.id,
                    reason="Both Maven and Gradle build files were detected.",
                ),
            )
            warnings = (
                WarningMessage(
                    code="AMBIGUOUS_BUILD_SYSTEM",
                    message="Both Maven and Gradle build files were detected.",
                ),
            )
        else:
            value = "maven" if maven else "gradle" if gradle else None
            result_facts.append(
                Fact(
                    key="repository.build_system",
                    value=value,
                    value_type=ValueType.STRING if value else ValueType.NULL,
                    producer_id=self._descriptor.id,
                    confidence=1.0,
                    evidence=(
                        Evidence(
                            kind="repository_scan",
                            description="Build system inferred from build-file presence.",
                        ),
                    ),
                    observed_at=observed_at,
                )
            )
        return AnalysisResult(
            facts=tuple(sorted(result_facts, key=lambda item: item.key)),
            unavailable=unavailable,
            warnings=warnings,
        )

    def _boolean_fact(self, key: str, value: bool, paths: list[str], observed_at: datetime) -> Fact:
        return Fact(
            key=key,
            value=value,
            value_type=ValueType.BOOLEAN,
            producer_id=self._descriptor.id,
            confidence=1.0,
            evidence=(
                Evidence(
                    kind="repository_scan",
                    description="Language inferred from repository file presence.",
                    paths=tuple(sorted(paths)[:100]),
                ),
            ),
            observed_at=observed_at,
        )
