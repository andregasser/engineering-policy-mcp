from __future__ import annotations

from datetime import UTC, datetime

from engineering_policy.domain.facts import FactStore
from engineering_policy.domain.models import (
    Condition,
    Evidence,
    Fact,
    FactState,
    Policy,
    UnavailableFact,
    ValueType,
)
from engineering_policy.resolver import resolve


def fact(key: str, value: bool | int) -> Fact:
    return Fact(
        key=key,
        value=value,
        value_type=ValueType.BOOLEAN if isinstance(value, bool) else ValueType.INTEGER,
        producer_id="test",
        confidence=1.0,
        evidence=(Evidence(kind="test", description="bounded"),),
        observed_at=datetime.now(UTC),
    )


def policy(*conditions: Condition) -> Policy:
    return Policy(
        id="policy",
        title="Policy",
        severity="mandatory",
        events=("before_completion",),
        instruction="Do the thing.",
        conditions=conditions,
        parameters=(),
        source_policy_set="test",
        source_path="policy.yaml",
    )


def test_fact_store_distinguishes_present_missing_and_unavailable() -> None:
    store = FactStore()
    store.add(fact("present", False))
    store.mark_unavailable(UnavailableFact("unavailable", "test", "failed safely"))

    assert store.lookup("present").state is FactState.PRESENT
    assert store.lookup("missing").state is FactState.MISSING
    assert store.lookup("unavailable").state is FactState.UNAVAILABLE


def test_flat_and_supports_required_operators() -> None:
    store = FactStore()
    store.add(fact("java", True))
    store.add(fact("files", 1))
    candidate = policy(
        Condition("java", "equals", True),
        Condition("files", "greater_than_or_equal", 1),
    )

    applicable, unresolved = resolve((candidate,), store)

    assert [item.policy.id for item in applicable] == ["policy"]
    assert unresolved == ()
    assert len(applicable[0].matched_reasons) == 2


def test_known_false_wins_over_unknown_in_flat_and() -> None:
    store = FactStore()
    store.add(fact("java", False))
    candidate = policy(
        Condition("java", "equals", True),
        Condition("files", "greater_than_or_equal", 1),
    )

    applicable, unresolved = resolve((candidate,), store)

    assert applicable == ()
    assert unresolved == ()


def test_mandatory_policy_with_unknown_fact_is_unresolved() -> None:
    applicable, unresolved = resolve((policy(Condition("unknown", "equals", False)),), FactStore())

    assert applicable == ()
    assert unresolved[0].reasons[0].state is FactState.MISSING
