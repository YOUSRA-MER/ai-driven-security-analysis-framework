"""Structured models used by the adaptive prompt-generation pipeline."""
from __future__ import annotations
from typing import Any
from pydantic import BaseModel, ConfigDict, Field
from backend.ai.models.prompt_validation import PromptValidationResult

class Prompt(BaseModel):
    """A candidate prompt produced for an authorized security assessment."""
    model_config = ConfigDict(extra="forbid")
    id: str
    content: str
    objective: str
    strategy_id: str = ""
    attack_family: str = ""
    asset_ids: list[str] = Field(default_factory=list)
    turn: int = 1
    metadata: dict[str, Any] = Field(default_factory=dict)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)

class PromptQualityEstimate(BaseModel):
    """Internal generation confidence, not a target-response score."""
    model_config = ConfigDict(extra="forbid")
    strategy_consistency: float = Field(ge=0.0, le=1.0)
    objective_alignment: float = Field(ge=0.0, le=1.0)
    expected_effectiveness: float = Field(ge=0.0, le=1.0)
    estimated_stealth: float = Field(ge=0.0, le=1.0)
    mutation_diversity: float = Field(ge=0.0, le=1.0)
    confidence: float = Field(ge=0.0, le=1.0)
    rationale: str = ""

class PromptMutationRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")
    prompt_id: str
    mutation: str
    source_prompt_id: str
    details: str = ""

class PromptGenerationResult(BaseModel):
    """Result of planning, adapting, validating, and selecting prompts."""
    model_config = ConfigDict(extra="forbid")
    prompts: list[Prompt] = Field(default_factory=list)
    selected_prompt: Prompt | None = None
    reasoning_summary: str = ""
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    mutation_history: list[PromptMutationRecord] = Field(default_factory=list)
    validator_results: dict[str, PromptValidationResult] = Field(default_factory=dict)
    quality_estimates: dict[str, PromptQualityEstimate] = Field(default_factory=dict)
