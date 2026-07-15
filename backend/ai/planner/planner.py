"""Top-level AI planner implementation."""

from __future__ import annotations

import asyncio
import logging
import time
from abc import ABC, abstractmethod

from backend.ai.models.attack_asset import AttackAsset
from backend.ai.models.planner_context import PlannerContext
from backend.ai.models.planner_result import PlannerError, PlannerResult
from backend.ai.models.prompt_generation import Prompt
from backend.ai.models.reasoning_session import AttackFamilyAssessment, AttackHypothesis, ReasoningSession, StrategyEvaluation
from backend.ai.planner.attack_optimizer import AttackOptimizer, DefaultAttackOptimizer
from backend.ai.planner.attack_planner import AttackPlanner, DefaultAttackPlanner
from backend.ai.planner.attack_selector import AttackSelector, DatasetAttackSelector
from backend.ai.planner.objective_analyzer import DefaultObjectiveAnalyzer, ObjectiveAnalyzer
from backend.ai.planner.strategy_selector import KnowledgeStrategySelector, StrategySelector
from backend.ai.providers.provider_interface import AIProvider
from backend.ai.reasoning.confidence_estimator import ConfidenceEstimator, HeuristicConfidenceEstimator
from backend.ai.reasoning.decision_engine import DecisionEngine, RuleAwareDecisionEngine
from backend.ai.retrieval.retriever import AIRetriever, DatasetRetriever
from backend.ai.utils.enums import PlanningStage


logger = logging.getLogger(__name__)


class Planner(ABC):
    """Coordinates AI planning components without executing attacks."""

    @abstractmethod
    async def plan(self, context: PlannerContext) -> PlannerResult:
        """Create a non-executable plan for a planner context.

        Args:
            context: Planner context containing the user objective and constraints.

        Returns:
            Planner result containing a non-executable plan or errors.
        """

        raise NotImplementedError


class AIPlanner(Planner):
    """Provider-backed planner for non-executable security assessment plans."""

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
        provider: AIProvider | None = None,
    ) -> None:
        """Initialize the planner with replaceable dependencies."""

        self.objective_analyzer = objective_analyzer or DefaultObjectiveAnalyzer()
        self.retriever = retriever or DatasetRetriever()
        self.attack_selector = attack_selector or DatasetAttackSelector()
        self.strategy_selector = strategy_selector or KnowledgeStrategySelector()
        self.decision_engine = decision_engine or RuleAwareDecisionEngine()
        self.attack_planner = attack_planner or DefaultAttackPlanner()
        self.attack_optimizer = attack_optimizer or DefaultAttackOptimizer()
        self.confidence_estimator = confidence_estimator or HeuristicConfidenceEstimator()
        self.provider = provider

    async def plan(self, context: PlannerContext) -> PlannerResult:
        """Run the complete planner pipeline using the injected provider.

        The planner performs deterministic dataset retrieval and selection, then
        asks the provider to reason over the bounded candidate set. It never
        calls targets, executes attacks, or sends prompts to applications.
        """

        started = time.perf_counter()
        metrics: dict[str, float | int] = {
            "retrieval_time": 0.0,
            "ranking_time": 0.0,
            "llm_time": 0.0,
            "generation_time": 0.0,
            "total_time": 0.0,
            "input_tokens": 0,
            "output_tokens": 0,
            "cache_hits": 0,
            "cache_misses": 0,
        }
        provider_errors: list[dict] = []
        use_provider = self.provider is not None
        logger.info("Planner started", extra={"session_id": context.session_id})
        try:
            context.stage = PlanningStage.ANALYZING_OBJECTIVE
            stage_started = time.perf_counter()
            context.objective_analysis = await self._analyze_objective(context)
            if isinstance(context.objective_analysis, PlannerError):
                self._record_provider_error(context.objective_analysis, provider_errors)
                context.objective_analysis = self.objective_analyzer.analyze(context)
                use_provider = False
            elif self.provider:
                context.objective_analysis = self._stabilize_objective_analysis(context)
            metrics["llm_time"] += self._elapsed_ms(stage_started) if self.provider else 0.0
            logger.info(
                "Planner objective analysis completed",
                extra={"session_id": context.session_id, "elapsed_ms": metrics["llm_time"] if self.provider else self._elapsed_ms(stage_started)},
            )
            context.trace.append("Objective analysis completed.")

            context.stage = PlanningStage.RETRIEVING_KNOWLEDGE
            stage_started = time.perf_counter()
            knowledge_entries, attack_assets = await asyncio.gather(
                asyncio.to_thread(self.retriever.retrieve_knowledge, context.objective_analysis, 10),
                asyncio.to_thread(self.retriever.retrieve_attack_assets, context.objective_analysis, 10),
            )
            context.knowledge_entries = knowledge_entries
            context.attack_assets = attack_assets
            metrics["retrieval_time"] = self._elapsed_ms(stage_started)
            logger.info("Planner retrieval completed", extra={"session_id": context.session_id, "elapsed_ms": metrics["retrieval_time"]})
            if hasattr(self.retriever, "cache_stats"):
                cache_stats = self.retriever.cache_stats()
                metrics["cache_hits"] = int(cache_stats.get("cache_hits", 0))
                metrics["cache_misses"] = int(cache_stats.get("cache_misses", 0))
            logger.info(
                "Dataset retrieval completed",
                extra={
                    "session_id": context.session_id,
                    "knowledge_count": len(context.knowledge_entries),
                    "asset_count": len(context.attack_assets),
                },
            )
            context.trace.append(
                f"Retrieved {len(context.knowledge_entries)} knowledge entries and "
                f"{len(context.attack_assets)} attack assets after relevance ranking."
            )

            context.stage = PlanningStage.SELECTING_ATTACKS
            stage_started = time.perf_counter()

            def select_and_rank_strategies():
                candidates = self.strategy_selector.select(context)
                return candidates, self.decision_engine.rank_strategies(context, candidates)

            selected_assets, strategy_result = await asyncio.gather(
                asyncio.to_thread(self.attack_selector.select, context),
                asyncio.to_thread(select_and_rank_strategies),
            )
            candidate_strategies, ranked_strategies = strategy_result
            metrics["ranking_time"] = self._elapsed_ms(stage_started)
            logger.info("Planner ranking completed", extra={"session_id": context.session_id, "elapsed_ms": metrics["ranking_time"]})
            context.trace.append(f"Selected {len(selected_assets)} attack assets.")

            context.stage = PlanningStage.SELECTING_STRATEGIES
            context.trace.append(f"Selected {len(ranked_strategies)} candidate strategies.")

            session = ReasoningSession(
                session_id=context.session_id,
                assessment_objective=context.objective,
                objective_analysis=context.objective_analysis,
                retrieved_knowledge=context.knowledge_entries,
                retrieved_attack_assets=context.attack_assets,
                candidate_strategies=ranked_strategies,
            )
            session.hypotheses = self._build_hypotheses(ranked_strategies, selected_assets)
            session.metadata["knowledge_ranking"] = self._ranking_snapshot(context.knowledge_entries)
            session.metadata["asset_ranking"] = self._ranking_snapshot(context.attack_assets)
            session.metadata["strategy_selection_reasoning"] = context.metadata.get("strategy_selection_reasoning", [])
            session.metadata["asset_selection_reasoning"] = context.metadata.get("asset_selection_reasoning", [])

            reasoning_summary = ""
            selected_family_ids: list[str] = []
            if use_provider:
                family_assessment = self._deterministic_family_assessment(context, ranked_strategies, selected_assets)
                if family_assessment is None:
                    logger.info("Reasoning request: attack family", extra={"session_id": context.session_id})
                    stage_started = time.perf_counter()
                    family_assessment = await self.provider.select_attack_family(session)
                    metrics["llm_time"] += self._elapsed_ms(stage_started)
                    logger.info("Planner family selection completed", extra={"session_id": context.session_id, "elapsed_ms": self._elapsed_ms(stage_started)})
                if isinstance(family_assessment, PlannerError):
                    self._record_provider_error(family_assessment, provider_errors, session=session)
                    use_provider = False
                else:
                    selected_family_ids = family_assessment.family_ids
                    session.metadata["family_assessment"] = family_assessment.model_dump()

                if use_provider:
                    strategy_evaluation = self._deterministic_strategy_evaluation(session, ranked_strategies)
                    if strategy_evaluation is None:
                        logger.info("Reasoning request: strategy", extra={"session_id": context.session_id})
                        stage_started = time.perf_counter()
                        strategy_evaluation = await self.provider.select_strategy(session)
                        metrics["llm_time"] += self._elapsed_ms(stage_started)
                        logger.info("Planner strategy selection completed", extra={"session_id": context.session_id, "elapsed_ms": self._elapsed_ms(stage_started)})
                    if isinstance(strategy_evaluation, PlannerError):
                        self._record_provider_error(strategy_evaluation, provider_errors, session=session)
                        session.selected_hypothesis = session.hypotheses[0] if session.hypotheses else None
                        session.discarded_hypotheses = session.hypotheses[1:]
                        use_provider = False
                    else:
                        session.metadata["strategy_evaluation"] = strategy_evaluation.model_dump()
                        session.selected_hypothesis = self._resolve_hypothesis(session.hypotheses, strategy_evaluation.selected_hypothesis_id)
                        session.discarded_hypotheses = [item for item in session.hypotheses if item.id != session.selected_hypothesis.id]

                if use_provider:
                    selected_hypothesis = session.selected_hypothesis
                    if selected_hypothesis:
                        reasoning_summary = selected_hypothesis.rationale
                        selected_strategies = [
                            item for item in ranked_strategies if item.id in selected_hypothesis.strategy_ids
                        ] or ranked_strategies[:3]
                        selected_assets = [
                            item for item in selected_assets if item.id in selected_hypothesis.asset_ids
                        ] or selected_assets
                        session.metadata["plan_directive"] = {
                            "selected_hypothesis_id": selected_hypothesis.id,
                            "strategy_ids": [item.id for item in selected_strategies],
                            "asset_ids": [item.id for item in selected_assets],
                            "reasoning_summary": reasoning_summary,
                            "deterministic": True,
                        }
                    else:
                        selected_strategies = ranked_strategies[:3]
                else:
                    selected_strategies = ranked_strategies[:3]
            else:
                selected_strategies = ranked_strategies[:3]

            context.stage = PlanningStage.BUILDING_PLAN
            plan = self.attack_planner.build_plan(context, selected_strategies, selected_assets)
            if selected_family_ids:
                plan.selected_attack_family = selected_family_ids[0]
            if reasoning_summary:
                plan.reasoning_summary = reasoning_summary

            context.stage = PlanningStage.OPTIMIZING_PLAN
            plan = self.attack_optimizer.optimize(context, plan)

            session.metadata["selected_asset_ids"] = [asset.id for asset in plan.assets[: min(5, len(plan.assets))]]
            generated_prompt_result = None
            if use_provider:
                logger.info("Reasoning request: prompt generation", extra={"session_id": context.session_id})
                stage_started = time.perf_counter()
                generated_prompt_result = await self.provider.generate_prompts(session)
                metrics["generation_time"] = self._elapsed_ms(stage_started)
                metrics["llm_time"] += metrics["generation_time"]
                logger.info("Planner prompt generation completed", extra={"session_id": context.session_id, "elapsed_ms": metrics["generation_time"]})
                if isinstance(generated_prompt_result, PlannerError):
                    self._record_provider_error(generated_prompt_result, provider_errors, session=session)
                    generated_prompt_result = None
                    use_provider = False
            optimized_prompts = (
                generated_prompt_result.prompts
                if generated_prompt_result is not None
                else await self._optimize_selected_prompts(
                    context,
                    plan.assets[: min(5, len(plan.assets))],
                    plan.selected_strategy,
                    use_provider=use_provider,
                )
            )

            confidence = await self._estimate_confidence(context, plan, session)
            plan.confidence_score = confidence["score"]
            plan.metadata["confidence_rationale"] = confidence["rationale"]
            plan.metadata["generated_prompts"] = [prompt.model_dump() for prompt in optimized_prompts]
            plan.metadata["reasoning_session"] = session.model_dump()
            plan.metadata["provider_errors"] = provider_errors
            plan.metadata["knowledge_ranking"] = session.metadata["knowledge_ranking"]
            plan.metadata["asset_ranking"] = session.metadata["asset_ranking"]
            plan.metadata["strategy_selection_reasoning"] = session.metadata["strategy_selection_reasoning"]
            plan.metadata["asset_selection_reasoning"] = session.metadata["asset_selection_reasoning"]
            plan.metadata["owasp_mapping"] = context.objective_analysis.metadata.get("owasp_mappings", []) if context.objective_analysis else []
            plan.metadata["mitre_mapping"] = context.objective_analysis.metadata.get("mitre_mappings", []) if context.objective_analysis else []
            plan.metadata["mitigations"] = self._mitigation_snapshot(context)
            provider_metrics = self._provider_metrics(provider_errors)
            metrics["input_tokens"] = provider_metrics["input_tokens"]
            metrics["output_tokens"] = provider_metrics["output_tokens"]
            metrics["total_time"] = round((time.perf_counter() - started) * 1000, 2)
            plan.metadata["planner_metrics"] = metrics

            context.stage = PlanningStage.COMPLETED
            elapsed_ms = round((time.perf_counter() - started) * 1000, 2)
            logger.info("Planner completed", extra={"session_id": context.session_id, "elapsed_ms": elapsed_ms})
            context.trace.append("Planning completed.")
            return PlannerResult(
                success=True,
                stage=context.stage,
                plan=plan,
                confidence=confidence["score"],
                confidence_level=self.confidence_estimator.estimate(context, plan).level,
                warnings=[error["message"] for error in provider_errors],
                errors=[],
                metadata={
                    "trace": list(context.trace),
                    "elapsed_ms": elapsed_ms,
                    "generated_prompts": [prompt.model_dump() for prompt in optimized_prompts],
                    "provider_errors": provider_errors,
                    "knowledge_ranking": session.metadata["knowledge_ranking"],
                    "asset_ranking": session.metadata["asset_ranking"],
                    "planner_metrics": metrics,
                },
            )
        except Exception as exc:  # noqa: BLE001 - API should return structured planner errors.
            elapsed_ms = round((time.perf_counter() - started) * 1000, 2)
            logger.exception("Planner error", extra={"session_id": context.session_id, "elapsed_ms": elapsed_ms})
            context.stage = PlanningStage.FAILED
            return PlannerResult(
                success=False,
                stage=context.stage,
                confidence=0.0,
                errors=[str(exc)],
                metadata={"trace": list(context.trace), "elapsed_ms": elapsed_ms, "planner_metrics": metrics},
            )

    async def _analyze_objective(self, context: PlannerContext):
        """Analyze the objective with provider support and deterministic fallback."""

        if self.provider:
            logger.info("Reasoning request: objective analysis", extra={"session_id": context.session_id})
            return await self.provider.analyze_objective(context.objective)
        return self.objective_analyzer.analyze(context)

    def _stabilize_objective_analysis(self, context: PlannerContext):
        """Anchor provider objective analysis with deterministic retrieval signals."""

        provider_analysis = context.objective_analysis
        deterministic = self.objective_analyzer.analyze(context)
        if not provider_analysis:
            return deterministic
        categories = list(dict.fromkeys([*deterministic.recommended_categories, *provider_analysis.recommended_categories]))
        risk_themes = list(dict.fromkeys([*deterministic.risk_themes, *provider_analysis.risk_themes]))
        capabilities = list(dict.fromkeys([*deterministic.target_capabilities, *provider_analysis.target_capabilities]))
        metadata = {**provider_analysis.metadata, **deterministic.metadata, "provider_objective_analysis": provider_analysis.model_dump()}
        return provider_analysis.model_copy(
            update={
                "recommended_categories": categories[:6],
                "risk_themes": risk_themes[:10],
                "target_capabilities": capabilities[:8],
                "metadata": metadata,
            }
        )

    def _deterministic_family_assessment(
        self,
        context: PlannerContext,
        ranked_strategies,
        selected_assets: list[AttackAsset],
    ) -> AttackFamilyAssessment | None:
        """Return a high-confidence family decision from ranked retrieval evidence."""

        candidates: list[tuple[float, str, str]] = []
        for entry in context.knowledge_entries:
            if entry.category == "attack_families":
                score = float(entry.metadata.get("retrieval_score", 0) or 0)
                candidates.append((score, entry.id, f"Dataset A attack-family entry '{entry.title}' ranked highest."))
        if ranked_strategies:
            strategy = ranked_strategies[0]
            if strategy.category:
                score = float(strategy.metadata.get("rank_score", strategy.metadata.get("score", 0)) or 0)
                candidates.append((score, strategy.category, f"Top ranked strategy '{strategy.id}' supports this family."))
        if selected_assets:
            asset = selected_assets[0]
            score = float(asset.metadata.get("selection_score", asset.metadata.get("retrieval_score", 0)) or 0)
            candidates.append((score, f"af-{asset.category.replace('_', '-')}", f"Top Dataset B asset '{asset.id}' supports this family."))
        if not candidates:
            return None
        score, family_id, reason = sorted(candidates, key=lambda item: item[0], reverse=True)[0]
        if score < 8:
            return None
        return AttackFamilyAssessment(
            family_ids=[family_id],
            rationale=f"{reason} Deterministic family selection used to avoid unnecessary LLM latency.",
            confidence=min(0.95, max(0.55, score / 60)),
        )

    def _deterministic_strategy_evaluation(self, session: ReasoningSession, ranked_strategies) -> StrategyEvaluation | None:
        """Return a high-confidence strategy decision from ranked strategy evidence."""

        if not ranked_strategies or not session.hypotheses:
            return None
        top_strategy = ranked_strategies[0]
        score = float(top_strategy.metadata.get("rank_score", top_strategy.metadata.get("score", 0)) or 0)
        if score < 8:
            return None
        selected = next(
            (item for item in session.hypotheses if top_strategy.id in item.strategy_ids),
            session.hypotheses[0],
        )
        alternatives = [item.id for item in session.hypotheses if item.id != selected.id][:3]
        return StrategyEvaluation(
            selected_hypothesis_id=selected.id,
            alternative_hypothesis_ids=alternatives,
            rationale=(
                f"Top ranked strategy '{top_strategy.id}' had strong deterministic agreement with the objective, "
                "selected family, assets, and conversation requirements."
            ),
            confidence=min(0.95, max(0.55, score / 60)),
        )

    async def _estimate_confidence(self, context: PlannerContext, plan, session: ReasoningSession) -> dict[str, float | str]:
        """Estimate confidence with provider support and deterministic fallback."""

        if self.provider and not session.metadata.get("provider_errors"):
            logger.info("Reasoning request: confidence", extra={"session_id": context.session_id})
            try:
                result = await self.provider.estimate_confidence(session)
                session.confidence_evolution.append(result)
                return {"score": result.score, "rationale": result.explanation}
            except Exception as exc:  # noqa: BLE001 - confidence has deterministic fallback.
                session.metadata.setdefault("provider_errors", []).append(
                    {"step": "estimate_confidence", "message": str(exc), "retryable": True, "metadata": {}}
                )
        estimate = self.confidence_estimator.estimate(context, plan)
        return {"score": estimate.score, "rationale": estimate.rationale}

    async def _optimize_selected_prompts(
        self,
        context: PlannerContext,
        assets: list[AttackAsset],
        strategy_id: str,
        use_provider: bool = True,
    ) -> list[Prompt]:
        """Optimize selected Dataset B prompts without executing them."""

        prompts = []
        for index, asset in enumerate(assets, start=1):
            prompt = Prompt(
                id=f"planned-prompt-{index:02d}",
                content=asset.attack_prompt,
                objective=context.objective,
                strategy_id=strategy_id,
                attack_family=asset.category,
                asset_ids=[asset.id],
                metadata={
                    "source_asset_id": asset.id,
                    "non_executable": True,
                    "selection_score": asset.metadata.get("selection_score"),
                    "selection_reason": asset.metadata.get("selection_reason"),
                    "retrieval_score": asset.metadata.get("retrieval_score"),
                },
            )
            if self.provider and use_provider:
                logger.info("Reasoning request: prompt optimization", extra={"session_id": context.session_id, "asset_id": asset.id})
                prompt = await self.provider.optimize_prompt(prompt)
            prompts.append(prompt)
        return prompts

    def _elapsed_ms(self, started: float) -> float:
        """Return elapsed milliseconds from a perf-counter start time."""

        return round((time.perf_counter() - started) * 1000, 2)

    def _provider_metrics(self, provider_errors: list[dict]) -> dict[str, int]:
        """Aggregate token metrics exposed by provider step metadata."""

        provider_last_metrics = getattr(self.provider, "last_metrics", {}) if self.provider else {}
        input_tokens = int(provider_last_metrics.get("input_tokens", 0) or 0)
        output_tokens = int(provider_last_metrics.get("output_tokens", 0) or 0)
        for error in provider_errors:
            metadata = error.get("metadata", {})
            if isinstance(metadata, dict):
                input_tokens += int(metadata.get("input_tokens", 0) or 0)
                output_tokens += int(metadata.get("output_tokens", 0) or 0)
        return {"input_tokens": input_tokens, "output_tokens": output_tokens}

    def _ranking_snapshot(self, items: list[object]) -> list[dict]:
        """Return concise ranking metadata for explainability output."""

        snapshot = []
        for item in items:
            metadata = getattr(item, "metadata", {})
            snapshot.append(
                {
                    "id": getattr(item, "id", ""),
                    "name": getattr(item, "name", getattr(item, "title", "")),
                    "category": getattr(item, "category", ""),
                    "retrieval_score": metadata.get("retrieval_score") if isinstance(metadata, dict) else None,
                    "selection_score": metadata.get("selection_score") if isinstance(metadata, dict) else None,
                    "reason": metadata.get("selection_reason") if isinstance(metadata, dict) else None,
                    "retrieval_reasons": metadata.get("retrieval_reasons", {}) if isinstance(metadata, dict) else {},
                }
            )
        return snapshot

    def _mitigation_snapshot(self, context: PlannerContext) -> list[dict]:
        """Return top mitigation knowledge entries relevant to the plan."""

        mitigations = []
        for entry in context.knowledge_entries:
            if entry.category == "mitigations" or "mitigation" in entry.id:
                mitigations.append(
                    {
                        "id": entry.id,
                        "title": entry.title,
                        "summary": entry.summary,
                        "score": entry.metadata.get("retrieval_score"),
                    }
                )
        return mitigations[:5]

    def _record_provider_error(
        self,
        error: PlannerError,
        provider_errors: list[dict],
        session: ReasoningSession | None = None,
    ) -> None:
        """Record a provider step failure without aborting the planner."""

        error_payload = error.model_dump(exclude={"raw_response"})
        provider_errors.append(error_payload)
        if session is not None:
            session.metadata.setdefault("provider_errors", []).append(error_payload)
        logger.warning(
            "Provider step failed; planner will continue with fallback",
            extra={"step": error.step, "planner_error_message": error.message},
        )

    def _build_hypotheses(self, strategies, assets: list[AttackAsset]) -> list[AttackHypothesis]:
        """Build bounded candidate hypotheses from selected strategies/assets."""

        hypotheses = []
        for index, strategy in enumerate(strategies[:5], start=1):
            category_hint = strategy.category.replace("af-", "").replace("-", "_")
            matched_assets = [asset for asset in assets if asset.category == category_hint] or assets[:3]
            hypotheses.append(
                AttackHypothesis(
                    id=f"hypothesis-{index:02d}",
                    attack_family=strategy.category or (f"af-{matched_assets[0].category.replace('_', '-')}" if matched_assets else ""),
                    strategy_ids=[strategy.id],
                    asset_ids=[asset.id for asset in matched_assets[:5]],
                    rationale=strategy.rationale or f"Strategy {strategy.id} matched retrieved knowledge and assets.",
                    expected_signal=matched_assets[0].success_criteria if matched_assets else "",
                    confidence=min(1.0, max(0.0, float(strategy.metadata.get("score", 10)) / 100)) if strategy.metadata else 0.5,
                )
            )
        return hypotheses

    def _resolve_hypothesis(self, hypotheses: list[AttackHypothesis], hypothesis_id: str) -> AttackHypothesis:
        """Return a selected hypothesis, falling back to the first candidate."""

        return next((item for item in hypotheses if item.id == hypothesis_id), hypotheses[0])
