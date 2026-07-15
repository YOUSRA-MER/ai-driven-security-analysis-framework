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
    """Weighted confidence estimator for planner decision quality."""

    def estimate(self, context: PlannerContext, plan: AttackPlan | None = None) -> ConfidenceEstimate:
        """Estimate confidence for the current planner context."""

        rationale_parts = []
        objective_clarity = 0.0
        if context.objective_analysis:
            objective_clarity = context.objective_analysis.confidence
            if context.objective_analysis.recommended_categories:
                objective_clarity = min(1.0, objective_clarity + 0.08)
            rationale_parts.append(f"objective clarity={objective_clarity:.2f}")

        knowledge_scores = [
            float(entry.metadata.get("retrieval_score", 0))
            for entry in context.knowledge_entries
            if isinstance(entry.metadata, dict)
        ]
        asset_scores = [
            float(asset.metadata.get("retrieval_score", 0))
            for asset in context.attack_assets
            if isinstance(asset.metadata, dict)
        ]
        knowledge_quality = min(1.0, (sum(knowledge_scores[:5]) / max(len(knowledge_scores[:5]), 1)) / 35) if knowledge_scores else 0.0
        retrieval_quality = min(1.0, (knowledge_quality + min(1.0, (sum(asset_scores[:5]) / max(len(asset_scores[:5]), 1)) / 35 if asset_scores else 0.0)) / 2)
        rationale_parts.append(f"retrieval quality={retrieval_quality:.2f}")

        strategy_agreement = 0.0
        if plan and plan.strategies:
            strategy_scores = [float(strategy.metadata.get("rank_score", strategy.metadata.get("score", 0))) for strategy in plan.strategies]
            strategy_agreement = min(1.0, (sum(strategy_scores[:3]) / max(len(strategy_scores[:3]), 1)) / 60)
            rationale_parts.append(f"strategy agreement={strategy_agreement:.2f}")

        knowledge_agreement = self._knowledge_agreement(context, plan)
        rationale_parts.append(f"knowledge agreement={knowledge_agreement:.2f}")

        provider_confidence = 0.0
        if plan:
            reasoning_session = plan.metadata.get("reasoning_session", {})
            if isinstance(reasoning_session, dict):
                family = reasoning_session.get("metadata", {}).get("family_assessment", {})
                strategy = reasoning_session.get("metadata", {}).get("strategy_evaluation", {})
                provider_values = [
                    float(item.get("confidence", 0))
                    for item in (family, strategy)
                    if isinstance(item, dict) and item.get("confidence") is not None
                ]
                provider_confidence = sum(provider_values) / len(provider_values) if provider_values else 0.0
        if provider_confidence:
            rationale_parts.append(f"provider confidence={provider_confidence:.2f}")

        score = (
            objective_clarity * 0.25
            + knowledge_agreement * 0.2
            + retrieval_quality * 0.2
            + strategy_agreement * 0.2
            + provider_confidence * 0.15
        )
        if not provider_confidence:
            score = score / 0.85
        score = min(1.0, round(score, 3))
        return ConfidenceEstimate(
            score=score,
            level=self._level(score),
            rationale="; ".join(rationale_parts) or "insufficient planning evidence",
        )

    def _knowledge_agreement(self, context: PlannerContext, plan: AttackPlan | None) -> float:
        """Estimate agreement between selected family, knowledge, and assets."""

        if not plan or not context.objective_analysis:
            return 0.0
        selected_family = plan.selected_attack_family.replace("af-", "").replace("-", "_")
        category_hits = 0
        if selected_family in {category.replace("-", "_") for category in context.objective_analysis.recommended_categories}:
            category_hits += 1
        if any(selected_family in entry.id.replace("-", "_") or selected_family in entry.summary.replace("-", "_").lower() for entry in context.knowledge_entries):
            category_hits += 1
        if any(asset.category == selected_family for asset in plan.assets):
            category_hits += 1
        return category_hits / 3

    def _level(self, score: float) -> ConfidenceLevel:
        """Return a confidence band for a numeric score."""

        if score >= 0.75:
            return ConfidenceLevel.HIGH
        if score >= 0.5:
            return ConfidenceLevel.MEDIUM
        return ConfidenceLevel.LOW
