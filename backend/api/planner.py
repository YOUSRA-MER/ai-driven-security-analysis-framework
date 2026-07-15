"""Planner playground API routes."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter
from pydantic import BaseModel, ConfigDict, Field

from backend.ai.models.planner_context import PlannerContext
from backend.ai.planner import AIPlanner
from backend.ai.providers.openrouter_provider import OpenRouterProvider
from backend.config.settings import get_settings


router = APIRouter(prefix="/planner", tags=["planner"])


class PlannerTestRequest(BaseModel):
    """Request body for planner playground tests."""

    model_config = ConfigDict(extra="forbid")

    objective: str = Field(min_length=1)
    target_type: str = "chatbot"


@router.post("/test")
async def test_planner(request: PlannerTestRequest) -> dict:
    """Run the complete planner pipeline for debugging in Swagger."""

    provider = OpenRouterProvider(settings=get_settings())
    planner = AIPlanner(provider=provider)
    context = PlannerContext(
        session_id=str(uuid4()),
        objective=request.objective,
        metadata={"target_type": request.target_type},
    )
    result = await planner.plan(context)
    plan = result.plan
    return {
        "success": result.success,
        "errors": result.errors,
        "warnings": result.warnings,
        "objective_analysis": context.objective_analysis.model_dump() if context.objective_analysis else None,
        "knowledge_used": [entry.model_dump() for entry in context.knowledge_entries],
        "attack_assets": [asset.model_dump() for asset in context.attack_assets],
        "selected_attack_family": plan.selected_attack_family if plan else "",
        "selected_strategy": plan.selected_strategy if plan else "",
        "reasoning_summary": plan.reasoning_summary if plan else "",
        "confidence": result.confidence,
        "attack_plan": plan.model_dump() if plan else None,
        "generated_prompts": result.metadata.get("generated_prompts", []),
        "trace": result.metadata.get("trace", []),
        "elapsed_ms": result.metadata.get("elapsed_ms"),
    }


@router.get("/health")
async def planner_health() -> dict:
    """Return planner and OpenRouter health status."""

    provider = OpenRouterProvider(settings=get_settings())
    provider_health = await provider.health()
    return {
        **provider_health,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
