"""AI provider interfaces and adapter placeholders."""

from backend.ai.providers.openrouter_provider import OpenRouterProvider
from backend.ai.providers.nvidia_provider import NvidiaProvider
from backend.ai.providers.provider_interface import AIProvider, LLMProvider, ProviderMessage, ProviderRequest, ProviderResponse, ProviderSummary, ReasoningResult

__all__ = [
    "AIProvider",
    "LLMProvider",
    "NvidiaProvider",
    "OpenRouterProvider",
    "ProviderMessage",
    "ProviderRequest",
    "ProviderResponse",
    "ProviderSummary",
    "ReasoningResult",
]

