"""Adaptive candidate construction and the prompt-generation reasoning loop."""
from __future__ import annotations
from abc import ABC, abstractmethod
from uuid import uuid4
from backend.ai.generation.prompt_mutator import ControlledPromptMutator, PromptMutator
from backend.ai.generation.prompt_validator import PolicyPromptValidator, PromptValidationResult, PromptValidator
from backend.ai.models.attack_asset import AttackAsset
from backend.ai.models.attack_plan import AttackPlan, AttackPlanStep
from backend.ai.models.knowledge_entry import KnowledgeEntry
from backend.ai.models.planner_context import PlannerContext
from backend.ai.models.prompt_generation import Prompt, PromptGenerationResult, PromptQualityEstimate
from backend.ai.providers.provider_interface import AIProvider

class PromptBuilder(ABC):
    """Turns planner evidence into candidates without target interaction."""
    @abstractmethod
    def build(self, context: PlannerContext, plan: AttackPlan, knowledge_entries: list[KnowledgeEntry], assets: list[AttackAsset]) -> list[Prompt]: ...

class AdaptivePromptBuilder(PromptBuilder):
    def build(self, context: PlannerContext, plan: AttackPlan, knowledge_entries: list[KnowledgeEntry], assets: list[AttackAsset]) -> list[Prompt]:
        selected_ids = {asset.id for asset in assets}
        usable = [asset for asset in plan.assets if asset.id in selected_ids] or assets or plan.assets
        steps = plan.steps or [AttackPlanStep(id="step-01", order=1, objective=plan.objective, strategy_id=plan.selected_strategy, asset_ids=[a.id for a in usable])]
        by_id = {asset.id: asset for asset in usable}
        knowledge_hint = "; ".join(entry.summary for entry in knowledge_entries[:2] if entry.summary)
        prompts: list[Prompt] = []
        for step in steps:
            step_assets = [by_id[asset_id] for asset_id in step.asset_ids if asset_id in by_id] or usable[:1]
            for asset in step_assets:
                # Composition uses the actual plan, retrieved evidence, and target context rather than a fixed attack template.
                context_hint = str(context.metadata.get("conversation_context", "")).strip()
                text = "\n".join(part for part in [
                    f"Authorized security assessment objective: {step.objective or plan.normalized_objective}.",
                    f"Selected strategy: {step.strategy_id or plan.selected_strategy}; attack family: {plan.selected_attack_family}.",
                    f"Target profile: {context.metadata.get('target_profile', 'unspecified') }.",
                    f"Conversation context: {context_hint}" if context_hint else "",
                    f"Planning evidence: {knowledge_hint}" if knowledge_hint else "",
                    "Candidate test input:", asset.attack_prompt.strip(),
                    f"Expected evaluation signal: {step.expected_signal or asset.success_criteria}",
                ] if part)
                prompts.append(Prompt(id=f"prompt-{uuid4()}", content=text, objective=step.objective or plan.objective, strategy_id=step.strategy_id or plan.selected_strategy, attack_family=plan.selected_attack_family, asset_ids=[asset.id], turn=step.order, metadata={"plan_id": plan.id, "step_id": step.id, "allowed_strategy_ids": [strategy.id for strategy in plan.strategies]}))
        return prompts

# Kept as a compatibility name; it is now plan-aware and not template-only.
TemplatePromptBuilder = AdaptivePromptBuilder

class PromptGenerationService:
    """Coordinates reasoning, construction, mutation, validation, and selection."""
    def __init__(self, builder: PromptBuilder | None = None, mutator: PromptMutator | None = None, validator: PromptValidator | None = None, provider: AIProvider | None = None) -> None:
        self.builder = builder or AdaptivePromptBuilder()
        self.mutator = mutator or ControlledPromptMutator()
        self.validator = validator or PolicyPromptValidator()
        self.provider = provider

    async def generate(self, context: PlannerContext, plan: AttackPlan, knowledge_entries: list[KnowledgeEntry] | None = None, assets: list[AttackAsset] | None = None, mutation_names: list[str] | None = None) -> PromptGenerationResult:
        knowledge, attack_assets = knowledge_entries or context.knowledge_entries or plan.retrieved_knowledge, assets or context.attack_assets or plan.assets
        summary = plan.reasoning_summary
        if self.provider:
            try: summary = (await self.provider.reason(plan, context)).summary
            except RuntimeError: pass  # Offline planning remains useful when the configured provider is unavailable.
        originals = self.builder.build(context, plan, knowledge, attack_assets)
        candidates, history = list(originals), []
        for original in originals:
            variants, records = self.mutator.mutate(original, mutation_names)
            candidates.extend(variants); history.extend(records)
        validations: dict[str, PromptValidationResult] = {}
        seen: set[str] = set()
        valid: list[Prompt] = []
        for candidate in candidates:
            result = self.validator.validate(candidate, seen)
            validations[candidate.id] = result
            if result.is_valid:
                seen.add(result.metadata["normalized"]); valid.append(candidate)
        estimates = {candidate.id: self._estimate(candidate, plan, len(history)) for candidate in valid}
        ranked = sorted(valid, key=lambda candidate: estimates[candidate.id].confidence, reverse=True)
        selected = ranked[0].model_copy(update={"confidence": estimates[ranked[0].id].confidence}) if ranked else None
        return PromptGenerationResult(prompts=ranked, selected_prompt=selected, reasoning_summary=summary, confidence=selected.confidence if selected else 0.0, mutation_history=history, validator_results=validations, quality_estimates=estimates)

    def _estimate(self, prompt: Prompt, plan: AttackPlan, mutation_count: int) -> PromptQualityEstimate:
        strategy = 1.0 if prompt.strategy_id and prompt.strategy_id in {item.id for item in plan.strategies} | {plan.selected_strategy} else 0.35
        objective = 1.0 if prompt.objective.strip() and prompt.objective.lower() in prompt.content.lower() else 0.65
        effectiveness = min(0.9, 0.45 + (0.15 if prompt.asset_ids else 0) + (0.1 if plan.selected_attack_family else 0))
        stealth = 0.75 if "authorized security assessment" in prompt.content.lower() else 0.5
        diversity = min(1.0, 0.35 + mutation_count / max(1, mutation_count + 4))
        confidence = round((strategy + objective + effectiveness + stealth + diversity) / 5, 3)
        return PromptQualityEstimate(strategy_consistency=strategy, objective_alignment=objective, expected_effectiveness=effectiveness, estimated_stealth=stealth, mutation_diversity=diversity, confidence=confidence, rationale="Internal planner-confidence estimate; it is not an attack or target-response score.")
