"""RAG poisoning attack strategy."""

from __future__ import annotations

from backend.attacks.library import DatasetAttackStrategy


class RagPoisoningAttack(DatasetAttackStrategy):
    """Tests whether poisoned retrieval content can steer model behavior."""

    name = "rag_poisoning"
    category = "rag_poisoning"
    dataset_name = "rag_poisoning.json"

