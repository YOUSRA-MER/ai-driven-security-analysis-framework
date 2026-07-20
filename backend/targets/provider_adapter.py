"""Bridge existing target adapters to the provider completion interface."""

from __future__ import annotations

from backend.ai.providers.provider_interface import ProviderRequest, ProviderResponse
from backend.models.conversation import Message
from backend.targets.base_target import TargetAdapter


class TargetAdapterProvider:
    """Expose any existing ``TargetAdapter`` as an LLM completion provider."""

    def __init__(self, target: TargetAdapter) -> None:
        self.target = target

    @property
    def provider_name(self) -> str:
        """Return a stable provider label derived from the adapter class."""

        class_name = self.target.__class__.__name__
        return class_name.removesuffix("Target").lower() or "target"

    @property
    def model(self) -> str:
        """Return the target model when the adapter exposes one."""

        return str(getattr(self.target, "model", "") or "")

    async def complete(self, request: ProviderRequest) -> ProviderResponse:
        """Convert provider messages to the repository's target message model."""

        messages = [
            Message(
                role=message.role.value,
                content=message.content,
                metadata=dict(message.metadata),
            )
            for message in request.messages
        ]
        response = await self.target.send(messages)
        if not isinstance(response, Message):
            raise TypeError("Target adapter returned a malformed response object.")
        return ProviderResponse(
            content=response.content,
            model=request.model or self.model or None,
            metadata=dict(response.metadata),
        )
