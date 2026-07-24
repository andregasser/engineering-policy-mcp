# Engineering Policy MCP – Codex Implementation Brief

**Status:** Authoritative PoC specification  
**Version:** 0.6  
**Purpose:** Implementation handoff for Codex  
**Platform:** Python 3.12  
**Target repositories:** Java, optionally Kotlin  
**Transport:** Local MCP server over `stdio`

## 1. Document authority

This brief defines the implementation scope of the first PoC.

If the earlier documents conflict, use this precedence:

1. This implementation brief
2. `mcp-api.md`
3. `facts.md`
4. `plugin-sdk.md`
5. `architecture.md`
6. `adrs.md`
7. `../legacy/concept-v0.4-addendum.md`
8. `../legacy/concept-v0.3.md`

The v0.3 concept remains the product vision and post-PoC roadmap. It must not be
used to expand the first PoC.

## 2. PoC objective

Implement one end-to-end vertical slice:

```text
Java Git worktree
    → required analyzers
    → typed engineering facts
    → deterministic policy resolution
    → equivalent CLI and MCP results
    → JSONL telemetry
```

The demo must show:

1. A small Java production change activates the testing policy.
2. A large Java production change additionally activates the comprehensive
   review policy.
3. A README-only change activates neither production policy.
4. An invalid Git base revision returns a structured error.
5. CLI and MCP return semantically equivalent results.

## 3. Fixed scope

### Included

- Python 3.12 project managed with `uv`
- official Python MCP SDK
- YAML policy catalog
- JSON Schema validation for policy YAML
- immutable domain models
- `FactStore` with present, missing and unavailable semantics
- analyzer registry and minimal dependency planner
- `RepositoryTechnologyAnalyzer`
- `GitChangeAnalyzer`
- `ChangeSizeAnalyzer`
- deterministic policy resolver
- shared application service
- CLI command `resolve`
- MCP tool `resolve_policies`
- JSONL telemetry
- composition of Company and Java-team policy sets
- unit and integration tests
- temporary/fixture Java Git repository
- a plan and fixtures for a small, repeatable agent-behavior evaluation
- user documentation needed to run the demo

### Excluded

- `task_start` and `before_commit`
- `explain_policy` and `inspect_facts`
- OpenAPI or database migration analysis
- Java AST parsing
- Maven or Gradle execution
- verifier API
- host hooks and lifecycle adapters
- HTTP transport
- remote policy repositories
- policy overrides and exceptions
- dashboard or OpenTelemetry export
- runtime plugin downloads
- packaging or publishing to PyPI

Interfaces may leave clean extension points for excluded capabilities, but no
unused framework or speculative implementation should be added.

## 4. Canonical event

The PoC supports exactly:

```text
before_completion
```

Any other event returns `UNSUPPORTED_EVENT`.

## 5. Required policies

The repository must contain these two policies as YAML.

### 5.1 Java team: test production changes

```yaml
id: team.java.test-production-change
title: Test production changes
severity: mandatory
events:
  - before_completion
instruction: >
  Run the relevant automated tests for the changed production code and report
  the result before completing the task.
when:
  facts:
    - fact: repository.language.java
      operator: equals
      value: true
    - fact: change.production_files.count
      operator: greater_than_or_equal
      value: 1
parameters: {}
```

### 5.2 Comprehensive review

```yaml
id: company.comprehensive-review
title: Perform a comprehensive review
severity: mandatory
events:
  - before_completion
instruction: >
  Perform a comprehensive review covering correctness, regressions,
  architecture consistency, security, backward compatibility, test coverage
  and unnecessary complexity. Resolve all material findings before completing
  the task.
when:
  facts:
    - fact: change.substantial
      operator: equals
      value: true
parameters:
  review_areas:
    - correctness
    - regression_risk
    - architecture
    - security
    - backward_compatibility
    - test_coverage
    - unnecessary_complexity
```

Conditions are a flat logical AND. Implement only the operators required by
these policies:

- `equals`
- `greater_than_or_equal`

Supporting more operators belongs after the PoC.

## 6. Configuration defaults

Use a repository-local configuration file:

```text
.engineering-policy/config.yaml
```

Defaults:

```yaml
schema_version: 1

policy_sets:
  - company/baseline
  - teams/java

analysis:
  production_paths:
    - "src/main/**"
  test_paths:
    - "src/test/**"
  exclude_paths:
    - ".engineering-policy/**"
    - "target/**"
    - "build/**"
    - ".gradle/**"
    - ".idea/**"

  substantial_change:
    production_files: 10
    changed_lines: 500

telemetry:
  enabled: true
  path: ".engineering-policy/telemetry/events.jsonl"
```

`change.substantial` is true when at least one threshold is met:

```text
production file count >= production_files threshold
OR
total changed lines >= changed_lines threshold
```

Policy sets are loaded in configured order and then normalized by policy ID.
Policy IDs must be unique across all selected sets. A duplicate is a
`POLICY_SCHEMA_INVALID` configuration error. Overrides are not supported.

## 7. Git worktree semantics

- `repository_path` must be absolute after input normalization.
- It must resolve to a Git worktree root.
- `base_revision` defaults to `HEAD`.
- The target is always the current worktree.
- Changed paths are the de-duplicated union of:
  - staged changes
  - unstaged changes
  - untracked, non-ignored files
- Renames use the destination path for path classification.
- Deleted files retain their former path for path classification.
- Ignored files and paths outside the repository root are excluded.
- `.engineering-policy/**` is excluded so telemetry can never affect analysis.
- Path ordering in facts and responses is lexicographical.
- Git commands are invoked with argument arrays, timeouts and output limits.
- Never use `shell=True`.

Line counts:

- For tracked files, calculate the diff from `base_revision` to the current
  combined worktree state so staged and unstaged edits are not double-counted.
- For untracked regular text files, count their lines as additions.
- For untracked binary files, count zero lines and emit a warning.
- For an untracked file larger than 10 MiB, count zero lines and emit a warning.
- Aggregate line totals are additions plus deletions.

Path classification order:

1. excluded
2. test
3. production
4. other

Use GitWildMatch-compatible matching via `pathspec`.

## 8. Repository technology semantics

The technology analyzer uses repository file presence only. It does not execute
build tools.

- Java is true when at least one non-excluded `.java` file exists.
- Kotlin is true when at least one non-excluded `.kt` file exists.
- Build system is:
  - `maven` when Maven build files exist and Gradle build files do not
  - `gradle` when Gradle build files exist and Maven build files do not
  - `null` when neither exists
  - unavailable with a warning when both are detected

Repository scanning must remain inside the resolved repository root and skip
`.git` plus configured excluded paths. It must not follow symbolic links.

## 9. Canonical facts

Implement these facts:

| Fact | Type | Producer |
|---|---|---|
| `repository.language.java` | boolean | repository-technology |
| `repository.language.kotlin` | boolean | repository-technology |
| `repository.build_system` | string or null | repository-technology |
| `change.changed_paths` | list of strings | git-change |
| `change.files.count` | integer | git-change |
| `change.production_files.count` | integer | git-change |
| `change.test_files.count` | integer | git-change |
| `change.java.production_files.count` | integer | git-change |
| `change.lines.added` | integer | git-change |
| `change.lines.deleted` | integer | git-change |
| `change.lines.total` | integer | git-change |
| `change.substantial` | boolean | change-size |

Every present fact contains:

- key
- value
- value type
- producer ID
- confidence
- bounded evidence
- observation timestamp

Evidence may contain paths, Git command descriptions and aggregate threshold
information. It must not contain source file contents, complete diffs or
secrets.

## 10. Unknown semantics

Fact lookup has three states:

- `present`
- `missing`
- `unavailable`

A missing or unavailable fact is never interpreted as `false`.

If a policy condition cannot be evaluated:

- mandatory policy → add to `unresolved_policies`
- do not add it to `applicable_policies`
- include the missing/unavailable fact and reason

A known condition evaluating to false makes the policy not applicable. The PoC
does not need to return a public `not_applicable_policies` collection.

Use `FACT_UNAVAILABLE` only when the requested resolution cannot produce a
meaningful result at all. A fact unavailable for one policy is normally
represented by a successful response containing that policy under
`unresolved_policies`. Unexpected analyzer execution failures use
`ANALYZER_FAILED`.

## 11. Analyzer planning

For each resolution:

1. Load and validate the catalog.
2. Filter policies by event.
3. Collect facts referenced by candidate policies.
4. Resolve fact producers and their dependencies.
5. Reject analyzer dependency cycles.
6. Topologically sort required analyzers.
7. Execute each selected analyzer once.
8. Record present or unavailable facts.
9. Resolve policies.

Required dependencies:

```text
repository-technology → repository.language.java
git-change            → change.production_files.count
git-change            → change.lines.total
change-size           → change.substantial
```

`change-size` requires the Git aggregate facts.

The PoC registers built-in analyzers directly behind the Protocols described in
`plugin-sdk.md`.

Python entry-point discovery, separate plugin packages and runtime plugin
loading are explicitly excluded. They are post-PoC extensions.

## 12. Application API

CLI and MCP call the same application service. The service accepts:

```json
{
  "event": "before_completion",
  "repository_path": "/absolute/path/to/repository",
  "base_revision": "HEAD",
  "task_id": "optional-task-id"
}
```

The successful result follows `mcp-api.md`, uses API version `v1alpha1`, and
contains:

- event
- applicable policies
- unresolved policies
- produced facts
- analyzer executions
- warnings

Collections must have deterministic ordering:

- policies by policy ID
- facts by fact key
- analyzers by execution order
- warnings by creation order

Volatile fields such as timestamps and durations may differ. Semantic
equivalence tests must normalize only those documented volatile fields.

## 13. CLI contract

Required command:

```bash
engineering-policy resolve \
  --event before_completion \
  --repository . \
  --base HEAD
```

Requirements:

- JSON result on stdout
- diagnostics on stderr
- exit code `0` for successful resolution, including unresolved policies
- non-zero exit code for structured execution errors
- no traceback in normal user-facing output

## 14. MCP contract

Required tool:

```text
resolve_policies
```

Requirements:

- local `stdio` server
- no normal logs on stdout
- input and output follow `mcp-api.md`
- no Python traceback returned to the client
- MCP adapter contains no policy or analyzer business logic

## 15. Structured errors

Implement at least:

| Code | Scenario |
|---|---|
| `DEPENDENCY_NOT_INSTALLED` | Git executable missing |
| `NOT_A_GIT_REPOSITORY` | invalid repository |
| `INVALID_REVISION` | base revision cannot be resolved |
| `UNSUPPORTED_EVENT` | event other than `before_completion` |
| `POLICY_SCHEMA_INVALID` | invalid policy catalog |
| `FACT_UNAVAILABLE` | required fact cannot be produced |
| `ANALYZER_FAILED` | analyzer execution fails |
| `INVALID_ARGUMENT` | invalid input |

Errors use the envelope from `mcp-api.md`. Internal exception details may be
logged to stderr but are not exposed through MCP.

## 16. Telemetry

Write JSON Lines to the configured path. Telemetry is the only intentional
write to the target repository. Its complete path must be excluded from
repository analysis.

Required events:

- `policy_resolution_started`
- `analyzer_executed`
- `fact_produced`
- `policy_resolved`
- `policy_resolution_completed`

Every event includes:

- schema version
- event type
- timestamp
- optional task ID
- repository identifier that does not expose source content

Do not record:

- prompts
- source contents
- complete diffs
- secrets
- personal profiles
- claims that an agent followed a policy

Telemetry failure emits a warning and must not change policy resolution.
Telemetry is emitted by the application/telemetry layer, never as an analyzer
side effect.

## 17. Architecture constraints

- Frozen dataclasses for domain models
- Pydantic at CLI/MCP/config boundaries
- thin CLI and MCP adapters
- one shared application service
- analyzers are read-only and side-effect free
- deterministic core logic
- no network access
- no runtime code execution from YAML
- no access outside the repository root
- reject configured paths that escape the repository root after normalization
- do not follow symlinks during repository scanning
- subprocess timeout and output-size limits
- errors translated at the application boundary

## 18. Suggested project layout

```text
engineering-policy-mcp/
├── AGENTS.md
├── README.md
├── pyproject.toml
├── uv.lock
├── docs/
│   ├── implementation-brief.md
│   ├── architecture.md
│   ├── facts.md
│   ├── mcp-api.md
│   └── plugin-sdk.md
├── evaluation/
│   └── evaluation-plan.md
├── schemas/
│   └── policy.schema.json
├── policies/
│   ├── company/
│   │   └── baseline/
│   │       └── comprehensive-review.yaml
│   └── teams/
│       └── java/
│           └── test-production-change.yaml
├── src/
│   └── engineering_policy/
│       ├── application/
│       ├── analyzers/
│       ├── catalog/
│       ├── cli/
│       ├── domain/
│       ├── mcp/
│       ├── plugins/
│       ├── resolver/
│       └── telemetry/
└── tests/
    ├── integration/
    ├── unit/
    └── fixtures/
```

Codex may adjust internal module filenames when this improves cohesion, but it
must preserve the architectural boundaries.

## 19. Required tests

### Unit tests

- policy YAML parsing and schema rejection
- duplicate policy ID rejection
- fact present/missing/unavailable behavior
- required condition operators
- flat AND conditions
- mandatory unresolved policy behavior
- change-size threshold boundary (`>=`)
- analyzer dependency planning and cycle detection
- deterministic ordering
- telemetry serialization and failure isolation
- telemetry path excluded from analyzed changes
- structured error mapping

### Analyzer contract tests

- descriptor validity
- declared fact names and types
- deterministic output
- missing Git behavior
- repository-root confinement
- staged, unstaged and untracked union
- no double-counting of paths or lines
- ignored file exclusion
- production/test/excluded path precedence
- symlink non-traversal
- oversized untracked-file handling

### Integration acceptance tests

1. **Small Java production change**
   - testing policy applicable
   - review policy not applicable

2. **Large Java production change**
   - testing policy applicable
   - review policy applicable
   - reason references the threshold evidence

3. **README-only change**
   - neither production policy applicable

4. **Invalid revision**
   - `INVALID_REVISION`
   - no traceback in public result

5. **CLI/MCP equivalence**
   - identical semantic result after documented volatile-field normalization

### Agent-behavior evaluation

Prepare the fixtures and result template for the evaluation defined in
`evaluation/evaluation-plan.md`. The experiment itself consists of separate
Codex runs after the technical implementation is complete; it is not a new
platform component.

## 20. Definition of done

The implementation is complete only when:

- `uv sync` succeeds
- `uv run ruff check .` succeeds
- `uv run mypy src tests` succeeds
- `uv run pytest` succeeds
- all five acceptance scenarios pass
- the agent-evaluation fixtures, instructions and result template are ready
- the README contains exact setup, CLI and MCP demo instructions
- no excluded capability was added
- a final review checks correctness, security, determinism, scope and test
  quality

## 21. Instructions for Codex

When this brief is handed to Codex:

1. Inspect all supplied documents and existing files.
2. Treat this brief as authoritative for conflicts.
3. Create a short implementation plan before editing.
4. Implement the vertical slice incrementally.
5. Run targeted tests after each layer.
6. Run the full Definition of Done before completion.
7. Perform a comprehensive final review and fix material findings.
8. Report:
   - implemented capabilities
   - test and quality results
   - deliberate scope exclusions
   - remaining risks or assumptions

Do not ask for design choices that this brief already resolves. Stop and ask
only if a genuinely blocking contradiction remains.
