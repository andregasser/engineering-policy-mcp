from __future__ import annotations

import json
from pathlib import Path

from engineering_policy.telemetry import TelemetryWriter


def test_telemetry_serializes_safe_event(tmp_path: Path) -> None:
    writer = TelemetryWriter(tmp_path, ".engineering-policy/events.jsonl", "task")

    writer.emit("policy_resolution_started", event="before_completion")

    event = json.loads((tmp_path / ".engineering-policy/events.jsonl").read_text("utf-8"))
    assert event["event_type"] == "policy_resolution_started"
    assert event["task_id"] == "task"
    assert "source" not in event


def test_telemetry_failure_is_isolated(tmp_path: Path) -> None:
    obstruction = tmp_path / "blocked"
    obstruction.write_text("not a directory", encoding="utf-8")
    writer = TelemetryWriter(tmp_path, "blocked/events.jsonl", None)

    writer.emit("policy_resolution_started")

    assert writer.warning() is not None
