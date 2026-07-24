# Initial prompt for Codex

Implement the Engineering Policy MCP proof of concept contained in this
repository.

Begin by reading:

1. `AGENTS.md`
2. `docs/spec/implementation-brief.md`
3. the supporting contracts in `docs/spec/`

The implementation brief is authoritative when documents conflict. The files
under `docs/legacy/` are product background only and must not expand the PoC.

Work autonomously through the complete vertical slice:

- establish the Python 3.12/uv project
- implement the domain and boundary models
- validate and load the YAML policy catalog
- compose the configured Company and Java-team policy sets
- implement facts and unknown semantics
- implement and plan the three required analyzers
- resolve the two supplied policies deterministically
- expose the shared application service through the CLI and MCP adapters
- emit safe JSONL telemetry
- implement all required tests and documentation
- prepare the fixtures and result template for the later agent-behavior evaluation

Keep the implementation deliberately small. Do not implement excluded roadmap
features.

Run all Definition of Done commands and the five acceptance scenarios. Then
perform a comprehensive final review and fix material findings before reporting
completion.

Ask a question only when a genuinely blocking contradiction remains after
applying the documented precedence rules. Otherwise, make the smallest
reasonable implementation choice, record it briefly, and continue.
