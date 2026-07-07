"""Multilingual attack strategy."""

from __future__ import annotations

from backend.attacks.library import DatasetAttackStrategy


class MultilingualAttack(DatasetAttackStrategy):
    """Tests cross-lingual and mixed-script prompt attacks."""

    name = "multilingual"
    category = "multilingual"
    dataset_name = "multilingual.json"

