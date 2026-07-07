"""Role-play jailbreak attack strategy."""

from __future__ import annotations

from backend.attacks.library import DatasetAttackStrategy


class RoleplayAttack(DatasetAttackStrategy):
    """Tests fictional, persona, and transcript frames."""

    name = "roleplay"
    category = "roleplay"
    dataset_name = "roleplay.json"

