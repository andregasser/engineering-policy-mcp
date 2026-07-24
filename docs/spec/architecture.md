# PoC Architecture

## Pipeline

```text
Repository
  → analyzer planner
  → built-in analyzers
  → typed FactStore
  → policy resolver
  → shared application service
  → CLI or MCP adapter
```

## Boundaries

- Domain: immutable facts, policies, conditions and resolution results.
- Catalog: configuration and policy loading plus schema validation.
- Analyzers: read-only deterministic fact producers.
- Resolver: pure evaluation of candidate policies against facts.
- Application: orchestration, error translation and telemetry.
- CLI/MCP: input/output adapters with no business logic.

## PoC analyzers

```text
repository-technology
git-change
change-size → requires Git aggregate facts
```

Analyzers are registered directly. Plugin discovery and separate plugin
packages are post-PoC work.

## Policy composition

The PoC loads:

```text
company/baseline
teams/java
```

The sets are combined without overrides. Duplicate policy IDs are invalid.

## Safety

- Repository analysis is read-only.
- Telemetry is written separately and excluded from analysis.
- Repository scans do not follow symlinks.
- Normalized paths may not escape the repository root.
- Git is executed without a shell, with time and output bounds.
- MCP over `stdio` reserves stdout for protocol messages.
