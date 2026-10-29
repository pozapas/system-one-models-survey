# li2026jevcascade

arXiv 2610.07716 (v2, 10 Oct 2026; first version 2026-10-06). "JevCascade: Readout Stability and Inference-Time Compute Allocation for Prefill-Only Decision Models". Full text: fulltext/2610.07716.html and .txt. Extractor batch V08.

**Authors and affiliation.** Ran Li and Lei Chen, Hong Kong University of Science and Technology (and HKUST Guangzhou for Chen) (title page). Academic.

**Task and data.** Classification and multiple choice with a restricted label menu. Sixteen datasets (ten core): intent detection (CLINC150, Banking77, MASSIVE, Snips and others), TREC question typing, MMLU, ARC, OBQA, CSQA, SciQ, AG News, DBpedia, emotion sets, SST-5 ordered scoring (Appendix A). Headline CLINC150 numbers use 500 test items (Section 1); the cascade uses 250 held-out CLINC150 items (Section 5.2); label-table repair uses 2,000 held-out items (Section 6). Datasets are public pre-2026 benchmarks.

**Decision models.** Six open System One families: kev (Palmer 2026; 0.8B, 4B, 9B), Open-Jev (Cai 2026; 2B, 9B; Qwen3.5 base plus pointer head), decider (0.8B, 2B), this-that, Mica-4B, Tiny-Jev (Appendix A, Section 4.1). No revision hashes. The hosted Jev is not evaluated; the title uses Jev as a family name. "Prefill-only decision model" defined in Section 3.1 (distribution over a menu in one forward pass). Contribution is a restriction predictor (restrict pass-1 probabilities to the menu, renormalize, read argmax) tested on 91 menu-only interventions.

**Comparators and parity.** Qwen3-4B-Instruct and Qwen3-8B generative models read option scores from the next-token distribution on the same 15-candidate menus (Section 4.3). Re-ask schemes (order marginalization, comparative re-ask) versus cascades at matched cost in 0.8B forward units (Section 5.2). Baselines for the predictor: probability-level estimator, accuracy-unchanged assumption, cross-source constant (Section 4.2). Thresholds for the cascade set on a training split; cascade threshold is a quantile of the confidence distribution (Sections 5.2, 6).

**Reference labels.** Benchmark gold labels (crowd-written intents, curated test sets); not adjudicated by the authors.

**n, sampling, intervals.** 500 test items for CLINC150 menu results, 250 for cascade comparison, 91 interventions, 35 context-free cells; sign test p=0.008 for avoidance menus; few confidence intervals reported; headline accuracies are point estimates (Sections 4 and 5).

**Exposure.** Public benchmarks (2018 to 2021 and earlier); no contamination check.

**Cost and latency.** Costs in 0.8B forward units (kev-9B costs 11 units); one call "one to two orders of magnitude cheaper than a same-scale generative language model" is cited from other papers (Section 1). Probe battery about ten GPU-minutes (Section 5.4). No hardware, no latency milliseconds.

**Calibration.** Expected calibration error of averaged order-permuted distribution falls from 0.09 (K=1) to 0.03 (K=2), a 67% reduction (Section 5.1); binning not stated (ledger codes calibration_quantity as none). Extra passes add little accuracy: pooled gain 1.2 points at K=16, MMLU 3.83 (Section 5.1). Probability-level variant of the predictor errs by 21.0 points vs 1.33 for ranking (Section 4.2).

**Cascade or escalation.** kev-0.8B to kev-4B on 250 CLINC150 items: 0.684 at 1.28 units vs 0.668 at 1.44 units for best re-ask; 0.760 at 2.40 units vs 0.652 at 2.00 units for order marginalization. Three-tier cascade reaches 9B accuracy at 1.0 to 6.3 units instead of 11; exceeds it on six of seven sources (Section 5.2, Table 2). kev gate beats random routing on five of five sources by 2.0 to 7.2 points; decider gate does not on every source (Section 5.2).

**Option-name, order, cardinality, robustness.** Menu size 2 to 30 and 150; correct label first drops self-selected 15-menu accuracy from 0.622 to 0.426, random 15-menu from 0.862 to 0.832; permutation flip rate under 6% at 150 labels (Section 4.4). Question wording moves Open-Jev-2B from 0.454 to 0.714 while shuffling changes at most 0.6 points; the comparative phrasing that costs Open-Jev-2B 9.4 points lifts kev-0.8B from 0.622 to 0.698 (Sections 4.4, 5.4). Hierarchical two-stage decision on TREC drops accuracy to 0.270 below flat 0.368 (Section 5.3). No language tests.

**Code and data.** https://github.com/rlisml/jev-cascade (Abstract). LLM tools used for editing and formatting (Appendix D).

**Authors' limitations.** Inference-time only; predictor exact for one family, tight for others; fixed positive residual of 2.5 to 4.9 points on emotion and product label spaces; per-item flip model is a postdiction with a small calibration set; presentation effects localized and reversible across families, training cause unreadable; deployment thresholds assume a retrieval front end with measurable recall (Limitations).
