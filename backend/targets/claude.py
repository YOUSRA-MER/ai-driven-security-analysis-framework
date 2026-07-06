"""Claude target adapter placeholder."""

from __future__ import annotations

from typing import Sequence

from backend.models.conversation import Message
from backend.targets.base_target import TargetAdapter


class ClaudeTarget(TargetAdapter):
    """Extension point for Anthropic Claude targets."""

    def __init__(self, model: str, api_key: str, name: str | None = None) -> None:
        self.model = model
        self.api_key = api_key
        self.name = name or f"claude:{model}"

    async def send(self, messages: Sequence[Message]) -> Message:
        """TODO: Implement with the selected Anthropic SDK and response schema."""
        raise NotImplementedError("ClaudeTarget is an integration placeholder.")

