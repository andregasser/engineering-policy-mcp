from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class ResolveRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    event: str
    repository_path: str = Field(min_length=1)
    base_revision: str = Field(default="HEAD", min_length=1)
    task_id: str | None = None
