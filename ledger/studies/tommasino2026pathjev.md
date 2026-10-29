# tommasino2026pathjev

arXiv 2610.32478v1 (cs.CV), 23 Oct 2026. "PathJev: Decision-Native Vision-Language Modelling for Histopathology." Authors Cristian Tommasino and Antonio M. Rinaldi, DIETI, University of Naples Federico II, Naples, Italy. Affiliation type: academic. License CC BY-NC-ND 4.0. (title block)

Study type: own-model (PathJev-P) with a pre-specified comparison against a generative model on the same backbone, zero-shot comparators and a supervised probe.

## Task and data
- Main Choice question per histology patch (tissue class, lesion subtype or Gleason pattern) with organ-specific candidate sets and a "none of these" option; Noul (yes/no) and Score (ordered) questions are exploratory. (Sec. 3.1, 4.2, App. F)
- Training: 40,000 patch states from BRACS, SICAPv2 and four SPIDER organ subsets; validation 2,100 states. Labels are the datasets' expert annotations or deterministic functions of them; no LLM-generated labels. (Sec. 4.2)
- Clean test sets (headline): HepatoBench liver 5,000 of 87,301 states (7 classes, images resampled as independent units, which "understates the uncertainty"), HiESD stomach 5,000 of 23,679 (10 classes, 44 patients), BRACS 570 (30 patients), SICAPv2 2,122 (21 patients). Seen-source SPIDER sets reported separately (4 x about 5,000). Large sets capped by a class-balanced draw set after a pilot. (Sec. 4.3, Table 1)
- Reference labels: expert pathology annotations released with each public dataset (single annotation per patch; adjudication not described). Datasets are public; contamination handled by role assignment ("clean" = no documented overlap with MedGemma, OmniMed-Jev or own training data); undisclosed backbone data cannot be excluded, and Table 8 marks most overlap cells "U" (undisclosed). Exact and perceptual duplicate audit found no copy of a training or validation image in clean sets; two SPIDER-skin test states excluded. (Sec. 4.1, 4.3, App. D Table 8)

## Decision models
- PathJev-P: MedGemma-1.5-4B (4-bit NF4) with LoRA (rank 16) and a shared decision head (per-candidate score, question-candidate interaction, set attention), two-stage training; selected lr 2e-4, 3 epochs; 3 seeds. No revision hash for MedGemma. Weights at huggingface.co/Cristiandieti/PathJev-P. (Sec. 3.2, 3.3, App. D Table 7)
- OmniMed-Jev (released decision-native checkpoint), zero-shot; no revision given; run with 448-pixel pre-resize. (Sec. 5.1, App. D)
- Inner-Jev read-out: base MedGemma-1.5-4B zero-shot, letter logits. (Sec. 5.1)
- No hosted Jev is evaluated.

## Comparators and tuning parity
- Gen-SFT: same backbone, LoRA configuration, training states and selection rule (lowest validation NLL on Choice questions, grid of two learning rates and 3 or 5 epochs, one seed, then two more seeds). But objective, number of supervised targets and optimiser steps differ (170,390 single-decision examples, 5,000 optimiser steps versus 200+2,500; 160,000 versus about 368,042 decision targets seen), so "the comparison is between two systems rather than an ablation of the decision head". Gen-SFT was scored only on the capped test sets. (Sec. 5.1, 6, App. D Table 7)
- CONCH zero-shot with an ensemble of five prompt templates; linear probe on H-optimus-0 features (fitted on part of the test set by nested grouped cross-validation for HepatoBench and HiESD, so a supervised reference rather than a competitor). (Sec. 5.1)
- Analysis plan with two hypotheses (H1a lower ECE, H1b higher balanced accuracy versus methods a, b, c, e) fixed and hashed on 17 October 2026 before any test evaluation; three amendments, A2 (temperature analyses) and A3 (read-out, order, grey image checks) are post hoc and flagged. (App. A)

## Results
Clean-average balanced accuracy: PathJev-P 0.541 +/- 0.015, Gen-SFT 0.492, CONCH 0.345, Inner-Jev 0.288, OmniMed-Jev 0.213; linear probe 0.724. Paired difference to Gen-SFT +0.049 [+0.038, +0.063] (95% cluster bootstrap over patients/slides/images, same 10,000 replicates for all methods, seed-by-seed pairing). Unseen organs 0.390 versus 0.277; in domain 0.692 versus 0.707; seen source 0.781 versus 0.810. Without HepatoBench the difference to Gen-SFT is +0.033 [+0.018, +0.052]. (Sec. 5.2, Tables 2, 9)

## Cost and latency
Training wall time 10.4 to 10.5 h versus 16.3 to 16.5 h for Gen-SFT on one GPU; the decision head answers in one forward pass, the generative read-out needs one pass per candidate. No inference latency measured; end-to-end whole-slide time not measured. GPUs H100 (L40 for post-hoc re-runs, probabilities differing by up to 0.12). (Sec. 5.4, 6, App. D, E, Table 7)

## Calibration
ECE with 15 equal-width bins on top-candidate confidence, plus NLL, Brier, adaptive ECE, AURC, reliability diagrams. Clean ECE PathJev-P 0.204 +/- 0.002, Gen-SFT 0.279 (difference -0.075 [-0.088, -0.064]), CONCH 0.403, OmniMed-Jev 0.517, probe 0.047. Post hoc: with a length-normalised read-out Gen-SFT ECE is 0.201 clean and 0.110 on unseen organs versus PathJev-P 0.301, so the calibration advantage depends on the read-out. Temperature scaling (fitted on the validation mix, which was also used for selection) lowers PathJev-P to 0.154; PathJev-P stays over-confident on unseen organs; temperature fitted on the other unseen organ lowers unseen-organ NLL from 2.079 to 1.781. (Sec. 5.3, Tables 2, 3, 10, 15)

## Cascade or escalation
Not a cascade, but whole-slide use runs the model on 16 representative tiles per cluster with abstention below top probability 0.5; four slides, descriptive only (e.g. slide 1a7624bc AUROC 0.983 clusters versus 0.946 all tiles). (Sec. 5.4, Table 4)

## Robustness
Candidate order: 10 random orders, PathJev-P clean bAcc 0.542 to 0.549, 7.3% of predictions change (OmniMed-Jev 18.9%, which also answers "other" for 49.8% of items). Grey-image check: balanced accuracy at chance. Image size for OmniMed-Jev (448 versus 896) changes little. Cardinality: up to 25 options for the Inner-Jev read-out; no language or option-name test. (Sec. 5.2, App. E)

## Code and data
Code, question templates, split manifests and the analysis plan at https://github.com/CosmoIknosLab/PathJev; weights and a demo on Hugging Face. Datasets public, some non-commercial licences. (Sec. 1, Data statement)

## Authors' limitations (Sec. 6)
Single patches, whole-slide pipeline not evaluated against pathologists; "clean" means no documented overlap and backbone data partly undisclosed; only two unseen organs; HepatoBench cannot be grouped by slide or patient; one backbone in 4-bit; one wording per candidate and one prompt ensemble for zero-shot models; Gen-SFT scored only on capped sets; the two trained systems differ in more than the decision head.
