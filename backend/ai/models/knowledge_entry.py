"""Knowledge dataset model definitions."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class KnowledgeEntry(BaseModel):
    """Normalized planning knowledge loaded from Dataset A.

    Attributes:
        id: Stable knowledge graph identifier.
        title: Human-readable title.
        category: Knowledge category such as objective, strategy, mitigation, or taxonomy.
        summary: Short planner-facing summary.
        source_path: Optional dataset-relative source path.
        tags: Search and routing tags.
        relationships: IDs of related knowledge graph entities.
        metadata: Additional source-specific fields retained from the dataset.
    """

    model_config = ConfigDict(extra="forbid")

    id: str
    title: str
    category: str
    summary: str = ""
    source_path: str | None = None
    tags: list[str] = Field(default_factory=list)
    relationships: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

