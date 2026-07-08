# Knowledge Dataset Architecture

## Version 1.0 Implementation

Dataset A Version 1.0 is implemented, populated, validated, and approved for
release.

- Architecture implemented: yes
- Production knowledge populated: yes
- Schema validation completed: yes
- Cross-reference validation completed: yes
- Release approved: yes

The architecture is stable and frozen for Version 1.0. The dataset is maintained
as a normalized JSON knowledge graph for retrieval, planning, reasoning,
evaluation, mitigation recommendation, reporting, and future RAG integration.

## 1. Reasoning Requirements

Before selecting an attack, an AI Planning Agent needs planning knowledge, not
more examples. Dataset A provides the knowledge needed to infer:

- The authorized security objective being tested.
- The failure mode and business risk behind that objective.
- Relevant attack families and which strategies are appropriate.
- Whether a test should be single-turn, multi-turn, tool-mediated, retrieval-based,
  or human-in-the-loop.
- Which safe prompt mutation concepts can vary framing without storing payloads.
- Which model or application traits increase or reduce expected vulnerability.
- Which evaluation rules, success indicators, and failure indicators should be used.
- Which OWASP LLM Top 10 and MITRE ATLAS mappings apply.
- Which mitigations and reporting recommendations should follow.
- Which objectives and attack families are related enough for retrieval expansion.

The architecture models knowledge as reusable entities connected by ID
references. The Attack Dataset remains the prompt memory. The Knowledge Dataset
is the planning graph.

## 2. Folder Hierarchy

```text
knowledge_dataset/
  README.md
  ARCHITECTURE.md
  index.json
  objectives/
    obj-*.json
    objective.example.json
  attack_families/
    af-*.json
    attack_family.example.json
  strategies/
    strat-*.json
    strategy.example.json
  prompt_mutations/
    mut-*.json
    prompt_mutation.example.json
  conversation_styles/
    style-*.json
    conversation_style.example.json
  model_profiles/
    model-*.json
    model_profile.example.json
  evaluation_rules/
    eval-*.json
    evaluation_rule.example.json
  mitigations/
    mit-*.json
    mitigation.example.json
  taxonomies/
    owasp/
      owasp-*.json
      owasp_mapping.example.json
    mitre/
      atlas-*.json
      mitre_mapping.example.json
  references/
    ref-*.json
    reference.example.json
  schemas/
    *.schema.json
```

## 3. Folder Rationale

### objectives/

Why it exists: objectives are the Planning Agent's entry point. They translate a
user's authorized testing goal into reusable reasoning labels.

Stores: security intent, risk statements, relevant attack families, taxonomy
mappings, evaluation rules, mitigations, and similarity links.

Files: one production JSON file per objective, named `<objective_id>.json`, plus
`objective.example.json`.

Used by: AI Planning Agent, Retrieval Engine, Reasoning Engine, Reporting Engine.

Relations: references attack families, evaluation rules, OWASP mappings, MITRE
mappings, mitigations, and related objectives.

### attack_families/

Why it exists: families group related testing approaches independently from
specific prompts.

Stores: family-level purpose, prerequisites, constraints, recommended strategies,
related families, and compatible model traits.

Files: one production JSON file per family, named `<attack_family_id>.json`,
plus `attack_family.example.json`.

Used by: Planning Agent, Adaptive Attack Generation, Retrieval Engine.

Relations: references strategies, prompt mutations, conversation styles,
evaluation rules, model profiles, taxonomies, mitigations, and references.

### strategies/

Why it exists: strategies describe how to conduct an authorized test at a planning
level without storing concrete attack text.

Stores: abstract planning method, recommended turns, prerequisites, mutation
concepts, evaluation rules, constraints, and stopping conditions.

Files: one production JSON file per strategy, named `<strategy_id>.json`, plus
`strategy.example.json`.

Used by: Reasoning Engine, Prompt Mutation Engine, Adaptive Attack Generation.

Relations: references prompt mutations, conversation styles, evaluation rules,
model profiles, attack families, and references.

### prompt_mutations/

Why it exists: mutation concepts help diversify generated test prompts while
keeping prompt strings in the Attack Dataset or generator layer.

Stores: abstract transformation intent, allowed scope, risk level, compatibility,
and safeguards.

Files: one production JSON file per mutation, named
`<prompt_mutation_id>.json`, plus `prompt_mutation.example.json`.

Used by: Prompt Mutation Engine, Adaptive Attack Generation.

Relations: referenced by strategies and attack families.

### conversation_styles/

Why it exists: turn structure is a planning decision. Some risks require single
turn probes; others require progressive, tool-mediated, or retrieval-aware tests.

Stores: interaction pattern, turn budget, state requirements, stopping rules, and
compatible strategies.

Files: one production JSON file per style, named `<conversation_style_id>.json`,
plus `conversation_style.example.json`.

Used by: Planning Agent, Orchestrator, Conversation Memory.

Relations: referenced by strategies and attack families.

### model_profiles/

Why it exists: model and deployment traits influence planning, scoring, and
expected vulnerability.

Stores: provider-neutral traits, capability assumptions, tool access, context
window class, retrieval exposure, guardrail posture, and known risk sensitivities.

Files: one production JSON file per profile, named `<model_profile_id>.json`,
plus `model_profile.example.json`.

Used by: Planning Agent, Target Adapters, Risk Classifier, Scoring Engine.

Relations: referenced by objectives, attack families, strategies, and evaluation
rules.

### evaluation_rules/

Why it exists: response analysis must be reusable and independent from attack
generation.

Stores: rule purpose, success indicators, failure indicators, evidence fields,
severity mapping, and scoring guidance.

Files: one production JSON file per rule, named `<evaluation_rule_id>.json`,
plus `evaluation_rule.example.json`.

Used by: Response Analyzer, Intelligent Scoring Engine, Reporting Engine.

Relations: referenced by objectives, attack families, and strategies.

### mitigations/

Why it exists: planning and reporting should connect each finding to practical
controls.

Stores: mitigation intent, control category, implementation guidance, verification
signals, and related taxonomy mappings.

Files: one production JSON file per mitigation, named `<mitigation_id>.json`,
plus `mitigation.example.json`.

Used by: Recommendation Engine, Reporting Engine.

Relations: referenced by objectives and attack families; references OWASP, MITRE,
and source references.

### taxonomies/owasp/

Why it exists: OWASP mappings are versioned and should not be duplicated across
objectives.

Stores: OWASP LLM Top 10 version, category ID, category name, planning relevance,
and related mitigations.

Files: one production JSON file per category mapping, named
`<owasp_mapping_id>.json`, plus `owasp_mapping.example.json`.

Used by: Planning Agent, Reporting Engine, Recommendation Engine.

Relations: referenced by objectives, families, rules, and mitigations.

### taxonomies/mitre/

Why it exists: MITRE ATLAS mappings change over time and should remain versioned.

Stores: ATLAS tactic or technique ID, name, version metadata, planning relevance,
and related entities.

Files: one production JSON file per mapping, named `<mitre_mapping_id>.json`,
plus `mitre_mapping.example.json`.

Used by: Planning Agent, Reporting Engine, Research Engine.

Relations: referenced by objectives, families, rules, and mitigations.

### references/

Why it exists: research provenance should be normalized and reusable.

Stores: papers, standards, repositories, documentation, blog posts, and internal
research notes.

Files: one production JSON file per reference, named `<reference_id>.json`,
plus `reference.example.json`.

Used by: Retrieval Engine, Reporting Engine, Research workflows.

Relations: referenced by every knowledge entity that depends on external or
internal source material.

### schemas/

Why it exists: schemas make the dataset machine-checkable.

Stores: JSON Schema files for each entity type.

Files: one schema per entity type, named `<entity>.schema.json`.

Used by: CI validation, dataset loaders, editor tooling, ingestion pipelines.

## 4. Entity Schemas

All entities share these base fields:

| Field | Type | Required | Validation | Description |
| --- | --- | --- | --- | --- |
| `id` | string | yes | lowercase kebab-case with domain prefix | Stable entity ID. |
| `name` | string | yes | 3-120 chars | Human-readable name. |
| `description` | string | yes | 20-1000 chars | Planning-oriented description. |
| `version` | string | yes | semantic version | Entity version. |
| `status` | string | yes | `draft`, `active`, `deprecated` | Lifecycle state. |
| `tags` | string[] | optional | lowercase snake_case | Retrieval tags. |
| `references` | string[] | optional | `ref-*` IDs | Source references. |
| `created_at` | string | yes | ISO 8601 date | Creation date. |
| `updated_at` | string | yes | ISO 8601 date | Last update date. |

### Objective

Prefix: `obj-`

Additional fields:

| Field | Type | Required | Validation | Description |
| --- | --- | --- | --- | --- |
| `user_intent_patterns` | string[] | yes | non-empty | Benign phrases that map user goals to this objective. |
| `security_problem` | string | yes | 10-300 chars | Risk being tested. |
| `planning_questions` | string[] | yes | non-empty | Questions the agent should answer before selecting strategies. |
| `recommended_attack_families` | string[] | yes | `af-*` IDs | Candidate families. |
| `recommended_evaluation_rules` | string[] | yes | `eval-*` IDs | Rules to score outcomes. |
| `owasp_mappings` | string[] | optional | `owasp-*` IDs | OWASP categories. |
| `mitre_mappings` | string[] | optional | `atlas-*` IDs | MITRE mappings. |
| `recommended_mitigations` | string[] | optional | `mit-*` IDs | Controls to report. |
| `related_objectives` | string[] | optional | `obj-*` IDs | Similar objectives. |

### Attack Family

Prefix: `af-`

Additional fields:

| Field | Type | Required | Validation | Description |
| --- | --- | --- | --- | --- |
| `scope` | string | yes | `direct`, `indirect`, `retrieval`, `tool`, `conversation`, `data` | Main testing surface. |
| `planning_use` | string | yes | 20-500 chars | When to select this family. |
| `recommended_strategies` | string[] | yes | `strat-*` IDs | Strategy options. |
| `compatible_conversation_styles` | string[] | yes | `style-*` IDs | Allowed turn structures. |
| `recommended_prompt_mutations` | string[] | optional | `mut-*` IDs | Safe mutation concepts. |
| `evaluation_rules` | string[] | yes | `eval-*` IDs | Scoring rules. |
| `related_families` | string[] | optional | `af-*` IDs | Related families. |
| `mitigations` | string[] | optional | `mit-*` IDs | Related controls. |

### Strategy

Prefix: `strat-`

Additional fields:

| Field | Type | Required | Validation | Description |
| --- | --- | --- | --- | --- |
| `attack_family` | string | yes | `af-*` ID | Owning family. |
| `strategy_type` | string | yes | controlled vocabulary | Abstract method category. |
| `recommended_turns` | object | yes | `min`, `max`, `preferred` integers | Turn budget guidance. |
| `conversation_styles` | string[] | yes | `style-*` IDs | Compatible styles. |
| `prompt_mutations` | string[] | optional | `mut-*` IDs | Mutation concepts. |
| `evaluation_rules` | string[] | yes | `eval-*` IDs | Rules to apply. |
| `preconditions` | string[] | optional | non-empty strings | Requirements before use. |
| `stop_conditions` | string[] | yes | non-empty strings | When to stop testing. |
| `safety_constraints` | string[] | yes | non-empty strings | Restrictions for authorized safe testing. |

### Prompt Mutation

Prefix: `mut-`

Additional fields:

| Field | Type | Required | Validation | Description |
| --- | --- | --- | --- | --- |
| `mutation_goal` | string | yes | 20-300 chars | Why the mutation is used. |
| `mutation_class` | string | yes | controlled vocabulary | Concept category. |
| `allowed_transformations` | string[] | yes | abstract only | Permitted high-level changes. |
| `prohibited_content` | string[] | yes | non-empty | Content this entity must never store. |
| `compatible_strategies` | string[] | optional | `strat-*` IDs | Strategy references. |

### Conversation Style

Prefix: `style-`

Additional fields:

| Field | Type | Required | Validation | Description |
| --- | --- | --- | --- | --- |
| `turn_pattern` | string | yes | controlled vocabulary | Single-turn, multi-turn, retrieval, tool, or mixed pattern. |
| `state_requirements` | string[] | optional | non-empty strings | Memory or context needs. |
| `turn_limits` | object | yes | integer min/max/preferred | Operational turn limits. |
| `recommended_for` | string[] | optional | `af-*` or `strat-*` IDs | Best-fit entities. |
| `stop_conditions` | string[] | yes | non-empty strings | Conversation termination guidance. |

### Model Profile

Prefix: `model-`

Additional fields:

| Field | Type | Required | Validation | Description |
| --- | --- | --- | --- | --- |
| `profile_type` | string | yes | `provider`, `deployment`, `capability`, `generic` | Profile category. |
| `capabilities` | string[] | yes | controlled tags | Relevant capabilities. |
| `context_window_class` | string | optional | `small`, `medium`, `large`, `very_large`, `unknown` | Context planning class. |
| `tool_access` | string | yes | `none`, `read_only`, `write_capable`, `external_action`, `unknown` | Tool risk level. |
| `risk_sensitivities` | object[] | optional | references `af-*` or `obj-*` | Known planning sensitivities. |
| `evaluation_notes` | string[] | optional | non-empty strings | Scoring considerations. |

### Evaluation Rule

Prefix: `eval-`

Additional fields:

| Field | Type | Required | Validation | Description |
| --- | --- | --- | --- | --- |
| `rule_type` | string | yes | `success`, `failure`, `severity`, `evidence`, `composite` | Rule category. |
| `success_indicators` | string[] | yes | behavioral indicators only | Signals of test success. |
| `failure_indicators` | string[] | yes | behavioral indicators only | Signals of target resilience. |
| `evidence_fields` | string[] | yes | snake_case | Evidence to capture. |
| `scoring_guidance` | object | yes | numeric 0.0-1.0 thresholds | Score interpretation. |
| `false_positive_risks` | string[] | optional | non-empty strings | Ambiguities to handle. |

### Mitigation

Prefix: `mit-`

Additional fields:

| Field | Type | Required | Validation | Description |
| --- | --- | --- | --- | --- |
| `control_category` | string | yes | controlled vocabulary | Policy, architecture, detection, training, evaluation, or operations. |
| `mitigates` | string[] | yes | `obj-*` or `af-*` IDs | Risks addressed. |
| `implementation_guidance` | string[] | yes | non-empty | Practical control guidance. |
| `verification_methods` | string[] | yes | non-empty | How to verify the mitigation. |
| `owasp_mappings` | string[] | optional | `owasp-*` IDs | OWASP links. |
| `mitre_mappings` | string[] | optional | `atlas-*` IDs | MITRE links. |

### OWASP Mapping

Prefix: `owasp-`

Additional fields:

| Field | Type | Required | Validation | Description |
| --- | --- | --- | --- | --- |
| `owasp_version` | string | yes | year/version string | OWASP LLM Top 10 version. |
| `category_id` | string | yes | e.g. `LLM01` | Category ID. |
| `category_name` | string | yes | 3-120 chars | Category name. |
| `planning_relevance` | string | yes | 20-500 chars | How planners use this category. |
| `related_entities` | string[] | optional | known entity IDs | Linked entities. |

### MITRE Mapping

Prefix: `atlas-`

Additional fields:

| Field | Type | Required | Validation | Description |
| --- | --- | --- | --- | --- |
| `atlas_id` | string | yes | MITRE ATLAS technique/tactic ID | External ATLAS identifier. |
| `atlas_name` | string | yes | 3-120 chars | Technique or tactic name. |
| `mapping_type` | string | yes | `tactic`, `technique`, `subtechnique` | Mapping type. |
| `planning_relevance` | string | yes | 20-500 chars | How planners use this mapping. |
| `related_entities` | string[] | optional | known entity IDs | Linked entities. |

### Reference

Prefix: `ref-`

Additional fields:

| Field | Type | Required | Validation | Description |
| --- | --- | --- | --- | --- |
| `source_type` | string | yes | `paper`, `standard`, `repository`, `documentation`, `blog`, `internal_note` | Source kind. |
| `authors` | string[] | optional | non-empty strings | Authors or organizations. |
| `published_at` | string | optional | ISO date or year | Publication date. |
| `url` | string | optional | URI | Source URL. |
| `citation` | string | yes | 5-500 chars | Human-readable citation. |
| `relevance` | string | yes | 20-500 chars | Why the source matters. |

## 5. Relationships

The dataset behaves as a lightweight knowledge graph:

- Objectives reference attack families, evaluation rules, taxonomies, mitigations,
  and related objectives.
- Attack families reference strategies, prompt mutations, conversation styles,
  evaluation rules, mitigations, related families, and references.
- Strategies reference one attack family, conversation styles, prompt mutations,
  evaluation rules, model profiles, and references.
- Prompt mutations are reusable concepts referenced by families and strategies.
- Conversation styles are reusable interaction plans referenced by families and
  strategies.
- Evaluation rules are shared by objectives, families, and strategies.
- Mitigations reference the risks and taxonomies they address.
- OWASP and MITRE mappings are versioned entities referenced by planning and
  reporting entities.
- References are normalized provenance records used across all entities.

No entity should duplicate another entity's long-form content. Store a canonical
record once and link to it by ID.

## 6. Naming And ID Conventions

- Production file names must equal the entity ID plus `.json`.
- Example files use `.example.json` and example-scoped IDs that do not collide
  with production IDs.
- IDs use lowercase kebab-case.
- Tags use lowercase snake_case.
- Dates use ISO 8601 calendar dates: `YYYY-MM-DD`.
- Versions use semantic versioning: `MAJOR.MINOR.PATCH`.
- Entity prefixes:
  - `obj-` objectives
  - `af-` attack families
  - `strat-` strategies
  - `mut-` prompt mutations
  - `style-` conversation styles
  - `model-` model profiles
  - `eval-` evaluation rules
  - `mit-` mitigations
  - `owasp-` OWASP mappings
  - `atlas-` MITRE mappings
  - `ref-` references

## 7. Validation Rules

- Every JSON file must validate against its schema in `schemas/`.
- Every referenced ID must exist in the dataset.
- Example files may use `.example.json`; production files must use exact IDs.
- Example files must reference example IDs only.
- Production files must not reference example IDs.
- Dataset entries must not contain concrete attack prompts, jailbreak prompts,
  payloads, exploit code, credentials, or step-by-step harmful instructions.
- `description`, `planning_use`, and `implementation_guidance` fields must stay
  reasoning-oriented.
- Taxonomy mappings must include a version field.
- Deprecated entities must keep their IDs stable and include replacement guidance
  in `description` or tags.

## 8. Scalability Notes

- Keep validation checks aligned with the approved release gates: JSON Schema,
  duplicate IDs, filename/ID consistency, and cross-reference integrity.
- Add generated embeddings over descriptions, tags, and relationship fields for
  retrieval without changing the canonical JSON format.
- Keep taxonomy versions as data, not folder names, so OWASP 2025, future OWASP
  versions, and MITRE ATLAS updates can coexist.
- Add `confidence` and `last_reviewed_at` fields later if research review
  workflows require maturity scoring.
- Introduce localized labels as optional sidecar files only if reporting needs
  multilingual output.
- Keep attack examples and generated prompts outside this dataset to preserve the
  separation between planning knowledge and attack memory.

## 9. Architectural Decisions

- JSON over a database: lightweight, reviewable, version-control friendly, and
  easy to load into future retrieval systems.
- Normalized entities over nested records: prevents duplicated taxonomy,
  mitigation, and evaluation logic.
- Stable IDs over path-derived references: enables file moves and future indexing.
- Versioned taxonomy mappings: supports OWASP and MITRE changes without breaking
  historical reports.
- Reasoning entities only: keeps the dataset safe, maintainable, and distinct from
  the Attack Dataset.
