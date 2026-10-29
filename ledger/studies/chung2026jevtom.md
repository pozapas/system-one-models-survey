# chung2026jevtom — Jev-ToM: Evaluating Theory of Mind in Typed Decision Models

- arXiv: 2610.18610v1 [cs.CL], 13 Oct 2026 (CC BY 4.0). Full text: fulltext/2610.18610.html and .txt (fetched 2026-10-28).
- Authors: Kawai Chung, Chunkit Chan, Yuxuan Liu, Yauwai Yim, Xi Yang, Wenbin Hu, Huihao Jing, Chiu Yeung Tang, Changxuan Fan, Ki Sen Hung, Tsun On Kwok, Haoran Li (Department of Computer Science and Engineering, The Hong Kong University of Science and Technology). Affiliation type: academic. A "Code" link appears on the title page but its URL is not in the extracted text.
- Code and data: versioned package planned (Ethical Considerations, Appendix I); anonymous review archive prepared; complete per-question release "remains planned".

## Task and data
Bounded Theory of Mind (ToM) answer selection with fixed candidates: 11,117 English text questions (11,167 minus 50 BigToM items whose stories omit the event needed by the reference) from nine benchmarks, 2,268 question families, 2/3/4/15 options (Table 1, Section 3.2): BigToM 1,200, OpenToM 2,533, ToMBench 730, SimpleToM 891, FANToM 1,805, ToMATO 1,396, CogToM 2,154, Hi-ToM 154, ToMi 254. Six capability groups (knowledge access, beliefs, goals/desires/intentions, emotions, social pragmatics, mental-state application) adapted from ATOMS. Strict scoring: invalid output counts wrong; overall EM is the benchmark-equal mean (Eq. 1-3). Interventions: supplied reasons (Section 4.3), candidate expansion, mental-state feedback (4.4), cost-time (4.5).

## Decision models and versions
Five typed models: TypeSafe Jev-1.13 (typesafe/jev-1.13, via OpenRouter; Table 7), Open-Jev-2B, Valen-Preview-0923, Tiny-Jev, OpenJev-0.6B. Seven generative baselines: SmolLM3-3B, Llama-3.1-8B-Instruct, GPT-4.1-nano, GPT-4o-mini, GPT-3.5-Turbo-1106, GPT-5.6-Luna, DeepSeek-V4-Flash-0731 (Section 3.4). OpenRouter tariffs frozen on 1 October 2026; no per-run dates for the evaluation calls given in the main text. Hardware not recorded for hosted routes ("hardware NR", Table 18).

## Comparators and tuning-budget parity
Same contexts, questions and candidate order for all; typed models get state plus instructions, generative models get the same content and return a label; temperature 0 and 32 output tokens for direct generative calls (Appendix G); "without task-specific fine-tuning" (Table 7). Luna runs at low effort in new tool-disabled sessions without the hard cap (Appendix G). Different concurrency and retry settings across deployments (Section 4.5).

## Reference labels
Original benchmark answer keys; native control questions included in overall (920 controls). Mixed templated and human-written sources. For ToMBench "all 730 question targets underwent an agent-assisted post-evaluation review ... not independent human validation" (3.2). Reason interventions use GPT-6.1-Sol-generated reasons, reviewed by three postgraduate annotators (Appendix E.3). Ledger label type: human_adjudicated (benchmark answer keys, the convention used for MMLU and BFCL in ledger.csv), although BigToM, ToMi and Hi-ToM are templated.

## n, sampling, intervals
Family-level bootstrap within benchmark (5,000 draws for primary, material and feedback; 2,000 six-condition; 10,000 matched candidates), 95% percentile intervals, no multiple-comparison adjustment (Appendix B.5). The main Table 2 reports point estimates only; intervals are in the reproduction materials.

## Test-set exposure
Public benchmarks released 2019 to 2026 (SimpleToM and CogToM are 2026), so ledger test_set_exposure is unclear for aggregate rows and public-pre-2026 only for OpenToM; "Possible training exposure to the public benchmarks also cannot be excluded" (Limitations). Some sources are fixed development subsets.

## Cost and latency
OpenRouter reference tariffs (not actual bills): Jev US$0.0295 per 1,000 questions; 32.7% below GPT-4.1-nano and 56.3% below GPT-4o-mini; DeepSeek US$0.0138 (Section 4.5). Jev separate serial timing pass: 73.03% EM, 282.31 ms mean (Table 18), 83.9% below nano and 82.3% below mini. Open-Jev-2B 464 ms on a local M4 Pro 48 GiB.

## Calibration and cascade
No ECE or Brier. Confidence-based selection at descriptive probability cutoff 0.90: coverage and retained error per benchmark (Figure 3, Table 11): SimpleToM 34.9% and OpenToM 29.0% retained error, ToMATO 1.8%; seven benchmarks below 10%. Risk-coverage curves in Appendix D. "The descriptive cutoff therefore needs task-specific validation".

## Robustness tests
Supplied reasons: aligned reasons raise earlier-correct accuracy 96.4% to 99.0%, swapped reasons drop it to 25.3% (4.3). Candidate expansion from 8 to 16 pairs lowers Jev strict accuracy 81.0% to 76.4% (Figure 7). Mental-state feedback: Jev 78.50 to 93.00 on 400 questions, most of the gain from question cues (Table 3). Option cardinality 2 to 15 is part of the benchmark. English only.

## Limitations (paper's own)
English text only; capability groups not exhaustive; training exposure possible; component-level evaluation, not an assistant; confidence and reason analyses exploratory; unequal source coverage across capabilities (Figure 1).
