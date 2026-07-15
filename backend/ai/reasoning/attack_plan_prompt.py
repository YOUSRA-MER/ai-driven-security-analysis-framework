"""Prompt builder for non-executable attack-plan reasoning."""

from __future__ import annotations

from typing import Any

from backend.ai.reasoning.prompt_templates import build_reasoning_prompt


class AttackPlanPromptBuilder:
    """Builds prompts for `PlanDirective` generation."""

    def build(self, *, payload: dict[str, Any], schema: dict[str, Any]) -> str:
        """Return the complete prompt for attack-plan directive creation.

        Args:
            payload: Objective, selected family/strategy context, hypotheses,
                and Dataset B asset IDs.
            schema: JSON schema for `PlanDirective`.

        Returns:
            Complete prompt sent to Qwen.
        """

        return build_reasoning_prompt(
            task_name="Construct a bounded non-executable attack plan directive.",
            output_model="PlanDirective",
            responsibilities=[
                "Use the objective, selected family, selected strategy, and Dataset B assets to choose plan inputs.",
                "Select strategy IDs and asset IDs from the supplied payload only.",
                "Explain why the selected directive is appropriate for defensive testing.",
                "Keep the plan at the directive level; downstream components build the concrete AttackPlan object.",
                "Preserve constraints and avoid instructions that imply execution against a target.",
            ],
            additional_guidance=[
                "Do not invent asset IDs or strategy IDs.",
                "Do not include generated prompts in this directive.",
                "Do not call tools, targets, browsers, APIs, or model endpoints.",
            ],
            schema=schema,
            payload=payload,
        )
