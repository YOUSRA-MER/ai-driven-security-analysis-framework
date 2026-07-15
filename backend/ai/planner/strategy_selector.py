"""Strategy selector interface."""

from __future__ import annotations

import re
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
    """Select Dataset A strategies with explicit comparative scoring."""

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
        objective_terms = self._terms(
            " ".join(
                [
                    context.objective,
                    context.objective_analysis.normalized_objective,
                    " ".join(context.objective_analysis.risk_themes),
                    " ".join(context.objective_analysis.recommended_categories),
                    " ".join(context.objective_analysis.target_capabilities),
                ]
            )
        )

        scored = []
        for entry in strategies:
            attack_family = str(entry.metadata.get("attack_family", ""))
            entry_terms = self._terms(" ".join([entry.id, entry.title, entry.summary, " ".join(entry.tags), str(entry.metadata)]))
            family_score = 20 if attack_family in preferred_families else 0
            semantic_score = self._jaccard(objective_terms, entry_terms) * 25
            tag_score = len(self._terms(" ".join(entry.tags)).intersection(objective_terms)) * 3
            effectiveness = self._metric(entry, "effectiveness", default=0.6) * 10
            stealth = self._metric(entry, "stealth", default=0.5) * 6
            reliability = self._metric(entry, "reliability", default=0.6) * 10
            complexity_penalty = self._metric(entry, "complexity", default=0.4) * 5
            conversation_fit = self._conversation_fit(entry, context) * 5
            total = family_score + semantic_score + tag_score + effectiveness + stealth + reliability + conversation_fit - complexity_penalty
            if total > 0:
                scored.append((total, entry, {
                    "family_score": round(family_score, 3),
                    "semantic_similarity": round(semantic_score / 25, 3),
                    "tag_score": round(tag_score, 3),
                    "effectiveness": round(effectiveness / 10, 3),
                    "stealth": round(stealth / 6, 3),
                    "reliability": round(reliability / 10, 3),
                    "conversation_fit": round(conversation_fit / 5, 3),
                    "complexity_penalty": round(complexity_penalty / 5, 3),
                }))
        scored.sort(key=lambda item: item[0], reverse=True)
        selected = [self._to_strategy(entry, score, metrics) for score, entry, metrics in scored[: self.max_strategies]]
        if not selected:
            selected = self._fallback_strategies(context, preferred_families)
        context.metadata["strategy_selection_reasoning"] = [
            {
                "strategy_id": strategy.id,
                "attack_family": strategy.category,
                "score": strategy.metadata.get("score"),
                "reason": strategy.rationale,
                "metrics": strategy.metadata.get("decision_metrics", {}),
            }
            for strategy in selected
        ]
        return selected

    def _fallback_strategies(self, context: PlannerContext, preferred_families: set[str]) -> list[StrategySpec]:
        """Create conservative strategy specs from retrieved family evidence."""

        families = list(preferred_families)
        if not families and context.objective_analysis:
            families = [f"af-{context.objective_analysis.recommended_categories[0].replace('_', '-')}" if context.objective_analysis.recommended_categories else "af-prompt-injection"]
        if not families:
            return []
        family = families[0]
        category = family.replace("af-", "").replace("-", "_")
        strategy_id = {
            "tool_abuse": "strat-tool-boundary-check",
            "indirect_prompt_injection": "strat-retrieval-source-conflict",
            "rag_poisoning": "strat-retrieval-source-conflict",
            "prompt_leakage": "strat-debug-session-framing",
            "prompt_injection": "strat-security-audit-framing",
            "jailbreak": "strat-refusal-boundary-comparison",
        }.get(category, "strat-security-audit-framing")
        return [
            StrategySpec(
                id=strategy_id,
                name=strategy_id.replace("strat-", "").replace("-", " ").title(),
                category=family,
                rationale=(
                    f"Selected as conservative fallback because top-ranked knowledge and objective analysis align with {family}."
                ),
                supporting_knowledge=[entry.id for entry in context.knowledge_entries[:3]],
                constraints=["Fallback strategy derived from ranked Dataset A evidence; no attack execution in planner."],
                metadata={
                    "strategy_type": "fallback_reasoned",
                    "score": 45.0,
                    "rank_score": 45.0,
                    "decision_metrics": {
                        "effectiveness": 0.65,
                        "stealth": 0.5,
                        "reliability": 0.65,
                        "conversation_fit": 0.75,
                        "complexity_penalty": 0.35,
                    },
                },
            )
        ]

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

    def _metric(self, entry, name: str, default: float) -> float:
        """Read a numeric strategy metric from metadata if available."""

        value = entry.metadata.get(name, entry.metadata.get(f"expected_{name}", default))
        try:
            numeric = float(value)
        except (TypeError, ValueError):
            numeric = default
        return max(0.0, min(1.0, numeric))

    def _conversation_fit(self, entry, context: PlannerContext) -> float:
        """Estimate whether the strategy's conversation shape fits the objective."""

        strategy_type = str(entry.metadata.get("strategy_type", "")).lower()
        capabilities = set(context.objective_analysis.target_capabilities if context.objective_analysis else [])
        if "multi" in strategy_type or "conversation" in strategy_type:
            return 1.0 if "multi_turn" in capabilities else 0.65
        if "tool" in strategy_type:
            return 1.0 if "tool_use" in capabilities else 0.45
        if "retrieval" in strategy_type:
            return 1.0 if "retrieval" in capabilities else 0.55
        return 0.75

    def _terms(self, text: str) -> set[str]:
        """Tokenize strategy text."""

        return {token for token in re.findall(r"[a-zA-Z0-9_]+", text.lower().replace("-", "_")) if len(token) >= 3}

    def _jaccard(self, left: set[str], right: set[str]) -> float:
        """Return lexical semantic similarity approximation."""

        if not left or not right:
            return 0.0
        return len(left.intersection(right)) / len(left.union(right))

    def _to_strategy(self, entry, score: float, metrics: dict[str, float]) -> StrategySpec:
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
            rationale=self._strategy_reason(entry, metrics),
            supporting_knowledge=[entry.id],
            constraints=[str(item) for item in entry.metadata.get("safety_constraints", [])],
            metadata={"strategy_type": strategy_type, "score": round(score, 3), "decision_metrics": metrics},
        )

    def _strategy_reason(self, entry, metrics: dict[str, float]) -> str:
        """Return concise comparative strategy explanation."""

        strengths = []
        if metrics["family_score"] > 0:
            strengths.append("matches the selected attack family")
        if metrics["semantic_similarity"] >= 0.05:
            strengths.append("aligns semantically with the objective")
        if metrics["effectiveness"] >= 0.6:
            strengths.append("has strong expected effectiveness")
        if metrics["reliability"] >= 0.6:
            strengths.append("has reliable expected signal")
        if metrics["conversation_fit"] >= 0.75:
            strengths.append("fits the required conversation mode")
        weakness = "moderate complexity" if metrics["complexity_penalty"] >= 0.6 else "manageable complexity"
        return f"Selected because it {', '.join(strengths) or 'is the best ranked compatible strategy'} with {weakness}."
