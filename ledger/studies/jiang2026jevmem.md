# jiang2026jevmem — Jev-Mem: System-One-Controlled Agentic Memory for Efficient AI Agents

arXiv:2609.23986v1 [cs.AI], submitted 21 Sep 2026, CC BY 4.0. HTML retrieved from https://arxiv.org/html/2609.23986v1.

## Authors and affiliation

Dongming Jiang, Yi Li, Bingzhe Li (corresponding). "Department of Computer Science, The University of Texas at Dallas." Affiliation type: **academic**.

## Task and data

Long-horizon agentic memory: **Jev-Mem** is a System-One/System-Two memory architecture in which a typed System-One controller 𝒥(S,𝒬) handles high-frequency, bounded memory-control decisions (memory typing, redundancy filtering, semantic/temporal/causal/entity relation construction on write; query routing, retrieval-budget allocation, graph traversal, candidate scoring, evidence-sufficiency checking, adaptive stopping on read), while a System-Two LLM is reserved for final answer synthesis (§3). Evaluated on **LoCoMo** [Maharana et al. 2024, arXiv:2402.17753], an ultra-long multi-session conversational-memory benchmark scored with an LLM-as-a-Judge metric (Zheng et al. 2023) based on `gpt-4o-mini` (Table 1 caption). Question categories: Multi-Hop, Temporal, Open-Domain, Single-Hop, Adversarial, Overall.

## Decision models evaluated

**Jev-Mem's System-One controller** — Appendix B confirms this genuinely calls TypeSafe's commercial Jev model via `TypeSafeClient.system_one`, submitting a shared state object plus a batch of typed questions ("Noul" for independent binary propositions, "Choice" for mutually exclusive alternatives); returned Noul values lie in [0,1] and are explicitly *not* assumed to be calibrated probabilities ("These model-reported values are not assumed to be calibrated probabilities," Appendix B.1). No specific Jev version string (e.g. `jev-1.13`) is given anywhere in the main text or appendix — `version_pin = not reported`. Comparators (baselines, §4.1, using "the same backbone answer model whenever applicable"): Full Context (no external memory), A-MEM, Nemori, MemoryOS, MAGMA (the strongest baseline overall). None of the baselines uses a typed System-One controller.

## Reference labels

LLM-as-a-Judge scoring (gpt-4o-mini) against LoCoMo's reference answers — coded `llm_teacher`.

## n, sampling design

Full LoCoMo benchmark; exact item count not stated in the body text beyond the standard LoCoMo scale (not independently re-stated by the paper). No confidence intervals, seeds, or repeats reported for either Table 1 (accuracy) or Table 2 (efficiency) — single-run point estimates only.

## Test-set exposure

LoCoMo is a public benchmark released in 2024 (Maharana et al.), predating both Jev (August 2026) and this paper — coded `public-pre-2026`.

## Cost and latency

Hardware/provider not reported for either the System-One controller calls or the System-Two LLM calls (no GPU/API details given in the main text). Headline efficiency (Table 2, §4.3): memory construction time 158 s for Jev-Mem vs 1,044 s for Nemori (the fastest competing memory system) — 84.9% reduction / 6.6× speedup; vs 3,636 s (A-MEM) and 3,276 s (MemoryOS). Average query latency 0.93 s for Jev-Mem vs 1.47 s (MAGMA, fastest memory-based baseline, 36.7% reduction) and 1.74 s (Full Context, 46.6% reduction); MemoryOS is far slower at 32.68 s/query.

## Calibration analysis

None. The System-One controller's returned values are explicitly stated not to be assumed calibrated (Appendix B.1), and no ECE/Brier/reliability analysis is reported anywhere in the paper.

## Cascade / escalation results

The System-One/System-Two split is itself a form of escalation-by-design (cheap structured decisions handled by System One; System Two "invoked only for complex reasoning and answer synthesis," §1) but no threshold-based escalation *rate* or confidence-based routing statistic is reported — no quantitative cascade result to extract.

## Option-name / robustness stress tests

None reported.

## Internal consistency note (table vs. body text)

Table 1's per-category values for Jev-Mem are **0.623 (Multi-Hop), 0.637 (Temporal), 0.618 (Open-Domain), 0.802 (Single-Hop), 0.962 (Adversarial), 0.777 (Overall)**. The body text (§4.2) restates several of these with different digits: "Jev-Mem reaches 0.625" for Multi-Hop (table: 0.623), "it achieves 0.610" for Open-Domain (table: 0.618), "the highest Single-Hop score of 0.797" (table: 0.802), and "matches the best result on temporal reasoning" for Temporal (table: Jev-Mem 0.637 vs MAGMA's 0.650 — not actually a match, per the table). These four small table/text discrepancies are flagged for the curators; the ledger rows (`parts/ledger_B.csv`, value_keys `jevMemMultiHopScore`/`jevMemOpenDomainScore`/`jevMemSingleHopScore`/`jevMemTemporalScore`) use the **table** values as `value` since Table 1 is the primary machine-checkable source, with the body-text figure noted in each row's `excerpt`/comparator context. This does not affect the headline Overall (0.777) or Adversarial (0.962) numbers, which the table and body text agree on exactly.

## Code and data availability

"The code of Jev-Mem is publicly available" at https://github.com/libingzheren/Jev-Mem (Abstract footnote). `code_available = yes`.

## Paper's own stated limitations

No dedicated limitations section or paragraph appears in the main text (checked via full-text read through Conclusion). The paper does not discuss LoCoMo's potential presence in the backbone LLM's or Jev's training data, does not report variance/seeds, and does not report hardware or the System-One Jev version pinned — these are gaps the curators should weigh when rating reporting completeness, though per protocol this study note does not itself assign a risk-of-bias rating.

## Notes on seed claims (see also parts/seed_check_B.csv)

- LoCoMo: **confirmed** (§4.1 "Datasets").
- "+11% over the strongest memory baseline": **confirmed** — paper states "an 11.0% relative improvement" (0.777 vs 0.700 for MAGMA; 0.777/0.700 − 1 = 11.0% exactly), matching the seed to within rounding of "%"" vs "11.0%".
- "6.6× faster construction": **confirmed** exactly (158 s vs 1,044 s = 6.60×).
- Co-author draft's 0.777 LLM-judge score: **confirmed** (Table 1, Abstract, Conclusion — all three agree).
- Co-author draft's 158 seconds for memory construction: **confirmed** (Table 2, Abstract, §4.3).
- Co-author draft's 0.93 (query latency): **confirmed** — this is average query latency in seconds (Table 2, §4.3), not a unitless score as the draft phrasing might suggest; flagged for the curators to state units when citing it.
