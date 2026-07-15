"""Typed state contracts for multi-stage AI planning reasoning."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from backend.ai.models.attack_asset import AttackAsset
from backend.ai.models.knowledge_entry import KnowledgeEntry
from backend.ai.models.objective_analysis import ObjectiveAnalysis
from backend.ai.models.strategy import StrategySpec


class AttackFamilyAssessment(BaseModel):
    model_config = ConfigDict(extra="forbid")
    family_ids: list[str] = Field(default_factory=list)
    rationale: str
    confidence: float = Field(ge=0.0, le=1.0)


class AttackHypothesis(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str
    attack_family: str
    strategy_ids: list[str] = Field(default_factory=list)
    asset_ids: list[str] = Field(default_factory=list)
    rationale: str
    expected_signal: str = ""
    confidence: float = Field(ge=0.0, le=1.0)


class StrategyEvaluation(BaseModel):
    model_config = ConfigDict(extra="forbid")
    selected_hypothesis_id: str
    alternative_hypothesis_ids: list[str] = Field(default_factory=list)
    rationale: str
    confidence: float = Field(ge=0.0, le=1.0)


class ConfidenceAssessment(BaseModel):
    model_config = ConfigDict(extra="forbid")
    score: float = Field(ge=0.0, le=1.0)
    explanation: str
    uncertainty_factors: list[str] = Field(default_factory=list)


class PlanDirective(BaseModel):
    model_config = ConfigDict(extra="forbid")
    selected_hypothesis_id: str
    strategy_ids: list[str] = Field(default_factory=list)
    asset_ids: list[str] = Field(default_factory=list)
    reasoning_summary: str


class PlanValidation(BaseModel):
    model_config = ConfigDict(extra="forbid")
    objective_aligned: bool
    stronger_strategy_available: bool
    conflicting_recommendations: list[str] = Field(default_factory=list)
    return_multiple_candidates: bool
    rationale: str


class ReasoningSession(BaseModel):
    """Auditable state accumulated before an attack plan is constructed."""
    model_config = ConfigDict(extra="forbid")
    session_id: str
    assessment_objective: str
    objective_analysis: ObjectiveAnalysis | None = None
    retrieved_knowledge: list[KnowledgeEntry] = Field(default_factory=list)
    retrieved_attack_assets: list[AttackAsset] = Field(default_factory=list)
    candidate_strategies: list[StrategySpec] = Field(default_factory=list)
    hypotheses: list[AttackHypothesis] = Field(default_factory=list)
    discarded_hypotheses: list[AttackHypothesis] = Field(default_factory=list)
    selected_hypothesis: AttackHypothesis | None = None
    confidence_evolution: list[ConfidenceAssessment] = Field(default_factory=list)
    reasoning_summary: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)
