# su2026jevspawn

JevSpawn: Adaptive Agentic Inference through Compositional Action Spaces. arXiv 2610.00437v1 (cs.AI), 2026-09-30. Extractor: batch V05. Ledger rows L1922 to L1931.

## Scope note
JevSpawn is a "Jev-style" finite probabilistic policy built on a pretrained open LLM (Qwen3.8-27B) with no additional training; it scores declared finite field values with parallel causal evaluation of the LLM's token probabilities (Sec. 3.1, 3.3). It is a borderline case for a typed probabilistic decision model. The measured quantity that clearly concerns a hosted typed decision model is the "TypeSafe Jev variant", in which hosted Jev (`jev-1.13.0`) replaces the finite scoring inside the same architecture while Qwen still writes declarations and text (Appendix B.4). The ledger therefore carries the Jev-variant rows plus a few JevSpawn headline rows for context.

## Authors and affiliation
Haoyang Su, Weiran Huang. Fudan University, Shanghai Jiao Tong University, Shanghai Innovation Institute (title block). Affiliation type: academic.

## Task and data
Eight tasks from five agent benchmarks: PPNL path planning from natural language (public test collections), Maze (LMRL Gym, fixed initial states), Grid (LLF Bench), LightsOut, RushHour, Sokoban (TextArena), 2048 and Nullify (KORGym); environment seeds 42 to 141 for the TextArena, LLF and KORGym tasks (Sec. 4.1). Up to 36 exploration rounds plus a submission step within a 300 s limit, context 16,384 tokens, 2,048 generation tokens, temperature zero, thinking disabled, seed 42, batch size 8 (Sec. 4.1). Ablations compare against separate full-method runs on the same 1,761 instances; long-horizon series use a 131,072-token context (Sec. 4.1). All benchmarks predate 2026; no contamination check is reported (not found in the text). Maze instance count is not stated in the main text.

## Decision models and versions
JevSpawn: Qwen3.8-27B fixed parameters; one parent selected and up to four distinct actions spawned per expansion (Sec. 4.1). TypeSafe Jev variant: API model `jev-1.13.0` for finite scoring, Qwen for declarations and text generation; both scorers receive the same task context and history under the common input limit; E2E latency includes network and API service time (Appendix B.4). No API access dates or run dates reported.

## Comparators and tuning-budget parity
Seven agent baselines: LATS, LLMCompiler, AgentPrune, HiAgent, FoldAgent, DyFlow, LatentMAS, run with the same Qwen3.8-27B policy on four H100 GPUs with tensor parallelism and bf16 (Sec. 4.1). The paper does not describe baseline-specific tuning or prompts in the main text; "Appendix B provides timing definitions and execution details".

## Reference labels
Task outcomes: success rates, benchmark rewards or scores from the environments (Table 1 caption).

## Sampling and intervals
Fixed seeds and instances. Figure 1 and Figure 3 report 95% paired bootstrap intervals (2,000 resamples) but Table 1 and Table 2 give point values only; a single run per method and instance is implied (Table 1/2). Interval values are shown only graphically.

## Headline results
JevSpawn has the highest score on five of eight tasks; AgentPrune remains strongest on PPNL, RushHour and Sokoban (Sec. 4.2, Table 1). Maze and Grid success 0.96 and 0.95 versus 0.52 and 0.73 for FoldAgent; 2048 score 305.12 versus 5.00 for LLMCompiler. Within the same architecture the Jev variant scores higher than Qwen scoring on PPNL (0.955 versus 0.950), LightsOut (0.66 versus 0.61) and Sokoban, matches Maze (0.960) and is lower on Grid (0.930 versus 0.950), RushHour, 2048 (296.000 versus 305.120) and Nullify (0.170 versus 0.210) (Sec. 4.2, Table 1).

## Calibration
None.

## Cascade and escalation
Not applicable. Retained branches allow recovery; no cost-quality cascade to a larger model.

## Option-name, cardinality, language and robustness tests
Ablations over expansion width {1, 2, 4, 8, 10}, parent allocations, declaration revision and shared observations (Sec. 4.1, 4.3); no option-name or order permutation tests of Jev.

## Cost and latency
JevSpawn E2E latency per task (s), for example Maze 40.91 versus 47.91 for the fastest baseline; LightsOut 111.05 versus 84.17 (FoldAgent); the Jev variant takes 1.4 to 2.1 times as long as Qwen scoring across all eight tasks (LightsOut 153.95 s versus 111.05 s), including API time (Sec. 4.2, Table 2). Text decoding throughput in Table 3. No dollar costs.

## Code and data availability
https://github.com/Hoyant-Su/JevSpawn (abstract).

## Authors' stated limitations
There is no limitations section; the conclusion lists none. Noted in text: longer execution accompanies higher scores on LightsOut and 2048; with a 300 s deadline 85% of 2048 tasks time out at 108 rounds (Sec. 4.2, 4.3).
