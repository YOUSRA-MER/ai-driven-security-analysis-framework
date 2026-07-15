"""Dataset A access interface for planning knowledge."""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from backend.ai.models.knowledge_entry import KnowledgeEntry
from backend.ai.utils.constants import KNOWLEDGE_DATASET_DIR
from backend.ai.utils.exceptions import RetrievalError


class DatasetARepository(ABC):
    """Abstract repository for the framework knowledge dataset.

    Dataset A is the reasoning layer used by planners. It contains objectives,
    attack-family descriptions, strategy metadata, mitigation guidance, taxonomy
    mappings, and references. It does not contain executable attack prompts.
    """

    def __init__(self, dataset_dir: Path = KNOWLEDGE_DATASET_DIR) -> None:
        """Initialize the repository.

        Args:
            dataset_dir: Filesystem path for Dataset A.
        """

        self.dataset_dir = dataset_dir

    @abstractmethod
    def load_entries(self) -> list[KnowledgeEntry]:
        """Load all normalized knowledge entries.

        Returns:
            A list of normalized knowledge records.

        Raises:
            NotImplementedError: Until concrete dataset loading is implemented.
        """

        raise NotImplementedError

    @abstractmethod
    def get_entry(self, entry_id: str) -> KnowledgeEntry | None:
        """Return one knowledge entry by ID.

        Args:
            entry_id: Stable knowledge entry identifier.

        Returns:
            The matching entry, or `None` if not found.
        """

        raise NotImplementedError


class FileDatasetARepository(DatasetARepository):
    """Filesystem-backed Dataset A repository placeholder."""

    _cache: dict[str, list[KnowledgeEntry]] = {}
    _cache_hits: int = 0
    _cache_misses: int = 0

    def load_entries(self) -> list[KnowledgeEntry]:
        """Load all normalized knowledge entries from disk.

        Returns:
            Normalized Dataset A entries from the knowledge dataset.

        Raises:
            RetrievalError: If the dataset directory does not exist or a JSON
                file cannot be parsed.
        """

        cache_key = str(self.dataset_dir.resolve())
        if cache_key in self._cache:
            type(self)._cache_hits += 1
            return [entry.model_copy(deep=True) for entry in self._cache[cache_key]]

        type(self)._cache_misses += 1
        if not self.dataset_dir.exists():
            raise RetrievalError(f"Dataset A directory does not exist: {self.dataset_dir}")

        entries: list[KnowledgeEntry] = []
        for path in sorted(self.dataset_dir.rglob("*.json")):
            if self._should_skip(path):
                continue
            try:
                raw = json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                raise RetrievalError(f"Invalid Dataset A JSON file: {path}") from exc
            if isinstance(raw, list):
                entries.extend(self._normalize(item, path) for item in raw if isinstance(item, dict))
            elif isinstance(raw, dict):
                entries.append(self._normalize(raw, path))
        self._cache[cache_key] = entries
        return [entry.model_copy(deep=True) for entry in entries]

    def get_entry(self, entry_id: str) -> KnowledgeEntry | None:
        """Return one knowledge entry by ID."""

        return next((entry for entry in self.load_entries() if entry.id == entry_id), None)

    def cache_stats(self) -> dict[str, int]:
        """Return Dataset A cache hit/miss counters."""

        return {"cache_hits": self._cache_hits, "cache_misses": self._cache_misses}

    def _should_skip(self, path: Path) -> bool:
        """Return whether a Dataset A JSON path should be skipped."""

        relative_parts = path.relative_to(self.dataset_dir).parts
        return (
            "schemas" in relative_parts
            or path.name == "index.json"
            or path.name.endswith(".example.json")
        )

    def _normalize(self, raw: dict[str, Any], path: Path) -> KnowledgeEntry:
        """Normalize one raw Dataset A object."""

        category = path.parent.name if path.parent != self.dataset_dir else "root"
        relationships = self._collect_relationships(raw)
        summary = str(raw.get("description") or raw.get("planning_use") or raw.get("summary") or "")
        metadata = dict(raw)
        return KnowledgeEntry(
            id=str(raw.get("id") or path.stem),
            title=str(raw.get("name") or raw.get("title") or path.stem),
            category=category,
            summary=summary,
            source_path=str(path.relative_to(self.dataset_dir)),
            tags=[str(tag) for tag in raw.get("tags", []) if tag],
            relationships=relationships,
            metadata=metadata,
        )

    def _collect_relationships(self, raw: dict[str, Any]) -> list[str]:
        """Collect related entity IDs from common knowledge graph fields."""

        relationship_fields = (
            "recommended_strategies",
            "compatible_conversation_styles",
            "recommended_prompt_mutations",
            "evaluation_rules",
            "related_families",
            "mitigations",
            "owasp_mappings",
            "mitre_mappings",
            "references",
            "recommended_attack_families",
            "recommended_evaluation_rules",
            "recommended_mitigations",
            "related_objectives",
            "conversation_styles",
            "prompt_mutations",
            "model_profiles",
        )
        relationships: list[str] = []
        for field in relationship_fields:
            value = raw.get(field, [])
            if isinstance(value, str):
                relationships.append(value)
            elif isinstance(value, list):
                relationships.extend(str(item) for item in value if item)
        attack_family = raw.get("attack_family")
        if attack_family:
            relationships.append(str(attack_family))
        return sorted(set(relationships))
