# chen2026cognit — COGNIT-Guard: Calibrated Standalone Direct-Decision Guardrails with Heterogeneous CPU-NPU Confidence Cascading under Explicit Latency and False-Positive Constraints

arXiv:2609.33671v1 [cs.CR], 27 Sep 2026 (header). HTML retrieved 2026-10-28 from https://arxiv.org/html/2609.33671; saved as fulltext/2609.33671.html and .txt.

## Authors and affiliation

Hao Chen, School of Cyber Security, Guangdong Polytechnic Normal University, Guangzhou, China (title block). Affiliation type: academic. Acknowledges Huawei Ascend 910C compute from the Shenzhen Research Institute of Big Data (Section V).

## Task and data

Binary prompt-safety gating (benign compliance vs violation) before target-LLM prefill, with dual-use false-positive control. DUCS-Bench (Dual-Use Compliance Safety Benchmark), built by the authors from Chinese statutory consultations, enterprise compliance inquiries and red-team prompts: 3,663 raw items, 3,551 unique after SHA-256 deduplication; 28 train/test violation overlaps removed. Strict clean unseen test (N=607: 238 benign, 369 violations); full track N=635 (§IV-A). 3-way split (seed 42): train 2,485, validation 533, held-out test 533; live latency profiling on a stratified 150-item sample, N=130 binary slice (82 violations, 48 benign). OOD test: 2,100-question SafetyBench-ZH sample (300 per each of 7 hazard categories; 694 unsafe, 1,406 safe) mapped from multiple-choice to binary decisions; English XSTest (N=450) cited for reference only (§IV-A).

## Decision models evaluated

- Laya-322M, a cross-encoder direct-decision model with a typed 2-way softmax head, used zero-shot and after supervised boundary adaptation on DUCS-Bench (COGNIT-Guard) and after adding a 458-item experience-replay rehearsal slice (§III-A, §IV-F). No release tag or revision is given for Laya-322M.
- CLM-8B (Contrastive Language Model, Qwen3-8B backbone plus 73MB dual-tower heads), a bi-encoder baseline on Ascend 910C (§IV-C).
- Traditional ML baseline: TF-IDF plus XGBoost with kNN evidence (fast CPU mode 38.91 ms) acting as the CPU gatekeeper (§III-B, Table III).
- Cascade: CPU gatekeeper escalates to the NPU-resident Laya-322M when the gatekeeper's confidence is below threshold theta (validation-selected, 0.70 live, 0.80 offline) (Eq. 6, Algorithm 1).
- Reference numbers for GPT-4, Llama-2-70B-Chat, WildGuard, SingGuard are cited from other papers, not run here (Table V).

## Comparators and tuning-budget parity

The ML baseline and the cascade gatekeeper are trained on the same 70% training split; Laya is fine-tuned on DUCS-Bench (training time 34.55 s for Laya-322M head adaptation per §IV-C; 41.85 s with rehearsal per §IV-F), while "Zero-Shot DFM" is untuned. Asymmetry between tuned in-domain and zero-shot systems is the point of the experiment. The cascade threshold is tuned on validation only (§III-B, §IV-A). Seeds: seed 42 for splits; a single run, no seed repetition reported.

## Reference labels

Each prompt "independently labeled by two domain annotators (0=benign compliance, 1=safety violation; inter-annotator Cohen's kappa=0.91, with disagreements resolved by a third senior reviewer)" (§IV-A). Reference type human_adjudicated. SafetyBench-ZH labels are the benchmark's own multiple-choice items mapped to binary.

## n, sampling, intervals

N=607 clean unseen test; Wilson 95% CIs for accuracy and FPR, paired McNemar test (p=1.19e-4 vs ML) and two-sided Fisher's exact test for FPR (§IV-B, Table II). Latency from 20 warm-up runs then B=1 on an Ascend 910C, 64 GB HBM, CANN 8.0, torch_npu 2.1, FP16 (§III-C, §IV-A). CPU: Intel Xeon 2.60 GHz, 32 GB RAM.

## Test-set exposure

DUCS-Bench is author-built and released with the paper (new); leak-free deduplicated. SafetyBench-ZH is a public benchmark (cited as [21]); date not stated in text; the model was not trained on it ("zero overlap against our N=458 experience replay rehearsal pool").

## Cost and latency

Laya-322M on Ascend 910C: mean 21.77 ms (P50 21.53, P95 23.44), 45.90 QPS at B=1 (Table II). Live serial cascade: 41.63 ms mean (P50 39.47, P95 76.25) with 5.38% (7/130) queries escalated to the NPU (Table III). Offline cascade at theta 0.80: 14.27 ms, 33.7% NPU ratio. CLM-8B uncached single stream 45.78 ms, batched B=64 6.64 ms per item, HBM VectorArena cache hit 0.60 ms P50 (Table IV). Cold-start unpinned Laya 48.20 ms. No dollar costs.

## Calibration

ECE (15 equal-width bins, Eq. 4) and Brier. COGNIT-Guard ECE 1.12%, Brier 0.0104; Traditional ML 13.11%, 0.0525; Zero-shot DFM 5.38%, 0.1654 (Table II). Calibration arises from supervised boundary adaptation; "validation-calibrated" posteriors, but no separate temperature or isotonic step is described (post_hoc: none stated). CLM-8B head adaptation: ECE 0.83%, Brier 0.0091 (§IV-C).

## Cascade or escalation

CPU fast gatekeeper to NPU-resident Laya-322M; the live serial cascade settles 94.62% (123/130) of queries on CPU, 99.23% accuracy (129/130), FPR 0.00% (0/48) at 41.63 ms mean (Table III, §IV-D). Offline sweep (N=635): pure NPU 98.90% accuracy, 0.42% FPR, 21.76 ms; theta 0.80: 98.58%, 0.00% FPR, 14.27 ms.

## Option-name, cardinality, language and robustness tests

Keyword perturbation test: holding sensitive keywords fixed while varying inquiry markers leaves zero-shot P(y=1) above 0.88, whereas COGNIT-Guard gives 0.003 on benign inquiries and 0.992 on attacks (§IV-B). OOD alignment tax on SafetyBench-ZH (Table V). Chinese-language data; English XSTest numbers cited from other work only. No option-order tests (binary).

## Code and data availability

Code, configs, latency scripts and anonymised DUCS-Bench manifests at https://github.com/moyuan10086/cascaded-guardrail-npu; external benchmarks referenced by sample IDs (Section V and Abstract).

## Limitations stated by the authors

No dedicated limitations section. §IV-G lists remaining failure regimes (anti-monopoly regulatory inquiries, academic camouflage of disinformation, borderline commercial health claims). Calibration of the live latency estimate rests on a 130-item live slice.
