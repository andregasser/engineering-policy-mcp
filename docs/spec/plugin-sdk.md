# Analyzer Extension Contract

The PoC has an internal analyzer extension boundary. It does not implement
runtime plugin discovery.

## Analyzer protocol

```python
class Analyzer(Protocol):
    def descriptor(self) -> AnalyzerDescriptor: ...
    def supports(self, context: RepositoryContext) -> bool: ...
    def analyze(
        self,
        context: AnalysisContext,
        facts: FactStore,
    ) -> AnalysisResult: ...
```

Descriptor fields:

```python
@dataclass(frozen=True)
class AnalyzerDescriptor:
    id: str
    provides: frozenset[str]
    requires: frozenset[str]
    cost: AnalyzerCost
    priority: int = 0
```

## Contract

Analyzers must be:

- read-only
- deterministic for identical repository state and configuration
- side-effect free
- explicit about unavailable dependencies
- bounded when invoking subprocesses
- confined to the normalized repository root

The planner selects only analyzers required by the candidate policies,
recursively adds dependencies, rejects cycles, topologically sorts the result
and executes every selected analyzer once.

## Deferred

The following do not belong to the PoC:

- Python package entry points
- separately distributed analyzer packages
- runtime plugin loading
- remote plugin downloads
- verifier or context-source contributions
