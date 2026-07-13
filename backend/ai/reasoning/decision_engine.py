"""Decision engine interface for planning choices."""

from __future__ import annotations

from abc import ABC, abstractmethod

from backend.ai.models.planner_context import PlannerContext
from backend.ai.models.strategy import StrategySpec


class DecisionEngine(ABC):
    """Makes high-level planning decisions from retrieved context."""

    @abstractmethod
    def rank_strategies(self, context: PlannerContext, strategies: list[StrategySpec]) -> list[StrategySpec]:
        """Rank strategies for a planner context.

        Args:
            context: Current planner context.
            strategies: Candidate strategies.

        Returns:
            Strategies ordered from most to least relevant.
        """

        raise NotImplementedError


class RuleAwareDecisionEngine(DecisionEngine):
    """Placeholder decision engine for future rule-based and AI reasoning."""

    def rank_strategies(self, context: PlannerContext, strategies: list[StrategySpec]) -> list[StrategySpec]:
        """Rank strategies for a planner context."""

        if not context.objective_analysis:
            return strategies
        preferred = set(context.objective_analysis.recommended_categories + context.objective_analysis.risk_themes)

        def score(strategy: StrategySpec) -> tuple[int, str]:
            text = " ".join(
                [
                    strategy.id,
                    strategy.name,
                    strategy.category,
                    strategy.rationale,
                    " ".join(strategy.constraints),
                ]
            ).lower().replace("-", "_")
            return (sum(1 for term in preferred if term.replace("-", "_") in text), strategy.id)

        return sorted(strategies, key=score, reverse=True)
