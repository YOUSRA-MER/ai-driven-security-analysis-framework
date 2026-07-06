"""Prompt normalization pipeline."""

from __future__ import annotations

from collections.abc import Iterable

from backend.prompt.converters import PromptConverter


class PromptNormalizer:
    """Applies prompt converters and strips unsafe transport artifacts."""

    def __init__(self, converters: Iterable[PromptConverter] | None = None) -> None:
        self.converters = list(converters or [])

    def normalize(self, text: str) -> str:
        normalized = text.replace("\r\n", "\n").strip()
        for converter in self.converters:
            normalized = converter.convert(normalized)
        return normalized

