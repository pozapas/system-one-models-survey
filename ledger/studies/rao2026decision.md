# Rao & Callison-Burch (2026), "Decision Models vs. LLMs as Rubric Judges: Cheaper, Faster, and Wrong in the Same Places"

## Identification
- arXiv 2609.29769, saved copy is v3 [cs.CL] dated 13 Oct 2026 (header); first version 2026-09-24 (sweep list). Later versions add the Decider (run 7 Oct 2026), the whole-rubric, effort and higher-tier conditions, so some numbers post-date the first version. License arXiv perpetual non-exclusive. Full text fulltext/2609.29769.html and .txt.
- Authors Delip Rao and Chris Callison-Burch, University of Pennsylvania (byline). affiliation_type = academic. Funding DARPA SciFy and IARPA BENGAL; "not incentivized by TypeSafe ... Perplexity" (Ethics Statement).

## Task and data
- Rubric judging: decision models versus flash-tier LLM judges on nine panels from seven public benchmarks with human judgments, 5,003 (unit, criterion) pairs per judge (Section 3.3; Table A3). Binary panels RiceChem (819-pair panel; full set 8,392 pairs) and HealthBench (406 pairs). Ordinal panels ELLIPSE, FED-Turn, FED-Dialogue, HelpSteer2, LFQA, USR-TC, USR-PC (3,778 pairs; each a 10% or 20% unit sample, 25 to 258 units per criterion result) (Limitations, Samples).
- All judges run in the open-source AutoRubric harness with identical criterion texts, fixed in advance with no examples, rewording or tuning (Section 3).
- Four conditions: per-criterion LLM judging (main), whole-rubric, high reasoning effort, higher-tier judges (Section 3.2; Appendices N, O, P).

## Decision models
- Jev (TypeSafe): requests used the jev-latest alias; the main runs (19 Sep 2026) did not log the version; a same-day stability study logged jev-1.13.0 on all 2,250 requests (Appendix A, "Requests named the jev-latest alias"). Framings: Choice (matched judge), Noul, Score; priced at $0.042 per million input tokens, output free (Section 3.1). Vendor note that Jev may read scope and negation literally (jaggedness page).
- Perplexity Decider pplx-decider-v1.1-27b (open-weight fine-tune of Qwen3.8-27B, released 5 Oct 2026, run 04:21 to 04:36 UTC on 7 Oct 2026, $0.02 per million input tokens) (Section 3.1; Appendix R). Added after the Jev analyses; its claims were recorded about 2.5 hours before it answered any study item. Reported separately; the two decision models are not compared with each other.

## Comparators and tuning parity
- Three flash-tier LLM judges: GPT-5.6 Luna (gpt-5.6-luna, temperature enforced 1.0), Gemini 3.8 Flash (gemini-3.8-flash), DeepSeek V4.1 Flash (deepseek/deepseek-v4.1-flash via OpenRouter); undated identifiers, harness default system prompts, temperature 0 otherwise, vendor-default reasoning; main runs 19 Sep 2026 (Section 3.2). Higher tier (2 Oct 2026): GPT-5.6 Terra, Gemini 3.1 Pro (Preview), DeepSeek V4 Pro.
- Parity: identical criterion texts, but the judges receive different instructions and option orders (Limitations); no wrapper or few-shot tuning for any judge; the Decider got Jev's framings and wrapper unchanged. Binary panels use a Jev wrapper (definitions of MET/UNMET); Jev Choice was not run without the NA option. Disclosed asymmetry, no tuning on test data, but the 5-point parity margin and several analyses were chosen post hoc.

## Reference labels
- Human labels from each benchmark: ordinal pair label = raters' mean level rounded to nearest level, halves up (46.8% of ELLIPSE labels are half-way); binary = rater majority, or RiceChem teaching-assistant label (Section 3.3). Unanimous and split-rater pairs reported separately. Rater reference scores each rater against the rounded mean of others.
- Judges read the authors' rubric versions rather than the raters' own instructions; this may explain the shared offset (exploratory account, Section 5, Appendix H). HelpSteer2 correctness tracks overall helpfulness at r = 0.94; provenance alone predicts LFQA labels about as well as the judges.

## n, sampling, intervals
- Paired comparisons resample units 10,000 times for percentile intervals, Holm-corrected bootstrap p-values within each decision model's 27 comparisons. Separated = 95% interval of accuracy difference excludes zero; parity = 90% interval within 5 points (post hoc margin); otherwise inconclusive (Section 3.4). Table 1 itself reports point accuracies without intervals.
- Cascade gains: oracle thresholds (optimistic) and cross-fitted (50 random halvings) (Section 6).

## Key results
- Jev Choice 27 comparisons: 8 separated, 8 parity, 11 inconclusive; accuracy per panel in Table 1 (RiceChem 81.0, HealthBench 77.1, ELLIPSE 13.4, FED-Turn 56.2, FED-Dialogue 48.6, HelpSteer2 48.6, LFQA 68.7, USR-TC 62.0, USR-PC 56.4). Gemini is most accurate matched judge on most ordinal panels.
- Cost 29x (Luna), 325x (Gemini), 66x (DeepSeek) of Jev Choice's $0.063 over nine panels; wall time 30x to 220x (Section 4.2). Across all conditions LLM judges cost 16 to 357 times the decision models and take 5 to 350 times as long (Abstract).
- LLM verdicts repeat Jev's 84 most confident ordinal errors in 96.0% (baseline 50.3%); Decider 86.5% (47.9%) (Section 5.2).
- Cascades Jev-first gain at most 2.7 points (oracle, flash-tier), 1.7 with higher-tier fallbacks; Decider-first at most 1.7 (Section 6.2; Table 2).

## Calibration
- Measured on binary panels only: AUROC of P(MET) 0.80 to 0.86; ECE 0.056 to 0.096 (ten equal-width bins on RiceChem, eight on HealthBench), 0.062 to 0.089 over the full 8,392 RiceChem pairs (Appendix D; Table D1). Decider ECE 0.084 to 0.148, overconfident at both ends on HealthBench. No post-hoc recalibration. Ordinal panels: confidence AUROC for correctness 0.57 to 0.70 (0.49 on ELLIPSE) (Section 6.1).

## Cost and latency
- List/billed prices on run dates (DeepSeek billed through OpenRouter at 1.23 to 1.46 times its list-price estimate). Jev median request latency 0.18 to 0.20 s per request in the stability passes (Appendix A); Jev Choice 29 s wall time for nine panels at 8 requests in flight (Table B1). Decider wall time set mainly by Perplexity's rate limit.

## Cascade or escalation
- Section 6, Table 3, Appendix K: Jev-first and Decider-first confidence-gated cascades to each LLM fallback; cross-fitted cascade matching the best LLM judge costs under half of it on 7 of 9 panels (per-criterion), 4 of 9 whole-rubric; juries add nothing (Appendix J).

## Option-name, cardinality, language, robustness
- NA/CANNOT_ASSESS option included for Jev Choice; Jev never chose CANNOT_ASSESS on binary panels. Judging mode (per-criterion vs whole-rubric), reasoning effort (medium, high) and model tier varied; option order shuffled per pair by logged seed for LLM judges, Jev sees scale order. English only. Run-to-run: about 3% of Jev pairs flip verdict across five passes on RiceChem.

## Test-set exposure
- Public benchmarks released before 2026; authors say a judge "may also have seen the items or labels of these public benchmarks in training" (Limitations). The Decider's training manifest includes HelpSteer2 attribute labels, with no check against the panel items.

## Code and data
- Release described in Appendix M: judge code, frozen panel samples, one verdict record per judge and pair, scripts that regenerate every number offline. No repository URL found in the text or HTML links, so ledger code_available = partial.

## Paper's own limitations
- Observational, exploratory account of the offset; flash-tier zero-shot judges rather than best obtainable; single run per ordinal panel and no Jev rerun on ordinal panels; samples of 25 to 258 units per criterion; post-hoc margins; two decision models only; English only; unstated rater conventions and label rounding rule.
