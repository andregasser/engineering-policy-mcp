from __future__ import annotations

from typing import Any

from engineering_policy import API_VERSION
from engineering_policy.domain.errors import PolicyError
from engineering_policy.domain.models import Evidence, Policy, Resolution


def _evidence(item: Evidence) -> dict[str, Any]:
    result: dict[str, Any] = {"kind": item.kind, "description": item.description}
    if item.paths:
        result["paths"] = list(item.paths)
    if item.details:
        result["details"] = dict(item.details)
    return result


def _policy(policy: Policy) -> dict[str, Any]:
    return {
        "id": policy.id,
        "title": policy.title,
        "severity": policy.severity,
        "instruction": policy.instruction,
        "parameters": dict(policy.parameters),
        "source_policy_set": policy.source_policy_set,
        "source_path": policy.source_path,
    }


def serialize_resolution(resolution: Resolution) -> dict[str, Any]:
    return {
        "api_version": API_VERSION,
        "event": resolution.event,
        "applicable_policies": [
            {
                **_policy(item.policy),
                "matched_reasons": [
                    {
                        "fact": reason.fact,
                        "actual_value": reason.actual_value,
                        "operator": reason.operator,
                        "expected_value": reason.expected_value,
                        "evidence": [_evidence(value) for value in reason.evidence],
                    }
                    for reason in item.matched_reasons
                ],
            }
            for item in resolution.applicable_policies
        ],
        "unresolved_policies": [
            {
                **_policy(item.policy),
                "reasons": [
                    {"fact": reason.fact, "state": reason.state.value, "reason": reason.reason}
                    for reason in item.reasons
                ],
            }
            for item in resolution.unresolved_policies
        ],
        "facts": [
            {
                "key": fact.key,
                "value": fact.value,
                "value_type": fact.value_type.value,
                "producer_id": fact.producer_id,
                "confidence": fact.confidence,
                "evidence": [_evidence(value) for value in fact.evidence],
                "observed_at": fact.observed_at.isoformat(),
            }
            for fact in resolution.facts
        ],
        "analyzers_executed": [
            {
                "analyzer_id": item.analyzer_id,
                "duration_ms": item.duration_ms,
                "success": item.success,
                "facts_produced": item.facts_produced,
            }
            for item in resolution.analyzers_executed
        ],
        "warnings": [
            {"code": warning.code, "message": warning.message} for warning in resolution.warnings
        ],
    }


def serialize_error(error: PolicyError) -> dict[str, Any]:
    return {
        "api_version": API_VERSION,
        "error": {
            "code": error.code,
            "message": error.message,
            "details": error.details,
            "retryable": error.retryable,
        },
    }
