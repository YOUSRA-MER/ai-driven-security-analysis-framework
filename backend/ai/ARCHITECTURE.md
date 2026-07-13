# AI Subsystem Architecture

The `backend.ai` package is the architecture layer for AI-assisted security
planning. It defines interfaces, Pydantic models, provider boundaries, memory
contracts, retrieval contracts, and planning orchestration skeletons.

This package intentionally does not implement attack execution, OpenRouter
requests, attack logic, or prompt generation behavior. Those responsibilities
belong to later implementation phases.

## Design Principles

- Planning only: The AI subsystem produces non-executable plans and typed
  intermediate objects.
- Dataset separation: Dataset A (`knowledge_dataset`) is reasoning knowledge.
  Dataset B (`Attack_dataset`) is attack asset data.
- Provider isolation: Provider adapters expose a neutral interface and hide
  provider-specific request formats.
- No side effects: Planner, retrieval, reasoning, and generation interfaces do
  not execute attacks or call external tools.
- Auditability: Context, result, asset, and strategy models preserve source IDs,
  rationale, constraints, and metadata.
- Single responsibility: Each module owns one narrow concern.

## Package Layout

```text
backend/ai/
  planner/       Planning pipeline interfaces.
  retrieval/     Dataset A and Dataset B access boundaries.
  generation/    Future prompt construction, mutation, and validation contracts.
  reasoning/     Decision ranking and confidence estimation contracts.
  providers/     Provider-neutral AI model interfaces and adapter placeholders.
  memory/        Session and planner memory contracts.
  models/        Pydantic planning domain models.
  utils/         Constants, enums, and domain exceptions.
```

## Models

`models/planner_context.py` carries state through the planning pipeline. It
contains the raw objective, current planning stage, objective analysis,
retrieved knowledge, retrieved attack assets, constraints, trace messages, and
metadata.

`models/objective_analysis.py` represents normalized understanding of the user's
security objective, including target capabilities, risk themes, recommended
categories, constraints, and confidence.

`models/knowledge_entry.py` normalizes Dataset A records for objectives, attack
families, strategies, mutations, evaluation rules, mitigations, taxonomy
mappings, and references.

`models/attack_asset.py` normalizes Dataset B prompt/payload records. It keeps
source, reference URL, OWASP mapping, MITRE mapping, severity, tags, prompt
text, and metadata.

`models/strategy.py` defines abstract strategy selections. A strategy is not
executable; it describes why a plan should use a testing style and which assets
or knowledge records support it.

`models/attack_plan.py` defines a non-executable plan and ordered plan steps.
Plan steps reference strategy IDs and asset IDs but do not send prompts to
targets.

`models/planner_result.py` wraps planning output with success status, final
stage, optional plan, confidence, warnings, errors, and metadata.

## Planner Components

`planner/planner.py` is the composition root for the AI planning workflow.
Future implementations should coordinate all subcomponents here while keeping
attack execution outside this package.

`planner/objective_analyzer.py` converts a raw objective into
`ObjectiveAnalysis`.

`planner/attack_selector.py` selects relevant `AttackAsset` records from
retrieved Dataset B candidates.

`planner/strategy_selector.py` selects abstract `StrategySpec` records from
Dataset A knowledge and planner context.

`planner/attack_planner.py` builds a non-executable `AttackPlan` from selected
strategies and assets.

`planner/attack_optimizer.py` prunes, prioritizes, or reorganizes a plan before
downstream prompt construction.

`planner/adaptive_engine.py` defines a future feedback-aware planning boundary.
It adapts plans, not prompts or executions.

## Retrieval Components

`retrieval/dataset_a.py` is the repository contract for `knowledge_dataset`.
Dataset A is the planner reasoning layer and does not store executable prompts.

`retrieval/dataset_b.py` is the repository contract for `Attack_dataset`.
Dataset B stores sourced attack assets that can be selected later by planning
logic.

`retrieval/retriever.py` coordinates retrieval from Dataset A and Dataset B using
`ObjectiveAnalysis`.

## Generation Components

`generation/prompt_builder.py` is the future boundary for turning an abstract
plan step into a prompt candidate.

`generation/prompt_mutator.py` is the future boundary for controlled prompt
variation.

`generation/prompt_validator.py` is the future boundary for validating prompt
candidates before use. Validation is separate from generation so policy and
scope checks remain explicit.

## Reasoning Components

`reasoning/decision_engine.py` is the future boundary for ranking strategies or
decisions using rules, heuristics, or AI-assisted reasoning.

`reasoning/confidence_estimator.py` is the future boundary for producing numeric
and banded confidence estimates.

## Provider Components

`providers/provider_interface.py` defines provider-neutral request, response,
and message models, plus the `AIProvider` interface.

`providers/openrouter_provider.py` is a placeholder for a future OpenRouter
adapter. It intentionally raises `NotImplementedError` and does not perform HTTP
requests.

## Memory Components

`memory/session_memory.py` defines request/session-scoped memory for transient
planning state.

`memory/planner_memory.py` defines audit-oriented memory for storing planner
contexts and results.

## Data Flow

1. A caller creates a `PlannerContext` with a user objective and constraints.
2. `ObjectiveAnalyzer` produces `ObjectiveAnalysis`.
3. `AIRetriever` retrieves Dataset A knowledge and Dataset B attack assets.
4. `AttackSelector` chooses relevant attack assets.
5. `StrategySelector` chooses abstract strategies.
6. `AttackPlanner` builds a non-executable `AttackPlan`.
7. `AttackOptimizer` may refine the plan.
8. `ConfidenceEstimator` estimates confidence.
9. `Planner` returns `PlannerResult`.

No step in this flow sends prompts to targets, calls OpenRouter, executes tools,
or performs an attack.

## Dependency Direction

- `models` depends only on `utils`.
- `retrieval`, `planner`, `generation`, `reasoning`, and `memory` depend on
  `models`.
- `providers` depends on `utils` and provider-neutral Pydantic models.
- Existing runtime attack execution code should depend on this subsystem only
  through stable models and interfaces.

## Future Implementation Notes

- Concrete dataset repositories should live behind `DatasetARepository` and
  `DatasetBRepository`.
- Provider-specific API code should remain inside provider adapters.
- Prompt generation should require explicit validation before any external use.
- Attack execution should remain outside `backend.ai`.
