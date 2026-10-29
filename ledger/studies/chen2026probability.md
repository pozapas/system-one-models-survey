# Chen and Li (2026), "Probability Contracts: Accuracy, Coherence, and Decisions Across LLM Interfaces"

## Identification
- arXiv 2609.37470, read as v2 ("arXiv:2609.37470v2 [cs.LG] 05 Oct 2026", header); first version per batch file 2026-09-27. License CC BY 4.0.
- Authors Han Chen and Yingrui Li, both "Independent Researcher" (byline). affiliation_type = independent.
- Code and data: a "compact submission supplement" with scores, analysis code and audit records; raw-response archives "retained separately"; the compact artifact "alone does not replay the full collection from raw bytes" (Appendix E). No URL appears in the text, so code_available = partial.
- AI use statement: ChatGPT, Codex, Claude and Gemini used for code, analysis, literature discovery, drafting and critique; humans take responsibility (AI Use Statement).

## Task and data
- Synthetic benchmark of finite "worlds" with four latent cells, integer prior counts and rational evidence likelihoods, whose exact posterior is computed with rational arithmetic and an independent 70-digit decimal path (agreement within 1e-15) (Section 4.1). Primary cohort: 1,000 roots, 250 per generator (finite-population, noisy-sensor, joint-attributes, missing-rule), 125 per generator-encoding stratum, encodings joined tables or nested records; 12 request variants per root, 12,000 intended slots, 11,913 eligible after 87 undefined conditionals (Section 5.1).
- Reference labels: exact posterior from the generator (synthetic); no human labels. Items generated for this study; "Semantic hashes separate it from 2,700 earlier benchmark roots; they do not establish absence from pretraining data" (Section 5.1). Coded test_set_exposure = new.
- Secondary: 400-root headroom cohort selected by binary posterior confidence; 200 reused worlds with Mistral and OLMo readouts; reasoning-budget arms (Appendix A, N, T). Not extracted except as noted in the paper's abstract.

## Models
- Jev-1.13.0 through native Noul ("Event") and Choice interfaces; "All returned responses identified Jev-1.13.0" (Appendix M); the stored request uses `model: jev-latest` (Appendix H). One recorded attempt per main request; a 477-request development set excluded (Section 5.1). Collection dates are not stated in the text. Jev returns serialized decimal probabilities, so rounding is part of the configuration (Section 5.1).
- Kev-4B (checkpoint 485ace8..., rank-16 LoRA adapter plus 256-dim pointer head, stored temperature T = 2.143546925 retained, no study fit), Qwen3.5-4B-Base (1001bb4...) and posttrained Qwen3.5-4B (851bf6e...) with answer-token likelihood readouts, FP32, non-thinking template (Section 5.1, Appendix B). Kev training suites not audited for overlap with benchmark worlds (Appendix B.1).
- Tuning parity: same requests and prompts across configurations, no test-set recalibration fitted (Section 2, Section 5.3). Comparisons "do not isolate a single component" because training, prompts, readout and precision vary (Section 8). Primary local models share a Qwen lineage.

## Statistics
- Posterior error primarily total variation (TV) to the exact posterior; expected multiclass Brier; reject-option controller (Chow 1970) with wrong cost 1, correct 0, deferral c (primary c = 0.10; also 0.02, 0.05, 0.20, 0.40); failed or rejected responses are assigned defer, so validity and coverage are reported with loss (Sections 5.2, 5.3).
- 5,000 paired root-bootstrap replicates, seed 2026092408, resampling within strata; eight generator-encoding strata weighted equally; pointwise percentile intervals, no multiplicity adjustment (Section 5.3). Primary targets, relations, costs and comparisons pre-specified before Jev collection; exact-posterior calibration, symmetric extensions, Sections 7 and Appendices P-S are post hoc (Analysis status).
- Calibration: prespecified top-class confidence versus outcome-draw reliability at 10, 15, 20 bins; the post-hoc 15-bin exact-posterior gap uses posterior mass of the selected class (Section 5.3, Appendix D.1). No recalibration fitted (post_hoc_calibration none).

## Cost, latency, cascade
- No latency or monetary cost is reported ("omitted monetary query costs", Section 8). Policies compare one-query (Event, Choice, Random interface) and two-query (Mean, Agreement) rules (Section 7.2): a cascade-like accept-or-defer analysis. At c = 0.10 Jev Event loss 0.09654 and Agreement 0.09654 versus always-defer 0.10000 (Table 4).

## Option-name, cardinality, order, robustness
- Variants include option permutation, layout change, opaque answer keys and irrelevant metadata (Section 4.2, Table 1); Jev mean permutation TV 0.0534 versus Kev 0.1143 (Table 2). Joint surface-order and answer-ID recoding changes the posttrained Qwen expected Brier by -0.1971 (Section 6.2). Cardinality 3 to 4 categories only.

## Authors' stated limitations (Section 8)
- Four-cell worlds and two encodings; open-ended tasks untested; primary local models share a Qwen lineage; hosted results cover one Jev revision; 7B extension has only 59 and 60 valid canonical JSON reports of 200; training, prompts, readout and precision vary; headroom cohort selected; post-hoc analyses exploratory; historical service order and omitted query costs limit policy comparisons.
