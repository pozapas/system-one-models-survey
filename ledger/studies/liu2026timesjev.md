# liu2026timesjev: TimesJev: Thinking Fast on Time Series with System 1 Sufficiency

arXiv:2610.26002v1 [cs.AI], 19 Oct 2026 (HTML title block; fulltext/2610.26002.html and .txt). Extractor batch V18.

## Authors and affiliation
Chenghao Liu, Wei Fan, Aniket Mahanti (University of Auckland); Jindong Han (Shandong University); Dongjie Wang (Northeast Normal University); Pengyang Wang (University of Macau); Hao Liu (HKUST Guangzhou) (title block). Affiliation type: academic. Code: https://github.com/coenliu/TimesJev (abstract footnote).

## Task and data
Time-series question answering with a fixed set of candidate answers, using four task groups of TSQA (Kong et al. 2025a): anomaly detection (Environment, AIOps, Healthcare, Web; 2 options), human activity classification (HAR; 6 classes), multiple-choice QA (Healthcare, Nature, Web, Other; 2 to 4 options) and true/false QA (same four domains) (§5.1, App. B Table 3). 13 dataset columns in total. "Overall" in Table 1 is the unweighted mean of the 13 column accuracies (checked: the 13 TimesJev + Decider-4B cells average 89.78). Table 3 lists train/test sizes 13,787/7,000 (anomaly, summed over 4 domains), 4,000/2,000 (HAR), 4,000/2,000 (MCQA), 3,703/2,000 (true/false), but the per-column accuracies imply much smaller denominators (anomaly and HAR cells are multiples of 0.2, i.e. n=500; MCQA healthcare 61.96 implies n=138 or 276), so the counts do not reconcile. One model is trained per anomaly domain (App. B).

## Decision models evaluated
- Decider-4B and Decider-2B, "the open-source System 1 models of the Jev family" (Marosi 2026, "Decider: one-pass typed decisions with calibrated probabilities") (§5.1). No version, revision or checkpoint hash is given. They read the answer from option probabilities with no decoding (Table 2 caption). Run zero-shot, LoRA fine-tuned on the TSQA training set, and as the frozen backbone of TimesJev.
- TimesJev (the paper's own method): a frozen Decider backbone plus a stochastic-gate feature selector (K=32 features from a 69-feature library, 240 for HAR) and a trained value-token MLP encoder (0.54M parameters). Trained once with seed 42, AdamW, 3 epochs, lr 1e-3, single NVIDIA RTX 5090 GPU (App. B.1, Table 4). The ablation table (Table 5) and K sweep (Fig. 6) use Decider-2B.
- Jev itself is not run; it is cited as the System 1 exemplar (TypeSafe AI 2026).

## Comparators and tuning-budget parity
General-purpose LLMs Qwen3.5-9B and Qwen3-8B (chain-of-thought), time-series reasoning models TimeOmni-1-7B, TS-Reasoner-7B, VeriTime-4B, and released Time-MQA checkpoints (Qwen-2.5-7B, Mistral-7B, Llama-3-8B, already fine-tuned on TSQA) (§5.1). Every non-Time-MQA baseline appears zero-shot and LoRA fine-tuned on the TSQA training set (Table 1). TimesJev's own training additionally selects lambda from {0.003, 0.01, 0.03, 0.1} "on held-out training data" and K=32 (App. B.1). The prompts, LoRA hyperparameters and tuning budget for the baselines are not described in the main text. Baselines' LoRA SFT is trained on the full TSQA training set while TimesJev uses a frozen backbone with 0.54M trained parameters, so budgets differ in kind. Decoding settings for the zero-shot reasoning models are not given.

## Reference labels
TSQA benchmark answer keys (Kong et al. 2025a). How those labels were built is not described in this paper; coded administrative_field (benchmark-supplied) with that caveat.

## n and sampling
Table 3 test sizes above. No intervals, no repeated seeds for TimesJev ("trained once with seed 42"), no significance tests. Differences of 1 to 3 points between LoRA baselines and TimesJev cannot be judged against sampling noise from the paper.

## Test-set exposure
TSQA is a public benchmark released in 2025 (Kong et al. 2025a); test items and answers predate 2026 and no contamination check is reported. Public-pre-2026.

## Cost and latency
Table 2: tokens, TFLOPs and latency (ms) per question. TimesJev + Decider-4B: about 0 tokens, 3.95 TFLOPs, 34.1 ms, overall 89.78. Decider-4B zero-shot 21.5 ms, LoRA 23.0 ms; Decider-2B 15.8 ms; Qwen3.5-9B zero-shot 12,528 ms (1,535 tokens), LoRA SFT 102 ms. Text claims 99% latency reduction (120 to 630 times) vs zero-shot reasoning models, 7 to 43 times faster than Time-MQA, 2 to 6 times faster than the LoRA baselines (§5.3). The abstract says 62.9% less inference time than the fine-tuned versions on average. Inference hardware and serving stack for the latency column are not stated (only the training GPU is given).

## Calibration
None reported. Answers are read from option probabilities but no ECE, Brier or reliability analysis appears.

## Cascade or escalation
None.

## Option-name, cardinality, language, robustness
Feature-value perturbation (Fig. 3): shuffling all feature values drives anomaly detection and classification to near chance; permuting the top feature drops sitting accuracy from 93.1% to 24.1% (§5.3). Ablations (Table 5, Decider-2B): without value tokens overall 48.84 vs 87.02 full; without STG selection 70.60; without compression 79.59; adding the raw series 85.51. K sweep: accuracy peaks at K=16 to 32 (Fig. 6). Option-name and option-order tests: none reported.

## Code and data
Code public (https://github.com/coenliu/TimesJev). TSQA is public.

## Authors' own limitations (Limitations section)
Restricted to fixed-candidate decisions (no forecasting or free-form output); features come from a fixed library with gates shared across inputs; no explanations generated.

## Notes for the grader
The headline claim of a "62%" or "69%" improvement over reasoning models compares TimesJev with zero-shot reasoning baselines (Table 1: best zero-shot Qwen3.5-9B 54.31, best zero-shot time-series reasoning model VeriTime-4B 56.77). Against LoRA-fine-tuned Qwen3.5-9B (86.91) the gap is 2.87 points. The abstract says "over 62%" while the introduction says "more than 69%"; the §5.2 text gives 65.4% and 58.3% for the two best zero-shot comparators.
