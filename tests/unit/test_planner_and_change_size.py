from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pytest

from engineering_policy.analyzers.base import AnalyzerCost, AnalyzerDescriptor
from engineering_policy.analyzers.change_size import ChangeSizeAnalyzer
from engineering_policy.analyzers.planner import plan
from engineering_policy.domain.errors import PolicyError
from engineering_policy.domain.facts import FactStore
from engineering_policy.domain.models import (
    AnalysisConfig,
    AnalysisResult,
    AppConfig,
    Fact,
    RepositoryContext,
    TelemetryConfig,
    ValueType,
)


class StubAnalyzer:
    def __init__(self, identifier: str, provides: str, requires: frozenset[str]) -> None:
        self._descriptor = AnalyzerDescriptor(
            identifier, frozenset({provides}), requires, AnalyzerCost.LOW
        )

    def descriptor(self) -> AnalyzerDescriptor:
        return self._descriptor

    def supports(self, context: RepositoryContext) -> bool:
        return True

    def analyze(self, context: RepositoryContext, facts: FactStore) -> AnalysisResult:
        return AnalysisResult()


def context(tmp_path: Path, files: int, lines: int) -> tuple[RepositoryContext, FactStore]:
    config = AppConfig(
        schema_version=1,
        policy_sets=(),
        analysis=AnalysisConfig((), (), (), 10, 500),
        telemetry=TelemetryConfig(False, "events.jsonl"),
    )
    store = FactStore()
    for key, value in (
        ("change.production_files.count", files),
        ("change.lines.total", lines),
    ):
        store.add(Fact(key, value, ValueType.INTEGER, "git", 1.0, (), datetime.now(UTC)))
    return RepositoryContext(tmp_path, "HEAD", config), store


def test_planner_orders_dependencies() -> None:
    first = StubAnalyzer("first", "a", frozenset())
    second = StubAnalyzer("second", "b", frozenset({"a"}))

    assert [item.descriptor().id for item in plan({"b"}, (second, first))] == [
        "first",
        "second",
    ]


def test_planner_rejects_cycles() -> None:
    first = StubAnalyzer("first", "a", frozenset({"b"}))
    second = StubAnalyzer("second", "b", frozenset({"a"}))

    with pytest.raises(PolicyError, match="cycle"):
        plan({"a"}, (first, second))


@pytest.mark.parametrize(("files", "lines"), [(10, 0), (0, 500)])
def test_change_size_threshold_is_inclusive(tmp_path: Path, files: int, lines: int) -> None:
    analysis_context, facts = context(tmp_path, files, lines)

    result = ChangeSizeAnalyzer().analyze(analysis_context, facts)

    assert result.facts[0].value is True
