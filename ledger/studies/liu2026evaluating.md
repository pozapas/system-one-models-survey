# liu2026evaluating — Evaluating System One Models for Agent Security Decisions: Reliability, Calibration, and Selective Automation

arXiv:2609.33401v3 [cs.CR], v3 dated 03 Oct 2026 (header; first version 2026-09-27 per the batch file). HTML retrieved 2026-10-28 from https://arxiv.org/html/2609.33401; saved as fulltext/2609.33401.html and .txt. Venue line: ACM FSE, July 12 to 16, 2027, Shenzhen (header). Numbers are from v3.

## Authors and affiliation

Yixuan Liu, TraceStone and Nanyang Technological University, Singapore (title block). Affiliation type: mixed (industry plus academic; single author).

## Task and data

Offline evaluation of model-based security checks for agentic software on three public benchmarks with original labels (§3.2): WAInjectBench-text (prompt injection in web-agent text; attack-derived segments with explicit instructions EI or without no-EI; test 1,612 inputs, twelve source families), R-Judge (interaction-record risk; test 236), AgentHarm (harmful vs benign requests; test 352 from 44 task groups, 176 harmful and 176 benign). Partitions (Table 2): R-Judge 100 development, 140 selection, 93 confirmation, 236 test; WAInjectBench 100, 966, 644, 1,612; AgentHarm 64 development and 352 test (no selection or confirmation, excluded from the policy experiment). Identical inputs grouped before splitting.

## Decision models evaluated

Table 1: Jev 1.13 (hosted API), Laya English checkpoint (PyTorch CPU FP32, 2,048-token budget), Decider approximately 2B (PyTorch MPS FP16), Bespoke Nimble approximately 9B (MLX GPU BF16; accepted budget 262,143 tokens; longest formatted input 2,155 tokens), with parent controls Decider parent Qwen3.5-2B-Base and Nimble parent Qwen3.5-9B scored by the same candidate-scoring procedure at temperature one. Adapted models retain released temperatures (§3.1). Jev is identified only as "Jev 1.13" and "Hosted API"; no patch version or run dates are stated (Table 1). Hugging Face revision hashes are not given in the text.

## Comparators and tuning-budget parity

General judges GPT-4.1 and Qwen3-8B (thinking disabled) with separate response configurations for classification and probability analyses; specialists ProtectAI DeBERTa v2, PIGuard, Prompt Guard 2 86M (injection only), WildGuard (AgentHarm); five reasoning judges GLM-5.3-Flash, GLM-5.3, DeepSeek-V4.1-Flash, Kimi-K2.6, Qwen3.8-27B (hosted APIs). Same complete input and safe/unsafe label definitions via adapters (§3.3). No fine-tuning or few-shot on test data; recalibration fitted on development inputs, thresholds on selection inputs, frozen for confirmation and test (§6.2). Budget asymmetries: the comparators are prompted or released as-is; the hosted APIs cannot be inspected for precision (Table 1 note).

## Reference labels

Original benchmark annotations of R-Judge, AgentHarm and WAInjectBench ("evaluate ... using their original labels", §1; "Each probability is evaluated against the unsafe event defined by its benchmark", §3.2). No new human adjudication. WAInjectBench labels attack-derived segments as unsafe even without direct commands (§3.2). Reference type recorded as administrative_field (benchmark-provided labels).

## n, sampling, intervals

95% CIs from 2,000 cluster-bootstrap resamples keeping related inputs together (R-Judge identical inputs, WAInjectBench source families, AgentHarm task variants); sign-randomization tests with Holm correction for paired FNR/FPR differences; McNemar secondary (§3.4). With twelve WAInjectBench source clusters, intervals are wide (Table 3: Jev Macro-F1 0.756 [0.452, 0.937]).

## Test-set exposure

Public benchmarks. "Public benchmarks may overlap training data" (§8). R-Judge (Yuan et al., 2024) and AgentHarm (Andriushchenko et al., 2025) predate 2026; WAInjectBench (Liu et al., 2026) is a 2026 benchmark per the citation. No contamination check.

## Cost and latency

None measured: "Deployment measurements also depend on the configuration: service routing, queueing, caching, and reasoning settings affect latency and API charges" (§7.1). No dollar or millisecond figures.

## Calibration

Brier, NLL, ECE with ten equal-width bins (also W5, W20 and Q10 quantile bins in Table 10), AUROC, AP, reliability diagrams (§5.1). Temperature scaling fitted on development inputs, T in [0.05, 20] by NLL (§5.1). Effects (Table 12): Jev WAInjectBench NLL 1.140 to 0.374, Brier 0.097 to 0.107; Jev AgentHarm NLL 0.481 to 2.163 with T = 0.05; "Temperature scaling improves test NLL in six of the twelve System One model and task combinations" (§5.4). Brier skill against a constant-probability reference is negative for Laya and Decider on WAInjectBench and for Laya, Decider and Nimble on R-Judge (Table 10). Jev assigns probability below 0.1 to 1,446 WAInjectBench inputs of which 133 (9.20%) are unsafe (§5.2).

## Cascade or escalation

Symmetric and independent allow/block/escalate policies (§6.1 to 6.4) and second-judge review (§6.6). Reported in terms of coverage, allowed fraction, misses and false blocks, not quality retained versus cost. The review rule would forward none of the high-confidence Jev misses on WAInjectBench (§6.6): "Each judge repeats over 80% of these errors for both models, and a rule accepting predictions at that confidence would send none of these misses for review."

## Option-name, cardinality, language and robustness tests

Not tested; English only; limits stated in §8 (adaptive attacks, other languages, multimodal inputs). Group analysis: EI versus no-EI WAInjectBench attack groups (§4.2, exploratory).

## Code and data availability

Experiment code, final predictions, benchmark partitions, configurations and analyses at https://github.com/yxsec/system-one-security-eval (Data Availability). OpenAI Codex assisted study design and code writing (Acknowledgments).

## Limitations stated by the authors

Threats to validity (§8): comparisons depend on prompts, answer-label order, context limits and reasoning settings; rare errors and few source clusters limit precision; EI/no-EI, threshold-sensitivity and cross-model error analyses are exploratory; threshold grid restricted; public benchmarks may overlap training data; adaptive attacks, other languages and multimodal inputs not covered; hosted model revisions can change between runs.
