# severo2026jevids: Jev-IDS, a System One Model for network intrusion detection in label-scarce and zero-day scenarios

## Identification

- arXiv 2610.01079v1, cs.CR, 01 Oct 2026 (header). Full text: fulltext/2610.01079.html and .txt.
- Authors: Paulo Severo, Silvio E. Quincozes, Amanda Dias. Affiliation: Graduate Program in Software Engineering, Federal University of Pampa (UNIPAMPA), Alegrete, Brazil. Affiliation type: academic. Funding FAPERGS grant 26/2551-9000194-3; no competing interests declared.

## Internal inconsistency to flag for the grader

The abstract, highlights and Section 8 describe a "300-flow NSL-KDD pilot split" with "5,400 decisions" and a comparison to "GPT-5.6 Luna" (F1 0.859, precision 0.941, recall 0.790, novel recall 0.838; 4.8 times faster, 3.8 times cheaper at k=1; 15 times fewer false alarms than a low-data Random Forest; k=2 F1 0.839). The body (Sections 5 and 6, Tables 1 to 4) instead reports a 2,000-flow evaluation set, 6,000 decisions per finite-k condition (2,000 flows x 3 seeds), Gemini 3.6 Flash as the generative baseline, F1 0.856 at k=1 and 0.846 at k=2, 7.7 times lower latency and 22 times lower cost at k=1. The abstract values 0.859 / 0.941 / 0.790 / 0.838 / 4.8 / 3.8 do not appear in any body table. The Section 8 conclusion says Jev "obtained the best overall results", whereas Section 6.1 says Gemini had higher F1 at every k. The contributions list says "two intrusion datasets" but only NSL-KDD is described (Section 5.3). The ledger therefore records body-table values as primary rows and the three abstract-only values as separate rows labelled "Abstract only".

## Task and data

- Flow-based binary intrusion detection plus five-way traffic category (normal, DoS, probe, R2L, U2R) on NSL-KDD. Training pool KDDTrain+; evaluation flows sampled from KDDTest+ (Section 5.3). Evaluation set 2,000 flows: 874 normal, 642 DoS, 213 probe, 248 R2L, 23 U2R (Table 1). Novel attack = specific attack type present in KDDTest+ and absent from KDDTrain+: 300 of 1,126 attack flows are novel, 826 known.
- Reference labels: the dataset's own attack-type fields (coded administrative_field). Test-set exposure: public benchmark from 2009; contamination not discussed.
- Examples: k labelled flows per category (k in {0,1,2,4,8}); three independent seeds; nested sampling; same examples for all detectors in a condition (Section 5.1).

## Decision model and comparators

- Jev with jev-1.13.0 explicitly specified in the request template (Section 4.2). Two typed questions per flow: a noul (binary) question is_attack giving p_attack, and a choice question over the five categories with confidence. Binary verdict computed locally with p_attack >= 0.5 (Section 4.4). One flow per request; retries up to five attempts, errors treated as benign (fail-open) in metrics (Sections 4.5, 5.1). Reference to TypeSafe launch post accessed 2026-09-21.
- Gemini 3.6 Flash, structured output with attack probability, binary class and category; deterministic settings; lowest reasoning setting (about 200 reasoning tokens per flow) (Sections 5.2, 6.4).
- Random Forest, 100 trees, trained on exactly the same labelled flows (k in {1,2,4,8}) and also on the full training pool. Isolation Forest, 100 trees, trained on benign flows only (Section 5.2).

## Tuning-budget parity

Same flow representation, category descriptions and labelled examples for Jev and Gemini; common 0.5 decision threshold for all probability-producing detectors (Sections 5.1, 5.2). The authors note the common threshold is not an optimised deployment configuration for every detector (Section 7). The Random Forest is not tuned beyond 100 trees. Gemini prompt details are in the released repository, not in the text read.

## n, sampling design, intervals

- n = 2,000 flows per condition, 6,000 decisions per finite k (Section 6.1). F1 reported as mean and sample SD across 3 seeds (Table 2); no confidence intervals. Exact two-sided McNemar tests on discordant decisions pooled across seeds, which treats repeated evaluation of the same flows as independent; the authors acknowledge this (Sections 5.5, 7).

## Key results

- Table 2: Jev F1 0.782 (k=0), 0.856 (k=1), 0.846 (k=2), 0.856 (k=4), 0.854 (k=8); Gemini 0.867, 0.880, 0.869, 0.884, 0.881; Random Forest 0.748, 0.777, 0.853, 0.865 (k=1,2,4,8) and 0.765 with the full pool; Isolation Forest 0.761. Gemini higher F1 at every k (Section 6.1). Jev precision 0.953 vs Gemini 0.942 at k=1. Novel recall Jev 0.747 vs Gemini 0.713 at k=1 (Gemini higher at k=0: 0.687 vs 0.622).
- Table 3 (exact McNemar): all flows Gemini favoured at every k, p < 0.001; novel attacks at k=1 Jev correct on 74 of 118 discordant decisions (p = 0.007), k=2 105 vs 57 (p < 0.001), k=4 p = 0.353, k=8 p = 0.221. Largest novel gain on R2L (Jev 0.151 to 0.262 vs Gemini 0.000 to 0.071). Random Forest k=1 vs Jev: disagree on 2,909 of 6,000, Jev correct on 2,161 (p < 0.001); RF k=1 false alarms about 764 vs about 43 for Jev.
- Table 4: cost per million decisions Jev US$43 / 74 / 106 / 169 / 295 vs Gemini US$1,068 / 1,651 / 2,409 / 2,869 / 3,035 (ratios 25, 22, 23, 17, 10); latency Jev 310 / 315 / 308 / 322 / 335 ms vs Gemini 2.24 / 2.42 / 2.65 / 2.13 / 1.99 s (ratios 7.2 to 8.6, 5.9 at k=8). Jev about 1.8k input tokens at k=1 with no output-token charge; Gemini 6,269 mean input tokens at k=8 with 4,004 cached. Costs are list-price estimates from recorded token usage; latency is end-to-end wall clock including network and provider overhead.
- Calibration: not evaluated ("probability calibration was not evaluated"); ROC-AUC 0.950 and PR-AUC 0.952 for Jev at k=1; no ECE, Brier or recalibration.
- Cascade: proposed as future work, not evaluated (Section 7).

## Option-name, cardinality, language, robustness tests

None. Attack names are withheld and mapped to five coarse categories (Section 4.1).

## Code and data availability

MIT-licensed code, frozen split identifiers, prompts and raw pilot prediction rows at https://github.com/jev-ids/jev-ids; documentation https://jev-ids.github.io/; analysed revision commit 286a310 (Data and code availability). NSL-KDD obtained from original sources.

## Authors' own limitations (Section 7)

NSL-KDD is dated and not representative of current traffic; "novel" means an absent attack type, not a truly new behaviour; common threshold not optimised; no calibration analysis; seed dependence not modelled in the statistics; only three seeds; hosted services far slower than local ML, so unsuited to line-rate use; only one dataset.
