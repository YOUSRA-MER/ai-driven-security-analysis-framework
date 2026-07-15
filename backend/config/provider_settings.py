"""Runtime settings for interchangeable reasoning providers."""
from __future__ import annotations
import os
from pydantic import BaseModel, ConfigDict, Field

class OpenRouterSettings(BaseModel):
    model_config = ConfigDict(extra="forbid")
    api_key: str | None = None
    base_url: str = "https://openrouter.ai/api/v1"
    model: str = "qwen/qwen3-235b-a22b:free"
    timeout_seconds: float = Field(default=30.0, gt=0)
    site_url: str | None = None
    app_name: str = "AI-Driven Security Analysis Framework"

    @classmethod
    def from_environment(cls) -> "OpenRouterSettings":
        return cls(api_key=os.getenv("OPENROUTER_API_KEY"), base_url=os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1").rstrip("/"), model=os.getenv("OPENROUTER_MODEL", cls.model_fields["model"].default), timeout_seconds=float(os.getenv("OPENROUTER_TIMEOUT_SECONDS", "30")), site_url=os.getenv("OPENROUTER_SITE_URL"), app_name=os.getenv("OPENROUTER_APP_NAME", cls.model_fields["app_name"].default))
