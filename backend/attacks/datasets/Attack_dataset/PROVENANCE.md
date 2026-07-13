# Attack Dataset Provenance

This provenance file is generated from the workbook `Source_Catalog` sheet and the source labels in `Real_Prompts_Data`.

## prompt_injection

- Meta CyberSecEval2/3 - Prompt Injection suite: https://github.com/meta-llama/PurpleLlama/tree/main/CybersecurityBenchmarks (catalog_id: src-prompt-injection-meta-cyberseceval2-3-prompt-injection-suite, matching_entries: 0, license: MIT)
- Open-Prompt-Injection (toolkit+attacks/defenses): https://github.com/liu00222/Open-Prompt-Injection (catalog_id: src-prompt-injection-open-prompt-injection-toolkit-attacks-defenses, matching_entries: 0, license: MIT/BSD (check repo))
- awesome-prompt-injection (curated list): https://github.com/Joe-B-Security/awesome-prompt-injection (catalog_id: src-prompt-injection-awesome-prompt-injection-curated-list, matching_entries: 0, license: unspecified)
- deepset/prompt-injections: https://huggingface.co/datasets/deepset/prompt-injections (catalog_id: src-prompt-injection-deepset-prompt-injections, matching_entries: 300, license: Apache 2.0)
- facebook/cyberseceval3-visual-prompt-injection: https://huggingface.co/datasets/facebook/cyberseceval3-visual-prompt-injection (catalog_id: src-prompt-injection-facebook-cyberseceval3-visual-prompt-injection, matching_entries: 0, license: CC (check repo))

Additional prompt-row source labels mapped by converter heuristics:
- deepset/prompt-injections (HF) (entries: 300)
- jayavibhav/prompt-injection-safety (HF, ~50k train/10k test) (entries: 300)

## jailbreak

- AdvBench (harmful_behaviors.csv): https://github.com/llm-attacks/llm-attacks (catalog_id: src-jailbreak-advbench-harmful-behaviors-csv, matching_entries: 150, license: MIT)
- HarmBench: https://github.com/centerforaisafety/HarmBench (catalog_id: src-jailbreak-harmbench, matching_entries: 0, license: MIT)
- JailBreakV-28K: https://arxiv.org/abs/2404.03027 (catalog_id: src-jailbreak-jailbreakv-28k, matching_entries: 0, license: Check paper for license)
- JailbreakBench / JBB-Behaviors: https://github.com/JailbreakBench/jailbreakbench (catalog_id: src-jailbreak-jailbreakbench-jbb-behaviors, matching_entries: 200, license: MIT + dataset DOI 10.57967/hf/2540)
- verazuo/jailbreak_llms (Do Anything Now): https://github.com/verazuo/jailbreak_llms (catalog_id: src-jailbreak-verazuo-jailbreak-llms-do-anything-now, matching_entries: 150, license: CC BY-NC-SA (research use - check LICENSE))

Additional prompt-row source labels mapped by converter heuristics:
- JailbreakBench/JBB-Behaviors (NeurIPS 2024) (entries: 200)
- llm-attacks/llm-attacks (AdvBench) (entries: 150)
- verazuo/jailbreak_llms (Shen et al., CCS 2024) (entries: 150)

## prompt_leakage

- LeakAgent: https://arxiv.org/abs/2412.05734 (catalog_id: src-prompt-leakage-leakagent, matching_entries: 0, license: Check repo)
- LeakBench: https://arxiv.org/abs/2606.18673 (catalog_id: src-prompt-leakage-leakbench, matching_entries: 0, license: Check paper)
- PLeak: https://arxiv.org/abs/2405.06823 (catalog_id: src-prompt-leakage-pleak, matching_entries: 0, license: Check repo)
- Prompt Leakage Effect and Defense Strategies (EMNLP 2024): https://arxiv.org/abs/2404.16251 (catalog_id: src-prompt-leakage-prompt-leakage-effect-and-defense-strategies-emnlp-2024, matching_entries: 0, license: unspecified)
- System Prompt Leakage Dataset (~355k rows): https://huggingface.co/datasets/gabrielchua/system-prompt-leakage (catalog_id: src-prompt-leakage-system-prompt-leakage-dataset-355k-rows, matching_entries: 150, license: Check HF card)

Additional prompt-row source labels mapped by converter heuristics:
- gabrielchua/system-prompt-leakage (~355k rows, HF) (entries: 150)

## indirect_prompt_injection

- Adaptive Attacks Break IPI Defenses: https://arxiv.org/abs/2503.00061 (catalog_id: src-indirect-prompt-inje-adaptive-attacks-break-ipi-defenses, matching_entries: 0, license: unspecified)
- AgentDojo: https://github.com/ethz-spylab/agentdojo (catalog_id: src-indirect-prompt-inje-agentdojo, matching_entries: 0, license: MIT)
- Greshake et al. foundational paper: https://arxiv.org/abs/2302.12173 (catalog_id: src-indirect-prompt-inje-greshake-et-al-foundational-paper, matching_entries: 0, license: unspecified)
- InjecAgent: https://github.com/uiuc-kang-lab/InjecAgent (catalog_id: src-indirect-prompt-inje-injecagent, matching_entries: 240, license: MIT (check repo))
- Taxonomy of Agent Safety Benchmarks (survey): https://arxiv.org/abs/2605.16282 (catalog_id: src-indirect-prompt-inje-taxonomy-of-agent-safety-benchmarks-survey, matching_entries: 0, license: unspecified)

Additional prompt-row source labels mapped by converter heuristics:
- uiuc-kang-lab/InjecAgent (Zhan et al., ACL 2024) (entries: 240)

## rag_poisoning

- Awesome-Rag-Attacks (framework): https://github.com/jawadhussein462/Awesome-Rag-Attacks (catalog_id: src-rag-poisoning-awesome-rag-attacks-framework, matching_entries: 0, license: Check repo)
- Awesome-Trustworthy-RAG (curated list): https://github.com/Arstanley/Awesome-Trustworthy-RAG (catalog_id: src-rag-poisoning-awesome-trustworthy-rag-curated-list, matching_entries: 0, license: unspecified)
- Benchmarking Poisoning Attacks against RAG: https://arxiv.org/abs/2505.18543 (catalog_id: src-rag-poisoning-benchmarking-poisoning-attacks-against-rag, matching_entries: 0, license: unspecified)
- PoisonedRAG: https://github.com/sleeepeer/PoisonedRAG (catalog_id: src-rag-poisoning-poisonedrag, matching_entries: 24, license: Check repo)
- Uncovering Competing Poisoning Attacks in RAG: https://arxiv.org/abs/2505.12574 (catalog_id: src-rag-poisoning-uncovering-competing-poisoning-attacks-in-rag, matching_entries: 0, license: unspecified)

Additional prompt-row source labels mapped by converter heuristics:
- sleeepeer/PoisonedRAG (USENIX Security 2025) - raw repo artifacts (entries: 24)

## roleplay

- "Do Anything Now" paper (Shen et al.): https://arxiv.org/abs/2308.03825 (catalog_id: src-roleplay-do-anything-now-paper-shen-et-al, matching_entries: 0, license: unspecified)
- JailbreakHunter: https://arxiv.org/abs/2407.03045 (catalog_id: src-roleplay-jailbreakhunter, matching_entries: 0, license: unspecified)
- RoleBreak / RoleBreakEval: https://arxiv.org/abs/2409.16727 (catalog_id: src-roleplay-rolebreak-rolebreakeval, matching_entries: 0, license: unspecified)
- verazuo/jailbreak_llms (DAN/persona subset): https://github.com/verazuo/jailbreak_llms (catalog_id: src-roleplay-verazuo-jailbreak-llms-dan-persona-subset, matching_entries: 150, license: CC BY-NC-SA (check LICENSE))

Additional prompt-row source labels mapped by converter heuristics:
- verazuo/jailbreak_llms - filtered for roleplay/persona pattern (entries: 150)

## encoding

- JBShield (evaluates Base64/encoding jailbreaks): https://arxiv.org/abs/2502.07557 (catalog_id: src-encoding-jbshield-evaluates-base64-encoding-jailbreaks, matching_entries: 0, license: unspecified)
- MLCommons AILuminate Jailbreak Benchmark v0.5: https://mlcommons.org/wp-content/uploads/2025/12/MLCommons-Security-Jailbreak-0.5.1.pdf (catalog_id: src-encoding-mlcommons-ailuminate-jailbreak-benchmark-v0-5, matching_entries: 0, license: MLCommons terms)
- StructuralSleight: https://arxiv.org/abs/2406.08754 (catalog_id: src-encoding-structuralsleight, matching_entries: 0, license: unspecified)
- TeleAI-Safety framework: https://arxiv.org/abs/2512.05485 (catalog_id: src-encoding-teleai-safety-framework, matching_entries: 0, license: unspecified)
- h4rm3l (composable jailbreak language): https://proceedings.iclr.cc/paper_files/paper/2025/file/904aac1c930c196f1c71533d4d9dc31a-Paper-Conference.pdf (catalog_id: src-encoding-h4rm3l-composable-jailbreak-language, matching_entries: 1, license: unspecified)

Additional prompt-row source labels mapped by converter heuristics:
- Mixture of Encodings paper (entries: 1)
- PayloadsAllTheThings Prompt Injection (entries: 1)
- Promptfoo ASCII/Base64 encoding examples (entries: 1)
- PyRIT FlipAttack (entries: 1)

## multilingual

- CSRT (Code-Switching Red-Teaming dataset): https://arxiv.org/abs/2406.15481 (catalog_id: src-multilingual-csrt-code-switching-red-teaming-dataset, matching_entries: 0, license: unspecified)
- Low-resource languages jailbreak GPT-4 (Yong et al.): https://arxiv.org/abs/2310.02446 (catalog_id: src-multilingual-low-resource-languages-jailbreak-gpt-4-yong-et-al, matching_entries: 0, license: unspecified)
- MultiJail (Deng et al.): https://arxiv.org/abs/2310.06474 (catalog_id: src-multilingual-multijail-deng-et-al, matching_entries: 0, license: unspecified)
- Multilingual Prompt Injections dataset: https://huggingface.co/datasets/yanismiraoui/prompt_injections (catalog_id: src-multilingual-multilingual-prompt-injections-dataset, matching_entries: 300, license: Check HF card)

Additional prompt-row source labels mapped by converter heuristics:
- yanismiraoui/prompt_injections (HF) (entries: 300)

## context_overflow

- Anthropic - Many-shot Jailbreaking research: https://www.anthropic.com/research/many-shot-jailbreaking (catalog_id: src-context-overflow-anthropic-many-shot-jailbreaking-research, matching_entries: 1, license: unspecified)
- Cognitive Overload Attack: https://arxiv.org/abs/2410.11272 (catalog_id: src-context-overflow-cognitive-overload-attack, matching_entries: 0, license: unspecified)
- Many-Turn Jailbreaking: https://arxiv.org/abs/2508.06755 (catalog_id: src-context-overflow-many-turn-jailbreaking, matching_entries: 0, license: unspecified)
- Many-shot Jailbreaking (NeurIPS 2024 paper): https://proceedings.neurips.cc/paper_files/paper/2024/file/ea456e232efb72d261715e33ce25f208-Paper-Conference.pdf (catalog_id: src-context-overflow-many-shot-jailbreaking-neurips-2024-paper, matching_entries: 0, license: unspecified)
- What Really Matters in Many-Shot Attacks?: https://arxiv.org/abs/2505.19773 (catalog_id: src-context-overflow-what-really-matters-in-many-shot-attacks, matching_entries: 0, license: unspecified)

Additional prompt-row source labels mapped by converter heuristics:
- Lost in the Middle / long-context evaluation (entries: 1)
- NVIDIA Garak probes (entries: 1)
- OWASP GenAI Security guidance (entries: 1)
- Promptfoo long-context evaluation (entries: 1)

## data_exfiltration

- AgentDojo (exfiltration-style attacker goals): https://github.com/ethz-spylab/agentdojo (catalog_id: src-data-exfiltration-agentdojo-exfiltration-style-attacker-goals, matching_entries: 0, license: MIT)
- InjecAgent (data-stealing test cases): https://github.com/uiuc-kang-lab/InjecAgent (catalog_id: src-data-exfiltration-injecagent-data-stealing-test-cases, matching_entries: 120, license: MIT (check repo))
- MITRE ATLAS AML.T0086 / AML.T0024: https://atlas.mitre.org/ (catalog_id: src-data-exfiltration-mitre-atlas-aml-t0086-aml-t0024, matching_entries: 0, license: MITRE terms)
- PII-Compass: https://arxiv.org/abs/2407.02943 (catalog_id: src-data-exfiltration-pii-compass, matching_entries: 0, license: unspecified)
- PII-Scope: https://arxiv.org/abs/2410.06704 (catalog_id: src-data-exfiltration-pii-scope, matching_entries: 0, license: unspecified)

Additional prompt-row source labels mapped by converter heuristics:
- uiuc-kang-lab/InjecAgent (Zhan et al., ACL 2024) (entries: 120)

## tool_abuse

- AgentDojo: https://github.com/ethz-spylab/agentdojo (catalog_id: src-tool-abuse-agentdojo, matching_entries: 0, license: MIT)
- InjecAgent (all test cases): https://github.com/uiuc-kang-lab/InjecAgent (catalog_id: src-tool-abuse-injecagent-all-test-cases, matching_entries: 150, license: MIT (check repo))
- MITRE ATLAS AML.T0053: https://atlas.mitre.org/ (catalog_id: src-tool-abuse-mitre-atlas-aml-t0053, matching_entries: 0, license: MITRE terms)
- Meta CyberSecEval2/3 - Code Interpreter Abuse suite: https://github.com/meta-llama/PurpleLlama/tree/main/CybersecurityBenchmarks (catalog_id: src-tool-abuse-meta-cyberseceval2-3-code-interpreter-abuse-suite, matching_entries: 0, license: MIT)
- OWASP Top 10 for Agentic Applications (Dec 2025): https://genai.owasp.org/ (catalog_id: src-tool-abuse-owasp-top-10-for-agentic-applications-dec-2025, matching_entries: 0, license: OWASP CC BY-SA 4.0)

Additional prompt-row source labels mapped by converter heuristics:
- uiuc-kang-lab/InjecAgent (Zhan et al., ACL 2024) (entries: 150)
