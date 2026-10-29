# zhuang2026startlux: StartLux-Decision, AutoThink Decision Models with Reinforcement Learning for Calibrated Deliberative Decisions

arXiv:2610.17309. First version v1 on 12 Oct 2026 (the screen list gives 2026-10-12); the HTML saved in `fulltext/2610.17309.html` and `.txt` is v2 dated 20 Oct 2026 (header line). Numbers below are from v2. Extractor batch V12.

## Authors and affiliations

Xialie Zhuang (StartLux; The University of Hong Kong), Zunhai Su (StartLux; HKU), Jia Pan (HKU), Ngai Wong (HKU; EMUS Lab), Guanhua Chen (Southern University of Science and Technology), Chuan-Wei Kuo (StartLux) (author block). Corresponding authors are flagged in a footnote. Affiliation type: mixed (company StartLux plus universities).

## Task and data

Own-model paper. StartLux-Decision is a family of open-weight decision models, 0.8B to 27B parameters (0.8B, 2B, 4B, 9B, 27B), with two variants (Sec. 1, 2).

- Instant: single forward pass, option-letter logit readout with temperature scaling and softmax over K options (Eq. 1, Sec. 2.1), with bidirectional attention in full-attention layers (Sec. 1, 6.1).
- AutoThink: answers confident cases directly and invokes explicit reasoning for uncertain ones (default confidence threshold 0.9), then fuses single-pass and post-reasoning distributions with weights 25% and 75% (Sec. 2.2, 5.2). Trained with RLCD2, a reinforcement-learning stage with a proper-score reward from a frozen model and a soft length penalty (Sec. 3).

Typed decisions: choice among named options, binary, or ordered scale of 2 to 10 levels (Sec. 2.1). Single readout supports up to 26 options (App. D.4).

Evaluation sets (Sec. 4):
- Decision Index (DI) 0.2.1: 38 benchmarks, five domains, chance-corrected skill points. DI 0.3 removes ForecastBench and replaces GSM8K with 2,638 reconstructed requests. Only the public subset (20% of the DI 0.3 leaderboard score) is evaluated; Table D.1 lists 37 benchmarks.
- DecisionPivot (introduced here): core track of 13 programmatically generated task families with 600 examples each (7,800 examples), mostly contrast pairs differing in one answer-changing detail; pair accuracy needs both items right. Reused-tasks track of 35 public test sets, 34,104 examples absent from training (Sec. 4.3).
- Held-out items from the training distribution: 2,986 examples after excluding 35 overlapping with training or RL data (Table 2).

## Decision models and versions

StartLux-Decision 0.8B to 27B Instant and 2B/4B/9B/27B AutoThink (released weights; no checkpoint hash in text). Reference models: Jev (hosted) with no version string and no access date in the main text ("a hosted decision model whose training procedure has not been publicly disclosed", Sec. 3 related work; Table 4); Perplexity Decider v1.1 (pplx-decider-v1.1-27b, accessed 11 October 2026), Clef (Cloudflare, accessed 11 October 2026), Decision 3.0 family (d3, d3-flash, d3-mini, d3-nano, d3-lite, d3-edge), Decision 2.0 family, Kev 27B, JEV-27B and JEV-9B (AutoTrust AI Lab), FlyMyJev-4B, H2O-Lightning-4B, d1-3B (Liquid AI), Bosun 3.1 1.7B, Bespoke Nimble 9B v3, OneJev 0.8B (Tables 4, 6). GLM-5.3 with explicit reasoning is also a DecisionPivot reference (Sec. 4.3).

## Comparators and tuning-budget parity

Reference scores on DI come from the public leaderboard except Decision 3.0, which the authors evaluate with their own pipeline, "using the model's own prompt and readout" (Table 4 caption, Table 6 caption). The leaderboard excludes reasoning-trace models (Table 4). Reference models receive no tuning by the authors. Important asymmetry: "The public subset of DI also served as the development benchmark", used to choose Stage 2 data recipes, prompt attention variants and seed averages, "so these scores reflect model selection and are not independent test results" (Sec. 4.1). Calibration temperatures, AutoThink gate, mixture weight and reasoning budget were set on held-out training-distribution items, not on DI. DecisionPivot "was not used for any data, checkpoint or configuration choice" (Sec. 4.1), but the same group built it and trained on related programmatically generated families (Sec. 5.1 notes representation effects). Latency comparisons use a matched subset of 186 of 300 requests that all systems handle in a single forward pass (Table 6).

## Reference labels

DI: public benchmark gold labels aggregated by the leaderboard (labels of mixed origin). DecisionPivot core: programmatic verification (synthetic procedure). Held-out training-distribution items: labels of the training distribution (origin not detailed in main text).

## n, sampling, intervals

DecisionPivot core n = 7,800; Figure 9 reports 95% bootstrap intervals, but headline figures are read from text (point estimates only, intervals appear only in the figure). DI scores are single point values with no intervals. Seed averages form the Instant checkpoints (Sec. 4.1). Calibration error: 15 confidence bins on maximum option probability, reported as confidence-accuracy gaps in percentage points (Sec. 4.4; equal-width versus equal-mass not stated).

## Test-set exposure

DI public subset: public benchmarks, "most evaluated tasks belonging to families represented during training" (Sec. 4.1); Appendix A.3 lists benchmark-specific training coverage and A.6 reports decontamination (not read in full). DecisionPivot core: newly generated; the paper reports decision-training data raise accuracy on represented families by 8.6 points versus 0.3 outside them (Sec. 5.1).

## Cost and latency

Single NVIDIA H200, vLLM, one request in flight. Median single-readout latency, BF16, 1,024-token prompts: 31 ms at 0.8B, 32 at 2B, 41 at 4B, 42 at 9B, 98 at 27B (Table 5; vLLM 0.31 in the caption, while App. D.3 gives vLLM 0.19.1 for evaluation; the paper does not reconcile these). Matched comparison (Table 6): 27B Instant median 51.9 ms versus Kev 27B 46.1, JEV-27B 46.8, Perplexity Decider 52.4. llama.cpp GGUF Q8_0 on H200 (Table 7) and Apple M5 Pro 64 GB with mlx-lm (Table 8) also reported. No latency or cost figure is given for hosted Jev. AutoThink adds generation cost: reasoning on about 33%, 29%, 28% of DI questions (4B, 9B, 27B), averaging 372, 271, 110 reasoning tokens per question (Sec. 5.2).

## Calibration

15-bin confidence-accuracy gaps on 7,800 DecisionPivot core examples (Sec. 4.4, Figure 11): AutoThink 2.4, 3.3, 5.2 points at 4B, 9B, 27B; Instant 7.3, 6.4, 5.1; Perplexity Decider v1.1 8.9; hosted Jev 13.8; Clef 19.3 (systematic overconfidence). Temperature scaling fitted on held-out items (Sec. 4.1). Policy-aware calibration (isotonic within confidence strata; logistic plus isotonic for best-of-N) reduces signed confidence-accuracy gaps from [-11.7, +20.5] to [-2.7, +2.1] points across 184 settings in four pipelines (best-of-N, think-gate, cascade, select-then-think); maps transferred to unseen datasets leave residual overconfidence of up to 6.1 points (Sec. 5.5). Example: 80 to 90% confidence predictions of a 9B verifier are 92% accurate individually but 78% after selecting the best of 32 candidates (Sec. 1, Figure 15).

## Cascade or escalation

AutoThink is itself a confidence-gated escalation from single-pass to reasoning. At threshold 0.9 the 9B model gains 1.0 accuracy point on held-out items with 596 reasoning tokens per example; 27B gains 2.5 points with 273 tokens (Sec. 5.2). DecisionPivot pair accuracy 9B: 59.9% with reasoning at the default gate versus 22.3% with reasoning disabled; 27B 86.9% versus 48.0% (Sec. 5.2). Acceptance at a 5% target error rate: about half of default predictions at 9B and 27B, 2% at 4B (Sec. 5.5).

## Option-name, cardinality, robustness

Contrast-pair design in DecisionPivot tests sensitivity to a single answer-changing detail. 151-option intent questions: 4B accuracy 86.7% versus 95.7% for 26 options, using parallel groups of at most 25 options and a final readout; the procedure eliminates the correct answer before the final round in 0.2 to 0.7% of cases (App. D.4). Quantization: FP8 and Q8_0 largely preserve scores, Q4_K_M can lose more (Table 9). vLLM bidirectional plugin agrees on the top choice with the reference implementation in 99.5 to 99.8% of cases; MLX 99.4 to 99.9% against vLLM (Sec. 6.1). Serving hazards: prefix caching changes 2.6% of readouts by more than 0.05; incomplete request coverage lowers a score from 66.36 to 61.31 (Table D.2). No language tests.

## Code and data availability

Model weights and inference code released at https://github.com/StartLuxLabs/StartLux-Decision; code Apache-2.0, weights CC BY-NC 4.0; model-generated training examples not redistributed (App. A.4). DecisionPivot cited as (StartLux, 2026).

## Authors' stated limitations

Future work on generalisation beyond represented task families and robust probability reliability under distribution shift (Sec. 7). In-text caveats: adaptive reasoning adds generation cost; calibration is sensitive to distribution shift; Instant remains preferable for latency-sensitive use (Sec. 5.2, 5.5).
