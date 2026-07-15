"""Prompt builder for attack-family selection reasoning."""

from __future__ import annotations

from typing import Any

from backend.ai.reasoning.prompt_templates import build_reasoning_prompt


class AttackFamilyPromptBuilder:
    """Builds prompts for `AttackFamilyAssessment` generation."""

    def build(self, *, payload: dict[str, Any], schema: dict[str, Any]) -> str:
        """Return the complete prompt for attack-family selection.

        Args:
            payload: Normalized objective, Dataset A knowledge, and candidate
                attack family context.
            schema: JSON schema for `AttackFamilyAssessment`.

        Returns:
            Complete prompt sent to Qwen.
        """

        return build_reasoning_prompt(
            task_name="Select the most relevant attack family for a non-executable security plan.",
            output_model="AttackFamilyAssessment",
            responsibilities=[
                "Compare candidate attack families against the normalized objective.",
                "For every candidate, evaluate applicability, strengths, weaknesses, expected success, and required conditions internally.",
                "Use Dataset A knowledge as the primary source of truth.",
                "Consider OWASP LLM Top 10 and MITRE ATLAS mappings when they clarify relevance.",
                "Prefer family IDs present in the retrieved knowledge or supplied candidates.",
                "Justify the selected family IDs in concise analyst language.",
                "Estimate confidence from evidence strength and source alignment.",
            ],
            additional_guidance=[
                "Do not invent attack family IDs.",
                "Return one or more family IDs only when supported by the payload.",
                "Do not generate or mutate attack prompts.",
            ],
            schema=schema,
            payload=payload,
        )
