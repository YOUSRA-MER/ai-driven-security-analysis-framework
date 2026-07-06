"""Target configuration models."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class TargetKind(str, Enum):
    """Supported target families."""

    OLLAMA = "ollama"
    OPENAI = "openai"
    GEMINI = "gemini"
    CLAUDE = "claude"
    REST_API = "rest_api"


@dataclass(slots=True)
class TargetConfig:
    """Configuration for a target adapter."""

    kind: TargetKind
    name: str
    model: str | None = None
    base_url: str | None = None
    api_key: str | None = None
    headers: dict[str, str] = field(default_factory=dict)
    options: dict[str, Any] = field(default_factory=dict)

