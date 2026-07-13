"""Prompt validation interface for generated prompt candidates."""

from __future__ import annotations

from abc import ABC, abstractmethod

from pydantic import BaseModel, ConfigDict, Field


class PromptValidationResult(BaseModel):
    """Result of validating a generated prompt candidate.

    Attributes:
        is_valid: Whether the prompt candidate passed validation.
        errors: Blocking validation errors.
        warnings: Non-blocking validation warnings.
        metadata: Additional validator annotations.
    """

    model_config = ConfigDict(extra="forbid")

    is_valid: bool
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    metadata: dict[str, str] = Field(default_factory=dict)


class PromptValidator(ABC):
    """Validates prompt candidates before they leave the AI subsystem."""

    @abstractmethod
    def validate(self, prompt: str) -> PromptValidationResult:
        """Validate a prompt candidate.

        Args:
            prompt: Prompt text to validate.

        Returns:
            Structured validation result.
        """

        raise NotImplementedError


class PolicyPromptValidator(PromptValidator):
    """Placeholder validator for policy and scope checks."""

    def validate(self, prompt: str) -> PromptValidationResult:
        """Validate a prompt candidate."""

        raise NotImplementedError("Prompt validation is not implemented yet.")

