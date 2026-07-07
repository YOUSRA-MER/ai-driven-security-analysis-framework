"""Direct prompt injection attack strategy."""

from __future__ import annotations

from backend.attacks.library import DatasetAttackStrategy


class PromptInjectionAttack(DatasetAttackStrategy):
    """Tests whether a target follows attacker instructions over application policy."""

    name = "prompt_injection"
    category = "prompt_injection"
    dataset_name = "prompt_injection.json"

