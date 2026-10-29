# chen2026system1 — System1-Arena: Which Decisions Can Be Left to System 1?

arXiv:2610.21244v1 [cs.CL], 15 Oct 2026; CC BY 4.0. HTML from https://arxiv.org/html/2610.21244. Extractor: batch V15.

## Authors and affiliation
Tianyu Chen, Xinyang Liu (equal), Ruyi An, Zhendong Wang, Mingyuan Zhou (corresponding), The University of Texas at Austin (title page). Affiliation type: academic. Code: https://github.com/TianyuCodings/S1-Arena (link in HTML).

## Task and data
A benchmark of decision requests (a state plus typed boolean, choice (2 to 255 options) or score (2 to 10 levels) questions). 92,125 questions across 105 tasks from 268 public sources in 16 domains, plus 138 closed-loop environments from 18 families (Section 1). Non-agentic component: 78,362 questions, 13 domains, 87 tasks, about 500 requests per task sampled with a fixed seed, stratified by label (Section 3.2; Appendix B). Static model comparison covers 85,305 questions in 94 tasks (Section 4). Single-step agent comparison: 3,481 recorded steps, 6,943 questions, seven tasks (Section 3.3). Closed loops: 127 environments with a success criterion (Appendix B).

## Decision models evaluated
30 models: 7 closed LLMs (verbalized probabilities in JSON), 13 open LLMs (answer-token probabilities, vLLM), 10 System-1 models: Jev (listed as "Jev 1.13"), Laya (421M), CLM-v0.1-8B, five Decision-2.0 models (Vega-27B, Lux-9B, Nox-4B, Sol-2B, Kai-0.6B), Microsoft-Decision-1 (post-trained from Qwen3.5-9B) and the OpenAI Decisions API (serves GPT-6 Luna) (Section 4; Table 1). Versions: Jev "1.13" without a date stamp; the OpenAI Decisions API "(public beta, October 2026)"; Microsoft-Decision-1 via OpenRouter "(alpha, October 2026; served by Azure)" (Appendix B). Jev runs "through the Vercel AI Gateway" (Appendix B). Run dates are not given beyond October 2026; prices "reflect the prices on the days of the runs" (Limitations).

## Comparators and tuning budget
Each model family has one fixed prompt, "no model gets a prompt that we tuned for it" (Appendix A). Reasoning disabled where the interface permits; five models (Claude Opus 5.5, GPT-6 Astra, Grok 4.7, gpt-oss-20b, gpt-oss-120b) must reason and use lowest effort (Section 4). One draw per request, run-to-run variation not measured (Limitations). Closed LLMs get verbalized probabilities (Opus gets no token probabilities); open LLMs get one question per prompt. Parity is by design: same requests, fixed per-family prompt. Instructions for tier-C requests (33% of requests) were written by the authors (Appendix B).

## Reference labels
"All labels come from the original sources; we do not create new labels": test results, solver outputs, resolved events, expert annotations, annotator distributions, original dataset labels (Section 3.2); 4,425 requests carry soft labels (Appendix B). Coded `mixed` (headline accuracy pools label types). Noise is inherited (Limitations).

## n, sampling and intervals
Accuracy and Brier are means over tasks (domain score = mean of tasks; overall = mean over all tasks equally weighted) (Section 3.4). No intervals on Table 1 or Table 2. The 95% intervals appear only for thinking-budget curves (paired bootstrap stratified by source, Appendix B). Sampling is about 500 requests per task, stratified by label.

## Test-data exposure
Public sources, "many ... several years old, so some inputs may have been seen in training" (Limitations). Some sources are recent (a FreshQA snapshot of 2026-04-21, Table 4). No contamination check. Coded public-pre-2026.

## Cost and latency
Latency is the median per-request time: local models on an idle GPU server; closed LLMs, Jev, Microsoft-Decision-1 and the OpenAI Decisions API "through the network", so latency includes service and network (Appendix B; Limitations). Jev 321 ms, $0.052 per 1,000 requests, 0 output tokens; GPT-6 Luna 1,276 ms, $0.143; Claude Opus 5.5 2,293 ms, $10.380 (Table 1). Costs in USD for hosted models and H100-equivalent GPU-seconds for local models, not converted (Section 4). The authors' own spending is not reported.

## Calibration
Brier score (0 to 2) is the headline; Appendix B defines ECE with 10 equal-mass bins but no ECE results were found in the text read. No post-hoc recalibration. Jev Brier 0.349 vs GPT-6 Luna 0.461. Answer-token probabilities can be overconfident (Gemma-4-31B at or above 0.999 on 87% of questions); reasoning raises accuracy but worsens Brier for Qwen3.8-27B (0.391 to 0.430) (Section 5; Figure 4).

## Cascade or escalation
None evaluated; the paper motivates routing between System-1 models and LLMs but tests no cascade.

## Option-name, cardinality, language and robustness tests
Domains vary in option count (2 to 255 options; labels with more than 26 options use multi-token number labels; Appendix B). Gaps by domain (Figure 3). No option-order shuffle, option-renaming or language test reported in the text read. Real-time mode advances the environment by each model's measured latency (Section 3.3).

## Code and data
Code https://github.com/TianyuCodings/S1-Arena; dataset and leaderboard links on the title page. Sources that forbid redistribution are rebuilt by loaders (2,607 requests; Appendix B).

## Authors' stated limitations
Inherited label noise; author-written tier-C instructions; public and older sources may be in training data; online services' latency includes the network; one draw per request (Section 7).
