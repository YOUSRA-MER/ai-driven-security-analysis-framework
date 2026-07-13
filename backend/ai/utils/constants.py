"""Constants for the AI planning subsystem."""

from __future__ import annotations

from pathlib import Path


AI_PACKAGE_ROOT = Path(__file__).resolve().parents[1]
"""Root path of the `backend.ai` package."""

DATASETS_ROOT = Path(__file__).resolve().parents[2] / "attacks" / "datasets"
"""Root path containing attack and knowledge datasets."""

KNOWLEDGE_DATASET_DIR = DATASETS_ROOT / "knowledge_dataset"
"""Default Dataset A location used for planning knowledge."""

ATTACK_DATASET_DIR = DATASETS_ROOT / "Attack_dataset"
"""Default Dataset B location used for attack assets."""

DEFAULT_RESULT_LIMIT = 20
"""Default upper bound for retrieval results returned by interface methods."""

MIN_CONFIDENCE = 0.0
"""Minimum normalized confidence value."""

MAX_CONFIDENCE = 1.0
"""Maximum normalized confidence value."""

