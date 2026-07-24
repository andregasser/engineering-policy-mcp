from __future__ import annotations

from datetime import UTC, datetime

from engineering_policy.analyzers.base import AnalyzerCost, AnalyzerDescriptor
from engineering_policy.domain.facts import FactStore
from engineering_policy.domain.models import (
    AnalysisResult,
    Evidence,
    Fact,
    RepositoryContext,
    UnavailableFact,
    ValueType,
)


class ChangeSizeAnalyzer:
    _descriptor = AnalyzerDescriptor(
        id="change-size",
        provides=frozenset({"change.substantial"}),
        requires=frozenset({"change.production_files.count", "change.lines.total"}),
        cost=AnalyzerCost.LOW,
        priority=30,
    )

    def descriptor(self) -> AnalyzerDescriptor:
        return self._descriptor

    def supports(self, context: RepositoryContext) -> bool:
        return True

    def analyze(self, context: RepositoryContext, facts: FactStore) -> AnalysisResult:
        files = facts.lookup("change.production_files.count")
        lines = facts.lookup("change.lines.total")
        if files.fact is None or lines.fact is None:
            return AnalysisResult(
                unavailable=(
                    UnavailableFact(
                        key="change.substantial",
                        producer_id=self._descriptor.id,
                        reason="Required Git aggregate facts are unavailable.",
                    ),
                )
            )
        file_count = int(files.fact.value)  # type: ignore[arg-type]
        line_count = int(lines.fact.value)  # type: ignore[arg-type]
        config = context.config.analysis
        substantial = (
            file_count >= config.substantial_production_files
            or line_count >= config.substantial_changed_lines
        )
        return AnalysisResult(
            facts=(
                Fact(
                    key="change.substantial",
                    value=substantial,
                    value_type=ValueType.BOOLEAN,
                    producer_id=self._descriptor.id,
                    confidence=1.0,
                    evidence=(
                        Evidence(
                            kind="threshold",
                            description="Substantial-change thresholds evaluated.",
                            details=(
                                ("production_files", file_count),
                                ("production_files_threshold", config.substantial_production_files),
                                ("changed_lines", line_count),
                                ("changed_lines_threshold", config.substantial_changed_lines),
                            ),
                        ),
                    ),
                    observed_at=datetime.now(UTC),
                ),
            )
        )
