from __future__ import annotations

from pathlib import Path, PurePosixPath

import yaml
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from engineering_policy.domain.errors import PolicyError
from engineering_policy.domain.models import AnalysisConfig, AppConfig, TelemetryConfig


class AnalysisConfigModel(BaseModel):
    model_config = ConfigDict(extra="forbid")
    production_paths: list[str] = Field(default_factory=lambda: ["src/main/**"])
    test_paths: list[str] = Field(default_factory=lambda: ["src/test/**"])
    exclude_paths: list[str] = Field(
        default_factory=lambda: [
            ".engineering-policy/**",
            "target/**",
            "build/**",
            ".gradle/**",
            ".idea/**",
        ]
    )
    substantial_change: dict[str, int] = Field(
        default_factory=lambda: {"production_files": 10, "changed_lines": 500}
    )


class TelemetryConfigModel(BaseModel):
    model_config = ConfigDict(extra="forbid")
    enabled: bool = True
    path: str = ".engineering-policy/telemetry/events.jsonl"


class AppConfigModel(BaseModel):
    model_config = ConfigDict(extra="forbid")
    schema_version: int = 1
    policy_sets: list[str] = Field(default_factory=lambda: ["company/baseline", "teams/java"])
    analysis: AnalysisConfigModel = Field(default_factory=AnalysisConfigModel)
    telemetry: TelemetryConfigModel = Field(default_factory=TelemetryConfigModel)


def _validate_relative_path(value: str, label: str) -> str:
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts:
        raise PolicyError(
            "INVALID_ARGUMENT",
            f"{label} must remain inside the repository root.",
            {label: value},
        )
    return value


def load_config(repository_root: Path) -> AppConfig:
    path = repository_root / ".engineering-policy" / "config.yaml"
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8")) if path.exists() else {}
        model = AppConfigModel.model_validate(raw or {})
    except (OSError, yaml.YAMLError, ValidationError) as exc:
        raise PolicyError(
            "INVALID_ARGUMENT", "Repository configuration is invalid.", {"path": str(path)}
        ) from exc

    if model.schema_version != 1:
        raise PolicyError(
            "INVALID_ARGUMENT",
            "Unsupported configuration schema version.",
            {"schema_version": model.schema_version},
        )
    thresholds = model.analysis.substantial_change
    if set(thresholds) != {"production_files", "changed_lines"} or any(
        not isinstance(value, int) or isinstance(value, bool) or value < 0
        for value in thresholds.values()
    ):
        raise PolicyError(
            "INVALID_ARGUMENT",
            "substantial_change must contain non-negative integer thresholds.",
            {},
        )
    policy_sets = tuple(_validate_relative_path(value, "policy_set") for value in model.policy_sets)
    telemetry_path = _validate_relative_path(model.telemetry.path, "telemetry.path")
    return AppConfig(
        schema_version=model.schema_version,
        policy_sets=policy_sets,
        analysis=AnalysisConfig(
            production_paths=tuple(model.analysis.production_paths),
            test_paths=tuple(model.analysis.test_paths),
            exclude_paths=tuple(model.analysis.exclude_paths),
            substantial_production_files=thresholds["production_files"],
            substantial_changed_lines=thresholds["changed_lines"],
        ),
        telemetry=TelemetryConfig(enabled=model.telemetry.enabled, path=telemetry_path),
    )
