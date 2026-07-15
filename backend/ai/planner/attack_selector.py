"""Attack asset selector interface."""

from __future__ import annotations

import re
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
    """Rank and select Dataset B attack assets for planner context."""

    def __init__(self, max_assets: int = 5) -> None:
        """Initialize the selector.

        Args:
            max_assets: Maximum assets to select for a plan.
        """

        self.max_assets = max_assets

    def select(self, context: PlannerContext) -> list[AttackAsset]:
        """Select attack assets for a planner context."""

        if not context.objective_analysis:
            return []
        preferred_categories = list(
            dict.fromkeys(
                [
                    *context.objective_analysis.recommended_categories,
                    *[str(category) for category in context.objective_analysis.metadata.get("source_categories", [])],
                ]
            )
        )
        severity_rank = {"critical": 4, "high": 3, "medium": 2, "low": 1}
        objective_terms = self._terms(
            " ".join(
                [
                    context.objective,
                    context.objective_analysis.normalized_objective,
                    " ".join(context.objective_analysis.risk_themes),
                    " ".join(context.objective_analysis.recommended_categories),
                    " ".join(str(category) for category in context.objective_analysis.metadata.get("source_categories", [])),
                ]
            )
        )
        strategy_terms = self._terms(" ".join(str(entry.metadata.get("strategy_type", "")) for entry in context.knowledge_entries))
        mutation_terms = self._terms(" ".join(str(entry.metadata.get("mutation_type", "")) for entry in context.knowledge_entries))

        def score(asset: AttackAsset) -> tuple[float, str]:
            text_terms = self._terms(
                " ".join(
                    [
                        asset.id,
                        asset.name,
                        asset.category,
                        asset.description,
                        asset.expected_behavior,
                        asset.success_criteria,
                        " ".join(asset.tags),
                        asset.attack_prompt[:1000],
                    ]
                )
            )
            semantic_score = self._jaccard(objective_terms, text_terms) * 30
            category_score = 18 if asset.category in preferred_categories else 0
            tag_score = len(self._terms(" ".join(asset.tags)).intersection(objective_terms)) * 3
            severity_score = severity_rank.get(asset.severity, 0)
            strategy_score = len(strategy_terms.intersection(text_terms)) * 2
            mutation_score = len(mutation_terms.intersection(text_terms)) * 2
            retrieval_score = float(asset.metadata.get("retrieval_score", 0)) / 5
            total = semantic_score + category_score + tag_score + severity_score + strategy_score + mutation_score + retrieval_score
            asset.metadata["selection_score"] = round(total, 3)
            asset.metadata["selection_reason"] = self._reason(asset, semantic_score, category_score, strategy_score, mutation_score)
            return (total, asset.id)

        ranked = sorted(context.attack_assets, key=score, reverse=True)
        selected = [asset for asset in ranked if asset.metadata.get("selection_score", 0) > 0]
        if selected:
            context.metadata["asset_selection_reasoning"] = [
                {
                    "asset_id": asset.id,
                    "category": asset.category,
                    "score": asset.metadata.get("selection_score"),
                    "reason": asset.metadata.get("selection_reason"),
                }
                for asset in selected[: self.max_assets]
            ]
        return selected[: self.max_assets]

    def _reason(
        self,
        asset: AttackAsset,
        semantic_score: float,
        category_score: int,
        strategy_score: int,
        mutation_score: int,
    ) -> str:
        """Return concise explanation for asset selection."""

        reasons = []
        if category_score:
            reasons.append(f"matches selected category {asset.category}")
        if semantic_score >= 3:
            reasons.append("has high objective similarity")
        if strategy_score:
            reasons.append("aligns with strategy signals")
        if mutation_score:
            reasons.append("supports mutation/adaptation signals")
        if not reasons:
            reasons.append("best available ranked Dataset B asset")
        return "; ".join(reasons)

    def _terms(self, text: str) -> set[str]:
        """Tokenize selector text."""

        return {token for token in re.findall(r"[a-zA-Z0-9_]+", text.lower().replace("-", "_")) if len(token) >= 3}

    def _jaccard(self, left: set[str], right: set[str]) -> float:
        """Return lexical semantic similarity approximation."""

        if not left or not right:
            return 0.0
        return len(left.intersection(right)) / len(left.union(right))
