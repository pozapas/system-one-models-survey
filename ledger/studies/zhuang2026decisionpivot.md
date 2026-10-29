# zhuang2026decisionpivot: DecisionPivot: A Diagnostic Benchmark for Decision Models in LLM Systems

arXiv:2610.28522v1 [cs.AI], 20 Oct 2026 (fulltext/2610.28522.html and .txt; PDF first page saved as fulltext/2610.28522.pdf for the affiliation line). Extractor batch V18.

## Authors and affiliation
Xialie Zhuang, Mingcong Lei, Zunhai Su, Ri Liu, Jianjin Li, Peixian Ma, Jia Pan, Ngai Wong, Guanhua Chen*, Chuan-Wei Kuo* (* corresponding), a single affiliation "StartLux" (PDF page 1). The benchmark authors also develop the StartLux-Decision-27B models (SL-27B Instant and AutoThink, labelled "StartLux (ours)" in Table 4) and state "As DecisionPivot and StartLux-Decision are developed by the same team, independent evaluation and additional case designs would provide valuable complementary evidence" (§6). Affiliation type: vendor. Code https://github.com/StartLuxLabs/DecisionPivot; data on Hugging Face (startlux-models) with access "granted on request" (Datasheet, Appendix F).

## Task and data
Diagnostic benchmark for decision models: 48 tasks, 40,033 items, seven decision roles. Core track: 7,800 generated items from 13 task families (200 items per family per difficulty level, three levels), organised in contrast groups where a pivotal detail changes the correct answer; "an independent solver agrees with all 600 answers" per family (Table 2) and verifies all core answers (§3.2). Reference track: 32,233 items from 35 public test sets with original metrics (§3.3). Version 1.1 items; input-sensitivity analyses use version 1.0 items. Fresh samples from seven generators check ranking stability (§5). Uniform guessing gives 39.6% item and 16.1% pair accuracy (Table 4 caption). Pair accuracy requires every member of a contrast group to be correct.

## Decision models evaluated
40 decision models plus 14 general models (Table 4, Table D10). The hosted reference is "jev-1.13.0 (the hosted reference)", "API, called on 7 and 9 October 2026" (§4, Appendix B, model table). Open models listed with HF revision hashes in Appendix B (for example JEV-27B revision 51740a8, JEV-9B b63f651, this-that 1.2 c4d1c30, Strands decider 2B v21 2b52a62; most revisions listed); Kev 27B, Perplexity Decider v1.1, Clef 27B, Clef flash 9.5B, Nimble v3, six Decision 2.0 models, six Decision 3.0 models, Liquid d1, H2O-Lightning-4B and others. General chat models DeepSeek-V4-Pro, DeepSeek-V4.1-Flash, GLM-5.3 (API, stated probabilities, core track only) and 11 open general models with one-pass option-key probabilities.

## Comparators and tuning-budget parity
Each model is evaluated "using documented, model-specific protocols": per-model probability readout, input limits (truncation) and reasoning settings, with prompts adapted to each model's interface (Appendix B). Input restrictions cause missing or truncated predictions, counted as incorrect (Table 4 dagger, Table B1); this confounds some rows. Higher-effort GLM-5.3 runs use provider-default sampling and a larger output budget, lower-effort runs use temperature 0 (§4.3). SL-27B AutoThink (the benchmark authors' own model) generates a reasoning trace when its top one-pass probability falls below 0.9. The authors' own models were filtered for detected overlap with public sets (Appendix C).

## Reference labels
Core track: synthetic, with answers computed by the generator and verified by independently implemented solvers. Reference track: source labels of 35 public test sets, original metrics, a mix of label types with "potential uncertainty in source labels" (§6). The reference score is a chance-corrected, floored mean over layers (0 = chance, 100 = perfect).

## n and sampling
Core: 7,800 items in contrast groups; pair accuracy intervals are 95% bootstrap intervals resampling groups (seed 20261007, matched resamples for paired comparisons, Appendix B.4). Calibration error is a point estimate with no interval. "Most evaluations use a single run" (§6). A second SL-27B AutoThink run changes 5.6% of individual answers (§4.3).

## Test-set exposure
Core track items are generated for this benchmark (new, version 1.1 revised). Reference track items come from public test sets with training-overlap flags taken from model documentation (Table C3): "Training-data overlap cannot be fully assessed for models without detailed training records" (§6). JEV-27B documents 498,010 synthetic scenarios labelled with the hosted reference's output distributions (Appendix C), i.e. JEV-27B is a distillation of hosted Jev.

## Cost and latency
Not reported (inference efficiency out of scope, §6); GLM-5.3 reasoning tokens per item 121 to 265, AutoThink 297 reasoning tokens per item on the 1,296-item subset (§4.3).

## Calibration
15 equal-width bins, calibration error reported as a percentage point estimate (Table D1, Appendix B.4), computed on core items; accuracy and share at confidence >= 0.90; retrospective empirical coverage at a 5% error rate ("auto at 5%", macro-averaged over 13 families). "Empirical selective coverage is retrospective and requires independent calibration for deployment" (§6). A single global threshold on the evaluation pairs raises binary pair accuracy to 74.2% (Perplexity Decider) and 30.6% (Clef 27B) (§5), described as optimistic. Table D1 lists selected systems only; the hosted Jev has no calibration entry among the rows read.

## Cascade or escalation
SL-27B AutoThink escalates to reasoning when the highest one-pass probability falls below 0.9 (reasoning on about two-thirds of reference items): core pair accuracy 86.9 vs 75.4 for the one-pass Instant variant, reference scores 58.9 vs 59.4 (§4.3).

## Option-name, cardinality, language, robustness
Option-order study (version 1.0): Kev 27B changes 4.9% of predictions under the first reordering variant (2.0% correct to incorrect, 1.5% incorrect to correct, net -0.5 points); natural wording changes up to 20.7% of predictions; pair-accuracy changes from -2.2 to +2.2 points (§5, Figure 7, Tables D8, D9). Difficulty levels: Perplexity Decider pair accuracy falls from 87.7 to 57.4 from level 1 to level 3. English only; multilingual out of scope (§6).

## Code and data
Code on GitHub; dataset on Hugging Face with access on request; generators, solvers, audits, scoring code and evaluation records released (Datasheet).

## Authors' own limitations (§6)
Written cases rather than end-to-end operation; difficulty levels vary size and complexity together; models evaluated through differing interfaces; single runs; input-sensitivity analyses on version 1.0 only; retrospective coverage; potential uncertainty in public source labels; training overlap cannot be fully assessed; fresh samples assess stability within existing generators only; developer overlap between benchmark and a leading evaluated model.

## Notes for the grader
The top-ranked models are the benchmark authors' own (SL-27B AutoThink 86.9, SL-27B Instant 75.4 pair accuracy); the best non-vendor model is Decision 3.0 d3 (71.3) and Perplexity Decider (70.1). The hosted Jev reference has pair accuracy 31.0 [29.4, 32.7] and item accuracy 63.9, with 19 of 40 decision models below the 16.1% uniform-guess pair baseline overall.
