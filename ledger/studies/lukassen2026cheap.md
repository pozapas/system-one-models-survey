# lukassen2026cheap: Cheap, Consistent, Calibrated, but Biased? Typed Decision Models as Judges

arXiv:2610.18122v1 [cs.CL], 13 Oct 2026 (license arXiv perpetual non-exclusive). Full text: `fulltext/2610.18122.html` and `.txt`. Extractor batch V12.

## Authors and affiliations

Fabian Lukassen (University of Göttingen), Christoph Weisser (Bielefeld University of Applied Sciences and Arts, HSBI), Alexander Silbersdorff (University of Göttingen) (author block). Affiliation type: academic.

## Task and data

Independent evaluation of typed decision models (TDMs) as pairwise judges. Reuses the CALM benchmark's items, perturbations, instruction and metrics (Ye et al. 2025; CALM commit f6248e9) for nine of CALM's twelve biases (position, verbosity, compassion fade, bandwagon, distraction, fallacy oversight, authority, sentiment, diversity), plus three additions (verbosity on better, authority on better, neutral note) (Sec. 3.1, Table 2). Two CALM datasets: the fact-related set, 533 items from GSM8K, MATH and ScienceQA with two responses written by GPT-4-Turbo (verbosity and fallacy oversight use 500 items, sentiment 150), and the alignment set, 439 questions from five public DPO datasets (Sec. 3.1). The authors shuffle response order so the better response is first in half of the items (departure from CALM). Design: 13,251 perturbed prompts plus 972 original prompts sent twice = 15,195 requests per model and format; each TDM receives three formats (CALM, native, decomposed), 364,680 requests for the eight TDMs (Sec. 3.2).

## Decision models evaluated and versions

Eight TDMs through OpenRouter's Decisions API, "offered for choice questions in early October 2026" (Sec. 3.2). Version strings as returned (Table 6): typesafe/jev-1.13-20260917 (Jev 1.13); jaredpalmer/kev-4b-20260924; togethercomputer/tev1-4b-experimental-20260923; upstage/solar-decide-20260928; liquid/d1-20260930; perplexity/pplx-decider-v1.1-27b-20261006; cloudflare/clef; cloudflare/clef-flash. Seven LLM judges: GPT-3.5 Turbo, GPT-4o (2024-05-13), GPT-6.1 Sol, Claude Sonnet 5.5, Claude Haiku 5.5, Gemini 3.8 Flash, Qwen3.8-27B; settings in Table 5; costs as reported by OpenRouter in October 2026. Run dates: October 2026 (Limitations: "our results describe the models of October 2026"); individual run dates not listed.

## Comparators and tuning-budget parity

Same CALM instruction for all judges (compare on six criteria, ignore order, length, names). LLM judges write a short explanation ending in a verdict; TDMs return probabilities for A and B, converted from CALM's instruction into one question (CALM format), or into per-field (native) or six-question (decomposed) requests. No tuning of any judge; three LLM judges accept no temperature and run at provider default, two use hidden reasoning set to low effort (Limitations). A 50/50 TDM answer (|pA-0.5| < 1e-5) is treated as no verdict and dropped (Table 7; three TDMs always return A on ties).

## Reference labels

Fact-related set: correct final answers from GSM8K, MATH and ScienceQA; both responses written by GPT-4-Turbo so that the better one is clearer (synthetic construction). Alignment set: preference datasets' chosen/rejected labels (administrative field), which "were made for training, and some rejected responses may be as good as the chosen ones" (Limitations). Bias tests compare a judge with itself (invariance), so they do not depend on labels.

## n, sampling, intervals

n as above. Intervals are 95% percentile bootstrap over items with 10,000 resamples (Sec. 3.3). Bias defined by the excess E = CR - RR (consistency minus robustness rate); a bias exists only if the lower end of the 95% interval of E exceeds delta = 0.05 (not corrected for multiple tests); significance by within-item permutation test with Benjamini-Hochberg FDR 5%. Accuracy and calibration numbers in Tables 3 and 21 carry no intervals.

## Test-set exposure

All items public (CALM released 2025; underlying datasets older). "Since all items are public, the LLMs and the TDMs built on them may have seen some of them during training" (Limitations).

## Cost and latency

Table 22: Jev 1.13 CALM format 2.2 minutes wall clock for 15,195 requests with 32 parallel requests, US$0.68, US$0.045 per 1,000 requests, median latency 0.25 s; LLM judges US$0.311 (Haiku 5.5) to US$7.312 (GPT-4o) per 1,000 judgments, median latency 2.33 to 5.79 s. At the median a 2026 LLM judge costs 37 times as much as a TDM and takes six times as long (Sec. 4.4). Latency measured at the stated parallelism through OpenRouter, so it includes API overhead.

## Calibration

Table 21 (original prompts, CALM format): ECE with 10 equal-width bins on the confidence (probability of the chosen response), Brier score and log loss of P(R1). Jev 1.13: alignment accuracy 0.78, confidence 0.83, ECE 0.081, Brier 0.169, log loss 0.63; fact-related accuracy 1.00, ECE 0.030, Brier 0.008. Range of ECE on alignment set across TDMs 0.07 (D1) to 0.25 (Solar). Calibration does not go with less bias (App. I). No post-hoc recalibration.

## Cascade or escalation

Not tested, but the authors support the cascade of Li et al. (2026): in all tests but two, 30% of verdicts given with probability below 0.6 flip against 3% of those above 0.9; odds ratio per further 0.1 of confidence 0.47 [0.45, 0.48] (Sec. 4.3). Asking in both orders and averaging probabilities removes position bias by construction, doubling cost; accuracy change -0.2 to +3.8 points; Jev +1.2 [-0.6, +3.2] (App. M, Table 25).

## Option-name, cardinality, order, robustness

Position bias: all eight TDMs show it, Jev with the smallest (excess 8) together with Perplexity Decider, versus at most 6 for any 2026 LLM judge (Sec. 4.1, 4.2). Format robustness: moving the same text between formats changes 4.5 to 5.5% of verdicts of the median model; Jev's layout change 0.8% (native) and 1.3% (decomposed) (Table 3). Option set is always two (A, B).

## Code and data availability

https://github.com/fabian-lu/TDM_as_a_Judge (footnote 1 and "Code & Data" link in the author block); notebooks contain every request and reply of the LLM judges (App. J).

## Authors' stated limitations

Only pairwise comparisons; every item has a reference, so reference-free judging is untested; no human verification beyond CALM; rewrites by GPT-4-Turbo may change more than intended (sentiment confounded with clarity); fake citations; preference datasets made for training; public items; non-uniform LLM judge settings; flips describe output change, not cause; training data unknown; 50/50 tie handling is inferred; results describe October 2026 models (Limitations).
