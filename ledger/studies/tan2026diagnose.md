# Tan et al. 2026, Diagnose Before You Refine: Multi-Dimensional Judge Feedback for Query-Efficient Jailbreak Attacks

arXiv:2610.19971v1 [cs.CR], 14 Oct 2026, arXiv perpetual non-exclusive licence (fulltext/2610.19971.txt, header). Borderline inclusion: the measured quantity is attack success; Jev is used as an in-loop probabilistic judge and, in one experiment, as an output filter.

## Authors and affiliations

Yixin Tan and Rui Wen (Institute of Science Tokyo), Chia-Yi Hsu and Chia-Mu Yu (National Yang Ming Chiao Tung University), Jiayang Liu (Nanyang Technological University) (title block). Affiliation type: academic.

## Task and data

Jailbreak attack on safety-aligned LLMs. 100 harmful requests from AdvBench and 100 from MaliciousInstruct; five open-source targets (Qwen2.5-7B, Llama-3.1-8B, Baichuan2-7B, Gemma-2-9B, GLM-4-9B) on both datasets, three closed-source targets (Gemini-3.1-Flash-Lite, Claude-Haiku-5.5, GPT-4.1-mini) on AdvBench (Section 6.1). Success is judged by two evaluators independent of Jev: HarmBench classifier (binary) and the fine-tuned StrongREJECT evaluator (continuous), so reference labels are model-based (ledger label type llm_teacher) (Section 6.1, Appendix A.5). Public benchmarks pre-2026, no contamination issue relevant to Jev. Single run, seed 42; no intervals reported for ASR (Appendix A.1).

## Decision model

Jev, "Jev v0.3.1" per Appendix A.2 (this differs from the 1.13 numbering used elsewhere in the batch; recorded as written), four typed questions (stance over 7 categories, relevance, specificity, completeness) in one call. The jailbreak score is m = P(comply or mixed) times normalised specificity (Eqs. 2, 3). Attacker receives only a scalar score and condensed instruction, not raw probabilities (Appendix A.4). In defence experiments a Jev output filter blocks responses with m at least 0.5 (Section 6.5); the 0.5 threshold is not tuned or justified.

## Comparators and tuning parity

PAIR, TAP, AutoDAN-Turbo with Mixtral-8x7B-Instruct-v0.1 as attacker for all methods, B=10 first queries of longer trajectories (Section 6.1, Appendix A.5, B). Each baseline keeps its own in-loop judge (GPT-4o-mini for one, a Gemma-based evaluator for another; Appendix B). The baselines are not given Jev feedback, so the comparison confounds search method with judge. Llama-Guard-3-8B and GPT-2 perplexity filters are the defence comparators.

## Headline results

Open-source AdvBench average HarmBench ASR 84.4 (TAP 72.6, PAIR 58.8, AutoDAN-Turbo 59.6) and StrongREJECT 0.833 (Section 6.2); MaliciousInstruct 95.2 (TAP 87.0); closed-source average 54.3 (TAP 48.0), Claude-Haiku-5.5 19 vs TAP 15 (Table 3); abstract: 89.8% average across ten open-source settings. Defence on Qwen2.5-7B AdvBench (Table 5): JSB ASR 86 undefended, 47 with Llama-Guard input filter, 28 with Llama-Guard output filter, 1 with the Jev output filter; Jev filter leaves 1 to 4% for all attacks. There is no ground-truth precision/recall for the Jev filter and no benign-response false-positive test.

## Calibration, cascade, robustness, cost

No calibration analysis. Stopping-threshold analysis: tau_stop 0.5 to 0.9; raising 0.7 to 0.9 gives no ASR gain with query use rising to 22.3 (Section 6.4). Query budgets 5, 10, 20, 40 (Figure 2). No option-name or order test. Jev latency and cost not reported.

## Code and data availability

None stated.

## Paper's own limitations

Predefined strategy library; closed-source evaluation uses lightweight variants; lower success against resistant targets such as Claude-Haiku-5.5 (Limitations).
