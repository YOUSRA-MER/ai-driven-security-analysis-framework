"""Conversation models independent from any provider SDK."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


@dataclass(slots=True)
class Message:
    """A normalized chat message exchanged with a target."""

    role: str
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(slots=True)
class Conversation:
    """A provider-neutral conversation history."""

    conversation_id: str = field(default_factory=lambda: str(uuid4()))
    messages: list[Message] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def add(self, role: str, content: str, **metadata: Any) -> Message:
        message = Message(role=role, content=content, metadata=metadata)
        self.messages.append(message)
        return message

    def copy_with_messages(self) -> "Conversation":
        return Conversation(
            conversation_id=self.conversation_id,
            messages=list(self.messages),
            metadata=dict(self.metadata),
        )

