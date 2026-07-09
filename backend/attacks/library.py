"""Dataset-backed attack library utilities."""

from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Any, Iterable

from backend.models.attack import AttackPrompt, AttackRequest, AttackStrategy


DATASET_DIR = Path(__file__).with_name("datasets") / "Attack_dataset"


class DatasetAttackStrategy(AttackStrategy):
    """Attack strategy that loads reusable prompts from a JSON dataset."""

    dataset_name: str

    def __init__(self, dataset_dir: Path | None = None) -> None:
        self.dataset_dir = dataset_dir or DATASET_DIR

    def load_attacks(self) -> list[dict[str, Any]]:
        path = self.dataset_dir / self.dataset_name
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
        if not isinstance(data, list):
            raise ValueError(f"{path} must contain a JSON list")
        return data

    def filter_attacks(
        self,
        *,
        category: str | None = None,
        tags: Iterable[str] | None = None,
        severity: str | None = None,
    ) -> list[dict[str, Any]]:
        attacks = self.load_attacks()
        tag_set = set(tags or [])
        if category:
            attacks = [attack for attack in attacks if attack.get("category") == category]
        if severity:
            attacks = [attack for attack in attacks if attack.get("severity") == severity]
        if tag_set:
            attacks = [
                attack
                for attack in attacks
                if tag_set.intersection(set(attack.get("tags", [])))
            ]
        return attacks

    def random_attack(
        self,
        *,
        category: str | None = None,
        tags: Iterable[str] | None = None,
        severity: str | None = None,
        rng: random.Random | None = None,
    ) -> dict[str, Any]:
        candidates = self.filter_attacks(category=category, tags=tags, severity=severity)
        if not candidates:
            raise ValueError("No attacks matched the requested filters")
        chooser = rng or random
        return chooser.choice(candidates)

    def build_prompts(self, request: AttackRequest) -> list[AttackPrompt]:
        category = request.metadata.get("category")
        tags = request.metadata.get("tags")
        severity = request.metadata.get("severity")
        attacks = self.filter_attacks(category=category, tags=tags, severity=severity)
        if request.metadata.get("randomize", False):
            random.shuffle(attacks)

        prompts: list[AttackPrompt] = []
        for attack in attacks:
            text = self.render_prompt(str(attack["attack_prompt"]), request)
            prompts.append(
                AttackPrompt(
                    text=text,
                    category=str(attack["category"]),
                    technique=str(attack["id"]),
                    metadata={
                        "attack_id": attack["id"],
                        "name": attack["name"],
                        "owasp_llm_top_10": attack.get("owasp_llm_top_10"),
                        "mitre_atlas": attack.get("mitre_atlas"),
                        "severity": attack.get("severity"),
                        "source": attack.get("original_source"),
                        "reference_url": attack.get("reference_url"),
                        "success_criteria": attack.get("success_criteria"),
                        "tags": attack.get("tags", []),
                        "mutation_ready": True,
                    },
                )
            )
        return prompts

    def render_prompt(self, prompt: str, request: AttackRequest) -> str:
        objective = request.objective or "[AUTHORIZED_TEST_OBJECTIVE]"
        return (
            prompt.replace("{{ objective }}", objective)
            .replace("{objective}", objective)
            .replace("[OBJECTIVE]", objective)
            .replace("[RESTRICTED_BEHAVIOR]", objective)
        )

