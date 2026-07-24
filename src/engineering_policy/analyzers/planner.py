from __future__ import annotations

from engineering_policy.analyzers.base import Analyzer
from engineering_policy.domain.errors import PolicyError


def plan(required_facts: set[str], analyzers: tuple[Analyzer, ...]) -> tuple[Analyzer, ...]:
    producer: dict[str, Analyzer] = {}
    for analyzer in analyzers:
        for fact in analyzer.descriptor().provides:
            if fact in producer:
                raise PolicyError(
                    "ANALYZER_FAILED", f"Multiple analyzers provide '{fact}'.", {"fact": fact}
                )
            producer[fact] = analyzer

    selected: dict[str, Analyzer] = {}

    def select_fact(fact: str) -> None:
        analyzer = producer.get(fact)
        if analyzer is None:
            return
        descriptor = analyzer.descriptor()
        if descriptor.id in selected:
            return
        selected[descriptor.id] = analyzer
        for dependency in sorted(descriptor.requires):
            select_fact(dependency)

    for fact in sorted(required_facts):
        select_fact(fact)

    ordered: list[Analyzer] = []
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(analyzer: Analyzer) -> None:
        descriptor = analyzer.descriptor()
        if descriptor.id in visiting:
            raise PolicyError(
                "ANALYZER_FAILED",
                "Analyzer dependency cycle detected.",
                {"analyzer_id": descriptor.id},
            )
        if descriptor.id in visited:
            return
        visiting.add(descriptor.id)
        dependencies = {
            producer[fact].descriptor().id: producer[fact]
            for fact in descriptor.requires
            if fact in producer and producer[fact].descriptor().id in selected
        }
        for dependency in sorted(
            dependencies.values(),
            key=lambda item: (item.descriptor().priority, item.descriptor().id),
        ):
            visit(dependency)
        visiting.remove(descriptor.id)
        visited.add(descriptor.id)
        ordered.append(analyzer)

    for analyzer in sorted(
        selected.values(), key=lambda item: (item.descriptor().priority, item.descriptor().id)
    ):
        visit(analyzer)
    return tuple(ordered)
