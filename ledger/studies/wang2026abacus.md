# wang2026abacus — ABACUS: Program-Guided Multistep Reasoning over Frozen Judgment Models

arXiv:2610.25963v1 [cs.AI], 19 Oct 2026. Full text: fulltext/2610.25963.html and .txt (arXiv HTML). CC BY 4.0. Key uses first author Yuhao Wang (distinct from wang2026truncated, wang2026unijev, and yang2026what).

## Authors and affiliation
Yuhao Wang, Zelin Zang (Westlake University; Zang also Hong Kong Institute of Science & Innovation, CAS, and Tsientang Institute for Advanced Study) (title block). Affiliation type: academic.

## Task and data
Application, not a new decision model. A generative teacher (GLM-5.3-Flash) designs, offline, judgment schemas and a composition program for a frozen judgment model, Kev; online, Kev scores declared local outcomes and the saved program composes the answer (Sec 3). Three allocations of design effort: human-designed workflow (object placement, 208 questions in 52 stories), task-specific interface (MuSR team allocation and murder mystery, 200 stories each), and shared interface on BIG-Bench Hard tasks web of lies, navigation and temporal sequences (50 development inputs each; 200 held-out questions each, 600 total) (Sec 4). Original six-task BBH deployment covered 1,135 inputs; the three-task study is a post-hoc subset (App. H, Table 12).

## Decision models evaluated
Kev-4B (Qwen3.5-4B-Base backbone, probability temperature 2.40605) as the frozen online judgment model, direct and with the Abacus programs; no release hash or run dates in the text (Sec 4.3.2, App. D). Qwen3.5-4B post-trained, seven answer policies (final only, concise 16/32/64/128/256 words, free reasoning) in non-thinking mode, as the generative comparator.

## Comparators and tuning parity
Direct Kev (full problem), Kev with a teacher-written task prompt, and Qwen3.5-4B policies given the same four solved examples; Qwen sampling temperature 0.7, top-p 0.8, top-k 20; each system uses its own serving stack (CUDA graphs and shared-state caching for Kev, vLLM for Qwen) on the same H20 GPU class (App. D). The construction teacher sees development data; the deployment program for truth chains was refined by agreement with the teacher on ten development inputs before freezing (Sec 3.4). Task selection was informed by observed performance, including held-out results (App. H).

## Reference labels
BBH and MuSR answer keys (synthetic or programmatically generated task answers).

## n and intervals
600 held-out questions, five collection rounds, 30,000 predictions across ten policies; paired crossed bootstrap (5,000 draws) for accuracy and latency, resampling questions within tasks and rounds (Sec 4.3.2). Repeated measurements do not add distinct inputs (App. H). Narrative studies report counts without intervals.

## Test-data exposure
BBH (2022-2023) and MuSR (2024) are public with released answers; no contamination check for the teacher or Qwen. Development inputs were used in admission checks (App. H).

## Cost and latency
Online client latency on one H20 GPU, BF16: Abacus 0.255 s per question vs Qwen free reasoning 2.150 s (8.43-fold), direct Kev 0.022 s (Table 4). Offline construction: 322,117 teacher tokens across nine programs; no monetary cost; the token-work proxy is higher for Abacus than for free Qwen reasoning; the authors state the latency edge does not imply lower FLOPs, energy or financial cost (App. F, H).

## Calibration
None reported; factorized winning frequencies in the narrative studies are not calibrated confidence (App. H). Kev uses its released temperature.

## Cascade or escalation
None in the usual sense; the Abacus program replaces direct Kev. Date understanding uses a declared direct-Kev fallback in the six-task scope (Table 12).

## Option-name, cardinality, robustness tests
None. The authors list longer chains, paraphrases, entity substitutions and option reorderings as untested (App. H). Two truth-chain errors trace to one initial local label, diagnosed by replay (App. D.1).

## Code and data availability
App. G says the release provides prompts, nine construction programs, three deployment programs, judgment schemas and split identifiers; no URL appears in the extracted text.

## Authors' limitations (App. H)
Three-task presentation selected after inspecting broader results (six-task macro 83.30% vs direct 64.80%; logical deduction 68.50%, causal judgment 54.81%, date understanding 77.50%); the 99.67% result belongs to separately frozen artifacts after reference-agreement refinement; the nine construction trajectories were evaluated on development inputs; comparisons do not isolate joint interface construction; the task-conditioned envelope is post hoc; formats and sizes tested are narrow; latency edge is hardware specific.
