"""Decision engine interface for planning choices."""

from __future__ import annotations

import re
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
    """Rule-aware strategy ranker with explainable comparative scoring."""

    def rank_strategies(self, context: PlannerContext, strategies: list[StrategySpec]) -> list[StrategySpec]:
        """Rank strategies for a planner context."""

        if not context.objective_analysis:
            return strategies
        preferred = set(context.objective_analysis.recommended_categories + context.objective_analysis.risk_themes)
        objective_terms = self._terms(
            " ".join(
                [
                    context.objective,
                    context.objective_analysis.normalized_objective,
                    " ".join(context.objective_analysis.risk_themes),
                    " ".join(context.objective_analysis.recommended_categories),
                ]
            )
        )

        def score(strategy: StrategySpec) -> tuple[float, str]:
            text = " ".join(
                [
                    strategy.id,
                    strategy.name,
                    strategy.category,
                    strategy.rationale,
                    " ".join(strategy.constraints),
                ]
            ).lower().replace("-", "_")
            text_terms = self._terms(text)
            lexical = sum(1 for term in preferred if term.replace("-", "_") in text)
            semantic = self._jaccard(objective_terms, text_terms) * 10
            metrics = strategy.metadata.get("decision_metrics", {})
            base_score = float(strategy.metadata.get("score", 0))
            effectiveness = float(metrics.get("effectiveness", 0.5)) * 8
            reliability = float(metrics.get("reliability", 0.5)) * 8
            stealth = float(metrics.get("stealth", 0.5)) * 4
            complexity_penalty = float(metrics.get("complexity_penalty", 0.4)) * 3
            total = base_score + lexical * 2 + semantic + effectiveness + reliability + stealth - complexity_penalty
            strategy.metadata["rank_score"] = round(total, 3)
            strategy.metadata["rank_reason"] = (
                f"Ranked by objective fit, Dataset A score, effectiveness {metrics.get('effectiveness', 0.5)}, "
                f"reliability {metrics.get('reliability', 0.5)}, stealth {metrics.get('stealth', 0.5)}, "
                f"and complexity penalty {metrics.get('complexity_penalty', 0.4)}."
            )
            return (total, strategy.id)

        return sorted(strategies, key=score, reverse=True)

    def _terms(self, text: str) -> set[str]:
        """Tokenize decision text."""

        return {token for token in re.findall(r"[a-zA-Z0-9_]+", text.lower().replace("-", "_")) if len(token) >= 3}

    def _jaccard(self, left: set[str], right: set[str]) -> float:
        """Return lexical semantic similarity approximation."""

        if not left or not right:
            return 0.0
        return len(left.intersection(right)) / len(left.union(right))
