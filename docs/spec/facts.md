# Canonical PoC Facts

## Model

Every present fact has:

- `key`
- `value`
- `value_type`
- `producer_id`
- `confidence`
- bounded `evidence`
- `observed_at`

Fact lookup states:

- `present`
- `missing`
- `unavailable`

Missing and unavailable are never equivalent to `false`.

## Catalog

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

No commit, OpenAPI, migration or host-context facts belong to this PoC.

## Path classification

Order:

1. excluded
2. test
3. production
4. other

Default exclusions include:

```yaml
- ".engineering-policy/**"
- "target/**"
- "build/**"
- ".gradle/**"
- ".idea/**"
```

Use GitWildMatch-compatible matching. Changed paths are unique and sorted.

## Evidence

Evidence may contain paths, Git operation descriptions and aggregate threshold
information. It must never contain source contents, complete diffs, secrets or
unbounded subprocess output.
