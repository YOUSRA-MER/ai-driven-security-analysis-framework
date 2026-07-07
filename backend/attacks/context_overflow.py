"""Long-context and context-overflow attack strategy."""

from __future__ import annotations

from backend.attacks.library import DatasetAttackStrategy


class ContextOverflowAttack(DatasetAttackStrategy):
    """Tests long-context, many-shot, and recency-based instruction drift."""

    name = "context_overflow"
    category = "context_overflow"
    dataset_name = "context_overflow.json"

