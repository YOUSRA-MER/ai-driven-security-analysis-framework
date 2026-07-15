"""AI provider interfaces and adapter placeholders."""

from backend.ai.providers.openrouter_provider import OpenRouterProvider
from backend.ai.providers.nvidia_provider import NvidiaProvider
from backend.ai.providers.provider_interface import AIProvider, ProviderMessage, ProviderRequest, ProviderResponse, ProviderSummary, ReasoningResult

__all__ = [
    "AIProvider",
    "NvidiaProvider",
    "OpenRouterProvider",
    "ProviderMessage",
    "ProviderRequest",
    "ProviderResponse",
    "ProviderSummary",
    "ReasoningResult",
]

