# huang2026consider: Consider, Then Choose, Order-Invariant Decisions in System One Models

arXiv:2610.18233v1 [cs.AI], 13 Oct 2026 (CC BY 4.0). Full text: `fulltext/2610.18233.html` and `.txt`. Extractor batch V12. Key `huang2026consider` is distinct from the existing `huang2026can` and from `huang2026skillscreen`.

## Authors and affiliations

Jianguo Huang (equal contribution), Yao Long Teng (equal contribution), Yanchen Deng (corresponding), Bo An, Nanyang Technological University, Singapore. Affiliation type: academic.

## Task and data

Own-method paper. "Runoff" is a training-free decision rule for choice questions that makes the answer independent of option order: it scores each option alone (pointwise decisions, order-blind), keeps a consideration set of leading options (probability mass alpha = 0.99, minimum size k_min = 3), then compares the candidates in every cyclic shift of their pointwise ranking and averages (two forward passes) (Sec. 1, 4, 5.1). The baselines are Listwise (one listwise decision in the given order) and cyclic averaging as implemented by AnyJev (Zhang et al. 2026).

Evaluation: choice questions from five benchmarks (Sec. 5.1): Banking20 and Newsgroups (20 options, 300 questions each), MMLU-Pro (10 options; 1,400 questions), Typed Decisions (LocalLLaMA, 600 questions, 4 to 5 options) and the public items of JevBench (139 questions, 3 to 6 options). Metrics: accuracy with options in original order (Acc) and flip rate under one shuffle per question (Flip). Extra analyses: number of options K = 2 to 20 on Banking20 and Newsgroups (Table 7); OSWorld computer-use agent on 316 tasks (Sec. 6).

## Decision models evaluated and versions

Ten models (Sec. 5.1): open LLMs read out as decision models, Qwen3-8B and Gemma 4 12B (Hugging Face google/gemma-4-12B-it, revision 707f0a3, accessed 2026-10-05); closed System One models Jev 1.13, Mercury Decide, GPT-6 Luna (APIs, "Jev 1.13" with minor version only and no build string); open fine-tuned System One models Torchcast 12B, Kev 9B (Kev repository commit 0fe8fc9 cited), Intern-Decision 4B, Tev1 4B, Laya. Jev documentation page last reviewed 2026-10-02 and accessed 2026-10-04 (reference list); Typed Decisions dataset revision f7a2487; JevBench public split accessed 2026-10-05. Run dates for the API calls are not stated.

## Comparators and tuning-budget parity

Every model is evaluated with its own native choice answer, with AnyJev cyclic averaging wrapped around it and with Runoff wrapped around it, with the same prompt templates (App. A) and same hyperparameters (alpha 0.99, k_min 3; chosen from a sensitivity study on Qwen3-8B over the five test datasets, so mildly tuned on the test sets, Table 6). Closed APIs are black boxes. Parity is good for the method comparison; there is no cross-model tuning.

## Reference labels

Benchmark gold labels: Banking and Newsgroups class labels, MMLU-Pro answer keys, Typed Decisions and JevBench public reference answers (provenance of the last two not described in this paper).

## n, sampling, intervals

n = 300 + 300 + 1,400 + 600 + 139 = 2,739 choice questions per model; one shuffle per question for flip rate; Table 7 uses 300 questions per model, dataset and K. No confidence intervals, no repeated shuffles and no statistical tests are reported; results are single point values (Table 2). Accuracy differences of about one point between Runoff and AnyJev are therefore not interpretable from the paper.

## Test-set exposure

All benchmarks public and pre-2026 (Banking, Newsgroups, MMLU-Pro) or 2026 public items (Typed Decisions, JevBench public split); no contamination check discussed.

## Cost and latency

Table 4 (open models, ms per record): Qwen3-8B AnyJev 165 to Runoff 80 on average (2.1x faster), Gemma 4 12B 280 to 134 (2.1x); with 20 options Banking20 Qwen3-8B 308 to 77 ms (4.0x); with 3 to 6 options Runoff is slightly slower (JevBench 67 to 77 ms). Runoff remains slower than a single Listwise decision. Cost model: Runoff reads K + m^2 option slots versus K^2 for cyclic averaging (Sec. 4). Hardware and provider for latency are not stated in the text read.

## Calibration

Not analysed. Probabilities are used only to form the consideration set (mass alpha).

## Cascade or escalation

Runoff is a two-stage consider-then-choose procedure; the consideration set contains the gold answer 90% of the time at k_min = 3 versus 77% at k_min = 1 and 83% at k_min = 2 (Sec. 6, Table 6). OSWorld agent: Runoff solves 27 versus 21 tasks natively with Qwen3.5-35B-A3B and 14 versus 9 with Qwen3.5-9B on 316 tasks (Figure 4, Sec. 6).

## Option-name, cardinality, order, robustness

The central topic is option-order robustness. Table 7 (K = 2 to 20, mean of Qwen3-8B and Gemma 4 12B on Banking20 and Newsgroups): at K = 20 Listwise flips 14.4%, AnyJev 8.0%, Runoff 0.0%; Runoff accuracy within 1.3 points of AnyJev. Listwise flip rate 5% at two options and 17% at 20 for Qwen3-8B (Sec. 1, Figure 1). Remaining Runoff flips on black-box APIs (Jev 1.13 0.9%, Mercury Decide 1.4%) come from the API returning different probabilities for identical requests (Sec. 5.2, Proposition 1). Option-name preferences are not addressed (Limitations).

## Code and data availability

No release statement or code repository for Runoff found in the text; third-party repositories are cited. Coded no.

## Authors' stated limitations

Invariance assumes the model answers identical requests identically (closed APIs leave a few flips); Runoff addresses only option order, not other biases such as preference for certain option names; on reasoning questions the consideration set more often misses the correct answer and Runoff trails cyclic averaging by a few points (Sec. 1, 5.2, Limitations).
