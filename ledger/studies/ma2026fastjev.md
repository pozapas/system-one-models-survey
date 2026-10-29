# ma2026fastjev — FastJEV: Understanding Redundancy for Compact JEV Inference

arXiv:2610.11379v1 [cs.CV], 8 Oct 2026. HTML retrieved from https://arxiv.org/html/2610.11379 (fulltext/2610.11379.html and .txt).

## Authors and affiliation

Jie Ma, Jie Gao, Yihang Liu, Zhike Qiu, Junle Li, Chongyi Zhuang, Jiayi Ji, Xiaoshuai Sun, Xiamen University (title block). Affiliation type academic.

## Task and data

Inference-efficiency study for multimodal candidate-scoring ("JEV") models: shared context anchoring (S), candidate prefix sharing in a trie (T) and decision-guided layer pruning (P), applied to candidate evaluation only, with no training (Sec. 3). Evaluated on AI2D test (3,088 questions), ScienceQA-IMG test (2,017), POPE (9,000), BLINK validation (1,901), ERQA (400), and a reconstructed LIBERO-10 offline set of 1,504 questions (188 frames from 20 evaluation episodes, eight question types per frame) whose labels come from simulator states and fixed trajectory rules; "the original question pool is unavailable" (Sec. 4.1). Layer ranking uses 32 OK-VQA inputs x 64 candidates, no labels (Sec. 4.1).

## Decision models evaluated

OmniJev v1.1 0.8B (24 layers), 2B (24), 4B (32) (Xu et al., 2026), "released" models with a visual encoder, language backbone and decision head scoring each candidate; binary questions use a sigmoid head at 0.5; LIBERO includes an abstention logit counted as an error (Sec. 3.1, 4.1). Not hosted TypeSafe Jev. No run dates.

## Comparators and tuning parity

Comparator is the same OmniJev v1.1 with the released inference path ("Original", which already computes the common prefix once); ablations S+P (without T), T+S+P (full FastJEV). The pruning mask is fixed per model on the unlabeled calibration set, so parity is by construction; no external baseline models are compared.

## Reference labels

Public benchmark answer keys (AI2D, ScienceQA, POPE, BLINK, ERQA; coded human_single) and simulator-derived rules for LIBERO (synthetic).

## n, sampling, intervals

Full evaluation splits (see Task and data). Timing: 64 fixed questions for three rounds on public sets, 20 frames on LIBERO; memory on 16 questions and ten frames (Sec. 4.1). The only intervals are episode-bootstrap intervals for LIBERO accuracy change at the default budget (2B -2.66 [-4.12, -1.27]; 4B -1.46 [-2.76, -0.07] percentage points; 2,000 resamples over 20 episodes, App. A.2). Main Table 1 has single point values.

## Test-set exposure

Five public benchmarks (2016 to 2025) with answer keys; no contamination check. LIBERO question set reconstructed by the authors. Coded public-pre-2026.

## Cost and latency

One NVIDIA L20 GPU, BF16, SDPA. At the default six-block budget, S+P speedups over Original are 1.053x to 1.258x in all 18 comparisons (3 sizes x 6 sets); full FastJEV (T+S+P) is faster only on POPE at the default budget and has geometric-mean speedups 0.938, 0.939, 0.953 at the larger budgets of Table 1 (i.e. slower), with LIBERO peak memory down 15.70%, 8.43%, 9.12% but higher latency (Sec. 4.2, 4.3, 4.6). T+S+P versus S+P on artificial 4B workloads: 2.736x speedup in one selected high-sharing condition (Sec. 4.5). Candidate depth reduced by 43.75% to 45.83% at the selected budgets.

## Calibration

None reported (accuracy and mean retention only; POPE F1 in App. A.2). Post-hoc calibration none.

## Cascade or escalation

None.

## Option-name, order, cardinality, robustness

Pruning budget sweeps: retention falls to 73.81% to 78.76% beyond 56% depth pruning; task sensitivity at larger budgets (Sec. 4.6, App. B); candidate overlap and branching structure analysis with artificial candidates (Sec. 4.5). No option-order or language tests.

## Code and data availability

Code: https://github.com/JieMaMagic/FastJEV (front matter).

## Paper's own limitations (App. C)

Reported limitations and future work in Appendix C (not summarised in the text read in detail); the main text states that execution benefit of prefix sharing depends on candidate overlap and branching and can increase latency (Sec. 4.7).
