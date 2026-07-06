# AI-Driven Security Analysis Platform for LLM Applications

This is a new, independent backend project for testing LLM applications against prompt injection, jailbreak, prompt leakage, indirect prompt injection, and data leakage risks.

The project does not copy PHANTOM or Microsoft PyRIT. PHANTOM was used only to identify reusable attack categories and payload styles. PyRIT was used only as architectural inspiration for targets, normalization, scoring, memory, conversation handling, and attack orchestration.

## Architecture

```text
backend/
  api/          API boundary for future HTTP endpoints
  attacks/      Original attack strategies
  ai/           Orchestration and future adaptive AI components
  targets/      Provider-neutral target adapters
  prompt/       Prompt normalization and conversion
  scoring/      Response scoring and vulnerability evaluation
  models/       Domain models and abstract interfaces
  reports/      Future report generation
  database/     Future persistence adapters
  utils/        Shared utilities
  config/       Runtime configuration
  main.py       Minimal CLI entry point
```

## Core Interfaces

- `AttackStrategy`: builds attack prompts for a specific test category.
- `AttackExecutor`: executes prompts against a target and scores responses.
- `TargetAdapter`: abstracts OpenAI, Ollama, Gemini, Claude, REST APIs, or custom apps.
- `PromptNormalizer`: applies prompt cleanup and converter pipelines before sending.
- `Scorer`: converts responses into normalized vulnerability scores.
- `AIOrchestrator`: coordinates campaigns and single attack runs.
- `AttackMemory`: placeholder boundary for future conversation and evidence persistence.

## Attack Modules

- `backend/attacks/prompt_injection.py`: direct instruction override, structured payload, metadata-style override, recursive instruction, and authority-claim probes.
- `backend/attacks/jailbreak.py`: controlled persona, fictional frame, authority escalation, continuation, and crescendo probes.
- `backend/attacks/prompt_leakage.py`: hidden instruction, configuration, hierarchy, and translation probes.
- `backend/attacks/indirect_prompt_injection.py`: document, metadata, hidden-text, and multi-turn memory-seed payloads for RAG/tool workflows.
- `backend/attacks/data_leakage.py`: secret, PII, endpoint, and debug-bundle leakage probes.

## Execution Flow

1. A user creates an `AttackRequest` with an objective and attempt limit.
2. `AIOrchestrator` selects one or more `AttackStrategy` classes.
3. Each strategy generates provider-neutral `AttackPrompt` objects.
4. `AttackExecutor` sends each prompt through `PromptNormalizer`.
5. The normalized prompt is appended to a `Conversation`.
6. A `TargetAdapter` sends the conversation to an LLM app or model provider.
7. The response is passed to a `Scorer`.
8. The scorer returns a `Score` with label, reason, and evidence.
9. The executor returns `AttackResult` records.
10. Future report modules will aggregate results into campaign reports.

## PHANTOM Concepts Reused

- Attack category coverage for prompt injection, jailbreak, leakage, indirect injection, and RAG-oriented attacks.
- Payload mutation concepts such as structured prompts, metadata injection, hidden document directives, many-shot/crescendo-style jailbreaks, and leakage pattern detection.
- The attack content was rewritten and reorganized behind this project's own interfaces.

## PyRIT Concepts Reused

- Strategy-driven attack execution.
- Provider-neutral target abstraction.
- Prompt normalization before target delivery.
- Conversation and message models.
- Scoring as a separate architecture boundary.
- Campaign orchestration as a service instead of embedding execution in each attack.

## Recommended Study Order

1. `backend/models/conversation.py`
2. `backend/models/attack_result.py`
3. `backend/models/attack.py`
4. `backend/targets/base_target.py`
5. `backend/prompt/normalizer.py`
6. `backend/scoring/scorer.py`
7. `backend/ai/orchestrator.py`
8. `backend/attacks/prompt_injection.py`
9. `backend/attacks/prompt_leakage.py`
10. `backend/attacks/indirect_prompt_injection.py`
11. `backend/attacks/data_leakage.py`
12. `backend/attacks/jailbreak.py`
13. `backend/targets/rest_api.py`
14. `backend/targets/ollama.py`

## Roadmap

- Add a FastAPI layer in `backend/api/`.
- Implement provider SDK adapters for OpenAI, Gemini, and Claude.
- Add persistent attack memory and campaign storage.
- Add LLM-based response analysis and adaptive attack generation.
- Add report generation with remediation guidance.
- Add unit tests for strategies, scoring, target adapters, and orchestration.

## Example

```bash
python -m backend.main --attack prompt_injection --objective "test whether hidden instructions are exposed" --ollama-model llama3
```

