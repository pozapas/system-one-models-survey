# Chouhan and Perry 2026, Verdict: Encode Once, Decide Many

arXiv:2610.20778v1 [cs.CL], 14 Oct 2026, arXiv perpetual non-exclusive licence (fulltext/2610.20778.txt, header). Own-model paper that also measures Laya and Jev itself.

## Authors and affiliations

Avdhesh Singh Chouhan and Jack Perry, both LEC AI (title block). Affiliation type: industry.

## Task and data

Typed-decisions benchmark (LocalLLaMA 2026 benchmark card): four synthetic workflows (agent-trace observability, customer service, invoice processing, security incidents), 1,200 training cases (6,000 decisions), 400 test cases (2,000 decisions), five typed questions per case. Gold labels are the mean of three samples from a teacher of roughly 4B-class capability, so scores measure agreement with the teacher; the card gives a "perfect scenario understanding" ceiling of 0.704, teacher self-agreement 0.735 and calls about 0.75 saturation (Section 4). Reference label type: llm_teacher. Standard benchmarks RACE (test), BoolQ (validation) and MultiRC (validation), all public pre-2026 (Section 7). Jev scored on 387 of 400 typed-decisions cases (13 lost to transient provider errors) and loses 2.1 to 3.4% of standard-benchmark items to API errors; a common-subset check shows the loss favours no system (Section 2, Table 1, Appendix C). Intervals: case-cluster bootstrap with 10,000 resamples, seed standard deviations; the authors disclose that the research process was adaptive rather than test-blind (live test accuracy was visible in training logs, a learning-rate ablation was re-checked after a test result) (Limitations, Selection and testing).

## Decision models

Verdict-MQ (own): ModernBERT encoder reading a case and all its questions in one pass under a structured attention mask; 150M and 395M, ModernBERT-base/large or NLI-initialised, 3 to 5 seeds, RTX 4090 Laptop GPU, bf16 (Section 3, 4). Laya typed-decisions checkpoint (421M, released specialist, fine-tuned on the benchmark's training split) and Laya general checkpoint, measured by the authors (Section 4). Jev, measured by the authors through the alias typesafe-ai/jev on Vercel AI Gateway, 2026-09-25 to 2026-09-27, one call per case with five batched questions, zero-shot; the gateway returns no pinned semantic version, and the benchmark card's figure for TypeSafe Jev 1.13.0 (acc 0.727) is used as the closest version record (Appendix L). Card-only rows: Featherless Simple Jev, meraGPT Decider 1, ModernBERT-base and MiniLM per workflow (not re-run).

## Comparators and tuning parity

Specialists (Verdict-MQ, Laya typed-decisions checkpoint, per-question cross-encoder Verdict-CE) are fitted to the benchmark's training split, Jev is zero-shot, so the paper states they are not directly comparable. Hyperparameters are chosen on a 15% development split. Matched fine-tuned baseline on RACE, BoolQ and MultiRC has the same initialisation and epoch budget; baseline MultiRC varies widely across seeds, with one failed seed inflating the +9-point gap (Appendix C).

## Headline results

Table 1: Verdict-MQ 395M accuracy 0.801 ± 0.005, KL 0.080 ± 0.001, Brier 0.045 ± 0.001, ECE 0.156 ± 0.007; Laya specialist 0.767, KL 0.117, Brier 0.061, ECE 0.214; Jev (measured) accuracy 0.734, KL 0.829, TV 0.251, Brier 0.148, ECE 0.028; Jev (card) 0.727, KL 1.442. KL and Brier advantage over Laya has p at most 0.0002 on every seed, raw and temperature-matched (Table 2). Autonomy dial at 90% target: Verdict-MQ large 62 to 71% coverage vs Laya 56% (Table 3). Standard benchmarks (Table 5): Jev zero-shot RACE 93.3, BoolQ 91.3, MultiRC 90.0, above every fine-tuned encoder (Verdict-MQ 77.4, 76.2, 80.6; baseline 78.9, 81.0, 71.6). Jev API 2.0 to 2.1 s per call vs Verdict-MQ 8.5 to 50.9 ms per case locally, 35 to 205 times (Appendix C).

## Calibration

10-bin top-label ECE, Brier, KL, TV against soft gold (Table 1). Per-system temperature scaling fitted on half of the cases and scored on the other half (Section 5, Appendix B): both Laya and Verdict-MQ then calibrate well (ECE Laya 0.030, Verdict-MQ 0.017 to 0.032). The card recommends distribution metrics over ECE because an input-ignoring prior has the best ECE. Jev's low raw ECE 0.028 sits next to a very high KL 0.829, so ECE alone is uninformative. No temperature scaling of Jev is reported.

## Cascade and escalation

Held-out autonomy dial and risk-coverage (AURC): thresholds chosen on one half of cases for target accuracy 90, 95, 98% and applied to the other half; case-level auto-handling only 19 to 27% of cases (Laya 2.5%) (Section 5, Table 3, Appendix B). Jev not included.

## Option-name, cardinality, language and robustness tests

Option-order invariance by construction, verified numerically (permutation changes outputs by at most 5.4e-7 in fp32; bf16 realised bound 3.9e-3) (Section 3). No test of Jev's option-order sensitivity.

## Cost and latency

Table 4 packed vs per-question latency for Verdict-MQ; Jev latency accounting in Appendix C. Jev's own inference time is not isolated, only the gateway wall clock.

## Code and data availability

https://github.com/LEC-AI/verdict (Apache-2.0), scripts regenerate every table; per-run training logs not released (Appendix K, Limitations).

## Paper's own limitations

Small synthetic teacher-labelled benchmark; Verdict-MQ unstable on BoolQ; like-for-like comparison with an open system only on typed decisions; Jev is a closed, versioned, vendor-operated service that can change; adaptive research process (Limitations, Appendix L).
