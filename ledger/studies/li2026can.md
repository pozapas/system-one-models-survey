# li2026can — Can Decision Models Understand Stance? Evaluating Jev Against General-Purpose LLMs

- arXiv: 2610.11901v1 [cs.CL], 8 Oct 2026; license arXiv.org perpetual non-exclusive (header). Full text: fulltext/2610.11901.html and .txt.
- Authors (header): Xing Li, Jinzhong Ning, Yijia Zhang (Dalian Maritime University); Liang Yang, Hongfei Lin (Dalian University of Technology). Affiliation type: academic.
- Code and data: no repository, no data statement, no limitations section found in the text. code_available = no.

## Task and data
Three-class stance detection (favor, against, neutral) toward a target, on two public benchmarks (Section 3.1, 4.1).
- VAST (Allaway and McKeown, 2020): English text-target pairs; all 3,006 official test records, seen-target and unseen-target subsets, repeated records retained; 759 target clusters (Section 4.1).
- ZS-CSD (Ding et al., 2025): Chinese conversational stance toward unseen targets; all 2,584 official test records (967 noun-phrase, 1,617 claim targets, Table 3); 45 target clusters; target strings disjoint across splits; original best model SITPCL reaches 43.81% macro-F1 (Section 4.1).
- Reference labels are the benchmark annotations ("Neutral follows the benchmark annotations", Section 3.1.1); the paper does not describe how the labels were produced. Coded human_single as a placeholder for "benchmark annotation, process not described".

## Decision model, exact version
Jev Choice interface, one record per request, no demonstrations, no confidence filtering: "We request jev-latest, returned as jev-1.13.0" (Section 4.2, 3.4). Collected 21 to 24 Sep 2026 with 16 concurrent requests and up to three retries (Section 4.3). Instruction plus a written criterion per label (Appendix A).

## Comparators and tuning parity
- DeepSeek V4.1 Flash (Responses API, schema-constrained) and Qwen3.8-Flash (Chat Completions, JSON), temperature 0, 32-token limit, thinking disabled, one record per request, shorter prose instruction (Section 4.2, Appendix A).
- GPT-5.6 via Codex CLI, reasoning effort none, up to 100 records per request; Claude Sonnet 5, thinking disabled, up to 25 records per request (Section 4.2). Batching differs from Jev (asymmetry disclosed). Neither GPT-5.6 nor Claude is shown a decision-model-style label criterion list; they get the prose instruction.
- Supervised references: Qwen2.5-3B-Instruct and 7B-Instruct, LoRA fine-tuned on each training split, lr 5e-5, five epochs, single run, no per-instance predictions (Section 4.2). Not paired-tested.
- Zero-shot prompted systems get identical test IDs and labels; failed final responses count as errors (Section 4.1).

## Main results (Table 1, full test sets)
- VAST accuracy / macro-F1: Jev 78.14 / 77.92; DeepSeek 74.82 / 73.99; Qwen3.8-Flash 74.52 / 73.79; GPT-5.6 78.51 / 78.08; Claude Sonnet 5 74.82 / 74.51; Qwen2.5-3B SFT 74.16 / 74.52; Qwen2.5-7B SFT 79.32 / 79.91.
- ZS-CSD accuracy / macro-F1: Jev 58.40 / 58.43; DeepSeek 58.28 / 56.89; Qwen 54.61 / 53.16; GPT-5.6 74.65 / 73.62; Claude 72.52 / 72.42; Qwen2.5-3B SFT 55.76 / 56.08; Qwen2.5-7B SFT 60.98 / 60.85.
- Paired target-bootstrap 95% intervals (5,000 resamples, seed 42, percentile, no multiplicity adjustment) are shown in Figure 1 only; the text says the Jev minus GPT-5.6 interval on VAST includes zero and the ZS-CSD gaps of 15.19 (GPT-5.6) and 13.99 (Claude) macro-F1 points are supported by the intervals (Section 5.1). Numeric interval bounds are not in the text.
- Table 2 per-class F1: ZS-CSD Jev against 56.66, favor 59.58, neutral 59.04; GPT-5.6 79.49, 82.70, 58.67. VAST Jev 77.13, 72.71, 83.92; GPT-5.6 78.25, 73.95, 82.05.
- Table 5 (ZS-CSD confusions): favor-against errors Jev 373, DeepSeek 275, Qwen 462, GPT-5.6 35, Claude 101.
- Table 3 (ZS-CSD macro-F1 by target type): noun phrase Jev 63.49, GPT-5.6 78.02; claim Jev 55.26, GPT-5.6 70.72. Table 4 by conversation length: the gap to GPT-5.6 falls from 22.69 points (2 turns) to 14.20 (6+ turns).

## Cost and latency
Table 1 records tokens and API cost for the whole test set: VAST Jev $0.0741 (1,763,143 input, 114,228 output tokens) vs GPT-5.6 $3.9010 vs Claude Sonnet 5 $4.7051 vs DeepSeek $0.2133 vs Qwen $0.1021; ZS-CSD Jev $0.0776 vs GPT-5.6 $3.9230 vs Claude $5.5582 vs DeepSeek $0.1829 vs Qwen $0.0948. Costs are computed from recorded tokens and vendor pricing dated 24 to 28 Sep 2026 (references). Pricing basis for Jev not described beyond that. No latency reported. GPT-5.6 and Claude cost is batch-based, so cost ratios are not strictly like for like.

## Calibration, cascade, robustness
No calibration analysis (probabilities explicitly unused, Section 3.4), no cascade, no option-name or language-swap test (languages differ by dataset: English VAST, Chinese ZS-CSD, so language and task are confounded).

## Test-set exposure
Both test sets are public before 2026 (VAST 2020, ZS-CSD 2025); no contamination check described.

## Limitations (paper)
No dedicated limitations section. The discussion notes that Jev's ZS-CSD gap may reflect difficulty with reply relationships and stance direction rather than conversation length (Section 5.4, Introduction). Single-turn group has only 45 samples (Section 5.4).
