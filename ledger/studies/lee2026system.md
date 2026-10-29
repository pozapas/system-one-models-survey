# lee2026system — Can a System-One LLM Perform Knowledge Tracing When Few or No Learners Are Logged?

arXiv:2610.11135v1 [cs.CL], 8 Oct 2026. HTML retrieved from https://arxiv.org/html/2610.11135 (fulltext/2610.11135.html and .txt).

## Authors and affiliation

Unggi Lee (Korea University Sejong Campus) and Haeun Park (Korea University; corresponding author) (title block). Affiliation type academic. Claude Code used for code and language editing (Use of Generative AI).

## Task and data

Knowledge tracing: predict whether a learner answers the next item correctly, posed to Jev as one typed yes/no question about a serialised learner state (last H=25 interactions), alone (Jev0-shot) or with 64 KC-matched solved examples and a similar-learner statistic from logged learners (JevKT) (Sec. 3, Fig. 1). Seven public datasets: ASSIST2009, NIPS34, XES3G5M, DBE-KT22, Algebra2005, Junyi 2018-19, ASSIST2017; learner-level 80/20 split (Sec. 4.1, App. A). Three cold-start settings on identical targets: P1 few training learners N in {8,16,32,64,128,256,all} (nested subsets, 5 seeds; first 50 interactions of held-out learners, 2,000 targets per dataset; N=0 means no target-platform data), P2 new learners (N=8, by position), P3 new items (20% of items removed, 3 seeds) (Sec. 4.1).

## Decision models evaluated

Jev, "jev-1.13-20260917 via OpenRouter" with H=25, k=64, n=20 (Sec. 4.1, App. B); the System-One endpoint; if input exceeds the context limit the number of shots is halved (3.4% of targets, mostly Algebra05) (App. B). Only one Jev version available; re-querying byte-identical requests 51 hours later gave Pearson .995 to .999 (App. G). Reader controls: GPT-4o-mini, Gemini-2.5-Flash-Lite, DeepSeek-V4-Flash behind TypeSafe's System-One adapter (probabilities written as text); JEV-9B (Qwen3.5-9B distilled from Jev); Laya (open-source, small encoder); Qwen3.5-9B variants A, B0, C (Table 2, Fig. 4). No access dates other than the snapshot string and the "about 51 hours" re-query.

## Comparators and tuning parity

Best of 28 pyKT deep KT models (eleven core plus 17), default hyperparameters, per-cell best model "selected on test, which favours DLKT" (Sec. 4.1, 5.5); a validation-tuned run (four strong models, eight configurations each) leaves deep KT below JevKT by +.070, +.042, +.030, +.010 at N=8, 16, 32, 64 (Sec. 5.5). System-Two LLM-KT: LOKT and Thinking-KT with Qwen3.5-9B (prompted, no training), CLST (trained, Mistral-7B LoRA, re-implemented on three datasets), LLM-KT (cited value only), BKT and PFA. Deep KT and CLST are trained on N learners; Jev0-shot uses no target data, JevKT uses N learners only as in-context evidence. The JevKT input recipe was selected by an exploration whose rule was fixed on the development split before evaluating test (Sec. 3, App. C).

## Reference labels

Observed learner correctness in public logs (task outcome).

## n, sampling, intervals

2,000 targets per dataset (14,000 per setting) over 5 seeds for P1; differences by one-sided paired learner-cluster bootstrap with Holm correction over datasets (Sec. 4.1, App. K). Table 1 reports point means without intervals; significance counts are given (Holm-significant on 7/7 datasets at N=8, 6/7 at N=16, 3/7 at N=32, 2/7 at N=64).

## Test-set exposure

Public datasets released before 2026; contamination analysis (ID-only difficulty questions with real vs fake IDs, relabelling IDs, continuation of public file rows) found no sign of memorisation; six synthetic datasets generated after the model release: JevKT still at or above best deep KT at N=8 (Sec. 5.5, App. L). Jev training data unknown.

## Cost and latency

JevKT 325 ms median latency in a single call, 72.23 predictions per second, $886 per 1M predictions; Jev0-shot $44; Thinking-KT (budget 2048, ten votes) $4,360 and 41.7 s per prediction; no-think $707; deep KT training at most $0.08 and under $1 per million predictions on one RTX 3090 at $0.22/h RunPod (September 2026) (Sec. 5.4, Table 4, App. J). API costs are OpenRouter prices paid by the authors (App. J); not carried into ledger beyond per-prediction cost.

## Calibration

15 equal-mass bins ECE and Brier on cold-start targets, no method recalibrated (Sec. 5.3, App. H, Table 13). Mean ECE Jev0-shot .084, Thinking-KT .253, LOKT .209; at N=8 JevKT ECE .070, Brier .182 vs best deep KT .076, .192. Jev shows mild underconfidence; vote-frequency readouts pile up at 0 and 1 (Fig. 5).

## Cascade or escalation

None. A crossover analysis: supervised KT catches up with JevKT between 64 and 128 learners (Table 1). Reasoning does not help Qwen3.5-9B (Thinking-KT never significantly better than no reasoning; Table 3).

## Option-name, order, language, robustness

Reader swaps and other-LLM adapter controls (Sec. 5.1, Table 2), paraphrased questions and state formats explored in App. C. No option-order shuffle reported for the yes/no question.

## Code and data availability

Anonymous repository https://anonymous.4open.science/r/jevkt-coldstart (code and result summaries); datasets public.

## Paper's own limitations

One closed System-One model; adapter reads probabilities written as text and may disadvantage the other LLMs; Jev training data unknown, contamination cannot be ruled out; results may change with future versions (only one version available); System-Two baselines on Qwen3.5-9B only; deep KT baselines use default hyperparameters in the main comparison; F1 threshold-sensitive on ASSIST17 (Limitations).
