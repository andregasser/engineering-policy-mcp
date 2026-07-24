from __future__ import annotations

from engineering_policy.domain.facts import FactStore
from engineering_policy.domain.models import (
    ApplicablePolicy,
    FactState,
    MatchedReason,
    Policy,
    UnresolvedPolicy,
    UnresolvedReason,
)


def _evaluate(actual: object, operator: str, expected: object) -> bool:
    if operator == "equals":
        return type(actual) is type(expected) and actual == expected
    if operator == "greater_than_or_equal":
        if (
            not isinstance(actual, int)
            or isinstance(actual, bool)
            or not isinstance(expected, int)
            or isinstance(expected, bool)
        ):
            return False
        return actual >= expected
    raise ValueError(f"Unsupported operator '{operator}'.")


def resolve(
    policies: tuple[Policy, ...], facts: FactStore
) -> tuple[tuple[ApplicablePolicy, ...], tuple[UnresolvedPolicy, ...]]:
    applicable: list[ApplicablePolicy] = []
    unresolved: list[UnresolvedPolicy] = []
    for policy in sorted(policies, key=lambda item: item.id):
        matches: list[MatchedReason] = []
        unknowns: list[UnresolvedReason] = []
        known_false = False
        for condition in policy.conditions:
            lookup = facts.lookup(condition.fact)
            if lookup.state is not FactState.PRESENT or lookup.fact is None:
                unknowns.append(
                    UnresolvedReason(
                        fact=condition.fact,
                        state=lookup.state,
                        reason=lookup.reason or "Fact is unknown.",
                    )
                )
                continue
            if _evaluate(lookup.fact.value, condition.operator, condition.value):
                matches.append(
                    MatchedReason(
                        fact=condition.fact,
                        actual_value=lookup.fact.value,
                        operator=condition.operator,
                        expected_value=condition.value,
                        evidence=lookup.fact.evidence,
                    )
                )
            else:
                known_false = True
        if known_false:
            continue
        if unknowns:
            if policy.severity == "mandatory":
                unresolved.append(UnresolvedPolicy(policy=policy, reasons=tuple(unknowns)))
            continue
        applicable.append(ApplicablePolicy(policy=policy, matched_reasons=tuple(matches)))
    return tuple(applicable), tuple(unresolved)
