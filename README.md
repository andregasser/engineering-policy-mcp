# Engineering Policy MCP

This repository contains the implementation specification and Codex handoff for
the Engineering Policy MCP PoC. The initial revision intentionally contains no
implementation.

## Start here

1. Read `AGENTS.md`.
2. Read `docs/spec/implementation-brief.md`.
3. Use `CODEX-PROMPT.md` as the initial task for Codex.
4. Treat files in `docs/legacy/` as background only.

## Authority

`docs/spec/implementation-brief.md` is authoritative. Its document-precedence
section resolves conflicts with every other supplied document.

## Expected result

Codex should implement a runnable Python 3.12 project in this directory with:

- deterministic policy resolution
- three analyzers
- Company and Java-team policy composition
- a shared application layer
- one CLI command
- one MCP tool
- JSONL telemetry
- complete unit and integration tests
- a documented plan for agent-behavior evaluation

The exact scope and Definition of Done are in the implementation brief.

## Package contents

```text
.
├── AGENTS.md
├── CODEX-PROMPT.md
├── README.md
├── docs/
│   ├── spec/
│   └── legacy/
├── evaluation/
│   └── evaluation-plan.md
└── policies/
    ├── company/baseline/
    └── teams/java/
```

The sample policies are input specifications. Codex may move them into the
final project layout prescribed by the implementation brief.
