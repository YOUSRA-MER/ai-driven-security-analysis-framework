"""Strategy selector interface."""

from __future__ import annotations

from abc import ABC, abstractmethod

from backend.ai.models.planner_context import PlannerContext
from backend.ai.models.strategy import StrategySpec


class StrategySelector(ABC):
    """Selects abstract testing strategies for a planner context."""

    @abstractmethod
    def select(self, context: PlannerContext) -> list[StrategySpec]:
        """Select strategies for a planner context.

        Args:
            context: Planner context with retrieved knowledge and assets.

        Returns:
            Selected abstract strategies.
        """

        raise NotImplementedError


class KnowledgeStrategySelector(StrategySelector):
    """Placeholder selector that will use Dataset A strategy knowledge."""

    def __init__(self, max_strategies: int = 5) -> None:
        """Initialize the selector.

        Args:
            max_strategies: Maximum strategies to return.
        """

        self.max_strategies = max_strategies

    def select(self, context: PlannerContext) -> list[StrategySpec]:
        """Select strategies for a planner context."""

        if not context.objective_analysis:
            return []
        preferred_families = self._preferred_family_ids(context)
        strategies = [entry for entry in context.knowledge_entries if entry.category == "strategies"]

        scored = []
        for entry in strategies:
            attack_family = str(entry.metadata.get("attack_family", ""))
            family_score = 10 if attack_family in preferred_families else 0
            tag_score = len(set(entry.tags).intersection(set(context.objective_analysis.risk_themes)))
            text_score = self._text_overlap(context.objective_analysis.normalized_objective, entry.summary)
            total = family_score + tag_score + text_score
            if total > 0:
                scored.append((total, entry))
        scored.sort(key=lambda item: item[0], reverse=True)
        return [self._to_strategy(entry, score) for score, entry in scored[: self.max_strategies]]

    def _preferred_family_ids(self, context: PlannerContext) -> set[str]:
        """Return preferred attack family IDs from retrieved knowledge."""

        family_ids = set()
        for entry in context.knowledge_entries:
            if entry.category == "attack_families" and self._family_matches(entry, context):
                family_ids.add(entry.id)
        return family_ids

    def _family_matches(self, entry, context: PlannerContext) -> bool:
        """Return whether an attack family matches the objective analysis."""

        analysis = context.objective_analysis
        if not analysis:
            return False
        category_tokens = set(analysis.recommended_categories + analysis.risk_themes)
        searchable = " ".join([entry.id, entry.title, entry.summary, " ".join(entry.tags)]).replace("-", "_").lower()
        return any(token.replace("-", "_") in searchable for token in category_tokens)

    def _text_overlap(self, left: str, right: str) -> int:
        """Return a lightweight text overlap score."""

        left_terms = {term for term in left.replace("-", "_").split() if len(term) >= 3}
        right_terms = {term for term in right.lower().replace("-", "_").split() if len(term) >= 3}
        return len(left_terms.intersection(right_terms))

    def _to_strategy(self, entry, score: int) -> StrategySpec:
        """Convert a knowledge entry into a strategy spec."""

        mode = "unknown"
        strategy_type = str(entry.metadata.get("strategy_type", ""))
        if "multi" in strategy_type or "conversation" in strategy_type:
            mode = "multi_turn"
        elif "tool" in strategy_type:
            mode = "tool_aware"
        elif "retrieval" in strategy_type:
            mode = "retrieval_augmented"
        elif strategy_type:
            mode = "single_turn"
        return StrategySpec(
            id=entry.id,
            name=entry.title,
            category=str(entry.metadata.get("attack_family") or ""),
            mode=mode,
            rationale=f"Selected from Dataset A with relevance score {score}.",
            supporting_knowledge=[entry.id],
            constraints=[str(item) for item in entry.metadata.get("safety_constraints", [])],
            metadata={"strategy_type": strategy_type, "score": score},
        )
