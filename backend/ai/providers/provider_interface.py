"""Provider interface definitions for future AI model integrations."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from backend.ai.utils.enums import ProviderRole


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

