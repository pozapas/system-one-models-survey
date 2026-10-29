# paschalides2026jev — To Jev or Not? Evaluating the Accuracy and Efficiency of Structured Decision Models for Hate-Speech Moderation (HateDecide)

arXiv:2610.03324v1 [cs.CL], 02 Oct 2026. HTML from https://arxiv.org/html/2610.03324 (fulltext/2610.03324.html and .txt).

## Authors and affiliation
Demetris Paschalides, George Pallis, Marios D. Dikaiakos; University of Cyprus, Computer Science Department, Nicosia, Cyprus (front matter). Affiliation type: academic.

## Task and data
Binary hate/non-hate classification on four English datasets, plus HateXplain three-class (hate/offensive/normal), Dynamic conduct type (six classes) and HateCheck referenced group and general-vs-directed attributes (§3.1, Tables 1, 5). Test sets (after label aggregation and de-duplication, Table 1): Dynamic 4,120 (2,268 hate / 1,852 non-hate), MHS 3,203 (782 / 2,421), HateXplain 1,924 (594 / 1,330), HateCheck 3,728 (2,563 / 1,165). Train/validation data only feed the supervised baselines. Official Dynamic and HateXplain splits kept; seeded 80/10/10 split for MHS; texts linked into near-duplicate and perturbation groups, kept within one partition (§3.1). Interventions: dataset-specific definition vs none, and direct (A) vs decomposed (B) classification with fixed rules (§3.3, Table 2).

## Decision models evaluated
Six decision-model configurations (Table 3, §3.2): Jev, "specifically jev-1.13.0", hosted API, undisclosed architecture; Laya (ModernBERT-large, local); Decider (Qwen 2B, local); SemIf over Qwen3.5-2B and over Qwen3.5-4B (an interface that reads answer-token probabilities from an unmodified LLM); Bespoke-Nimble-9B (Qwen3.5-9B + LoRA, NF4). References list "Accessed: September 25, 2026" for Laya, Nimble, Decider and SemIf and 24 September 2026 for the Jev blog; no revision hashes. Baselines: CoPE-A-9B (policy-conditioned labeller, NF4), BART-large-MNLI (zero-shot), GPT-5.6 Luna and GPT-6 Sol (commercial LLMs, constrained JSON, no explanations), TF-IDF+LR and fine-tuned DistilBERT (supervised, trained on one dataset, validation-selected).

## Comparators, tuning-budget parity
Decision models and commercial LLMs receive the same definition, question and options (§3.2); commercial LLMs return constrained JSON without explanations. Supervised baselines are trained on the datasets' own labels (Appendix F: 5,000-post subset for the three-class run) and tested cross-dataset. Instructions and decomposition rules were written by the authors from dataset documentation; HateXplain definition is a proxy from Davidson et al. (§3.1, §5.1). A threshold-tuned direct control (A*) uses 200 validation texts per model and dataset (App. G). No prompt tuning on test data is described.

## Reference labels
Dataset annotations: Dynamic (annotator-written, model-in-the-loop texts), MHS (about 3 annotators per comment, strict-majority yes/no kept), HateXplain (majority label of annotators), HateCheck (constructed functional test cases, 29 functional tests) (§3.1). Coded human_crowd for the first three and synthetic for HateCheck.

## n, sampling, intervals
Full test partitions, fully paired across models and conditions (§3.4). Differences in macro-F1 analysed with 10,000 group-resampling bootstrap draws and Bonferroni-widened intervals (48, 28, 30, 10 comparisons for commercial, definition, decomposition analyses) (§3.4). Headline macro-F1 values in Table 4 carry no intervals; only paired differences are tested. Jev ablation controls (Table 11) use 800 texts per dataset.

## Test-data exposure
Public datasets from 2019 to 2021 era releases; the authors state "prior training exposure remains uncertain" and that out-of-the-box does not establish unseen data (§5.1 Limitations). No contamination check.

## Cost, latency, hardware
Median complete-decision latency on HateCheck (N = 3,728), one text at a time: Laya 48 ms, SemIf-4B 184 ms, Jev 336 ms, Luna 844 ms, Sol 1,426 ms (§4.4). Hosted cost per 1K texts: Jev $0.033, Luna $0.120, Sol $1.177; "Jev scores 1.6 macro-F1 points below Sol at ~97% lower recorded cost" (§4.4). Local models on an NVIDIA T4 (16 GB), two Xeon Gold 6230, 96 GB RAM; local inference has no monetary cost assigned (§3.4). Decomposition raises Jev's cost by 64% (HateCheck) to 139% (Dynamic) with latency up at most 9% (§4.4).

## Calibration
Not analysed (no ECE). Threshold-tuned control only (App. G).

## Cascade
Exploratory selective routing of cached predictions: Laya answers except the fraction with smallest probability margin, which goes to a commercial model. Referring 20% to Sol raises Laya's macro-F1 from .658 to .729 (Dynamic), .696 to .721 (MHS), .730 to .763 (HateXplain); Luna lowers HateXplain to .714. Referral fractions not selected on development data, cascade latency not measured end to end (App. I).

## Robustness / other
Definition sensitivity: the dataset-specific definition changes 2.8% to 28% of predictions across decision models; 8 of 28 comparisons significant gains, 8 significant losses (§4.2). Decomposition significantly improves in 6 of 30 comparisons, lowers in 11 (§4.3). No option-name, cardinality or language tests; English only.

## Code and data availability
Not stated in the text read (no repository URL for HateDecide found). Datasets are public.

## Paper's own limitations (§5.1)
Instructions and rules reflect the authors' reading of documentation, including a HateXplain proxy definition; component answers lack human annotations; agreement with annotations is not adherence to a policy; English only; HateCheck is synthetic test cases so cost-quality results need confirmation on everyday traffic; prior training exposure uncertain.

## Notes for the grader
Model names GPT-5.6 Luna and GPT-6 Sol are as printed in the paper. Jev is the only hosted decision model; a single run date is not stated beyond reference access dates (24-25 September 2026).
