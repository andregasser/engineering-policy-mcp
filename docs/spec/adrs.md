# PoC Architecture Decisions

## ADR-001: Python 3.12 and uv

The platform uses Python 3.12, the official Python MCP SDK and `uv`.

## ADR-002: Deterministic facts and resolution

Analyzers produce typed facts. Policies never inspect repositories directly.
No LLM runs inside the server.

## ADR-003: One application service

CLI and MCP are thin adapters over the same orchestration service.

## ADR-004: Built-in analyzers for the PoC

The analyzer Protocol is implemented, but built-in analyzers are registered
directly. Entry-point plugin discovery is deferred.

## ADR-005: Company and team composition

The PoC combines Company and Java-team policy sets without overrides.

## ADR-006: Safe JSONL telemetry

Telemetry is a cross-cutting application concern. Its repository-local path is
excluded from analysis so observation cannot change policy outcomes.

## ADR-007: Agent behavior is evaluated separately

The platform reports selected policies, not whether an agent obeyed them.
Adherence is assessed through a small repeatable experiment rather than an
unproven telemetry claim.
