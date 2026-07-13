"""Session memory interface for planner workflows."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class SessionMemory(ABC):
    """Stores request-scoped AI planning state."""

    @abstractmethod
    def get(self, session_id: str, key: str) -> Any:
        """Return a value from session memory.

        Args:
            session_id: Session identifier.
            key: Memory key.

        Returns:
            Stored value, if available.
        """

        raise NotImplementedError

    @abstractmethod
    def set(self, session_id: str, key: str, value: Any) -> None:
        """Store a value in session memory.

        Args:
            session_id: Session identifier.
            key: Memory key.
            value: Value to store.
        """

        raise NotImplementedError


class InMemorySessionMemory(SessionMemory):
    """Placeholder in-memory session memory implementation."""

    def get(self, session_id: str, key: str) -> Any:
        """Return a value from session memory."""

        raise NotImplementedError("Session memory storage is not implemented yet.")

    def set(self, session_id: str, key: str, value: Any) -> None:
        """Store a value in session memory."""

        raise NotImplementedError("Session memory storage is not implemented yet.")

