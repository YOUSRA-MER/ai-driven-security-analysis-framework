"""Indirect prompt injection attack strategy."""

from __future__ import annotations

from backend.attacks.library import DatasetAttackStrategy


class IndirectPromptInjectionAttack(DatasetAttackStrategy):
    """Embeds instructions inside content that a RAG or tool-using app may ingest."""

    name = "indirect_prompt_injection"
    category = "indirect_prompt_injection"
    dataset_name = "indirect_prompt_injection.json"

