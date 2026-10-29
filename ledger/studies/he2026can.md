# he2026can

arXiv 2610.35721v1 (cs.LG), 26 Oct 2026. "Can JEV Support Clinical Trial Criteria Assessment?" Authors Mengxian He, Ziyue Gao, Hao Wei, Minqing Zhang, Wu Yuan (The Chinese University of Hong Kong), Chun Li, Shunyi Zhang (Capital Medical University). Affiliation type: academic. (title block)

## Task and data
- Criterion-level clinical trial prescreening: given a patient record, a condition question and permitted labels (met, not_met, insufficient, not_applicable for TrialGPT only), assign a label per patient-condition pair. Retrospective; 3,135 standardized conditions across 734 jobs; primary test 2,048 conditions: TrialGPT 774 (four classes; 129 met, 366 not met, 243 insufficient, 36 n/a), MIMIC-III clinical-trial questions 322 (83 met, 97 not met, 142 insufficient), MIMIC-IV apixaban questions plus 89 derived LVEF conditions 952 (255, 667, 30). Confirmation partitions (423) in Appendix A.1. (Sec. 3.3, Tables 3-4)
- Reference labels: source-derived (TrialGPT annotations, largely synthetic patient summaries; MIMIC questions model-generated and human-reviewed); no clinician revision of labels; mapping rules fixed before predictions. MIMIC-IV insufficient labels (30) all come from the derived LVEF question; 526 of 529 MIMIC-III jobs hold one condition. (Sec. 2.1, 3.1-3.3)
- Public datasets (TrialGPT 2024, MIMIC-III/IV question resources 2025) pre-2026; no contamination check. Evaluated under zero data retention. (Abstract, Sec. 3.1)

## Decision model
- Jev via TypeSafe text Choice API, model version jev-1.14.0 (documentation accessed 16 Oct 2026; release date 14 Oct 2026); returns label, probability vector and a derived confidence; architecture inaccessible. Individual (Single) and shared-context (Batch) requests; one saved execution per mode. Exact run dates not stated. (Sec. 2.2, 2.4, refs [4-6])

## Comparators and tuning parity
- Qwen Flash (hosted alias qwen3.8-flash), strict JSON schema output of labels, no explanation, thinking off in primary runs (4,096-token completion limit); separate thinking on/off Batch comparison with 8,192 tokens. Same frozen patient text, assessment policies and label descriptions for both; Qwen additionally gets the format instruction; no prompt tuning described; no native probabilities for Qwen. Cost is an upper bound at list prices; latency at job level. (Sec. 2.3, 4.1, Table 6)

## Results
Macro-F1 (accuracy) Batch: TrialGPT Jev 0.652 [0.601, 0.702] vs Qwen 0.660 [0.602, 0.714]; MIMIC-III 0.768 [0.724, 0.811] vs 0.534 [0.489, 0.578] (paired diff +0.234, 95% CI 0.187 to 0.281); MIMIC-IV 0.807 [0.767, 0.846] vs 0.814 [0.774, 0.851]. Single: Jev 0.646, 0.771, 0.808; Qwen 0.645, 0.523, 0.732; MIMIC-IV Single paired diff +7.66 pp (1.82 to 13.39). Insufficient-class recall on MIMIC-III 56.3% vs 9.9%. Grouped bootstrap intervals; one execution per mode, so repeated-call variability is not separated from packaging effect. Failed requests: 1, 0/1, 4/0 for Jev. (Sec. 5.1, 5.2, Table 5, App. A.5)

## Cost and latency
Median complete-job time Batch: Jev 1.20 / 1.18 / 1.40 s vs Qwen 4.55 / 2.80 / 8.90 s on TrialGPT / MIMIC-III / MIMIC-IV; Jev Single TrialGPT 8.08 s, MIMIC-IV 18.30 s. Estimated upper-bound cost per 1,000 conditions Batch: Jev 0.0170 / 0.2045 / 0.0216 USD vs Qwen 0.0645 / 0.4314 / 0.0684; not cheaper in MIMIC-IV Single (0.2057 vs 0.1987). Totals 0.6306 vs 1.0481 USD over 6,270 planned outputs per model. Latency measured over provider APIs, different providers. (Sec. 5.4)

## Calibration
Native probability diagnostics on test: ECE (ten equal-width bins) Batch 0.0336 TrialGPT, 0.0958 MIMIC-III, 0.0346 MIMIC-IV; Single 0.0475, 0.0974, 0.0376; Brier (summed multiclass) 0.3756, 0.3611, 0.1556 Batch; high-probability (>=0.9) errors 20/196, 20/172, 19/560. No recalibration; authors say values do not establish clinical thresholds or a cross-model ranking. (App. A.4, Table 12)

## Cascade or escalation
None (Jev proposed as first-pass component with clinician verification).

## Robustness
Single vs Batch packaging; Qwen thinking on/off; no option-name, cardinality or language tests. (Sec. 5.2, 5.3)

## Code and data
No code availability statement; datasets are public or credentialed (MIMIC via PhysioNet). Prompts and output contracts in App. A.8. (App. A)

## Authors' limitations
Retrospective evaluation against source-derived labels without clinician revision; one saved execution per mode; MIMIC-III has little context sharing; MIMIC-IV insufficient class comes from one question family; Jev outputs must be verified against patient records; cost is an estimated upper bound; thinking comparison test-only. (Sec. 1, 3.3, 5.2, 5.4, 6)
