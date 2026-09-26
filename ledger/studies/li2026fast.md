# li2026fast — Fast Intent-Driven Service Orchestration with Jev for 6G Edge Networks

arXiv:2609.23136v1 [cs.NI], submitted 19 Sep 2026. HTML retrieved from https://arxiv.org/html/2609.23136v1.

## Authors and affiliation

Delong Li, Xu Wang, Haochen Gong, Rui Lang, Guangsheng Yu (corresponding, Guangsheng.Yu@uts.edu.au); same author group and same "School of Electrical, Mechanical and Biomedical Engineering, University of Technology Sydney" affiliation as `li2026replacing` (2609.22753), and the two papers appear to share the same real-OCR testbed pattern (two-node service, Tesseract, IIIT5K), though this paper's application is a mobile/NR image service rather than the earlier fixed two-node service — flagged for the curators to consider jointly when pooling, since these are not independent measurement instruments. Affiliation type: **academic**.

## Task and data

Intent-driven 6G mobile-edge service orchestration: a natural-language contract (permitted execution locations, deadline, priority) must be interpreted while wireless requests continue to arrive under NR delivery, handovers, and shared edge queues (§III). Four measurement blocks (Table I): Integration (14 trajectories × 22,500 requests), Cloud (60 × 22,500), Local interface (36 × 22,500), Image service (16 × 270). The Integration and Cloud/Local blocks use a modeled edge-execution layer driven by 5G-LENA NR packet traces (ns-3.48, 5G-LENA v5.1, seed 42, run 1); the Image block additionally executes real Tesseract OCR on IIIT5K images after simulated NR delivery.

## Decision models / systems evaluated

- **Jev** — "TypeSafe Jev 1.13" via OpenRouter, provider fallback disabled, native Choice questions (Appendix A-A).
- **DeepSeek** — `deepseek-v4.1-flash` via Together/OpenRouter, strict JSON schema, temperature 0, 128-token limit, reasoning disabled.
- **Gemini** — `Gemini 3.1 Flash Lite` via Google AI Studio/OpenRouter, strict JSON schema, temperature 0, 256-token limit, reasoning "minimal".
- **Qwen3.5-4B** — self-hosted via vLLM 0.29.0 on one NVIDIA L40 GPU, BF16, 32,768-token context, ≤4 sequences, thinking disabled. Two interfaces compared: an 18-profile catalog-identifier interface (33/63 correct) and a direct-attribute interface (63/63 correct); the direct-attribute interface becomes the principal local comparator after this correctness gap is discovered (§V-E).
- **Structured-input reference** — receives canonical contracts directly (no model call), used as an upper-bound dashed line, not a decision model.

Tuning-budget parity: Jev/DeepSeek/Gemini share the "same prompt" contract structure (`comparator_tuning_budget = same prompt`); Qwen's interface choice is explicitly flagged by the authors as changing both quality and latency (`not reported`, since it is a deliberate interface ablation rather than a tuning-budget-matched condition).

## Reference labels

Canonical contracts are researcher-authored ("authored transitions", §VI-D) rather than LLM-generated (contrast with `li2026replacing`, where an agent generated Study A's reference labels) — coded `administrative_field` for the three-field contract-correctness rows. Real image-service OCR correctness against IIIT5K reference text (Unicode NFC, whitespace-trimmed, case-preserving) is coded `human_adjudicated`. Completion-fraction rows (deadline/placement/priority met) use `task_outcome`.

## n, sampling design

Cloud block: 21 distinct contract descriptions × 3 timing repeats = 63 contract checks per model, 22,500 requests per trajectory. Local block reuses the same 21-description text set with a contemporaneous Jev remeasurement and two Qwen interfaces. Image block: 96 public IIIT5K test images, 3 images/s per UE for 30 s, two mobility/load traces × 2 repeats = 4 trajectories × 270 requests = 1,080 requests per method.

## Test-set exposure

Bounded, authored contract catalog and transitions — `new`. IIIT5K source images are a public pre-existing corpus, but the sampled 96-image set, contract catalog, and mobility traces are newly constructed for this paper (seed 42).

## Cost and latency

Hardware/provider: Jev/DeepSeek/Gemini via OpenRouter; Qwen3.5-4B self-hosted via vLLM on one NVIDIA L40 GPU; NR simulation via ns-3.48 + 5G-LENA v5.1; real image service on two logical workers sharing one host, Tesseract via HTTP.

- Cloud block median decision latency (63 checks, all three models correct on all contracts): Jev 374.6 ms vs DeepSeek 482.9 ms (22.4% reduction) and vs Gemini 984.5 ms (61.9% reduction) (Table II).
- Local block: Jev 356.2 ms vs direct-attribute Qwen 757.1 ms (53.0% reduction) (Table III).
- Integration block: cached interpretation + numerical scheduling raises Jev's updated-contract completion from 43.24% (direct model-selected placement) to 95.59% (§V-A).
- Real image service (1,080 arrivals/method): Jev completes 459 correctly on time vs DeepSeek 463, Qwen (direct-attribute) 435, structured reference 473; Jev's contract-interpretation latency 408.9 ms vs DeepSeek 497.0 ms vs Qwen 759.9 ms (Table IV).
- Billed API cost inverts the latency ordering: cloud block, Jev $0.002125 vs DeepSeek $0.001262 vs Gemini $0.009698 for 21 calls — "Jev supplies the faster measured response; DeepSeek has the lower billed interpretation fee" (§VI-C). Image-service fees (Table IV) likewise favor DeepSeek ($0.000939 vs Jev $0.001616).

## Calibration analysis

None reported.

## Cascade / escalation results

None as such, but the Integration block is effectively an ablation of two orchestration architectures (direct model-selected placement vs. cached-interpretation-plus-numerical-scheduling) for the same three models — recorded as `cascade_result = ""` in the ledger since it is an architectural not a confidence-threshold escalation.

## Option-name / robustness stress tests

Interface-sensitivity result: the same Qwen3.5-4B weights answer 33/63 contracts correctly via an 18-profile catalog-identifier interface vs 63/63 via a direct-attribute interface, with mean updated-scenario completion rising from 85.17% to 91.84% despite a longer response (447.9 ms → 757.1 ms; Table III, §V-E). "Exchanged waiting time" replay (§V-D): substituting each comparator's recorded model/scheduling waits into Jev's interpreted contracts exactly reproduces DeepSeek's (12/12 cloud trajectories) and direct-attribute Qwen's (12/12 local trajectories) modeled completion summaries, isolating the completion gap to control-wait timing rather than contract semantics.

## Code and data availability

No code/data repository URL given in the paper text. `code_available = no`.

## Paper's own stated limitations (§VI-D)

Latency comparisons "include the model, serving system, and transport path" without attributing delay to individual provider components. Bounded contract catalog and authored transitions; timing repeats reuse the same inputs; the application adds only two mobility/load traces, so requests sharing a trajectory are dependent observations. Completion differences are descriptive, "including the four-request Jev–DeepSeek gap in the image service." Two logical workers share one host in the real service. Suggested extensions: independently varying mobility/link load/distributed edge capacity, and independently sampled contracts.

## Notes on seed claims

No seed claims were assigned for this paper ("No seeds" per the task brief) — headline latency/accuracy/cost extracted directly into `parts/ledger_B.csv` (rows L212–L223). No corresponding rows in `parts/seed_check_B.csv`.
