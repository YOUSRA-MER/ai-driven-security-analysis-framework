"""Enumerations shared by the AI planning subsystem."""

from __future__ import annotations

from enum import Enum


class PlanningStage(str, Enum):
    """Lifecycle stages for an AI planning request."""

    CREATED = "created"
    ANALYZING_OBJECTIVE = "analyzing_objective"
    RETRIEVING_KNOWLEDGE = "retrieving_knowledge"
    SELECTING_ATTACKS = "selecting_attacks"
    SELECTING_STRATEGIES = "selecting_strategies"
    BUILDING_PLAN = "building_plan"
    OPTIMIZING_PLAN = "optimizing_plan"
    COMPLETED = "completed"
    FAILED = "failed"


class ConfidenceLevel(str, Enum):
    """Human-readable confidence bands for planning decisions."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    UNKNOWN = "unknown"


class DatasetKind(str, Enum):
    """Supported AI retrieval dataset groups."""

    KNOWLEDGE = "knowledge_dataset"
    ATTACK = "attack_dataset"


class StrategyMode(str, Enum):
    """Abstract execution style for a selected strategy."""

    SINGLE_TURN = "single_turn"
    MULTI_TURN = "multi_turn"
    RETRIEVAL_AUGMENTED = "retrieval_augmented"
    TOOL_AWARE = "tool_aware"
    UNKNOWN = "unknown"


class ProviderRole(str, Enum):
    """Message roles understood by provider adapters."""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"

