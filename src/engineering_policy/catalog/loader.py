from __future__ import annotations

import json
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

from engineering_policy.domain.errors import PolicyError
from engineering_policy.domain.models import Condition, JsonValue, Policy


def _as_json_mapping(value: object) -> dict[str, JsonValue]:
    if not isinstance(value, dict) or not all(isinstance(key, str) for key in value):
        raise TypeError("Expected a JSON object.")
    return value


class PolicyCatalog:
    def __init__(self, project_root: Path) -> None:
        self._project_root = project_root
        schema = json.loads((project_root / "schemas" / "policy.schema.json").read_text("utf-8"))
        self._validator = Draft202012Validator(schema)

    def load(self, policy_sets: tuple[str, ...]) -> tuple[Policy, ...]:
        policies: list[Policy] = []
        seen: set[str] = set()
        for policy_set in policy_sets:
            directory = self._project_root / "policies" / policy_set
            if not directory.is_dir():
                raise PolicyError(
                    "POLICY_SCHEMA_INVALID",
                    f"Policy set '{policy_set}' does not exist.",
                    {"policy_set": policy_set},
                )
            for path in sorted(directory.glob("*.yaml")):
                policy = self._load_one(path, policy_set)
                if policy.id in seen:
                    raise PolicyError(
                        "POLICY_SCHEMA_INVALID",
                        f"Duplicate policy ID '{policy.id}'.",
                        {"policy_id": policy.id},
                    )
                seen.add(policy.id)
                policies.append(policy)
        return tuple(sorted(policies, key=lambda item: item.id))

    def _load_one(self, path: Path, policy_set: str) -> Policy:
        try:
            raw_object = yaml.safe_load(path.read_text(encoding="utf-8"))
            raw = _as_json_mapping(raw_object)
        except (OSError, yaml.YAMLError, TypeError) as exc:
            raise self._schema_error(path) from exc
        errors = sorted(self._validator.iter_errors(raw), key=lambda error: list(error.path))
        if errors:
            raise self._schema_error(path)

        when = _as_json_mapping(raw["when"])
        conditions = tuple(
            Condition(
                fact=str(item["fact"]),
                operator=str(item["operator"]),
                value=item["value"],
            )
            for item in when["facts"]  # type: ignore[union-attr]
            if isinstance(item, dict)
        )
        parameters = _as_json_mapping(raw["parameters"])
        return Policy(
            id=str(raw["id"]),
            title=str(raw["title"]),
            severity=str(raw["severity"]),
            events=tuple(str(event) for event in raw["events"]),  # type: ignore[union-attr]
            instruction=str(raw["instruction"]).strip(),
            conditions=conditions,
            parameters=tuple(sorted(parameters.items())),
            source_policy_set=policy_set,
            source_path=path.relative_to(self._project_root).as_posix(),
        )

    @staticmethod
    def _schema_error(path: Path) -> PolicyError:
        return PolicyError(
            "POLICY_SCHEMA_INVALID",
            f"Policy file '{path.name}' is invalid.",
            {"path": str(path)},
        )
