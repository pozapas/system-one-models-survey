# lan2026decisionrobust — DecisionRobust: Benchmarking Robustness for JEV Style Decision Models Across Text and Vision

- arXiv: 2610.19118v1 [cs.CL], 13 Oct 2026. Full text: fulltext/2610.19118.html and .txt (fetched 2026-10-28).
- Authors: Yifan Lan, Zhongye Liu, Yurui Chang, Hanyu Wang, Yongkang Du, Lu Lin, Jinghui Chen (The Pennsylvania State University). Affiliation type: academic.
- Code and data: "The benchmark is available at yifan-lan.github.io/DecisionRobust/" (abstract); a fuller pre-selection candidate set is also to be released (Section 2.3.3).

## Task and data
Adversarial robustness benchmark for Jev-style decision models (Choice, Noul and Score formats) over application tasks (Table 1): content filtering (AEGIS 2.0, PromptShield, SMS Spam), tool and skill routing (BFCL, Skill Router), workflow assessment (WorkflowEvals traces, customer service, security incidents), retrieval (NevIR, ESCI), GUI targeting (jevnav, ScreenSpot, Multimodal-Mind2Web), physical state and motion (arm, drive), market forecasting (Siim), visual decisions (ImajevBench, FinQA, Geometry3K), language diagnostics (SST-2, MMLU). 10 text attack strategies (DeepWordBug, Charmer, TextFooler, SememePSO, SCPN, PromptAttack S2/S3, StressTest, sensor edits, prompt injection with 4 templates and 2 locations) and 7 image strategies (5 common corruptions, optimised transfer attack with three surrogates, in-image and instruction injection). Metrics: sample-level and candidate-level attack success rate (ASR), label-consistent ("checked") ASR, flip ASR vs target ASR (Section 3).

## Decision models and versions
Text attacks are built on Jev "jev-1.13.0" as construction model (Section 2.3.1). Evaluation: 30 text model configurations (6 selection models, 24 held-out, e.g. Vega-27B, Lux-9B, NeoHorse-Jev-4B, GEV-26B, Mica-4B, OneJev 4B/9B/27B, GLiNER2.5-Decide-340M) and 17 vision configurations (5 selection, 12 held-out, e.g. Imajev-4B, Visual-Jev-4B, Jev-Omni, OneJev-4B, StandardOne-8B, Strands Decider-2B, Perplexity Decider v1.1-27B). Transfer targets for the large pool: KEV, AutoTrust, OpenJEV, Bosun, Liquid D1. Run dates, hardware and serving routes are not reported in the main text.

## Comparators and tuning-budget parity
Models receive identical candidates without further optimisation. Attack candidates were selected by how many of the six text (or five vision) selection models they fool, so selection models have an in-sample disadvantage; held-out models are used to report transfer (Section 2.3.3). Jev rows in Table 3 are attacks built against Jev itself (not transfer).

## Reference labels
Source-dataset gold labels (human or dataset-defined); attack validity judged by external LLMs (GPT-5 mini with DeepSeek-V4-Flash for text, Claude Sonnet 5 for images; both must recover the reference), GPT-5 semantic review plus human review of every text perturbation example, manual readability check for common image corruptions (Section 2.3.3). Ledger label type human_adjudicated (dataset answer keys, matching ledger.csv convention).

## n, sampling, intervals
Per-task pools small (N=3 to 120, many N=14 or 50, Table 3); ASR denominators are model-specific clean-correct samples. No confidence intervals or bootstrap reported. Curated sets: 141 text perturbations from 120 samples, 374 injections from 265 samples; 200 image perturbations, 223 in-image and 120 instruction injections; 160 image-question pairs.

## Test-set exposure
Source datasets are mostly public, but several application sets are 2026 community projects (for example the Siim trading set) and every attacked item is newly constructed, so ledger test_set_exposure is new. No contamination check.

## Cost and latency
Not reported.

## Calibration and cascade
No calibration analysis; Score correctness uses the API probability-weighted mean within 0.5 of the reference; Noul multiclass normalises truth probabilities. No cascade.

## Robustness results
Attacks transfer beyond the selection models; label checks substantially cut ASR in both modalities (for Jev SST-2 Choice, raw 93.9 vs checked 73.5; NevIR raw 98.0 vs checked 20.4; Table 3); perturbation robustness does not imply injection robustness (GLiNER2.5-Decide-340M 11.4% perturbation ASR vs 55.3% injection target ASR); optimised image perturbations transfer weakly (Figures 2 and 3, Tables 5 to 7). Option-name and language tests absent.

## Limitations (paper's own)
Individual decisions only, not downstream workflow effects; limited transfer of image perturbations; computational limits on attack methods, configurations and task coverage (Conclusion).
