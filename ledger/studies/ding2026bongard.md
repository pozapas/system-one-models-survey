# ding2026bongard

Bongard: Training Machine Intuition (An Open Encoder-Decoder Model for Probabilistic Judgment). arXiv 2609.39111v1 (cs.CL), 2026-09-30, technical report. Extractor: batch V05. Ledger rows L1854 to L1870.

## Authors and affiliation
Li Ding (corresponding), Haidi Jin, Chen Ji. AgentBull Pte Ltd (title block). Affiliation type: industry. Own-model paper: the authors build Bongard and compare it with hosted Jev. Appendix G: Li Ding designed, trained and evaluated; Jin and Ji processed training data.

## Task and data
Open-weight System One model (T5Gemma 2 4B-4B encoder-decoder, 7.51B parameters, 7.09B trainable, bilinear judgment head of 1.3M parameters; Sec. 3.2, Table 2) answering typed Choice, Noul and Score questions about a state in one pass. Three training stages: supervised judgments (about 51 h on one B200), JEPA-style alignment (23.4 h), sandbox outcome learning (about 11 h on a B300) (Sec. 4, 5). Evaluation: public System One benchmarks (DecisionBench 1.0 with 23,900 rows, JevBench v1.4, typed-decisions, behavior-benchmark, ImajevBench v2.0-lite; Table 8), a same-item comparison with Jev on 49,291 items from 24 public benchmarks (Table 12, Appendix F), Laya multilingual and long-document tests (Sec. 7.3), backbone comparison on BoolQ, SocialIQA and WinoGrande (Sec. 7.4), a fair-chance test of 18 questions (Sec. 7.5), games (Sec. 7.7) and stage ablations (Table 10). Public benchmark items predate 2026. The paper reports no contamination or training-overlap audit between its stage-1 corpus (text, structured data, images; retrieval, derived and program-exact judgments, Sec. 4.1) and these public test sets, except that evaluation sets listed in Table 10 are "excluded from stage 3 training"; the extractor did not find a statement about stages 1 and 2.

## Decision models and versions
Bongard final model: the uniform average of the stage-3 checkpoints from rounds 8 to 15, served with fitted temperatures between 1.2 and 2.15 (Sec. 4.3, 6, 7); weights huggingface.co/AgentBull/bongard-mini, no commit hash given. Hosted Jev: "Jev 1.13" on third-party leaderboards (29 September 2026 snapshots, Table 8); in the authors' own same-item comparison Bongard's requests were sent unchanged to "Jev 1.13" through TypeSafe's API on 30 September 2026 (Sec. 7.2); no full version identifier (such as jev-1.13.0) is given. Other systems listed in leaderboards (Imajev-4B, Winnow-12B, DeepSeek V4.1 Flash, GPT-5.6 Luna, Laya checkpoints, Jeff-Gemma4-E2B) are taken from public leaderboards and reports, not re-run (Sec. 7).

## Comparators and tuning-budget parity
Same-item comparison with Jev uses identical states, instructions and candidates; most item sets come from Laya and Jeff benchmark code, others are full public splits, with one task sentence and the benchmark's own labels (Appendix F). Bongard is trained on a large corpus (including temperature fitting on external development sets, Sec. 6) while Jev is used zero-shot through its API; leaderboard comparisons rely on each leaderboard's settings. Bongard's authors state "Our API runs reproduce four independent Jev measurements within one point" (Sec. 7.2). Tuning-budget parity is not equal by construction (a trained system versus a vendor API).

## Reference labels
DecisionBench: labels as defined by the leaderboard (not described in this paper; ledger leaves reference_label_type empty). typed-decisions: gold is a teacher distribution ("the scores measure agreement with that teacher", Table 8 caption). Other same-item sets use each benchmark's own gold labels (Table 12). Fair-chance questions: analytic uniform target. Stage-1 corpus labels include program-exact synthetic solvers and filtered teacher distributions (Sec. 4.1).

## Sampling and intervals
Full public splits where stated ("Test and validation splits are complete", Table 12); Laya and Jeff item sets rebuilt from their code, some sub-sampled (for example 100 questions per language in MASSIVE, Sec. 7.3). No confidence intervals, seeds or repeated runs reported for the headline numbers; Jev answered each item once on 30 September 2026 (Sec. 7.2).

## Headline results
DecisionBench accuracy 78.05% (4th of 61; Imajev-4B 79.7%, Winnow-12B 76.7%, Jev 1.13 72.0%), ECE 0.063 versus Jev 0.128, NLL 0.72 versus 2.43 (Table 8, Sec. 7.1). typed-decisions: KL from teacher 0.256 versus Jev 1.442, Brier 0.132 versus 0.148, but top-label agreement 0.594 versus Jev 0.727. Same-item comparison: Bongard leads Jev on six benchmarks and is within three points on nine more; Jev leads by more than three points on 9 of 24, mostly JudgeBench (79.7 vs 55.4), prompt injection (75.9 vs 56.9) and toxicity (67.5 vs 53.5) (Sec. 7.2, 9, Table 12). Largest Bongard lead Banking77 93.1 vs 79.8 (Table 12). Fair-chance: mean KL from uniform 0.0009 for Bongard versus 0.769 for Jev (Sec. 7.5).

## Calibration
ECE on 15 bins on the leaderboard (Sec. 7.1). Serving temperatures fitted per primitive and per option count (Guo et al.), pool of external development sets, exact-probability questions and teacher-authored held-out questions (Sec. 6). Stage 3 plus temperatures: external development NLL 0.824 to 0.691, ECE 0.141 to 0.030 (Sec. 7.8). Stage 2 moved calibration towards overconfidence (ECE 0.12 to 0.15, Sec. 4.2.5). Jev overconfident on subjective-label sets: ECE 0.481 (support-ticket triage), 0.277 (Emotion), 0.179 (SST-5) versus 0.077, 0.032, 0.051 for Bongard (Sec. 7.2). Binning for the authors' own per-dataset ECE values is not stated.

## Cascade and escalation
None.

## Option-name, cardinality, language and robustness tests
Banking77 with 77 candidates (Sec. 7.2). Option order: Choice probabilities are not guaranteed order-invariant; training reshuffles options and an optional serving mode averages over cyclic rotations, off by default (Sec. 6). Stage-2 frozen panel of 14,606 re-expressions (restatements, logical complements, reordered options): accuracy 75.7% to 85.9% (Table 6). Languages: MASSIVE intent over 51 languages, Bongard mean 77.4% versus Laya multilingual 36.6% (Sec. 7.3); Jev on the same items 89.3% (Table 12). Long documents up to 30,000 tokens: 260 of 260 correct (Sec. 7.3). The authors also state Jev still leads on several judgment types (Sec. 9).

## Cost and latency
Bongard on one RTX PRO 6000 in BF16: median 36 ms on short JevBench items; mean 91 ms over DecisionBench rows; 32 questions about one state take 221 ms (5.2 times less than separate requests, 6.9 ms per decision); about 400,000 decisions per hour batched; at $1.79 per GPU hour about $4.4 per million decisions, against $40 for Jev and $127 for GPT-6 Luna (Sec. 7.6, Figure 6, costs taken from JevBench results). On an RTX 4090 the median is 116 ms per public item (Sec. 6). Jev latencies on the leaderboard include network time (Figure 6 caption). The training cost of Bongard (about 85 GPU hours across stages) is reported as time, not dollars (Sec. 5); this is an author-side training cost, not recorded as a ledger row.

## Code and data availability
Weights (Gemma terms of use) and runtime/server code (github.com/AgentBull/bongard, Apache 2.0) are open (Sec. 1). The training corpus is not stated to be released.

## Authors' stated limitations (Sec. 9)
Alignment terms isolated only by a short independent control showing a reshaped representation but not a decision gain; stage-3 progress tracked on a panel from its own environments and consequences in unseen environments not tested directly; verifying worked answers less reliable; Jev still leads on several kinds of judgment (typed-decisions top-label agreement, 9 of 24 same-item benchmarks); stage-1 and stage-2 encoders cannot focus on the question, and question-aware encoding can change an answer when other instructions join the request and limits the encoder cache.
