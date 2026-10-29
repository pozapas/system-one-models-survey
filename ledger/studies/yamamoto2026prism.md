# yamamoto2026prism: PRISM, Calibrating Black-Box Judges with Counterfactual Probes

arXiv:2610.18389v1 [cs.LG], 13 Oct 2026 (CC BY 4.0). Full text: `fulltext/2610.18389.html` and `.txt`. Extractor batch V12.

## Authors and affiliations

Kakei Yamamoto (MIT Laboratory for Information and Decision Systems, Statistics and Data Science Center, EECS; work done as an intern at Sakana AI), So Kuroki (Sakana AI) (author block). Affiliation type: mixed (university and company).

## Task and data

Application paper. PRISM (Probe-based Residual Inference of Scoring Misalignment) holds the evaluated content fixed, asks the judge to emphasise or de-emphasise individual attributes (length, formality, extractiveness, hedging, accuracy, coherence etc.), measures overall score changes as a surrogate Jacobian and fits a ridge correction to human labels; inference needs only baseline and probed overall scores (Sec. 1, 2). Jev is used as a typed-rating judge: "Jev-1.13 returns an expected score over five categories, coded 0-4, through the Decisions API"; the individual-summary call contains all 38 scoring questions (one baseline, two wordings for each sign of eight attributes, five neutral clauses) (App. A.2). Sol (gpt-5.6-sol) is the main non-typed comparator judge; Sonnet and Gemma are supplementary.

Benchmarks (Sec. 3, 3.1): SummEval (100 documents x 16 summaries = 1,600 pairs, target is the average of four expert ratings); HANNA (96 prompts x 11 stories, three raters on six criteria); additional pairwise-accuracy benchmarks for Jev only: Topical-Chat (34 confirmation contexts), HelpSteer2 (188), MT-Bench (81), JudgeBench (287). Metric: mean within-document (SummEval) or within-prompt (HANNA) Spearman correlation, five outer folds with training on the remaining groups; pairwise accuracy on the additional benchmarks with reference ties excluded and predicted ties half credit.

## Decision models evaluated and versions

Jev requests use the alias typesafe/jev-1.13; the returned version is typesafe/jev-1.13-20260917 (Table 5, App. A.1). Sol gpt-5.6-sol (reasoning effort none, temperature 0 or 1); Sonnet anthropic/claude-sonnet-4.5; Gemma google/gemma-4-31b-it. Interfaces: TypeSafe Decisions API for Jev; OpenRouter (and the direct OpenAI API for some Sol runs) for others. Model-version dates beyond the Jev returned version are not given; the analysis environment was inspected on 13 October 2026.

## Comparators and tuning-budget parity

Rubric-based baselines: SAJA broad and granular (random forest on criterion ratings fitted to human labels) and G-Eval (averaged normalised criterion scores). PRISM is fitted to human labels and uses extra probe calls, so Vanilla (uncalibrated) versus PRISM is not budget-matched; SAJA is fitted too. G-Eval is not fitted. "Additional probe calls incur inference cost, motivating comparisons under matched budgets" (Limitations). Regularisation chosen by validation within training folds; for additional benchmarks a development set is used for probe screening and regularisation (Sec. 3). The comparison across judges mixes protocols (single-candidate expected ratings for Jev, batched pointwise integer ratings for Sol on SummEval).

## Reference labels

SummEval: expert ratings (coherence, consistency, fluency, relevance), averaged. HANNA: three human raters on six criteria. Topical-Chat/USR, HelpSteer2, MT-Bench, JudgeBench: released human or benchmark reference judgments ("We reuse released annotations rather than collect new human ratings", App. B). Coded human_adjudicated for SummEval, human_crowd for HANNA.

## n, sampling, intervals

Intervals are 95% document or prompt bootstrap (2,000 resamples); paired intervals for differences; fitted methods evaluated on the same five held-out groups. "Significantly improve" statements rely on paired intervals that are unadjusted for multiple comparisons (Table 15 caption). Table 3 additional benchmarks: "The paired 95% gain intervals include zero" for most (Table 15: Topical-Chat +0.002 [+0.000, +0.005]; HelpSteer2 +0.016 [-0.003, +0.040]; MT-Bench +0.010 [-0.011, +0.033]; JudgeBench +0.002 [-0.003, +0.009] against Vanilla).

## Test-set exposure

All benchmarks public and pre-2026 (SummEval 2021, HANNA 2022, Topical-Chat/USR 2020, HelpSteer2 2024, MT-Bench 2023, JudgeBench 2025). "Benchmark contamination cannot be ruled out" (Limitations). Release-level data notices checked 13 October 2026 (Table 10).

## Cost and latency

Not reported per decision. Jev individual-summary call contains 38 scoring questions; repeated runs; no latency or per-call cost for Jev. Aggregate research API usage reported (about 1.4 million responses) but it is the authors' own spending and is not extracted.

## Calibration

Here calibration means correcting score bias toward human ranking, not probability calibration; no ECE or Brier on Jev's probabilities. Jev probabilities are converted to an expected score. Post-hoc correction is a ridge regression on probe responses ("other": learned linear correction fitted on human labels).

## Cascade or escalation

None.

## Option-name, order, robustness

Probe signal above repeat variation: for Jev's 14-property bank pooled RMS ratio 2.51, per-attribute ratios from 1.24 (hedging) to 4.14 (extractiveness) (Sec. 2.2, Figure 2a). Presentation-order sensitivity in batched pointwise scoring: probe-response correlation 0.68 between repeats of one order, 0.32 across orders, 0.78 after averaging eight orders; uncalibrated expert Spearman 0.587 for one order and 0.647 for eight (Sec. 2.2). Probe attribute bank robustness: quality (8) 0.705, style (8) 0.710, combined (16) 0.711 (Table 4b).

## Code and data availability

No code repository for PRISM found in the text or links (only the HANNA benchmark repository and LaTeXML links). Coded no.

## Authors' stated limitations

Rubric-free calibration of text judgments with human labels; probe calls add inference cost; transfer across tasks, model versions and rater populations untested; benchmark contamination cannot be ruled out; targets overall scores for fixed inputs, not biases from joint candidate presentation (Limitations).
