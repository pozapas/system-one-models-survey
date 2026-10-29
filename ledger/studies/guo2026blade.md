# guo2026blade — BLADE: Auditing Information Use for Failure Attribution in LLM Multi-Agent Systems

- arXiv: 2610.18780v1, 13 Oct 2026. Full text: fulltext/2610.18780.html and .txt (fetched 2026-10-28).
- Authors: Xiaoguang Guo, Yaohao Long, Chuxu Zhang (University of Connecticut; Long lists a personal email). Affiliation type: academic.
- Code: no repository link found in the text.

## Task and data
Application paper: BLADE (Blame Localization via Audited Dependency Evidence) is a training-free pipeline for failure attribution in multi-agent trajectories that uses Jev for every probabilistic judgment: (1) dependency reconstruction (four relations, probability threshold 0.3), (2) graph-guided contract auditing of at most K=2 source-decision handoffs per event with nine labels, (3) defeasible global diagnosis over all events (Section 3). Data: 1,228 failed trajectories from five subsets of Who&When (Hand-Crafted, Algorithm-Generated; natural failures) and Who&When Pro (Magentic-One, DyLAN, MetaGPT; injected failures) (Section 4.1). Metrics: agent accuracy and step accuracy against annotated responsible agent and decisive step; invalid predictions count wrong.

## Decision model and version
Jev, "TypeSafe, jev-1.13.0" (Section 3.2). A single decision model is used for all strategies; no access date or run dates stated. Trajectories exceeding Jev's 32k-token limit (22 of 995 Who&When and Magentic-One runs) are shortened for all methods (App. A.2). Leaking fields in Who&When Pro (injected-step metadata) removed before any method reads a run (App. A.1).

## Comparators and tuning-budget parity
Seven baselines (All-at-once, Step-by-step, Binary search, TRIAGE, FALAT, ErrorProbe, TrajDebug) "instantiated under a shared Jev decision interface using identical tasks and recorded trajectories", without auxiliary free-form generation (4.1, App. B.2). These are the authors' adaptations of published methods, which originally used free-text LLMs; BLADE has a bespoke multi-stage design with hyperparameters theta=0.3, K=2 (how they were chosen is not stated in the main text), so the comparison is parity of interface rather than of design effort.

## Reference labels
Benchmark annotations of the responsible agent and decisive step: human annotation for Who&When (Zhang et al., 2025); known injection locations for Who&When Pro (Liu et al., 2026). Ledger label types: human_adjudicated for the HC and AG rows and macro rows (benchmark annotations), synthetic for the Pro rows. DyLAN step prediction is correct if it names a turn of the annotated agent in the annotated round.

## n, sampling, intervals
Per-subset results are point estimates; paired task-cluster bootstrap (20,000 replicates, seed 0) for macro step-accuracy gains: +5.6 [2.8, 8.6] over All-at-once and all seven intervals above zero (App. C.2, Table 3).

## Test-set exposure
Who&When (ICML 2025) is public pre-2026 (ledger public-pre-2026 for the HC and AG rows); Who&When Pro is Liu et al. 2026, so Pro rows and macro rows are coded unclear. No contamination check; Jev training data unknown.

## Cost and latency
"Estimated Jev inference cost of approximately $1.9 across all 1,228 trajectories at the published input-token rate" (Section 4.4); latency not reported; auditing 13 to 23% as many handoffs as exhaustive auditing (Section 1).

## Calibration, cascade
Jev probabilities are used for thresholding dependencies (0.3) and arg-max selection, not evaluated for calibration; no ECE. No cascade.

## Robustness tests
Evidence shuffling and removal ablations (Table 2), recency-based vs dependency-guided source selection, trajectory length effects, tolerance k localization (Figure 3). No option-name, language or cardinality test.

## Main results
Macro step accuracy 57.6% vs 52.0% for All-at-once (Jev), macro agent accuracy 66.8% vs 64.0% for TrajDebug; best or tied-best step accuracy on all five subsets (three outright, two ties) (Table 1).

## Limitations (paper's own)
Five subsets only; relies on recorded traces and truncation may omit evidence; a single decision model (Jev) used, so generalisation across backbones untested (Limitations).
