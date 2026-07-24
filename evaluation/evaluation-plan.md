# Agent-Behavior Evaluation

## Goal

Determine whether situational MCP policies improve Codex behavior compared
with no policy support and static repository instructions.

This is a manual PoC experiment. Do not build an evaluation platform.
Run it after the technical implementation is complete, using separate Codex
sessions so the variants remain independent.

## Variants

Run the same tasks under three conditions:

| Variant | Repository instructions | Policy MCP |
|---|---|---:|
| A – Baseline | no engineering policies | no |
| B – Static | both complete policy texts in `AGENTS.md` | no |
| C – MCP | short bootstrap instruction only | yes |

## Tasks

1. Small Java production-code change.
2. Large Java production-code change above a configured threshold.
3. README-only change.

Use identical starting repositories and prompts for every variant. Run each
combination at least three times if time permits.

## Observations

Record for every run:

- whether `resolve_policies` was called when available
- selected policies
- whether relevant automated tests were run
- whether a comprehensive review was performed
- review areas covered
- material findings identified
- material findings fixed before completion
- irrelevant policy actions performed
- resolver duration
- policy instruction characters delivered to the agent
- unresolved policies and warnings

Do not claim that telemetry proves adherence. Adherence is determined from the
recorded agent trace and resulting repository state.

## Metrics

```text
Invocation rate =
  eligible MCP runs with resolve_policies call / eligible MCP runs

Mandatory adherence rate =
  completed mandatory actions / applicable mandatory actions

False-positive action rate =
  irrelevant policy actions / all policy-driven actions

Selection precision =
  relevant policies selected / all selected policies

Context reduction =
  1 - dynamic policy characters / static policy characters
```

Also report:

- median resolver latency
- unresolved-policy rate
- number of material review findings fixed

## Success criteria

The PoC is promising when:

- policy selection is correct in all fixture scenarios
- MCP invocation is reliable enough to continue testing
- MCP adherence is at least as good as static instructions
- README-only changes do not trigger production actions
- dynamic delivery reduces irrelevant policy context
- median resolver latency is acceptable for interactive use

Do not invent a fixed latency target before measuring the fixture repository.
Report the observed value and its practical impact.

## Result template

Create `evaluation/results.md`:

```markdown
# Evaluation Results

## Environment

## Raw runs

| Run | Variant | Task | MCP called | Policies | Tests | Review | Findings fixed | Duration |
|---|---|---|---:|---|---:|---:|---:|---:|

## Metrics

## Observations

## Limitations

## Recommendation
```
