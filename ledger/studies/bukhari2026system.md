# bukhari2026system — System X: An LLM Decision Model That Replies from Its Own KV Cache

arXiv:2610.25456v1 [cs.AI], 18 Oct 2026. Full text: fulltext/2610.25456.html and .txt (arXiv HTML). Code https://github.com/Turinglogicuk/system-x; adapter https://huggingface.co/TuringLogic/system-x (title block, Sec 11).

## Authors and affiliation
Syed Usama Khalid Bukhari (Turing Logic LTD), Syed Safwan Khalid (affiliation blank), Muhammad Aamir (University of Oxford) (title block). Affiliation type: mixed (company plus university). Not affiliated with TypeSafe AI (Acknowledgements).

## Task and data
Own model. System X adds a REPLY_WITH_TEXT option to the LLM-as-Jev readout (Li and Wagle [24]): option scores come from batched suffix scoring on copies of one prompt KV cache; when the reply option wins or top probability is below tau, the same model continues from the cache and writes 1 to 2 sentences (Sec 1, 3.1 to 3.3). Evaluation sets: JevBench public 231 items; Banking77 test 3,080 rows with 77 options; held-out Bitext reply task 300 rows; hand-written 97 cases written by the authors; for System X+ also ABCD next step (300), Bitext verticals (300), CFPB complaints (199) (Sec 4, 6.1). Also reply-quality checks, ABCD utterance ranking (500 turns) and lm-evaluation-harness tasks (Sec 7, 8).

## Decision models evaluated
System X = Qwen3-0.6B plus LoRA (r=16, 10.1M trainable parameters), trained one epoch on 9,000 Reason-9k decision rows plus 3,000 Bitext reply rows, single run, seed 20260922 (Sec 4; repo version v2). System X+ (v3) adds ABCD, Bitext verticals and CFPB rows (23,496 rows) (Sec 6). System X v4 = Qwen3-1.7B plus LoRA with 24,256 rows and teacher-rewritten reply targets (Qwen3-14B via Ollama, Q4_K_M), plus System X v4-0.6B control (Sec 9). Hosted Jev is not evaluated; published LLM-as-Jev numbers are quoted as context ("Paper" columns, Table 1).

## Comparators and tuning-budget parity
The comparator is each system's own untrained base LLM under the same prompt (Table 1, 9); the "Paper" columns are from a different training condition (full fine-tuning, different seeds and hardware) and are explicitly not a controlled ablation (Table 1 caption, Sec 2). A matched decision-only LoRA run is missing (Sec 10). Reply quality comparisons differ in prompts, generation limits and fine-tuning (Sec 7.3). Hand-written set was consulted repeatedly while developing v3 and v4 recipes (Sec 10), so it is not an independent test.

## Reference labels
JevBench public gold labels (benchmark); Bitext hybrid synthetic dataset mapped intents to actions (synthetic); ABCD agent next actions from crowdworker dialogues; CFPB complaint categories mapped by the authors' keyword rules; hand-written set labelled by the authors (human_single). LLM judges (Gemma 4 31B via Ollama, serving revision not pinned; Claude Opus 5.5 blind subset) grade replies; no human evaluation (Sec 7.3, 10).

## n, design, intervals
Single seed per configuration; exact two-sided sign/McNemar tests on discordant items, no multiplicity correction, no confidence intervals on accuracies (Sec 4, 10). JevBench has 231 items, limited power (Sec 5.1, 10).

## Test-data exposure
JevBench (2026 public benchmark), Banking77 (2020), ABCD (2021), CFPB, Bitext (public synthetic). Held-out sets are removed from training by message-level split; base-model pretraining overlap not assessed (Table 4 caption). Cross-benchmark n-gram decontamination of LLM-as-Jev not reproduced (Sec 10).

## Cost and latency
Latency on Apple M4 Pro, bf16, median of 5 runs: System X with cache reuse vs two-call pipeline, saving 15% at 367 prompt tokens to 37% at 4,161 (Table 3); at 1.7B saving 17% to 39% (Sec 9.3). Training time 90 min on M4 Pro (0.6B), 32 min System X+ and 57 min v4 on one RTX 5090 (Sec 4, 6.1, 9.1). No monetary cost reported.

## Calibration
ECE with 15 equal-width bins and Brier summed over classes, measured on the distribution before fallback (Sec 2). Brier loss term trained in. No post-hoc recalibration. System X: JevBench ECE 0.292 to 0.169; v4: 0.404 to 0.123 (Table 1, 9).

## Cascade or escalation
Low-confidence fallback to generation at tau 0.5 (default 0.65) used for communication, not as a correctness check; it lowered hand-written accuracy from 78.4% to 76.3% because errors were confident (Sec 5.2).

## Option-name, cardinality, robustness tests
Hand-written set uses option names and descriptions different from training; REPLY_WITH_TEXT description differs from the training one (Sec 3.2, 4). Banking77 77-option test. No explicit option-order permutation test; no language test. Unfamiliar actions attract the reply option with high confidence (Sec 5.4).

## Code and data availability
Code, scripts, lockfile public; v4 LoRA adapter on Hugging Face under proposed CC BY-NC 4.0, subject to training-data licence review; base models not redistributed (Sec 11, App. C).

## Authors' limitations (Sec 10)
Two sizes, LoRA only, one seed; confounded changes in v4; small hand-written set consulted repeatedly; synthetic reply data; LLM judges agree only moderately (kappa 0.44 to 0.51); no human evaluation; no matched decision-only ablation; not compared with a reranker baseline.
