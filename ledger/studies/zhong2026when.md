# zhong2026when

When the Right Answer Is Missing: An Arithmetic-Dependent Rejection Bottleneck in Jev. arXiv 2609.39496v1 (cs.LG), 2026-09-30. Extractor: batch V05. Ledger rows L1871 to L1882.

## Authors and affiliation
Jike Zhong (University of Southern California), Ming Li (University of Florida), Yuxiang Lai (Emory University); equal contribution (title block). Affiliation type: academic. Ethics statement: all inputs are synthetic records with no personal data.

## Task and data
Rejection when a menu holds no valid answer. Each case has a three-candidate menu plus an explicit rejection option (None); paired answer-present and answer-absent menus built from programmatic generators with exact ground truth (Sec. 3.1, 4.1). Main set: 100 problems each for two-operation arithmetic (a+b-c), numerical lookup and purchase totals (qp+s); contextual controls: 128 inventory problems and 64 each for refund policy and logical eligibility; further experiments on operation depth (50 paired cases per depth), magnitude bands (100 fresh cases per band), candidate distance (50 inventory cases), operator mixes (50 + 50 + 100), 15 pilot task families of 20 paired cases each, and label wording controls (Sec. 4.1 to 4.5). All data are newly generated, so training-data exposure is unlikely (synthetic; no real benchmark items).

## Decision model and version
Jev, evaluated through the hosted API; the text gives no version identifier (no jev-1.13.0 string, no run dates). The reference list cites TypeSafe documentation for "Jev 1.13 jaggedness", accessed September 25, 2026, which suggests but does not state the evaluated version (reference list). Three formulations: Menu Choice (A, B, C, None), candidate-level T/F Choice (categorical, ablation) and native Boolean (Noul type), with matched payloads differing only in the type field (Sec. 3.2).

## Comparators and tuning-budget parity
Qwen3.5-9B with reasoning as a generative control on the identical menus, scoring menus and joint verification prompts; token-limit failures account for 66 of 67 errors (Sec. 4.1, 4.3, Figure 5). The Jev interfaces are compared on identical menus. The threshold repair is tuned on separate development problems (20 per task/interface, search over thresholds 0 to 1 in steps of .01) and applied unchanged to disjoint evaluation sets (Sec. 5.2); Qwen is not threshold-tuned.

## Reference labels
Synthetic programmatic ground truth: the correct answer is computed deterministically (Sec. 3.1, 4.1).

## Sampling and intervals
Fixed-size generated sets (100 per main task, 20 to 80 for pilots). Named contrasts use 20,000 case-bootstrap resamples with seed 2026092901; paired 95% bootstrap intervals appear in Figure 3b and Figure 8b but the interval values are not given in the text. Pilot results report explicit denominators (Sec. 3.3). Several results come from 10 to 20 cases per cell (Table 1, Figure 6), so those are indicative only.

## Headline results
Menu Choice answer-present accuracy 99% versus correct rejection 7% on a+b-c (92-point paired gap); purchase totals 94% versus 24%; inventory 127/128 versus 14/128 (Sec. 4.2). Native Boolean answer-absent exact match 99% versus 27% for T/F Choice (Sec. 4.3). Supplying the computed result restores Menu rejection to 100% (Sec. 4.3). Rejection falls to 4% already at two operations (Sec. 4.4). Alternative labels ("Other", "None of the above") give 9% and 6% rejection (Sec. 4.5). Refund-policy and logical-eligibility controls reach 64/64 under both conditions, and lookup is near perfect, so the failure is task-dependent (Sec. 4.2). Threshold calibration at tau .03 raises arithmetic rejection from 7% to 79% while answer-present accuracy goes from 99% to 97%; purchase 24% to 79% with present accuracy 94% to 86% (Sec. 5.3, Table 2).

## Calibration
No ECE or Brier. The paper analyses score separation: arithmetic T/F AUC .985 despite 88/200 exact-match menus; purchase AUC .942 with 62/200 (Sec. 5.1). Post-hoc decision-threshold adjustment on saved scores, offline (no recalibration of the probabilities themselves) (Sec. 5.2).

## Cascade and escalation
None. Deterministic computation is mentioned as another remedy when structured inputs allow it (Sec. 6).

## Option-name, cardinality, language and robustness tests
Rejection label wording (NONE, Other, None of the above) and position of None (moved across four positions, recovering only 5, 0, 2 and 0 of 40 inventory failures) (Sec. 4.5). Candidate distance bands (Sec. 4.4). Magnitude and depth variation. English only.

## Cost and latency
No cost or latency reported. The threshold repair needs no additional inference (Sec. 5.2).

## Code and data availability
No code or data link in the text; programmatic generators are described, but no repository is cited (not found in the full text).

## Authors' stated limitations (Limitations section)
Hosted API only, with no access to weights or activations, so mechanisms are not identified. Future work lists real-world retrieval settings, cross-task calibration and training for reliable rejection (Sec. 6).
