"""Tool abuse attack strategy."""

from __future__ import annotations

from backend.attacks.library import DatasetAttackStrategy


class ToolAbuseAttack(DatasetAttackStrategy):
    """Tests unsafe tool invocation, side effects, and agentic overreach."""

    name = "tool_abuse"
    category = "tool_abuse"
    dataset_name = "tool_abuse.json"
