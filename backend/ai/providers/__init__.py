"""AI provider interfaces and adapter placeholders."""

from backend.ai.providers.openrouter_provider import OpenRouterProvider
from backend.ai.providers.provider_interface import AIProvider, ProviderMessage, ProviderRequest, ProviderResponse

__all__ = [
    "AIProvider",
    "OpenRouterProvider",
    "ProviderMessage",
    "ProviderRequest",
    "ProviderResponse",
]

