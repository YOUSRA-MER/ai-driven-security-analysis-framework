"""Encoding and obfuscation attack strategy."""

from __future__ import annotations

from backend.attacks.library import DatasetAttackStrategy


class EncodingAttack(DatasetAttackStrategy):
    """Tests encoded, transformed, or delimiter-wrapped instructions."""

    name = "encoding"
    category = "encoding"
    dataset_name = "encoding.json"

