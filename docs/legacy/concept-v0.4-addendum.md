# Engineering Policy MCP – PoC Addendum (v0.4)

This document supplements the v0.3 concept with implementation decisions for
Codex.

## Fixed PoC Scope

Implement one vertical slice only.

Include: YAML policy catalog, GitChangeAnalyzer,
RepositoryTechnologyAnalyzer, ChangeSizeAnalyzer, Policy Resolver,
`resolve_policies` MCP tool, `resolve` CLI, JSONL telemetry.

Exclude: OpenAPI semantic analysis, Verifiers, Hook adapters, HTTP server,
remote repositories.

## Canonical Facts

- `repository.language.java`
- `repository.language.kotlin`
- `repository.build_system`
- `change.changed_paths`
- `change.files.count`
- `change.production_files.count`
- `change.test_files.count`
- `change.java.production_files.count`
- `change.lines.added`
- `change.lines.deleted`
- `change.lines.total`
- `change.substantial`
- `commit.requested`

## Git Semantics

Base revision defaults to `HEAD`. Target is the current worktree. Include
staged, unstaged and untracked files. Ignore ignored files and paths outside
the repository root.

## Technology Decisions

- Python 3.12
- uv
- Official Python MCP SDK
- Pydantic at boundaries
- Frozen dataclasses in domain
- Typer
- PyYAML
- jsonschema
- pytest
- ruff
- mypy

## Plugin Model

Discover plugins via Python entry points. Plugins contribute analyzers and
policy packs. Analyzer planner executes only analyzers required by candidate
policies.

## Structured Errors

- `DEPENDENCY_NOT_INSTALLED`
- `NOT_A_GIT_REPOSITORY`
- `INVALID_REVISION`
- `UNSUPPORTED_EVENT`
- `POLICY_SCHEMA_INVALID`
- `FACT_UNAVAILABLE`

## Acceptance Scenarios

- Small Java change
- Large Java change
- README-only change
- Invalid revision
- CLI and MCP produce equivalent semantic output

## Codex AGENTS.md

Implement only the documented PoC scope. Run ruff, mypy and pytest before
completion. CLI and MCP share one application layer. Never use `shell=True`.
Unknown facts are never interpreted as false.
