"""Attack plan model definitions."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from backend.ai.models.attack_asset import AttackAsset
from backend.ai.models.knowledge_entry import KnowledgeEntry
from backend.ai.models.strategy import StrategySpec


class AttackPlanStep(BaseModel):
    """One abstract step in an AI-generated attack plan.

    Attributes:
        id: Stable step identifier within the plan.
        order: Step order in the plan.
        objective: Step-specific testing objective.
        strategy_id: Selected strategy identifier.
        asset_ids: Attack asset identifiers referenced by this step.
        expected_signal: Evidence the evaluator should look for later.
        metadata: Additional step annotations.
    """

    model_config = ConfigDict(extra="forbid")

    id: str
    order: int
    objective: str
    strategy_id: str
    asset_ids: list[str] = Field(default_factory=list)
    expected_signal: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)


class AttackPlan(BaseModel):
    """Non-executable plan produced by the AI planner.

    Attributes:
        id: Stable plan identifier.
        objective: Original user objective.
        normalized_objective: Planner-normalized objective.
        selected_attack_family: Selected Dataset A attack-family identifier.
        selected_strategy: Primary selected strategy identifier.
        summary: Human-readable plan summary.
        reasoning_summary: Explanation of why the plan was selected.
        confidence_score: Normalized confidence score.
        strategies: Abstract selected strategies.
        assets: Attack assets selected for later prompt construction.
        retrieved_knowledge: Knowledge records considered by the planner.
        retrieved_assets: Attack assets considered by the planner.
        steps: Ordered non-executable plan steps.
        fallback_strategies: Secondary strategy identifiers.
        execution_recommendations: Non-executable recommendations for later runners.
        constraints: Plan-wide safety, scope, and runtime constraints.
        metadata: Additional plan annotations.
    """

    model_config = ConfigDict(extra="forbid")

    id: str
    objective: str
    normalized_objective: str = ""
    selected_attack_family: str = ""
    selected_strategy: str = ""
    summary: str = ""
    reasoning_summary: str = ""
    confidence_score: float = 0.0
    strategies: list[StrategySpec] = Field(default_factory=list)
    assets: list[AttackAsset] = Field(default_factory=list)
    retrieved_knowledge: list[KnowledgeEntry] = Field(default_factory=list)
    retrieved_assets: list[AttackAsset] = Field(default_factory=list)
    steps: list[AttackPlanStep] = Field(default_factory=list)
    fallback_strategies: list[str] = Field(default_factory=list)
    execution_recommendations: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
