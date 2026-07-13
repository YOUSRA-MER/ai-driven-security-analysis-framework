"""Objective analysis model definitions."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from backend.ai.utils.enums import ConfidenceLevel


class ObjectiveAnalysis(BaseModel):
    """Structured interpretation of a user's security testing objective.

    Attributes:
        objective: Original objective provided by the user.
        normalized_objective: Planner-normalized version of the objective.
        target_capabilities: Capabilities implied by the target application.
        risk_themes: Security themes relevant to the objective.
        recommended_categories: Attack categories that may be relevant.
        constraints: User, policy, or system constraints discovered during analysis.
        confidence: Numeric confidence for this analysis.
        confidence_level: Human-readable confidence band.
        metadata: Additional analyzer annotations.
    """

    model_config = ConfigDict(extra="forbid")

    objective: str
    normalized_objective: str = ""
    target_capabilities: list[str] = Field(default_factory=list)
    risk_themes: list[str] = Field(default_factory=list)
    recommended_categories: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    confidence: float = 0.0
    confidence_level: ConfidenceLevel = ConfidenceLevel.UNKNOWN
    metadata: dict[str, Any] = Field(default_factory=dict)

