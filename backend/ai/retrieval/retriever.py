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
    """Dataset retriever with lightweight relevance ranking."""

    MAX_KNOWLEDGE_CONTEXT = 10
    MAX_ASSET_CONTEXT = 10

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
        max_results = min(limit or DEFAULT_RESULT_LIMIT, self.MAX_KNOWLEDGE_CONTEXT)
        return self._rank(entries, analysis, max_results)

    def retrieve_attack_assets(self, analysis: ObjectiveAnalysis, limit: int | None = None) -> list[AttackAsset]:
        """Retrieve Dataset B assets relevant to an objective analysis."""

        assets = self.dataset_b.load_assets()
        max_results = min(limit or DEFAULT_RESULT_LIMIT, self.MAX_ASSET_CONTEXT)
        return self._rank(assets, analysis, max_results)

    def cache_stats(self) -> dict[str, int]:
        """Return combined Dataset A and Dataset B cache counters."""

        stats = {"cache_hits": 0, "cache_misses": 0}
        for repository in (self.dataset_a, self.dataset_b):
            if hasattr(repository, "cache_stats"):
                repo_stats = repository.cache_stats()
                stats["cache_hits"] += int(repo_stats.get("cache_hits", 0))
                stats["cache_misses"] += int(repo_stats.get("cache_misses", 0))
        return stats

    def _rank(self, items: list, analysis: ObjectiveAnalysis, limit: int) -> list:
        """Rank retrievable items against objective analysis."""

        query_terms = self._analysis_terms(analysis)
        source_categories = [str(category) for category in analysis.metadata.get("source_categories", [])]
        preferred_categories = {category.replace("-", "_") for category in [*analysis.recommended_categories, *source_categories]}
        preferred_owasp = self._terms(" ".join(str(item) for item in analysis.metadata.get("owasp_mappings", [])))
        preferred_mitre = self._terms(" ".join(str(item) for item in analysis.metadata.get("mitre_mappings", [])))
        scored = []
        for item in items:
            text = self._item_text(item)
            item_terms = self._terms(text)
            semantic = self._jaccard(query_terms, item_terms)
            keyword_overlap = len(query_terms.intersection(item_terms))
            category = str(getattr(item, "category", "")).replace("-", "_")
            metadata = getattr(item, "metadata", {}) if isinstance(getattr(item, "metadata", {}), dict) else {}
            item_tags = self._terms(" ".join(getattr(item, "tags", [])))
            item_owasp = self._terms(" ".join([str(getattr(item, "owasp_llm_top_10", "")), str(metadata.get("owasp_mappings", ""))]))
            item_mitre = self._terms(" ".join([str(getattr(item, "mitre_atlas", "")), str(metadata.get("mitre_mappings", ""))]))
            relationships = {
                str(value).replace("af-", "").replace("-", "_").lower()
                for value in getattr(item, "relationships", [])
            }
            category_bonus = 1.0 if category in preferred_categories else 0.0
            family_bonus = 1.0 if preferred_categories.intersection(item_terms) else 0.0
            tag_overlap = len(item_tags.intersection(query_terms))
            owasp_overlap = len(preferred_owasp.intersection(item_owasp)) if preferred_owasp else len({"owasp", "llm"}.intersection(item_owasp.intersection(query_terms)))
            mitre_overlap = len(preferred_mitre.intersection(item_mitre)) if preferred_mitre else len({"atlas", "mitre"}.intersection(item_mitre.intersection(query_terms)))
            relationship_bonus = 1.0 if relationships.intersection(preferred_categories) else 0.0
            score = (
                semantic * 30
                + min(keyword_overlap, 12) * 2.0
                + category_bonus * 12
                + family_bonus * 8
                + min(tag_overlap, 8) * 2.5
                + min(owasp_overlap, 4) * 3
                + min(mitre_overlap, 4) * 3
                + relationship_bonus * 6
            )
            if score > 0:
                self._annotate_retrieval_score(
                    item,
                    score=score,
                    reasons={
                        "semantic_similarity": round(semantic, 3),
                        "objective_keyword_overlap": keyword_overlap,
                        "attack_family_match": bool(category_bonus or family_bonus),
                        "owasp_overlap": owasp_overlap,
                        "mitre_overlap": mitre_overlap,
                        "tag_overlap": tag_overlap,
                        "relationship_proximity": bool(relationship_bonus),
                    },
                )
                scored.append((score, item))
        scored.sort(key=lambda pair: (pair[0], getattr(pair[1], "id", "")), reverse=True)
        return [item for _, item in scored[:limit]]

    def _analysis_terms(self, analysis: ObjectiveAnalysis) -> set[str]:
        """Return weighted query terms from objective analysis."""

        text = " ".join(
            [
                analysis.objective,
                analysis.normalized_objective,
                " ".join(analysis.risk_themes),
                " ".join(analysis.recommended_categories),
                " ".join(str(category) for category in analysis.metadata.get("source_categories", [])),
                " ".join(analysis.target_capabilities),
                " ".join(str(value) for value in analysis.metadata.values() if isinstance(value, str)),
            ]
        )
        terms = self._terms(text)
        for category in analysis.recommended_categories:
            terms.update(self._terms(category))
        return terms

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

    def _annotate_retrieval_score(self, item: object, *, score: float, reasons: dict[str, object]) -> None:
        """Attach retrieval score metadata to a Pydantic item in place."""

        metadata = getattr(item, "metadata", None)
        if isinstance(metadata, dict):
            metadata["retrieval_score"] = round(score, 3)
            metadata["retrieval_reasons"] = reasons

    def _jaccard(self, left: set[str], right: set[str]) -> float:
        """Return lexical semantic similarity approximation."""

        if not left or not right:
            return 0.0
        return len(left.intersection(right)) / len(left.union(right))

    def _terms(self, text: str) -> set[str]:
        """Tokenize text for lightweight lexical retrieval."""

        return {
            token
            for token in re.findall(r"[a-zA-Z0-9_]+", text.lower().replace("-", "_"))
            if len(token) >= 3
        }
