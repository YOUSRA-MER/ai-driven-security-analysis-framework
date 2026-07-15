"""Minimal backend entry point."""

from __future__ import annotations

import argparse
import asyncio
import logging

from fastapi import FastAPI

from backend.ai.orchestrator import AIOrchestrator
from backend.api.planner import router as planner_router
from backend.attacks.context_overflow import ContextOverflowAttack
from backend.attacks.data_leakage import DataLeakageAttack
from backend.attacks.data_exfiltration import DataExfiltrationAttack
from backend.attacks.encoding import EncodingAttack
from backend.attacks.indirect_prompt_injection import IndirectPromptInjectionAttack
from backend.attacks.jailbreak import JailbreakAttack
from backend.attacks.multilingual import MultilingualAttack
from backend.attacks.prompt_injection import PromptInjectionAttack
from backend.attacks.prompt_leakage import PromptLeakageAttack
from backend.attacks.rag_poisoning import RagPoisoningAttack
from backend.attacks.roleplay import RoleplayAttack
from backend.attacks.tool_abuse import ToolAbuseAttack
from backend.targets.ollama import OllamaTarget
from backend.targets.rest_api import RestApiTarget


logging.basicConfig(level=logging.INFO)

app = FastAPI(title="AI-Driven Security Analysis Platform")
app.include_router(planner_router)


ATTACKS = {
    "prompt_injection": PromptInjectionAttack,
    "jailbreak": JailbreakAttack,
    "prompt_leakage": PromptLeakageAttack,
    "indirect_prompt_injection": IndirectPromptInjectionAttack,
    "rag_poisoning": RagPoisoningAttack,
    "roleplay": RoleplayAttack,
    "encoding": EncodingAttack,
    "multilingual": MultilingualAttack,
    "context_overflow": ContextOverflowAttack,
    "data_exfiltration": DataExfiltrationAttack,
    "tool_abuse": ToolAbuseAttack,
    "data_leakage": DataLeakageAttack,
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run an LLM security analysis attack.")
    parser.add_argument("--attack", choices=ATTACKS.keys(), required=True)
    parser.add_argument("--objective", required=True)
    parser.add_argument("--max-attempts", type=int, default=5)
    parser.add_argument("--ollama-model")
    parser.add_argument("--rest-endpoint")
    return parser


async def run() -> None:
    args = build_parser().parse_args()

    if args.ollama_model:
        target = OllamaTarget(model=args.ollama_model)
    elif args.rest_endpoint:
        target = RestApiTarget(name="rest-api-target", endpoint=args.rest_endpoint)
    else:
        raise SystemExit("Provide --ollama-model or --rest-endpoint.")

    strategy = ATTACKS[args.attack]()
    orchestrator = AIOrchestrator(target=target)
    results = await orchestrator.run_attack(
        strategy=strategy,
        objective=args.objective,
        max_attempts=args.max_attempts,
    )

    for result in results:
        print(
            f"{result.attack_name}/{result.category} "
            f"status={result.status.value} score={result.score.value:.2f} "
            f"label={result.score.label} reason={result.score.reason}"
        )


if __name__ == "__main__":
    asyncio.run(run())
