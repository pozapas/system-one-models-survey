# tang2026omnimed

OmniMed-Jev: Calibrating LVLM Confidence for Trustworthy Medical Multimodal Decisions via System One. arXiv 2610.00381v1 (cs.LG), 2026-09-30. Extractor: batch V05. Ledger rows L1908 to L1921.

## Authors and affiliation
Luyao Tang (email lytang1999@gmail.com, affiliation line garbled in the HTML) and Cheng Chen, Department of Electrical and Computer Engineering, The University of Hong Kong (title block). Affiliation type: academic. Own-model paper; Jev is the motivating interface, not an evaluated system: no hosted Jev call is reported.

## Task and data
A typed decision model (Choice, Noul, Score over runtime candidate sets, one forward pass, many decisions per state) for medical images, built by adding a shared candidate-scoring head to MedGemma-1.5-4B-it (Sec. 3). Suite built by the authors from fifteen public source datasets: classification (ten pooled MedMNIST collections, one choice problem), multi-label chest radiograph findings (14 or 13 binary decisions per state), counting (blood-smear cell counts), regression (ejection fraction from cardiac ultrasound, retinal score from fundus) (Sec. 4.1, Appendix A). 23,558 training images, 155,729 decision targets, 726 held-out states, test n = 200 for classification, multi-label and regression and 126 for counting (Table 1, Appendix I). The authors constructed tasks and splits rather than using a published benchmark (Sec. 4.1). Held-out data come from the same sources as training; per-class, per-source and out-of-distribution behaviour is not measured (Sec. 6). The public source datasets predate 2026, and the MedGemma backbone pretraining overlap is not examined.

## Decision models and versions
OmniMed-Jev: head with 1,057,410 parameters, 39,555,202 of 2,529,778,162 backbone parameters adapted (LoRA rank 16, 4-bit NF4); two-stage training (head for 200 steps, then head plus LoRA) (Sec. 4.2, Appendix E). Both models are scored at step 2424, which is OmniMed-Jev's best-validation checkpoint (Sec. 4.2); the generative baseline was therefore evaluated at a step chosen on the other model's validation curve (disclosed asymmetry). Seed 42 for training; no hosted-service versions involved.

## Comparators and tuning-budget parity
Gen-SFT: same backbone, images, LoRA configuration, optimiser, 3,685 steps, seed and option-order augmentation, next-token objective; only max_length differs (1,024 versus 3,072) because OmniMed-Jev packs all of a state's decisions in one sequence (Table 8). The authors state the comparison "cannot separate the interface from the denser supervision and the additional decision head" (Abstract, Sec. 4.2, Appendix I). Probabilities for Gen-SFT are a reconstruction: each candidate scored by the summed log-probability of its continuation, normalised over the candidate set (Sec. 4.4, Appendix F); direct elicitation of a distribution failed (Table 10). For counting the reconstruction places no count on the annotated value in any of the 126 decisions, so the baseline's confidence-based numbers are uninformative there (Sec. 5.3). Compute: one A800 each, 12.86 h (Gen-SFT) versus 13.95 h (OmniMed-Jev) (Table 9).

## Reference labels
Source dataset annotations (diagnostic classes, finding labels, cell counts, clinical measurements); label provenance per dataset is in Appendix A (not extracted in detail). The ledger uses human_single as the nearest category.

## Sampling and intervals
Fixed held-out suite (726 states); one training run and one seed per model. Differences are paired: paired bootstrap 95% intervals from 20,000 resamples (seed 20260925), exact McNemar and sign tests (Appendix E). Classification balanced-accuracy difference +0.0422, interval [-0.0196, +0.1059]; multi-label F1 +0.0170 [-0.0264, +0.0620]; counting MAE +0.3730 [+0.0952, +0.6429]; regression MAE -0.3912 [-0.8756, +0.0173]. Only the counting difference is distinguishable from zero and it favours the generative baseline (Sec. 5.1). Wilson intervals are used for proportions (Appendix C). The ECE and Brier values in Table 2 carry no intervals.

## Headline results
Point accuracy comparable (Table 1). Calibration: ECE 0.0806 versus 0.2589 (classification), 0.0114 versus 0.2981 (multi-label), 0.0408 versus 0.4204 (counting), 0.0913 versus 0.1267 (regression) (Table 2, OmniMed-Jev versus Gen-SFT). The text states a 3 to 26 times ECE reduction and a 9, 44 and 126 times reliability-term reduction in classification, counting and multi-label (Sec. 5.2). Counting MAE worse (2.5159 versus 2.1429); the authors explain it as the expectation fold over a wide grid and call this a hypothesis (Sec. 5.5).

## Calibration
ECE (number of bins and binning scheme not stated in the main text), Murphy decomposition of Brier into reliability and resolution, AURC and risk at coverage 50% to 100%, DDx@0.9 (Sec. 4.3, 5.2, 5.3, Appendix C). Calibration here is trained, not post hoc; no temperature scaling, isotonic or Platt recalibration is applied (post-hoc calibration is described as complementary, Sec. 6).

## Cascade and escalation
Selective prediction only: AURC 0.0126 versus 0.2474 on multi-label; risk at the most confident 50% to 95% shown in Figure 4 (values only in the figure). No escalation or cost analysis.

## Option-name, cardinality, language and robustness tests
Candidate permutation at inference (classification top-1 agreement 0.90, counting 0.42, regression 0.67), restriction to two or four candidates (accuracy 0.87 and 0.73 at step 2424; chance 0.50 and 0.25) and gold removal (runner-up selected 0.88) (Sec. 5.4, Table 6). No option-name wording tests. Training shuffles Choice and Noul candidates; Score grids are never permuted. Detection (bounding boxes) was removed because the coordinate head collapsed to a constant box (Sec. 3.1, Appendix A).

## Cost and latency
Training wall clock only (Table 9); no inference latency or cost. 

## Code and data availability
Code at github.com/lytang63/OmniMed-Jev (Abstract). Source datasets are public.

## Authors' stated limitations (Appendix I and Sec. 6)
Bounded decisions only (no free text; detection not achieved); denser factorised supervision (155,729 targets from 23,558 images) plausibly explains part of the late classification crossover and is not ablated; four families and 726 held-out states do not establish clinical utility; retrospective data from the same sources as training; claims about direction of effect, not significance, for three of four families.
