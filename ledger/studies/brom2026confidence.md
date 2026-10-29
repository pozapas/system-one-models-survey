# brom2026confidence — Confidence Is Not a Promise: A Reference Audit of Typed Decision Models

arXiv:2610.36311v1 [cs.LG], 26 Oct 2026. Full text: fulltext/2610.36311.html and .txt. Long single-author audit paper (15 sections plus appendices A-G). The paper's own numbers are produced by five released scripts with seed 20261020 (Sec 5, Reproducibility).

## Authors and affiliation
Pedro Carvalho Brom; Department of Mathematics, Federal Institute of Brasília, Brazil (title block). Affiliation type: academic.

## Task and data
Primary: MASSIVE 1.1 test split in pt-PT and en-US; first 2,000 shuffled utterances (seed 13); each is a five-option choice question (gold intent plus four distractors); items 0-999 calibrate, 1,000-1,999 report (Sec 5). Extensions: 52 MASSIVE locales (Sec 8, Jev answered 1,000 report items in 50 more locales); four further domains (News Category headlines, financial tweets, Fake.Br, LIAR2) with 2-6 options (Sec 9); synthetic typing noise and greedy typo attacks (Sec 7); drift streams (Sec 10); M3 monthly series, direction of next value (Sec 10.5); explanation-fidelity coalition games (Sec 11). External check on 2,989 Portuguese and 3,003 English MASSIVE items outside the sample (Sec 6.3).

## Decision models evaluated
Jev 1.13 via API, answers collected 2026-09-26 and frozen; Jev 1.14 used only in the explanation front (Sec 5, Sec 14). Laya (open weights) at code commit 4066d5d, weights revision 55cf4c4: multilingual (mmBERT-base, 322M), English and typed-decisions (ModernBERT-large) checkpoints, and fine-tuned versions of the multilingual and typed-decisions checkpoints on 11,274 MASSIVE pt-PT items after removing 240 exact duplicates of test items (Sec 5, Table 2). Vendor documentation pages consulted 2026-10-20 and archived.

## Comparators and tuning parity
Laya is compared with Jev both un-tuned and after fine-tuning on in-domain labels; Jev gets no tuning and is used as returned, with no temperature scaling because its probabilities are rounded to two decimals; Laya gets a fitted temperature (Sec 4.2, Sec 5). The paper treats label count as the controlled variable (non-inferiority margin 2 points). The gate comparison (point rule, Beta lower-bound rule, Learn then Test, SGR) is a comparison among threshold rules, not among models. Exponential smoothing (ETS) is the M3 comparator.

## Reference labels
Dataset gold labels (MASSIVE intents, battery dataset labels, M3 realized direction). The paper does not describe annotation procedures; coded human_crowd (the majority precedent for MASSIVE rows in the ledger) for dataset gold labels and task_outcome for M3.

## n and intervals
1,000 report items per locale and language; Wilson intervals for accuracy, Clopper-Pearson for the vendor statement, percentile bootstrap (2,000) for AUROC, exact McNemar for paired differences (Sec 5). Gate rules evaluated on 10,000 calibration draws against a plug-in population (the 2,000 items), with one-sided 95% Clopper-Pearson upper bounds; 190 exchangeable evaluations in total; item-level versus Monte Carlo variance separated (Sec 5, Sec 6.3). Many analyses are labelled exploratory or registered; Table 1 gives each claim's status.

## Test-data exposure
MASSIVE and the battery datasets are public pre-2026 datasets; no contamination check for Jev reported. Near duplicates may remain in the Laya fine-tuning set (Sec 14).

## Cost and latency
Jev: US$0.016 per 1,000 decisions at the vendor price (mean 384 input tokens, US$0.042 per million input tokens) (Table 5). Jev latency not measured. Laya: 12.7 ms per item on CPU; fine-tuning about 17 s on one RTX 5090 at 4,000 labels. Costs for the authors' own API calls are also stated in Sec 7-8 and are not recorded in the ledger.

## Calibration
15-bin ECE as returned and after temperature scaling, Brier, NLL, AUROC of confidence (Table 6). Jev ECE 0.020 (pt) and 0.019 (en); AUROC 0.905 and 0.894. Jev is evaluated as returned; its answers are rounded to two decimals so about three quarters put 1.00 on one option (Sec 4.2). Laya: temperature fitted by Newton's method on the calibration half; temperatures 0.40 to 1.77.

## Cascade or escalation
Selective gate (Sec 4.5, 6.3): accept when confidence is at least a threshold, escalate otherwise. Point-estimate threshold breaks a 95/99% accuracy promise in 147 of 190 evaluations; Learn then Test in none; Beta lower-bound rule decides more items than Learn then Test in 128 and fewer in none. For Jev the Beta rule qualifies no threshold in 52 to 61% of splits at 99%. Lowering Jev coverage from 100% to 90% removes 32 of its 53 errors at about 3 reviews per avoided error. No cascade to a stronger model.

## Option-name, cardinality, robustness tests
Typing noise and greedy typo attacks on Laya (Jev measured only under random noise): Jev loses 0.7 to 2.2 points; the promise calibrated on clean text breaks in 9 of 12 noisy conditions for Jev (Sec 7). 52 locales: promise holds in 8 of 51 for Jev calibrated in en-US (Sec 8). Domain battery: Jev ECE 0.076 to 0.171 (Sec 9). Option cardinality from 2 to 6 across domains; no option-order test.

## Code and data availability
The paper states it releases frozen answers of both deciders with a datasheet, a promise check and the code that produces every number (Abstract, contribution 8); no URL appears in the extracted text.

## Authors' limitations (Sec 14)
One dataset (MASSIVE, five options) for most measurements and one dataset per further domain; only exact duplicates removed from fine-tuning set; occlusion explanations and coalition games delete words; Jev measured mostly in 1.13 with rounding to two decimals; gate evaluated on random splits of one fixed sample so exchangeability is assumed; synthetic noise; cost ratios are illustrative; under drift or correlated items neither the Beta rule nor Learn then Test keeps its promise without further assumptions.
