# Ye, Liu & Jiang (2026), "NumericJev: Jev-like LLM Numerical Decoding with Multiway Decision Trees"

## Identification
- arXiv 2609.28587v1 [stat.ML], 23 Sep 2026 (header). License CC BY-NC-SA 4.0. Full text fulltext/2609.28587.html and .txt.
- Authors Weiwei Ye, Hangchen Liu, Renhe Jiang, all "The University of Tokyo" (byline). affiliation_type = academic.

## Task and data
- Training-free numerical decoding over a structured-choice (Jev-like) interface: recursive K-way interval refinement of a user-supplied range (Algorithm 1, Section 3). Depth ceil(log_K N); 100-cell grid needs two rounds for K=10.
- Main evaluation (Section 4, "Fixed affine-grid evaluation"): 64 base arithmetic expressions (16 each of +, -, x, /; results integers 1..99 except 50), seed 20260923, four affine transforms (y=z, 0.01z, z-50, 10000z) = 256 expressions, two option orders, two conditions (Arithmetic, and Provided with the answer in state). 512 outputs per method per condition. 1,024 jobs, 6,144 method outputs.
- Archived exploratory evaluations (Section 4, Appendix E): 12 hand-picked arithmetic questions (16-value grid); S&P 500 closing level on three dates (3230.78, 3756.07, 4769.83 from FRED) with two orders and two repeats; threshold/CDF experiment, 48 query groups (Section 5.6).

## Decision model
- Hosted Jev "identified as jev-1.13-20260917" for all choice-interface experiments (Section 4). Served identifier, every request and response recorded. No run dates for individual calls beyond seeds; documentation accessed 23 Sep 2026 and FRED references verified 23 Sep 2026 (References).
- Single model version (Limitations, Section 6: "one hosted model version").

## Comparators and tuning parity
- Within-Jev decoders: direct selection among 100 grid values; interval trees K=2, 4, 10; sequential decimal index digits; independent binary index bits (Section 4 "Decoders"). Same prompt wording across trees; index encodings get same lower bound and step.
- Four SCM-trained continuous heads (spline and Beta, Qwen3.5-4B-Base and 9B-Base, LoRA rank 16, 12,000 structural-causal training queries, checkpoint selected on a 3,000-query validation split before this comparison) transferred to the arithmetic suite without arithmetic training; prompt semantically matched but not text-identical (Appendix F). Authors state backbones and training differ, so no output-head ablation (Figure 1 caption; Section 6).
- Cases, prompts, model version and job order fixed and hashed before execution; prompts not revised after inspecting results; but this controlled extension follows exploratory experiments, so "not a blind model-development benchmark" (Section 4).

## Reference labels
- Synthetic: deterministic arithmetic verified by an exact-rational AST evaluator (Appendix B). Historical index references from FRED series SP500.

## n, sampling, intervals
- 95% family-bootstrap intervals, 10,000 percentile replicates, seed 20260923, resampling the 64 base families (keeping transforms, orders and paired conditions together) (Section 4). Paired MAPE differences of trees vs direct choice all include zero ([-14.48, 7.03], [-16.10, 10.31], [-14.05, 12.77]); paired NMAE differences exclude zero (Section 5.1).
- Primary endpoint MAPE; NMAE secondary; "within 5% relative error" added post hoc (Section 5.3).
- Historical study has only three distinct dates (Table 3).

## Results (key)
- NMAE 5.18% direct vs 1.84% K=10 (1.76% K=2, 1.60% K=4); MAPE 21.68% direct vs 19.73% K=10 (Table 1). Within 5%: 83.40% K=10 vs 80.47% direct (Section 5.3). Supplied-value MAPE 3.79% direct vs 0% K=2 (Table 1). Index digits 84.43% and bits 95.13% MAPE.
- Scale reversal: x10^4 domain K=10 MAPE 30.96% vs 0.52% direct (Section 5.4; Table 2). Ordering gap 0.56% (K=10) vs 1.23% (direct); affine gap 2.44% vs 6.91% (Table 4).
- Historical recall: mean relative error 4.58%, 0% when supplied; binary follow-up with changed prompt 31.17% (Section 5.5).
- Continuous heads: 2.73 to 6.25% within 5% (Section 5.3; Table 6).

## Calibration
- None evaluated. "The model’s categorical probabilities are not assumed to be calibrated numerical uncertainty" (Section 3.1). 25 of 48 threshold query groups produce non-monotone CDFs; isotonic projection is a shape repair and "cannot establish calibration" (Sections 3.4, 5.6; Appendix G).

## Cost and latency
- Provider-reported totals for the main run: 6,982,898 input tokens, 1,773,003 output tokens; 6,863 requests (Appendix C). Authors state these are not audited billing and not isolated per-method latency. Dependency depths (rounds) given in Table 1 but "not measurements of isolated method latency". Continuous-head wall time 47 to 99 s per checkpoint on one GPU each (Appendix F; GPU model not named).

## Cascade, option-name, cardinality, robustness
- No cascade. Option-order reversal (ordering gap, Table 4) and affine/scale transformations (Table 2, Table 4) are the robustness tests; digit and bit encodings test representation. No language tests.

## Test-set exposure
- Generated arithmetic expressions with a published seed, new; historical S&P levels are public facts, authors say recall test, "not ... demonstrated training-data membership" (Section 4).

## Code and data
- https://github.com/Bring-AI/jev-numeric (abstract). Offline reproducibility from saved responses; re-querying may change or fail if pinned version unavailable (Appendix H). Illustration and prose prepared with a language-model coding agent per Appendix H.

## Paper's own limitations (Section 6)
- One hosted model version; simple generated arithmetic; small historical example; continuous-head baselines differ in backbone and training; user supplies range and resolution; no out-of-range targets; bootstrap does not capture backend changes.
