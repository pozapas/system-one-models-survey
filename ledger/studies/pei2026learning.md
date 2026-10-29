# pei2026learning — Learning to Formalize: Bridging Open-Ended Workloads and Fast Decision Models

arXiv:2610.36595v1 [cs.AI], 27 Oct 2026. Full text: fulltext/2610.36595.html and .txt. Application paper: a small generative "candidate formalizer" feeds a frozen decision model as selector.

## Authors and affiliation
Chengxuan Pei, Ziyao Wang (CUHK-Shenzhen), Teng Mei (University of Tokyo), Zhe Li (Kunlunxin Corporation) (title block). Affiliation type: mixed (academic and industry).

## Task and data
CALVIN environment D manipulation (language-conditioned, 34 tasks), privileged-state setting with paused physics (Sec 4.2, Limitations). Two evaluations. (1) Official-API motivating comparison on 200 CALVIN-D test episodes (Sec 4.3, Table 1). (2) Six-arm local comparison on all 1,011 official CALVIN-D validation annotations, excluded from SFT and checkpoint selection; at most 12 decisions and 360 simulator steps per episode, one format repair allowed, each annotation evaluated once per arm, four episodes concurrent (Sec 4.2).

## Decision models evaluated
Official TypeSafe Jev-1.13.0 API selecting among up to 34 generic motion choices, and with three pose candidates from DeepSeek V4 Flash (Sec 4.3). AutoTrust JEV-27B as frozen local selector (publisher's selection protocol and wide-label extension for up to 34 poses; no revision identifier given) (Sec 4.2). The contribution is the formalizer: Qwen3-4B and Qwen3-1.7B fully fine-tuned for two epochs on 36,453 DeepSeek-generated candidate lists from 4,612 episodes (Sec 4.2).

## Comparators and tuning parity
Base Qwen3-4B and Qwen3-1.7B generators with the same selector; JEV-27B with generic motions; Qwen3.5-27B direct generation of one pose. Authors state the generic and direct arms differ in candidate count, model family or output target, so they are deployment comparisons and not component ablations; the Jev API comparison changes both candidate source and count (Sec 4.1, 4.3, Limitations). The proposed formalizer is fine-tuned on in-domain teacher data while the baselines (generic, direct) are not tuned. Jev-1.13.0 API run date not given.

## Reference labels
CALVIN official single-task success oracle (task outcome) (Sec 4.2, 4.3).

## n and intervals
Counts only: 22/200, 93/200, 532/1011 and so on. No confidence intervals; the authors state repeated runs and dependence-aware uncertainty are needed because annotations may overlap (Sec 4.7, Limitations). A split of "first 200" versus "remaining 811" annotations is reported (Table 3).

## Test-data exposure
CALVIN (2022) is a public benchmark; validation annotations excluded from SFT and checkpoint selection; the first 200 had been inspected before (Table 3). No Jev-specific contamination analysis.

## Cost and latency
Mean decision latency 1.826 s (SFT 1.7B), 2.573 s (SFT 4B), 3.670 s (Qwen3.5-27B direct), 5.602 s (JEV-27B generic), including parsing, validation and repairs, excluding execution (Table 2). Request-level stage timing in Table 4. Resource use: GPU-hours and whole-board NVML energy (Table 5). Jev API latency not measured (Table 1 caption "Latency is unreported"). Hosted Jev median latency of 138 ms is cited from another paper (Sec 2.2). No monetary cost reported.

## Calibration
None. The selector uses argmax of its preference rule and "need not expose calibrated task-success probabilities" (Sec 3.3).

## Cascade or escalation
None as an escalation scheme. The formalizer plus frozen selector pipeline replaces a large generative backend; a one-time format repair is allowed (Sec 4.2).

## Option-name, cardinality, robustness tests
Candidate count K=3 for hybrids versus up to 34 for generic; not varied in a controlled sweep (Sec 4.7 lists candidate-count sweeps as future work). Per-task heterogeneity noted (e.g. drawer closing 0/29 for SFT pipelines). No option-order or language tests.

## Code and data availability
No code or data link given in the extracted text.

## Authors' limitations
Single dataset (CALVIN-D) with privileged state and paused physics; no transfer shown; each annotation evaluated once, overlap among annotations; candidate lists may omit useful actions or inherit teacher errors; generic and generated candidates differ in count and direct generation uses a different model family; API study has no latency; costs exclude teacher collection, SFT and CPU/system energy (Limitations).
