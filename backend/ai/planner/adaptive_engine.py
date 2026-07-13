"""Adaptive planning engine interface."""

from __future__ import annotations

from abc import ABC, abstractmethod

from backend.ai.models.attack_plan import AttackPlan
from backend.ai.models.planner_context import PlannerContext


class AdaptiveEngine(ABC):
    """Adapts future plans from feedback without executing attacks."""

    @abstractmethod
    def adapt(self, context: PlannerContext, prior_plan: AttackPlan) -> AttackPlan:
        """Adapt a prior plan from feedback in the context.

        Args:
            context: Planner context containing feedback or memory references.
            prior_plan: Existing non-executable plan.

        Returns:
            Adapted non-executable plan.
        """

        raise NotImplementedError


class DefaultAdaptiveEngine(AdaptiveEngine):
    """Placeholder adaptive engine for future feedback-aware planning."""

    def adapt(self, context: PlannerContext, prior_plan: AttackPlan) -> AttackPlan:
        """Adapt a prior plan from feedback in the context."""

        raise NotImplementedError("Adaptive planning is not implemented yet.")

