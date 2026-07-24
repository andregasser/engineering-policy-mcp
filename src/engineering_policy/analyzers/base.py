from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Protocol

from engineering_policy.domain.facts import FactStore
from engineering_policy.domain.models import AnalysisResult, RepositoryContext


class AnalyzerCost(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass(frozen=True)
class AnalyzerDescriptor:
    id: str
    provides: frozenset[str]
    requires: frozenset[str]
    cost: AnalyzerCost
    priority: int = 0


class Analyzer(Protocol):
    def descriptor(self) -> AnalyzerDescriptor: ...

    def supports(self, context: RepositoryContext) -> bool: ...

    def analyze(self, context: RepositoryContext, facts: FactStore) -> AnalysisResult: ...
