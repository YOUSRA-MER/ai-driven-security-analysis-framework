"""OpenRouter provider for Qwen-backed planning reasoning."""

from __future__ import annotations

import asyncio
import json
import logging
import re
import time
from typing import Any, TypeVar
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from pydantic import BaseModel, ValidationError

from backend.ai.models.attack_plan import AttackPlan
from backend.ai.models.objective_analysis import ObjectiveAnalysis
from backend.ai.models.planner_result import PlannerError
from backend.ai.models.prompt_generation import Prompt, PromptGenerationResult
from backend.ai.models.reasoning_session import (
    AttackFamilyAssessment,
    AttackHypothesis,
    ConfidenceAssessment,
    PlanDirective,
    PlanValidation,
    ReasoningSession,
    StrategyEvaluation,
)
from backend.ai.providers.provider_interface import AIProvider, ProviderMessage, ProviderRequest, ProviderResponse, ReasoningResult
from backend.ai.reasoning.attack_family_prompt import AttackFamilyPromptBuilder
from backend.ai.reasoning.attack_plan_prompt import AttackPlanPromptBuilder
from backend.ai.reasoning.objective_prompt import ObjectivePromptBuilder
from backend.ai.reasoning.prompt_generation_prompt import PromptGenerationPromptBuilder
from backend.ai.reasoning.prompt_templates import (
    JSON_OUTPUT_INSTRUCTION,
    REPAIR_JSON_INSTRUCTION,
    build_reasoning_prompt,
    build_repair_prompt,
)
from backend.ai.reasoning.strategy_prompt import StrategyPromptBuilder
from backend.ai.utils.enums import ProviderRole
from backend.config.settings import Settings, get_settings


logger = logging.getLogger(__name__)
T = TypeVar("T", bound=BaseModel)


class OpenRouterProvider(AIProvider):
    """OpenRouter adapter for structured Qwen reasoning.

    The provider is the only component allowed to communicate with OpenRouter.
    It uses the OpenAI-compatible `/chat/completions` endpoint and requests
    strict JSON objects that are validated into Pydantic models.
    """

    def __new__(cls, settings: Settings | None = None):
        """Return the configured provider while preserving legacy imports."""

        resolved_settings = settings or get_settings()
        if cls is OpenRouterProvider and resolved_settings.llm_provider == "nvidia":
            from backend.ai.providers.nvidia_provider import NvidiaProvider

            return NvidiaProvider(settings=resolved_settings)
        return super().__new__(cls)

    def __init__(self, settings: Settings | None = None) -> None:
        """Initialize the provider.

        Args:
            settings: Optional application settings. If omitted, environment
                settings are loaded through `get_settings`.
        """

        self.settings = settings or get_settings()
        self.objective_prompt_builder = ObjectivePromptBuilder()
        self.attack_family_prompt_builder = AttackFamilyPromptBuilder()
        self.strategy_prompt_builder = StrategyPromptBuilder()
        self.attack_plan_prompt_builder = AttackPlanPromptBuilder()
        self.prompt_generation_prompt_builder = PromptGenerationPromptBuilder()

    @property
    def model(self) -> str:
        """Return the configured OpenRouter model."""

        return self.settings.openrouter_model

    async def complete(self, request: ProviderRequest) -> ProviderResponse:
        """Return a raw OpenRouter chat completion response.

        Args:
            request: Provider-neutral request object.

        Returns:
            Provider-neutral response object.

        Raises:
            RuntimeError: If the API key is missing or OpenRouter returns no
                assistant content after retries.
        """

        if not self.settings.openrouter_api_key:
            raise RuntimeError("OPENROUTER_API_KEY is not configured.")
        return await asyncio.to_thread(self._complete_sync, request)

    async def analyze_objective(self, objective: str) -> ObjectiveAnalysis | PlannerError:
        """Analyze a user assessment objective with Qwen.

        Args:
            objective: User-provided assessment objective.

        Returns:
            Structured objective analysis.
        """

        return await self._structured_step(
            step="analyze_objective",
            payload={"objective": objective},
            model=ObjectiveAnalysis,
            prompt=self.objective_prompt_builder.build(
                objective=objective,
                schema=ObjectiveAnalysis.model_json_schema(),
            ),
        )

    async def reason_about_attack(self, session: ReasoningSession) -> ReasoningResult:
        """Reason about retrieved knowledge and assets without selecting execution.

        Args:
            session: Current reasoning session.

        Returns:
            Provider-neutral reasoning result.
        """

        return await self._structured(
            task=(
                "Summarize how the retrieved knowledge and attack assets support "
                "the assessment objective. Do not generate prompts or execute attacks."
            ),
            payload={"session": self._compact_session(session)},
            model=ReasoningResult,
        )

    async def select_attack_family(self, session: ReasoningSession) -> AttackFamilyAssessment | PlannerError:
        """Select likely attack families from retrieved planning context."""

        payload = self._family_selection_payload(session)
        return await self._structured_step(
            step="select_attack_family",
            payload=payload,
            model=AttackFamilyAssessment,
            prompt=self.attack_family_prompt_builder.build(
                payload=payload,
                schema=AttackFamilyAssessment.model_json_schema(),
            ),
        )

    async def reason_attack_families(self, session: ReasoningSession) -> AttackFamilyAssessment | PlannerError:
        """Compatibility alias for attack-family reasoning."""

        return await self.select_attack_family(session)

    async def select_strategy(self, session: ReasoningSession) -> StrategyEvaluation | PlannerError:
        """Select the strongest strategy hypothesis for the objective."""

        payload = self._strategy_selection_payload(session)
        return await self._structured_step(
            step="select_strategy",
            payload=payload,
            model=StrategyEvaluation,
            prompt=self.strategy_prompt_builder.build(
                payload=payload,
                schema=StrategyEvaluation.model_json_schema(),
            ),
        )

    async def build_attack_plan(self, session: ReasoningSession) -> PlanDirective | PlannerError:
        """Build a plan directive from selected hypotheses and assets.

        The directive references existing strategy and asset IDs. It does not
        contain generated attack prompts.
        """

        payload = self._plan_directive_payload(session)
        return await self._structured_step(
            step="build_attack_plan",
            payload=payload,
            model=PlanDirective,
            prompt=self.attack_plan_prompt_builder.build(
                payload=payload,
                schema=PlanDirective.model_json_schema(),
            ),
        )

    async def generate_prompts(self, session: ReasoningSession) -> PromptGenerationResult | PlannerError:
        """Generate bounded prompt candidates from selected Dataset B assets.

        Args:
            session: Reasoning state containing the selected hypothesis and
                retrieved attack assets.

        Returns:
            Validated prompt-generation result or a step-scoped planner error.
        """

        payload = self._prompt_generation_payload(session)
        return await self._structured_step(
            step="generate_prompts",
            payload=payload,
            model=PromptGenerationResult,
            prompt=self.prompt_generation_prompt_builder.build(
                payload=payload,
                schema=PromptGenerationResult.model_json_schema(),
            ),
        )

    async def optimize_prompt(self, prompt: Prompt) -> Prompt:
        """Optimize a selected dataset prompt for clarity.

        Args:
            prompt: Prompt object derived from an existing Dataset B asset.

        Returns:
            Optimized prompt object.
        """

        return await self._structured(
            task=(
                "Optimize this authorized assessment prompt for clarity and test "
                "observability. Integrate the objective, preserve safety scope, and return no placeholders. "
                "Return the Prompt JSON object only."
            ),
            payload={"prompt": prompt.model_dump()},
            model=Prompt,
        )

    async def validate_plan_reasoning(self, session: ReasoningSession) -> PlanValidation:
        """Validate whether the selected plan remains objective-aligned."""

        return await self._structured(
            task="Validate plan alignment and alternatives. Return JSON only.",
            payload={"session": self._compact_session(session)},
            model=PlanValidation,
        )

    async def estimate_confidence(self, session: ReasoningSession) -> ConfidenceAssessment:
        """Estimate confidence for the selected plan."""

        return await self._structured(
            task="Estimate planning confidence. Return JSON only.",
            payload={"session": self._compact_session(session)},
            model=ConfidenceAssessment,
        )

    async def reason(self, plan: Any, context: Any) -> ReasoningResult:
        """Compatibility wrapper for generic provider reasoning."""

        return await self._structured(
            task="Summarize this non-executable plan reasoning. Return JSON only.",
            payload={"plan": self._safe_dump(plan), "context": self._safe_dump(context)},
            model=ReasoningResult,
        )

    async def generate_attack_prompt(self, prompt: Prompt) -> Prompt:
        """Compatibility wrapper that delegates to prompt optimization."""

        return await self.optimize_prompt(prompt)

    async def mutate_prompt(self, prompt: Prompt, mutation: str) -> Prompt:
        """Compatibility wrapper for future mutation support."""

        candidate = prompt.model_copy(update={"metadata": {**prompt.metadata, "requested_mutation": mutation}})
        return await self.optimize_prompt(candidate)

    async def summarize_response(self, response: str):
        """Summarize a response.

        This is retained for interface compatibility; response scoring is out of
        scope for planner integration.
        """

        from backend.ai.providers.provider_interface import ProviderSummary

        return await self._structured(
            task="Summarize this text for a planning audit report. Return JSON only.",
            payload={"response": response},
            model=ProviderSummary,
        )

    async def generate_hypotheses(self, session: ReasoningSession):
        """Generate strategy hypotheses for interface compatibility."""

        class Hypotheses(BaseModel):
            hypotheses: list[AttackHypothesis] = []

        result = await self._structured(
            task="Generate non-executable planning hypotheses. Return JSON only.",
            payload={"session": self._compact_session(session)},
            model=Hypotheses,
        )
        return result.hypotheses

    async def evaluate_strategies(self, session: ReasoningSession) -> StrategyEvaluation:
        """Compatibility alias for `select_strategy`."""

        return await self.select_strategy(session)

    async def direct_plan(self, session: ReasoningSession) -> PlanDirective:
        """Compatibility alias for `build_attack_plan`."""

        return await self.build_attack_plan(session)

    async def health(self) -> dict[str, Any]:
        """Check OpenRouter configuration and API reachability.

        Returns:
            Health details safe to expose through API responses.
        """

        configured = self.settings.openrouter_configured
        reachable = False
        error = ""
        if configured:
            try:
                await asyncio.to_thread(self._get_models_sync)
                reachable = True
            except Exception as exc:  # noqa: BLE001 - health endpoint must report errors.
                error = str(exc)
        return {
            "api_configured": configured,
            "api_reachable": reachable,
            "model": self.model,
            "planner_ready": configured and reachable,
            "error": error,
        }

    async def _structured(self, task: str, payload: dict[str, Any], model: type[T]) -> T:
        """Compatibility helper for legacy structured provider calls."""

        schema = model.model_json_schema()
        prompt = build_reasoning_prompt(
            task_name=task,
            output_model=model.__name__,
            responsibilities=[
                "Reason over the supplied payload for the requested planner compatibility task.",
                "Return only the model described by the schema.",
                "Do not execute attacks, call targets, or invent IDs.",
            ],
            schema=schema,
            payload=payload,
        )
        result = await self._structured_step(step=model.__name__, payload=payload, model=model, prompt=prompt)
        if isinstance(result, PlannerError):
            raise RuntimeError(result.message)
        return result

    async def _structured_step(
        self,
        *,
        step: str,
        payload: dict[str, Any],
        model: type[T],
        prompt: str,
    ) -> T | PlannerError:
        """Request one small JSON object from OpenRouter and validate it.

        Args:
            step: Name of the provider step being executed.
            payload: JSON-serializable context payload.
            model: Pydantic model expected in the response.
            prompt: Complete prompt built by the reasoning prompt layer.

        Returns:
            Parsed Pydantic object, or a step-scoped planner error after all
            parsing and retry strategies fail.
        """

        schema = model.model_json_schema()
        requests = [
            self._build_structured_request(
                prompt=prompt,
                system_prompt=JSON_OUTPUT_INSTRUCTION,
                include_response_format=True,
            ),
            self._build_structured_request(
                prompt=build_repair_prompt(original_prompt=prompt, schema=schema, payload=payload),
                system_prompt=REPAIR_JSON_INSTRUCTION,
                include_response_format=True,
            ),
        ]
        last_error: Exception | None = None
        last_raw_response: str | None = None
        response_format_unsupported = False
        for attempt, current_request in enumerate(requests, start=1):
            started = time.perf_counter()
            try:
                logger.info("Reasoning request started", extra={"model": self.model, "step": step, "attempt": attempt})
                response = await self.complete(current_request)
                last_raw_response = response.content
                logger.info(
                    "Raw OpenRouter response before JSON parsing",
                    extra={
                        "model": response.model,
                        "step": step,
                        "attempt": attempt,
                        "raw_response": response.content,
                    },
                )
                parsed_json = self._parse_json_object(response.content)
                parsed = model.model_validate(parsed_json)
                usage = response.metadata.get("usage", {})
                logger.info(
                    "Reasoning request completed",
                    extra={
                        "model": response.model,
                        "step": step,
                        "attempt": attempt,
                        "elapsed_ms": round((time.perf_counter() - started) * 1000, 2),
                        "tokens": usage,
                    },
                )
                return parsed
            except RuntimeError as exc:
                last_error = exc
                response_format_unsupported = response_format_unsupported or self._looks_like_response_format_error(str(exc))
                logger.warning(
                    "Reasoning request transport failed",
                    extra={
                        "model": self.model,
                        "step": step,
                        "attempt": attempt,
                        "elapsed_ms": round((time.perf_counter() - started) * 1000, 2),
                        "error": str(exc),
                    },
                )
                if not response_format_unsupported:
                    break
            except (ValidationError, json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
                last_error = exc
                logger.warning(
                    "Reasoning request failed",
                    extra={
                        "model": self.model,
                        "step": step,
                        "attempt": attempt,
                        "elapsed_ms": round((time.perf_counter() - started) * 1000, 2),
                        "error": str(exc),
                    },
                )
                if attempt < len(requests):
                    await asyncio.sleep(min(2**attempt, 6))
        if response_format_unsupported:
            fallback = self._build_structured_request(
                prompt=build_repair_prompt(original_prompt=prompt, schema=schema, payload=payload),
                system_prompt=REPAIR_JSON_INSTRUCTION,
                include_response_format=False,
            )
            try:
                logger.info("Reasoning request started without response_format", extra={"model": self.model, "step": step})
                response = await self.complete(fallback)
                last_raw_response = response.content
                logger.info(
                    "Raw OpenRouter response before JSON parsing",
                    extra={"model": response.model, "step": step, "attempt": "fallback", "raw_response": response.content},
                )
                parsed_json = self._parse_json_object(response.content)
                return model.model_validate(parsed_json)
            except (ValidationError, json.JSONDecodeError, RuntimeError, KeyError, TypeError, ValueError) as exc:
                last_error = exc

        return PlannerError(
            step=step,
            message=f"OpenRouter JSON response invalid for {step}: {last_error}",
            raw_response=last_raw_response,
            retryable=True,
            metadata={"model": self.model, "expected_model": model.__name__},
        )

    def _build_structured_request(
        self,
        *,
        prompt: str,
        system_prompt: str,
        include_response_format: bool = True,
    ) -> ProviderRequest:
        """Build a JSON-only structured request for OpenRouter."""

        metadata: dict[str, Any] = {"temperature": 0.1, "max_tokens": 2048}
        if include_response_format:
            metadata["response_format"] = {"type": "json_object"}
        return ProviderRequest(
            model=self.model,
            messages=[
                ProviderMessage(
                    role=ProviderRole.SYSTEM,
                    content=system_prompt,
                ),
                ProviderMessage(
                    role=ProviderRole.USER,
                    content=prompt,
                ),
            ],
            metadata=metadata,
        )

    def _complete_sync(self, request: ProviderRequest) -> ProviderResponse:
        """Run a synchronous OpenRouter chat completion request."""

        body = json.dumps(
            {
                "model": request.model or self.model,
                "messages": [{"role": message.role.value, "content": message.content} for message in request.messages],
                **request.metadata,
            },
            ensure_ascii=False,
        ).encode("utf-8")
        headers = {
            "Authorization": f"Bearer {self.settings.openrouter_api_key}",
            "Content-Type": "application/json",
            "X-Title": self.settings.app_name,
        }
        url = f"{self.settings.openrouter_base_url}/chat/completions"
        try:
            with urlopen(Request(url, data=body, headers=headers, method="POST"), timeout=self.settings.openrouter_timeout_seconds) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"OpenRouter HTTP {exc.code}: {detail[:500]}") from exc
        except (URLError, TimeoutError) as exc:
            raise RuntimeError(f"OpenRouter request failed: {exc}") from exc

        choices = payload.get("choices") or []
        content = choices[0].get("message", {}).get("content") if choices else None
        if not content:
            raise RuntimeError("OpenRouter returned no assistant message content.")
        return ProviderResponse(
            content=content,
            model=str(payload.get("model") or request.model or self.model),
            metadata={"id": payload.get("id", ""), "usage": payload.get("usage", {})},
        )

    def _get_models_sync(self) -> None:
        """Call OpenRouter models endpoint for reachability checks."""

        headers = {"Authorization": f"Bearer {self.settings.openrouter_api_key}"}
        with urlopen(Request(f"{self.settings.openrouter_base_url}/models", headers=headers, method="GET"), timeout=10) as response:
            if response.status >= 400:
                raise RuntimeError(f"OpenRouter models endpoint returned HTTP {response.status}")
            response.read(128)

    def _parse_json_object(self, content: str) -> dict[str, Any]:
        """Parse the first valid JSON object from a provider response.

        The parser accepts raw JSON, fenced JSON, JSON surrounded by natural
        language, and responses that contain multiple brace pairs. It never uses
        `eval` or unsafe parsing.
        """

        text = content.strip()
        candidates = [text]
        candidates.extend(match.group(1).strip() for match in re.finditer(r"```(?:json|JSON)?\s*(.*?)```", text, re.DOTALL))
        candidates.extend(self._extract_json_object_candidates(text))

        errors: list[str] = []
        seen: set[str] = set()
        for candidate in candidates:
            if not candidate or candidate in seen:
                continue
            seen.add(candidate)
            try:
                parsed = json.loads(candidate)
            except json.JSONDecodeError as exc:
                errors.append(str(exc))
                continue
            if isinstance(parsed, dict):
                return parsed
            errors.append("Parsed JSON was not an object.")
        raise json.JSONDecodeError(
            "No valid JSON object found in OpenRouter response. "
            + " | ".join(errors[:3]),
            text,
            0,
        )

    def _extract_json_object_candidates(self, text: str) -> list[str]:
        """Extract brace-balanced JSON object candidates from arbitrary text."""

        candidates: list[str] = []
        starts = [index for index, char in enumerate(text) if char == "{"]
        for start in starts:
            depth = 0
            in_string = False
            escaped = False
            for index in range(start, len(text)):
                char = text[index]
                if in_string:
                    if escaped:
                        escaped = False
                    elif char == "\\":
                        escaped = True
                    elif char == '"':
                        in_string = False
                    continue
                if char == '"':
                    in_string = True
                elif char == "{":
                    depth += 1
                elif char == "}":
                    depth -= 1
                    if depth == 0:
                        candidates.append(text[start : index + 1])
                        break
        return candidates

    def _looks_like_response_format_error(self, message: str) -> bool:
        """Return whether an API error likely rejects `response_format`."""

        lowered = message.lower()
        return "response_format" in lowered or "json_object" in lowered

    def _family_selection_payload(self, session: ReasoningSession) -> dict[str, Any]:
        """Build a bounded payload for attack-family selection."""

        return {
            "objective": session.assessment_objective,
            "requested_prompt_count": session.metadata.get("requested_prompt_count", 3),
            "target_profile": session.metadata.get("target_profile", ""),
            "attack_context": session.metadata.get("attack_context", ""),
            "objective_analysis": self._safe_dump(session.objective_analysis),
            "retrieved_knowledge": [
                {
                    "id": item.id,
                    "title": item.title,
                    "category": item.category,
                    "summary": item.summary,
                    "tags": item.tags[:10],
                }
                for item in session.retrieved_knowledge[:10]
            ],
            "retrieved_attack_asset_categories": sorted({asset.category for asset in session.retrieved_attack_assets[:10]}),
        }

    def _strategy_selection_payload(self, session: ReasoningSession) -> dict[str, Any]:
        """Build a bounded payload for hypothesis and strategy selection."""

        return {
            "objective": session.assessment_objective,
            "objective_analysis": self._safe_dump(session.objective_analysis),
            "selected_family_assessment": session.metadata.get("family_assessment", {}),
            "candidate_strategies": [self._safe_dump(item) for item in session.candidate_strategies[:5]],
            "hypotheses": [self._safe_dump(item) for item in session.hypotheses[:5]],
        }

    def _plan_directive_payload(self, session: ReasoningSession) -> dict[str, Any]:
        """Build a bounded payload for non-executable plan directives."""

        return {
            "objective": session.assessment_objective,
            "objective_analysis": self._safe_dump(session.objective_analysis),
            "strategy_evaluation": session.metadata.get("strategy_evaluation", {}),
            "selected_hypothesis": self._safe_dump(session.selected_hypothesis),
            "candidate_strategy_ids": [item.id for item in session.candidate_strategies[:5]],
            "available_asset_ids": [item.id for item in session.retrieved_attack_assets[:10]],
            "hypotheses": [self._safe_dump(item) for item in session.hypotheses[:5]],
        }

    def _prompt_generation_payload(self, session: ReasoningSession) -> dict[str, Any]:
        """Build a bounded payload for prompt generation from selected assets."""

        selected_asset_ids = set(session.metadata.get("selected_asset_ids", []))
        candidate_assets = [
            asset
            for asset in session.retrieved_attack_assets
            if not selected_asset_ids or asset.id in selected_asset_ids
        ][:5]
        return {
            "objective": session.assessment_objective,
            "objective_analysis": self._safe_dump(session.objective_analysis),
            "selected_hypothesis": self._safe_dump(session.selected_hypothesis),
            "plan_directive": session.metadata.get("plan_directive", {}),
            "selected_assets": [
                {
                    "id": asset.id,
                    "name": asset.name,
                    "category": asset.category,
                    "severity": asset.severity,
                    "attack_prompt": asset.attack_prompt,
                    "success_criteria": asset.success_criteria,
                    "tags": asset.tags[:12],
                }
                for asset in candidate_assets
            ],
        }

    def _compact_session(self, session: ReasoningSession) -> dict[str, Any]:
        """Return a compact session payload to keep reasoning requests bounded."""

        return {
            "session_id": session.session_id,
            "assessment_objective": session.assessment_objective,
            "objective_analysis": self._safe_dump(session.objective_analysis),
            "retrieved_knowledge": [self._safe_dump(item) for item in session.retrieved_knowledge[:10]],
            "retrieved_attack_assets": [
                {
                    "id": asset.id,
                    "name": asset.name,
                    "category": asset.category,
                    "severity": asset.severity,
                    "tags": asset.tags[:12],
                    "description": asset.description[:500],
                    "success_criteria": asset.success_criteria[:500],
                }
                for asset in session.retrieved_attack_assets[:10]
            ],
            "candidate_strategies": [self._safe_dump(item) for item in session.candidate_strategies[:5]],
            "hypotheses": [self._safe_dump(item) for item in session.hypotheses[:5]],
            "selected_hypothesis": self._safe_dump(session.selected_hypothesis),
            "metadata": session.metadata,
        }

    def _safe_dump(self, value: Any) -> Any:
        """Convert Pydantic objects to JSON-safe values."""

        if isinstance(value, BaseModel):
            return value.model_dump()
        return value
