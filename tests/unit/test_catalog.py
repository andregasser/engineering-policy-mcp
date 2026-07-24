from __future__ import annotations

from pathlib import Path

import pytest

from engineering_policy.catalog import PolicyCatalog
from engineering_policy.domain.errors import PolicyError


def project_copy(tmp_path: Path) -> Path:
    root = tmp_path / "project"
    (root / "schemas").mkdir(parents=True)
    source_root = Path(__file__).resolve().parents[2]
    (root / "schemas/policy.schema.json").write_bytes(
        (source_root / "schemas/policy.schema.json").read_bytes()
    )
    return root


def valid_policy(identifier: str) -> str:
    return f"""
id: {identifier}
title: Test
severity: mandatory
events: [before_completion]
instruction: Run tests.
when:
  facts:
    - fact: repository.language.java
      operator: equals
      value: true
parameters: {{}}
"""


def test_loads_and_orders_policy_catalog(tmp_path: Path) -> None:
    root = project_copy(tmp_path)
    directory = root / "policies/test"
    directory.mkdir(parents=True)
    (directory / "z.yaml").write_text(valid_policy("z"), encoding="utf-8")
    (directory / "a.yaml").write_text(valid_policy("a"), encoding="utf-8")

    policies = PolicyCatalog(root).load(("test",))

    assert [policy.id for policy in policies] == ["a", "z"]


def test_rejects_schema_violation(tmp_path: Path) -> None:
    root = project_copy(tmp_path)
    directory = root / "policies/test"
    directory.mkdir(parents=True)
    (directory / "bad.yaml").write_text("id: incomplete\n", encoding="utf-8")

    with pytest.raises(PolicyError, match="invalid") as raised:
        PolicyCatalog(root).load(("test",))
    assert raised.value.code == "POLICY_SCHEMA_INVALID"


def test_rejects_duplicate_ids_across_sets(tmp_path: Path) -> None:
    root = project_copy(tmp_path)
    for policy_set in ("one", "two"):
        directory = root / "policies" / policy_set
        directory.mkdir(parents=True)
        (directory / "policy.yaml").write_text(valid_policy("duplicate"), encoding="utf-8")

    with pytest.raises(PolicyError) as raised:
        PolicyCatalog(root).load(("one", "two"))
    assert raised.value.code == "POLICY_SCHEMA_INVALID"
