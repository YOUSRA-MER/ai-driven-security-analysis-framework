"""Dataset B access interface for attack assets."""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from backend.ai.models.attack_asset import AttackAsset
from backend.ai.utils.constants import ATTACK_DATASET_DIR
from backend.ai.utils.exceptions import RetrievalError


class DatasetBRepository(ABC):
    """Abstract repository for the attack asset dataset.

    Dataset B stores concrete public red-team prompts, payload templates, source
    references, taxonomy mappings, and metadata. It is used for selection only in
    this layer; execution is intentionally outside this subsystem.
    """

    def __init__(self, dataset_dir: Path = ATTACK_DATASET_DIR) -> None:
        """Initialize the repository.

        Args:
            dataset_dir: Filesystem path for Dataset B.
        """

        self.dataset_dir = dataset_dir

    @abstractmethod
    def load_assets(self) -> list[AttackAsset]:
        """Load all normalized attack assets.

        Returns:
            A list of normalized attack assets.
        """

        raise NotImplementedError

    @abstractmethod
    def get_asset(self, asset_id: str) -> AttackAsset | None:
        """Return one attack asset by ID.

        Args:
            asset_id: Stable attack asset identifier.

        Returns:
            The matching asset, or `None` if not found.
        """

        raise NotImplementedError


class FileDatasetBRepository(DatasetBRepository):
    """Filesystem-backed Dataset B repository placeholder."""

    def load_assets(self) -> list[AttackAsset]:
        """Load all normalized attack assets from disk.

        Returns:
            Normalized attack assets from `Attack_dataset`.

        Raises:
            RetrievalError: If the dataset directory does not exist or a JSON
                file cannot be parsed.
        """

        if not self.dataset_dir.exists():
            raise RetrievalError(f"Dataset B directory does not exist: {self.dataset_dir}")

        assets: list[AttackAsset] = []
        for path in sorted(self.dataset_dir.glob("*.json")):
            if path.name == "source_catalog.json":
                continue
            try:
                raw = json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                raise RetrievalError(f"Invalid Dataset B JSON file: {path}") from exc
            if not isinstance(raw, list):
                continue
            assets.extend(self._normalize(item, path) for item in raw if isinstance(item, dict))
        return assets

    def get_asset(self, asset_id: str) -> AttackAsset | None:
        """Return one attack asset by ID."""

        return next((asset for asset in self.load_assets() if asset.id == asset_id), None)

    def _normalize(self, raw: dict[str, Any], path: Path) -> AttackAsset:
        """Normalize one raw Dataset B object."""

        metadata = dict(raw.get("metadata", {}))
        metadata["source_path"] = str(path.relative_to(self.dataset_dir))
        return AttackAsset(
            id=str(raw["id"]),
            name=str(raw.get("name") or raw["id"]),
            category=str(raw.get("category") or path.stem),
            attack_prompt=str(raw.get("attack_prompt") or ""),
            severity=str(raw.get("severity") or "unknown"),
            owasp_llm_top_10=str(raw.get("owasp_llm_top_10") or ""),
            mitre_atlas=str(raw.get("mitre_atlas") or ""),
            description=str(raw.get("description") or ""),
            expected_behavior=str(raw.get("expected_behavior") or ""),
            success_criteria=str(raw.get("success_criteria") or ""),
            tags=[str(tag) for tag in raw.get("tags", []) if tag],
            original_source=str(raw.get("original_source") or ""),
            reference_url=str(raw.get("reference_url") or ""),
            metadata=metadata,
        )
