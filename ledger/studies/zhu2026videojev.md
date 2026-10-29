# zhu2026videojev — VideoJev: System One Model for Video Understanding and Interaction

- arXiv: 2610.18615v1 [cs.CV], 13 Oct 2026 (CC BY 4.0). Full text: fulltext/2610.18615.html and .txt (fetched 2026-10-28).
- Authors: Yuhan Zhu, Xiangyu Zeng, Qingyi Si, Chenxu Yang, Yifei Li, Luozheng Qin, Junhao Zhou, Dingyu Yao, Jun Zhang, Chuanyu Qin, Zhiqiu Zhang, Yuandong Yang, Yuqi Xu, Tianyu Zhang, Hongcheng Guo, Jiaqi Wang, Nan Duan, Limin Wang. Affiliation keys on the title page: NJU, JD.com, UCAS, THU, XMU, SJTU, USTC, FDU (per-author mapping lost in extraction). Affiliation type: mixed (universities plus JD.com).
- Code and weights: no link found in the text.

## Task and data
Own-model paper: VideoJev replaces autoregressive decoding of an MLLM with a candidate-scoring head (512-d projections, scale 10, two tokens <|option_end|> and <|decide|>), scoring temporal intervals (sigmoid, Kadane decoding at tau 0.25) and textual options (softmax) (Section 2). Cached inference (video prefix prefilled once) and Joint inference (several queries in one forward pass). Evaluated on three temporal grounding benchmarks (Charades-STA, ActivityNet Captions, QVHighlights, TimeLens-Bench refined annotations; R1@0.3/0.5/0.7 and mIoU) and four multiple-choice Video QA benchmarks (LVBench test 1,549, Video-MME test 2,700, LongVideoBench val 1,337, MLVU dev 2,174 questions; frames only, no subtitles) (Section 3.1).

## Decision models and versions
VideoJev-4B (dense, Qwen3.5-4B backbone) and VideoJev-35B-A3B (MoE, Qwen3.6-35B-A3B backbone). Baselines in Tables 1 and 2: GPT-5, Gemini-2.5-Pro (grounding); GPT-5.2, Gemini-3-Pro, Claude-Opus-4.5, Seed2.0-Pro (QA, published numbers); open 4B group (Molmo2-4B, Qwen3-VL-4B, Mage-VL, Qwen3.5-4B, VideoChat3-4B, Video-ORA-4B, TimeLens2-4B) and 30-35B-A3B group (Nemotron-3-Nano-Omni, Qwen3-VL-30B-A3B, Qwen3.5-35B-A3B, Qwen3.6-35B-A3B), Instruct and Thinking modes. No run dates stated.

## Comparators and tuning-budget parity
The paper trains VideoJev (two-stage, 160 and 375 updates; 64 H200 GPUs) on TimeLens-100K, TimeLens2-93K and an internally curated corpus of about 240K MCQs over 19K videos; baselines are used as released (comparator_tuning_budget not reported in the ledger; VideoJev is trained, baselines are not), except one controlled comparison: Qwen3.5-4B fine-tuned autoregressively on exactly the same post-training data (single stage, Table 3), which scores 1.3 mIoU points and 1.9 QA points lower. Generative baselines in timing share video prefill. Decoding threshold tau 0.25 fixed across all experiments (no tuning on test reported). Proprietary QA numbers are quoted from other sources (Table 2).

## Reference labels
Benchmark-provided annotations (annotation process not described in this paper): TimeLens-Bench refined timestamps; human-written MCQ keys for QA. Ledger label type human_adjudicated (benchmark answer keys, matching ledger.csv convention).

## n, sampling, intervals
Point estimates for all tables; no bootstrap or seeds. 95% confidence intervals appear only in the multi-query efficiency figure (Figure 3: 40 sampled videos per task).

## Test-set exposure
The four QA benchmarks are public pre-2026 (Video-MME, LVBench, LongVideoBench, MLVU); the grounding rows use TimeLens-Bench refined annotations (CVPR 2026) over older videos, so ledger test_set_exposure is unclear for grounding rows. Training data (TimeLens) comes from the same lineage as the grounding benchmarks; no contamination analysis reported.

## Cost and latency
Model forward time only on single H200, batch size 1: grounding on full Charades test (1,313 videos, 3,363 queries): VideoJev-4B 0.276 s vs Qwen3.5-4B 0.763 s (2.8x), 35B-A3B 0.336 s vs 1.054 s (3.1x). QA on full LVBench (103 videos, 1,549 questions): VideoJev-4B 1.123 s, Qwen3.5-4B Thinking 144.929 s (129x); 35B-A3B 1.493 s vs 149.777 s (100x). Joint inference adds 55 ms (grounding) and 31 ms (QA) from one to ten queries (Section 3.5).

## Calibration and cascade
Equal-width ten-bin ECE, four-benchmark mean: 8.65 points (4B) and 8.13 (35B-A3B); "VideoJev receives no calibration-specific training"; temperature scaling proposed, not run (Section 3.5). On LVBench the 35B-A3B reaches 95.8% accuracy on 591 predictions with confidence at least 99%, against 73.4% overall; no escalation experiment.

## Robustness tests
Joint vs Cached inference (Joint better by 0.8/0.5 points at 4B), joint vs single-task training, Soft IoU, final MLP, two-stage vs single-stage ablations (Tables 4 to 8). Option-position bias addressed by training-time permutation; no option-name or language robustness test.

## Limitations (paper's own)
Future Work section: closed-set decisions only; extension to open-ended agent workflows and streaming; probabilities overestimate correctness. No separate limitations section.
