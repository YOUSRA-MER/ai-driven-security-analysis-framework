"""Prompt mutator interface for future controlled variation."""

from __future__ import annotations

from abc import ABC, abstractmethod

from backend.ai.models.attack_plan import AttackPlanStep


class PromptMutator(ABC):
    """Produces safe, auditable prompt variants from prompt candidates."""

    @abstractmethod
    def mutate(self, prompt: str, step: AttackPlanStep) -> list[str]:
        """Return prompt variants for a plan step.

        Args:
            prompt: Original prompt candidate.
            step: Associated attack plan step.

        Returns:
            Prompt variants.
        """

        raise NotImplementedError


class ControlledPromptMutator(PromptMutator):
    """Placeholder mutator for future deterministic and AI-assisted mutations."""

    def mutate(self, prompt: str, step: AttackPlanStep) -> list[str]:
        """Return prompt variants for a plan step."""

        raise NotImplementedError("Prompt mutation is not implemented yet.")

