# gao2026more

More Choices, Fewer Decisions: Ordinal-Scale Bias in JEV-like Direct-Decision Models. arXiv 2609.38827; first version 2026-09-30, the saved full text is v2 (14 Oct 2026). Extractor: batch V05. Ledger rows L1837 to L1853.

## Authors and affiliation
Tianxiang Gao, Jinzhe Li, Zhiyuan Li, Yi Chang, Yuan Wu (corresponding). School of Artificial Intelligence, Jilin University (also College of Software, International Center of Future Science, and the Engineering Research Center of Knowledge-Driven Human-Machine Intelligence, Jilin University) (title block). Affiliation type: academic. No vendor link stated.

## Task and data
Diagnostic study of "ordinal scale-utilization bias": whether argmax decisions of direct-decision models cover as many effective labels as the gold distribution (effective support = exp(entropy)). Main panel: 40 public datasets, 5,000 items each, sampled without replacement and stratified by gold label with fixed seeds (Sec. 3.2, Appendix B); 36 labelled ordinal (graded scales, K from 3 to 10 and more, Appendix Table 4), 4 nominal (SNIPS K=7, Yahoo Answers K=10, SCOTUS K=13, DBpedia K=14). Additional panels: candidate order (6 ordinal + 3 nominal datasets, 2 random permutations per item, 90,000 extra queries per model); candidate count (K = 2 to 14 on 1,400 items from each of RealToxicity Continuation, Civil Comments Toxicity, STS-B plus DBpedia reference); fixed-count spacing (Word Concreteness, WMT20, Measuring Hate Speech, Stanford Politeness, 7 spacing conditions, seed 20261007, 138,894 questions per open checkpoint; Jev only on the 3-source panel, 104,118 questions) (Sec. 3.4 to 3.6, Table 3). ANLI motivating observation on 6,400 development and test items (Sec. 1). All data public and predating 2026 (Appendix B.2, access dates 2026-09-28/29). The authors flag that SST-5, DBpedia-14 and IMDb are KEV training sources and were not audited for overlap (Limitations); Jev's training data are unknown.

## Decision models and versions
Jev: hosted endpoint identifier `typesafe/jev-1.13-20260917` (Sec. 3.1, Appendix B.1), no sampling parameters, candidates keyed A, B, C in presentation order; inputs over 24,000 bytes truncated in the middle for a 10-dataset collection batch (Appendix B.2). KEV-0.8B, KEV-4B, KEV-9B (jaredpalmer/kev-0.8b, kev-4b, kev-9b; Qwen3.5 backbones), and StartLux Decision at 0.8B, 2B, 4B, 9B, 27B (Sec. 3.1). KEV-0.8B and KEV-4B are also fine-tuned by the authors with BA-LoRA on 32,000 examples (8 sources x 4,000; disjoint from the evaluation panel) (Sec. 3.7, Appendix E). Collection dates for Jev requests are not stated beyond the 2026-09-17 version identifier and reference access dates of 2026-09-28/29.

## Comparators and tuning-budget parity
All nine models receive the same text, question and candidate list; outputs are mapped to labels by candidate text (Sec. 3.1). No prompt tuning is described and no prompts are varied across models. Parity: same items and format; the BA-LoRA arm is a deliberate fine-tuning intervention applied to KEV only and is reported separately.

## Reference labels
Gold labels of the public source datasets (reviews, ratings, rubric and annotation scores, Appendix B.2 Table 4 lists the 40 datasets; label provenance per dataset is not described in the main text). Label type is mixed and not characterised by the authors; the ledger uses human_crowd as the nearest single category.

## Sampling and intervals
5,000 items per dataset; fixed seeds; no confidence intervals. "All results are point estimates" (Limitations). Main panel success: 199,999 per original KEV checkpoint (one non-ok response), 200,000 for Jev and StartLux (Appendix Table 3 note).

## Headline results
Across 36 ordinal datasets, mean effective-support deviation D_R is 25.92 (Jev 1.13) to 39.53 points (StartLux-0.8B); nominal tasks 0.99 to 13.37 (Table 1). Jev ordinal accuracy 37.67%, nominal 84.39% (Table 1). Prediction compression rises with K (Spearman 0.74 to 0.82 for Jev/KEV, Sec. 4.1); on balanced 14-level RealToxicity Jev puts 66.2% of predictions on Level 01. Larger models improve accuracy without consistently restoring utilization (KEV-4B more accurate but more compressed than KEV-0.8B). Under candidate-order randomization the two random orders agree on 58.1 to 78.0% of ordinal items (so 22 to 42% of answers differ), but macro accuracy by at most 0.95 points (Table 2, Sec. 4.2.1). Scale refinement: Jev D_R 4.1 (K=2) to 45.6 (K=14) on the same items (Sec. 4.2.2). Wider spacing at fixed K can raise accuracy without restoring utilization (Sec. 4.2.3). BA-LoRA lowers KEV-0.8B D_R from 52.6 to 13.2 and KEV-4B from 53.6 to 14.4 on held-out items from the eight training sources; transfer to 28 unseen ordinal sets helps at 4B (26.8 to 21.3) and hurts at 0.8B (25.0 to 29.9) (Sec. 4.3).

## Calibration
No ECE or Brier. The paper reports probability-side diagnostics: soft utilization U_soft and top-1 margin (Table 1, Figure 2); for example Jev margin falls from 69.0 to 21.8 points under equal-frequency binning as K grows (Sec. 4.2.2). No post-hoc recalibration of probabilities.

## Cascade and escalation
None run. The conclusion recommends reporting D_R, TVD and order sensitivity for judges used as first-stage evaluators in confidence-based cascades (Appendix A).

## Option-name, cardinality, language and robustness tests
Candidate-order permutation (two per item) and cardinality sweep K = 2 to 14 are the core tests (Sec. 4.2.1 and 4.2.2). Spacing manipulation at fixed K (Sec. 4.2.3). English-language datasets mainly; LABR (Arabic) is included (Appendix B.2). No option-name or wording variation.

## Cost and latency
No cost or latency figures. Jev received 521,518 constructed queries across four panels plus 6,400 ANLI items; billed calls and hosted GPU usage are not exposed. StartLux final runs sum to 21.90 hours; local inference on NVIDIA GeForce RTX 4080 SUPER (RTX PRO 6000 for StartLux-27B); Jev hardware not disclosed (Appendix B.1).

## Code and data availability
Anonymous review artifact https://anonymous.4open.science/r/jev_ordinal_scale_bia/ with sample identifiers, gold labels, hashes and numeric predictions; no source passages, no post-trained checkpoints; MIT licence for original code (abstract, Appendix B.2). Use of AI assistants for literature review, programming and polishing is disclosed (Appendix B.2).

## Authors' stated limitations (Limitations section)
Binary ordinal/nominal taxonomy rather than graded coupling; scale-refinement result from three ordinal sources with DBpedia as a ceiling reference only; two permutations per item; all results are point estimates; D_R equal to zero does not imply the same labels; one hosted system and two open families; possible training exposure of KEV on SST-5, DBpedia-14 and IMDb.
