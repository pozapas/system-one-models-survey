# zhang2026anyjev

AnyJev Technical Report: Typed Decisions from One Prefill of Any Open LLM. arXiv 2610.00831v1 (cs.LG), 2026-09-30, "early report on work in development". Extractor: batch V05. Ledger rows L1932 to L1945.

## Authors and affiliation
Jiamu Zhang, Tianze Yang, Yucheng Shi, Evan Chen, Zixiang Nie, Kelly Wan, Liangjie Hong, Ninghao Liu, Liang Wu. Nokia Applied Research (Nokia, Sunnyvale CA), Tencent Hunyuan, The Hong Kong Polytechnic University (title block). Affiliation type: industry (mostly), with one academic co-affiliation. Own-system paper; hosted Jev is not evaluated.

## Task and data
A typed decision readout (probabilities over the supplied options from one prefill of a frozen instruction-tuned LLM, restricted to single-token option labels) with two training-free corrections: a label-prior division (batch calibration, alpha = 0.75 chosen on a separate sweep of 230 model/question pairs scored against gold labels) and log-space averaging over the K cyclic rotations of the option list (Sec. 3, 4). Evaluations: (1) 20-option sweep, 300 held-out items per cell, tasks banking20 (20 BANKING77 intents), newsgroups (20 Newsgroups classes) and a binary prompt-injection task; thirteen models run, eleven in the 20-option sweep (Sec. 6). (2) JevBench public subset, 231 items of which 213 are scored (18 skipped as ordinal or irregular), items have 2 to 6 options (3.6 on average) (Sec. 6, 7.2). (3) Full test split of the default BEV Decision Mix configuration: 24,386 rows expanded to 46,320 decisions (18,808 choices of 2 to 10 options, 17,572 yes/no, 9,940 ordinal scores) (Appendix E). (4) Serving test on an 18-option MASSIVE routing question, 300 decisions (Sec. 7.4). All public data; no contamination analysis.

## Decision models and versions
AnyJev applied to open instruction-tuned models at released weights in bfloat16: Qwen3 (1.7B, 4B, 8B, 32B, 30B-A3B), Qwen2.5-7B, Llama-3.2-3B, Mistral-7B-v0.3, Granite-3.3-8B, Phi-4-mini, SmolLM2-1.7B, OLMo-2-7B, gpt-oss-20b (low reasoning); Qwen3.5-9B and Qwen3-32B for the BEV evaluation (Sec. 6, 7.3). No revision hashes in the main text (the Chinese-Jev paper cites AnyJev repository revision 45add30). Software: PyTorch 2.5.1, CUDA 12.4, Transformers 4.55.4, vLLM 0.7.0, one H100 NVL (Sec. 6). Three rows on the injection task fail the answer-mass gate (m = 0.408, 0.710, 0.976) and are excluded (Sec. 3). The gpt-oss harmony template gave m = 0.000 and showed that high accuracy can come from a faulty prompt end (Sec. 3).

## Comparators and tuning-budget parity
Within AnyJev: raw readout, rotations only, rotations plus prior, plus temperature (same models and items). On BEV Decision Mix the published baseline interfaces are Bespoke-Nimble-9B (fine-tuned), Laya typed-decisions, Qwen3-Reranker-0.6B and NanoJev, taken from their released configurations (Appendix E, Table 14); the authors note that Nimble's 2.56-point lead over the 9B rotation average "is an observed system difference, not an isolated estimate of the effect of fine-tuning" (Sec. 7.3). Fitted quantities: alpha (against gold labels), temperature (100 to 500 labelled examples of the same question, five out-of-fold folds pooled over tiers), stopping threshold (unlabelled states) (Sec. 6). Nimble rows come from a different training regime (fine-tuned) than the frozen AnyJev models.

## Reference labels
Gold labels of the public datasets (BANKING77, 20 Newsgroups, MASSIVE, JevBench, BEV Decision Mix); BEV Decision Mix and JevBench label provenance is not described here.

## Sampling and intervals
300 items per cell with no intervals for the 20-option results ("those runs record aggregates rather than per-item outcomes"); the sign test over eleven models gives p = 4.9e-4 for 11 of 11 (Sec. 7.1, 9). JevBench: 95% bootstrap intervals over 2,000 resamples, paired over items (Figure 3, Table 7). BEV Decision Mix: Wilson intervals that treat decisions as independent and are descriptive (Table 14 notes). Intervals are over items, not over runs or seeds (Sec. 9).

## Headline results
Order-flip rate on reversing the option list falls from 0.328 to 0.138 (banking20) and 0.334 to 0.183 (newsgroups), accuracy rises on 11 of 11 models (by 7.2 and 5.9 points on the means) (Table 1). On the binary injection task rotations remove order dependence (0.180 to 0.000) without raising accuracy (3 of 7, p = 0.77) (Sec. 7.1). JevBench accuracy spans 0.549 (Qwen3-1.7B) to 0.798 (Qwen3-32B); debiasing changes pooled accuracy by +0.006 [-0.004, +0.018] (Sec. 7.2). BEV Decision Mix: AnyJev on Qwen3.5-9B 68.01% (rotations, prior off) versus 67.85% raw; Qwen3-32B 67.59% versus 67.03%; Nimble-9B 70.57%; Laya typed-decisions 56.20%; NanoJev 32.99%; the batch prior lowers accuracy to 65.01% and 65.55% (Sec. 7.3, Table 14).

## Calibration
ECE on 15 equal-mass bins (within shard, then mean over four shards for AnyJev and Nimble; one shard for other baselines; not pooled ECE) (Table 14 notes). Temperature scaling (one global temperature): banking20 ECE 0.251 to 0.088 (Table 1); JevBench temperature lowers ECE on seven of eight models, raises it on one (Granite-3.3-8B 0.270 to 0.301) (Sec. 7.2). No recalibration of the label-free steps.

## Cascade and escalation
No model cascade. An unlabelled-state stopping rule reduces rotations read: threshold 6.0 chosen on 600 unlabelled states reads 7.3 of 18 rotations and agrees with the full-rotation decision on 98.7% of held-out decisions, giving 2.22 times the decisions per second on vLLM (Table 3); with selection and verification on disjoint states, Qwen2.5-7B reaches a verified Clopper-Pearson bound 0.0079 at 10.61 of 18 and 9.01 of 20 rotations; two of four cells certified (Sec. 5, 7.4). The serving run selected and bounded on the same states, which the authors flag as not covering the selection (Sec. 9).

## Option-name, cardinality, language and robustness tests
Option-list reversal (order-flip rate) is the main robustness measure; cardinality 2 (injection) versus 20 (banking20, newsgroups); JevBench K = 2 to 6 with the trend of the effect on K tested (slope +0.0059 per option, interval [-0.0012, +0.0132]) (Sec. 7.2). Canonical option ordering described but not measured (Sec. 4.2). The option-set mask experiment collapsed accuracy to chance (0.042 versus 0.633 on 18-option routing) (Sec. 8). No language tests.

## Cost and latency
Throughput on one H100 for the 18-option routing question: vLLM 16.7 decisions/s with all 18 rotations versus 37.2 decisions/s with the budget at wave 2; Transformers 7.0 versus 16.5 decisions/s (Table 3). Packing the K rotations into one forward is 1.20 times faster than the shared-prefix path on a short state (Sec. 5, 8). No dollar costs or latency percentiles.

## Code and data availability
https://github.com/nokia-applied-research/AnyJev (title block); open source (abstract).

## Authors' stated limitations (Sec. 9)
One prefill cannot reason (hardest JevBench tier 0.343 to 0.590); JevBench has few options (3.6 on average) where the rotation average has least to remove; 18 items unscored; 20-option results have no intervals; intervals are over items not runs; the stopping threshold is selected and certified on the same sample in the serving run; efficiency and accuracy measurements use different tasks; hidden-state readouts need a local backend. The report is explicitly an early measurement, "not a settled ranking" (Status).
