# Engineering Policy MCP

This proof of concept resolves situational engineering policies for the current
state of a local Java Git worktree. It exposes the same deterministic
application service through a JSON CLI and one MCP `stdio` tool.

## Requirements and setup

- macOS or Linux
- Git
- `uv`

Install the locked Python 3.12 environment:

```bash
uv sync
```

No build tool is executed and no network is used by the running resolver.

## CLI demo

Run against any local Git worktree:

```bash
uv run engineering-policy resolve \
  --event before_completion \
  --repository /absolute/path/to/repository \
  --base HEAD
```

The CLI prints one JSON result to stdout. Errors use the same structured
`v1alpha1` envelope and a non-zero exit code. Diagnostics never contaminate
stdout.

The target repository may provide `.engineering-policy/config.yaml`:

```yaml
schema_version: 1
policy_sets:
  - company/baseline
  - teams/java
analysis:
  production_paths: ["src/main/**"]
  test_paths: ["src/test/**"]
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

These values are also the defaults when the file is absent.

## MCP server

Start the local `stdio` server with:

```bash
uv run engineering-policy-mcp
```

Example Codex MCP configuration:

```toml
[mcp_servers.engineering-policy]
command = "uv"
args = ["run", "--directory", "/absolute/path/to/engineering-policy-mcp", "engineering-policy-mcp"]
```

The server exposes exactly one tool:

```text
resolve_policies(
  event="before_completion",
  repository_path="/absolute/path/to/repository",
  base_revision="HEAD",
  task_id="optional"
)
```

Only `before_completion` is supported. The target is always the combined
current worktree: staged, unstaged and untracked non-ignored changes.

## Policies

- `team.java.test-production-change` applies when the repository contains Java
  and at least one production file changed.
- `company.comprehensive-review` applies when at least 10 production files or
  at least 500 total lines changed.

Missing or unavailable facts are not interpreted as false. A mandatory policy
whose conditions cannot be evaluated appears under `unresolved_policies`.

## Quality and acceptance tests

```bash
uv sync
uv run ruff check .
uv run mypy src tests
uv run pytest
```

The integration suite creates temporary Java Git repositories and covers the
small-production, large-production, README-only, invalid-revision and
CLI/service-equivalence scenarios. The separate agent-behavior experiment is
described in `evaluation/evaluation-plan.md`; it is not performed by the
resolver.

## Safety and scope

Repository analysis stays inside the resolved Git root, skips symlinks and
never executes Maven, Gradle or code from policy YAML. Evidence and telemetry
contain bounded metadata, never source content or complete diffs. Runtime
telemetry is the only intentional target-repository write and its path is
excluded from analysis.
