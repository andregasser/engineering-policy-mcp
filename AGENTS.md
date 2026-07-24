# AGENTS.md

## Mission

Implement the Engineering Policy MCP proof of concept described in
`docs/spec/implementation-brief.md`.

## Authority

- The implementation brief is authoritative.
- Supporting documents in `docs/spec/` provide detailed contracts.
- Documents in `docs/legacy/` are background and must not expand the PoC.
- Do not implement excluded or future capabilities.

## Required workflow

1. Read the complete implementation brief and relevant supporting specs.
2. Inspect the current repository before changing files.
3. Create and maintain a concise implementation plan.
4. Implement one working vertical slice incrementally.
5. Run focused tests after each layer.
6. Keep CLI and MCP as thin adapters over one application service.
7. Before completion, run:

   ```bash
   uv sync
   uv run ruff check .
   uv run mypy src tests
   uv run pytest
   ```

8. Perform a final review for correctness, security, determinism, scope,
   error handling and test quality. Fix all material findings.

## Engineering constraints

- Python 3.12
- `uv` for dependency and project management
- official Python MCP SDK
- Pydantic at external boundaries
- frozen dataclasses in the domain
- deterministic output ordering
- unknown facts are never interpreted as false
- no `shell=True`
- no commands or code loaded from policy YAML
- no network access
- no source content, full diffs or secrets in telemetry or evidence
- no filesystem access outside the resolved repository root during analysis
- do not follow symlinks during repository scanning
- `.engineering-policy/**` must never contribute analysis facts
- stdout is reserved for protocol or CLI JSON output

## Scope discipline

Do not add:

- additional MCP tools
- additional lifecycle events
- host hooks
- HTTP transport
- OpenAPI or migration analysis
- Java AST parsing
- Maven or Gradle execution
- verifier APIs
- remote policy repositories
- dashboards
- PyPI publication
- Python entry-point plugin discovery

Clean extension points are welcome only where required by the current design.
Do not build speculative abstractions.

## Completion report

Report:

- what was implemented
- test and quality-command results
- acceptance-scenario results
- agent-evaluation readiness and any evaluation work still requiring separate runs
- deliberate exclusions
- remaining risks or assumptions

Do not claim completion while a required command or acceptance scenario fails.
