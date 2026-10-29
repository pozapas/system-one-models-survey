# wang2026jevlitemas — Jev-LiteMAS: Separating Decisions from Generation in Multi-Agent Workflows

arXiv:2610.21411v2 [cs.AI], 16 Oct 2026 (v2 as retrieved; first version 15 Oct 2026 per the batch list); CC BY 4.0. HTML from https://arxiv.org/html/2610.21411. Extractor: batch V15.

## Authors and affiliation
Kaixiang Wang, Zhaojiacheng Zhou, Jiong Lou, Jie Li, Shanghai Jiao Tong University, Shanghai, China (title page). Affiliation type: academic. The ACM template placeholders (DOI, conference) are unfilled in the title block.

## Task and data
A multi-agent LLM framework where Jev (a) picks the next expert from a legal candidate set after each artifact ("feedback-driven handoffs") and (b) screens intermediate artifacts as pass or escalate, escalating flagged ones to an LLM re-reviewer (Sections 3, 4). Four benchmarks: MATH, MBPP+ (EvalPlus pass@1), API-Bank (strict accuracy over 445 API-call prediction points from 150 episodes) and IDRBench I3 (integrable/non-integrable labels). 150 instances sampled from each benchmark by stratified random sampling with seed 42, same instances for all methods (Appendix C.3). Error-injection experiments use MATH and MBPP+ only, with DeepSeek-V4-Flash (Section 5.4).

## Decision model
"Jev (TypeSafe AI, 2026)"; no version string, no access or run dates, no API provider stated (Section 5.1). The routing and screening questions are posed to Jev with a candidate set or pass/escalate options. The extracted text does not list prompts for Jev in the main text.

## Comparators and tuning budget
Single-Agent, MetaGPT, AFlow, AgentNet, LAS as full-framework baselines; LLM Router (DeepSeek-V4-Flash), SLM Router (Qwen3-1.7B-Instruct) and Rule Router in the routing ablation; LLM Judge and SLM Judge versus Jev in screening; five protective baselines under attack (MAD, G-Safeguard, MAS-Shield, AgentMonitor, XG-Guard) (Sections 5.1, 5.3, 5.4). Whether baselines were re-implemented, reproduced or tuned is not stated in the main text; all use the same sampled instances and the same expert backbones. Tuning parity cannot be assessed from the text read.

## Reference labels
Native benchmark criteria: answer equivalence (MATH), test suites (MBPP+, API-Bank checker), dataset ground truth for IDRBench I3 (Appendix C.3). Screening TPR/FPR labels are produced by an injection procedure (errors injected into one randomly selected expert's artifact) or a clean run, coded synthetic.

## n, sampling and intervals
150 per benchmark; accuracy increments of 0.67 points. One run per configuration is implied; no confidence intervals, no repeated seeds are reported. Differences of 1 point or less are within one or two instances.

## Test-data exposure
MATH (2021), MBPP+ (2021 and 2023), API-Bank (2023) and IDRBench I3 (2025) are public. No contamination check. Coded public-pre-2026; the injected-error screening data is generated for the paper.

## Cost and latency
Generative-LLM tokens exclude Jev and SLM tokens (Table 2 caption; Section 5.1). Latency is wall-clock from local execution logs averaged over sampled instances (Appendix C.3). With GPT-5 experts, Jev adds 1.13 to 2.21 s per evaluation unit, 2.92% to 6.85% of end-to-end latency, and 1.56% to 2.14% of model cost; model cost per evaluation unit ranges $0.00664 to $0.01766 (Section 5.5; Figure 3). Dollar costs are the framework's per-task cost computed from recorded token usage and pricing.

## Calibration
None. Jev outputs are used as hard pass/escalate or argmax routing decisions; no probability quality is assessed. No threshold sweep is reported in the main text.

## Cascade or escalation
Jev screens each artifact; escalated artifacts go to an LLM reviewer. Under injected errors Jev-LiteMAS reaches ACC 94.00 (MATH) and 84.67 (MBPP+) with attack success 3.33% and 4.00%, using 14.6% and 21.7% fewer generative tokens than LLM-only judging, and 29.4% and 24.2% fewer on clean cases (Tables 3, 4; Section 5.4). Escalation fraction analysis is formal (Appendix C.2); the observed escalation fraction is not given in the text read.

## Option-name, cardinality, language and robustness tests
Content-blind router ablation (masking substantive expert outputs) lowers accuracy 18.00 points on IDRBench I3 and 9.02 on API-Bank (Table 2). Sensitivity to generative-LLM call budgets and heterogeneous expert backbones in Appendix B (not extracted). No option-order, renaming or language test.

## Code and data
No repository link found in the paper text or HTML links. Coded no.

## Authors' stated limitations
Routing over a predefined expert pool; no dynamic creation of experts; efficiency of re-review depends on artifact quality distribution (Appendix A). Limitations are in an appendix, not in the conclusion.
