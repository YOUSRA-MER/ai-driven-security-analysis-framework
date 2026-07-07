"""Data exfiltration attack strategy."""

from __future__ import annotations

from backend.attacks.library import DatasetAttackStrategy


class DataExfiltrationAttack(DatasetAttackStrategy):
    """Tests whether a target exposes secrets, private data, traces, or training data."""

    name = "data_exfiltration"
    category = "data_exfiltration"
    dataset_name = "data_exfiltration.json"

