# yu2026visual — Visual Jev: Accurate and Efficient Decisions from Shared Visual Context

- arXiv: 2609.25845v1 [cs.CV], submitted 22 Sep 2026. License CC BY-NC-ND 4.0.
- Authors: Guanxu Yu (Independent Research), Yuhang Yao (Carnegie Mellon University, alumni). Affiliation type: mixed (independent / academic).
- Source: fulltext/2609.25845.html / .txt (fetched via `https://arxiv.org/html/2609.25845v1`, 2026-09-24).
- **Important scope note:** "Visual Jev" here is an independently built vision decision system (Qwen3-VL-4B/8B-Instruct backbone + LoRA, answer-supervised post-training) named in the style of TypeSafe's Jev, not TypeSafe's own product. It belongs to the "open ones" category the brief lists (a typed/probabilistic decision system over VLM candidate tokens). Treat `model` values as "Visual Jev (Qwen3-VL-4B)" / "Visual Jev (Qwen3-VL-8B)" and `affiliation_type` = mixed, not vendor.

## Task and data
Many-questions-per-image forced-choice decisions on four benchmarks: GQA (object/attribute/relation Choice questions, training family), SNLI-VE (Claim, 3-way entailment, training family), TextVQA (Choice, held out), TallyQA (counting Choice, held out). Open answers converted to Choice-format candidate sets; image-level train/test isolation (§4, "Benchmarks").

## Decision models evaluated
- 4B original backbone (Qwen3-VL-4B-Instruct, LM-head readout, no post-training) — task_family baseline.
- 4B answer SFT (LoRA answer-supervised post-training, LM-head readout) — the recommended "Visual Jev" default config.
- 8B original backbone / 8B answer SFT — scale comparison, same recipe.
- 4B decision CE (typed Choice/Claim head instead of LM head; matched data/budget) — control.
- 4B decision CE + sufficiency (adds evidence-sufficiency head) — control, Appendix A.
- 4B decision CE, K ≤ 4 (typed head trained only on ≤4-option examples) — slot-coverage ablation.

## Comparators and tuning-budget parity
All systems share backbone, data, prompts, readout position (where applicable) and update budget (3,000 updates, batch size 8, LoRA r=16); "same backbone, examples, prompts, readout position and update budget as answer SFT" (§5.1) — fine-tuned/matched-budget parity, not zero-shot prompting comparison. This paper does not compare to TypeSafe's own Jev or to other vendor models — it is a systems ablation study of one open architecture.

## Reference labels
Benchmark gold labels (GQA/SNLI-VE/TextVQA/TallyQA original annotations), converted to Choice format by the authors; reference_label_type = human_adjudicated (original dataset human annotations) — not an LLM teacher or model consensus.

## n and sampling
Training: 30,416 GQA Choice items + 9,000 SNLI-VE Claim items, 3 seeds for principal systems. Table 3 efficiency/disagreement analysis uses 7,532 GQA execution-test questions. Table 12 paired-intervention corpus: 11,371 emitted pairs, 7,603 rejected attempts (Appendix B).

## Test-set exposure
Public benchmarks (GQA 2019, SNLI-VE 2019, TextVQA 2019, TallyQA 2019) — all public-pre-2026, so test_set_exposure = public-pre-2026 (possible backbone pretraining exposure, not addressed as a limitation directly, though image-level train/test isolation is enforced for the paper's own splits).

## Cost / latency and hardware
"Measurements use one RTX 5090 in bfloat16, five warm repetitions after two discarded warm-ups" (§4, "Evaluation and timing"). Table 3/13 give amortized ms/question at N=1..32 for 8 execution paths (independent, independent_batch, vision_cache[+batch], prefix_share[+batch], generate variants). hardware_or_provider = "1x NVIDIA RTX 5090 (32GB), PyTorch 2.14, CUDA 13.0, Transformers 5.17" (Appendix C).

## Calibration
Table 6 (Appendix A) reports temperature-scaled Accuracy, Macro-F1, NLL, Brier, AURC and Cov.@5%-risk for B1 (backbone) through M (full sufficiency variant); temperature is fitted on a held-out calibration split (30% hash of parent image id) — post_hoc_calibration = temperature. No binned ECE metric is reported; calibration_quantity recorded as "Brier / NLL (temperature-scaled, not ECE)".

## Cascade / escalation
None reported (not a routing/cascade paper).

## Robustness / stress tests
- Candidate-set / language-prior diagnostic (Table 1): grey-image (blind) baselines per benchmark vs chance vs sighted, e.g. GQA grey 0.585 vs chance 0.365 vs sighted 0.841 — shows the Choice conversion carries a language prior (flagged in Limitations).
- Slot-coverage ablation: a 16-slot typed head trained only on K≤4 examples scores 0.639 on held-out 8-option TextVQA vs 0.973/0.975 for the LM-head/normal decision-CE systems (§6, "Slot coverage is a constraint on typed heads").
- Mixed-precision numerical-drift analysis (Table 11): vision-cache-only path is bitwise identical to independent execution; batched/prefix-sharing paths introduce small logit/probability deviations (up to 0-20 of 7,532 argmax flips), traced to mixed-precision execution, not sample-wise divergence.
- Evidence-sufficiency negative result (Appendix A): a trained sufficiency head detects missing evidence well (0.969 AUROC intact-vs-degraded) but reduces macro decision accuracy from 0.761 to 0.748 and does not improve selective prediction (AURC 0.0356 for plain decision-CE vs 0.0456 with sufficiency head) — explicitly a negative/control result.

## Code and data availability
Project page and GitHub linked from the paper header ("Project: Website • GitHub"), exact URLs not printed as plain text in the fetched HTML (icon links). code_available recorded as "yes (project GitHub, URL not resolved in plain-text extraction)".

## Limitations (paper's own, from "Limitations" section)
- "The workload requires co-available questions" — the serving gain (5.7 ms/question at N=32) is an amortized throughput measure assuming several questions are known together; at N=1 sharing adds overhead (82.9 ms vs 48.1 ms), and independently arriving requests would incur queueing latency excluded from the benchmark.
- "One backbone family, two scales, one language" — only Qwen3-VL (4B/8B), English, ≤16 candidates, frozen vision tower; a second architecture family untested.
- "Task transfer and statistical scope are limited" — TextVQA/TallyQA held out and show little gain; results establish improvement on trained families only, not broad transfer; CIs are cluster bootstraps over parent images (test sampling only, not training randomness); fixed step budget, no exhaustive schedule/loss-weight sweep.
- "The Choice conversions carry a language prior" — grey-image (blind) accuracy well above chance on GQA (58.5% vs 36.5% chance) and near chance on SNLI-VE (33.4% vs 33.3%).
- "The appendix sufficiency study depends on imperfect annotations" — evidence regions from GQA scene graphs, not human-verified pixel rationales; small manual inspection found 1/6 triples had a granularity issue.

## Seed claims checked (see parts/seed_check_C.csv)
1. Macro accuracy 70.6% → 76.1% after answer-supervised post-training — confirmed: "Answer-supervised post-training raises equal-weight macro accuracy from 0.706 to 0.761" (Abstract; Table 2, 4B original 0.706 → 4B answer SFT 0.761 ± 0.002).
2. 8.9× and 3.4× speedups at N=32 — confirmed: "At N = 32 questions per image, shared batched execution is 8.9x faster in warm amortized time than independent serial execution and remains 3.4x faster than an already-batched baseline that recomputes the prefix" (Abstract; §5.2: 50.7ms→5.7ms = 8.9x vs fully-independent; 19.3ms→5.7ms = 3.4x vs already-batched no-reuse).
3. Typed-head control — confirmed: "A matched typed-head control offers no consistent accuracy advantage over the LM-head readout" (Abstract; §5.1: answer SFT 0.761±0.002 vs decision CE 0.761±0.001, overlapping seed ranges 0.758-0.764 vs 0.760-0.763).
