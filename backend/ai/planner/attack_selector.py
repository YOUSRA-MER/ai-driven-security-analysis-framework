"""Attack asset selector interface."""

from __future__ import annotations

from abc import ABC, abstractmethod

from backend.ai.models.attack_asset import AttackAsset
from backend.ai.models.planner_context import PlannerContext


class AttackSelector(ABC):
    """Selects attack assets from retrieved Dataset B records."""

    @abstractmethod
    def select(self, context: PlannerContext) -> list[AttackAsset]:
        """Select attack assets for a planner context.

        Args:
            context: Planner context with objective analysis and retrieved assets.

        Returns:
            Selected attack assets.
        """

        raise NotImplementedError


class DatasetAttackSelector(AttackSelector):
    """Placeholder selector for attack dataset assets."""

    def __init__(self, max_assets: int = 12) -> None:
        """Initialize the selector.

        Args:
            max_assets: Maximum assets to select for a plan.
        """

        self.max_assets = max_assets

    def select(self, context: PlannerContext) -> list[AttackAsset]:
        """Select attack assets for a planner context."""

        if not context.objective_analysis:
            return []
        preferred_categories = context.objective_analysis.recommended_categories
        severity_rank = {"critical": 4, "high": 3, "medium": 2, "low": 1}

        def score(asset: AttackAsset) -> tuple[int, int, int, str]:
            category_score = 10 if asset.category in preferred_categories else 0
            tag_score = len(set(asset.tags).intersection(set(context.objective_analysis.risk_themes)))
            severity_score = severity_rank.get(asset.severity, 0)
            return (category_score, tag_score, severity_score, asset.id)

        ranked = sorted(context.attack_assets, key=score, reverse=True)
        selected = [asset for asset in ranked if asset.category in preferred_categories]
        if len(selected) < self.max_assets:
            selected.extend(asset for asset in ranked if asset.id not in {item.id for item in selected})
        return selected[: self.max_assets]
