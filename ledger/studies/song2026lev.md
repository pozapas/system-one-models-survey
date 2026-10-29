# song2026lev — LEV: Thinking Fast and Deep with Looped Decision Models

arXiv:2610.20951v1 [cs.AI], 14 Oct 2026 (title page). License CC BY 4.0. HTML from https://arxiv.org/html/2610.20951. Extractor: batch V15.

## Authors and affiliation
Dingjie Song (equal), Zhiling Yan (equal), Yuxuan Zhang, Lichao Sun (corresponding). Lehigh University; University of British Columbia and Vector Institute (title page). Affiliation type: academic.

## Task and data
The paper builds a new decision model, LEV, which reruns the layers of a natively looped language model and reads the options with a shared pointer head after every loop step; a small logistic-regression stopper picks the depth per question (Sections 4.2, 4.3). Evaluation panels (Table 5, Appendix B.2): Kev-Seen 1,464, Kev-Transfer 1,264, Kev-Skills 1,083 (tuning panels, development partitions of frozen Kev suites); LevBench 4,370 scored (own suite, frozen before any model read it) and Kev-Breadth 3,023 (14 datasets from five areas) as held-out panels; JevBench 231 public items (48 easy, 72 standard, 111 hard); a calibration partition of 1,148. The locked test uses the test partitions of LevBench (8,740 scored) and Kev-Breadth (3,031), "read once after the recipe and the stopper were fixed" (Section 7.2).

## Decision models evaluated
LEV-1.4B and LEV-2.6B (Ouro backbones, R=4 steps), LEV-3B (Nanbeige4.2-3B, 2 steps); LoRA rank 16, one epoch on 31,329 records (Section 5). Dense controls trained on the same data: Qwen3-1.7B-Base, Qwen3.5-2B-Base, Qwen3.5-4B-Base. Released references: Kev-0.8B, Kev-4B, and closed "Jev 1.13.0" (Section 5; Table 1). Jev is a reference row only: its per-item outcomes are "taken from the outcomes published in the JevBench repository" and, for Kev-Skills and Kev-Breadth, "from the reads published in the Kev repository" (Appendix B.5). Jev latency (652 ms) is "measured through the production API with the network included" (Table 1 footnote). No run date or API version string beyond "1.13.0". No LEV checkpoint revision is stated (Hugging Face collection linked on the title page).

## Comparators and tuning budget
Dense controls use "the same data and recipe" (Table 1); Kev references are "trained differently". The recipe and the stopper design were chosen on the three tuning panels, then the held-out panels and a locked test were read (Sections 5, 7.2). Cascades pair small and large dense models with a top-probability escalation rule; an escalated request pays for both models (Appendix F). No Jev cascade.

## Reference labels
Not described for JevBench in this paper (scored with JevBench's own code; Appendix B.5). Kev-Breadth uses public datasets; LevBench mixes new items of public training sources, generated reasoning families (programmatic labels) and eight never-trained public datasets (Appendix B.4). Coded `unclear` for JevBench and `synthetic` for LevBench and Kev-Breadth pooled rows.

## n, sampling and intervals
95% paired bootstrap intervals that resample groups of related questions (Section 5); exact McNemar test on JevBench (Appendix B.5). Headline JevBench accuracies in Table 1 are point values without intervals.

## Test-data exposure
LevBench items were screened against Train-31k, all Kev evaluation partitions, the public JevBench items and MMLU-Pro (Appendix B.4). Larger training sets were screened against every evaluation partition (Appendix B.3). Some LevBench and Kev-Breadth content comes from public datasets (BoardgameQA, StepGame, CLadder, LogiQA 2.0, AR-LSAT, QuAIL, TimeDial; Appendix B.4). The date of the JevBench public items is not stated.

## Cost and latency
Median per-request latency on one H200 GPU, bf16, one request at a time, without fused kernels (Section 5; Limitations). LEV-2.6B: 51 ms at depth 1 to 200 ms at depth 4; LEV-1.4B 15 to 58 ms; LEV-3B 23 and 45 ms; Kev-0.8B 79 ms; Kev-4B 108 ms (Table 1). Counted in floating-point operations every LEV model is at or below the dense options (Appendix F, Table 17: negative differences at equal FLOPs). Authors give no dollar costs for their own runs beyond GPU description.

## Calibration
Top-label ECE on the 111 JevBench hard items after per-depth temperature scaling fitted on the calibration partition (Section 4.2; Table 9). LEV readouts 0.18 to 0.26 with no trend in depth; Kev-0.8B 0.172, Kev-4B 0.112, Jev 1.13.0 0.086 (Table 9). Fitted temperatures 1.05 to 1.18 (Ouro) and 1.00 to 1.02 (LEV-3B) (Appendix C.3). ECE on Kev-Breadth 0.07 to 0.12 (Appendix). Binning scheme of ECE not stated; coded ECE-equal-width on the assumption of JevBench's top-label ECE code (flag).

## Cascade or escalation
On-demand depth saves 15% to 24% of computation, within 1.0 point of the deepest readout (Section 7.2, Table 2). Against dense cascades at the same measured latency, on-demand LEV-1.4B and LEV-3B are 7.0 to 8.8 points more accurate at 39 to 46 ms (Section 7.4). Confidence-threshold early exit set on labelled data does not beat the fixed-depth frontier (Section 7.3, Figure 8).

## Option-name, cardinality, language, robustness tests
Kev's "none of the above" augmentation is used in training (Appendix B.1). Unknowable-tier questions are scored by how often the model answers confidently (Appendix B.4). No option-order or language test.

## Code and data
Code https://github.com/OpenLAIR/lev, models https://huggingface.co/collections/songdj/lev, site https://openlair.github.io/lev/ (title page).

## Authors' stated limitations
Only 1.4B to 3B looped backbones; JevBench only through 231 public items; cost counted in loop steps, not wall-clock; latency measured one request at a time without optimised serving (Limitations).
