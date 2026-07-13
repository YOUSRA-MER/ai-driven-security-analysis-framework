"""Attack asset model definitions."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class AttackAsset(BaseModel):
    """Normalized attack prompt or payload asset loaded from Dataset B.

    Attributes:
        id: Stable attack asset identifier.
        name: Human-readable attack name.
        category: Attack category used by orchestration and reporting.
        attack_prompt: Concrete prompt text or payload template.
        severity: Dataset-provided severity label.
        owasp_llm_top_10: OWASP GenAI mapping.
        mitre_atlas: MITRE ATLAS mapping.
        tags: Search, routing, and mutation tags.
        original_source: Source label from the attack dataset.
        reference_url: Validated source URL.
        metadata: Additional source row or import metadata.
    """

    model_config = ConfigDict(extra="forbid")

    id: str
    name: str
    category: str
    attack_prompt: str
    severity: str
    owasp_llm_top_10: str
    mitre_atlas: str
    description: str = ""
    expected_behavior: str = ""
    success_criteria: str = ""
    tags: list[str] = Field(default_factory=list)
    original_source: str = ""
    reference_url: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)
