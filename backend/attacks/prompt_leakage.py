"""Prompt leakage attack strategy."""

from __future__ import annotations

from backend.attacks.library import DatasetAttackStrategy


class PromptLeakageAttack(DatasetAttackStrategy):
    """Attempts to detect exposure of hidden instructions or runtime configuration."""

    name = "prompt_leakage"
    category = "prompt_leakage"
    dataset_name = "prompt_leakage.json"

