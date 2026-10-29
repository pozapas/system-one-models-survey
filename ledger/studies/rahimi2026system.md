# rahimi2026system — System One Models for Wireless Decision-Making: Applications and Performance Evaluation

arXiv:2610.04345v1 [eess.SP], 03 Oct 2026. HTML from https://arxiv.org/html/2610.04345 (fulltext/2610.04345.html and .txt).

## Authors and affiliation
Masoud Rahimi, S. M. Matin Alemohammad, Hamid Behroozi, Mahdi Nouri; Department of Electrical Engineering, Sharif University of Technology, Tehran, Iran (front matter). Affiliation type: academic.

## Task and data
Perspective-plus-evaluation paper. Two own simulation case studies (§IV): (I) receive-antenna selection, MIMO link with two transmit and eight candidate receive antennas, two selected; ten Rayleigh-fading realisations at SNR 0, 10, 20 dB give 30 channel-SNR instances with 28 admissible antenna pairs each; (II) intent-conditioned RAN slicing, 100 physical resource blocks split among eMBB, URLLC and mMTC in steps of 20 (21 actions), 30 instances (five service-intent profiles x six network-state variants), scored by a simplified numerical simulator. A third scenario (edge-service orchestration) is redrawn from the independent study of Li et al. [29] and is not a new measurement (§IV-D). Deel customer evaluation (70% to 97% approved-answer matching; 50% to 86% expense categorisation) is quoted from a TypeSafe LinkedIn post and flagged as customer-reported, not reproducible (§I).

## Decision models evaluated
Jev (hosted API), "Using Jev as a System-One implementation" (Abstract). No version string, model ID, or run date is given in the text read; the Jev blog is cited as accessed September 23, 2026. Comparators: "GPT-Sol" (a frontier LLM, exact identifier not given) and "Qwen" (exact checkpoint and size not given in the text read), both asked to return a single action identifier in JSON; classical baselines (exhaustive search, norm-based selection, correlation-based method CBM, random; load-aware allocation for slicing) (§IV-A, B, C).

## Comparators, tuning-budget parity
Same instances per task; Jev categorical interface vs LLMs instructed to return a JSON action id; input variants (with or without capacity-oriented guidance and derived features) are explored for LLMs and Jev (guided variant for LLMs includes guidance and features; Jev additionally has guidance-only and feature-assisted variants) (§IV-B). Optimal actions and evaluator scores withheld from inputs (§IV-A). The headline figures use the best-shown variants but the text does not state which variant the quoted numbers correspond to, nor how variants were chosen; classical methods are timed locally and are not hardware-matched.

## Reference labels
Exhaustive-search optimum (capacity) and exhaustive-enumeration utility reference computed by the authors' simulator (§IV-B, C). Coded task_outcome.

## n, sampling, intervals
30 instances per scenario; ten channel realisations per SNR. No confidence intervals or repeats stated for the headline quantities; Fig. 6 and 7 (from [29]) show interquartile ranges only (§IV-D). Figures 2-5 are plots; the quoted numbers appear in text.

## Test-data exposure
Newly generated simulation instances; no public benchmark.

## Cost, latency, hardware
Client-observed latency for successful API request excluding pacing and retry waits; therefore reflects serving infrastructure and network path (§IV-A). Receive-antenna selection: Jev 1.52 s, GPT-Sol 12.86 s, Qwen 3.62 s (about 8.5x and 2.4x faster). RAN slicing median: Jev 1.46 s, Qwen 5.13 s, GPT-Sol 5.29 s. No hardware, price or token cost reported.

## Calibration
No calibration analysis performed (calibration discussed only as an open challenge, §II, §V-B).

## Cascade
No cascade experiment; a hybrid System-One/System-Two architecture is proposed qualitatively (§I, §VI).

## Robustness
No option-name, order, cardinality or language tests. Input-variant ablation (guidance and features) only for the antenna task.

## Code and data
No code or data release statement found in the text read.

## Paper's own limitations
No limitations section. Stated caveats in text: "the present results cover only one task and should not be interpreted as a general limitation of the model class" (§IV-B); vendor-reported speedups are "vendor-reported and workload dependent" (§I); the edge-service results come from [29] and "remain separate" (§IV-D).

## Notes for the grader
Model identities for the comparators and the Jev version are not given. Only 30 instances per scenario with no intervals. The scenario III numbers are secondary and are not entered in the ledger.
