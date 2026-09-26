# li2026replacing — Replacing Large Language Models with Jev Decision Models for Low-Latency Edge Service Orchestration

arXiv:2609.22753v1 [cs.DC], submitted 19 Sep 2026. HTML retrieved from https://arxiv.org/html/2609.22753v1.

## Authors and affiliation

Delong Li, Xu Wang, Haochen Gong, Rui Lang, Guangsheng Yu (corresponding, Guangsheng.Yu@uts.edu.au). "The authors are with the School of Electrical, Mechanical and Biomedical Engineering, University of Technology Sydney, Sydney, Australia." Affiliation type: **academic**.

## Task and data

Edge-service admission: a natural-language service request must be interpreted into a four-field intent contract (service = count/detection/OCR/unsupported; locality; quality floor; urgency; 4×3×3×3 = 108 possible tuples) before a shared scheduler places the job (§III-A, Table I). Two studies:
- **Study A** — 216 synthetic English requests (6 wording families × 2 instances of each of the 108 field combinations), recurring across three consecutive measurement blocks (seeds 42/43/44), combining live API decision latency with modeled execution on a simulated edge topology (4 edge nodes + 1 cloud node) (§IV-B, Appendix A-C). No images processed in Study A.
- **Study B** — a real two-node OCR service (local macOS worker + remote Linux worker via SSH), executing Tesseract 5.5.3 on IIIT5K scene-text images. Eight conditions (steady/bursty arrivals × changing/repeated text × cache off/on), each with 48 arrivals (36 supported OCR + 12 unsupported), run once per of four backends (Appendix A-D).

## Decision models / systems evaluated

- **Jev** — accessed via "OpenRouter's Decisions endpoint with identifier typesafe/jev-1.13; responses identify jev-1.13-20260917 and provider TypeSafe" (Appendix A-A). Four native Choice questions per request return the shared intent fields in one call.
- **DeepSeek** — `deepseek-v4.1-flash` via OpenRouter, pinned to Together, provider fallback disabled; strict four-field JSON, temperature 0, 128-token limit, reasoning disabled (reasoning-token counts recorded as zero).
- **Qwen2.5-7B-Instruct** (Study B only) — revision `a09a35458c70`, self-hosted BF16 on one NVIDIA L40, Transformers + SDPA, PyTorch 2.2.0+cu121; same generative prompt/contract as DeepSeek, greedy decoding, 128-token limit.
- **Rules** (Study B only) — a fixed keyword/regex parser, untuned on evaluation wording.

Tuning-budget parity: Jev and DeepSeek receive the "same intent contract, admission limits, execution policy, and caching mechanism" (§IV-A) — coded `comparator_tuning_budget = same prompt`. Qwen and the rule parser are not tuning-matched to Jev (different mechanism class); coded `not reported` where relevant.

## Reference labels

Study A: "An agent generates both the descriptions and their reference labels" (§IV-B) — coded `llm_teacher`. Study B: OCR correctness is checked against IIIT5K's dataset annotations after Unicode NFC normalization and whitespace trimming, case retained — coded `human_adjudicated`. Operational/modeled completion (deadline + placement + tier + priority match) uses the evaluator's own canonical contract, `task_outcome`.

## n, sampling design

Study A: 216 requests × 3 blocks = 648 semantic measurements per model; 24 paired service conditions (8 conditions × 3 blocks), 48 arrivals each (884 supported arrivals per backend total across the fixed matrix, plus 268 unsupported). Study B: 8 conditions × 48 arrivals = 384 arrivals per backend (288 supported OCR + 96 unsupported), executed once per backend in randomized sequential order, seed 42.

## Test-set exposure

Synthetic requests and images assembled for this study, measured 18 Sep 2026 — coded `new`. IIIT5K itself is a public pre-existing scene-text corpus, but the specific 20-training/80-test image sample (seed 42; "20 training and 80 test images," Appendix A-D) and request texts are newly drawn for this paper.

## Cost and latency

Hardware/provider: Jev and DeepSeek via OpenRouter (TypeSafe / Together); Qwen self-hosted on one NVIDIA L40 GPU; real OCR service on one local macOS worker + one remote Linux worker over SSH, 6 processor cores + Qwen's accelerator on the remote side. Decision latency measured client-side, 2 s request deadline, 4 concurrent interpretation slots, 15 s API timeout, no retries (Appendix A-B).

- Study A median decision latency: Jev 314.7–320.7 ms vs DeepSeek 381.4–434.7 ms across 3 blocks (26.5%, 26.1%, 15.9% reductions); p95 reductions 36.7%/33.0%/9.1% (§V-A, Table II).
- Study A API fees per operational completion: 69.15–72.57% lower with Jev across 24 paired conditions (§V-E).
- Study B end-to-end latency (cache-disabled, common-success subset): 11.1–25.3% lower with Jev; median per-request savings 70.6–135.7 ms (Table IV). Caching largely erases the gap: steady-repeated cache-on medians 110.9 ms (Jev) vs 112.4 ms (DeepSeek), paired saving −0.37 ms.
- Study B API fees per correct OCR completion: 68.97–70.61% lower with Jev over all 8 conditions (~$0.011–$0.067/1000 completions for Jev vs $0.036–$0.215 for DeepSeek); fees exclude compute/communication/energy/maintenance (§V-E, Fig. 8).

## Calibration analysis

None reported — the paper is a latency/completion/cost study, not a probabilistic-calibration study. `calibration_quantity = none`.

## Cascade / escalation results

None. No routing/cascade design in this paper.

## Option-name / robustness stress tests

No explicit option-order or language stress test. The paper does report a semantic-accuracy trade-off: DeepSeek is more exactly-correct on the strict four-field endpoint (216/215/216 out of 216 across blocks) vs Jev (214/213/212); eight of Jev's nine errors replace "unspecified" urgency with "normal" urgency (operationally equivalent under this scheduler), and one maps an unsupported translation request to OCR (§V-A, Fig. 2).

## Code and data availability

No code or data repository URL given in the paper text. `code_available = no`.

## Paper's own stated limitations (§VI-C)

"The studies use synthetic English requests, repeated texts and images, and one measurement session; completion retention is descriptive." Real service has only two workers and one service family. Hosted timings include provider and network paths (comparing deployed services, not isolating internal model inference); API fees cover only interpretation calls, excluding local compute/communication. Next steps: independently authored requests across days/services/network conditions, and adding a domain-trained classifier/bounded extractor to the comparison.

## Notes on seed claims

No seed claims were assigned for this paper (brief instructs "No seeds, so extract the headline latency, accuracy and cost" — done above and in `parts/ledger_B.csv`, rows L200–L211). No corresponding rows in `parts/seed_check_B.csv`.
