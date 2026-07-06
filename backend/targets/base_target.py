"""Target adapter interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Sequence

from backend.models.conversation import Message


class TargetAdapter(ABC):
    """Provider-neutral interface for sending prompts to a target."""

    name: str

    @abstractmethod
    async def send(self, messages: Sequence[Message]) -> Message:
        """Send normalized messages to the target and return its response."""

