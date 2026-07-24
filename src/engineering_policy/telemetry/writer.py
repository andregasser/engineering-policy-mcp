from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from engineering_policy.domain.models import WarningMessage


class TelemetryWriter:
    def __init__(self, repository_root: Path, relative_path: str, task_id: str | None) -> None:
        self._path = repository_root / relative_path
        self._task_id = task_id
        self._repository_id = hashlib.sha256(str(repository_root).encode()).hexdigest()[:16]
        self._failed = False

    def emit(self, event_type: str, **fields: Any) -> None:
        if self._failed:
            return
        event = {
            "schema_version": 1,
            "event_type": event_type,
            "timestamp": datetime.now(UTC).isoformat(),
            "task_id": self._task_id,
            "repository_id": self._repository_id,
            **fields,
        }
        try:
            self._path.parent.mkdir(parents=True, exist_ok=True)
            with self._path.open("a", encoding="utf-8") as stream:
                stream.write(json.dumps(event, separators=(",", ":"), sort_keys=True) + "\n")
        except OSError:
            self._failed = True

    def warning(self) -> WarningMessage | None:
        if not self._failed:
            return None
        return WarningMessage(
            code="TELEMETRY_WRITE_FAILED",
            message="Telemetry could not be written; policy resolution was not affected.",
        )
