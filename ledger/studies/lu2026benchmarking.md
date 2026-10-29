# lu2026benchmarking — Benchmarking candidate coverage and rejection policy transfer in typed decision models

arXiv:2610.03387, first submitted 2026-10-02 (batch CSV); text read is v2 ([cs.AI], 06 Oct 2026) from https://arxiv.org/html/2610.03387 (fulltext/2610.03387.html and .txt). v1 was not read.

## Authors and affiliation
Jiawen Lu, Tongtong Wu; Monash University (front matter). Affiliation type: academic.

## Task and data
Rejection (explicit "none" / missing-answer detection) by typed decision models when the reference answer is omitted from the candidate set. Data: AG News (4 classes), DBpedia-14, Emotion (6), TREC (6, supplemental), CLINC150 intents plus out-of-scope (OOS) queries (§2.2, Table 1). Study contains 1,456 classification texts and 750 CLINC queries; test texts per task 120/420/166/150 (AG/DBpedia/Emotion/TREC) and 400 CLINC (300 in-scope + 100 OOS); calibration 80/280/120/120/350 (Table 1). Policy transfer: Laya/Jev none-score thresholds calibrated on 80 pairs per source task, applied to other targets at k = 2 candidates (§3.1, §5.4). CLINC: artificial omission (300 matched queries, k = 5), natural BM25 retrieval misses at k = 2, 5, 10, and public OOS (100 queries) (§2.3, §3.2). Interface controls reuse 120 classification texts (10 calibration, 20 test per task) (§2.2). An earlier 889-text discovery study (300 calibration, 589 test) is reported separately and is exploratory (App. E).

## Decision models evaluated
Laya (software 0.3.21, pinned English checkpoint, model card accessed 2026-10-05), Jev ("pinned and verified as jev-1.13.0", hosted Choice API, API reference accessed 2026-10-02, up to 64 questions per call, four workers), and Qwen2.5-7B-Instruct (greedy BF16, 2,048-token input cap, 32-token output cap, checkpoint accessed 2026-10-03) as a discrete-choice LLM baseline; a BM25 scope gate is a non-neural reference (§5.2, Table 3, Refs 2, 3, 16, 18). The authors state "one checkpoint or version per model" (§4.1). Qwen is not a probabilistic typed model (supplies discrete choices only) (§5.2).

## Comparators, tuning-budget parity
Equal calibration budget: every target is evaluated with both the source policy and a target recalibration at the same 80-pair label budget (§1, §3.1). Models share frozen request files and the same candidate sets and descriptions (§5.2). Qwen uses a fixed instruction; no prompt tuning described. Threshold chosen to maximise detection subject to false rejection at most 5% on calibration data (§5.4).

## Reference labels
Public dataset labels of each source (class or intent labels, CLINC OOS label); coverage defined by the public reference label (§2.1). Annotation processes of the datasets are not described in the paper. Coded administrative_field. The authors note overlapping descriptions can leave acceptable alternatives after label removal (§4.1).

## n, sampling, intervals
Seeded frozen samples (seeds 20261003/6/7/8) with approximately balanced classes (20 calibration and 30 test texts per class). 2,000 percentile text-bootstrap draws (base seed 20261005); intervals marginal and unadjusted; transfer rows share texts; Wilson intervals for one-observation-per-text rates (§5.4). Natural-miss estimates at k = 10 rest on five cases (§3.2).

## Test-data exposure
Public datasets all pre-2026 (AG News, DBpedia, Emotion, TREC, CLINC150). "model pretraining overlap is unknown" (§4.1). Source revisions pinned by commit hash (App. A.1). No contamination test.

## Cost, latency, hardware
Not measured as an outcome ("Tokens, dates and costs are operational metadata, not intrinsic measurements", App.). No cost or latency comparison.

## Calibration
Score quality: AUROC and Brier of the none score on balanced artificial pairs; reliability curves with ten equal-width bins; DBpedia k = 13: Jev none-score AUROC 0.987 (0.980-0.994), Brier 0.068 (0.056-0.081); Laya 0.865 (0.845-0.885), 0.191 (0.169-0.213) (§3.3, §5.3). Post-hoc step is a calibrated rejection threshold per configuration (not temperature scaling).

## Cascade
None (BM25 retrieval gate is a reference only).

## Robustness
Neutral identifiers (option_000 keys) versus natural names, and task-aligned versus legacy NONE wording, with 20 test texts per task; Qwen detection falls 20.0 points on AG News k = 3 and 30.6 on DBpedia k = 13 under neutral keys; Laya detection rises 25.0 points on Emotion k = 5 under task-aligned NONE wording; Jev and Qwen show zero detection change there (§3.4). Candidate-count variation k = 2 to 13 (§3.2, §3.3). English only.

## Code and data
https://github.com/luckykevvv/Decision_Model_Benchmark: code, frozen requests, recorded predictions and scoring outputs; recorded predictions allow offline recomputation (§5.6, Abstract).

## Paper's own limitations (§4.1)
Coverage follows public reference labels; approximately balanced samples differ from deployment frequencies; rare-class support limited; pretraining overlap unknown; one checkpoint per model; task changes combine distribution and rubric shifts; no population risk guarantee from the empirical calibration constraint; discovery stage exploratory, later protocol frozen but not preregistered (App. E); Qwen recorded 1,369 interface failures in core cases (§5.2).

## Notes for the grader
Qwen interface failures counted in native-rate denominators. Headline Jev rate (69.3% false rejection on Emotion) comes from transferring a DBpedia-calibrated threshold, not from Jev's native none option.
