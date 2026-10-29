# li2026agrijev — AgriJev: Efficient Agricultural Candidate Scoring with Multi-Scale Adapted Models

- arXiv: 2610.19478v1 [cs.CL], 14 Oct 2026. Full text: fulltext/2610.19478.html and .txt (fetched 2026-10-28).
- Author: Xuechen Li (University of Minnesota Twin Cities). Affiliation type: academic (single author).
- Code and weights: "Public hosting and final artifact-access arrangements remain incomplete" (Limitations); "Public redistribution of processed data or model artifacts is not claimed" (Ethical Considerations).

## Task and data
Own-model paper: AgriJev adapts Qwen3.5 (0.8B, 2B, 4B, 9B) with query/value LoRA to score candidates in one forward call (logits of locally assigned single-token candidate codes, softmax over the candidate set; Eq. 1, 2). Training: 41,724 records (29,482 entity-typing examples from AgriCHN and CROP, 12,242 native BBK English questions), 600-record development partition (3.3). Internal tests: 12,040 views over 1,505 groups (3,578 typing, 7,156 assertion, 1,306 event views, events silver) and a 1,173-record BIO subset (Table 1, 4.1). External: 18 prepared views, 17 in the main mean (AgriEval, CROP, CMMLU agronomy, C-Eval plant protection and veterinary, TMMLU+ agriculture, pathology, pharmacology, five SeedBench views, DEW-LogiQ, ORKG AgriNER, FAIRagro NER, Ag-valuate judged pairs); "These views are not 17 independently created datasets" (4.1).

## Decision models and versions
AgriJev 0.8B/2B/4B/9B. Comparators (4.2): original Qwen3.5 and matched Qwen3.5-SFT (both native answer generation, thinking off, greedy, 64 new tokens), AgriReason-4B, Akshara-7B, GLiClass, NLI, BGE, GLiClass-FT and RoBERTa-FT (supervised controls), and "cached Jev 1.13.0 choices" (hosted Jev, version string "Jev 1.13.0"; no call dates given in the main text). Hosted Jev timing: 22,162 new requests (5.3).

## Comparators and tuning-budget parity
Qwen3.5-SFT "shares the agricultural records, candidate permutations, adapter configuration, and update budget with the adapted family" (3.4). Jev is zero-shot with no agricultural adaptation and a different service contract; the paper states that interface similarity "does not imply reproducing Jev training" (Related Work). AgriJev and generators differ in prompt boundary and supervised response, "so their comparison does not isolate training normalization" (3.4). Single-run details in Appendix B (no seeds repeated). The training set includes BBK English questions whose released test partition is used for training only.

## Reference labels
Source answer keys of existing benchmarks (exam-style multiple choice, annotated entity mentions, judged pairs); event labels explicitly silver (extraction-derived, closed-world negatives, no expert adjudication) (Limitations). Ledger label type human_adjudicated for external views (benchmark answer keys, matching ledger.csv convention).

## n, sampling, intervals
Point estimates only; "These descriptive point estimates do not establish equivalence or statistical significance" (5.2). Mean weights 17 views equally. CROP original and reordered views share questions.

## Test-set exposure
External sources mix older public benchmarks (CMMLU 2023, C-Eval 2023, TMMLU+ 2024, SeedBench 2025, CROP 2024, Ag-valuate 2022) with 2026 sources (AgriEval, Yan et al. 2026; AgriCHN, 2026); ledger test_set_exposure is public-pre-2026 for single older views and unclear for the mean and 2026 views. No explicit contamination analysis; Qwen3.5 pretraining overlap unknown.

## Cost and latency
Fixed workload (32 BIO texts, 27 candidates, A100 40GB, batch 1, 96 timings per model): AgriJev medians 42.96, 41.90, 60.93, 93.80 ms (0.8B to 9B) vs original generation 124.04, 125.17, 161.79, 181.24 ms and SFT generation 189.16 ms at 9B (ratios 1.93 to 2.99). Hosted Jev client-side p50 388.53 to 397.24 ms, p95 446.08 to 469.79 ms per view across 22,162 requests; "not a hardware-matched speed comparison" (5.3).

## Calibration and cascade
"Equation 1 defines a candidate-relative distribution; normalization does not establish calibrated confidence"; independent calibration untested (Limitations). No cascade.

## Robustness tests
Paired CROP reordering view (excluded from the main mean), invalid-output accounting (generators produced 113 and 236 invalid codes among 808 SeedBench 3-2 decisions, kept in denominator), arithmetic upper bound if all invalid outputs were correct (original 71.02%, SFT 74.15% vs AgriJev 75.44%). No language-swap or option-name test beyond CROP reordering; benchmarks are mostly Chinese or Traditional Chinese with some English.

## Limitations (paper's own)
Typing and assertion reuse source annotations; BIO is internal; generated extraction labels and closed-world negatives remain silver; views differ in units; unseen-label transfer, independent calibration and unrestricted agricultural reasoning untested; 32-input timing workload not general; single-run details; public hosting incomplete (Limitations).
