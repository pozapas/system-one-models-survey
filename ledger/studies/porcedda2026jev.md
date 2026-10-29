# Porcedda (2026), "Jev thinks 'I don't know', but doesn't say it: Introducing Sys1Cal-v1 Dataset for Probability Calibration"

Coder: batch V04. Full text: fulltext/2609.35342.html and .txt (arXiv HTML v1).

## Identification
- arXiv 2609.35342v1 [cs.AI], 28 Sep 2026; CC BY 4.0.
- Author: Riccardo Porcedda; little-g.ai, Sant'Anna School of Advanced Studies (L'EMbeDS) and University of Pisa (author block). Affiliation type: mixed (company plus universities).

## Task and data
- Probability-semantics benchmark Sys1Cal-v1: True/False questions about a proposition A with exact P(A) known by construction. Six state families (explicit probabilities, frequencies, compound, conditional, Bayes rule, sequential updates) rendered in seven forms (direct, counts, ratios, tables, prose, nested, distractor). 365 rendered examples from 92 problems (Section 2.1).
- Reference label: synthetic exact probability.
- Test exposure: new synthetic items.

## Decision model
- Jev through its Noul, Choice and Score primitives. No version, no run dates (searched for 1.13, 1.14, "version"). Choice uses options True/False; Score uses 10 levels from "Completely false" to "Completely true", expectation mu_S = sum q_j z_j with z_j = j/9 (Section 2.2).
- Each item queried 10 times because outputs are not deterministic; the mean probability is scored (Section 3).

## Comparators and tuning parity
- SemIf, an open-source Choice-style baseline [14], evaluated only on Choice (Section 3.1). Prompting and setup for SemIf not described. Jev primitives are compared with each other on identical items.

## Results
- Table 1: mean total variation / mean OVL (soft accuracy = 1 - |p_hat - p*|): Jev-Choice 0.236 / 0.764, Jev-Noul 0.0817 / 0.918, Jev-Score 0.1139 / 0.886, SemIf-Choice 0.371 / 0.629.
- Table 3 (Choice): raw mean/median OVL 0.764 / 0.771; after inverse uncertainty map 0.880 / 0.903; T/U/F interval OVL 0.931 / 0.978 with mean uncertainty width 0.292. The T/U/F score is interval compatibility, a more permissive quantity than binary OVL and "not directly identical to binary OVL" (Section 5).
- Fitted Score-to-Choice map: alpha = 0.530, beta = 1.011, R^2 = 0.834; mean absolute-error reduction 0.110 with a 95% CI that excludes zero (bounds not given) (Section 4). Table 2: global lambda 0.978 [0.789, 1.000]; latent-problem lambda_j 0.821 [0.760, 0.882], p = 2.94e-44.
- Representation sensitivity (Appendix A, Table 6), mean pairwise TV: Noul 0.0441, Score expectation 0.0656, Choice 0.0998, SemIf Choice 0.117.
- Decision example (Table 4): the same raw Choice output 0.632 leads to "act True" (raw), "act False" (calibrated 0.400) and "defer" (T/U/F, interval [0.400, 0.767]) at costs 100 for error and 45 for deferral (Section 5).

## Internal inconsistencies noted by the coder
- The Abstract says median soft accuracy improves "from 0.771 to 0.978", which compares binary OVL with the T/U/F interval score; Section 5 and Table 3 give 0.978 for T/U/F and 0.903 for the binary corrected Choice; the Conclusion gives 0.971 for T/U/F. The Contributions list says the mean rises "from 0.764 to 0.931".
- The inverse map was fitted on Sys1Cal-v1 and evaluated on the same 365 items; no held-out split or cross-validation is described. The corrected-Choice numbers are therefore in-sample.

## Sampling design and intervals
- Bootstrap CIs only for the latent-uncertainty parameters. No intervals on OVL means. Items are renderings of 92 problems, so the effective sample is closer to 92 than 365; the paper clusters over latent problems for lambda_j.

## Calibration
- Calibration quantity is OVL / total variation against known probabilities, not ECE or Brier; the paper contrasts itself with JevBench confidence-ECE (Introduction). Post-hoc calibration: inverse of fitted parametric map (coded "other").

## Cost and latency
- Not reported.

## Cascade
- No empirical cascade. The T/U/F deferral rule is shown in a worked example only (Table 4).

## Robustness
- Representation sensitivity across seven renderings (Appendix A). No option-order, option-name or language tests. Choice has only two options.

## Code and data
- https://github.com/little-g-ai/Sys1Cal-v1 (footnote 1).

## Authors' stated limitations (Section 6)
- Synthetic and templated, limited ecological coverage; Score analysis uses one-dimensional expectation; the uncertainty model is observational, "they don't prove, that Jev explicitly represents a hidden third truth value".
