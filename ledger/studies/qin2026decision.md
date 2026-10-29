# Qin et al. (2026), "Decision Readouts for Text-Mediated Video Anomaly Detection: An Exploratory Evaluation of Jev and Qwen"

## Identification
- arXiv 2609.34180v1 [cs.AI], 28 Sep 2026 (header); paper dated 27 September 2026. License arXiv perpetual non-exclusive. Self-described "Exploratory preprint, version 1".
- Authors: Xukui Qin, Youting Wang, Xinjie He, Ziyang Luo, Runxiong Wu, Yan-Syuan Chen, Zhongyao Chu; "Independent researchers" (byline). affiliation_type = independent.
- Code and data: "Code and machine-readable evaluation artifacts are not publicly released with this version" (Section 7). code_available = no. Generative AI (ChatGPT, Codex) used for revision and code (Section 7).

## Task and data
- Video anomaly detection decided from fixed video-derived text (cached LAVAD captions and temporal summaries), scoring a target frame anchor with a broad prompt: "Visible physical violence, dangerous incidents, or other clearly abnormal activity" (Section 3.2). Sparse development pilot: 40 videos (20 source groups per dataset), 400 anchors from UCF-Crime and XD-Violence (200 each; 10 positive UCF anchors in six groups, 37 positive XD anchors in ten groups), two text views (Sum = summary, Cap = ordered captions) over the same anchors; 4,000 requested predictions in the original five-backend pilot (Section 3.1, Abstract). "The 40 videos, not the 4,000 predictions, describe the primary sample size" (Section 1).
- Selection used video-level metadata, ordered by SHA-256 of a fixed seed, ten normal and ten anomalous videos per dataset, stride-16 anchors (Section 3.1, Appendix B). The labels are the datasets' temporal benchmark labels (UCF-Crime, XD-Violence) "not a new annotation study" (Section 2); provenance of the original annotations is not described, ledger codes human_adjudicated as benchmark gold. The broad prompt does not match each benchmark's annotation policy (Section 3.2), so probability scores measure agreement with benchmark labels, not verified calibration.
- Exposure: public datasets (2018 and 2020 era) and pretraining overlap "unknown" (Section 5). Author-cache captions from LAVAD (CVPR 2024). Coded public-pre-2026.

## Models and comparators
- Jev `jev-1.13.0` (Section 3.3): Choice (eleven-option rating distribution A = {0.0,...,1.0}, expectation and argmax computed) and Noul (event probability). Measured from a Mac client; run dates not stated, references accessed 2026-09-27.
- Comparators from one fixed local Qwen model: Qwen3-4B-Instruct-2507 (commit cdbee75f...), NF4 with FP16 compute, SDPA, batch one, 2,048-token limit, greedy generation, max 16 new tokens: short rating, ordinal full-answer likelihood expectation (normalized over the eleven legal answers), generated probability (Section 3.3). Historical LAVAD raw scores as a cached reference. A binary YES/NO likelihood control was implemented but "was not executed in this version" (Section 3.3).
- Tuning parity: same fixed evidence for all readouts; prompts differ only by the output contract; no tuning on test data; "the stronger local reference is identified descriptively after observation" (Section 4.1). Jev vs Qwen differ in weights, training and service, so no causal interface claim (Section 1).

## Statistics
- UCF primary metric ROC-AUC, XD primary standard AP, trapezoidal PR-AUC separate; Brier, NLL (log argument floored at 1e-15), ten-bin equal-width ECE descriptive (Section 3.4). Constants p = 0 and p = pi (evaluation prevalence, label-informed, descriptive) as no-information references.
- Intervals: paired source-group bootstrap, 2,000 replicates, seed 1729, 95% percentile; UCF has 1,997 valid replicates (single-class replicates excluded). 44 original contrasts plus additions, all exploratory, no family-wise control (Section 3.4).
- Missing outputs retained as null, never zero; matched-subset diagnostics reported separately (Section 3.5). Two post-start operational amendments (after requests 30 and 397) (Section 3.5). No calibration fit, no recalibration (post_hoc_calibration none).

## Validity and failures
- Choice returned 776 of 800 valid under the study's numerical policy (97.00%); 20 failed the unit-mass check (tolerance 1e-6 absolute), 4 the choice/maximum check; all 800 distributions on a hundredths grid, probability sums from 0.99 to 1.00 (Section 4.3). Noul and three Qwen readouts completed 800/800. Full-coverage Choice quality cells are unavailable, so Choice is not ranked (Table 1, Table 2).

## Cost and latency
- Client-observed successful-request service times, Jev from a Mac client, Qwen on an RTX 2080 SUPER, concurrency one each, not hardware-matched (Section 4.4, Table 5): Choice median 0.3181 s, Noul 0.3139 s, Qwen generated probability 0.5775 s, Qwen ordinal 1.3215 s, Qwen short 0.6379 s. API invoice unknown; the authors disclose a pilot-ledger reservation figure, which is the authors' own spend and is not extracted (Appendix G). No end-to-end video cost.

## Cascade, option-name, cardinality, robustness
- No cascade. No option-order or wording test; the authors note the executed Noul prompt requested an event probability rather than a direct Boolean, with direct yes/no wording "an untested sensitivity" (Section 5). Choice has eleven options; Noul binary.

## Authors' stated limitations (Section 5)
- Jev versus Qwen changes weights, training and service; summary versus captions changes evidence; missing YES/NO likelihood control; only 20 source groups per dataset and ten UCF positives; source-title grouping may miss near duplicates; pretraining overlap unknown; multiple exploratory comparisons and amendments; label mismatch under the broad prompt; offline and non-causal inputs; resource numbers concern scoring only.
