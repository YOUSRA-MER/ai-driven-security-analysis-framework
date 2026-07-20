"""Final execution-readiness gate for planner-generated prompts."""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from backend.ai.generation.prompt_validator import PolicyPromptValidator, PromptValidator
from backend.ai.models.attack_asset import AttackAsset
from backend.ai.models.attack_plan import AttackPlan
from backend.ai.models.prompt_generation import Prompt
from backend.ai.utils.enums import StrategyMode


FAMILY_INDICATORS: dict[str, set[str]] = {
    "prompt_injection": {
        "ignore",
        "instruction",
        "override",
        "disregard",
        "obey",
        "disobey",
        "system",
        "developer",
        "safety",
        "guideline",
        "policy",
        "reveal",
        "hidden",
        "secret",
        "execute",
        "injected",
        "malicious",
        "decode",
        "encoded",
        "role",
    },
    "indirect_prompt_injection": {
        "injected",
        "instruction",
        "tool output",
        "retrieved",
        "document",
        "email",
        "webpage",
        "ignore",
        "override",
        "execute",
    },
    "jailbreak": {
        "jailbreak",
        "ignore",
        "unrestricted",
        "uncensored",
        "roleplay",
        "persona",
        "bypass",
        "policy",
        "rules",
        "refuse",
        "developer mode",
    },
    "prompt_leakage": {
        "system prompt",
        "hidden instruction",
        "developer message",
        "policy text",
        "reveal",
        "repeat",
        "verbatim",
        "configuration",
    },
    "data_exfiltration": {
        "secret",
        "credential",
        "token",
        "password",
        "private",
        "sensitive",
        "exfiltrate",
        "send",
        "reveal",
    },
    "tool_abuse": {
        "tool",
        "execute",
        "call",
        "permission",
        "approve",
        "argument",
        "action",
        "unauthorized",
    },
    "rag_poisoning": {
        "retrieval",
        "retrieved",
        "document",
        "source",
        "citation",
        "context",
        "poison",
        "knowledge base",
    },
    "roleplay": {
        "role",
        "roleplay",
        "pretend",
        "persona",
        "character",
        "fictional",
        "scenario",
        "authority",
    },
    "encoding": {
        "encode",
        "encoded",
        "decode",
        "base64",
        "hexadecimal",
        "unicode",
        "cipher",
        "reverse",
    },
    "multilingual": {
        "translate",
        "translation",
        "language",
        "multilingual",
        "english",
        "french",
        "spanish",
        "arabic",
    },
    "context_overflow": {
        "context",
        "previous",
        "earlier",
        "remember",
        "conversation",
        "instructions",
        "priority",
        "latest",
    },
}

FAMILY_ALIASES: dict[str, str] = {
    "context_manipulation": "context_overflow",
    "example_direct_prompt_injection": "prompt_injection",
    "retrieval_attacks": "rag_poisoning",
}

PLANNER_SCAFFOLD_PATTERN = re.compile(
    r"\b(?:authorized (?:test|security assessment) objective(?: placeholder)?|"
    r"controlled target condition|expected evaluation signal|selected strategy|target profile|"
    r"conversation context|planning evidence|candidate test input)\s*:",
    re.IGNORECASE,
)


@dataclass(slots=True)
class PromptFinalizationResult:
    """Accepted prompts plus auditable rejection information."""

    prompts: list[Prompt] = field(default_factory=list)
    rejected: list[dict[str, object]] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


class PromptFinalizer:
    """Render, enrich, classify, and validate prompts before execution."""

    def __init__(self, validator: PromptValidator | None = None) -> None:
        self.validator = validator or PolicyPromptValidator()

    def finalize(
        self,
        *,
        objective: str,
        plan: AttackPlan,
        prompts: list[Prompt],
    ) -> PromptFinalizationResult:
        """Return only concrete, relevant, validated prompt candidates."""

        result = PromptFinalizationResult()
        seen: set[str] = set()
        assets = {asset.id: asset for asset in [*plan.assets, *plan.retrieved_assets]}

        for sequence_index, candidate in enumerate(prompts, start=1):
            source = candidate.content.strip()
            target_content, objective_removed = self._sanitize_target_content(source, objective)
            family = self._normalize_family(candidate.attack_family or plan.selected_attack_family)
            conversation_mode = self._conversation_mode(plan, candidate)
            indicators = self._relevance_indicators(target_content, family)
            asset = self._source_asset(candidate, assets)
            metadata = {
                **candidate.metadata,
                "execution_ready": True,
                "non_executable": False,
                "objective_rendered": False,
                "objective_removed": objective_removed,
                "conversation_mode": conversation_mode,
                "conversation_group": plan.id if conversation_mode == "multi_turn" else candidate.id,
                "sequence_index": sequence_index,
                "relevance_indicators": indicators,
                "relevance_score": self._relevance_score(family, indicators),
            }
            if asset is not None:
                metadata.update(self._asset_metadata(asset))

            prompt = candidate.model_copy(
                update={
                    "content": target_content,
                    "objective": objective,
                    "attack_family": family or candidate.attack_family,
                    "turn": sequence_index if conversation_mode == "multi_turn" else 1,
                    "metadata": metadata,
                }
            )
            validation = self.validator.validate(prompt, seen)
            rejection_reasons = list(validation.errors)
            rejection_reasons.extend(self._quality_errors(target_content, objective, family))

            if rejection_reasons:
                result.rejected.append(
                    {
                        "prompt_id": prompt.id,
                        "sequence_index": sequence_index,
                        "attack_family": family,
                        "reasons": rejection_reasons,
                        "preview": target_content[:240],
                    }
                )
                continue

            normalized = str(validation.metadata.get("normalized", ""))
            if normalized:
                seen.add(normalized)
            prompt.metadata["validation_warnings"] = list(validation.warnings)
            if self._is_irrelevant(family, indicators):
                prompt.metadata["validation_warnings"].append(
                    f"Dataset prompt has weak lexical alignment with {family.replace('_', ' ')}; "
                    "preserved because keyword relevance is not an execution-readiness requirement."
                )
            result.prompts.append(prompt)

        if result.rejected:
            result.warnings.append(
                f"Rejected {len(result.rejected)} of {len(prompts)} generated prompt(s) during execution-readiness validation."
            )
        if not result.prompts:
            result.warnings.append("No generated prompts passed execution-readiness validation.")
        return result

    def is_relevant_candidate(self, *, content: str, family: str, objective: str) -> bool:
        """Return whether candidate text contains an observable family signal."""

        relevance_content, _ = self._sanitize_target_content(content.strip(), objective)
        normalized_family = self._normalize_family(family)
        indicators = self._relevance_indicators(relevance_content, normalized_family)
        return (
            not self._is_irrelevant(normalized_family, indicators)
            and not self._quality_errors(relevance_content, objective, normalized_family)
        )

    def _sanitize_target_content(
        self,
        content: str,
        objective: str,
    ) -> tuple[str, bool]:
        """Remove planner and evaluator scaffolding from the target payload."""

        scaffold_lines = (
            r"Authorized (?:test|security assessment) objective(?: placeholder)?:.*",
            r"(?:Assessment )?[Oo]bjective:.*",
            r"Controlled target condition:.*",
            r"Expected evaluation signal:.*",
            r"Selected strategy:.*",
            r"Target profile:.*",
            r"Conversation context:.*",
            r"Planning evidence:.*",
            r"Candidate test input:\s*",
        )
        sanitized = content
        for pattern in scaffold_lines:
            sanitized = re.sub(rf"(?im)^\s*{pattern}\s*$", "", sanitized)

        # Remove objective from inline contexts
        if objective.strip():
            objective_value = re.escape(objective.strip())
            # Match full phrase patterns
            sanitized = re.sub(
                rf"(?i)\s*Authorized (?:test|security assessment) objective(?: placeholder)?:\s*"
                rf"(?:\{{\{{\s*objective\s*\}}\}}|{objective_value})\.?",
                "",
                sanitized,
            )
            # Match standalone lines
            sanitized = re.sub(
                rf"(?im)^\s*(?:assessment\s+)?objective:\s*{objective_value}\.?\s*$",
                "",
                sanitized,
            )
            # Remove exact objective text appearing anywhere (not just patterns)
            # This catches cases where the objective is embedded without a prefix
            if len(objective.strip()) > 15:  # Only remove if objective is substantial
                sanitized = re.sub(
                    rf"(?i)\b{re.escape(objective.strip())}\b",
                    "",
                    sanitized,
                )

        # Remove all placeholder patterns
        for pattern in (r"\{\{\s*objective\s*\}\}", r"\{objective\}", r"\[OBJECTIVE\]"):
            sanitized = re.sub(pattern, "", sanitized, flags=re.IGNORECASE)

        # Replace restricted behavior placeholder
        sanitized = re.sub(
            r"\[RESTRICTED_BEHAVIOR\]",
            "the restricted behavior",
            sanitized,
            flags=re.IGNORECASE,
        )

        # Normalize excessive whitespace
        sanitized = re.sub(r"\n{3,}", "\n\n", sanitized).strip()
        return sanitized, sanitized != content

    def _quality_errors(self, content: str, objective: str, family: str) -> list[str]:
        """Return target-payload quality failures that require regeneration."""

        errors: list[str] = []
        if PLANNER_SCAFFOLD_PATTERN.search(content):
            errors.append("prompt contains planner-only scaffolding")
        if objective.strip() and objective.strip().lower() in content.lower():
            errors.append("prompt exposes the assessment objective to the target")
        words = re.findall(r"\b[\w'-]+\b", content, flags=re.UNICODE)
        if len(words) < 4:
            errors.append("prompt is not a complete target-directed instruction")
        if family not in {"encoding", "multilingual"} and len(content) >= 80:
            whitespace_ratio = sum(character.isspace() for character in content) / len(content)
            if whitespace_ratio < 0.035:
                errors.append("prompt is too dense or code-like for reliable execution")
        return errors

    def _conversation_mode(self, plan: AttackPlan, prompt: Prompt) -> str:
        configured = str(prompt.metadata.get("conversation_mode", "")).lower()
        if configured in {"single_turn", "multi_turn"}:
            return configured
        strategy = next(
            (item for item in plan.strategies if item.id == prompt.strategy_id),
            next((item for item in plan.strategies if item.id == plan.selected_strategy), None),
        )
        if strategy is not None:
            if strategy.mode is StrategyMode.MULTI_TURN:
                return "multi_turn"
            if strategy.mode is not StrategyMode.UNKNOWN:
                return "single_turn"
        strategy_id = (prompt.strategy_id or plan.selected_strategy).lower()
        if "multi-turn" in strategy_id or "multi_turn" in strategy_id or "gradual-escalation" in strategy_id:
            return "multi_turn"
        return "single_turn"

    def _relevance_indicators(self, content: str, family: str) -> list[str]:
        terms = FAMILY_INDICATORS.get(family)
        if not terms:
            return []
        candidate = content.lower()
        return sorted(term for term in terms if term in candidate)

    def _relevance_score(self, family: str, indicators: list[str]) -> float:
        if family not in FAMILY_INDICATORS:
            return 1.0
        return round(min(1.0, len(indicators) / 3), 3)

    def _is_irrelevant(self, family: str, indicators: list[str]) -> bool:
        return family in FAMILY_INDICATORS and len(indicators) < 2

    def _source_asset(self, prompt: Prompt, assets: dict[str, AttackAsset]) -> AttackAsset | None:
        for asset_id in prompt.asset_ids:
            if asset_id in assets:
                return assets[asset_id]
        source_id = str(prompt.metadata.get("source_asset_id", ""))
        return assets.get(source_id)

    def _asset_metadata(self, asset: AttackAsset) -> dict[str, object]:
        return {
            "source_asset_id": asset.id,
            "asset_name": asset.name,
            "expected_behavior": asset.expected_behavior,
            "success_criteria": asset.success_criteria,
            "severity": asset.severity,
            "owasp_llm_top_10": asset.owasp_llm_top_10,
            "mitre_atlas": asset.mitre_atlas,
        }

    def _normalize_family(self, family: str) -> str:
        normalized = family.lower().removeprefix("af-").replace("-", "_").strip()
        return FAMILY_ALIASES.get(normalized, normalized)
