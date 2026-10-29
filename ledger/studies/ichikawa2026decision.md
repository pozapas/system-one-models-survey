# ichikawa2026decision

arXiv 2610.34956v1 (cs.AI), 26 Oct 2026 (paper dated 24 Oct 2026). "Decision Model Factory: Building Specialized Sovereign Decision Models." Single author Yuma Ichikawa; affiliation markers 1,2 appear but the affiliation text was not captured in the HTML. Affiliation type: not reported. (title block)

## Task and data
- Build pipeline (recipe, LoRA training, adapter-strength selection, per-answer-type temperature calibration, export verification) plus a decision runner; five models evaluated on S1MB (System One Mosaic Benchmark): 8,067 judgments over 27 Japanese benchmarks and 26,269 over 137 English benchmarks; Task Avg is the mean over three answer types (Noul, Choice, Score) of trivial-baseline-adjusted, clipped benchmark scores times 100. Passage ranking on JQaRA, MIRACL Japanese, MLDR Japanese using the affirmative-option probability of a Noul relevance judgment. Embedded-instruction test on 300 held-out states each in English, Japanese, Portuguese; calibration on 600 development decisions. (Sec. 2, 5.1)
- Reference labels: benchmark labels aggregated in S1MB (mixed). Public benchmarks pre-2026; no contamination check; development decisions for calibration are the same data used to fit temperature (in-sample ECE). (Sec. 5.1, 5.2)

## Decision models
- DF-JA-Large and DF-Large (Gemma 4 31B), DF-Long (Gemma 4 26B-A4B MoE, 262,144-token inputs), DF-Small and DF-JA-Small (Gemma 4 E4B, distilled from a larger decision teacher with beta 0.5). Option-logit readout with LoRA, no extra head; logit soft-capping c=30. No model revisions or hashes reported; S1MB evaluator revision a77c30c, Japanese dataset revision 59b66dd; public snapshot 4c0e5d5 retrieved 18 Oct 2026. Hosted Jev is cited only. (Sec. 2, 5.1, App. A, refs [1],[12])

## Comparators and tuning parity
- Backbone before adaptation with same readout and packaging; public results from a fixed snapshot of 34 complete S1MB evaluations (not re-run, differing protocols unknown); Ruri v3 and bge-reranker-v2-m3 on identical candidate passages. DF models are trained and tuned on a development split with adapter strength chosen from {0.5, 0.75, 1}; comparators are not tuned by the authors. Single build per model, no seeds or intervals. (Sec. 5.1, App. A)

## Results
S1MB Japanese Task Avg: DF-JA-Large 67.63 (backbone 58.99), DF-Large 66.98, DF-Long 63.57 (backbone 51.58), DF-Small 52.96 and DF-JA-Small 52.49 (E4B backbone 31.97); best public snapshot 60.05; Saihai 8B 49.77. English: DF-Long 63.55 (from 52.14), DF-Large 62.31, DF-Small 47.30 (from 36.49). JQaRA nDCG@10 90.1 vs Ruri 86.9 and BGE 67.8; MIRACL Ja 93.7 vs 91.8 and 90.1; MLDR Ja 98.9 vs 97.7 and 97.6. (Table 1, 2, Sec. 5.2)

## Cost and latency
Single NVIDIA B200 or 16 Intel Xeon cores, synthetic support tickets, medians after warm-up. Runner vs general path, DF-Long BF16: eight questions one state 29.4 vs 71.7 ms (2.44x), eight states 30.9 vs 68.8 ms (2.23x), four states x eight questions 570 vs 364 decisions/s, one question 15.0 vs 16.3 ms. Bulk throughput about 2,328 decisions/s (E4B) and 380 (DF-Large); E4B on 16 CPU cores 11.2 decisions/s; 27K-token document question 0.41 s. Runner and standard path differ by at most 0.2 points on S1MB and JQaRA. Training time/cost not reported. (Table 3, Sec. 5.2)

## Calibration
Temperature per answer type fitted on development decisions; DF-Long ECE 0.024 on those same 600 decisions (in-sample; binning not stated). (Sec. 2, 5.2, Table 2)

## Cascade or escalation
None.

## Robustness
Embedded instructions ignored in 899 of 900 trials across English, Japanese, Portuguese; Japanese and English evaluation; no option-name or cardinality tests reported. (Sec. 5.2)

## Code and data
No code or model-release statement found. S1MB evaluator public (github.com/hotchpotch/S1MB). (refs)

## Authors' limitations
No limitations section.
