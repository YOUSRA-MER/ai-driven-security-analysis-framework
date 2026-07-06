"""Generic REST API target adapter."""

from __future__ import annotations

import asyncio
import json
import urllib.request
from typing import Any, Sequence

from backend.models.conversation import Message
from backend.targets.base_target import TargetAdapter


class RestApiTarget(TargetAdapter):
    """Sends prompts to an HTTP JSON endpoint."""

    def __init__(
        self,
        name: str,
        endpoint: str,
        prompt_field: str = "prompt",
        response_field: str = "response",
        headers: dict[str, str] | None = None,
        extra_payload: dict[str, Any] | None = None,
    ) -> None:
        self.name = name
        self.endpoint = endpoint
        self.prompt_field = prompt_field
        self.response_field = response_field
        self.headers = headers or {}
        self.extra_payload = extra_payload or {}

    async def send(self, messages: Sequence[Message]) -> Message:
        prompt = messages[-1].content
        return await asyncio.to_thread(self._post, prompt)

    def _post(self, prompt: str) -> Message:
        payload = {**self.extra_payload, self.prompt_field: prompt}
        request = urllib.request.Request(
            self.endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json", **self.headers},
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=60) as response:
            body = json.loads(response.read().decode("utf-8"))
        content = self._extract_response(body)
        return Message(role="assistant", content=content, metadata={"target": self.name})

    def _extract_response(self, body: Any) -> str:
        if isinstance(body, dict):
            value = body
            for part in self.response_field.split("."):
                value = value.get(part, "")
                if not isinstance(value, dict):
                    break
            return str(value)
        return str(body)

