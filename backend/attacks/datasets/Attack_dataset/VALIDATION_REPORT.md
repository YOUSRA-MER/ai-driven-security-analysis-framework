# Attack Dataset Validation Report

Validation result: FAIL

## JSON Parse Validation
- Parsed category files: 11
- Parsed entries: 2244
- Result: PASS

## Required Field Completeness
- Required fields: id, name, category, owasp_llm_top_10, mitre_atlas, severity, attack_prompt, description, expected_behavior, success_criteria, tags, original_source, reference_url, metadata
- Field/order errors: 0
- Missing `{{ objective }}` placeholders after normalization: 2235
- Result: FAIL

## ID Uniqueness Across All Files
- Duplicate IDs: 0
- Result: PASS

## Duplicate Or Near-Duplicate Prompt Detection
- Exact duplicate normalized prompts: 770
- Near-duplicate prompt pairs at >=0.985 similarity: 28
- Result: WARN

## Invalid URL Detection
- Unique HTTP URLs checked: 18
- Invalid URLs: 1
- Result: FAIL

## Category And Severity Validation
- Invalid categories: []
- Invalid severities: []
- Empty prompts: 0
- Result: PASS

## Entry Count Validation
| Category | Entries |
| --- | --- |
| prompt_injection | 600 |
| jailbreak | 500 |
| prompt_leakage | 150 |
| indirect_prompt_injection | 240 |
| rag_poisoning | 24 |
| roleplay | 150 |
| encoding | 5 |
| multilingual | 300 |
| context_overflow | 5 |
| data_exfiltration | 120 |
| tool_abuse | 150 |

## Severity Distribution
| Severity | Entries |
| --- | --- |
| critical | 632 |
| high | 1307 |
| low | 2 |
| medium | 303 |

## URL Validation Details
| URL | Valid | Status/Error |
| --- | --- | --- |
| https://arxiv.org/abs/2307.03172 | True | 200 |
| https://arxiv.org/abs/2408.04811 | True | 200 |
| https://genai.owasp.org/ | False | The read operation timed out |
| https://github.com/JailbreakBench/jailbreakbench | True | 200 |
| https://github.com/NVIDIA/garak | True | 200 |
| https://github.com/llm-attacks/llm-attacks | True | 200 |
| https://github.com/microsoft/PyRIT | True | 200 |
| https://github.com/sleeepeer/PoisonedRAG | True | 200 |
| https://github.com/uiuc-kang-lab/InjecAgent | True | 200 |
| https://github.com/verazuo/jailbreak_llms | True | 200 |
| https://huggingface.co/datasets/deepset/prompt-injections | True | 200 |
| https://huggingface.co/datasets/gabrielchua/system-prompt-leakage | True | 200 |
| https://huggingface.co/datasets/jayavibhav/prompt-injection-safety | True | 200 |
| https://huggingface.co/datasets/yanismiraoui/prompt_injections | True | 200 |
| https://proceedings.iclr.cc/paper_files/paper/2025/file/904aac1c930c196f1c71533d4d9dc31a-Paper-Conference.pdf | True | 200 |
| https://swisskyrepo.github.io/PayloadsAllTheThings/Prompt%20Injection/ | True | 200 |
| https://www.anthropic.com/research/many-shot-jailbreaking | True | 200 |
| https://www.promptfoo.dev/docs/red-team/ | True | 200 |

## Near-Duplicate Samples
| ID A | ID B | Similarity |
| --- | --- | --- |
| atk-jailbreak-00005 | atk-jailbreak-00094 | 0.99 |
| atk-jailbreak-00152 | atk-jailbreak-00887 | 1.0 |
| atk-jailbreak-00152 | atk-jailbreak-01437 | 1.0 |
| atk-jailbreak-00165 | atk-jailbreak-00841 | 1.0 |
| atk-jailbreak-00165 | atk-jailbreak-01391 | 1.0 |
| atk-jailbreak-00214 | atk-jailbreak-00891 | 1.0 |
| atk-jailbreak-00214 | atk-jailbreak-01441 | 1.0 |
| atk-jailbreak-00220 | atk-jailbreak-00816 | 1.0 |
| atk-jailbreak-00220 | atk-jailbreak-01366 | 1.0 |
| atk-jailbreak-00221 | atk-jailbreak-00875 | 0.9925 |
| atk-jailbreak-00221 | atk-jailbreak-01425 | 0.9925 |
| atk-jailbreak-00300 | atk-jailbreak-00827 | 1.0 |
| atk-jailbreak-00300 | atk-jailbreak-01377 | 1.0 |
| atk-jailbreak-00811 | atk-jailbreak-01361 | 1.0 |
| atk-jailbreak-00812 | atk-jailbreak-01362 | 1.0 |
| atk-jailbreak-00813 | atk-jailbreak-01363 | 1.0 |
| atk-jailbreak-00814 | atk-jailbreak-01364 | 1.0 |
| atk-jailbreak-00815 | atk-jailbreak-01365 | 1.0 |
| atk-jailbreak-00816 | atk-jailbreak-01366 | 1.0 |
| atk-jailbreak-00817 | atk-jailbreak-01367 | 1.0 |
| atk-jailbreak-00818 | atk-jailbreak-01368 | 1.0 |
| atk-jailbreak-00819 | atk-jailbreak-01369 | 1.0 |
| atk-jailbreak-00820 | atk-jailbreak-01370 | 1.0 |
| atk-jailbreak-00821 | atk-jailbreak-01371 | 1.0 |
| atk-jailbreak-00822 | atk-jailbreak-01372 | 1.0 |

## Invalid URL Details
| URL | Error |
| --- | --- |
| https://genai.owasp.org/ | The read operation timed out |
