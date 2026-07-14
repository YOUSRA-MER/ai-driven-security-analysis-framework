# AI-Driven Security Analysis Platform for LLM Applications

This is a new, independent backend project for testing LLM applications against prompt injection, jailbreak, prompt leakage, indirect prompt injection, and data leakage risks.


## Architecture

```text
backend/
  api/          API boundary for future HTTP endpoints
  attacks/      Dataset-backed attack strategies and sourced prompt library
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

- `backend/attacks/datasets/*.json`: curated attack entries with OWASP mappings, source references, success criteria, and mutation-ready tags.
- `backend/attacks/datasets/knowledge_dataset/`: normalized planning knowledge for the future AI Planning Agent. It stores objectives, attack families, strategies, evaluation rules, model profiles, mitigations, taxonomies, references, and JSON Schemas, but intentionally does not store attack prompts or payloads.
- `backend/attacks/library.py`: shared dataset loader with filtering, random selection, placeholder rendering, and `AttackPrompt` conversion.
- `backend/attacks/prompt_injection.py`: PromptInject, garak, and ps-fuzz style direct injection probes.
- `backend/attacks/jailbreak.py`: Crescendo, AdvBench, HarmBench, and FlipAttack style probes using safe placeholders for restricted behaviors.
- `backend/attacks/prompt_leakage.py`: PromptInject prompt-leakage and hidden instruction disclosure probes.
- `backend/attacks/indirect_prompt_injection.py`: hidden web, HTML comment, and tool-content indirect injections.
- `backend/attacks/rag_poisoning.py`: poisoned retrieval chunks, citation laundering, and recency-boost attacks.
- `backend/attacks/roleplay.py`: movie-script, persona, and fictional framing probes.
- `backend/attacks/encoding.py`: reversed-word, encoded-wrapper, and delimiter escape probes.
- `backend/attacks/multilingual.py`: cross-lingual and mixed-script prompt attacks.
- `backend/attacks/context_overflow.py`: long-context, many-shot, and retrieval-stuffing probes.
- `backend/attacks/data_exfiltration.py`: secret, tool transcript, and training-data replay probes.
- `backend/attacks/data_leakage.py`: compatibility alias for existing data leakage workflows.

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
