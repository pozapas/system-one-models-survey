# Perifanis, Pavlidis and Symeonidis (2026), "SeLMRoute: Probabilistic Semantic Evidence for Large Language Model Routing"

## Identification
- arXiv 2609.34736v1 [cs.AI], 28 Sep 2026 (header). License CC BY 4.0.
- Authors: Vasilis Perifanis (Indigma Innovations; Democritus University of Thrace; Athena Research Center), Nikolaos Pavlidis (Indigma Innovations; Democritus University of Thrace), Symeon Symeonidis (Democritus University of Thrace) (byline). affiliation_type = mixed (company and universities).
- Code: https://github.com/Indigma-Innovations/SeLMRoute (Abstract). code_available = yes.

## What the paper is
- A router, not a decision-model evaluation as such: SeLMRoute asks a typed decision model (JEV, the "decision model" the abstract leaves unnamed; the body names JEV) 16 fixed probe questions about each query (8 binary Noul, 8 four-level Score; plus a seventeenth Choice task-family question used only for diagnostics), keeps the probability masses as a 40-feature semantic state, and trains a CatBoost performance learner to predict each candidate LLM's accuracy; routing then picks the best predicted candidate (Sections 3.2, 4.1). The Jev-related quantities are therefore (a) the downstream routing accuracy with a Jev-derived semantic state versus other representations, (b) a "JEV-Direct" baseline where Jev picks a model from anonymised candidate profiles, (c) a Jev versus Laya backend swap, (d) extraction latency and token cost. Included because Jev's probabilistic outputs are measured on a stated task against stated reference outcomes. Jev's own per-probe accuracy is not measured (no gold for the probes).

## Task and data
- LLMRouterBench performance-oriented setting: 15 datasets, 20 candidate models, frozen bundle of 11,481 queries and 229,620 candidate outcomes (published count 11,480; the extra record is in the MMLU-Pro bundle) (Section 4.1, Table 2). Cost-aware setting: 13 flagship models, 10 datasets, 12,446 queries, 161,520 observed outcomes (Section 4.11). Reference = observed per-instance correctness scores of each candidate model supplied by LLMRouterBench (task_outcome).
- Grouped evaluation: group = (dataset, normalized query text), 11,423 unique groups; five 70/30 grouped splits with seeds 42, 999, 2024, 2025, 3407, and a five-fold grouped out-of-fold (OOF) evaluation with paired tests (Section 4.1). 10,000 bootstrap replications and 20,000 permutations, clustered by group.
- Exposure: public benchmark datasets (AIME, BBH, MMLU-Pro, MedQA, and others) released before 2026; whether Jev's training saw them is unknown; probes ask about task properties, not the answers. Coded public-pre-2026.

## Models
- Jev: version string not reported (no jev-x.y identifier in the text); accessed through the TypeSafe API at "$0.042 per million input tokens, with no charge for output tokens" (Section 4.12); references to TypeSafe docs and blog accessed 2026-09-28. Run dates not stated.
- Laya: open-weight typed decision model (repository NandhaKishorM/laya, Apache-2.0, accessed 2026-09-23), run locally, same probe schema; version not stated (Section 4.6, references).
- Comparators for the representation: GTE-Qwen2 dense embeddings + CatBoost, TF-IDF, DomainOnly, Hard (16 argmax judgments), Full (88 features), and published LLMRouterBench routers (RouterDC, GraphRouter, EmbedLLM, MODEL-SAT, Avengers) taken from the benchmark paper under a different protocol (Table 4; "we do not use the published values for paired statistical claims", Section 4.2). Tuning parity: all representations use the same CatBoost regression procedure and the same splits (Section 4.1); CatBoost hyperparameters not described as tuned per representation. JEV-Direct uses a single typed decision with anonymised candidate profiles built from training-fold outcomes (Section 4.5).
- Probe set and ProbabilityMass choice were developed on this benchmark; the Lite-12 probe selection is nested (Section 4.7) but the original sixteen probes were not selected nested. Selection of ProbabilityMass as the default after seeing results is not ruled out by the text.

## Statistics
- Mean +/- standard deviation over five grouped 70/30 splits; clustered 95 percent bootstrap CI and two-sided paired permutation tests on OOF predictions (Section 4.1). A noninferiority test with margin 0.5 for Lite-12 fails (lower bound -0.783) (Section 4.7).
- Calibration: no calibration analysis; the paper plans to study calibration of the semantic state later (Section 5). Selective routing: semantic entropy AURC 0.0901 versus router margin 0.0974 on OOF; Domain-OOD fixed entropy threshold gives 65.38 at 96.82 percent coverage versus 65.32 unfiltered (Section 4.10).

## Cost and latency
- Jev extraction: 1,606.7 mean input tokens per query (p95 1,919), mean latency about 350 ms and p95 481 ms including network (remote API); estimated extraction cost 0.0675 USD per 1,000 queries, 0.775 USD total over 11,481 queries (Section 4.12, 4.13, Table 7). Laya local: mean 103 ms, p95 206 ms; "should not be interpreted as a direct comparison of model execution speed" (Section 4.13). Lite-12: 1,062.7 tokens, 33.9 percent lower input cost, p95 394 ms (Sections 4.7, 4.12, 4.13). Downstream CatBoost 1.23 ms per query at batch size one.
- Performance-cost routing: mean PerfGain +2.66 +/- 1.85 percent over GPT-5 across five splits, but "no positive monetary savings" under the strict validation-selected protocol (Abstract, Section 4.11).

## Cascade, option-name, cardinality, robustness
- No escalation cascade (routing). Robustness: probe reduction (Lite-12), leave-one-probe-out (Table 5), Dataset-OOD (67.02 ProbabilityMass versus 67.29 GTE-Qwen2) and Domain-OOD (65.66 versus 67.31) distribution shifts (Section 4.9). No option-name or order test on the probes. Score probes have four levels, Noul binary.

## Authors' stated limitations
- Published router numbers use a different protocol and are external comparisons only; ProbabilityMass vs Hard difference not significant (p = 0.1099); Domain-OOD advantage goes to dense embeddings; Lite-12 noninferiority not established; monetary savings not established under the strict protocol; JEV latency measured via remote API and not comparable with local Laya (Sections 4.2, 4.3, 4.9, 4.11, 4.13).
