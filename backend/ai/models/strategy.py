"""Strategy planning model definitions."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from backend.ai.utils.enums import StrategyMode


class StrategySpec(BaseModel):
    """Abstract, non-executable attack strategy selected by the planner.

    Attributes:
        id: Stable strategy identifier.
        name: Human-readable strategy name.
        category: Attack category associated with the strategy.
        mode: Conversation or execution style for the strategy.
        rationale: Planner rationale for selecting the strategy.
        required_assets: Attack asset IDs needed by this strategy.
        supporting_knowledge: Knowledge entry IDs that justify this strategy.
        constraints: Constraints that downstream components must honor.
        metadata: Additional strategy annotations.
    """

    model_config = ConfigDict(extra="forbid")

    id: str
    name: str
    category: str
    mode: StrategyMode = StrategyMode.UNKNOWN
    rationale: str = ""
    required_assets: list[str] = Field(default_factory=list)
    supporting_knowledge: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

