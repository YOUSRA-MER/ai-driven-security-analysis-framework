# Attack Dataset Validation Report

Validation result: PASS

## JSON Parse Validation
- Parsed category files: 11
- Parsed entries: 1678
- Result: PASS

## Required Field Completeness
- Required fields: id, name, category, owasp_llm_top_10, mitre_atlas, severity, attack_prompt, description, expected_behavior, success_criteria, tags, original_source, reference_url, metadata
- Field/order errors: 0
- Missing `{{ objective }}` placeholders after normalization: 0
- Result: PASS

## ID Uniqueness Across All Files
- Duplicate IDs: 0
- Result: PASS

## Duplicate Or Near-Duplicate Prompt Detection
- Exact duplicate normalized prompts: 0
- Near-duplicate prompt pairs at >=0.985 similarity: 5
- Result: PASS

## Invalid URL Detection
- Unique HTTP URLs checked: 18
- Invalid URLs: 0
- Result: PASS

## Category And Severity Validation
- Invalid categories: []
- Invalid severities: []
- Empty prompts: 0
- Result: PASS

## Entry Count Validation
| Category | Entries |
| --- | --- |
| prompt_injection | 300 |
| jailbreak | 395 |
| prompt_leakage | 150 |
| indirect_prompt_injection | 240 |
| rag_poisoning | 16 |
| roleplay | 148 |
| encoding | 5 |
| multilingual | 149 |
| context_overflow | 5 |
| data_exfiltration | 120 |
| tool_abuse | 150 |

## Severity Distribution
| Severity | Entries |
| --- | --- |
| critical | 582 |
| high | 940 |
| low | 2 |
| medium | 154 |

## URL Validation Details
| URL | Valid | Status/Error |
| --- | --- | --- |
| https://arxiv.org/abs/2307.03172 | True | 200 |
| https://arxiv.org/abs/2408.04811 | True | 200 |
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
| https://owasp.org/www-project-top-10-for-large-language-model-applications/ | True | 200 |
| https://proceedings.iclr.cc/paper_files/paper/2025/file/904aac1c930c196f1c71533d4d9dc31a-Paper-Conference.pdf | True | 200 |
| https://proceedings.neurips.cc/paper_files/paper/2024/file/ea456e232efb72d261715e33ce25f208-Paper-Conference.pdf | True | 200 |
| https://swisskyrepo.github.io/PayloadsAllTheThings/Prompt%20Injection/ | True | 200 |
| https://www.promptfoo.dev/docs/red-team/ | True | 200 |

## Near-Duplicate Samples
| ID A | ID B | Similarity |
| --- | --- | --- |
| atk-jailbreak-00005 | atk-jailbreak-00094 | 0.99 |
| atk-roleplay-02105 | atk-roleplay-02117 | 0.9997 |
| atk-roleplay-02105 | atk-roleplay-02187 | 0.996 |
| atk-roleplay-02117 | atk-roleplay-02187 | 0.9963 |
| atk-roleplay-02140 | atk-roleplay-02229 | 0.9997 |
