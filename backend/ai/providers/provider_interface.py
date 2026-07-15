"""Provider interface definitions for future AI model integrations."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from backend.ai.utils.enums import ProviderRole
from backend.ai.models.objective_analysis import ObjectiveAnalysis
from backend.ai.models.planner_result import PlannerError
from backend.ai.models.prompt_generation import Prompt, PromptGenerationResult
from backend.ai.models.reasoning_session import AttackFamilyAssessment, AttackHypothesis, ConfidenceAssessment, PlanDirective, PlanValidation, ReasoningSession, StrategyEvaluation


class ProviderMessage(BaseModel):
    """Provider-neutral chat message.

    Attributes:
        role: Provider message role.
        content: Message content.
        metadata: Provider-specific annotations.
    """

    model_config = ConfigDict(extra="forbid")

    role: ProviderRole
    content: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class ProviderRequest(BaseModel):
    """Provider-neutral request envelope.

    Attributes:
        messages: Ordered provider messages.
        model: Optional provider model identifier.
        metadata: Provider-specific request options.
    """

    model_config = ConfigDict(extra="forbid")

    messages: list[ProviderMessage]
    model: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class ProviderResponse(BaseModel):
    """Provider-neutral response envelope.

    Attributes:
        content: Provider response content.
        model: Optional model that produced the response.
        metadata: Provider-specific response data.
    """

    model_config = ConfigDict(extra="forbid")

    content: str
    model: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class ReasoningResult(BaseModel):
    """Provider-neutral explanation used by generation, never a raw payload."""
    model_config = ConfigDict(extra="forbid")
    summary: str
    recommended_mutations: list[str] = Field(default_factory=list)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)


class ProviderSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")
    summary: str


class AIProvider(ABC):
    """Abstract interface for AI provider adapters."""

    @abstractmethod
    async def complete(self, request: ProviderRequest) -> ProviderResponse:
        """Return a provider completion for a request.

        Args:
            request: Provider-neutral request object.

        Returns:
            Provider-neutral response object.
        """

        raise NotImplementedError

    @abstractmethod
    async def analyze_objective(self, objective: str) -> ObjectiveAnalysis | PlannerError:
        raise NotImplementedError

    @abstractmethod
    async def reason_about_attack(self, session: ReasoningSession) -> ReasoningResult:
        raise NotImplementedError

    @abstractmethod
    async def select_attack_family(self, session: ReasoningSession) -> AttackFamilyAssessment | PlannerError:
        raise NotImplementedError

    @abstractmethod
    async def select_strategy(self, session: ReasoningSession) -> StrategyEvaluation | PlannerError:
        raise NotImplementedError

    @abstractmethod
    async def build_attack_plan(self, session: ReasoningSession) -> PlanDirective | PlannerError:
        raise NotImplementedError

    @abstractmethod
    async def generate_prompts(self, session: ReasoningSession) -> PromptGenerationResult | PlannerError:
        raise NotImplementedError

    @abstractmethod
    async def reason(self, plan: Any, context: Any) -> ReasoningResult:
        raise NotImplementedError

    @abstractmethod
    async def generate_attack_prompt(self, prompt: Prompt) -> Prompt:
        raise NotImplementedError

    @abstractmethod
    async def mutate_prompt(self, prompt: Prompt, mutation: str) -> Prompt:
        raise NotImplementedError

    @abstractmethod
    async def optimize_prompt(self, prompt: Prompt) -> Prompt:
        raise NotImplementedError

    @abstractmethod
    async def summarize_response(self, response: str) -> ProviderSummary:
        raise NotImplementedError

    @abstractmethod
    async def reason_attack_families(self, session: ReasoningSession) -> AttackFamilyAssessment: raise NotImplementedError
    @abstractmethod
    async def generate_hypotheses(self, session: ReasoningSession) -> list[AttackHypothesis]: raise NotImplementedError
    @abstractmethod
    async def evaluate_strategies(self, session: ReasoningSession) -> StrategyEvaluation: raise NotImplementedError
    @abstractmethod
    async def estimate_confidence(self, session: ReasoningSession) -> ConfidenceAssessment: raise NotImplementedError
    @abstractmethod
    async def direct_plan(self, session: ReasoningSession) -> PlanDirective: raise NotImplementedError
    @abstractmethod
    async def validate_plan_reasoning(self, session: ReasoningSession) -> PlanValidation: raise NotImplementedError

