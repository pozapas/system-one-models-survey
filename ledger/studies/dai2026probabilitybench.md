# dai2026probabilitybench

arXiv 2610.17016v1 (cs.LG), 12 Oct 2026. "ProbabilityBench: Model Evaluation and Calibration with Exact Ground-Truth Uncertainty."
Authors: Yuyang Dai (Florida State University), Yuting Tang (University of Tokyo; RIKEN AIP), Futoshi Futami (University of Osaka; University of Tokyo; RIKEN AIP), Takashi Ishida (RIKEN AIP; University of Tokyo). Affiliation type: academic. (title block)

## Task and data
- Benchmark of three simulated text worlds with exact instance-level class probabilities and Bayes error: peer-review outcome (accept/reject), covert information transfer (AI-safety audit), credit risk (default). Each world has Low, Medium, High Bayes-error settings by hiding information (Table 2: Bayes error 0.034/0.091/0.109 peer review, 0.019/0.074/0.145 covert transfer, 0.026/0.108/0.167 credit risk). Memos rendered from fixed templates with 4 relevant and 13 irrelevant numeric features; rendering provably preserves class probabilities. (Sec. 3, 4, App. B)
- Models report the positive-class probability; scored by KL(p* || q) in nats (q clipped to [0.001, 0.999]). Reference labels: synthetic, analytic exact probabilities (not sampled labels). Few-shot demonstrations are other memos with sampled outcome labels. (Sec. 5, App. A.2)
- Test cases are newly generated per seed (seeds 2032 to 2034); no contamination possible by construction, though the generators are public.

## Models
- Eight native decision models via OpenRouter native Noul endpoint: Jev 1.13 Noul (typesafe/jev-1.13-20260917), GPT-6 Luna Decisions, Liquid d1, Perplexity Decider V1.1 27B, Clef, Clef Flash, Solar Decide, Kev 4B. Eight generative models: GPT-5.6 Luna (medium reasoning, via OpenRouter), Qwen3.8 Flash, Mistral Small 3.2, DeepSeek V4 Flash, Claude Haiku 5.5, Gemini 3.8 Flash, GPT-5.6 Terra, Claude Sonnet 5.5. Run dates not stated; price source dates 2026-09-21 to 2026-10-09. (App. A.2, A.3, Table 1)
- Only Jev has a stated pinned version string; the others are named without resolved IDs in this paper.

## Comparators and parity
- Same memos, questions, criteria and 25 demonstrations (Medium visibility) for all 16 models; generative models receive byte-identical messages to GPT-5.6 Luna with a system message asking for positive-class probability (not confidence in the chosen class). Native decision models use default endpoint settings; generative settings fixed before full collection after a small validity pilot (reasoning off with 2,000-token cap for several, medium reasoning with 8,000 or 16,000 caps for others). No per-model prompt tuning reported. No retries for quality; transport-only retries. A model-world pair is plotted only if every 300-case seed block is at least 99.5% valid (Gemini 3.8 Flash dropped in covert transfer: 16 content_filter replies). (App. A.3)
- Headline comparison: first 300 held-out cases per world per seed, three seeds, 25 shots, Medium visibility. Demonstration-count study (Jev vs GPT-5.6 Luna): 0, 10, 25, 50 shots, 500 cases per seed per world, 18,000 predictions per model. (App. A.2)

## Results
- Cost-quality: Perplexity Decider is cheapest in every world; decision models account for ten of fourteen model-world points on the observed Pareto frontiers (including Jev and Perplexity Decider). GPT-5.6 Terra has the lowest mean KL in peer review; Claude Sonnet 5.5 in covert transfer and credit risk, at much higher list prices. Per-model KL values appear only in Fig. 1 and Fig. 3 (plots), not in a table. (Sec. 5, Fig. 1)
- Few-shot: Jev mean KL in peer review falls from 0.248 (0 shots) to 0.203 (50 shots), Luna's rises from 0.199 to 0.411; Jev about stable in covert transfer; both improve in credit risk, larger reduction for Jev. Sample standard deviations across seeds shown, no confidence intervals. (Sec. 5)

## Calibration
KL to exact class probability (proper-score decomposition) as the probability-quality metric; no binning or ECE for the models. Calibration estimators themselves are meta-evaluated (witness multicalibration error positive even for the true probabilities). No post-hoc recalibration. (Sec. 5)

## Cost and latency
Costs at published list prices applied to provider-returned token counts, divided by requests (not valid replies). Jev 1.13 Noul 0.042 USD per million input tokens, 0.00 output; Perplexity Decider V1.1 27B 0.02; GPT-6 Luna Decisions 0.10; Liquid d1 0.04; Clef 0.24; Clef Flash 0.09; Solar Decide 0.10 (routed at 0.05); Kev 4B 0.042. Jev returns roughly 20 output tokens; decision models bill input tokens only. No latency reported. (App. A.3, Table 1)

## Cascade or escalation
None.

## Robustness
Number of demonstrations (0/10/25/50), visibility (Low/Medium/High Bayes error). Clipping affects 1,149 of 42,300 probabilities in the 16-model comparison (731 DeepSeek V4 Flash, 230 Perplexity Decider, 150 Liquid d1, 19 Luna Decisions); 67 Luna replies and no Jev replies in the 36,000-prediction demonstration study. No option-name or language tests (binary positive-class question).

## Code and data
Code: https://github.com/ishida-lab/ProbabilityBench (project link on the title page and "The released code holds the authoritative value lists", App. B). Per-model KL values for the 16 models appear only in Fig. 1 and Fig. 3, checked on PDF page 1: axes carry ticks only, markers carry no value labels, so no per-model KL rows were extracted.

## Authors' limitations (Sec. 6)
Fixed templates (no LLM-generated prose); three domains chosen by the authors; substantial manual design and verification; population integrals for calibration are estimates.
