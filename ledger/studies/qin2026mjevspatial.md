# qin2026mjevspatial — MJev-Spatial: System One Spatial Intelligence via Native Attention Matching

arXiv:2610.22276v2 [cs.CV], v1 15 Oct 2026, v2 26 Oct 2026. HTML (v2) retrieved 2026-10-28 (fulltext/2610.22276.html, .txt). Coder: batch V16.

## Authors and affiliation

Luozheng Qin, Yuhan Zhu, Changhai Zhou, Qian Qiao, Jun Gao, Yuhua Zhou, Harry Zhang, Xiangyu Zeng, Yuxuan Liu, Yuxin Lu, Kaijie Chen, Andrew Chen, Pony Ma. Contact emails at m.fudan.edu.cn and mindlab.ltd (title block); affiliation lines are not rendered in the HTML text, so type is inferred from emails: mixed (university plus company). Own-model paper.

## Task and data

A multimodal "System 1" decision model for spatial intelligence: every output type (supplied options, numerical values, 2D points) is cast as classification over a finite candidate set scored with the backbone's final-layer pretrained query and key projections, no new parameters (§3, Eq. 1, 6). Numerical and point outputs use coarse-to-fine multi-stage classification. Evaluation on 12 public spatial benchmarks (§4.1): SAT, CV-Bench, BLINK, MMSI-Bench, RefSpatial-Bench, Where2Place, Point-Bench, RoboSpatial VQA and pointing, ERQA, EmbSpatial, VSI-Bench. Overall = mean over 12 benchmarks, each benchmark equal weight (App. D.3). Request counts per benchmark in Table 10 (e.g. SAT real 300 requests = 150 questions x 2 orders; CV-Bench 2.6K; RefSpatial 200; Point-Bench 982). Ablations use a fixed 72K-QA mixture (25K SAT, 22K VST-P, 25K RefSpatial) and a 300-example internal development set VST-300 for length (§4.1).

## Models evaluated

MJev-Spatial: Qwen3.5-4B backbone, full-parameter fine-tuned, vision encoder and merger frozen, 12.3M converted QA (RefSpatial, SAT, SenseNova-SI, VSI-590K-image, VST-P), final "r12" corpus (§3.3, App. B). No separate version string. Jev is cited as the precedent (TypeSafe AI, 2026) but is not evaluated. Earlier Molmo2-ER-based prototype with LoRA and a decision head mentioned (§2). In-paper decision-model comparison: native Q/K vs linear classifier vs KEV pointer under matched 72K training (Table 3).

## Comparators and tuning-budget parity

Seven autoregressive VLMs: Qwen3.5-4B (base), Qwen3-VL-8B-Instruct, InternVL3.5-8B, Molmo2-ER, Spatial-SSRL-Qwen3VL-4B, SenseNova-SI Qwen3-VL-8B, SpatialThinker-7B (§4.1). Base evaluated locally with BF16, greedy decoding, thinking disabled, 2,048 generated tokens for choice/pointing (App. D.2). The proposed model is trained on 12.3M QA from the very sources that overlap with several evaluation benchmarks' training sets (SAT, RefSpatial, VST-P), while generalist baselines are not trained on them (SenseNova-SI is, partially). Parity: asymmetric. The paper does not state prompt protocol for the other six baselines in the text I read. Pilot ablations: "Each model is trained for 2.2K updates using the same optimizer, learning-rate schedule, and image-token budgets" (§4.1).

## Reference labels

Public benchmark gold answers and masks (administrative_field); VST-300 is a fixed internal development set (origin of labels not described in the main text).

## n, sampling, intervals

No confidence intervals, no seeds or repeat runs, no significance tests anywhere in the main text. Single-run scores. Point-Bench macro-averaged over five categories (App. D.1).

## Test-set exposure

All 12 benchmarks are public (released pre-2026). Contamination handling: training examples whose images exactly match public evaluation images or are near-duplicates (dHash Hamming <= 2, aspect within 1%, MAD <= 6) are removed; 201 near-duplicate QA excluded; "These checks target nearly identical images; they do not establish physical-scene or video-neighbor independence" (App. B.3).

## Cost and latency

Mean single-query latency 160.6 ms across 12 benchmarks on one NVIDIA B200, batch size one, including image I/O, preprocessing, transfer, inference and decoding; warmup excluded; 2.5x faster than the fastest autoregressive baseline and 5.6x faster than Qwen3.5-4B (§4.2, §5, Table 11). Training: global batching with cross-GPU load balancing raised throughput 30.78% (99.06 to 129.54 QA/s, Table 6, 8 L20D GPUs). No dollar costs.

## Calibration, cascade

No calibration analysis (probabilities are produced by softmax but accuracy only is evaluated). No cascade or escalation.

## Robustness

Candidate order: training deterministically shuffles options; SAT is evaluated in both answer orders (App. D.1, §3.2). No language or cardinality tests. Ablations on numerical discretization, visual refinement, multi-point decoding (§4.3). Mean of Overall: 65.64 vs Qwen3-VL-8B-Instruct 62.79, Molmo2-ER 59.06, Qwen3.5-4B 54.80, Spatial-SSRL 60.08, SenseNova-SI 56.90, SpatialThinker 39.68, InternVL3.5-8B 48.24 (Table 2).

## Code and data

Code https://github.com/Fr0zenCrane/MJev-Spatial (title block). Training data are public datasets with a conversion pipeline (App. B); evaluation manifests pin dataset revisions (references).

## Own limitations

No dedicated limitations section. The paper notes: the geometric bound on point error does not guarantee accuracy (§3.1); earlier matched-head evaluations used an 8,192-token cap while later runs use 32,768 (App. D); near-duplicate checks do not establish scene independence (App. B.3); short training-throughput runs include no quality evaluation (§4.4). Ablation conclusions are task dependent ("no consistent winner", §4.3).
