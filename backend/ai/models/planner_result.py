"""Planner result model definitions."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from backend.ai.models.attack_plan import AttackPlan
from backend.ai.utils.enums import ConfidenceLevel, PlanningStage


class PlannerResult(BaseModel):
    """Output envelope returned by the AI planner.

    Attributes:
        success: Whether planning completed successfully.
        stage: Final planning stage.
        plan: Optional non-executable attack plan.
        confidence: Numeric confidence in the plan.
        confidence_level: Human-readable confidence band.
        warnings: Non-fatal planning warnings.
        errors: Fatal or blocking planning errors.
        metadata: Additional result annotations.
    """

    model_config = ConfigDict(extra="forbid")

    success: bool
    stage: PlanningStage
    plan: AttackPlan | None = None
    confidence: float = 0.0
    confidence_level: ConfidenceLevel = ConfidenceLevel.UNKNOWN
    warnings: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class PlannerError(BaseModel):
    """Non-fatal provider error scoped to one planner step.

    Attributes:
        step: Planner/provider step that failed.
        message: Human-readable error summary.
        raw_response: Raw model response when available. This must never include
            credentials or provider secrets.
        retryable: Whether the caller may retry the same step.
        metadata: Additional safe diagnostic details.
    """

    model_config = ConfigDict(extra="forbid")

    step: str
    message: str
    raw_response: str | None = None
    retryable: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)
