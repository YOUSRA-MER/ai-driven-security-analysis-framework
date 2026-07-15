"""Application settings loaded from environment variables."""

from __future__ import annotations

import os
from functools import lru_cache

from dotenv import load_dotenv
from pydantic import BaseModel, ConfigDict, Field


load_dotenv()


class Settings(BaseModel):
    """Runtime settings for the AI security analysis framework.

    Attributes:
        llm_provider: Active provider selected by `LLM_PROVIDER`.
        nvidia_api_key: NVIDIA NIM API key loaded from `NVIDIA_API_KEY`.
        nvidia_model: NVIDIA NIM model identifier.
        nvidia_base_url: OpenAI-compatible NVIDIA NIM base URL.
        openrouter_api_key: OpenRouter API key loaded from `OPENROUTER_API_KEY`.
        openrouter_model: OpenRouter model identifier.
        openrouter_base_url: OpenAI-compatible OpenRouter base URL.
        openrouter_timeout_seconds: HTTP timeout for OpenRouter requests.
        openrouter_max_retries: Number of retry attempts for transient provider errors.
        app_name: Human-readable app name used for logging and OpenRouter headers.
    """

    model_config = ConfigDict(extra="forbid")

    llm_provider: str = "nvidia"
    nvidia_api_key: str | None = None
    nvidia_model: str = "nvidia/nemotron-3-ultra-550b-a55b"
    nvidia_base_url: str = "https://integrate.api.nvidia.com/v1"
    nvidia_timeout_seconds: float = Field(default=60.0, gt=0)
    nvidia_max_retries: int = Field(default=2, ge=1)
    openrouter_api_key: str | None = None
    openrouter_model: str = "qwen/qwen3-235b-a22b:free"
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    openrouter_timeout_seconds: float = Field(default=60.0, gt=0)
    openrouter_max_retries: int = Field(default=3, ge=1)
    app_name: str = "AI-Driven Security Analysis Framework"

    @property
    def openrouter_configured(self) -> bool:
        """Return whether the OpenRouter API key is configured."""

        return bool(self.openrouter_api_key)

    @property
    def nvidia_configured(self) -> bool:
        """Return whether the NVIDIA API key is configured."""

        return bool(self.nvidia_api_key)


@lru_cache
def get_settings() -> Settings:
    """Load application settings from the current environment.

    Returns:
        Settings object populated from environment variables.
    """

    return Settings(
        llm_provider=os.getenv("LLM_PROVIDER", "nvidia").strip().lower(),
        nvidia_api_key=os.getenv("NVIDIA_API_KEY"),
        nvidia_model=os.getenv("NVIDIA_MODEL", "nvidia/nemotron-3-ultra-550b-a55b"),
        nvidia_base_url=os.getenv("NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1").rstrip("/"),
        nvidia_timeout_seconds=float(os.getenv("NVIDIA_TIMEOUT_SECONDS", "60")),
        nvidia_max_retries=int(os.getenv("NVIDIA_MAX_RETRIES", "2")),
        openrouter_api_key=os.getenv("OPENROUTER_API_KEY"),
        openrouter_model=os.getenv("OPENROUTER_MODEL", "qwen/qwen3-235b-a22b:free"),
        openrouter_base_url=os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1").rstrip("/"),
        openrouter_timeout_seconds=float(os.getenv("OPENROUTER_TIMEOUT_SECONDS", "60")),
        openrouter_max_retries=int(os.getenv("OPENROUTER_MAX_RETRIES", "3")),
        app_name=os.getenv("OPENROUTER_APP_NAME", "AI-Driven Security Analysis Framework"),
    )
