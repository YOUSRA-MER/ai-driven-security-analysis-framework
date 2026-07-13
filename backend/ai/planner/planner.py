"""Top-level AI planner interface and orchestration skeleton."""

from __future__ import annotations

from abc import ABC, abstractmethod

from backend.ai.models.planner_context import PlannerContext
from backend.ai.models.planner_result import PlannerResult
from backend.ai.planner.attack_optimizer import AttackOptimizer, DefaultAttackOptimizer
from backend.ai.planner.attack_planner import AttackPlanner, DefaultAttackPlanner
from backend.ai.planner.attack_selector import AttackSelector, DatasetAttackSelector
from backend.ai.planner.objective_analyzer import DefaultObjectiveAnalyzer, ObjectiveAnalyzer
from backend.ai.planner.strategy_selector import KnowledgeStrategySelector, StrategySelector
from backend.ai.reasoning.confidence_estimator import ConfidenceEstimator, HeuristicConfidenceEstimator
from backend.ai.reasoning.decision_engine import DecisionEngine, RuleAwareDecisionEngine
from backend.ai.retrieval.retriever import AIRetriever, DatasetRetriever
from backend.ai.utils.enums import PlanningStage


class Planner(ABC):
    """Coordinates AI planning components without executing attacks."""

    @abstractmethod
    def plan(self, context: PlannerContext) -> PlannerResult:
        """Create a non-executable plan for a planner context.

        Args:
            context: Planner context containing the user objective and constraints.

        Returns:
            Planner result containing a non-executable plan or errors.
        """

        raise NotImplementedError


class AIPlanner(Planner):
    """Composition root for the AI planning subsystem.

    This class is intentionally a skeleton. Future implementations should wire
    objective analysis, retrieval, selection, optimization, validation, and
    confidence estimation here without performing attack execution.
    """

    def __init__(
        self,
        objective_analyzer: ObjectiveAnalyzer | None = None,
        retriever: AIRetriever | None = None,
        attack_selector: AttackSelector | None = None,
        strategy_selector: StrategySelector | None = None,
        decision_engine: DecisionEngine | None = None,
        attack_planner: AttackPlanner | None = None,
        attack_optimizer: AttackOptimizer | None = None,
        confidence_estimator: ConfidenceEstimator | None = None,
    ) -> None:
        """Initialize the planner with replaceable dependencies.

        Args:
            objective_analyzer: Component that analyzes the assessment objective.
            retriever: Component that retrieves Dataset A and Dataset B records.
            attack_selector: Component that selects Dataset B attack assets.
            strategy_selector: Component that selects abstract strategies.
            decision_engine: Component that ranks strategy candidates.
            attack_planner: Component that builds non-executable plans.
            attack_optimizer: Component that refines non-executable plans.
            confidence_estimator: Component that estimates plan confidence.
        """

        self.objective_analyzer = objective_analyzer or DefaultObjectiveAnalyzer()
        self.retriever = retriever or DatasetRetriever()
        self.attack_selector = attack_selector or DatasetAttackSelector()
        self.strategy_selector = strategy_selector or KnowledgeStrategySelector()
        self.decision_engine = decision_engine or RuleAwareDecisionEngine()
        self.attack_planner = attack_planner or DefaultAttackPlanner()
        self.attack_optimizer = attack_optimizer or DefaultAttackOptimizer()
        self.confidence_estimator = confidence_estimator or HeuristicConfidenceEstimator()

    def plan(self, context: PlannerContext) -> PlannerResult:
        """Create a non-executable plan for a planner context."""

        try:
            context.stage = PlanningStage.ANALYZING_OBJECTIVE
            context.objective_analysis = self.objective_analyzer.analyze(context)
            context.trace.append("Objective analysis completed.")

            context.stage = PlanningStage.RETRIEVING_KNOWLEDGE
            context.knowledge_entries = self.retriever.retrieve_knowledge(context.objective_analysis)
            context.attack_assets = self.retriever.retrieve_attack_assets(context.objective_analysis)
            context.trace.append(
                f"Retrieved {len(context.knowledge_entries)} knowledge entries and "
                f"{len(context.attack_assets)} attack assets."
            )

            context.stage = PlanningStage.SELECTING_ATTACKS
            selected_assets = self.attack_selector.select(context)
            context.trace.append(f"Selected {len(selected_assets)} attack assets.")

            context.stage = PlanningStage.SELECTING_STRATEGIES
            candidate_strategies = self.strategy_selector.select(context)
            selected_strategies = self.decision_engine.rank_strategies(context, candidate_strategies)
            context.trace.append(f"Selected {len(selected_strategies)} strategies.")

            context.stage = PlanningStage.BUILDING_PLAN
            plan = self.attack_planner.build_plan(context, selected_strategies, selected_assets)

            context.stage = PlanningStage.OPTIMIZING_PLAN
            plan = self.attack_optimizer.optimize(context, plan)

            estimate = self.confidence_estimator.estimate(context, plan)
            plan.confidence_score = estimate.score
            plan.metadata["confidence_rationale"] = estimate.rationale
            context.stage = PlanningStage.COMPLETED
            context.trace.append("Planning completed.")

            return PlannerResult(
                success=True,
                stage=context.stage,
                plan=plan,
                confidence=estimate.score,
                confidence_level=estimate.level,
                warnings=[],
                errors=[],
                metadata={"trace": list(context.trace)},
            )
        except Exception as exc:
            context.stage = PlanningStage.FAILED
            return PlannerResult(
                success=False,
                stage=context.stage,
                confidence=0.0,
                errors=[str(exc)],
                metadata={"trace": list(context.trace)},
            )
