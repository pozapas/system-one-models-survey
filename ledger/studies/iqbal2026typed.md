# iqbal2026typed: Typed Decision Models under Prevalence Shift: Decision Training, Calibration, and Implicit Priors

arXiv:2610.26325v1 [cs.LG], 19 Oct 2026 (HTML title block; fulltext/2610.26325.html and .txt). Extractor batch V18.

## Authors and affiliation
Abdul Rahman Iqbal, Muhammad Fawad Nasim (Faculty of Computer Science and Information Technology, The Superior University, Lahore, Pakistan); Amir Saleem (Independent Researcher) (title block). Affiliation type: academic. Artifacts at https://github.com/AbdulRahmanIqbal/tdm-prevalence-shift (§1).

## Task and data
Candidate-set classification as typed decisions under simulated prevalence (label) shift. Five public English datasets (Table 2): CLINC150 in-scope intent (test 4,500; 150 classes, candidate sets of 18 to 19 options from fixed k-means label groups), HWU64 intent (test 1,076; 21 to 22 options), FPB financial sentiment (test 970, 50%-agreement subset, 64/16/20 split following Araci 2019), HateXplain (test 1,924, 3 labels), TREC-6 question type (test 500, 6 labels). Fixed label groups were used because candidate sets built around the gold label let a text-blind classifier recover the gold label for 97.6% of CLINC150 and 90.2% of HWU64 examples (§4). Option order shuffled per example with a fixed seed and the gold position counterbalanced. Prevalence shift: Dirichlet-resampled target priors, confirmatory at alpha=1 over a fixed set of 50 priors; descriptive at alpha=0.1 and over 200 or 2,000 draws (§4, §5.2). The results concern candidate-set decisions with simulated label shift only (§1, §7).

## Decision models evaluated
Table 3: Jev through the Cloudflare Workers AI API (typesafe/jev), "the response's version field was jev-1.13.0 for every call (16,234 in the full run and 7,500 in three repeats)", queried on 2026-10-13 between 05:47 and 07:50 UTC (Appendix D); Tev1-4B (togethercomputer/Tev1-4B-experimental, commit 0b7becf0, bf16); Nimble-9B (Qwen3.5-9B + LoRA bespokelabs/Bespoke-Nimble-9B, commit fe33f82b, release original-2676 trained on 2,676 synthetic examples, 8-bit). Base models Qwen3.5-4B (851bf6e8) and Qwen3.5-9B (c2022362) read out identically. The later Nimble release (training data include 500 public TREC questions) is not used for the confirmatory pair. Jev gets label names as option keys and label descriptions as criteria; probabilities rounded to two decimals and renormalised over candidates (§4).

## Comparators and tuning-budget parity
Trained classifiers: DeBERTa-v3-large fine-tuned on the full training set, 5 seeds (first seed used for analyses), lr selected from {1e-5, 2e-5} on dev, 5 epochs; TF-IDF + logistic regression with C selected on dev (§4). The authors note the asymmetry: the trained classifiers use the development set both for model selection and recalibration whereas zero-shot systems use it only for recalibration and the implicit prior. Open TDMs and their base models receive token-identical prompts in the TDM's own training format (checked on all 16,234 development and test prompts). No few-shot variants. Label texts were frozen before any model was run (§4).

## Reference labels
Dataset gold labels, described only as "public, human-labelled" (§1). The annotation process is not described in this paper (FPB 50%-agreement subset; HateXplain and CLINC150 crowd labels per the source datasets). Coded human_crowd.

## n and sampling
Test sizes above. 35 confirmatory paired tests fixed and hashed before the final runs: paired bootstrap (B=10,000) over test examples for Macro-F1 and ECE differences, class-stratified bootstrap conditional on 50 fixed target priors for PA1 to PA3; percentile 95% intervals are unadjusted, p-values Holm-adjusted over 35 tests (§4). 14 of the 35 tests significant (Table 7). Quantities fitted on the dev set are held fixed in the bootstrap, so intervals understate total uncertainty (§7). One amendment after the first local predictions but before DeBERTa/Jev runs and before any test was computed; earlier pipeline checks touched test splits, mainly FPB (Appendix A, §1).

## Test-set exposure
All five datasets are public and predate 2026; exact and near-duplicate overlap with vendor-named corpora was checked: 614 of 1,076 HWU64 test texts occur in MASSIVE (582 exact, 32 near-duplicate), 96 of 4,500 CLINC150, 4 of 500 TREC-6, 1 FPB text, no HateXplain text. "We cannot rule out pretraining contamination for any model." On the 462 non-overlapping HWU64 examples every system loses 2.2 to 5.9 Macro-F1 points (Table 21, App. D).

## Cost and latency
Jev API median 713 ms including network, 95th percentile 942 ms (Appendix D). Local models on one NVIDIA RTX 4070 Ti (12 GB) p50: Qwen3.5-4B 110 to 171 ms, Tev1-4B 121 to 214 ms, Qwen3.5-9B 315 to 395 ms, Nimble-9B 418 to 482 ms; DeBERTa-v3-large 24 to 56 ms at batch size one; TF-IDF about 0.5 ms on CPU. No monetary cost reported for Jev.

## Calibration
ECE with 15 bins, top label, candidate-restricted (Table 4); Brier and NLL under shift in Tables 16 and 17. Post-hoc arms (Table 12, descriptive): EM prior correction with the implicit prior (label-free), temperature scaling and bias-corrected temperature scaling followed by EM (labelled on dev), oracle prior. Jev's ECE under shift on HateXplain falls from 0.271 to 0.254 with label-free EM and to 0.071 with BCTS+EM (§5.3).

## Cascade or escalation
Threshold risk: excess risk of a confidence threshold set for 80% coverage on the dev set (PA2); no cascade to a larger model.

## Option-name, cardinality, language, robustness
Fixed candidate groups to block gold-label leakage through the option list; option order shuffled with counterbalanced gold position. Tev1 was trained mostly on at most eight options, so 18 to 22 options are out of its training distribution (§4). Jev repeat-call nondeterminism (Table 10): same prediction on 96.4 to 99.8% of 500 test examples per dataset, same probability vector on only 19.4 to 87.4%, ECE run-to-run range at most 1.2 points. English only. Full-label (150 or 64 class) classification is not tested.

## Code and data
All frozen label texts, candidate sets, prompts, evaluation code and every per-example probability vector released at the GitHub URL above (§1).

## Authors' own limitations (§7)
Three TDMs, two open backbones; English public datasets; small FPB and TREC-6 tests; candidate-set format only; label shift simulated by resampling (optimistic case for prior correction); confirmatory shift estimand conditional on one set of 50 priors (the frozen FPB PA1 estimate is 1.7 points but the 2,000-prior mean is 0.4); Jev version cannot be pinned beyond the response string and Jev is not deterministic; 9B models run in 8-bit; bootstrap intervals understate uncertainty.

## Notes for the grader
The conclusion is deliberately balanced: TDMs "neither uniformly better than their backbones nor uniquely fragile under shift". The abstract and Table 6 both report the significant FPB-only result for Jev vs DeBERTa under moderate shift. The Nimble comparison uses an 8-bit matched pair and an early release chosen to avoid TREC contamination.
