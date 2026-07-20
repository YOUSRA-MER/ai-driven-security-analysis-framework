"""Ollama target adapter."""

from __future__ import annotations

import asyncio
import json
import urllib.request
from typing import Sequence

from backend.models.conversation import Message
from backend.targets.base_target import TargetAdapter


class OllamaTarget(TargetAdapter):
    """Sends chat prompts to a local Ollama server."""

    def __init__(
        self,
        model: str,
        base_url: str = "http://localhost:11434",
        name: str | None = None,
        options: dict[str, object] | None = None,
        timeout_seconds: float = 120.0,
    ) -> None:
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.name = name or f"ollama:{model}"
        self.options = options or {}
        self.timeout_seconds = timeout_seconds

    async def send(self, messages: Sequence[Message]) -> Message:
        return await asyncio.to_thread(self._chat, messages)

    def _chat(self, messages: Sequence[Message]) -> Message:
        payload = {
            "model": self.model,
            "stream": False,
            "messages": [{"role": message.role, "content": message.content} for message in messages],
            "options": self.options,
        }
        request = urllib.request.Request(
            f"{self.base_url}/api/chat",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
            body = json.loads(response.read().decode("utf-8"))
        content = body.get("message", {}).get("content", "")
        usage = {
            "prompt_tokens": int(body.get("prompt_eval_count", 0) or 0),
            "completion_tokens": int(body.get("eval_count", 0) or 0),
        }
        usage["total_tokens"] = usage["prompt_tokens"] + usage["completion_tokens"]
        return Message(
            role="assistant",
            content=content,
            metadata={
                "target": self.name,
                "usage": usage,
                "total_duration_ns": int(body.get("total_duration", 0) or 0),
            },
        )
