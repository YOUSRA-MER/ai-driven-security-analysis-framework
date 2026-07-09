# Attack Dataset Index

Excel-backed attack prompt dataset converted from `source/AI_Redteam_Sources_and_Prompts_extended.xlsx`.
The adjacent `knowledge_dataset` was not modified.

Total entries: 1678
Excel prompt rows read: 2244
Exact duplicate prompt rows skipped within category: 566
Category files: 11
Source catalog records: 53

## Per-File Counts
| File | Entries |
| --- | --- |
| prompt_injection.json | 300 |
| jailbreak.json | 395 |
| prompt_leakage.json | 150 |
| indirect_prompt_injection.json | 240 |
| rag_poisoning.json | 16 |
| roleplay.json | 148 |
| encoding.json | 5 |
| multilingual.json | 149 |
| context_overflow.json | 5 |
| data_exfiltration.json | 120 |
| tool_abuse.json | 150 |

## Skipped Duplicate Rows
| Category | Skipped Rows |
| --- | --- |
| prompt_injection | 300 |
| jailbreak | 105 |
| prompt_leakage | 0 |
| indirect_prompt_injection | 0 |
| rag_poisoning | 8 |
| roleplay | 2 |
| encoding | 0 |
| multilingual | 151 |
| context_overflow | 0 |
| data_exfiltration | 0 |
| tool_abuse | 0 |

## Severity Distribution
| Severity | Entries |
| --- | --- |
| critical | 582 |
| high | 940 |
| low | 2 |
| medium | 154 |

## Top Tags
| Tag | Entries |
| --- | --- |
| excel-import | 1678 |
| high | 940 |
| critical | 582 |
| injecagent | 510 |
| hf | 449 |
| jailbreak | 395 |
| safety-bypass | 395 |
| data-exfiltration | 317 |
| instruction-hierarchy | 300 |
| prompt-injection | 300 |
| indirect-prompt-injection | 240 |
| untrusted-content | 240 |
| direct-harm | 193 |
| others | 171 |
| medium | 154 |
| jailbreak-prompt | 150 |
| advbench | 150 |
| harmful-behavior-goal | 150 |
| zou-et-al-2023 | 150 |
| agentic-risk | 150 |
| tool-abuse | 150 |
| deepset | 150 |
| prompt-injection-sample | 150 |
| prompt-injections | 150 |
| jayavibhav-prompt-injection-safety | 150 |
| prompt-injection-safety-labeled | 150 |
| gabrielchua-system-prompt-leakage | 150 |
| prompt-leakage | 150 |
| system-prompt | 150 |
| system-prompt-leakage-sample | 150 |
| multilingual | 149 |
| multilingual-prompt-injection | 149 |
| translation | 149 |
| yanismiraoui-prompt-injections | 149 |
| persona | 148 |
| roleplay | 148 |
| roleplay-persona-jailbreak | 148 |
| privacy | 128 |
| discord | 106 |
| website | 104 |

## Top Sources
| Source | Entries |
| --- | --- |
| uiuc-kang-lab/InjecAgent (Zhan et al., ACL 2024) | 510 |
| verazuo/jailbreak_llms (Shen et al., CCS 2024) | 150 |
| llm-attacks/llm-attacks (AdvBench) | 150 |
| deepset/prompt-injections (HF) | 150 |
| jayavibhav/prompt-injection-safety (HF, ~50k train/10k test) | 150 |
| gabrielchua/system-prompt-leakage (~355k rows, HF) | 150 |
| yanismiraoui/prompt_injections (HF) | 149 |
| verazuo/jailbreak_llms - filtered for roleplay/persona pattern | 148 |
| JailbreakBench/JBB-Behaviors (NeurIPS 2024) | 95 |
| sleeepeer/PoisonedRAG (USENIX Security 2025) - raw repo artifacts | 16 |
| N/A | 2 |
| Promptfoo ASCII/Base64 encoding examples | 1 |
| PayloadsAllTheThings Prompt Injection | 1 |
| PyRIT FlipAttack | 1 |
| Mixture of Encodings paper | 1 |
| Promptfoo long-context evaluation | 1 |
| NVIDIA Garak probes | 1 |
| Lost in the Middle / long-context evaluation | 1 |
| OWASP GenAI Security guidance | 1 |
