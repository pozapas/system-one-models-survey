# grey_kev — Kev-9B (jaredpalmer) model card and GitHub report vs Jev

- Not arXiv. Grey literature: Hugging Face model card + GitHub repository README.
- source_url: https://huggingface.co/jaredpalmer/kev-9b ; https://github.com/jaredpalmer/kev
- Affiliation type: independent (Jared Palmer; no institutional/vendor affiliation stated; open-source project comparing itself against the vendor's Jev).
- Fetched: 2026-09-24. Files: fulltext/grey_kev_hf.md (model card), fulltext/grey_kev_github.md (repo README, serving-performance benchmarks).
- License: Apache 2.0 (adapter, head, and Qwen3.5 base).
- No seed claims assigned to Kev in the extraction brief ("Extract any evaluation numbers").

## Task and data
Typed decision evaluation (Choice/Noul/Score) on several partitions of an internally curated suite ("decision-v7"):
- **decision-v7 development** (in-distribution): 1,204 records, ten trained public sources (Banking77, BoolQ, AG News, MultiNLI, SST-5, Yelp Review Full, TREC, DBpedia-14, Amazon Reviews Multi EN, IMDB) + programmatic policy data.
- **transfer-v4 development** (out-of-domain): 764 records, six never-trained sources + held-out policy structures.
- **transfer-v4 test** ("locked test", read once per candidate).
- **transfer-v9 development**: newer columns (MMLU-Pro 10-way, buried-state robustness, unknowable-confidence share).
- **External suites** run by third parties on their own items, reusing Kev's and Jev's published numbers: SemIf's authored-144 set, scienthoon's 900 support tickets, ekzhang's 1,000-question MMLU-Pro sample.

## Decision models / version pins
- **Kev-9B**: LoRA adapter (r=16, 45.4M trainable params) + pointer head on `Qwen/Qwen3.5-9B-Base` (revision `68c46c4b`); hub `jaredpalmer/kev-9b`, trial `night2-9b-du/00-trial-0`; the pre-delta checkpoint is at revision `v7-base`. Also compared: Kev-8B (Qwen3 base, not Qwen3.5), Kev-4B, Kev-0.8B.
- **Jev**: version not pinned to a specific string in this source (referred to simply as "Jev"); described as accessed via "TypeSafe's public `/v1/systemone` contract" and "live Jev" for the SemIf comparison, implying a hosted-API call at evaluation time rather than a fixed offline checkpoint.

## Comparators and tuning-budget parity
Kev-9B is purpose-trained (LoRA, 2 epochs on `decision-v7`, then a 15-minute "delta" fine-tune on 1,425 additional records) specifically for this suite; Jev is queried as a general hosted decision model with no suite-specific tuning ("No Jev outputs were used for training" — Kev's training did not distill from Jev). comparator_tuning_budget for Jev rows = "not reported (general hosted model, zero-shot, not tuned on this suite)"; for Kev rows = "fine-tuned (LoRA + delta fine-tune)".

## Reference labels
Mix of original public-dataset gold labels (Banking77, BoolQ, AG News, MultiNLI, SST-5, etc. — human_adjudicated) and programmatically generated policy/rule-structure records (896 policy minimal-pair records over nine template families; 1,680 records from 60 randomly generated rule structures) — these programmatic records are best classed as reference_label_type = administrative_field (rule-derived ground truth, not human-annotated).

## n and sampling
decision-v7 dev: 1,204 records. transfer-v4 dev: 764 records. Locked test: read once per candidate (`runs/locked/kev-9b-night2-du-ungated/`). Training: 10,000 public records (1,000/source) + 896 policy records + 1,680 rule-structure records for the base recipe; the delta adds 1,425 new records (900 date-bearing policy cases, 255 evidence-removed "unknowable" cases + 270 intact controls) mixed with 2,000 replayed training records. External suites: SemIf's 144 items, scienthoon's 900 tickets, ekzhang's 1,000-question MMLU-Pro sample.

## Test-set exposure
The `decision-v7`/`transfer-v4` suites and the locked test are original to this project (constructed 2026) — test_set_exposure = new for these. The underlying public source datasets (Banking77, BoolQ, MMLU, etc.) are public-pre-2026. External suites (SemIf, scienthoon, ekzhang) are third-party, dates/exposure not independently verified — recorded as unclear.

## Cost and latency
GitHub README "Serving Performance" section — self-hosted, not a metered API, so no per-request dollar cost like Jev's; GPU rental cost given instead. Table (model time per request, median of 20 requests, "new state / repeated state" format): Kev-9B on H100, 6 questions: 37 ms / 24 ms (CUDA-graph path); with fused Triton kernels, 6 questions on H100: 24.1 ms / 17.0 ms. GPU $/hour: L4 $0.80, L40S $1.95, H100 $3.95, A100 80GB $2.50. "Kev-9B bf16 needs ~19 GB of GPU memory for serving; training took 91 min on one H100 (peak 39.5 GB)." hardware_or_provider = "self-hosted (H100/L40S/A100/L4), flash-linear-attention + CUDA graphs". No directly comparable Jev latency/cost figures are given in this source (Jev is accessed via its hosted API, priced/timed differently and not benchmarked for latency here).

## Calibration
"Calibration is built in. `head.pt` carries a temperature (T=2.30) fitted on this checkpoint's in-distribution development rows by minimising negative log-likelihood... It never changes an answer: the argmax is identical... Per-(type, option-count) temperatures were tested and are worse out of domain. The fit uses no out-of-domain or test data." Out-of-domain (transfer-v4 dev, 764 records): Kev-9B raw ECE 0.106 -> served (T=2.30) ECE 0.042, vs Jev's ECE 0.049 (i.e., Kev's own post-hoc-calibrated ECE is slightly BETTER than Jev's on this specific comparison). Brier: Kev raw 0.286 -> served 0.264, vs Jev 0.211 (Jev still has lower Brier). calibration_quantity = ECE / Brier (binning method not specified); post_hoc_calibration = temperature (T=2.30, fit by NLL minimization on in-distribution dev rows only).

## Cascade / escalation
Not applicable — a direct model-vs-model comparison, not a routing/cascade study. A `date_facts` preprocessor is reported separately as a non-model intervention (see Robustness below), not a cascade.

## Robustness / stress tests
- **Confident-error rate out of domain** (p>=0.9 and wrong): Kev-9B raw 8.7% -> served (calibrated) 4.0%, vs Jev 3.7% — close after Kev's own calibration fix.
- **Coverage at <=5% error budget** (share of decisions automatable): Kev-9B raw 0.47 / served 0.45, vs Jev's 0.70 — Jev automates substantially more of the workload at the same error tolerance, the clearest "Jev leads" result in this source.
- **Unknowable items answered at >=0.9 confidence** (lower is better, transfer-v9): Kev-9B (raw) 0.26 -> v7-base 0.05 -> served/delta-tuned 0.00, vs Jev 0.09 — Kev's delta fine-tune specifically targeted and fixed over-confident answers on evidence-free ("unknowable") items, ending up better than Jev on this specific stress test.
- **Knowledge gap set by the base model**: MMLU 0.74 (Kev) vs 0.90 (Jev); MMLU-Pro 0.515 (Kev) vs 0.840 (Jev) — "the untrained Qwen3.5-9B scores the same, and a Kev on the 35B-A3B MoE did not move MMLU-Pro either," i.e., this gap is attributed to base-model knowledge, not the decision-adapter training.
- **Date-arithmetic weakness and preprocessor fix**: `deadline` (3-level date arithmetic) Kev 0.80 vs Jev 0.93, improving to 0.90 for Kev with the `KEV_DATE_FACTS=1` preprocessor (explicitly reported separately, "never folded into the model's own numbers").
- **Delta fine-tune tradeoffs** ("What the delta cost"): coverage at <=5% error fell (0.53->0.47 dev; 0.66->0.62 locked test), confident errors rose (7.5%->8.7% raw), MMLU-Pro fell 0.545->0.515, scienthoon's ECE rose 0.082->0.113 — a fine-tune that fixed one failure mode (unknowable-item overconfidence, dates) while worsening others; "the pre-registered criteria for the delta were met for dates and for the unknowable-confidence behaviour and not met for coverage; the locked read decided promotion" anyway.
- **Numerical-precision robustness of serving optimizations**: CUDA-graph and fused-kernel paths differ from the fp32 evaluation path by at most 0.012-0.039 in probability, with "at most one of the 280 highest-probability answers" changing across setups — a serving-fidelity check, not an accuracy result per se.

## Code and data availability
GitHub: https://github.com/jaredpalmer/kev (Apache 2.0), with `PLAN_Qwen35.md`, `PLAN.md`, `runs/leaderboard.md`, per-trial hashes and paired bootstraps, `result.json` per run. code_available = "yes (https://github.com/jaredpalmer/kev, Apache 2.0)".

## Limitations (source's own, "Known limits" section)
- "Slow on a Mac. The DeltaNet kernels have no MPS implementation... A five-question request that takes 0.3 s on Kev-8B takes about 2 s here in bf16 on an M5."
- "Knowledge... is the remaining gap and is set by the base" (MMLU/MMLU-Pro gap vs Jev, see Robustness above).
- "The raw logits are over-confident out of domain; the built-in temperature (T=2.30) fixes most of it without changing any answer... Coverage at a 5% error budget is 0.47-0.62 against Jev's 0.70."
- Requires `transformers >= 5.17` and `peft >= 0.21`; 9B bf16 needs ~19 GB GPU memory to serve, 91 min / 39.5 GB peak to train on one H100.

## Notes for cross-referencing other rows in this ledger
Kev's own comparison numbers for Jev (e.g. "Jev: 0.857" out-of-domain, "0.845" in-distribution) are presented without a pinned Jev version string in the fetched card text — unlike jev-1.13.0 seen elsewhere in this ledger (e.g. wu2026reflex, li2026kite, grey_bespoke_nimble). Treat Kev-vs-Jev comparisons as measured on Kev's own suite by Kev's own author, on an unspecified/unpinned Jev snapshot, and interpret head-to-head numbers accordingly (independent/self-reported, not vendor- or peer-reviewed).
