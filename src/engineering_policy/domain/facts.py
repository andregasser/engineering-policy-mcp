from __future__ import annotations

from engineering_policy.domain.models import Fact, FactLookup, FactState, UnavailableFact


class FactStore:
    def __init__(self) -> None:
        self._facts: dict[str, Fact] = {}
        self._unavailable: dict[str, UnavailableFact] = {}

    def add(self, fact: Fact) -> None:
        if fact.key in self._facts or fact.key in self._unavailable:
            raise ValueError(f"Fact '{fact.key}' was recorded more than once.")
        self._facts[fact.key] = fact

    def mark_unavailable(self, unavailable: UnavailableFact) -> None:
        if unavailable.key in self._facts or unavailable.key in self._unavailable:
            raise ValueError(f"Fact '{unavailable.key}' was recorded more than once.")
        self._unavailable[unavailable.key] = unavailable

    def lookup(self, key: str) -> FactLookup:
        if fact := self._facts.get(key):
            return FactLookup(state=FactState.PRESENT, fact=fact)
        if unavailable := self._unavailable.get(key):
            return FactLookup(state=FactState.UNAVAILABLE, reason=unavailable.reason)
        return FactLookup(state=FactState.MISSING, reason="No analyzer produced this fact.")

    def present(self) -> tuple[Fact, ...]:
        return tuple(self._facts[key] for key in sorted(self._facts))
