"""Tests for planner-driven attack execution."""

from __future__ import annotations

import asyncio
import unittest
from collections.abc import Sequence
from typing import Any

from backend.ai.models.attack_plan import AttackPlan
from backend.ai.models.planner_result import PlannerResult
from backend.ai.models.prompt_generation import Prompt
from backend.ai.providers.provider_interface import ProviderRequest, ProviderResponse
from backend.ai.utils.enums import ConfidenceLevel, PlanningStage
from backend.models.attack import AttackExecutor, AttackPrompt, AttackRequest, AttackStrategy
from backend.models.attack_result import Score
from backend.models.conversation import Message
from backend.models.execution_result import (
    ExecutionConfig,
    ExecutionErrorCode,
    ExecutionStatus,
    TurnStatus,
)
from backend.targets.base_target import TargetAdapter


class SequencedProvider:
    """Provider double that returns or raises configured outcomes in order."""

    provider_name = "test-provider"
    model = "test-model"

    def __init__(self, outcomes: list[Any]) -> None:
        self.outcomes = list(outcomes)
        self.requests: list[ProviderRequest] = []

    async def complete(self, request: ProviderRequest) -> ProviderResponse:
        self.requests.append(request.model_copy(deep=True))
        outcome = self.outcomes.pop(0)
        if isinstance(outcome, BaseException):
            raise outcome
        return outcome


class SlowProvider:
    provider_name = "slow-provider"
    model = "slow-model"

    def __init__(self) -> None:
        self.calls = 0

    async def complete(self, request: ProviderRequest) -> ProviderResponse:
        self.calls += 1
        await asyncio.sleep(0.05)
        return ProviderResponse(content="late", model=self.model)


class InterruptingProvider:
    provider_name = "interrupting-provider"
    model = "interrupting-model"

    async def complete(self, request: ProviderRequest) -> ProviderResponse:
        raise asyncio.CancelledError


class FakeTarget(TargetAdapter):
    name = "fake-target"
    model = "target-model"

    def __init__(self) -> None:
        self.requests: list[list[Message]] = []

    async def send(self, messages: Sequence[Message]) -> Message:
        self.requests.append(list(messages))
        return Message(role="assistant", content="target response", metadata={"source": "fake"})


class FakeScorer:
    def score(self, prompt: str, response: str) -> Score:
        return Score(value=0.1, label="safe", reason="test")

    def error_score(self, message: str) -> Score:
        return Score(value=0.0, label="error", reason=message)


class FakeStrategy(AttackStrategy):
    name = "fake-strategy"
    category = "test"

    def build_prompts(self, request: AttackRequest) -> Sequence[AttackPrompt]:
        return [AttackPrompt(text="legacy prompt", category=self.category, technique="legacy")]


def planner_result(*contents: str, metadata: dict[str, Any] | None = None) -> PlannerResult:
    """Build the smallest valid completed planner result for executor tests."""

    prompts = [
        Prompt(
            id=f"prompt-{index}",
            content=content,
            objective="test objective",
            strategy_id="strategy-1",
            attack_family="family-1",
            asset_ids=[f"asset-{index}"],
            turn=index,
            metadata={"source": "test"},
        )
        for index, content in enumerate(contents, start=1)
    ]
    plan = AttackPlan(
        id="plan-1",
        objective="test objective",
        selected_attack_family="family-1",
        selected_strategy="strategy-1",
    )
    result_metadata = {"generated_prompts": [prompt.model_dump() for prompt in prompts]}
    result_metadata.update(metadata or {})
    return PlannerResult(
        success=True,
        stage=PlanningStage.COMPLETED,
        plan=plan,
        confidence=0.8,
        confidence_level=ConfidenceLevel.HIGH,
        metadata=result_metadata,
    )


class AttackExecutorTests(unittest.IsolatedAsyncioTestCase):
    async def test_multi_turn_execution_preserves_conversation_context(self) -> None:
        provider = SequencedProvider(
            [
                ProviderResponse(
                    content="response one",
                    model="resolved-model",
                    metadata={"usage": {"total_tokens": 5}},
                ),
                ProviderResponse(
                    content="response two",
                    model="resolved-model",
                    metadata={"usage": {"total_tokens": 7}},
                ),
            ]
        )
        executor = AttackExecutor(provider=provider)

        result = await executor.execute(
            planner_result("prompt one", "prompt two"),
            ExecutionConfig(max_retries=0, conversation_mode="multi_turn"),
        )

        self.assertEqual(result.execution_status, ExecutionStatus.COMPLETED)
        self.assertEqual(result.responses, ["response one", "response two"])
        self.assertEqual(result.total_turns, 2)
        self.assertEqual(result.execution_metrics.token_usage["total_tokens"], 12)
        self.assertEqual(
            [message.role.value for message in provider.requests[1].messages],
            ["user", "assistant", "user"],
        )
        self.assertEqual(
            [message.content for message in provider.requests[1].messages],
            ["prompt one", "response one", "prompt two"],
        )
        self.assertEqual(result.conversation_history[1].metadata["planned_turn"], 2)
        self.assertEqual(result.conversation_history[1].metadata["conversation_mode"], "multi_turn")

    async def test_single_turn_prompts_receive_fresh_conversation_histories(self) -> None:
        provider = SequencedProvider(
            [
                ProviderResponse(content="response one", model="test-model"),
                ProviderResponse(content="response two", model="test-model"),
            ]
        )
        executor = AttackExecutor(provider=provider)

        result = await executor.execute(
            planner_result("prompt one", "prompt two"),
            ExecutionConfig(max_retries=0),
        )

        self.assertEqual(result.execution_status, ExecutionStatus.COMPLETED)
        self.assertEqual(
            [[message.role.value for message in request.messages] for request in provider.requests],
            [["user"], ["user"]],
        )
        self.assertEqual(provider.requests[1].messages[0].content, "prompt two")
        self.assertEqual(result.conversation_history[1].metadata["conversation_mode"], "single_turn")

    async def test_multi_turn_conversation_groups_do_not_share_context(self) -> None:
        result = planner_result("group one", "group two", "group two continuation")
        prompts = result.metadata["generated_prompts"]
        prompts[0]["metadata"].update({"conversation_mode": "multi_turn", "conversation_group": "group-1"})
        prompts[1]["metadata"].update({"conversation_mode": "multi_turn", "conversation_group": "group-2"})
        prompts[2]["metadata"].update({"conversation_mode": "multi_turn", "conversation_group": "group-2"})
        provider = SequencedProvider(
            [
                ProviderResponse(content="response one", model="test-model"),
                ProviderResponse(content="response two", model="test-model"),
                ProviderResponse(content="response three", model="test-model"),
            ]
        )

        execution = await AttackExecutor(provider=provider).execute(
            result,
            ExecutionConfig(max_retries=0),
        )

        self.assertEqual(execution.execution_status, ExecutionStatus.COMPLETED)
        self.assertEqual([message.content for message in provider.requests[1].messages], ["group two"])
        self.assertEqual(
            [message.content for message in provider.requests[2].messages],
            ["group two", "response two", "group two continuation"],
        )

    async def test_progress_callback_receives_turn_lifecycle_events(self) -> None:
        provider = SequencedProvider([ProviderResponse(content="response", model="test-model")])
        executor = AttackExecutor(provider=provider)
        events: list[dict[str, Any]] = []

        result = await executor.execute(
            planner_result("prompt"),
            ExecutionConfig(max_retries=0),
            progress_callback=events.append,
        )

        self.assertEqual(result.execution_status, ExecutionStatus.COMPLETED)
        self.assertEqual([event["type"] for event in events], ["turn_started", "turn_completed"])

    async def test_transient_rate_limit_is_retried_once(self) -> None:
        provider = SequencedProvider(
            [
                RuntimeError("Provider HTTP 429: rate limit exceeded"),
                ProviderResponse(content="recovered", model="test-model"),
            ]
        )
        executor = AttackExecutor(provider=provider)

        result = await executor.execute(
            planner_result("retry me"),
            ExecutionConfig(max_retries=2, retry_base_delay_seconds=0, retry_max_delay_seconds=0),
        )

        self.assertEqual(result.execution_status, ExecutionStatus.COMPLETED)
        self.assertEqual(len(provider.requests), 2)
        self.assertEqual(result.execution_metrics.retry_count, 1)
        self.assertEqual(result.errors[0].code, ExecutionErrorCode.RATE_LIMIT)
        self.assertTrue(result.errors[0].retryable)

    async def test_exhausted_transient_failure_remains_classified_as_retryable(self) -> None:
        provider = SequencedProvider(
            [
                RuntimeError("Provider HTTP 503: unavailable"),
                RuntimeError("Provider HTTP 503: unavailable"),
            ]
        )
        executor = AttackExecutor(provider=provider)

        result = await executor.execute(
            planner_result("retry me"),
            ExecutionConfig(
                max_retries=1,
                retry_base_delay_seconds=0,
                retry_max_delay_seconds=0,
            ),
        )

        self.assertEqual(result.execution_status, ExecutionStatus.FAILED)
        self.assertTrue(all(error.retryable for error in result.errors))

    async def test_transient_connection_failure_recovers(self) -> None:
        provider = SequencedProvider(
            [
                ConnectionError("connection refused"),
                ProviderResponse(content="recovered", model="test-model"),
            ]
        )
        executor = AttackExecutor(provider=provider)

        result = await executor.execute(
            planner_result("retry me"),
            ExecutionConfig(
                max_retries=1,
                retry_base_delay_seconds=0,
                retry_max_delay_seconds=0,
            ),
        )

        self.assertEqual(result.execution_status, ExecutionStatus.COMPLETED)
        self.assertEqual(result.errors[0].code, ExecutionErrorCode.CONNECTION_FAILURE)

    async def test_permanent_failure_is_not_retried_and_later_prompts_continue(self) -> None:
        provider = SequencedProvider(
            [
                RuntimeError("Authentication failed"),
                ProviderResponse(content="second response", model="test-model"),
            ]
        )
        executor = AttackExecutor(provider=provider)

        result = await executor.execute(
            planner_result("first prompt", "second prompt"),
            ExecutionConfig(max_retries=3),
        )

        self.assertEqual(result.execution_status, ExecutionStatus.PARTIAL)
        self.assertEqual(len(provider.requests), 2)
        self.assertEqual(result.conversation_history[0].status, TurnStatus.ERROR)
        self.assertEqual(result.conversation_history[1].status, TurnStatus.SUCCESS)
        self.assertEqual(result.errors[0].code, ExecutionErrorCode.PROVIDER_FAILURE)
        self.assertFalse(result.errors[0].retryable)

    async def test_timeout_is_retried_then_returned_as_structured_failure(self) -> None:
        provider = SlowProvider()
        executor = AttackExecutor(provider=provider)

        result = await executor.execute(
            planner_result("slow prompt"),
            ExecutionConfig(
                max_retries=1,
                timeout_seconds=0.001,
                retry_base_delay_seconds=0,
                retry_max_delay_seconds=0,
            ),
        )

        self.assertEqual(result.execution_status, ExecutionStatus.FAILED)
        self.assertEqual(provider.calls, 2)
        self.assertEqual(result.execution_metrics.provider_calls, 2)
        self.assertTrue(all(error.code is ExecutionErrorCode.TIMEOUT for error in result.errors))

    async def test_empty_response_is_not_retried(self) -> None:
        provider = SequencedProvider([ProviderResponse(content="   ", model="test-model")])
        executor = AttackExecutor(provider=provider)

        result = await executor.execute(planner_result("prompt"), ExecutionConfig(max_retries=3))

        self.assertEqual(result.execution_status, ExecutionStatus.FAILED)
        self.assertEqual(len(provider.requests), 1)
        self.assertEqual(result.errors[0].code, ExecutionErrorCode.EMPTY_RESPONSE)

    async def test_malformed_response_is_not_retried(self) -> None:
        provider = SequencedProvider([{"unexpected": "shape"}])
        executor = AttackExecutor(provider=provider)

        result = await executor.execute(planner_result("prompt"), ExecutionConfig(max_retries=3))

        self.assertEqual(result.execution_status, ExecutionStatus.FAILED)
        self.assertEqual(len(provider.requests), 1)
        self.assertEqual(result.errors[0].code, ExecutionErrorCode.MALFORMED_RESPONSE)

    async def test_max_turns_returns_partial_result_and_warning(self) -> None:
        provider = SequencedProvider([ProviderResponse(content="only response", model="test-model")])
        executor = AttackExecutor(provider=provider)

        result = await executor.execute(
            planner_result("prompt one", "prompt two"),
            ExecutionConfig(max_turns=1, max_retries=0),
        )

        self.assertEqual(result.execution_status, ExecutionStatus.PARTIAL)
        self.assertEqual(result.total_turns, 1)
        self.assertEqual(result.execution_metrics.planned_turns, 2)
        self.assertIn("max_turns=1", result.warnings[0])

    async def test_planner_execution_metadata_controls_turn_limit(self) -> None:
        provider = SequencedProvider([ProviderResponse(content="only response", model="test-model")])
        executor = AttackExecutor(provider=provider)
        planned = planner_result(
            "prompt one",
            "prompt two",
            metadata={"execution_metadata": {"max_turns": 1, "max_retries": 0}},
        )

        result = await executor.execute(planned)

        self.assertEqual(result.execution_status, ExecutionStatus.PARTIAL)
        self.assertEqual(result.total_turns, 1)
        self.assertEqual(len(provider.requests), 1)

    async def test_sensitive_target_and_execution_metadata_is_redacted(self) -> None:
        provider = SequencedProvider([ProviderResponse(content="response", model="test-model")])
        executor = AttackExecutor(provider=provider)
        planned = planner_result(
            "prompt",
            metadata={
                "target_information": {
                    "model": "test-model",
                    "api_key": "target-secret",
                    "request_metadata": {"authorization": "Bearer target-token"},
                }
            },
        )

        result = await executor.execute(
            planned,
            ExecutionConfig(metadata={"nested": {"access_token": "execution-secret"}}),
        )

        self.assertEqual(result.metadata["target_information"]["api_key"], "[REDACTED]")
        self.assertEqual(
            result.metadata["target_information"]["request_metadata"]["authorization"],
            "[REDACTED]",
        )
        self.assertEqual(result.metadata["nested"]["access_token"], "[REDACTED]")

    async def test_failed_planner_result_never_calls_provider(self) -> None:
        provider = SequencedProvider([])
        executor = AttackExecutor(provider=provider)
        failed = PlannerResult(
            success=False,
            stage=PlanningStage.FAILED,
            errors=["planning failed"],
        )

        result = await executor.execute(failed)

        self.assertEqual(result.execution_status, ExecutionStatus.FAILED)
        self.assertEqual(result.total_turns, 0)
        self.assertEqual(len(provider.requests), 0)
        self.assertEqual(result.errors[0].code, ExecutionErrorCode.INVALID_PLANNER_RESULT)

    async def test_interruption_returns_structured_interrupted_result(self) -> None:
        executor = AttackExecutor(provider=InterruptingProvider())

        result = await executor.execute(planner_result("prompt"), ExecutionConfig(max_retries=0))

        self.assertEqual(result.execution_status, ExecutionStatus.INTERRUPTED)
        self.assertEqual(result.conversation_history[0].status, TurnStatus.INTERRUPTED)
        self.assertEqual(result.errors[0].code, ExecutionErrorCode.INTERRUPTED)

    async def test_existing_target_adapter_is_supported_through_provider_bridge(self) -> None:
        target = FakeTarget()
        executor = AttackExecutor(target=target)

        result = await executor.execute(planner_result("target prompt"), ExecutionConfig(max_retries=0))

        self.assertEqual(result.execution_status, ExecutionStatus.COMPLETED)
        self.assertEqual(result.provider, "fake")
        self.assertEqual(result.model, "target-model")
        self.assertEqual(target.requests[0][0].content, "target prompt")

    async def test_legacy_strategy_execution_remains_compatible(self) -> None:
        target = FakeTarget()
        executor = AttackExecutor(target=target, scorer=FakeScorer())

        results = await executor.run(FakeStrategy(), AttackRequest(objective="legacy"))

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].response, "target response")
        self.assertEqual(results[0].prompt, "legacy prompt")


if __name__ == "__main__":
    unittest.main()
