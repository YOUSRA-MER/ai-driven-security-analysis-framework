"""Planner memory interface for reusable planning artifacts."""

from __future__ import annotations

from abc import ABC, abstractmethod

from backend.ai.models.planner_context import PlannerContext
from backend.ai.models.planner_result import PlannerResult


class PlannerMemory(ABC):
    """Stores planner contexts and planner results for auditability."""

    @abstractmethod
    def save_context(self, context: PlannerContext) -> None:
        """Persist a planner context.

        Args:
            context: Planner context to persist.
        """

        raise NotImplementedError

    @abstractmethod
    def save_result(self, result: PlannerResult) -> None:
        """Persist a planner result.

        Args:
            result: Planner result to persist.
        """

        raise NotImplementedError


class InMemoryPlannerMemory(PlannerMemory):
    """Placeholder planner memory implementation."""

    def save_context(self, context: PlannerContext) -> None:
        """Persist a planner context."""

        raise NotImplementedError("Planner context persistence is not implemented yet.")

    def save_result(self, result: PlannerResult) -> None:
        """Persist a planner result."""

        raise NotImplementedError("Planner result persistence is not implemented yet.")

