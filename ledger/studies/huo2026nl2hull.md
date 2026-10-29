# huo2026nl2hull — NL2Hull: A Natural Language-Driven Constrained Ship Design Decision Framework

arXiv:2610.09896v1 [cs.AI], 7 Oct 2026. HTML retrieved from https://arxiv.org/html/2610.09896 (fulltext/2610.09896.html and .txt).

## Authors and affiliation

Wenhua Huo, Fenglei Han, Wangyuan Zhao, Jialin Wu, Jiayi Han, Harbin Engineering University, Harbin, P. R. China (title block). Affiliation type academic.

## Task and data

Natural-language ship-hull editing framed as typed discrete decisions (action count 1 to 3; region, operation, qualitative or explicit magnitude mode, one of six FFD levels, two Boolean preservation flags per action) that drive a NURBS free-form-deformation engine (Sec. 2.2). SDD Dataset: 30,000 structured FFD records on 12 hull models, 149,998 LLM-written Chinese descriptions (seven LLMs incl. Claude Opus 5, Kimi K3, GLM-5.3, Grok-4.7, DeepSeek-V4.1-Flash, GPT-5.6 Sol, MiMo-V2.6-Pro), cleaned to 134,558 records; splits 88,604 train, 22,758 validation, 23,196 test (Sec. 2.3). SDDBench: 5,000 test records selected by hull, description source, action count and explicit magnitude, with 43,496 typed questions (Sec. 2.3). End-to-end test: KVLCC2 hull, 300 experiments (400 requests) (Sec. 3.3.1). External check on public JevBench (48 Easy, 72 Original, 111 Hard tasks) (Sec. 3.2.2).

## Decision models evaluated

Chip (the authors' model): adapts the Kev decision interface, initialized from the open Kev-0.8B checkpoint (Qwen3.5-0.8B-Base), full SDD training partition, 2 epochs, rank-16 LoRA, lr 2e-5, one RTX A6000 (Sec. 2.2, App. B). Chip-2B and Chip-4B for scale ablation (Table 8). "Native JEV decision model" as a comparator, no version, no access dates, no API details (Sec. 3.2.1, Table 3); the paper cites Deusser et al. 2026 and "Evaluating and benchmarking the system one model jev". Kev-Base 0.8B (before adaptation) as the 0% reference (Table 9).

## Comparators and tuning parity

Three flagship LLMs (Claude Opus 5, GPT-5.6 Sol, DeepSeek V4.1 Flash) and three local small LLMs (Qwen3, Gemma 3, Llama 3.2) were prompted to return probability distributions in strict JSON ("prompt-constrained adaptation", Sec. 3.2.1, App. A.1), through Pi Agent non-interactively. JEV and Chip use typed interfaces directly. Chip is fine-tuned on 88,604 in-distribution records; JEV and the LLMs are not tuned for the task, so the comparison is domain-adapted model versus off-the-shelf comparators (the paper treats FFD exact match as joint decision quality and interface reliability, Sec. 3.2.1). Same SDDBench records, questions, candidate sets and metric procedure for all (Sec. 2.3).

## Reference labels

Labels are the structured action specifications sampled programmatically; the natural-language requests are LLM-generated (Sec. 2.3). Coded synthetic. No human annotation or human validation of descriptions is reported beyond rule-based format checks.

## n, sampling, intervals

43,496 questions (5,000 records) for SDDBench; question accuracy over successfully evaluated questions, FFD exact match over all 5,000 records (Table 3). No confidence intervals, one run per model, no seeds for ablations except nested subset sampling with a fixed seed (Sec. 3.4.3).

## Test-set exposure

SDDBench is newly built by the authors (2026); coded new. JevBench is a public benchmark (GitHub) whose comparison rows are "public reference results", not re-run by the authors; Chip was tested on it after ship-design training.

## Cost and latency

Mean per-request latency on SDDBench (ms): Chip 118.01 (p95 235.55), JEV 1510.33 (p95 2908.01; 4,322 completed requests), Claude Opus 5 7844.00, GPT-5.6 Sol 16009.20, DeepSeek V4.1 Flash 4630.63, Qwen3 25280.05, Gemma3 18407.59, Llama3.2 22589.78 (Table 6). Hardware for latency per system is not stated beyond Chip training on an RTX A6000 and "locally served" small models; API evaluators timed failed attempts too. Geometry processing added about 0.13 s per end-to-end experiment (Sec. 3.3.2). No dollar costs.

## Calibration

NLL, ECE (10 equal-width bins, max-probability confidence) and multiclass Brier on the expanded question set (Sec. 3.2.1, Eq. 8 to 10). Table 3: Chip ECE 0.0032, Brier 0.0551; JEV 0.0271, 0.1266. Kev-Base before adaptation ECE 0.1995 (Table 9). JevBench: Chip Original-tier ECE 0.1633, Brier 0.3489 (Table 4). No post-hoc recalibration reported.

## Cascade or escalation

None.

## Option-name, order, language, robustness

Requests are in Chinese (Sec. 2.3, App. A); no option-name or order tests. Scale ablation (0.8B, 2B, 4B) shows near-identical results (Table 8); data-size ablation 0% to 100% (Table 9). Failure analysis for small LLMs: 4,225, 2,359, 4,443 of 5,000 records rejected for key mismatches or missing answer objects (Sec. 4.2).

## Code and data availability

https://github.com/wenhuahuo/NL2Hull (code and dataset) (Abstract).

## Paper's own limitations

End-to-end constraint-handling flaw in multi-region edits (60% success, 39 of 45 constrained experiments violated a constraint; Sec. 4.1); no continuous magnitude or extent prediction; need for composition-aware constraint handling (Conclusion). JevBench Hard-tier accuracy below the strongest public references (Sec. 3.2.2).
