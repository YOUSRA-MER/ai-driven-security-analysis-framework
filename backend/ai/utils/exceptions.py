"""Domain exceptions for the AI planning subsystem."""

from __future__ import annotations


class AISubsystemError(Exception):
    """Base exception for AI subsystem errors."""


class PlanningError(AISubsystemError):
    """Raised when a planning workflow cannot produce a valid plan."""


class RetrievalError(AISubsystemError):
    """Raised when a retrieval component cannot load or search a dataset."""


class ProviderError(AISubsystemError):
    """Raised when an AI provider adapter fails before returning a response."""


class ValidationError(AISubsystemError):
    """Raised when an AI subsystem model or prompt artifact is invalid."""

