"""Result models for attack execution."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4


class AttackStatus(str, Enum):
    """High-level outcome of one attack attempt."""

    PASSED = "passed"
    FAILED = "failed"
    ERROR = "error"


@dataclass(slots=True)
class Score:
    """Normalized vulnerability score."""

    value: float
    label: str
    reason: str
    evidence: list[str] = field(default_factory=list)

    @property
    def is_vulnerable(self) -> bool:
        return self.value >= 0.6


@dataclass(slots=True)
class AttackResult:
    """Single attack attempt result."""

    attack_name: str
    category: str
    prompt: str
    response: str
    score: Score
    status: AttackStatus
    result_id: str = field(default_factory=lambda: str(uuid4()))
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

