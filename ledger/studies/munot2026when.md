# munot2026when

arXiv 2610.29217v1 (cs.AI), 21 Oct 2026. "When Multiple Choices Are Correct: Asymmetric Probability Allocation in Jev and Other Decision Models." (title block)
Author: Rushab Munot, independent researcher. Affiliation type: independent. (title block)

## Task and data
Probability allocation when a choice list holds several correct choices. Three datasets: MetaTool tool selection (2,795 one-correct, 497 two-correct, 995 no-correct lists), HotpotQA distractor validation set (7,405 questions, two supporting passages, lists of 2 to 10), ECtHR Task A of LexGLUE (655 one violated article, 192 with two to four, 153 none; ten articles per list). Gold labels as released by each dataset. Experiments: five identical copies of a correct choice in five cyclic permutations (25,695 lists per model; 3,292 MetaTool queries, 1,000 HotpotQA, 847 ECtHR); gap between correct choices on lists as released (ECtHR in ten cyclic permutations); yes/no per-choice calibration; single-threshold selection; no-correct-choice lists. (Sec. 2, Tables 2, 20)

## Models
Jev jev-1.13.0 via TypeSafe API; Liquid d1 (liquid/d1) and GPT-6 Luna Decisions (openai/gpt-6-luna-decisions) via Vercel AI Gateway, no vendor version published, "the models that the gateway served in October 2026". Same requests sent once to each model, no tuning, same instructions. (Sec. 2 Models)

## Metrics and intervals
Gap between highest and lowest correct-choice probability (percentage points), share of lists with every correct choice ranked above every distractor, share of those with a correct choice below 1/n, exact set accuracy at the best single threshold (chosen on the evaluation data, so optimistic), ECE over ten equal-width bins. 95% bootstrap intervals, 2,000 resamples of examples, Appendix J Table 22. (Sec. 2, Sec. 3, App. J)

## Calibration
ECE for one-correct lists (confidence): Jev 8 (MetaTool), 3 (ECtHR); Liquid d1 9, 1; GPT-6 Luna Decisions 14, 1 percentage points. Yes/no ECE 3 to 9 over all bins, 8 to 18 without the 0 to 0.1 bin. No post-hoc calibration. (Sec. 3, App. D, Tables 15, 16)

## Robustness
Identical-copy tests show position bias: Liquid d1 and GPT-6 Luna Decisions predict the first copy in 76% to 98% of answers; Jev 36% first on MetaTool and 56% last on ECtHR. Lists with no correct choice: Jev and Liquid d1 answer every list, mean confidence 0.49 to 0.87; GPT-6 Luna Decisions can refuse. Option order tested through cyclic permutations. English only. (Sec. 3, App. E, Table 5)

## Test-data exposure
Public pre-2026 datasets (MetaTool 2024, HotpotQA 2018, LexGLUE 2022); no contamination check.

## Cost, latency, cascade
Not reported. No cascade.

## Code and data
https://github.com/Rushab1/gr-jev (MIT; tag arxiv-v1; saved model responses not in repository). (App. K)

## Authors' limitations
Three hosted decision models only; generative models out of scope; three English datasets with dataset labels as correct sets; one threshold per dataset and one yes/no question per choice; other tasks and per-example thresholds left to future work. (Limitations)
