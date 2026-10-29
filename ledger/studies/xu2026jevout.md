# Xu, Song, Zhang, Chen, Liu, Hu & Zhao (2026), "JevOut: Natural Context Can Flip Decision Models"

## Identification
- arXiv 2609.30243, saved copy v2 [cs.CL] 08 Oct 2026 (header); abstract page says submitted 24 Sep 2026 (v1), last revised 8 Oct 2026. License arXiv perpetual non-exclusive. Full text fulltext/2609.30243.html and .txt.
- Authors Zixiang Xu, Zirui Song, Chiyu Zhang, Xiuying Chen, Xi Liu, Xiyang Hu, Yue Zhao (PDF page 1; the saved HTML lacks the byline, so the PDF was saved as fulltext/2609.30243.pdf). Affiliations on PDF page 1: University of Southern California; Mohamed bin Zayed University of Artificial Intelligence; Arizona State University; two authors as Independent Researcher. Corresponding author Yue Zhao (USC). affiliation_type = academic (mixed with independent researchers).
- Homepage https://xzx34.github.io/jevout/ ; code https://github.com/xzx34/JevOut (header).

## Task and data
- Natural-context redirection: short, natural, answer-preserving context additions (typically one sentence) that move an initially correct decision to a wrong option fixed in advance. Targeted Flip Rate (TFR) = share of initially correct decisions with at least one targeted flip within 64 accepted target evaluations (Introduction; Section 4.1).
- Seven datasets: MMLU-Pro, SuperGPQA, MuSR, ToMBench, LAR-ECHR, SATA-Bench (binary reduction), BFCL V4 (tool routing). 50 development and 100 held-out source items per dataset; 700-item item-disjoint test set; at most one initially correct decision per source item per target (Section 4.1; Appendix B.2). Primary runs span 1,449 eligible model-item pairs.
- Proposer Gemma4-12B with a separate constraint-check invocation that does not see the target option; probability-guided optimization uses the full option distribution to weight parents by target margin (Sections 3, 4.1).

## Decision models
- Hosted Jev 1.13.0 (n = 508 initially correct), OpenSourceJev (Qwen3-1.7B Q8 typed branches; n = 328), Von 1.0 (395M non-autoregressive decision model; n = 328), plain Qwen scorer (same Qwen3-1.7B Q8 weights, numbered options; n = 285) (Section 4.1). No run dates; Jev documentation accessed 2026-09-23.

## Comparators and tuning parity
- The four systems are co-targets, not competing contenders. Controls: neutral one-shot (no target visible), target-aware one-shot, and repeated independent target-aware generation under the same 64-call ceiling (Jev only). All use the optimizer's base proposer and acceptance checks. Same attack budget across systems; the attack is tuned per system through its own feedback (Section 4.1).

## Reference labels
- Benchmark gold answers define initial correctness and the wrong target; blinded human evaluation validates contexts (three independent annotators, 250 successful contexts mixed with 100 accepted-but-unsuccessful controls; majority judgment 91.6% natural, answer-preserving, no decisive answer-changing evidence; controls 93.0%) (Section 4.2; Appendix C.1, Table 7). reference_label_type for flip rows = task_outcome.

## n, sampling, intervals
- All rates retain the initially correct population; 95% Wilson intervals (Section 4.1). Jev TFR 61.4% (312/508) [57.1, 65.5] (Table 8). Paired 95% bootstrap intervals (5,000 dataset-stratified resamples) for the feedback ablation on 140 matched Jev decisions (Figure 4b).
- Repeatability audit: 100 of 312 successful Jev cases sampled by seeded hash (seed 20261002), ten extra identical-input evaluations; 97/100 reproduce the flip in at least 8 of 10 calls, 93 in all ten (Appendix I.2).

## Key results
- Table 1: TFR (%) within 64 accepted calls: Jev 61.4, OpenSourceJev 72.6, Von 73.2, plain Qwen 64.9. Neutral one-shot 2.2 (Jev) to 8.4; target-aware one-shot 16.9 (Jev) to 21.6.
- Initially confident decisions (p_y >= 0.9): Jev 45.5% (n = 290), OpenSourceJev 67.3, Von 59.7, plain Qwen 59.3 (Table 2).
- Single-sentence additions suffice for 41.5% of the initially correct Jev population; 64-word cap retains 57.5% (Table 3).
- Repeated independent generation 48.0%; optimization adds 13.4 pp; probability-only allocation +7.1 pp over label-only on 140 matched decisions (Section 4.4).
- Cross-model transfer 21.1% to 31.2% outside the shared-backbone pair (Section 4.5; Figure 5). Learned proposer V2 raises one-generation TFR from 16.1% to 21.9% (Table 4).

## Calibration
- No ECE or calibration analysis. Uses the returned probabilities to show that flips often carry high confidence: for each system a majority of successes include a context with target probability >= 0.7 (Jev 45.1% of 508 meet this, Table 1). Initial confidence strata in Figure 3a and Table 13.

## Cost and latency
- Not reported as cost or latency; call counts only (Appendix I.1; independent-generation control 27,143 proposals and 24,860 accepted target evaluations).

## Cascade, option-name, cardinality, robustness
- Cross-model transfer (Figure 5), word-cap coverage (Table 3), budget curves (Figure 4a), task-level results (Tables 8 to 11). English only. Option cardinality varies by dataset (SATA reduced to binary). No cascade.

## Test-set exposure
- Public benchmarks (MMLU-Pro, SuperGPQA, MuSR, ToMBench, LAR-ECHR, SATA-Bench, BFCL V4) released before 2026; the study measures vulnerability on initially correct items, so contamination would raise the eligible population rather than the flip rate. No contamination check noted.

## Code and data
- GitHub repository https://github.com/xzx34/JevOut and homepage given in the header.

## Paper's own limitations
- English tasks with finite option sets and known correct answers; single-decision evaluation, no closed-loop propagation; multilingual and open-ended action settings untested; dual-use note (Limitations; Ethical Considerations).
