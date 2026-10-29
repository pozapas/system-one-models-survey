# chen2026secjev — SecJev: Bringing Security Expertise to System One Decision Models

arXiv:2610.03073, first submitted 2026-10-02 (batch CSV); text read is v2 (cs.CR, 14 Oct 2026) from https://arxiv.org/html/2610.03073 (fulltext/2610.03073.html and .txt). v1 text was not read, so a v1/v2 difference cannot be excluded.

## Authors and affiliation
Zheng Chen, Fei Yu, Haohao Huang, Yang Li, Anlong Chen, Lei Chen. University of Electronic Science and Technology of China and the National Key Laboratory of Security Communication (front matter). Affiliation type: academic.

## Task and data
Security decisions as typed Boolean, choice and ordered questions. SecJev-Corpus: 170,185 questions from 115,324 scenes, eight sources and 14 tasks (CICIoT2023, ToN-IoT, Twins/Streamlet, VeReMi NextGen, ByzFL-based experiments, LANL authentication, AgentDojo, InjecAgent) (§4, Table 1). Splits: training 118,818, calibration 14,821, development 14,912, test 21,634 questions (Table 2). Group-aware splits (captures, source hosts, simulation runs, days, tool-response groups) (§4.2). Transfer tests: BIPIA-derived prompt-injection detection and IoT-23 malicious flows, 1,000 balanced binary test examples each, 4-shot (§5.4, Table 5). Also Kev general-decision (1,200 q) and general-transfer (656 q) suites (§6.3, Table 8).

## Decision models evaluated
SecJev family at 0.8B, 2B, 4B, 9B: rank-16 LoRA adapters plus Kev pointer head on Qwen3.5 backbones, trained three epochs (§3.3). 0.8B/4B/9B inherit released Kev adapters and heads ("official Kev"); the 2B starts from the authors' own general-decision model (§3.3). Exact Kev checkpoint revision hashes are not given in the text read; general suites use Kev upstream "decision-v7" and "transfer-v4" dataset revisions (App.). Baselines: Kev-0.8B/4B/9B (initialisation, general decision models), SecGen (answer-key one-token generative SFT with the same recipe at 0.8B and 4B), a candidate-sequence classifier at 0.8B, a direct-Qwen pointer (no Kev initialisation), and a training-majority baseline (§5.3, Table 3, 4). Jev itself is not evaluated.

## Comparators, tuning-budget parity
SecGen, classifier and direct-Qwen pointer use matching Qwen3.5 base, rank-16 LoRA, scene weighting, three epochs, development-based selection (§5.3, App. F); same security recipe. Kev-4B and Kev-9B comparators are the general initialisation without security training, so the comparison is specialised versus general, not budget-matched (they are labelled "Init." in Table 3). In the transfer test all three 4B models use the same 4-shot prompt with demonstrations from a disjoint pool (§5.4).

## Reference labels
Mixed. Source-annotation tasks use the original dataset labels (CICIoT2023, ToN-IoT, VeReMi, ByzFL controlled experiments) (administrative/dataset labels); policy tasks (Twins, LANL) have answers computed from a displayed rule and history, independently recomputed for 37,490 questions (synthetic procedure); AgentDojo/InjecAgent labels from the benchmarks. Two human reviewers checked 280 questions (20 per task): they agree on 261 (93.21%); on the 100 source-label questions they agree on 81 and both rate the visible evidence sufficient for 28 (§6.4). Coded administrative_field in the ledger because the headline macro mixes types.

## n, sampling, intervals
All 21,634 test questions scored; task-macro, micro and balanced-macro accuracy. Paired 95% intervals from 2,000 source-stratified bootstrap draws of whole groups (§5.1); intervals are reported for macro gains (e.g. 4B gain [18.59, 30.75] points, §5.2) but Table 3 itself shows no intervals. Single training run per model (no seeds reported in the text read).

## Test-data exposure
Source datasets are public and pre-2026 (CICIoT2023, ToN-IoT, LANL, VeReMi, AgentDojo, InjecAgent, BIPIA, IoT-23); no contamination check reported; the corpus itself is new and test records are released.

## Cost, latency, hardware
Timing on one RTX 3090, common BF16 backbone with FP32 adapters and heads, batch size one, medians over five passes of 100 short (<=512 tokens) and 100 long (2,048-8,192 tokens) requests (§5.3, Table 4). 0.8B: SecJev 79.2 ms short, 164.1 ms long, 2.56 GiB; SecGen 80.4 ms, 167.4 ms, 3.52 GiB. 4B: SecJev 109.1/578.8 ms, 10.18 GiB; SecGen 116.9/599.9 ms, 12.58 GiB. Kev-9B 169.1/861.0 ms, 17.11 GiB (Table 4). No dollar cost.

## Calibration
One scalar temperature per model fitted on the calibration split by NLL (§3.3). Table 9: ECE (15 equal-width bins) rises after scaling at every size (4B 1.84 -> 3.56; 9B 1.53 -> 2.48) while NLL falls; Brier worsens slightly. On the general suites the frozen security temperature improves NLL, Brier and ECE (§6.3).

## Cascade
None.

## Robustness
Paraphrase (1,400 pairs) and choice permutation (500 pairs): answer agreement 95.36-98.36% and 97.40-98.80% (§6.1, Table 6). Capability retention on Kev general suites within 0.5 points except 0.8B transfer (68.45 -> 66.01, interval [-4.73, -0.15]) (§6.3).

## Code and data
Adapters, decision heads, SecJev-Corpus and code released; https://github.com/UESTC1010/SecJev (front matter). Source-specific licence conditions retained (§4.2, Ethics).

## Paper's own limitations
Finite decisions over supplied observations; capture/experiment annotations can depend on information outside the input, so those tasks measure source-label prediction; no end-to-end deployment evaluation; uneven task difficulty; residual semantic overlap and transfer beyond tested sources open; human review shows source-label tasks have incomplete evidence (Limitations, §6.4).

## Notes for the grader
Near-ceiling policy tasks (99-100%) are rule application on displayed evidence. The headline "SecJev-0.8B beats Kev-9B by 20.51 points" compares a security-trained model with an untrained general Kev; Table 3 computes 90.34 vs 69.82 macro accuracy.
