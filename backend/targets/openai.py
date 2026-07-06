"""OpenAI target adapter placeholder."""

from __future__ import annotations

from typing import Sequence

from backend.models.conversation import Message
from backend.targets.base_target import TargetAdapter


class OpenAITarget(TargetAdapter):
    """Extension point for OpenAI-compatible targets."""

    def __init__(self, model: str, api_key: str, name: str | None = None) -> None:
        self.model = model
        self.api_key = api_key
        self.name = name or f"openai:{model}"

    async def send(self, messages: Sequence[Message]) -> Message:
        """TODO: Implement with the selected OpenAI SDK and response schema."""
        raise NotImplementedError("OpenAITarget is an integration placeholder.")

