# Konak (2026), "More Features Are Not More Evidence: Limits of Training-Free Human Activity Recognition with Jev"

Coder: batch V04. Full text: fulltext/2609.36154.html and .txt (arXiv HTML v1).

## Identification
- arXiv 2609.36154v1 [cs.AI], 28 Sep 2026; CC BY 4.0.
- Author: Orhan Konak, Hasso Plattner Institute, University of Potsdam (author block). Affiliation type: academic. The paper declares no external funding and no conflict, and states that "TypeSafe AI did not fund or support this study, and access to Jev was obtained through the publicly available API" (Section 7).

## Task and data
- Training-free human activity recognition from five-second accelerometer windows (100 samples at 20 Hz, no overlap). Datasets: WISDM watch (UCI507, 18 classes, 51 subjects), UCI341/HAPT smartphone (6 classes, 30 subjects), PAMAP2 hand/wrist (12 classes, 9 subjects) (Section 3.2, Table 1).
- Matched benchmark: 50 windows per class, class-balanced, selected deterministically across subjects independent of model predictions: 900 WISDM, 300 UCI341, 600 PAMAP2 = 1,800 windows; 5,400 Jev requests (three representations each) (Section 3.2, 3.4).
- Representations: R1 20 numerical features, R2 32 numerical features, R3 deterministic English rendering plus the complete R2 values (Section 3.3). The R3 deviation (JSON suffix retained) is documented, so R3 - R2 does not isolate semantics.
- Reference label: activity labels of the public datasets (annotation by recording protocol; coded administrative_field).
- Test exposure: public pre-2026 datasets; contamination of provider pretraining "cannot be excluded" (Sections 2.2, 7).

## Decision model
- "Jev uses the pinned identifier jev-1.13.0 and the TypeSafe System One endpoint" (Section 3.4). One Choice question with the native class names in canonical order, no descriptions, no labeled examples, retrieval or prompt tuning. No run dates stated beyond the reference-list access date 2026-09-26 for the vendor blog. Completed in one run with no retries.

## Comparators and tuning parity
- Generative baseline Claude Sonnet 5 (structured output restricted to the same vocabulary, same instruction, same payloads); no probabilities from it. Supervised references trained with leave-one-subject-out on the complete eligible population: Random Forest (500 trees, R2 features), SVM (RBF), 1D-CNN. Training-free models and supervised references are not tuning-matched by design. No prompt variants were tried ("No trial of other configurations is implied", Section 7).

## Results
- Table 2 (95% subject-cluster bootstrap): macro-F1 for Jev R3 0.0378 [0.0341, 0.0414] WISDM, 0.1184 [0.0989, 0.1363] UCI341, 0.0893 [0.0711, 0.1116] PAMAP2; RF 0.7057, 0.8899, 0.8041; SVM 0.6970, 0.8869, 0.7586; CNN 0.6857, 0.9067, 0.7504; Claude R3 0.0891, 0.2379, 0.1575. Jev R2 collapses to near-single-class prediction (899/900, 300/300 and 595/600 windows to walking; UCI341 R2 macro-F1 0.0476 equals the collapsed value 2/[K(K+1)]).
- Probability audit (Table 3, valid vectors only): 86 of 5,400 probability vectors fail the sum-to-one and range criterion; native choice and probability argmax disagree in 96 cases. R3: ECE 0.2532, 0.3489, 0.1294; multiclass Brier 1.0571, 0.9400, 0.9319; AUROC of max probability for argmax correctness 0.5803, 0.6750, 0.5859; mean max-probabilities 0.3667, 0.5844, 0.2952 against argmax accuracies 0.1135, 0.2405, 0.1658.
- Cost and latency (Table 4): Jev medians 0.291 to 0.300 s over nine conditions (p95 0.480 to 0.668 s; maximum 5.335 s), Claude 1.440 to 1.558 s; Jev USD 0.035 to 0.071 per 1,000 windows at list price USD 0.042 per million input tokens, Claude USD 1.545 to 3.547. Concurrency one, request-to-response wall time including network effects; no hardware controlled.
- Post-hoc fusion with RF (Section 5, Figure 4; designed after seeing main results, frozen before scoring): lambda = 0.20 macro-F1 change +0.0070 [0.0024, 0.0125] on WISDM, -0.0103 [-0.0253, 0.0034] on UCI341, -0.0043 [-0.0125, 0.0042] on PAMAP2. Complete-case subsets 890, 291, 591 windows.

## Sampling design and intervals
- Subject-cluster bootstrap with 10,000 replicates and seed 2026; paired comparisons share draws. Intervals are "descriptive" and exclude model-service variability; one completed response per case. No significance tests. Brier, NLL, ECE and AURC are point estimates without intervals.
- Main protocol frozen in version control before inference ("pre-inference protocol freeze", not a registered preregistration). Hybrid analysis explicitly post hoc and exploratory.

## Calibration and cascade
- Ten-bin equal-width ECE on valid vectors (bins [0,0.1) to [0.9,1]); no recalibration fitted. Selective-prediction risk-coverage curves (Figure 3). No cascade or escalation rule evaluated; the fusion analysis is a linear probability pool with a fixed weight grid.

## Robustness
- Three representations (R1, R2, R3) and three datasets are the robustness axis. No option-order, option-name or language tests; class names are the native dataset labels and some are terse (e.g. "teeth", "soup", "catch"; Section 6.2).

## Code and data
- "Code, evaluation scripts, and derived artifacts ... have been prepared for public release. The corresponding archival record will be made available separately" (Section 7). No URL; coded partial.

## Authors' stated limitations (Section 7)
- One pinned Jev version, one generative baseline, three datasets, one completed response per case, no alternative prompts; class balancing, clean activity boundaries, five-second windows; WISDM threshold fitting uses the unlabeled evaluation population; contamination cannot be excluded.
- The paper discloses a list-price cost of the full Jev run; not extracted as it is the author's own spend.
