# wu2026reflex — REFLEX with Jev for Efficient Selective Control in LLM Agents

- arXiv: 2609.26532v1 [cs.AI], submitted 22 Sep 2026. License CC BY 4.0.
- Authors: Tiantong Wu (Nanyang Technological University, Singapore), Wei Yang Bryan Lim (Nanyang Technological University, Singapore). Affiliation type: academic.
- Source: fulltext/2609.26532.html / .txt (fetched via `https://arxiv.org/html/2609.26532v1`, 2026-09-24).

## Task and data
REFLEX is an agent-control architecture: Jev (as a fast typed decision + confidence layer) handles bounded agent decisions (tool selection, continue/stop, retrieval, clarification, completion), escalating to a strong LLM when confidence is low or free-form generation is needed (Eq. 1-2, §3.1). Evaluated on:
1. **REFLEX-Sim v1.2.0** — a frozen, audited, deterministic tool environment (100 held-out tasks, C0-C4 task-complexity bands), scored by terminal-state assertions/policy constraints, not exact trajectory match (§4, "REFLEX-Sim", "Audit and freeze protocol").
2. **RF-5C** — a preregistered 2x factorial intervention crossing action-set size K in {10,25,50} with 4 ambiguity levels (A0-A3), 60 scenario families x 2 realizations = 1,440 decisions (§4, "Decision-complexity interventions").
3. **Matched competitor-type intervention** — 240 decisions, read vs write near-valid competitor, holding gold action/distance/count/similarity fixed.
4. **BFCL** (external) — function-selection (1,800 decisions) and function-relevance (100 cases) accuracy, plus a K=2 to K=64 candidate-set-size sweep.
5. **τ²-bench v1.0.1** (external, multi-turn) — 300 held-out episodes, 60 paired tasks x 5 conditions across three domains, native terminal-state reward.

## Decision models evaluated / version pin
"The decision layer uses the version-pinned jev-1.13.0 API" (§4, "Models") — matches the memory note that `jev-latest` resolves to jev-1.13.0. Strong/generative fallbacks: Qwen3.8-Max (primary), with cross-family validation swapping in Kimi K3 or DeepSeek-V4-Pro (Jev, threshold, tools, evaluator held fixed); small/cheap generative model: Qwen3.8-Flash.

## Comparators (baselines) and tuning-budget parity
- B0: strong-only agent (Qwen3.8-Max or family fallback) — same prompt/default reasoning.
- B1: Flash-only agent.
- B3: "Flash cascade with self-escalation" — a cheap generative model that decides itself when to call the strong model; explicitly treated as "a central baseline without assuming that a specialized decision layer will outperform it" (§3.2).
- R1/Rτ: REFLEX with Jev, swept over τ in {0.5, 0.7, 0.8, 0.9, 0.95}; primary operating point τ=0.5.
"Kimi and DeepSeek use the same fixed high reasoning effort in the strong-only and REFLEX conditions" — same-prompt/fixed-reasoning-effort parity across arms (§4, "Models").

## Reference labels
REFLEX-Sim: terminal-state assertions and policy constraints authored/audited by the researchers (human_adjudicated), with "two evaluator audits before the final v1.2.0 freeze" (§4). BFCL: externally authored function-selection/relevance decisions (human_adjudicated, from the BFCL benchmark). τ²-bench: native terminal-state reward from the benchmark's own environment (task_outcome).

## n and sampling
REFLEX-Sim: 100 frozen tasks (all reported main runs "zero harness errors"). RF-5C: 1,440 decisions (60 families x 2 realizations x 12 K-by-ambiguity cells x 10 decisions/cell — cells of 120 decisions each per Table S2 reference). Matched intervention: 240 decisions. BFCL: 1,800 function-selection decisions + 100 relevance cases + 300 instances for the K=2-64 sweep. τ²-bench: 300 episodes (60 paired tasks x 5 conditions). Confidence intervals: paired cluster bootstrap over task/scenario family, "final analyses use 10000 resamples" (§4, "Inference and multiplicity"); McNemar test for paired binary success.

## Test-set exposure
REFLEX-Sim is a newly constructed, frozen (2026) benchmark — new. BFCL and τ²-bench are existing public benchmarks (2025-2026) — public-pre-2026 is approximately right for BFCL (Patil et al. 2025) though τ²-bench v1.0.1 (Barres et al. 2026) is itself very recent; recorded as "public-pre-2026" for BFCL and "new" (2026 benchmark, described as "external validation rather than a leaderboard submission") for τ²-bench in the rows below, per each dataset.

## Cost and latency
"For every API call, we log input and output tokens, model identifiers, decoding parameters, and latency. Costs use dated price snapshots for each provider and region and are recomputed from raw token records" (§4, "Pricing and latency accounting"). Table 3 (τ²-bench): $/episode and $/success per condition. REFLEX-Sim: "strong calls per successful task" used instead of raw dollar cost in the main table (Table 1); Table S14 (not fetched in this pass) has additional cost/efficiency measures.

## Calibration
Table (§5.1 prose): "Calibration is moderate, with a Brier score of 0.103 and ECE of 0.129" for Jev's confidence at τ=0.5 on REFLEX-Sim autonomous decisions. AURC = 0.019 vs 0.145 for random escalation at matched coverage (~7.6x lower). calibration_quantity = "Brier / ECE (binning method not specified in main text)"; post_hoc_calibration = none reported.

## Cascade / escalation results (central to this paper)
- REFLEX-Sim (Table 1): B0 (strong-only) 88% success, 4.10 strong calls/task. R1 τ=0.5: 95% success, 1.12 strong calls/task, GMR (call reduction) = 0.727 (72.7%). At τ=0.9/0.95, R1 matches B0's 88% success with 2.18/2.30 calls/task (GMR 46.8%/43.9%).
- Replacement rates by decision function (Table 2): tool selection 99%, completion 77%, retrieval 56%, clarification 28%.
- Cross-family (Table 4, "E6"): GMR 0.719 (Qwen), 0.714 (Kimi), 0.661 (DeepSeek); strong-model calls decrease 66.1%-71.9% overall; strong-token reductions 50.6%-64.1%.
- τ²-bench (Table 3, external): REFLEX τ=0.5 cuts cost by 3.7x vs B0 ($0.0572 vs $0.2111), success 0.850 vs 0.900 (paired diff -0.050, 95% CI [-0.150,+0.050], unresolved). B3 (cheap self-escalation cascade) is cheaper still ($0.0411) with numerically higher success (0.917), also statistically unresolved vs REFLEX. "A cheap generative cascade remains competitive when ordinary routing is already highly accurate" — the paper's own limiting/negative finding for this arm.
- BFCL (external, Figure 5a/Table S4): function-selection accuracy 98.4% over 1,800 decisions vs function-relevance ("should we call at all") accuracy only 52.0% over 100 cases (Fisher p=5.1e-47). Increasing K from 2 to 64 barely changes routing accuracy (99.0% -> 98.7%, paired diff -0.0033, 95% CI [-0.010, 0.000]). Incorrect BFCL calls have mean confidence 0.778, "indicating that a tau=0.7 gate would still allow incorrect calls."

## Robustness / stress tests
- RF-5C factorial: increasing K (action-set size) from 10 to 50 reduces accuracy by 6.7 percentage points (95% CI [-11.3,-2.5], p=0.0008, averaged over ambiguity); moving from ambiguity A0 to A3 reduces accuracy by 5.6 points (95% CI [-11.9,-0.3], p=0.038); interaction not significant.
- Matched competitor-type intervention: read vs write competitor -> accuracy 0.842 vs 0.833 (n.s., +0.008, 95% CI [-0.050,+0.067]); but irreversible-commit errors 1.7% (read) vs 10.0% (write) (Delta -0.083, 95% CI [-0.150,-0.025], p=0.0014); deferral errors 12.5% (read) vs 5.8% (write) (Delta +0.067, 95% CI [+0.025,+0.125], p=0.0016) — error type shifts without accuracy change.
- Embedding-similarity construction audit (Table S10, 5,931 candidate actions): median similarity to gold action 0.310 (one-change competitors), 0.333 (two-change), 0.237 (far distractors); 22.2% of far distractors exceed the median near-competitor similarity — embedding similarity is not a reliable proxy for procedural distance.

## Code and data availability
Not explicitly stated with a URL in the sections read; not confirmed in this pass (recorded as "not reported").

## Limitations (paper's own, from "Limitations" section)
- "We use one proprietary typed decision model, Jev, so the results do not establish that all non-generative decision models have the same selective-control behavior."
- E6 varies only the strong fallback, keeping the decision model fixed; "several controlled benchmarks also show ceiling effects for 2026 frontier models" (Kimi 100% on REFLEX-Sim; BFCL function selection near-perfect).
- RF-5C effects "concentrated in authority and risk families and should not be generalized to all agent decisions."
- The τ evaluation is "a held-out validation with 300 episodes, rather than a full leaderboard evaluation with multiple trials," used as "external evidence about cost and where failures occur, without claiming benchmark superiority."
- "Reported API costs are dated snapshots and may change with provider pricing, caching, or deployment region."

## Seed claims checked (see parts/seed_check_C.csv)
1. "100 frozen tasks, BFCL and τ-style" — confirmed: REFLEX-Sim v1.2.0 has "100 held-out tasks" (§4), evaluated alongside external BFCL and τ²-bench validations (§5.4).
2. "95% success with 72.7% fewer strong-model calls" — confirmed verbatim: "R1 at τ = 0.5 achieves 95% success with 1.12 calls per task, a 72.7% reduction" (§5.1; Table 1).
3. "limited advantage over a cheap generative cascade when routing is already accurate" — confirmed: on τ²-bench, "a cheap LLM cascade with self-escalation remains competitive" (Abstract), and BFCL/τ²-bench show "the room for improvement depends on the task" with "zero control-selection or argument-generation errors" observed (§5.4, Table 3, Table S11).
