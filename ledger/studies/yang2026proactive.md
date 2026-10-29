# yang2026proactive

arXiv 2610.16967v1 (cs.CV), 12 Oct 2026. "Proactive Physical AI through Continuous Observation and Timely Intervention."
Authors: Zhenhua Yang, Jiafeng Liang, Xingyu Zhou, Yi Jiang, Xiayu Cao, Zui Chen, Luqi Wang, Haiyang Sun, Yufei Xiang, Chang Li, Rongchuan Mu, Bowen Chi, Zihe Tong, Mingyu Li, Huijie Ma, Yiqiao Yang, Baoqi Ren, Zhiming Ma, Zhihao Zhu, Jiahao Ji, Zhuoyao Wang, Qianyu Wang, Xiangyu Liu. The HTML text exposes no affiliation lines; affiliation type not stated in the extracted text, recorded as unclear (likely mixed or industry; do not rely on it). (title block)

## EXCLUDED from the ledger (no rows written)
Reason: not a typed probabilistic decision model. StreamingJev is a fine-tuned Qwen3.5-4B that generates one of two tokens under prefix-constrained decoding, with no caller-declared option list and no probabilities reported. Notes below are kept for the record only.

## Why borderline
The paper builds "a Jev-style proactive timing model (dubbed StreamingJev)": Qwen3.5-4B post-trained to emit one of two tokens, <silence> or <response>, per observation, with prefix-constrained decoding that stops once all legal continuations imply the same decision. The text never reports probabilities, logits, thresholds on a score or calibration, and never names TypeSafe Jev; "Jev-style" refers to a restricted finite decision output. It is a binary decision interface evaluated inside a streaming video agent, not a probability-returning typed decision model as defined. Decision after review: excluded, no ledger rows. (Sec. 3.1, 3.2, Fig. 3)

## Task and data
- Proactive timing: decide when a streaming assistant should intervene. Evaluation on Omni-MMI PA/PT and paired ProactiveVideoQA-derived EGO and WEB episodes under Explicit (objective given) and Role (standing responsibilities, no target event) settings; reference annotations hidden at inference; responses matched one-to-one to reference windows. Also OVO-Bench and StreamingBench PO for public-benchmark timing (Table B.1: OVO SSR 629, CRR 240, StreamingBench PO 250 scoring units). Headline row counts for Table 1 not given in the main text. (Sec. 4.1, Table B.1)
- Training: 224,268 causal decision sequences (2,058,267 supervised decision turns) from 20,258 Internet source videos, labels built by an automated pipeline with offline annotators using full videos. (Sec. 3.1)
- Reference labels: benchmark reference annotations of response windows (human-made); training labels pipeline-generated.
- Test benchmarks public (Omni-MMI, ProactiveVideoQA 2025) and possible overlap of Internet training videos with test sources is not discussed in the extracted text.

## Models and comparators
- StreamingJev: post-trained from Qwen3.5-4B for three epochs (language model and output head updated, visual encoder and merger frozen). Run with a shared Qwen3.8-27B Worker for responses. Version identifiers: none beyond the base-model name. (Sec. 3.1, Table G.2)
- Matched comparator: Qwen3.5-4B Base timing model plus the same Worker and same input and scheduling budgets (this pair is the controlled comparison). Other systems keep their own interfaces and schedules: Qwen3.5-4B, Qwen3-VL-8B-Instruct, MiniCPM-V-4.6, GPT-6, Gemini, Claude, LiveStar-8B, Dispider. The authors' model is trained on the task while most baselines are zero-shot prompts, so tuning-budget parity is not equal. (Sec. 4.1, Table 1)

## Results (Table 1)
Explicit F1 42.43 (Qwen3.5-4B Base + Worker 30.49; strongest baseline Claude 36.16, margin 6.27 points); Explicit FP/min 0.04 (Base + Worker 0.70). Omni-MMI PA 57.00 and PT 87.00 (Base + Worker 35.50 and 53.00). Role F1 33.45 (LiveStar-8B 31.98, Base + Worker 28.72), Role FP/min 0.18. No intervals or seeds in the main-text table. (Table 1, Sec. 4.1)

## Cost and latency
Cumulative inference optimizations on 398 causal sequences with 3,768 timing decisions, single NVIDIA A800 80 GB, BF16, 1 Hz sampling: P50 latency 346.84 ms (full recompute) -> 240.26 (+cache) -> 214.16 (+dynamic token dropping, tau 0.9) -> 147.05 ms (+prefix-constrained decoding); P95 512.63 -> 251.77 ms; peak memory 9.85 -> 9.50 GB; decision agreement with full recomputation 98.65%. (Table 4)

## Calibration
None reported.

## Cascade or escalation
None for the timing model; the Response Model is triggered by the timing decision (event-driven, not a confidence cascade).

## Robustness
DTD threshold sensitivity (Table F.1); real-robot evaluation on Reachy Mini (20 cases per category); no option-name, cardinality or language tests.

## Code and data
No code or data URL found in the extracted text.

## Authors' limitations
No dedicated limitations paragraph found in the extracted text.
