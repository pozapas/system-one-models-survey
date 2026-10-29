# li2026seeing

arXiv 2610.33702, v1 24 Oct 2026, v2 27 Oct 2026 (full text read at v2; the screening line and abstract numbers 78.4 / 72.1 / 74.8% match). "Seeing the Options: Typed Decisions over Visual Candidates with Reusable Option Memory." Single author Fengxin Li, Harbin Institute of Technology, Shenzhen. Affiliation type: academic. (title block)

Study type: own-model (Iris) built on Jeva's decision module, compared on the same backbone with a retrained joint-encoding baseline.

## Task and data
- Multimodal-Mind2Web element selection recast with image candidates: each candidate is the element's screenshot crop (6 px padding, minimum side 48 px, longest 336 px) with a short tag-and-attribute label, K=16, deduplicated by (text, image bytes), order shuffled with a seed derived from the record id. Steps: train 7,751; cross-task 1,337; cross-website 1,017; cross-domain 4,042 (6,396 test records); 4.3 to 6.1% of steps have the gold element absent and are kept as null targets (81 / 44 / 222 null steps). (Sec. 4, App. B)
- Other evaluations: OneJev-Data (94,707 released rows, 2,000 held out) for typed outputs and null detection; JevBench (231 text rows) and ImaJev-Bench (154 dev rows with public labels) taken from the MetaEncoder comparison; MMEB-V2 reranking of the top 16 of Qwen3-VL-Embedding-2B, 12 tasks, 1,000 queries each; full-page candidate pools (658,639 candidates over 1,337 steps) for scaling and reuse. (Sec. 4, 5.6, 5.7, 5.9, 5.10)
- Reference labels: the Mind2Web gold element from human demonstrations (human_single); MMEB-V2 dataset ground truth; the provenance of OneJev-Data, JevBench and ImaJev-Bench labels is not described in this paper. (Sec. 4, 5.6)
- Mind2Web (2023) and MMEB-V2 are public and predate 2026; no contamination check for the Qwen3.5 backbone.

## Decision models
- Iris-4B: Qwen3.5-4B vision-language backbone (vision tower frozen), LoRA rank 64 initialised from Jeva-4B's adapter, Jeva's decision module unchanged; independent per-candidate encoding (default), or state-conditioned encoding (candidate encoded after the state but never after another candidate). Stage 1 on 80,000 OneJev-Data rows (the run's final save was lost to a distributed-training fault), stage 2 on 7,751 Mind2Web steps for 2 epochs. Released checkpoints: Iris-4B (mixture of 65,502 rows) and Iris-4B-conditioned (with an abstention stage); no checkpoint hashes in the text. (Sec. 3, 5.8, App. A)
- OneJev-4B (released weights, and retrained with LoRA r=32 on the same 7,751 steps in its crops-in-state format, 2 epochs); Jeva-4B numbers are reported from its own paper, not rerun; OpenJev-27B and MetaEncoder-30B numbers are copied from the MetaEncoder paper. (Sec. 5.3, Table 3)

## Comparators and tuning parity
- Retrained OneJev and conditioned Iris receive the same 7,751 steps for two epochs, final checkpoints reported without selection; this is the controlled comparison. Hyperparameters differ (OneJev LoRA r=32, Iris r=64). (Sec. 5.4, App. A)
- Selection on test-like data: a "selected" checkpoint (epoch 2, step 50) and the abstention margin delta=0.24 were chosen on the cross-task test split, so released cross-task numbers (89.75, 92.07) are marked as selection-split numbers; the released rows carry that selection. (Sec. 5.4, Table 2)
- Jeva's text-candidate numbers are a reference point, not a controlled comparison. Stage 1 checkpoint is an early save (at 86% of an epoch). (Sec. 7, App. A)

## Results
Mind2Web K=16 (cross-task / cross-website / cross-domain): Iris-4B independent 78.38 / 72.07 / 74.84 with flip rate 0.00; zero-shot Iris 31.11 / 25.07 / 32.73; OneJev-4B released with crops in state 37.85 / 37.46 / 34.83 (flip 50.64 / 52.80 / 54.30); OneJev-4B retrained 90.58 / 89.48 / 91.59 (flip 7.63 / 10.13 / 7.99); Iris state-conditioned 89.60 / 84.46 / 87.48; released conditioned 92.07 / 87.02 / 90.20; Jeva-4B text candidates 79.99 / 62.25 / 66.23. No confidence intervals or repeated runs for accuracy (the paper notes checkpoints that never saw Mind2Web move by about +/-2 points). JevBench: Iris-4B with Jeva weights 100.0 original, 100.0 easy, 60.36 hard versus OpenJev-27B 98.61, 100.0, 76.58; ImaJev-Bench dev 70.13 versus MetaEncoder-30B 85.55. MMEB-V2 mean hit@1: first stage 74.9, Qwen3-VL-Reranker-8B 78.4, Iris retrieval-tuned 40.3, Iris zero-shot 24.4. (Tables 2 to 4)

## Cost and latency
A800-80GB, synchronous timing: independent Iris 208 ms at K=16 (cleared caches), 2.3 s at K=256, 23.9 s at K=2,048; state-conditioned 254 ms versus 737 ms for retrained OneJev at K=16 through its server; reuse speedup 3.6x (K=16), 37x (K=256), 191x (K=2,048), within 5% of the closed form except r=1 at large K. Patch-embedding Conv3d replaced by a matrix product: 5.2 s to 15 ms (350x). Stage 2 training 47 min on 4 GPUs; OneJev retraining 1.6 h on one GPU. (Sec. 3.6, 5.4, 5.10, App. A)

## Calibration
Null probability AUROC: independent 0.780 to 0.867, conditioned 0.919 to 0.947, with abstention stage 0.935 to 0.969; abstention rate on null steps 11 to 14%, 34 to 43%, 77 to 79%. Noul Brier 0.127 (stage 1) and 0.153 (mixture) on 2,000 held-out rows; no ECE, no recalibration. (Table 5, Table 6)

## Cascade or escalation
None (abstention via a coverage gate is a within-model feature).

## Robustness
Order invariance is structural (Proposition 1): flip rate exactly 0.00 over five candidate orders (original, reversed, three random) on all 6,396 records; ties between pixel-identical candidates are not counted as flips and the raw rate is in released summaries. Option-count scaling to K=2,048 (cost measured, not accuracy). Joint-encoding baselines flip 7.6 to 54.3%. Null detection limited by only 4 to 6% null steps. No language or option-name tests.

## Code and data
Code, benchmark construction scripts, deduplication and shuffling scripts, training configurations and evaluation outputs at https://github.com/lllfx/Iris. Jeva's curriculum data are not public.

## Authors' limitations (Sec. 7)
Images only (video as stills); vision tower frozen and not tuned; stage 1, label text on crops and pixel budget not ablated; null detection coarse on Mind2Web; Jeva-4B trained from its released checkpoint rather than from scratch, Jeva numbers not a controlled comparison. Also reported in text: independent encoding falls short of its own first-stage retriever on MMEB-V2.
