# li2026sok — SoK: Semantic Decision Engines in Network Control Loops

arXiv:2610.06425v1 [cs.NI], 05 Oct 2026 (version line in fulltext/2610.06425.html and .txt). Full text: fulltext/2610.06425.html and .txt. A systematization of 139 paper families plus bounded tests with the authors' own measurements (Sec VI-VII, Appendices A-B).

## Authors and affiliation
Delong Li, Chen Li, Xu Wang, Haochen Gong, Rui Lang, Guangsheng Yu; School of Electrical, Mechanical and Biomedical Engineering, University of Technology Sydney, Australia (title block). Affiliation type: academic.

## What the ledger records and what it leaves out
The paper marks every result as SoK-owned, borrowed and reanalysed, or borrowed context (Sec VI-D, Table VII "Ownership" column). The ledger rows hold only SoK-owned measurements: the access-policy, coupled-placement, contract-catalogue and held-out route tasks (Sec VII, Tables VII-XII, XVIII-XXII; Table XVIII caption "Placement rows are SoK-owned", Table XXI caption "Policy rows are SoK-owned"). Left out on purpose:
- The service-contract and RAN-policy blocks of Tables VII, XVIII, XXI and XXII, Tables XIII and XV-XVII, and the VII-B sentence on 16 service arrivals/s; all are borrowed and reanalysed from the authors' earlier studies [2] (arXiv 2609.22753) and [3] (arXiv 2609.23136), which the ledger already holds as li2026replacing and li2026fast (Sec VII, refs [2, 3]).
- The transport and edge fixed-action intervention and the load arm (Sec VI-F, VII-A, VII-B, Table XIV). They are SoK-owned but inject controlled delays of 0, 0.1, 0.5 and 2 s into fixed actions with no decision model in the loop, so the abstract's "10 s budget ... for none at 4.992 arrivals/s" result gets no row (Sec VI-F, VII-B).
- The audit counts over the 139 families (50 loop claims, 4 with matched support; Sec I, V), which are literature coding, not model measurements.

## Task and data (SoK-owned arms)
Constructed application-layer tasks with complete predicates (Sec IX): access policy with 4, 16 or 64 interacting requirements over 120 cases (60 changed, 60 preserved), with long irrelevant context and repeated-requirement variants at 24k characters (Table VIII); coupled placement over 3, 5 and 8 nodes (40 cases each, four demand families) with complete, prose, missing, stale, conflicting-current and resolved-conflict observation states (Table IX) and self-check versus public-gate workflows under independent quota, shared quota and shared quota plus fault-domain separation (Table XII, XX); contract catalogue with 48 configurations per condition (stable, rekeyed, two new candidates, absent) (Table X, XIX); held-out route catalogues with 20 new graphs per contract, 120 per condition, eight candidates, with a feasible candidate present or absent (Table XI). Correctness is minimum-cost feasible selection or justified refresh, rebuilding or escalation (Tables IX, XI captions).

## Decision models evaluated
Application-control tasks use "Jev-1.13" (Sec VII, model-version paragraph). Jev-1.13.0 is named only for the borrowed service-contract and RAN tasks (same paragraph). Minor version only for the SoK-owned arms; no run dates are given, only "the second collection batch" (Table VII caption). Provider and hardware for Jev are not stated in the text.

## Comparators and tuning parity
Same-task comparators on the same cases: DeepSeek-V4.1-Flash, Gemini-3.1-Flash-Lite, GLM-4.7-Flash and a local Qwen3.5-4B, plus task rules (full rule, cheapest, first entry, per-stage rule, ungated rule, link-only, lexical rule) and MiniLM re-ranking on the contract task (Sec VII; Tables VIII-XII). Conditions "pair the same cases and candidates" (Table VIII caption); instructions given to each model and any tuning are not described, so tuning parity is coded not reported. The public-gate arm "jointly changes instructions, refresh actions and check ownership" (Fig 7 caption; Sec IX), so those rows are a workflow-redesign effect. No SoK-owned arm compares Jev with another typed decision model; Laya and AnyJev-L0 appear only in borrowed rows (Tables VII, XVIII, XXI).

## Reference labels
Task predicates on constructed instances computed by complete feasibility and cost rules; the full rule meets every measured condition (Sec VIII "Compute Joint Feasibility"; Sec IX). Coded synthetic.

## n and intervals
120 cases per condition (placement, policy, routes), 48 (contract), 81 for the Table VII latency block (Table VII caption). 95% Wilson intervals for proportions (Sec VI-E; Tables XVIII, XIX, XXI); paired stratified bootstrap with 10,000 draws, seed 42, and exact McNemar with Holm adjustment within each declared family (Sec VI-E; Tables XX, XXII). Each experiment uses one random stream, so intervals do not cover replication (Sec IX). Questions and comparison families were set after inspecting the records and are exploratory (Sec VI-D, IX).

## Test-data exposure
New constructed items (Sec IX); test_set_exposure coded new.

## Headline numbers (authors' own measurements)
- Placement, Jev-1.13: correct action 50/120 (41.7%, 33.2-50.6) with conflicting current reports, 11/120 (9.2%, 5.2-15.7) when an older conflict is resolved by newer evidence; DeepSeek-V4.1-Flash and GLM-4.7-Flash 100.0% and 1.7% / 0.8%, Gemini-3.1-Flash-Lite 25.8% on both (Sec VII-C; Table IX; Table XVIII). Complete state, shared quota: Jev 14/120 against Gemini 36/120 (Table IX).
- Coverage: Jev requests new contract candidates in 45/48 absent cases (93.8%, 83.2-97.9; GLM-4.7-Flash 33.3%, lexical rule 100.0%) but escalates only 4/120 infeasible route cases (GLM-4.7-Flash 109/120); with a feasible route listed Jev scores 95/120 against Gemini 97/120 (Sec VII-C; Tables X, XI, XIX).
- Workflow: Jev's independent-quota correctness rises from 29/120 (self-check) to 84/120 (public gate), paired gain 45.8 pp (37.5-54.2); shared quota 23.3 pp (15.8-30.8); shared quota plus fault-domain separation 32.5 pp (25.0-40.0) (Sec VII-C; Table XX).
- Structure: access policy 107/120, 97/120 and 47/120 for 4, 16 and 64 requirements (89.2%, 80.8%, 39.2%), change -50.0 pp (-59.2 to -40.8) against Gemini-3.1-Flash-Lite -5.8 pp (Sec VII-D; Tables VIII, XXI). Irrelevant context 0.8 pp (-1.7 to 3.3) and repetition 3.3 pp (-0.8 to 8.3), both pHolm 1 (Table XXII).

## Cost and latency
Table VII access-policy base block (81 cases, second collection batch): Jev-1.13 return p50 / p95 / p99 0.350 / 0.483 / 0.620 s, 100.0% within 1 s and 0.0% within 100 ms; Qwen3.5-4B 0.329 / 0.388 / 0.435 s; DeepSeek-V4.1-Flash 0.469 / 1.623 / 6.123 s; rules 0.000 s (Table VII). Table VIII gives Jev 0.382 s median and 0.646 s p95 on the 120 short-input cases; the two figures come from different case sets and are not in conflict (Table VII and VIII captions). Jev response medians across the placement and route tasks are 0.350-0.375 s (Tables IX, XI, XII). The Jev provider is not reported and Qwen3.5-4B is run locally (Sec VII), so the latency contrast mixes hosted and local deployment. No cost figures for the SoK-owned arms.

## Calibration
None; probabilities are not analysed.

## Cascade or escalation
Escalation is a scored outcome: new-candidate requests 45/48 and route catalogue rebuilding 4/120 for Jev (Sec VII-C). No cascade to a stronger model.

## Option-name, cardinality, robustness tests
Requirement count 4/16/64, irrelevant context and repetition (Tables VIII, XXI, XXII); candidate rekeying and replacement (Table XIX); observation-state perturbations (Table XVIII). Eight route candidates and four placement candidates (Tables IX, XI). No language test.

## Code and data availability
GitHub link OniReimu/SoK-JEV (https://github.com/OniReimu/SoK-JEV) in the title block; the text does not describe its contents.

## Authors' limitations (Sec IX)
The audit measures what the literature reports; measured consequences come from the source studies and the SoK-owned tasks, and the surveyed systems of other authors remain untested; one random stream per experiment; exploratory questions with Holm control within families only; constructed tasks whose graph costs do not represent measured network delay; the public-gate contrast estimates a workflow redesign, not the effect of moving one check; the load arm's post-queue actions do not run concurrently and transport and edge comparisons are descriptive.
