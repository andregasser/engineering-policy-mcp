from __future__ import annotations

from dataclasses import dataclass

from engineering_policy.domain.models import JsonValue


@dataclass(frozen=True)
class PolicyError(Exception):
    code: str
    message: str
    details: dict[str, JsonValue]
    retryable: bool = False

    def __str__(self) -> str:
        return self.message


def invalid_argument(message: str, **details: JsonValue) -> PolicyError:
    return PolicyError("INVALID_ARGUMENT", message, details)
