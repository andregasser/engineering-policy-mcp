from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from pathlib import Path

type JsonValue = bool | int | float | str | list[JsonValue] | dict[str, JsonValue] | None


class FactState(StrEnum):
    PRESENT = "present"
    MISSING = "missing"
    UNAVAILABLE = "unavailable"


class ValueType(StrEnum):
    BOOLEAN = "boolean"
    INTEGER = "integer"
    STRING = "string"
    NULL = "null"
    STRING_LIST = "list[string]"


@dataclass(frozen=True)
class Evidence:
    kind: str
    description: str
    paths: tuple[str, ...] = ()
    details: tuple[tuple[str, JsonValue], ...] = ()


@dataclass(frozen=True)
class Fact:
    key: str
    value: JsonValue
    value_type: ValueType
    producer_id: str
    confidence: float
    evidence: tuple[Evidence, ...]
    observed_at: datetime


@dataclass(frozen=True)
class UnavailableFact:
    key: str
    producer_id: str
    reason: str


@dataclass(frozen=True)
class FactLookup:
    state: FactState
    fact: Fact | None = None
    reason: str | None = None


@dataclass(frozen=True)
class Condition:
    fact: str
    operator: str
    value: JsonValue


@dataclass(frozen=True)
class Policy:
    id: str
    title: str
    severity: str
    events: tuple[str, ...]
    instruction: str
    conditions: tuple[Condition, ...]
    parameters: tuple[tuple[str, JsonValue], ...]
    source_policy_set: str
    source_path: str


@dataclass(frozen=True)
class MatchedReason:
    fact: str
    actual_value: JsonValue
    operator: str
    expected_value: JsonValue
    evidence: tuple[Evidence, ...]


@dataclass(frozen=True)
class ApplicablePolicy:
    policy: Policy
    matched_reasons: tuple[MatchedReason, ...]


@dataclass(frozen=True)
class UnresolvedReason:
    fact: str
    state: FactState
    reason: str


@dataclass(frozen=True)
class UnresolvedPolicy:
    policy: Policy
    reasons: tuple[UnresolvedReason, ...]


@dataclass(frozen=True)
class AnalyzerExecution:
    analyzer_id: str
    duration_ms: float
    success: bool
    facts_produced: int


@dataclass(frozen=True)
class WarningMessage:
    code: str
    message: str


@dataclass(frozen=True)
class AnalysisResult:
    facts: tuple[Fact, ...] = ()
    unavailable: tuple[UnavailableFact, ...] = ()
    warnings: tuple[WarningMessage, ...] = ()


@dataclass(frozen=True)
class AnalysisConfig:
    production_paths: tuple[str, ...]
    test_paths: tuple[str, ...]
    exclude_paths: tuple[str, ...]
    substantial_production_files: int
    substantial_changed_lines: int


@dataclass(frozen=True)
class TelemetryConfig:
    enabled: bool
    path: str


@dataclass(frozen=True)
class AppConfig:
    schema_version: int
    policy_sets: tuple[str, ...]
    analysis: AnalysisConfig
    telemetry: TelemetryConfig


@dataclass(frozen=True)
class RepositoryContext:
    root: Path
    base_revision: str
    config: AppConfig


@dataclass(frozen=True)
class Resolution:
    event: str
    applicable_policies: tuple[ApplicablePolicy, ...]
    unresolved_policies: tuple[UnresolvedPolicy, ...]
    facts: tuple[Fact, ...]
    analyzers_executed: tuple[AnalyzerExecution, ...]
    warnings: tuple[WarningMessage, ...] = field(default_factory=tuple)
