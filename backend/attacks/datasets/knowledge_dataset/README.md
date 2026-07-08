# Knowledge Dataset

The Knowledge Dataset is Dataset A for the framework and is the reasoning layer
for the AI Planning Agent.

It does not store attack prompts, payloads, jailbreak examples, or executable attack
templates. Those belong in the existing Attack Dataset. This dataset stores the
normalized knowledge needed to decide what to test, why it matters, which attack
families are relevant, how to evaluate responses, and which mitigations should be
recommended afterward.

## Version 1.0 Status

- Architecture: Complete
- Production Knowledge: Complete
- Validation: Passed
- Release Status: Approved

Version 1.0 contains production-ready planning knowledge for retrieval, reasoning,
attack-family selection, strategy selection, evaluation, mitigation
recommendation, reporting, and future RAG integration. The architecture is stable
and frozen for Version 1.0.

Read [ARCHITECTURE.md](ARCHITECTURE.md) before adding entries. It defines the
folder hierarchy, entity schemas, ID conventions, relationships, validation rules,
and example records.

## Layout

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

The directory acts as a lightweight JSON knowledge graph. Each entity has a stable
ID and references other entities by ID.

## Directory Roles

- `objectives/`: user security objectives and planner entry points.
- `attack_families/`: reusable attack-family reasoning categories.
- `strategies/`: abstract, authorized testing strategies without prompt payloads.
- `prompt_mutations/`: safe mutation concepts for controlled prompt variation.
- `conversation_styles/`: turn-structure guidance for orchestration.
- `model_profiles/`: provider-neutral model and deployment traits.
- `evaluation_rules/`: response-analysis and scoring criteria.
- `mitigations/`: recommended controls and verification methods.
- `taxonomies/`: OWASP and MITRE ATLAS mappings.
- `references/`: normalized source and provenance records.
- `schemas/`: JSON Schemas used to validate each entity type.
