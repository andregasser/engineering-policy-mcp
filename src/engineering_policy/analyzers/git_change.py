from __future__ import annotations

import os
from datetime import UTC, datetime

from engineering_policy.analyzers.base import AnalyzerCost, AnalyzerDescriptor
from engineering_policy.analyzers.git import run_git
from engineering_policy.analyzers.paths import PathClassifier
from engineering_policy.domain.facts import FactStore
from engineering_policy.domain.models import (
    AnalysisResult,
    Evidence,
    Fact,
    RepositoryContext,
    ValueType,
    WarningMessage,
)

MAX_UNTRACKED_SIZE = 10 * 1024 * 1024


class GitChangeAnalyzer:
    _provided = frozenset(
        {
            "change.changed_paths",
            "change.files.count",
            "change.production_files.count",
            "change.test_files.count",
            "change.java.production_files.count",
            "change.lines.added",
            "change.lines.deleted",
            "change.lines.total",
        }
    )
    _descriptor = AnalyzerDescriptor(
        id="git-change",
        provides=_provided,
        requires=frozenset(),
        cost=AnalyzerCost.HIGH,
        priority=20,
    )

    def descriptor(self) -> AnalyzerDescriptor:
        return self._descriptor

    def supports(self, context: RepositoryContext) -> bool:
        return True

    def analyze(self, context: RepositoryContext, facts: FactStore) -> AnalysisResult:
        classifier = PathClassifier(context.config.analysis)
        tracked = self._tracked_paths(context)
        untracked = self._untracked_paths(context)
        changed_paths = sorted(
            path for path in tracked | untracked if classifier.classify(path) != "excluded"
        )
        additions, deletions, warnings = self._tracked_lines(context, classifier)
        untracked_additions, untracked_warnings = self._untracked_lines(
            context, untracked, classifier
        )
        additions += untracked_additions
        warnings.extend(untracked_warnings)

        production = [path for path in changed_paths if classifier.classify(path) == "production"]
        tests = [path for path in changed_paths if classifier.classify(path) == "test"]
        java_production = [path for path in production if path.endswith(".java")]
        observed_at = datetime.now(UTC)
        evidence = (
            Evidence(
                kind="git_change",
                description=f"Compared '{context.base_revision}' with the combined worktree.",
                paths=tuple(changed_paths[:1000]),
            ),
        )
        values: dict[str, tuple[object, ValueType]] = {
            "change.changed_paths": (changed_paths, ValueType.STRING_LIST),
            "change.files.count": (len(changed_paths), ValueType.INTEGER),
            "change.production_files.count": (len(production), ValueType.INTEGER),
            "change.test_files.count": (len(tests), ValueType.INTEGER),
            "change.java.production_files.count": (len(java_production), ValueType.INTEGER),
            "change.lines.added": (additions, ValueType.INTEGER),
            "change.lines.deleted": (deletions, ValueType.INTEGER),
            "change.lines.total": (additions + deletions, ValueType.INTEGER),
        }
        result_facts = tuple(
            Fact(
                key=key,
                value=value,  # type: ignore[arg-type]
                value_type=value_type,
                producer_id=self._descriptor.id,
                confidence=1.0,
                evidence=evidence,
                observed_at=observed_at,
            )
            for key, (value, value_type) in sorted(values.items())
        )
        return AnalysisResult(facts=result_facts, warnings=tuple(warnings))

    @staticmethod
    def _tracked_paths(context: RepositoryContext) -> set[str]:
        output = run_git(
            context.root,
            [
                "diff",
                "--name-status",
                "-z",
                "--find-renames",
                context.base_revision,
                "--",
            ],
        ).stdout
        fields = output.split(b"\0")
        paths: set[str] = set()
        index = 0
        while index < len(fields) and fields[index]:
            status = os.fsdecode(fields[index])
            index += 1
            if status.startswith(("R", "C")):
                index += 1
            if index < len(fields):
                paths.add(os.fsdecode(fields[index]))
                index += 1
        return paths

    @staticmethod
    def _untracked_paths(context: RepositoryContext) -> set[str]:
        output = run_git(context.root, ["ls-files", "--others", "--exclude-standard", "-z"]).stdout
        return {os.fsdecode(item) for item in output.split(b"\0") if item}

    @staticmethod
    def _tracked_lines(
        context: RepositoryContext, classifier: PathClassifier
    ) -> tuple[int, int, list[WarningMessage]]:
        output = run_git(
            context.root, ["diff", "--numstat", "-z", context.base_revision, "--"]
        ).stdout
        additions = 0
        deletions = 0
        warnings: list[WarningMessage] = []
        fields = output.split(b"\0")
        for field in fields:
            if not field:
                continue
            parts = field.split(b"\t", 2)
            if len(parts) != 3:
                continue
            added, deleted, raw_path = parts
            path = os.fsdecode(raw_path)
            if classifier.classify(path) == "excluded":
                continue
            if added == b"-" or deleted == b"-":
                warnings.append(
                    WarningMessage(
                        code="BINARY_FILE",
                        message=f"Binary file '{path}' contributes zero changed lines.",
                    )
                )
                continue
            additions += int(added)
            deletions += int(deleted)
        return additions, deletions, warnings

    @staticmethod
    def _untracked_lines(
        context: RepositoryContext, paths: set[str], classifier: PathClassifier
    ) -> tuple[int, list[WarningMessage]]:
        additions = 0
        warnings: list[WarningMessage] = []
        for relative in sorted(paths):
            if classifier.classify(relative) == "excluded":
                continue
            path = context.root / relative
            if path.is_symlink() or not path.is_file():
                continue
            size = path.stat().st_size
            if size > MAX_UNTRACKED_SIZE:
                warnings.append(
                    WarningMessage(
                        code="OVERSIZED_UNTRACKED_FILE",
                        message=(
                            f"Untracked file '{relative}' exceeds 10 MiB "
                            "and contributes zero lines."
                        ),
                    )
                )
                continue
            content = path.read_bytes()
            if b"\0" in content:
                warnings.append(
                    WarningMessage(
                        code="BINARY_FILE",
                        message=f"Binary file '{relative}' contributes zero changed lines.",
                    )
                )
                continue
            additions += len(content.splitlines())
        return additions, warnings
