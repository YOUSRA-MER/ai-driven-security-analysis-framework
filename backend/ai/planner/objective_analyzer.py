"""Objective analyzer interface."""

from __future__ import annotations

import re
from abc import ABC, abstractmethod

from backend.ai.models.objective_analysis import ObjectiveAnalysis
from backend.ai.models.planner_context import PlannerContext
from backend.ai.utils.enums import ConfidenceLevel


CATEGORY_SIGNALS: dict[str, tuple[str, ...]] = {
    "prompt_injection": ("prompt injection", "instruction override", "ignore instructions", "system override"),
    "jailbreak": ("jailbreak", "bypass", "refusal", "safety", "policy bypass"),
    "prompt_leakage": ("prompt leak", "system prompt", "developer message", "hidden instruction", "prompt disclosure"),
    "indirect_prompt_injection": ("indirect", "email", "web page", "retrieved content", "tool output", "document"),
    "rag_poisoning": ("rag", "retrieval", "poison", "poisoning", "citation", "vector"),
    "roleplay": ("roleplay", "persona", "fiction", "character", "dan"),
    "encoding": ("encoding", "base64", "unicode", "obfuscation", "cipher", "encoded"),
    "multilingual": ("multilingual", "translation", "language", "cross-lingual", "low-resource"),
    "context_overflow": ("long context", "many-shot", "overflow", "context window", "multi-turn"),
    "data_exfiltration": ("exfiltration", "secret", "token", "credential", "pii", "privacy", "data leak"),
    "tool_abuse": ("tool", "agent", "function", "side effect", "email", "calendar", "browser"),
}


class ObjectiveAnalyzer(ABC):
    """Analyzes a raw user objective into structured planning signals."""

    @abstractmethod
    def analyze(self, context: PlannerContext) -> ObjectiveAnalysis:
        """Analyze the objective stored in a planner context.

        Args:
            context: Planner context containing the raw objective.

        Returns:
            Structured objective analysis.
        """

        raise NotImplementedError


class DefaultObjectiveAnalyzer(ObjectiveAnalyzer):
    """Placeholder objective analyzer for future deterministic and AI analysis."""

    def analyze(self, context: PlannerContext) -> ObjectiveAnalysis:
        """Analyze the objective stored in a planner context."""

        normalized = self._normalize(context.objective)
        matched_categories = self._match_categories(normalized)
        risk_themes = self._extract_risk_themes(normalized, matched_categories)
        capabilities = self._extract_capabilities(normalized)
        confidence = self._confidence(matched_categories, risk_themes)
        return ObjectiveAnalysis(
            objective=context.objective,
            normalized_objective=normalized,
            target_capabilities=capabilities,
            risk_themes=risk_themes,
            recommended_categories=matched_categories,
            constraints=list(context.constraints),
            confidence=confidence,
            confidence_level=self._confidence_level(confidence),
            metadata={
                "analyzer": self.__class__.__name__,
                "matched_signal_count": sum(
                    1
                    for category in matched_categories
                    for signal in CATEGORY_SIGNALS.get(category, ())
                    if signal in normalized
                ),
            },
        )

    def _normalize(self, objective: str) -> str:
        """Normalize objective text for deterministic analysis."""

        return re.sub(r"\s+", " ", objective.strip().lower())

    def _match_categories(self, normalized: str) -> list[str]:
        """Return categories whose signals appear in the objective."""

        matches = []
        for category, signals in CATEGORY_SIGNALS.items():
            if any(signal in normalized for signal in signals):
                matches.append(category)
        if not matches:
            matches.append("prompt_injection")
        return matches

    def _extract_risk_themes(self, normalized: str, categories: list[str]) -> list[str]:
        """Extract high-level risk themes from objective text."""

        themes = set(categories)
        for word in ("secrets", "credentials", "privacy", "policy", "retrieval", "tools", "agents", "multiturn"):
            if word in normalized:
                themes.add(word)
        return sorted(themes)

    def _extract_capabilities(self, normalized: str) -> list[str]:
        """Infer target capabilities mentioned by the user."""

        capabilities = []
        checks = {
            "retrieval": ("rag", "retrieval", "knowledge base", "vector"),
            "tool_use": ("tool", "function", "agent", "browser", "email", "calendar"),
            "multi_turn": ("multi-turn", "many-shot", "conversation", "turn"),
            "multilingual": ("multilingual", "translation", "language"),
            "sensitive_data": ("secret", "pii", "credential", "token", "privacy"),
        }
        for capability, signals in checks.items():
            if any(signal in normalized for signal in signals):
                capabilities.append(capability)
        return capabilities

    def _confidence(self, categories: list[str], risk_themes: list[str]) -> float:
        """Compute a deterministic confidence score for the objective analysis."""

        score = 0.45 + min(0.35, 0.08 * len(categories)) + min(0.2, 0.03 * len(risk_themes))
        return min(1.0, round(score, 3))

    def _confidence_level(self, confidence: float) -> ConfidenceLevel:
        """Convert numeric confidence into a confidence band."""

        if confidence >= 0.75:
            return ConfidenceLevel.HIGH
        if confidence >= 0.5:
            return ConfidenceLevel.MEDIUM
        return ConfidenceLevel.LOW
