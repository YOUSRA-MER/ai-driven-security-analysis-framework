"""Backward-compatible data leakage attack strategy."""

from __future__ import annotations

from backend.attacks.data_exfiltration import DataExfiltrationAttack


class DataLeakageAttack(DataExfiltrationAttack):
    """Alias for data exfiltration probes kept for existing CLI users."""

    name = "data_leakage"
    category = "data_leakage"

