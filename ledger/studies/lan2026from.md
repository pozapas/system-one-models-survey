# Lan et al. 2026, From Detection to Decision: Calibration and Deferral for Prompt-Injection Detection

arXiv:2610.20907v1 [cs.CR], 14 Oct 2026, CC BY 4.0 (fulltext/2610.20907.txt, header).

## Authors and affiliations

Qianlong Lan, Anuj Kaul, Vinothini Pandurangan, Indranil Sanyal, all eBay Inc. (title block). Affiliation type: industry.

## Task and data

Prompt-injection detection as an ALLOW, BLOCK, DEFER decision. Frozen confirmatory cohort of 47,611 examples (Table 1): TensorTrust 526 (all attacks), BIPIA 36,128 (53 benign, 36,075 attacks), NotInject 89 (all benign), PIDS-Bench v3 10,868 (5,488 benign, 5,380 attacks); 41,981 attacks and 5,630 benign overall (88.2% attack prevalence) (Section 3.1). Labels are the benchmark attack or benign labels (construction by benchmark, ledger label type synthetic). Four benchmark families selected before the confirmatory run; development 1,000, gate-calibration 2,000, reviewer-calibration 1,000 and feasibility 1,000 examples are disjoint from the confirmatory set (Section 3.1). Benchmarks are public and mostly pre-2026 (PIDS-Bench IEEE Access 2026); the paper does not test contamination of the evaluated models. Pooled results characterise this mixture, not natural prevalence, and single-class subsets leave some metrics undefined (Sections 4.1, 6). No confidence intervals reported anywhere (Section 6).

## Decision model

Jev-native: "We query jev-latest through the official TypeSafe SDK using a fixed prompt-injection question and retain the native probability returned by the model" (Section 3.2). The resolved version and run dates are not reported; the blog reference was accessed 2026-10-01. No post-hoc calibration was applied to Jev, whereas Prompt Guard 2 is temperature scaled on target calibration data, which the authors flag as an asymmetry (Section 6).

## Comparators and tuning parity

Llama Prompt Guard 2 22M and 86M (raw and scalar temperature scaling fitted on the 2,000-example gate-calibration split; identical AUROC), and GPT-5.5 LLM judge with verbalized probability (prompt chosen from three on the 1,000-example development split, temperature 1.591 on reviewer-calibration split, FNR-first operating point 0.0527 with FPR 98.6% on calibration) (Section 3.2). The Jev prompt is one fixed question not tuned on development data; the comparators receive target-split calibration and prompt selection. Asymmetric by design and disclosed.

## Headline results

Table 2: AUROC Jev 0.871, LLM judge 0.897, PG2-86M 0.757, PG2-22M 0.714; Jev FNR at 0.5 is 0.649 (misses 64.9% of attacks), PG2 variants miss over 90%; TPR at 1% FPR is 0.125 for Jev (0.9% to 12.5% across methods). Table 3: Jev ECE 0.541, Brier 0.440, NLL 1.432, mean attack probability on false negatives 0.1630 (27,231 false negatives); PG2-86M calibrated 0.571, 0.439, 1.104. Dataset-level Jev ECE: BIPIA 0.660, NotInject 0.045, PIDS-Bench 0.167, TensorTrust 0.204 (Table 6). Table 4: escalation to reach system FNR at most 1%: Jev 92.55% (FPR 45.84%), PG2-22M 92.45%, PG2-86M 91.89%; differences under one point are not interpreted.

## Calibration

10 equal-width bins ECE, Brier, NLL, mean probability on false negatives, reliability diagrams (Figure 2, Section 3.3). Scalar temperature scaling p = sigmoid(z/T) with T in [0.05, 20], fitted by NLL on the gate-calibration split, probabilities clipped to [1e-7, 1-1e-7] when logits are unavailable. Jev's native probabilities are not better calibrated than temperature-scaled PG2-86M on all metrics; a post-hoc calibration ablation for Jev is listed as missing.

## Cascade and escalation

Gate plus frozen LLM reviewer: gate probability mapped to ALLOW, DEFER, BLOCK intervals fitted on the gate-calibration split; deferred inputs go to the reviewer (Section 3.3, Figure 1). Reported crossings are descriptive test-set statistics, not deployed thresholds. Illustrative cost model (FP 1, FN 100, review 0.5) (Table 4, Section 6).

## Option-name, cardinality, language and robustness tests

None; one fixed question wording ("different wording or later model versions may yield different results", Section 6). Distribution shift is studied across dataset families.

## Cost and latency

Table 5: mean, p50, p95 latency per example: PG2-86M 43.8, 38.4, 69.7 ms; PG2-22M 45.8, 45.3, 76.1; Jev 190.9, 155.2, 301.7; LLM judge 3,890.2, 3,476.0, 6,603.9; includes network and provider overhead, no hardware normalisation (Section 4.4, Section 6). No Jev dollar cost reported.

## Code and data availability

https://github.com/lanqianlong/calibrated-decision-models with prediction files for 47,611 aligned records and scripts (Appendix C).

## Paper's own limitations

Single fixed Jev question and API version; verbalized LLM probabilities differ from token likelihoods; benchmark mixture not natural prevalence; single-class subsets; illustrative cost model; latency not hardware-controlled; no confidence intervals; adaptation asymmetry between PG2 and Jev; evaluation covers detection and routing, not end-to-end compromise (Section 6).
