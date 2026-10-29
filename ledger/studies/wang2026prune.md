# wang2026prune: Prune First, Decide Fast, scalable semantic query processing with JEVDB

## Identification

- arXiv 2610.02046v1, cs.DB, 01 Oct 2026 (header); title block dated September 2026. Full text: fulltext/2610.02046.html and .txt.
- Authors: Zhengle Wang, Hanxu Yan, Fuheng Zhao, Chunwei Liu (corresponding, chunwei@purdue.edu). Affiliations: Purdue Data & AI System Lab (PDAIS) and University of Utah. Affiliation type: academic. Footnote 1: JEVDB "is an independent academic research project developed by Purdue University, and is not affiliated with or endorsed by TypeSafe AI."

## Task and data

- Semantic database operators (filter, classify, rank, join) executed by typed decision primitives (Noul, Choice, Score) with Yannakakis-style semijoin reduction, Semantic Bloom Filters (SBFs) and escalation of uncertain cases to a reasoning model (Section 3).
- SemBench: all 21 queries from SemBench's Table 4 that operate on text and structured attributes (Movie, E-Commerce, MMQA, Cars), official per-scenario scale factors; image queries excluded (Section 4.1). Quality per query: F1, 1/(1+relative error), adjusted Rand index, macro-F1 or Spearman correlation as in SemBench.
- Shelob (new, built by the authors): TPC-DS SF1 augmented with textual return reports, known-issue bulletins and release notes; five queries (Q1-Q5) on tiers XS, S, M; aggregate candidate space 81,528 pairs (XS), 332,262 (S), 1.37 million (M); largest single join 540K candidates; full SF1 would expose 18.1 million report-bulletin pairs (Section 4.1, Table 2). 1,200 s execution limit; F1 against "Shelob's reference answers", ambiguous references counted as neither true nor false positives. How the reference answers were produced is not described in the text read.
- Test-set exposure: SemBench is a 2026 public benchmark (Lao et al. 2026); Shelob is new. No contamination analysis.

## Systems evaluated

- JEVDB-Flash: Jev jev-1.13.0 at a fixed 0.5 threshold, no reasoning model; Noul for filters and joins, Choice for classification, Score for ranking; pack layout with k = 100 and 64 workers on Shelob, 20 concurrent workers on SemBench (Section 4.1).
- JEVDB (quality-controlled): Jev fast path, pairwise SBF screening, selective escalation to gpt-6-luna; the cascade calibrates 400 items per predicate (Section 3.3.3 says a sample of, for example, 200 pairs) with tolerated recall and precision loss 0.05 relative to the calibration judge; second stage packs 16 items per request with 64 concurrent requests; optional condition index over 20,558 documents costing 15 s and $0.54 of Jev inference (Section 4.1).
- Baselines: LOTUS, Palimpzest, ThalamusDB. On SemBench, published SemBench numbers with Gemini 2.5 Flash, mean of five runs, four queries not supported by ThalamusDB. On Shelob, LOTUS 1.1.3, Palimpzest 0.8.2 and ThalamusDB 0.1.15 re-run with gpt-6-luna and SemBench-style configurations (Section 4.1).

## Tuning-budget parity

Not matched. SemBench baselines are the benchmark's published runs (Gemini 2.5 Flash, five-run mean) against a single JEVDB-Flash run; concurrency set to match the baseline setting (20 workers). On Shelob, baselines use gpt-6-luna while JEVDB-Flash uses no reasoning model. Prompts for the baselines are the benchmark configurations. LOTUS embeddings computed on CPU; the authors note GPU would reduce LOTUS latency (Section 4.1). The calibration judge (gpt-6-luna) labels the cascade's calibration sample; final F1 is against reference answers.

## n, sampling design, intervals

21 SemBench queries, 15 Shelob query-tier runs (single run each, no intervals, no repeats stated for JEVDB). Bold best-per-query quality compared at two decimals.

## Key results

- SemBench aggregate (Section 4.2, Table 3): JEVDB-Flash 41.50 s and $1.06 vs LOTUS 3,709 s and $14.28, Palimpzest 2,988 s and $19.81; speedups about 89.4x and 72.0x, cost reductions about 13.5x and 18.7x. ThalamusDB supports 17 queries, 2,434 s and $3.01. Fastest on all 21 queries, cheapest on 19. Quality best or tied best on 14 of 21, within 0.02 on four more; abstract says "equal or superior quality on 18 of 21 queries". The Conclusion states aggregate reductions of about 88x, 71x, 12.5x and 17.4x, which differ from the body's 89.4x, 72.0x, 13.5x and 18.7x.
- Shelob (Section 4.3, Table 4): only 14 of 45 baseline runs complete in 1,200 s, none at M. JEVDB-Flash completes all 15 runs in 12.38, 64.69 and 288.55 s total for XS, S, M at $0.56, $2.30 and $9.42, mean F1 66.3, 64.0 and 63.2 (Q1 85.3-88.9, Q2/Q3 71.7-73.8, Q4 23.8-30.4). Full JEVDB completes all 15 runs, F1 91.5-98.7, mean F1 97.5, 96.1 and 95.7 at XS, S, M, latency 320.6, 727.8 and 2,616 s, model cost $0.37, $1.16 and $5.81 (excluding one-time $0.54 index). Note JEVDB-Flash costs more than full JEVDB at tier M because it evaluates all pairs without SBF screening.
- Pruning: SBF screening removes 87.4% of 1.78M candidate pairs, leaving 224K; condition-index scoring cuts escalations to the reasoning model from 194K to 87K (55.2% reduction).
- Calibration: Jev's probabilities are described as calibrated but no calibration metric (ECE, Brier, reliability) is reported. Thresholds [l, h) are set by an online calibration sample against an LLM judge (Section 3.3.3).

## Option-name, cardinality, language, robustness tests

None.

## Code and data availability

"An interactive query simulator, source code, and benchmarks are previewed at https://jevdb.org" (Abstract). Recorded as partial.

## Cost and latency

Cost from measured token counts and list prices at the time of the runs: Jev $0.042 per million input tokens; gpt-6-luna $0.10 input and $0.50 output per million tokens, cached input $0.01 and cache writes $0.125; end-to-end wall-clock latency including relational processing and model requests (Section 4.1). SemBench baseline costs are the published ones.

## Authors' own limitations

No separate limitations section. Section 5 notes multi-modal inputs (excluded SemBench image queries) and semantic-aware optimisation as future work. The text states fixed-threshold Jev decisions "do not provide uniformly high quality across predicates" (Section 4.3).
