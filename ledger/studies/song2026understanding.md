# song2026understanding — Understanding Jev-Style System One Models: Does Structure Reduce Selection Bias?

arXiv:2610.35826v2 [cs.CL], 27 Oct 2026 (first version 2026-10-26 per batch list). Full text: fulltext/2610.35826.html and .txt (arXiv HTML). Main paper (Secs 1-10) is an empirical order-robustness study; Appendices A-I are a survey of Jev-style implementations that reports no new measurements (Sec 8 end, Appendix list).

## Authors and affiliation
Mingyang Song, Mao Zheng, Zhiyuan Ma, Xinpeng Zhou; Foundation Model Department, Tencent, China (title block). Affiliation type: industry.

## Task and data
Multiple-choice selection with reordered options. Primary collection of 1,700 questions: 1,200 SuperGPQA (4-10 options, balanced over easy/middle/hard, 400 each) and 500 LEXam (125 each at 4, 8, 16, 32 options) (Sec 2.1). Scope datasets: MMLU-Pro, 300 questions (100 each at 8, 9, 10 options); GPQA Diamond, all 198 questions with four options (Sec 2.1). Every question is shown in eight presentations: original order, reversal, six random permutations; separately, eight repeated requests in the original order (Sec 2.3-2.4). Candidate identifiers move with content. Metrics: retention of initial successes, cumulative failure set, same-candidate agreement, changed-choice rate, plurality-vote gain, unanimity accuracy (Sec 2.4-2.7).

## Decision models evaluated
Hosted Jev 1.13 and Jev 1.14 (Sec 2.2; "Jev returns a choice through its native decision interface"). Twelve Jev reproductions: AutoTrust-JEV-9B, -27B, -35B, -27B-v1.1, -Gemma4-26B-A4B; StartLux-Decision-v1 at 0.8B, 2B, 4B, 9B, 27B, 35B-A3B; pplx-decider-v1.1-27b, each choosing the highest native probability without deliberation (Sec 2.2). Exact access dates for the hosted Jev runs are not stated.

## Comparators and tuning parity
Six generative LLMs: DeepSeek-V4.1-Flash-1017, Claude Sonnet 5.5, GPT-6.1-sol, Qwen3.8-Flash-Next, Gemini 3.8 Flash, GLM-5.3-Flash. They receive a serialized question and menu and return a selection; low reasoning effort (adaptive thinking at low effort for Claude Sonnet 5.5). Authors state "Their training, inference procedures, and interfaces are not matched" (Sec 2.2 and footnote 4, Sec 2.3). No tuning of any system; no debiasing method applied (Sec 9).

## Reference labels
Benchmark-supplied gold answer keys (SuperGPQA, LEXam, MMLU-Pro, GPQA Diamond). The paper does not describe how the keys were made. Coded human_adjudicated by precedent for expert benchmarks; treat as benchmark answer key.

## n and intervals
1,700 primary questions; 487 shared initial successes for the paired comparison; 300 and 198 for scope sets. Pointwise 95% percentile intervals from 2,000 benchmark-stratified bootstrap resamples of source groups, models and conditions preserved jointly; paired draws for differences (Sec 2.4, 2.6). Subgroup intervals are described as exploratory without multiplicity adjustment (Sec 8). Headline Jev percentages (27.3, 28.5, 84.9, 83.6) have no intervals; differences carry intervals.

## Test-data exposure
All four datasets are public pre-2026 benchmarks (SuperGPQA, LEXam, MMLU-Pro, GPQA); no contamination check is reported. The design measures presentation sensitivity, not absolute accuracy.

## Cost and latency
Not reported. Hardware or provider for Jev runs not reported.

## Calibration
No calibration analysis; the paper studies argmax choices, not probabilities.

## Cascade or escalation
None. Plurality voting over eight orders is tested as an aggregation remedy (Sec 5): gain 0.96 pp (Jev 1.13) and 1.01 pp (Jev 1.14) over mean single-presentation accuracy.

## Option-name, cardinality, robustness tests
This is the order-robustness study. Jev failure set expands 27.3% (1.13) and 28.5% (1.14) over 8 orders while accuracy range stays 1.47 and 1.53 pp (Sec 3.1-3.2). Jev loses 27.0-27.8% of initial successes under reordering versus 8.8-9.2% under repetition (Sec 3.4). Option count 4 to 32 examined (Sec 4.3-4.4; Jev changed-choice 20.8-21.6% at 4 options, 68.0-73.6% at 32). Differences by difficulty (hard SuperGPQA: Jev loses 53.9-54.6% of initial successes). Option labels were not independently manipulated (Sec 2.3). Language: English and legal (LEXam) tasks; language robustness not tested.

## Code and data availability
No repository, data or code link for this study found in the main text. Appendix I cites implementations of other projects only.

## Authors' limitations (Sec 8)
Behavioral differences do not identify a mechanism; training, inference and interfaces differ across models so no causal claim about decision heads; identifiers travel with content so position and ID effects are not separated; task mixture varies domain, language, difficulty and candidate count together; subgroup intervals exploratory; continued first failures do not predict growth under further requests.
