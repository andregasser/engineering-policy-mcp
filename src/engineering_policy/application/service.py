from __future__ import annotations

import time
from dataclasses import replace
from pathlib import Path

from pydantic import ValidationError

from engineering_policy.analyzers import (
    ChangeSizeAnalyzer,
    GitChangeAnalyzer,
    RepositoryTechnologyAnalyzer,
    plan,
)
from engineering_policy.analyzers.base import Analyzer
from engineering_policy.analyzers.git import resolve_repository_root, validate_revision
from engineering_policy.application.boundary import ResolveRequest
from engineering_policy.catalog import PolicyCatalog, load_config
from engineering_policy.domain.errors import PolicyError
from engineering_policy.domain.facts import FactStore
from engineering_policy.domain.models import (
    AnalyzerExecution,
    RepositoryContext,
    Resolution,
    WarningMessage,
)
from engineering_policy.resolver import resolve
from engineering_policy.telemetry import TelemetryWriter


class PolicyService:
    def __init__(
        self,
        project_root: Path | None = None,
        analyzers: tuple[Analyzer, ...] | None = None,
    ) -> None:
        self._project_root = project_root or Path(__file__).resolve().parents[3]
        self._catalog = PolicyCatalog(self._project_root)
        self._analyzers = analyzers or (
            RepositoryTechnologyAnalyzer(),
            GitChangeAnalyzer(),
            ChangeSizeAnalyzer(),
        )

    def resolve(self, request: ResolveRequest) -> Resolution:
        if request.event != "before_completion":
            raise PolicyError(
                "UNSUPPORTED_EVENT",
                f"Event '{request.event}' is not supported.",
                {"event": request.event},
            )
        repository_root = resolve_repository_root(Path(request.repository_path))
        validate_revision(repository_root, request.base_revision)
        config = load_config(repository_root)
        telemetry_relative = config.telemetry.path
        if telemetry_relative not in config.analysis.exclude_paths:
            config = replace(
                config,
                analysis=replace(
                    config.analysis,
                    exclude_paths=(*config.analysis.exclude_paths, telemetry_relative),
                ),
            )
        policies = tuple(
            policy
            for policy in self._catalog.load(config.policy_sets)
            if request.event in policy.events
        )
        required_facts = {condition.fact for policy in policies for condition in policy.conditions}
        execution_plan = plan(required_facts, self._analyzers)
        context = RepositoryContext(
            root=repository_root, base_revision=request.base_revision, config=config
        )
        store = FactStore()
        warnings: list[WarningMessage] = []
        executions: list[AnalyzerExecution] = []
        telemetry = (
            TelemetryWriter(repository_root, telemetry_relative, request.task_id)
            if config.telemetry.enabled
            else None
        )
        if telemetry:
            telemetry.emit("policy_resolution_started", event=request.event)
        for analyzer in execution_plan:
            self._execute_analyzer(analyzer, context, store, warnings, executions, telemetry)
        applicable, unresolved = resolve(policies, store)
        if telemetry:
            for applicable_policy in applicable:
                telemetry.emit(
                    "policy_resolved",
                    policy_id=applicable_policy.policy.id,
                    outcome="applicable",
                )
            for unresolved_policy in unresolved:
                telemetry.emit(
                    "policy_resolved",
                    policy_id=unresolved_policy.policy.id,
                    outcome="unresolved",
                )
            resolved_ids = {
                *(item.policy.id for item in applicable),
                *(item.policy.id for item in unresolved),
            }
            for policy in policies:
                if policy.id not in resolved_ids:
                    telemetry.emit(
                        "policy_resolved",
                        policy_id=policy.id,
                        outcome="not_applicable",
                    )
            telemetry.emit(
                "policy_resolution_completed",
                applicable_count=len(applicable),
                unresolved_count=len(unresolved),
            )
            if warning := telemetry.warning():
                warnings.append(warning)
        return Resolution(
            event=request.event,
            applicable_policies=applicable,
            unresolved_policies=unresolved,
            facts=store.present(),
            analyzers_executed=tuple(executions),
            warnings=tuple(warnings),
        )

    @staticmethod
    def _execute_analyzer(
        analyzer: Analyzer,
        context: RepositoryContext,
        store: FactStore,
        warnings: list[WarningMessage],
        executions: list[AnalyzerExecution],
        telemetry: TelemetryWriter | None,
    ) -> None:
        started = time.perf_counter()
        try:
            result = analyzer.analyze(context, store)
        except PolicyError:
            if telemetry:
                telemetry.emit(
                    "analyzer_executed",
                    analyzer_id=analyzer.descriptor().id,
                    success=False,
                    facts_produced=0,
                )
            raise
        except Exception as exc:
            if telemetry:
                telemetry.emit(
                    "analyzer_executed",
                    analyzer_id=analyzer.descriptor().id,
                    success=False,
                    facts_produced=0,
                )
            raise PolicyError(
                "ANALYZER_FAILED",
                f"Analyzer '{analyzer.descriptor().id}' failed.",
                {"analyzer_id": analyzer.descriptor().id},
            ) from exc
        for fact in result.facts:
            store.add(fact)
            if telemetry:
                telemetry.emit("fact_produced", fact_key=fact.key, producer_id=fact.producer_id)
        for unavailable in result.unavailable:
            store.mark_unavailable(unavailable)
        warnings.extend(result.warnings)
        execution = AnalyzerExecution(
            analyzer_id=analyzer.descriptor().id,
            duration_ms=(time.perf_counter() - started) * 1000,
            success=True,
            facts_produced=len(result.facts),
        )
        executions.append(execution)
        if telemetry:
            telemetry.emit(
                "analyzer_executed",
                analyzer_id=execution.analyzer_id,
                success=True,
                facts_produced=execution.facts_produced,
            )


def parse_request(data: object) -> ResolveRequest:
    try:
        return ResolveRequest.model_validate(data)
    except ValidationError as exc:
        raise PolicyError("INVALID_ARGUMENT", "Resolution request is invalid.", {}) from exc
