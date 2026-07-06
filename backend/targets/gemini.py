"""Gemini target adapter placeholder."""

from __future__ import annotations

from typing import Sequence

from backend.models.conversation import Message
from backend.targets.base_target import TargetAdapter


class GeminiTarget(TargetAdapter):
    """Extension point for Google Gemini targets."""

    def __init__(self, model: str, api_key: str, name: str | None = None) -> None:
        self.model = model
        self.api_key = api_key
        self.name = name or f"gemini:{model}"

    async def send(self, messages: Sequence[Message]) -> Message:
        """TODO: Implement with the selected Gemini SDK and response schema."""
        raise NotImplementedError("GeminiTarget is an integration placeholder.")

