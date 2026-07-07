"""Jailbreak attack strategy."""

from __future__ import annotations

from backend.attacks.library import DatasetAttackStrategy


class JailbreakAttack(DatasetAttackStrategy):
    """Runs controlled jailbreak probes using sourced benchmark techniques."""

    name = "jailbreak"
    category = "jailbreak"
    dataset_name = "jailbreak.json"

