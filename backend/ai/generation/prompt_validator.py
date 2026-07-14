"""Validation for generated assessment prompts."""
from __future__ import annotations
import re
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
from backend.ai.models.prompt_validation import PromptValidationResult

if TYPE_CHECKING:
    from backend.ai.models.prompt_generation import Prompt

class PromptValidator(ABC):
    @abstractmethod
    def validate(self, prompt: "Prompt", seen_contents: set[str] | None = None) -> PromptValidationResult: ...

class PolicyPromptValidator(PromptValidator):
    """Checks generation integrity; it never raises for invalid candidates."""
    def __init__(self, min_length: int = 12, max_length: int = 12000) -> None:
        self.min_length, self.max_length = min_length, max_length

    def validate(self, prompt: "Prompt", seen_contents: set[str] | None = None) -> PromptValidationResult:
        content = prompt.content.strip()
        errors: list[str] = []
        warnings: list[str] = []
        if not content: errors.append("prompt content is empty")
        if len(content) < self.min_length: errors.append("prompt is shorter than the configured minimum")
        if len(content) > self.max_length: errors.append("prompt exceeds the configured maximum length")
        if re.search(r"\{\{[^}]*\}\}|\$\{[^}]*\}", content): errors.append("unresolved placeholder found")
        if "\x00" in content: errors.append("prompt contains a null character")
        if content.count("```") % 2: errors.append("unbalanced code fence")
        normalized = " ".join(content.lower().split())
        if seen_contents is not None and normalized in seen_contents: errors.append("duplicate prompt")
        if prompt.strategy_id and prompt.strategy_id not in str(prompt.metadata.get("allowed_strategy_ids", prompt.strategy_id)):
            errors.append("prompt strategy is inconsistent with its plan")
        if not prompt.objective.strip(): errors.append("prompt objective is empty")
        if not content.endswith((".", "?", "!", ":")): warnings.append("prompt has no terminal punctuation")
        return PromptValidationResult(is_valid=not errors, errors=errors, warnings=warnings, metadata={"length": str(len(content)), "normalized": normalized})
