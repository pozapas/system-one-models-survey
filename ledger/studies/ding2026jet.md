# Ding (2026), "JET: Justification Evaluation in Transformer"

## Identification
- arXiv 2609.33874, read as v2 ("arXiv:2609.33874v2 [cs.LG] 29 Sep 2026", header). First submission date per batch file: 2026-09-27. License CC BY-SA 4.0.
- Author: Shenghao Ding, "Affiliation: Yet Another AI" (byline). affiliation_type = industry (single-author company affiliation; no university).
- Code: https://github.com/yet-another-ai/jet (Appendix A). Raw per-run artifacts "are excluded from the repository" and "retained outside version control" (Appendix A, Section 7).

## What the paper is
- JET is an inference system, not a trained decision model: "JET uses pretrained language and vision-language models to select among a finite set of answers without requiring additional training" (Abstract). It scores each supplied candidate answer by conditional likelihood (teacher forcing, no sampling) and normalizes over candidates (Eq. 4, Section 3.2). Implemented on llama.cpp at pinned revision b29c606e28a0 (reference [6]). Borderline for the decision-model definition (candidate likelihoods, K candidate continuations rather than one forward pass with a declared-answer head), but the output is a typed probability distribution over declared options with no free text, so included. Jev 1.13 enters only as an external reference measured by the author (Table 4).
- Normalization is not claimed to be calibration: "Normalization alone does not establish probability calibration" (Section 3.2). No ECE, Brier or reliability analysis; gold NLL only (Section 6.2). "Future work should measure calibration" (Section 8).

## Task and data
- MMLU full test set, 14,042 questions, 57 subjects, zero-shot (Section 5.1, Appendix A). Reference labels: the benchmark answer key (coded human_adjudicated, following ledger precedent for MMLU). BoolQ is used only in a 541-request sampled workload (256 BoolQ validation + 5 MMLU per subject) for the prefix-reuse timing study (Appendix A).
- Public MMLU, released 2020, so exposure is public-pre-2026; no contamination check on the base models. The LoRA run excludes exact MMLU matches "although these checks cannot rule out paraphrases or pretraining contamination" (Section 6.1).

## Systems evaluated
- JET with Qwen3.5-0.8B, 2B, 4B, 9B (Q8_0), Qwen3.5-27B and Qwen3.6-35B-A3B (Q4_K_M), on an Intel Arc A770 16 GiB (Vulkan; i9-13900K, 64 GiB RAM) and an RTX 4090 (Vulkan and CUDA) (Table 1, Table 3, Appendix A). Model revisions are not given as hashes in the text (only names and quantization).
- Jev 1.13 (hosted API): "The author's manual evaluation of Jev 1.13 yields 89.06%, with a separately reported API throughput of 2.86 requests/s" (Section 5.5). Run date for the Jev measurement not stated separately (primary experiments September 21-29, 2026, Appendix A). Jev's concurrency and timing boundaries are undocumented (Appendix A). Jev interface is "sampler-free and exposes no configurable reasoning or few-shot settings" (Section 5.5).
- Published larger-model MMLU numbers (Llama 3.1 70B 83.6, 405B 87.3, Qwen2.5-72B 85.3, DeepSeek-V3 88.5) are copied from model cards under different protocols and are not ledger rows (Table 4 caption).
- LoRA: Qwen3.5-4B, rank 16, one epoch, 22,791 training records (BoolQ, ARC-Easy, ARC-Challenge, SNLI), evaluated 74.39 vs 66.46 baseline (Section 6.2). Baseline GGUF is from a separate conversion repository, so gain "cannot be attributed entirely to LoRA" (Section 6.3).

## Tuning-budget parity
- JET configurations all use the same zero-shot prompt; the Jev comparison is explicitly not matched: "differences in evaluation and timing protocols do not establish parity with Jev" (Section 1); "Shared benchmark coverage does not ensure identical prompting, answer scoring, or aggregation" (Section 5.5). The JET prompt/scoring protocol was refined over "early prompt baselines, intermediate optimization variants" which are omitted from Figure 2 (Section 5.5), so some development on MMLU is possible; not quantified.

## Sampling and intervals
- Full-set, single run per model and backend: "One run per model, with no repeat-run variance estimate" (Tables 1 and 3 captions). No confidence intervals. Counts reconcile (e.g. 11,948/14,042 = 85.09%).
- Backend sensitivity: 328 top-1 choices differ between CUDA and Vulkan on Qwen3.6-35B-A3B (Section 5.5); 16, 12 and 14 changes on a 570-question subset (Appendix A.1).

## Cost and latency
- Throughput is requests per complete-process wall time including model loading and shutdown, not a latency percentile (Section 5.1). RTX 4090 Vulkan: Qwen3.5-27B 2.21 req/s, Qwen3.6-35B-A3B 4.17 req/s (Table 3). Jev API 2.86 req/s (Section 5.5), not comparable. Prefix reuse speedups 2.23x and 2.18x on 541 requests with identical responses (Table 2). No dollar costs.

## Cascade, option-name, cardinality, robustness
- No cascade. Candidate likelihoods "are sensitive to answer wording, length, and answer priors" (Section 7) but no option-name perturbation test is reported. Cardinality: 4-way MMLU choices only.

## Authors' stated limitations
- One run per model; no variance (Section 7). Prefix study bundles prefix reuse and cache reset (Section 5.4). Jev comparison uncontrolled (Section 7). Calibration, latency distributions and multimodal accuracy unmeasured (Sections 4.3, 7, 8). Raw artifacts not in version control (Section 7). AI-assisted writing disclosed (Statements).
