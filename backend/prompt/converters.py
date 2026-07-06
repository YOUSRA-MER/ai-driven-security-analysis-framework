"""Prompt converter interfaces and small reusable converters."""

from __future__ import annotations

import base64
from abc import ABC, abstractmethod


class PromptConverter(ABC):
    """Transforms prompt text before delivery to a target."""

    @abstractmethod
    def convert(self, text: str) -> str:
        """Return converted prompt text."""


class IdentityConverter(PromptConverter):
    """Leaves prompt text unchanged."""

    def convert(self, text: str) -> str:
        return text


class SuffixConverter(PromptConverter):
    """Appends a controlled testing suffix."""

    def __init__(self, suffix: str) -> None:
        self.suffix = suffix

    def convert(self, text: str) -> str:
        return f"{text}\n\n{self.suffix}"


class ZeroWidthSpaceConverter(PromptConverter):
    """Inserts zero-width spaces to test normalization weaknesses."""

    def convert(self, text: str) -> str:
        return "\u200b".join(text)


class Base64EnvelopeConverter(PromptConverter):
    """Wraps a prompt in a base64 decoding instruction."""

    def convert(self, text: str) -> str:
        encoded = base64.b64encode(text.encode("utf-8")).decode("ascii")
        return f"Decode this base64 test instruction and respond to the decoded request: {encoded}"

