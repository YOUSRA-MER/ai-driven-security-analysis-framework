"""Attack orchestration service."""

from __future__ import annotations

from collections.abc import Iterable

from backend.models.attack import AttackExecutor, AttackRequest, AttackStrategy
from backend.models.attack_result import AttackResult
from backend.prompt.normalizer import PromptNormalizer
from backend.scoring.scorer import RegexLeakScorer, Scorer
from backend.targets.base_target import TargetAdapter


class AIOrchestrator:
    """Coordinates attack strategies against a selected target."""

    def __init__(
        self,
        target: TargetAdapter,
        scorer: Scorer | None = None,
        normalizer: PromptNormalizer | None = None,
    ) -> None:
        self.executor = AttackExecutor(
            target=target,
            scorer=scorer or RegexLeakScorer(),
            normalizer=normalizer or PromptNormalizer(),
        )

    async def run_attack(
        self,
        strategy: AttackStrategy,
        objective: str,
        max_attempts: int = 5,
    ) -> list[AttackResult]:
        request = AttackRequest(objective=objective, max_attempts=max_attempts)
        return await self.executor.run(strategy, request)

    async def run_campaign(
        self,
        strategies: Iterable[AttackStrategy],
        objective: str,
        max_attempts_per_strategy: int = 5,
    ) -> list[AttackResult]:
        results: list[AttackResult] = []
        for strategy in strategies:
            request = AttackRequest(objective=objective, max_attempts=max_attempts_per_strategy)
            results.extend(await self.executor.run(strategy, request))
        return results

