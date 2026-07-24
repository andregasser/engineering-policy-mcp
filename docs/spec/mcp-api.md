# MCP and Application API Contract

## Version

Every success and error response uses:

```text
v1alpha1
```

## Tool

The PoC exposes exactly one MCP tool:

```text
resolve_policies
```

### Input

```json
{
  "event": "before_completion",
  "repository_path": "/absolute/path/to/repository",
  "base_revision": "HEAD",
  "task_id": "optional-task-id"
}
```

Only `before_completion` is supported.

### Success

```json
{
  "api_version": "v1alpha1",
  "event": "before_completion",
  "applicable_policies": [],
  "unresolved_policies": [],
  "facts": [],
  "analyzers_executed": [],
  "warnings": []
}
```

Applicable policies contain:

- ID, title, severity and instruction
- parameters
- matched reasons with fact, actual value, operator, expected value and evidence
- source policy set and path

Unresolved policies identify the missing or unavailable facts and reasons.

Analyzer executions contain:

- analyzer ID
- duration in milliseconds
- success
- number of facts produced

Policies and facts use deterministic ordering. Timestamps and durations are
volatile and may be normalized for semantic-equivalence tests.

## CLI equivalence

```bash
engineering-policy resolve \
  --event before_completion \
  --repository . \
  --base HEAD
```

The CLI and MCP adapter call the same application service and return
semantically equivalent results.

## Errors

```json
{
  "api_version": "v1alpha1",
  "error": {
    "code": "INVALID_REVISION",
    "message": "Git revision 'missing' could not be resolved.",
    "details": {
      "revision": "missing"
    },
    "retryable": false
  }
}
```

Required codes:

- `DEPENDENCY_NOT_INSTALLED`
- `NOT_A_GIT_REPOSITORY`
- `INVALID_REVISION`
- `UNSUPPORTED_EVENT`
- `POLICY_SCHEMA_INVALID`
- `FACT_UNAVAILABLE`
- `ANALYZER_FAILED`
- `INVALID_ARGUMENT`

A fact unavailable only for one policy normally produces a successful response
with an unresolved policy. `FACT_UNAVAILABLE` is reserved for a request that
cannot produce a meaningful resolution.

No traceback is returned through MCP. Normal logs use stderr.
