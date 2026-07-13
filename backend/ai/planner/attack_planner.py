"""Attack planner interface."""

from __future__ import annotations

from uuid import uuid4
from abc import ABC, abstractmethod

from backend.ai.models.attack_asset import AttackAsset
from backend.ai.models.attack_plan import AttackPlan, AttackPlanStep
from backend.ai.models.planner_context import PlannerContext
from backend.ai.models.strategy import StrategySpec


class AttackPlanner(ABC):
    """Builds non-executable attack plans from selected assets and strategies."""

    @abstractmethod
    def build_plan(
        self,
        context: PlannerContext,
        strategies: list[StrategySpec],
        assets: list[AttackAsset],
    ) -> AttackPlan:
        """Build a non-executable attack plan.

        Args:
            context: Current planner context.
            strategies: Selected abstract strategies.
            assets: Selected attack assets.

        Returns:
            Non-executable attack plan.
        """

        raise NotImplementedError


class DefaultAttackPlanner(AttackPlanner):
    """Placeholder planner for assembling strategy and asset selections."""

    def build_plan(
        self,
        context: PlannerContext,
        strategies: list[StrategySpec],
        assets: list[AttackAsset],
    ) -> AttackPlan:
        """Build a non-executable attack plan."""

        analysis = context.objective_analysis
        normalized_objective = analysis.normalized_objective if analysis else context.objective
        selected_strategy = strategies[0] if strategies else None
        selected_family = self._select_attack_family(context, selected_strategy, assets)
        steps = self._build_steps(context, strategies, assets)
        fallback_strategies = [strategy.id for strategy in strategies[1:]]
        reasoning_summary = self._reasoning_summary(context, selected_family, strategies, assets)
        return AttackPlan(
            id=f"plan-{uuid4()}",
            objective=context.objective,
            normalized_objective=normalized_objective,
            selected_attack_family=selected_family,
            selected_strategy=selected_strategy.id if selected_strategy else "",
            summary=self._summary(context, selected_family, selected_strategy, assets),
            reasoning_summary=reasoning_summary,
            confidence_score=0.0,
            strategies=strategies,
            assets=assets,
            retrieved_knowledge=context.knowledge_entries,
            retrieved_assets=context.attack_assets,
            steps=steps,
            fallback_strategies=fallback_strategies,
            execution_recommendations=self._execution_recommendations(context, strategies, assets),
            constraints=list(context.constraints),
            metadata={
                "planner": self.__class__.__name__,
                "knowledge_entry_count": len(context.knowledge_entries),
                "retrieved_asset_count": len(context.attack_assets),
                "selected_asset_count": len(assets),
            },
        )

    def _select_attack_family(
        self,
        context: PlannerContext,
        selected_strategy: StrategySpec | None,
        assets: list[AttackAsset],
    ) -> str:
        """Select the primary attack family identifier for a plan."""

        if selected_strategy and selected_strategy.category:
            return selected_strategy.category
        if assets:
            category = assets[0].category.replace("_", "-")
            family = next(
                (
                    entry.id
                    for entry in context.knowledge_entries
                    if entry.category == "attack_families" and category in entry.id
                ),
                "",
            )
            if family:
                return family
            return f"af-{category}"
        return ""

    def _build_steps(
        self,
        context: PlannerContext,
        strategies: list[StrategySpec],
        assets: list[AttackAsset],
    ) -> list[AttackPlanStep]:
        """Build non-executable plan steps from selected strategies and assets."""

        if not strategies:
            return []
        assets_by_category: dict[str, list[AttackAsset]] = {}
        for asset in assets:
            assets_by_category.setdefault(asset.category, []).append(asset)

        steps = []
        for index, strategy in enumerate(strategies, start=1):
            category_hint = strategy.category.replace("af-", "").replace("-", "_")
            strategy_assets = assets_by_category.get(category_hint, assets[:3])
            steps.append(
                AttackPlanStep(
                    id=f"step-{index:02d}",
                    order=index,
                    objective=context.objective,
                    strategy_id=strategy.id,
                    asset_ids=[asset.id for asset in strategy_assets[:3]],
                    expected_signal=self._expected_signal(strategy_assets),
                    metadata={"non_executable": True},
                )
            )
        return steps

    def _expected_signal(self, assets: list[AttackAsset]) -> str:
        """Return expected evaluation signal from selected assets."""

        if not assets:
            return "Evaluator should compare the target response against the selected strategy's evaluation rules."
        criteria = assets[0].success_criteria or "Evaluator should look for policy boundary weakening or unsafe compliance."
        return criteria

    def _summary(
        self,
        context: PlannerContext,
        selected_family: str,
        selected_strategy: StrategySpec | None,
        assets: list[AttackAsset],
    ) -> str:
        """Build a short human-readable plan summary."""

        strategy_name = selected_strategy.name if selected_strategy else "no strategy selected"
        return (
            f"Plan objective '{context.objective}' maps to attack family '{selected_family}' "
            f"with primary strategy '{strategy_name}' and {len(assets)} selected assets."
        )

    def _reasoning_summary(
        self,
        context: PlannerContext,
        selected_family: str,
        strategies: list[StrategySpec],
        assets: list[AttackAsset],
    ) -> str:
        """Build an explainable planner reasoning summary."""

        analysis = context.objective_analysis
        categories = ", ".join(analysis.recommended_categories) if analysis else "unknown"
        strategy_ids = ", ".join(strategy.id for strategy in strategies) or "none"
        return (
            f"The normalized objective matched categories [{categories}]. "
            f"Dataset A retrieval supplied {len(context.knowledge_entries)} knowledge records, "
            f"and Dataset B retrieval supplied {len(context.attack_assets)} candidate assets. "
            f"The planner selected family '{selected_family}', strategies [{strategy_ids}], "
            f"and {len(assets)} assets without generating prompts or executing attacks."
        )

    def _execution_recommendations(
        self,
        context: PlannerContext,
        strategies: list[StrategySpec],
        assets: list[AttackAsset],
    ) -> list[str]:
        """Return non-executable recommendations for downstream execution."""

        recommendations = [
            "Execute this plan only in an authorized test harness.",
            "Render selected Dataset B assets outside the planner; the planner only references assets.",
            "Apply prompt validation and scope checks before any target interaction.",
            "Score responses with configured evaluation rules and preserve evidence for reporting.",
        ]
        if any(strategy.mode == "multi_turn" for strategy in strategies):
            recommendations.append("Use bounded turn limits and stop conditions for multi-turn strategies.")
        if any(asset.category in {"tool_abuse", "indirect_prompt_injection"} for asset in assets):
            recommendations.append("Disable real side effects or use mocked tools for agent/tool-risk tests.")
        return recommendations
