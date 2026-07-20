"""Typed results and configuration for planner-driven attack execution."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, model_validator

from backend.ai.providers.provider_interface import ProviderMessage


class ExecutionStatus(str, Enum):
    """High-level outcome of a planner-driven execution."""

    COMPLETED = "completed"
    PARTIAL = "partial"
    FAILED = "failed"
    INTERRUPTED = "interrupted"


class TurnStatus(str, Enum):
    """Outcome of one target interaction."""

    SUCCESS = "success"
    ERROR = "error"
    INTERRUPTED = "interrupted"


class ExecutionErrorCode(str, Enum):
    """Stable error categories consumed by evaluation and reporting."""

    INVALID_PLANNER_RESULT = "invalid_planner_result"
    TIMEOUT = "timeout"
    RATE_LIMIT = "rate_limit"
    PROVIDER_UNAVAILABLE = "provider_unavailable"
    CONNECTION_FAILURE = "connection_failure"
    MALFORMED_RESPONSE = "malformed_response"
    EMPTY_RESPONSE = "empty_response"
    PROVIDER_FAILURE = "provider_failure"
    INTERRUPTED = "interrupted"


class ExecutionError(BaseModel):
    """Structured error raised while validating or executing one turn."""

    model_config = ConfigDict(extra="forbid")

    code: ExecutionErrorCode
    message: str
    turn_number: int | None = None
    attempt: int | None = None
    retryable: bool = False
    exception_type: str = ""
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = Field(default_factory=dict)


class ExecutionTurn(BaseModel):
    """Complete audit record for one prompt/response interaction."""

    model_config = ConfigDict(extra="forbid")

    turn_number: int
    prompt: str
    response: str
    provider: str
    model: str
    latency_ms: float = Field(ge=0.0)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    status: TurnStatus
    metadata: dict[str, Any] = Field(default_factory=dict)


class ExecutionMetrics(BaseModel):
    """Aggregated runtime measurements for an execution."""

    model_config = ConfigDict(extra="forbid")

    planned_turns: int = 0
    attempted_turns: int = 0
    successful_turns: int = 0
    failed_turns: int = 0
    provider_calls: int = 0
    retry_count: int = 0
    average_latency_ms: float = 0.0
    minimum_latency_ms: float = 0.0
    maximum_latency_ms: float = 0.0
    token_usage: dict[str, int] = Field(default_factory=dict)
    started_at: datetime
    ended_at: datetime


class ExecutionConfig(BaseModel):
    """Runtime controls that do not alter planner decisions or prompt content."""

    model_config = ConfigDict(extra="forbid")

    max_turns: int | None = Field(default=None, ge=1)
    max_retries: int = Field(default=2, ge=0)
    timeout_seconds: float = Field(default=60.0, gt=0.0)
    retry_base_delay_seconds: float = Field(default=0.5, ge=0.0)
    retry_max_delay_seconds: float = Field(default=8.0, ge=0.0)
    continue_on_error: bool = True
    conversation_mode: str | None = Field(default=None, pattern="^(single_turn|multi_turn)$")
    model: str | None = None
    initial_messages: list[ProviderMessage] = Field(default_factory=list)
    request_metadata: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_retry_delays(self) -> "ExecutionConfig":
        """Ensure exponential backoff has a coherent upper bound."""

        if self.retry_max_delay_seconds < self.retry_base_delay_seconds:
            raise ValueError("retry_max_delay_seconds must be greater than or equal to retry_base_delay_seconds")
        return self


class ExecutionResult(BaseModel):
    """Provider-neutral output consumed directly by future evaluators."""

    model_config = ConfigDict(extra="forbid")

    execution_id: str = Field(default_factory=lambda: str(uuid4()))
    planner_id: str
    objective: str
    provider: str
    model: str
    execution_status: ExecutionStatus
    conversation_history: list[ExecutionTurn] = Field(default_factory=list)
    responses: list[str] = Field(default_factory=list)
    execution_metrics: ExecutionMetrics
    total_latency: float = Field(ge=0.0, description="Total wall-clock execution latency in milliseconds.")
    total_turns: int = Field(ge=0)
    errors: list[ExecutionError] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
