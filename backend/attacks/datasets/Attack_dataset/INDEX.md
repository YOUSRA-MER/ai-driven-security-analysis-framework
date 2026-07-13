# Attack Dataset Index

Excel-backed attack prompt dataset converted from `source/AI_Redteam_Sources_and_Prompts_extended.xlsx`.
The adjacent `knowledge_dataset` was not modified.

Total entries: 2244
Category files: 11
Source catalog records: 53

## Per-File Counts
| File | Entries |
| --- | --- |
| prompt_injection.json | 600 |
| jailbreak.json | 500 |
| prompt_leakage.json | 150 |
| indirect_prompt_injection.json | 240 |
| rag_poisoning.json | 24 |
| roleplay.json | 150 |
| encoding.json | 5 |
| multilingual.json | 300 |
| context_overflow.json | 5 |
| data_exfiltration.json | 120 |
| tool_abuse.json | 150 |

## Severity Distribution
| Severity | Entries |
| --- | --- |
| critical | 632 |
| high | 1307 |
| low | 2 |
| medium | 303 |

## Top Tags
| Tag | Entries |
| --- | --- |
| excel-import | 2244 |
| high | 1307 |
| hf | 750 |
| critical | 632 |
| instruction-hierarchy | 600 |
| prompt-injection | 600 |
| injecagent | 510 |
| jailbreak | 500 |
| safety-bypass | 500 |
| data-exfiltration | 317 |
| medium | 303 |
| deepset | 300 |
| prompt-injection-sample | 300 |
| prompt-injections | 300 |
| multilingual | 300 |
| multilingual-prompt-injection | 300 |
| translation | 300 |
| yanismiraoui-prompt-injections | 300 |
| jayavibhav-prompt-injection-safety | 300 |
| prompt-injection-safety-labeled | 300 |
| indirect-prompt-injection | 240 |
| untrusted-content | 240 |
| jailbreakbench | 200 |
| jbb-behaviors | 200 |
| jbb-harmful-behavior | 200 |
| direct-harm | 193 |
| others | 171 |
| 0 | 156 |
| jailbreak-prompt | 150 |
| advbench | 150 |
| harmful-behavior-goal | 150 |
| zou-et-al-2023 | 150 |
| agentic-risk | 150 |
| tool-abuse | 150 |
| gabrielchua-system-prompt-leakage | 150 |
| prompt-leakage | 150 |
| system-prompt | 150 |
| system-prompt-leakage-sample | 150 |
| persona | 150 |
| roleplay | 150 |

## Top Sources
| Source | Entries |
| --- | --- |
| uiuc-kang-lab/InjecAgent (Zhan et al., ACL 2024) | 510 |
| deepset/prompt-injections (HF) | 300 |
| yanismiraoui/prompt_injections (HF) | 300 |
| jayavibhav/prompt-injection-safety (HF, ~50k train/10k test) | 300 |
| JailbreakBench/JBB-Behaviors (NeurIPS 2024) | 200 |
| verazuo/jailbreak_llms (Shen et al., CCS 2024) | 150 |
| llm-attacks/llm-attacks (AdvBench) | 150 |
| gabrielchua/system-prompt-leakage (~355k rows, HF) | 150 |
| verazuo/jailbreak_llms - filtered for roleplay/persona pattern | 150 |
| sleeepeer/PoisonedRAG (USENIX Security 2025) - raw repo artifacts | 24 |
| N/A | 2 |
| Promptfoo ASCII/Base64 encoding examples | 1 |
| PayloadsAllTheThings Prompt Injection | 1 |
| PyRIT FlipAttack | 1 |
| Mixture of Encodings paper | 1 |
| Promptfoo long-context evaluation | 1 |
| NVIDIA Garak probes | 1 |
| Lost in the Middle / long-context evaluation | 1 |
| OWASP GenAI Security guidance | 1 |
