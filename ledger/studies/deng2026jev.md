# deng2026jev — Jev for Scientific Decisions: Evaluating Semantic Choices and Their Consequences

- arXiv: 2609.24965v1 [cs.CL], submitted 21 Sep 2026. License CC BY-NC-ND 4.0.
- Authors: Boyuan Deng (Johns Hopkins University, corresponding), Shuyi Fan (Columbia University), Hongyang Zhang (The Hong Kong Polytechnic University), Xinhong Xie (The Pennsylvania State University). Affiliation type: academic.
- Source: fulltext/2609.24965.html / .txt (fetched via `https://arxiv.org/html/2609.24965v1`, 2026-09-24).

## Task and data
Twenty source-grounded scientific "Choices" (typed multiple-choice decisions) across ten cases (two Choices per case), drawn from manufacturing/materials, physical simulation, climate, metrology and biological-experiment literature (§2.1, Table 3). Each model receives prepared evidence passages, structured records, question instructions and candidate meanings; a shared deterministic program (Eq. 1) converts selected relations into scientific outputs and a final consistency label. These 20 model-routed Choices are part of a larger development collection of 40 Choices in 20 case groups (the other 20 resolved by deterministic code rules, Table 2), plus one engineering control (§2.1).

## Decision models evaluated (version strings as reported, Table 1)
Jev 1.13; GPT-5.6 Luna; GPT-5.6 Terra; GPT-5.6 Sol; GPT-6 Astra; Claude Sonnet 5; Claude Opus 5; Qwen3.8 Flash; Qwen3.8 Max 0902; DeepSeek V4.1 Flash; DeepSeek V4 Pro 0813; Kimi K3. Twelve configurations total, evaluated in three groups with serial requests, shuffled case order and rotating model order within each group (§2.3). Each configuration: 50 planned requests (10 cases × 5 repetitions), 100 semantic answers (2 Choices/case).

## Comparators and tuning-budget parity
Jev uses its native Choice interface; all other models return candidate identifiers via a constrained JSON schema (§2.1). "Each request was evaluated once, without retries or provider substitution" (§2.3) — same prompting/evidence contract across models, i.e. same-prompt parity, not individually tuned per model. All other models run at "provider's default reasoning setting" is stated for the separate evals.typesafe.ai grey-literature source, not this paper; this paper does not state reasoning-effort settings beyond "Model versions and inference settings are specified in the accompanying code and results" (§2.3) — comparator_tuning_budget recorded as "not reported" beyond same-prompt.

## Reference labels
Reference relations (r*), outputs (z*) and final labels (y*) constructed by the authors from source documents; "References for fourteen groups received human review; the other six groups relied on assistant review" (Appendix A.2) — i.e., mixed human-adjudicated / LLM-assisted review, authors' own construction. Reference labels withheld from model input. reference_label_type recorded as human_adjudicated (majority human-reviewed) with the mixed caveat noted in excerpts.

## n and sampling
n = 20 Choices × 5 repetitions = 100 semantic answers per configuration (planned); 50 case-level downstream/joint/label decisions per configuration. 12 configurations. Primary scores use planned denominators (no credit for missing responses); Appendix C gives conditional-on-response scores.

## Test-set exposure
Sources include historic published literature (e.g., Luria & Delbrück 1943) reinterpreted into new Choices; the case-construction and packaging is original to this paper (2026), so classed as new/unclear — the underlying source documents are older public literature, but the Choice framing and evidence packets are newly authored for this study (§2.1, Appendix A.2). Not explicitly discussed as a training-data risk in Limitations.

## Cost and latency
"Latency measures elapsed client request time; we report its median and nearest-rank 95th percentile among successful responses. Cost is the known mean charge per successful response, using provider-reported charges (r) or estimates from token usage and applicable prices (e)" (§2.3). Table 1 gives per-model median/p95 latency (s) and cost ($/1,000 requests). No hardware specified (API calls); "r" = reported charges, "e" = usage-based estimates.

## Calibration
No calibration/ECE analysis in this paper — it evaluates discrete Choice correctness, not probability calibration.

## Cascade/escalation
None reported.

## Robustness / stress tests
The culture-history case (B002, based on Luria & Delbrück 1943) is a robustness-relevant finding: three comparator models (GPT-5.6 Luna, Qwen3.8 Flash, Qwen3.8 Max) together produced seven wrong semantic selections, all on the same Choice (growth-history count), while the second Choice in that case (clonal descent) was always answered correctly, so the final consistency label remained correct despite the wrong quantity (§3.2). This is the paper's "correct labels can conceal wrong quantities" finding — a label-only evaluation would miss it. Jev made zero such errors.

## Code and data availability
"Model versions and inference settings are specified in the accompanying code and results" (§2.3) — implies a code/results release, but no explicit repository URL located in the fetched full text. code_available recorded as "not reported" (no URL found in main text or references).

## Limitations (paper's own, from "Limitations" section)
- Development collection of 20 model-routed Choices in 10 cases; same curated English packets recur across the 5 repetitions; six configurations achieve complete correctness, and all observed semantic errors concern one Choice — "evaluating transfer requires new, source-separated cases and broader relation coverage."
- Every model-routed reference label is inconsistent (none is not_stated/other/conflicting) — "the collection therefore measures relation selection and its consequences within these cases. Balanced claim decisions and uncertain-evidence cases are needed to assess label discrimination and abstention."
- Reference construction "involved assisted source review and author decisions, with further source review covering fourteen of twenty model-routed Choices."
- "The harness comparison uses one implemented configuration per model; its component effects would require a separate ablation study."
- "Latency and cost depend on services, execution windows, reasoning settings and cache states... Charges for missing responses and the costs of source preparation, candidate construction, human review and local computation are unmeasured, leaving total workflow expenditure undetermined."

## Seed claims checked (see parts/seed_check_C.csv)
1. "20 source-grounded scientific Choices, 12 configurations" — confirmed (Table 1: 12 rows; §2.1: "twenty scientific Choices in ten cases").
2. "matches five configurations at full semantic correctness" — confirmed verbatim in Abstract: "Jev matched five other configurations at complete semantic correctness" (GPT-5.6 Sol, GPT-6 Astra, Claude Sonnet 5, Claude Opus 5, Kimi K3 all at Semantic=100/100, Table 1).
3. "lowest latency" — confirmed: Jev median 0.335s / p95 0.442s, both lowest in Table 1 among all 12 configurations.
