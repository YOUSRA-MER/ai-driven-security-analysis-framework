"""Pydantic contracts for prompt validation outcomes."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class PromptValidationResult(BaseModel):
    """Non-throwing validation outcome for a generated prompt."""

    model_config = ConfigDict(extra="forbid")
    is_valid: bool
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    metadata: dict[str, str] = Field(default_factory=dict)
