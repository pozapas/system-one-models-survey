# li2026reading — Reading Right, Acting Wrong: Diagnosing Decision Failures of System One Models in Agent Loops

- arXiv: 2610.18579v1 [cs.AI], 13 Oct 2026 (CC BY 4.0). Full text: fulltext/2610.18579.html and .txt (fetched 2026-10-28).
- Authors: Yubo Li, Ramayya Krishnan, Rema Padman (Carnegie Mellon University). Affiliation type: academic. Project website https://yubol-bobo.github.io/System_one_model_evaluation (title footnote); no explicit code or data release statement found.

## Task and data
Behavioural diagnosis of next-action choice by System One models: each agent decision state gets a next-action question (choose from all admissible actions) and independent factual probes about the same state; crossing "all facts correct" (U) with "action correct" (D) gives four outcomes (Section 2). Frozen benchmark of 65,228 records (59,234 test, 5,994 dev), 19,663 paired test states, from ALFWorld, BabyAI-Text, TextWorld (exact simulator ground truth), tau2-bench airline and retail, tool use, web, 360 coding records (Section 3, Appendix C). Follow-up studies: generated states with probes sufficient by construction (1,200 test states, Section 6.1), probe-then-decide on 2,783 paired states (Table 3), decision-oriented probes on 644 ALFWorld states, controls and calibration (Section 7).

## Decision models and versions
Table 1: 14 System One models (hosted JEV 1.13 and OpenAI Decisions; open Clef-27B, Kev-9B, CLM-8B, Laya, Eikos-27B, Perplexity Decider-27B, SimpleJev-27B, Vega-27B, Torchcast-27B, Quyet-1.0-Large; recipes Cygnet and Decider-chat-31B), three likelihood readouts (Gemma-4-31B, Qwen3.8-27B, Qwen3.5-9B) and GPT-6.1 Sol as reasoning reference. "JEV is pinned by its version string (jev-1.13.0), but its provider does not promise long-term support" (Appendix D). Formal runs ended 1 October 2026; a 2,783-state rerun on 6 October matched on 96.3%; on 5 October 16 of 24 minimal requests returned server errors. OpenAI Decisions identified only as gpt-6-luna, collected 11 October 2026. Open models "pinned to released revisions" (revision strings not given in main text). Local systems on one H100.

## Comparators and tuning-budget parity
Identical frozen requests for all systems, no truncation, over-limit questions counted wrong and reported as coverage (Section 4). "Readouts differ by design, so comparisons are between deployed choice interfaces and do not isolate architecture, size or training data." Systems use authors' own serving code and settings; two author runtimes shorten long states themselves (Table 1 note). GPT-6.1 is a deliberating reference, not a competitor.

## Reference labels
Gold sets computed from simulator state (first actions of all shortest plans, checked against breadth-first search); tau2 gold from successful trajectories; probes from simulator, database or data labels (Sections 2.1, 3). Generated states have unique gold by enumeration (6.1). Label audits: 98 flagged records (42 conflicting, 56 duplicated in dev) change no group score by more than 3.5 points; 303 ALFWorld location labels name co-located receptacles (Section 5.4, Appendix E).

## n, sampling, intervals
Pooled counts over 19,663 paired states, "which summarize prevalence and are not a ranking statistic" (Section 2.3); intervals appear in Table 3 and Figures 8c, 9 (95%). Main accuracy table (Table 2) has no intervals. Latency panel 163 items (first of three passes), first pass reported.

## Test-set exposure
ALFWorld, BabyAI-Text, TextWorld are public pre-2026 environments and tau2-bench is Barres et al. 2026, but the paired states are newly rolled out from the simulators and frozen in a hash-sealed manifest, not taken as verbatim public items, so ledger test_set_exposure is new; hash-sealed frozen manifest; confirmation cohorts generated later from new seeds, plus freshly generated procedure states (Section 3). No contamination analysis for model training.

## Cost and latency
JEV billed 209.2M input tokens, $8.79 for all 65,228 records ($0.13 per 1,000 decision states); OpenAI Decisions $18.69 ($0.29); GPT-6.1 $642.00 under batch pricing ($9.84 per 1,000; about 73 times JEV); self-hosted at $2.50 per H100-hour assumed (Section 4, Appendix D). Median latency 205.7 ms (p95 290.5) for JEV vs 27.4 to 225 ms for other System One models, 317 to 947 ms for likelihood readouts, 2,276 ms for GPT-6.1 (Table 1).

## Calibration
Figure 11 (reliability diagrams, ECE with 15 bins; spacing not stated; no post-hoc recalibration applied): JEV 6.8%, Cygnet 2.6% (recipe includes calibration), Gemma likelihood readout 19.1% (mean confidence 0.98 at accuracy 0.79), Vega-27B 26.6%, OpenAI Decisions own confidence field 13.9% (Section 7).

## Cascade
Confidence cascade on generated states: re-ask only below confidence 0.7 reaches 0.932 for JEV with a second request on 38% of states (Section 6.1). Own-answer composition: JEV 0.791 to 0.968; code composition 0.996.

## Robustness
Trace ablation, observation minimal pairs, stated rule changes (strong systems follow stated rules in 90 to 99%, JEV 93.3%), difficulty ladders (Section 7, Figure 10). No option-name, cardinality or language robustness test beyond option count in latency panel.

## Limitations (paper's own, Section 10)
Behavioural evidence only; probes not sufficient on natural states; labels can be stricter than necessary (5 to 42% of simulator errors are also optimal); deployment differences (hosted version drift, public beta); single decisions on frozen traces, not closed-loop execution; follow-up studies cover subsets of systems; GPT-6.1 calibration not comparable.
