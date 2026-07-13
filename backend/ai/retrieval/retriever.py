"""Retrieval interface for planning context assembly."""

from __future__ import annotations

import re
from abc import ABC, abstractmethod

from backend.ai.models.attack_asset import AttackAsset
from backend.ai.models.knowledge_entry import KnowledgeEntry
from backend.ai.models.objective_analysis import ObjectiveAnalysis
from backend.ai.retrieval.dataset_a import DatasetARepository, FileDatasetARepository
from backend.ai.retrieval.dataset_b import DatasetBRepository, FileDatasetBRepository
from backend.ai.utils.constants import DEFAULT_RESULT_LIMIT


class AIRetriever(ABC):
    """Retrieves planning knowledge and attack assets for a normalized objective."""

    @abstractmethod
    def retrieve_knowledge(self, analysis: ObjectiveAnalysis, limit: int | None = None) -> list[KnowledgeEntry]:
        """Retrieve Dataset A entries relevant to an objective analysis.

        Args:
            analysis: Structured objective analysis.
            limit: Optional maximum number of entries to return.

        Returns:
            Relevant knowledge entries.
        """

        raise NotImplementedError

    @abstractmethod
    def retrieve_attack_assets(self, analysis: ObjectiveAnalysis, limit: int | None = None) -> list[AttackAsset]:
        """Retrieve Dataset B assets relevant to an objective analysis.

        Args:
            analysis: Structured objective analysis.
            limit: Optional maximum number of assets to return.

        Returns:
            Relevant attack assets.
        """

        raise NotImplementedError


class DatasetRetriever(AIRetriever):
    """Placeholder retriever that will coordinate Dataset A and Dataset B search."""

    def __init__(
        self,
        dataset_a: DatasetARepository | None = None,
        dataset_b: DatasetBRepository | None = None,
    ) -> None:
        """Initialize the retriever.

        Args:
            dataset_a: Optional Dataset A repository.
            dataset_b: Optional Dataset B repository.
        """

        self.dataset_a = dataset_a or FileDatasetARepository()
        self.dataset_b = dataset_b or FileDatasetBRepository()

    def retrieve_knowledge(self, analysis: ObjectiveAnalysis, limit: int | None = None) -> list[KnowledgeEntry]:
        """Retrieve Dataset A entries relevant to an objective analysis."""

        entries = self.dataset_a.load_entries()
        return self._rank(entries, analysis, limit or DEFAULT_RESULT_LIMIT)

    def retrieve_attack_assets(self, analysis: ObjectiveAnalysis, limit: int | None = None) -> list[AttackAsset]:
        """Retrieve Dataset B assets relevant to an objective analysis."""

        assets = self.dataset_b.load_assets()
        ranked = self._rank(assets, analysis, limit or DEFAULT_RESULT_LIMIT)
        preferred_categories = set(analysis.recommended_categories)
        if preferred_categories:
            category_matches = [asset for asset in assets if asset.category in preferred_categories]
            ranked_ids = {asset.id for asset in ranked}
            ranked.extend(asset for asset in category_matches if asset.id not in ranked_ids)
        max_results = limit or DEFAULT_RESULT_LIMIT
        return ranked[:max_results]

    def _rank(self, items: list, analysis: ObjectiveAnalysis, limit: int) -> list:
        """Rank retrievable items against objective analysis."""

        query_terms = self._terms(
            " ".join(
                [
                    analysis.objective,
                    analysis.normalized_objective,
                    " ".join(analysis.risk_themes),
                    " ".join(analysis.recommended_categories),
                    " ".join(analysis.target_capabilities),
                ]
            )
        )
        scored = []
        for item in items:
            text = self._item_text(item)
            item_terms = self._terms(text)
            overlap = len(query_terms.intersection(item_terms))
            category_bonus = 4 if getattr(item, "category", "") in analysis.recommended_categories else 0
            tag_bonus = len(set(getattr(item, "tags", [])).intersection(query_terms))
            score = overlap + category_bonus + tag_bonus
            if score > 0:
                scored.append((score, item))
        scored.sort(key=lambda pair: pair[0], reverse=True)
        return [item for _, item in scored[:limit]]

    def _item_text(self, item: object) -> str:
        """Return searchable text for a knowledge entry or attack asset."""

        fields = [
            getattr(item, "id", ""),
            getattr(item, "title", ""),
            getattr(item, "name", ""),
            getattr(item, "category", ""),
            getattr(item, "summary", ""),
            getattr(item, "description", ""),
            " ".join(getattr(item, "tags", [])),
        ]
        metadata = getattr(item, "metadata", {})
        if isinstance(metadata, dict):
            fields.append(" ".join(str(value) for value in metadata.values() if isinstance(value, (str, int, float))))
        return " ".join(fields)

    def _terms(self, text: str) -> set[str]:
        """Tokenize text for lightweight lexical retrieval."""

        return {
            token
            for token in re.findall(r"[a-zA-Z0-9_]+", text.lower().replace("-", "_"))
            if len(token) >= 3
        }
