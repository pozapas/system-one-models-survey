# rafe2026estimating — Estimating Uncoded Crash Factors with Tabular Foundation and System One Models: Kumo Tabular and Jev

arXiv:2610.10321v1 [stat.AP], 7 Oct 2026 (TIST template). HTML retrieved from https://arxiv.org/html/2610.10321 (fulltext/2610.10321.html and .txt). The paper declares no relationship with TypeSafe or NVIDIA.

## Authors and affiliation

Amir Rafe and Subasish Das, Texas State University, San Marcos, USA. Affiliation type academic.

## Task and data

Joint estimation of crash factors documented in police narratives vs coded fields for 5,601,890 Texas CRIS crashes 2017 to 2025 (narrative population U = 5,018,080 geolocated crashes with narrative over 40 characters) (Sec. 3). Design: Phase 0 Kumo Tabular reads the coded record of every crash (97 features); Phase 1 Jev reads narratives in wave 1 (simple random sample of 150,000) and wave 2 (79,510 drawn with recorded probabilities by discordance score); Phase 2 human tier of 400 narratives (2,309 consensus judgments of two or three coders); a second human check tier of 600 narratives (427 read by a specialist) drawn with recorded probabilities (Table 2, Sec. 4). Fifteen factors (nine with a coded field). Estimator: multiwave predict-then-debias (Kluger and Bates), Eq. 1 to 3.

## Decision models evaluated

Narrative reader Jev "pinned to version jev-1.13.0, with a typed schema of 27 questions and its gating rule" (Sec. 4.1), a closed commercial model with undisclosed training data (Conclusion). Table reader Kumo Tabular, "pinned to weight revision v1.0.0 and run in its small size with a context of 60,000 labeled rows" (Sec. 4.1); its target is the probability that Jev flags the factor, fitted to flags at p >= 0.5 and cross-fitted in 5 folds. Both are in-context, one-forward-pass probabilistic readers; Kumo Tabular is a tabular foundation model rather than a language decision model and is treated as a secondary subject. No run dates for Jev are stated in the text read.

## Comparators and tuning parity

Table-reader evaluation (Sec. 4.2, 5.2, Table 6): Kumo Tabular (small, medium, large), TabICLv2, TabPFN 3 and 3.5 (evaluation license), CatBoost on the same context and on the whole pool, plus a booster tuned per target; same contexts, test rows and labels. Kumo Tabular small "was fixed as the production reader before this comparison" (Sec. 5.2). For Jev itself there is no comparator; Jev's probabilities are recalibrated on the human tier (Platt, isotonic, or identity, selected by held-out Brier over 50 half-splits) (Sec. 4.1, App. B).

## Reference labels

Human consensus of two or three coders who did not see model output (phase-2 tier); second check tier read by two specialists (Cohen's kappa 0.93, 98% agreement) and a careful reader without crash background who answered yes 59% as often (Sec. 4.1). Coded human_adjudicated for Jev rows. The table-reader AUC rows are scored against Jev's own flags (llm_teacher), and also against human labels in text (Kumo 0.913 vs 0.874 booster over fifteen factors).

## n, sampling, intervals

Wave 1 n = 150,000 (simple random), wave 2 n = 79,510 (Poisson draw, probabilities 0.0057 to 0.68), human tier 400 narratives, check tier 600. Intervals add the design half-width and the spread of 200 narrative-cluster recalibration refits (Sec. 4.1, App. B). Paired bootstrap for table-reader AUC comparisons, unadjusted for multiplicity (Sec. 5.2). Many factors have under 30 human positives (Table B.2).

## Test-set exposure

Private administrative data under a TxDOT agreement, not redistributable (Data availability); narratives were sent to the narrative reader after identifier replacement. Coded private.

## Cost and latency

Reading every narrative in U about 773 dollars at the vendor's price; planning cost of a human-coded narrative 0.60 dollars (six judgments at ten cents) (Sec. 5.2, Fig. 8 caption). Kumo Tabular small 8,393 rows per second, 12.1 GB GPU, 11 minutes for one pass over 5,601,890 crashes vs TabPFN 3.5 556 rows per second, 2.8 hours; one A100 GPU (Table 6, Sec. 5.2). Jev latency not reported.

## Calibration

Recalibration of Jev's probabilities against the human tier is central: the identity map was ineligible for every factor except vehicle defects "because the narrative reader's probabilities overstate the human rate" (App. B). Held-out Brier (x1000) raw to chosen: alcohol 4.56 to 2.71, phone use 0.88 to 0.29, unbelted 3.59 to 0.14, wrong-way 9.57 to 5.92, vehicle defect 17.26 to 17.26 (identity) (Table B.2). Coded-field shift eta = 2.00 (95% interval 0.37 to 4.50). Estimates move by at most 8% under alternate maps except vehicle defects (21% lower). No ECE for Jev. Kumo Tabular calibration error 0.002 and slope 1.01 against Jev flags (Table 6).

## Cascade or escalation

No decision-model cascade; a budget allocation result: one more round of 400 human judgments cuts RMS relative half-width from 22.0 to 16.2 percent vs 21.2 for reading every narrative (Sec. 5.2). The table-reader-ranked re-read list shows lift 7 to 58 at the top one percent (Fig. 7).

## Option-name, order, language, robustness

None for Jev beyond version pinning and a gating rule. Kumo Tabular sizes and context grid reported in Table 6 and App. D.

## Code and data availability

Code, question schemas, coder guide, design summaries and aggregate tables: https://github.com/pozapas/kumo-jev-crash-records. Raw crash records not redistributable.

## Paper's own limitations (Conclusion)

Closed narrative reader with undisclosed training data, pinned to one version and audited against two human tiers; model-based extrapolation to crashes lacking a usable narrative; single state; recalibration tier dominates uncertainty (Sec. 6).
