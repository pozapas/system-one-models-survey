# chen2026company — The Company a Question Keeps: Auditing Open Jev-Style Models for Retrieval

- arXiv: 2610.14631v1 [cs.IR], 10 Oct 2026, license CC BY-NC-ND 4.0 (header). Full text: fulltext/2610.14631.html and .txt.
- Author: Jianbo Chen, Tsinghua University, Beijing (header). Affiliation type: academic. Single author.
- Code and data: "The artifact is not yet publicly available; redistribution of source data is subject to the applicable licenses" (Limitations). "Pinned code and checkpoint revisions in artifact" (references note). code_available = no. Revision hashes are therefore not in the text.

## Task and data
Audit of request independence, evidence dependence and eligibility dependence in open Jev-style models for retrieval decisions (Sections 1, 3). Data: TREC DL2019/2020 passage qrels with MS MARCO top-1000 text; 92 eligible queries (39 in 2019, 53 in 2020) with two unique grade-2/3 and four grade-0 passages; each query gives three states of three passages with zero, one or two positive passages; 276 states in total (117 in 2019, 159 in 2020); grade 1 and unjudged passages not used (Section 4.1). Each state gives three target judgments (828 paired judgments per checkpoint). Scenario balance is constructed, positive prevalence one third. SciFact probe: 20 claims, two models, 60 pairs each (Section 5.4). Reference labels: TREC qrel grades from the track assessors; coded human_single. Grade-0 labels "may be imperfect" (Limitations).

## Models and versions
Seven open trained checkpoints: Laya-typed (ModernBERT, ~421M) and Laya-general, Kev-0.8B, Kev-4B (Qwen3.5-4B-Base with adapter and pointer head) and Kev-9B, Bespoke Nimble-9B (Qwen3.5-9B adapter, BF16 merged, T = 1.0), Von 1.2 (option-isolated, shipped input-conditioned calibration) (Section 4.3). "We use fixed checkpoint revisions and the released inference engines", but hashes are not in the text. PyTorch 2.8.0, Transformers 5.17.0; main runs on an H800 GPU with BF16 autocast as the CUDA default, FP32 for the precision diagnostic (Sections 4.3, 5.2). The hosted Jev service is not tested ("The hosted Jev service and official-adapter end-to-end behavior are untested", Limitations). Model selection by repository visibility, so the sample is not representative (Limitations). The extended checkpoint group and several analyses are exploratory (Sections 4.3, 7).

## Comparators and tuning
Ordinary-LLM controls: Qwen3.5-4B, Qwen3.5-9B, Llama-3.1-8B-Instruct, Qwen2.5-1.5B-Instruct (exploratory), BF16, batch size one, three computations (independent question compilation, schema-visible probe, constrained joint generation), initial and explicit-output realizations (Section 4.4). Native models use shipped temperatures (Kev 2.40605, Nimble T = 1.0 unfitted, Laya shipped, Von shipped). Thresholds 0.5, 0.7, 0.9 fixed before inference. Training data, base models, prompts, precision and calibration differ between systems, so cross-model comparisons are confounded (Limitations).

## Intervals
95% query-bootstrap intervals (5,000 resamples, seed 20260928, years kept separate), no multiplicity adjustment; zero-event cells carry a one-sided 95% binomial upper bound (7.4% in 2019, 5.5% in 2020 for query-level events) (Section 4.5).

## Results (Tables 2 to 4; order is 2019/2020)
- Nimble-9B request-set strict flips 9.1 [6.0, 12.8] / 8.0 [5.2, 11.3]; action change 21.4 [15.4, 28.2] / 18.9 [12.6, 25.8]; correct-action change 0.0 [-6.0, 6.0] / +8.2 [3.8, 12.6] points; field masking removes all 70 request-set flips (Section 5.1).
- All Kev scales, Laya-typed and Von have zero observed request-set flips; Laya-general 0.6 / 0.8 (BF16), none in FP32 (Table 2, Section 5.2).
- State addition flips: Laya-typed 13.1 / 15.1, Kev-4B 5.1 / 5.2, Nimble 4.0 / 2.5; document isolation flips more in every checkpoint (Laya-typed 27.4 / 25.4) (Section 5.1).
- Singleton accuracy (Table 4): Kev-9B 78.1 / 85.3 (Brier 0.157 / 0.111); Kev-4B 75.2 / 80.1; Nimble-9B 74.1 / 77.1; Laya-typed 66.1 / 64.8 against the all-No rate of 66.7; Kev-0.8B 51.0 / 53.2; Von 37.0 / 40.9; controls Qwen3.5-9B 76.4 / 83.6, Qwen3.5-4B 67.5 / 73.4, Llama-3.1-8B 34.2 / 34.8, Qwen2.5-1.5B 70.4 / 68.8. Correct-action rates (overall): Kev-9B 65.0 / 76.1, Nimble-9B 58.1 / 62.3, Qwen3.5-9B control 70.9 / 75.5.
- Ordinary-LLM controls with the joint all-question request: flips 9.4 to 18.8% and action changes 21.4 to 49.1% (Section 5.5).
- Option and criteria sensitivity (Table 3): criteria reversal flips Nimble 14.5 / 15.1 and Kev-4B about 5%; Von none; separator-position diagnostic removes two eligibility flips on selected states (maximum A/B logit movement 0.592 to 1.14e-5).
- Calibration: Brier scores only (Table 4); no ECE, no recalibration beyond shipped temperatures. Von polarity correction removal raises accuracy 37.0 / 40.9 to 39.9 / 44.0.

## Cost, latency, cascade
No cost or latency (throughput comparison precluded by shared GPU workloads, Limitations). Selection or abstention rule at fixed thresholds is the closest analogue to a cascade; no escalation tested.

## Test-set exposure
TREC DL2019/2020 and MS MARCO are public before 2026; upstream training-data overlap unverified (Limitations). Constructed three-passage states and randomized orders are new.

## Limitations (Section 7)
One English corpus and two test years; constructed states and scenario mixture limit transfer to deployment; grade-0 labels may be imperfect; exact deduplication leaves possible semantic duplicates; repository visibility guided selection; cross-model differences confounded; intervals exclude training-run and model-family variation; artifact not public; cross-hardware invariance untested.
