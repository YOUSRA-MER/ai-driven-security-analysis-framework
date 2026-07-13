"""Attack plan optimizer interface."""

from __future__ import annotations

from abc import ABC, abstractmethod

from backend.ai.models.attack_plan import AttackPlan
from backend.ai.models.planner_context import PlannerContext


class AttackOptimizer(ABC):
    """Optimizes non-executable attack plans before prompt generation."""

    @abstractmethod
    def optimize(self, context: PlannerContext, plan: AttackPlan) -> AttackPlan:
        """Optimize a non-executable attack plan.

        Args:
            context: Current planner context.
            plan: Candidate plan.

        Returns:
            Optimized plan.
        """

        raise NotImplementedError


class DefaultAttackOptimizer(AttackOptimizer):
    """Placeholder optimizer for future plan pruning and prioritization."""

    def optimize(self, context: PlannerContext, plan: AttackPlan) -> AttackPlan:
        """Optimize a non-executable attack plan."""

        return plan
