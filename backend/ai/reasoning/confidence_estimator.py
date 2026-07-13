"""Confidence estimation interface for planning decisions."""

from __future__ import annotations

from abc import ABC, abstractmethod

from backend.ai.models.attack_plan import AttackPlan
from backend.ai.models.planner_context import PlannerContext
from backend.ai.utils.enums import ConfidenceLevel


class ConfidenceEstimate:
    """Simple confidence estimate returned by estimators.

    Attributes:
        score: Normalized confidence score between 0 and 1.
        level: Human-readable confidence level.
        rationale: Short explanation for the confidence estimate.
    """

    def __init__(self, score: float, level: ConfidenceLevel, rationale: str = "") -> None:
        self.score = score
        self.level = level
        self.rationale = rationale


class ConfidenceEstimator(ABC):
    """Estimates confidence for a planning context or decision."""

    @abstractmethod
    def estimate(self, context: PlannerContext, plan: AttackPlan | None = None) -> ConfidenceEstimate:
        """Estimate confidence for the current planner context.

        Args:
            context: Current planner context.
            plan: Optional plan to include in the estimate.

        Returns:
            Confidence estimate.
        """

        raise NotImplementedError


class HeuristicConfidenceEstimator(ConfidenceEstimator):
    """Placeholder confidence estimator for future heuristic scoring."""

    def estimate(self, context: PlannerContext, plan: AttackPlan | None = None) -> ConfidenceEstimate:
        """Estimate confidence for the current planner context."""

        score = 0.2
        rationale_parts = []
        if context.objective_analysis:
            score += context.objective_analysis.confidence * 0.35
            rationale_parts.append("objective analysis available")
        if context.knowledge_entries:
            score += min(0.2, len(context.knowledge_entries) / 50)
            rationale_parts.append(f"{len(context.knowledge_entries)} knowledge entries retrieved")
        if context.attack_assets:
            score += min(0.2, len(context.attack_assets) / 60)
            rationale_parts.append(f"{len(context.attack_assets)} attack assets retrieved")
        if plan and plan.strategies:
            score += min(0.15, len(plan.strategies) * 0.04)
            rationale_parts.append(f"{len(plan.strategies)} strategies selected")
        score = min(1.0, round(score, 3))
        return ConfidenceEstimate(
            score=score,
            level=self._level(score),
            rationale="; ".join(rationale_parts) or "insufficient planning evidence",
        )

    def _level(self, score: float) -> ConfidenceLevel:
        """Return a confidence band for a numeric score."""

        if score >= 0.75:
            return ConfidenceLevel.HIGH
        if score >= 0.5:
            return ConfidenceLevel.MEDIUM
        return ConfidenceLevel.LOW
