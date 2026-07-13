"""OpenRouter provider adapter placeholder."""

from __future__ import annotations

from backend.ai.providers.provider_interface import AIProvider, ProviderRequest, ProviderResponse


class OpenRouterProvider(AIProvider):
    """Placeholder adapter for a future OpenRouter integration.

    This class intentionally does not implement HTTP requests, authentication,
    retry behavior, streaming, or provider-specific payload construction.
    """

    def __init__(self, api_key: str | None = None, default_model: str | None = None) -> None:
        """Initialize the placeholder provider.

        Args:
            api_key: Optional API key that future implementations may use.
            default_model: Optional provider model identifier.
        """

        self.api_key = api_key
        self.default_model = default_model

    async def complete(self, request: ProviderRequest) -> ProviderResponse:
        """Return a provider completion for a request."""

        raise NotImplementedError("OpenRouter requests are intentionally not implemented yet.")

