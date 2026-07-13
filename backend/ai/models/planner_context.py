"""Planner context model definitions."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from backend.ai.models.attack_asset import AttackAsset
from backend.ai.models.knowledge_entry import KnowledgeEntry
from backend.ai.models.objective_analysis import ObjectiveAnalysis
from backend.ai.utils.enums import PlanningStage


class PlannerContext(BaseModel):
    """State container passed through the AI planning pipeline.

    Attributes:
        session_id: Session identifier for planning memory and traceability.
        objective: User-provided security testing objective.
        stage: Current planning lifecycle stage.
        objective_analysis: Optional structured objective analysis.
        knowledge_entries: Retrieved Dataset A records.
        attack_assets: Retrieved Dataset B records.
        constraints: Scope, policy, and runtime constraints.
        trace: Human-readable planning trace messages.
        metadata: Additional request-specific state.
    """

    model_config = ConfigDict(extra="forbid")

    session_id: str
    objective: str
    stage: PlanningStage = PlanningStage.CREATED
    objective_analysis: ObjectiveAnalysis | None = None
    knowledge_entries: list[KnowledgeEntry] = Field(default_factory=list)
    attack_assets: list[AttackAsset] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    trace: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

