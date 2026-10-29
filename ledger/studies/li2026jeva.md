# li2026jeva — Jeva: System One Models from First Principles

- arXiv: 2610.18773v2 [cs.AI], 18 Oct 2026 (v1 13 Oct 2026; CC BY 4.0). Full text: fulltext/2610.18773.html and .txt (v2, fetched 2026-10-28).
- Authors: Qi Li, Xinchao Wang (National University of Singapore). Affiliation type: academic.
- Code and weights: no repository link for Jeva found in the text (reference notes link other projects' repositories).

## Task and data
Own-model paper proposing a decision-native architecture: a shared Qwen3.5-4B encoder embeds the request and each option independently; a one-block decision stack refines only the request state against immutable option memory; symmetric aggregation gives permutation-equivariant probabilities; a separate coverage gate gives an explicit null outcome; option vectors and layer projections are cacheable (Sections 1 and 3). Unified Choice, Noul and Score outputs. Evaluation (Section 4): Typed Decisions (LocalLLaMA, 2026; 2,000 test decisions = 600 Choice + 600 Noul + 800 Score), BANKING77 and MASSIVE with 8 or 16 candidates (answer-present and answer-withheld), three Mind2Web slices (K=16), 3,080 matched BANKING77 K=16 requests for null detection (588 absent), ToolRet-based diagnostic of 500 requests with K from 32 to 2,048, MLDR long-document sets for cache tests.

## Decision models and versions
Jeva-4B (Qwen3.5-4B, pooled width 2560, d=768, L=1, H=8, rank-64 LoRA 13.37M parameters). Baselines (Table 1): Jev-1.13.0, JevK5, InternDecision-4B/2B/0.8B, ReFlex-4B, SemIf-4B, KEV-4B (BF16 and FP32), CLM-8B, Valen-Preview-2B, Laya-English, Qwen3.5-4B and 2B label log-probability. Jev access route, run date and hardware are not stated. Baselines "retain their documented interfaces and native runtimes".

## Comparators and tuning-budget parity
Jeva is trained by a six-plus-stage curriculum of about 1M examples (typed decisions, intent selection, verification, reading, large-candidate retrieval, some teacher-blended probabilities) (App. C.1); baselines are used as released. In-domain exposure of Jeva to intent-selection data similar to BANKING77/MASSIVE is not ruled out by the text; no contamination check reported. For open-set evaluation JevK5 and CLM get an explicit None candidate while Jev, InternDecision and KEV answer an auxiliary Noul availability question (Section 4), so null comparisons rest on different interfaces.

## Reference labels
Public benchmark labels (BANKING77, MASSIVE, Mind2Web human annotations). Typed Decisions is a Hugging Face community dataset (LocalLLaMA/typed-decisions); this paper does not describe its labels, but the dataset card (see studies/grey_localllama_typed_decisions.md) records synthetic 2026 scenarios with gold = mean of three samples from a teacher endpoint. Ledger codes Typed Decisions rows llm_teacher and new.

## n, sampling, intervals
Point estimates; no bootstrap or seeds across training runs. Latency figure boxes show median and IQR (Figure 9). Permutation tests: original, reversed and up to three seeded random orders on 600 Choice examples.

## Test-set exposure
Public benchmarks released 2020 to 2023 (BANKING77, MASSIVE, Mind2Web; ledger public-pre-2026) and a synthetic 2026 community dataset (Typed Decisions; ledger new); exposure of the training curriculum to the public benchmarks is not ruled out.

## Cost and latency
Local synchronized H200 timing. ToolRet K=2048: p50 94.459 s to 12.040 s with length-aware batching (7.85x), accuracy 69.88% vs JevK5 67.47% at 28 s. Cache: MLDR p50 2,102.0 ms to 75.1 ms at full option reuse; Typed Decisions p50 93.1 ms to 46.6 ms (Section 4.3 and 4.4). Jev's own latency is not reported.

## Calibration
Noul Brier against soft targets (Jev 0.0342, Jeva 0.0184, Table 2). No ECE or reliability diagram; temperature scaling mentioned only as complementary related work. Learned coverage temperature and threshold in the null gate.

## Cascade
None.

## Robustness tests
Candidate permutations (Jev flip rate 17.00%, all-order accuracy 66.67%, mean TV 0.0858; Jeva 0.00%, 76.67%), nested candidate-set expansion (83 queries, K 32 to 2,048; Jeva correct at every size on 58 queries vs 48 for JevK5 and 7 for CLM), null detection (Section 4.2). No language or option-name test.

## Limitations (paper's own)
No limitations section. Statements: unsupported slices excluded from accuracy; proofs assume exact arithmetic; individual-text length limits remain (Section 3.4).
