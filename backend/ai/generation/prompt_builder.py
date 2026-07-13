"""Prompt builder interface for future prompt construction."""

from __future__ import annotations

from abc import ABC, abstractmethod

from backend.ai.models.attack_plan import AttackPlan, AttackPlanStep


class PromptBuilder(ABC):
    """Builds concrete prompt candidates from an abstract attack plan.

    Implementations must not execute attacks. They should only transform a
    selected plan and asset references into candidate prompt text for later
    validation and orchestration.
    """

    @abstractmethod
    def build(self, plan: AttackPlan, step: AttackPlanStep) -> str:
        """Build a prompt candidate for a plan step.

        Args:
            plan: Non-executable attack plan.
            step: Plan step requiring prompt construction.

        Returns:
            Prompt candidate text.
        """

        raise NotImplementedError


class TemplatePromptBuilder(PromptBuilder):
    """Placeholder prompt builder for dataset-backed templates."""

    def build(self, plan: AttackPlan, step: AttackPlanStep) -> str:
        """Build a prompt candidate for a plan step."""

        raise NotImplementedError("Prompt construction is not implemented yet.")

