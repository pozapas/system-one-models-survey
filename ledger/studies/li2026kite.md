# li2026kite — KITE: Scaling Jev Population Experiments with Sparse Flagship Calibration

- arXiv: 2609.27535v1 [cs.MA], submitted 23 Sep 2026. License CC BY-NC-SA 4.0.
- Author: Hengyu Li (The University of Tokyo). Affiliation type: academic. Declared: "This work is personal research with no funding of any kind and no competing interests" (section 12).
- Source: fulltext/2609.27535.html / .txt (fetched via `https://arxiv.org/html/2609.27535v1`, 2026-09-24).
- Code: https://github.com/HengyuLi-Ozaki-lab/kite_population_simulator (MIT license); only aggregates redistributed, Jev response cache not released.

## Task and data
KITE (Kernel, Intervention anchors, Tabulated execution, Error propagation) is a population-experiment architecture: query a typed behavioral kernel (Jev) once per unique rendered state, then execute populations of any size from the resulting table via event-keyed inverse-CDF sampling with common random numbers; a flagship LLM (GPT-6 Astra) supplies sparse paired-anchor corrections for a small fraction of states, and measured human-model discrepancy is propagated as a shared (not per-agent-independent) error term into effect estimates (Eq. 1-4, section 3). Three human-referenced datasets:
- **SocSci210**: 210 TESS social-science experiments (170 seen / 40 unseen studies, 37 supporting held-out intervention comparisons).
- **Arechar**: 45 COVID headlines, sharing/accuracy judgments on 6-point scales, 16 countries.
- **Epstein**: 9,070 completed participants, 5 waves, 8 intervention types, 20 cards (10 true/10 false headlines).

## Decision model / version pin
"The kernel is TypeSafe's Jev, pinned to jev-1.13.0, released on September 15, 2026" (Introduction) — directly matches the memory note that `jev-latest` resolves to jev-1.13.0. Flagship correction model: GPT-6 Astra (used via Codex CLI/subscription, not a metered API invoice). Comparison-tier models in the "Quality per expensive prediction" cost analysis: GPT-5.6 Luna (cheap tier, explicitly "not a flagship") and GPT-6 Astra.

## Comparators and tuning-budget parity
Kernel-only (Jev) vs. Hybrid (Jev + sparse Astra paired-anchor correction) vs. Flagship-direct-audit (Astra alone on a disjoint panel) vs. a condition-blind pooled-human oracle (G1, diagnostic baseline, not deployable). All use the same frozen p3 Noul-probability contract (one Noul probability per option, bundled and renormalized) — "Question wording, option text, fixed field order, and model version belong to the contract and cache key" (section 3.1). Not a prompting-budget comparison in the usual LLM sense; Jev/Astra/Luna are all queried zero-shot under the fixed p3 contract.

## Reference labels
Human experimental data from the three named studies (TESS/SocSci210, Arechar COVID-headline experiments, Epstein misinformation-sharing experiments) — reference_label_type = human_crowd (survey/experiment participants), i.e., real human respondents' answers and effect estimates, not LLM-generated or consensus labels.

## n and sampling
- Epstein (D1): 9,070 participants; 73,600 kernel predictions ($1.60); 1,080 Astra paired-anchor predictions (~1.7% of 64,000 application states) plus 9,000 predictions on a disjoint direct-audit panel; 60 cell corrections all feasible.
- SocSci210 (D3): 37 held-out studies, 162 blocks, 2,082 anchor items (3 anchors/condition, 1.00 million tokens, 15 minutes); reference is an earlier unpaired five-per-cell flagship run of 3,615 items.
- Arechar (16-country content-fidelity test): "matched-subset comparison" on a 30-person-per-country-condition subset in the both-new part.
- Discrepancy model (D2): fit on 91 seen studies / 2,195 effects (max likelihood + 80 study-bootstrap fits); retrospective evaluation on 37 held-out studies.
- Scale run (S1): 500 previously unused Epstein wave-3 personas x 20 cards x 2 conditions = 20,000-state workload.

## Test-set exposure
Mixed: SocSci210/Arechar/Epstein are pre-existing public human datasets (2021-2023), so test_set_exposure = public-pre-2026 for the underlying human data, but the paper explicitly flags this as a limitation for the model side: "A3c publication-status test finds no detectable interaction in flagship advantage... recall versus inference remains unresolved" and (Limitations) "familiar experimental designs may be recognized from training data. The experiments therefore do not license literature-absent intervention prediction."

## Cost and latency
Section 9 ("Cost and scale"): Jev costs per 1,000 predictions: $0.0344 (SocSci210, A3-era), $0.0331 (full SocSci210 test table, $4.53 for 136,901 predictions), $0.0319 (Arechar held-out), $0.0217 (Epstein D1), $0.0227 (fresh S1 predictions). Astra flagship costs per 1,000 predictions: $15.65 (SocSci210 A3b), $8.94 (Epstein D1), $10.62 (SocSci210 D3); GPT-5.6 Luna: $0.27/1,000 (SocSci210 A3). Implied cost ratios: ~8x Jev for Luna, ~455x for Astra (SocSci210), ~312x for Astra (Arechar). Scale execution (Table 3, hardware = "one Apple M4 Pro laptop (14 cores, 48 GB RAM), macOS 26.6.2, Python 3.12.2, NumPy 2.5.3, pandas 3.0.6, single process"): vectorized engine, 10^6 agents x 20 steps = 0.90 s (2.2x10^7 agent-steps/s); scalar engine 10^4 agents = 0.95 s. Fresh live-prediction latency: median 213 ms, p95 304 ms, under a 960-call/min throttle (~922 live calls/min achieved, 1,303 predictions/min including cache reuse); 29.2% of requested states were exact cache hits.

## Calibration
"Absolute option judgments were selected on development studies: p3 expected calibration error was 0.027, compared with approximately 0.23-0.25 for relative-choice formulations" (section 3.1) — calibration_quantity = ECE (binning unspecified), comparing the paper's chosen absolute (Noul-probability) prompting scheme against relative-choice formulations, not a post-hoc recalibration. post_hoc_calibration = none (this is a prompt/contract-design choice, not temperature/isotonic/Platt scaling).

## Cascade / escalation — the central mechanism
Not a confidence-gated request-time cascade in the REFLEX sense; rather a fixed sparse-anchor design: a small, pre-specified fraction of states get a flagship (Astra) paired-anchor call, and the flagship's estimated *effect* (not raw prediction) replaces the kernel's effect within each correction cell (Eq. 2-3, section 3.3). Headline results:
- **Epstein**: raw effect MAE falls from 0.0305 (kernel) to 0.0180 (hybrid), a 41% reduction (paired absolute-error improvement 0.0125, 95% CI [0.0064, 0.0167]); flagship-direct-audit MAE = 0.0200 (Table 2).
- **SocSci210**: primary approximation correlation 0.608 (kernel) -> 0.709 (hybrid) [0.550, 0.832]; captured decision gain 0.268 (kernel) -> 0.386 (hybrid), improvement 0.119 [0.014, 0.224], using 3 anchors/condition (2,082 items, ~1.5% of population states); at 1 anchor (694 items, 0.5%) gain is already 0.114 [0.014, 0.215]. Direct flagship's own gain is 0.336.
- Discrepancy-interval coverage (D2): retrospective coverage 0.93/0.96 at nominal 0.80/0.90 for Jev, vs. 0.29/0.36 from human-sampling-only intervals.

## Robustness / stress tests
- **Content fidelity across 16 countries** (section 6, Arechar): all 3 held-out test parts pass frozen item-and-person gates; content/sharing/accuracy rankings pass in all 15 new countries (both odd and even item halves), exceeding the required 12. Intervention sensitivity (prompt/tips nudge effects) fails both frozen gates for Jev (prompt -0.102/-0.034/-0.060, all "fail"; tips also fail); Astra passes both gates, with a prompt advantage over Jev of 0.077 [0.055, 0.099] and tips advantage of 0.030 [0.008, 0.051] on the matched subset.
- **Decision-value saturation**: from 5 to 200 simulated respondents per cell, sign accuracy ranges only 0.632-0.674 and captured gain 0.255-0.358 "without a rising trend" — more simulated respondents reduce persona-sampling noise but do not fix systematic kernel error.
- **Demographic-persona limits**: cross-validated demographic-group predictor has individual-response correlation of only 0.013.
- **Memory tier** (separately evaluated, B2): passes coherence and marginal-preservation criteria in 6/6 clean within-subject studies; median correlation-pattern agreement rises from 0.01 to 0.52 (~65% of human split-half structure); distant-pair coherence reaches only 40% of human coherence; raw self-conditioning (without correction) "can surrender 91% of the independent kernel's marginal advantage over a uniform baseline."
- **Scale variance reduction**: common random numbers reduce effect standard deviation from 0.00303 to 0.00072 across 100 seeds at 10^4 agents (~18-fold variance reduction).

## Code and data availability
"Code and evaluation records are available at https://github.com/HengyuLi-Ozaki-lab/kite_population_simulator (MIT license)... Only aggregates are redistributed; the Jev response cache is not released and outputs are not used for distillation" (section 12). code_available = "partial (code + aggregate results on GitHub, MIT; raw Jev response cache and underlying microdata not released)".

## Limitations (paper's own, from "Limitations" section)
- "Only two held-out human-referenced datasets test the hybrid: Epstein and SocSci210; their effect structures and prior exposure differ." Policy-value and headline-heterogeneity preregistered primaries "were not shown."
- "D3's primary approximation gain passes narrowly; within-task sensitivity is unchanged within uncertainty and raw effect MAE worsens. Pairing does not demonstrably outperform equal-budget unpaired prediction."
- "Sparse calibration can import flagship errors, as in Epstein wave 5, while the kernel itself overpredicts norms messages. Neither parent is a universally better behavioral model."
- "Discrepancy slopes vary across study selections... A3c is inconclusive about recall; familiar experimental designs may be recognized from training data. The experiments therefore do not license literature-absent intervention prediction."
- "Memory coherence is local, and cohort-level marginal correction may erase real persistence or treatment pathways when exposure is endogenous."
- "Proprietary models and access limits constrain replication: reproducible code does not imply reproducible outputs. Version pins and private caches preserve recorded calculations, but vendor updates, repeat-call variability, and unavailable response caches prevent guaranteed independent regeneration of the same predictions."

## Seed claims checked (see parts/seed_check_C.csv)
1. "anchors covering 1.7% of states reduced effect error by 41% on Epstein experiments with 9,070 participants" — confirmed: "Astra supplies 1,080 paired anchor predictions, approximately 1.7% of the 64,000 application states" (section 7.1); "Effect MAE falls by 41%" (Table 2: Kernel raw MAE 0.0305 -> Hybrid raw MAE 0.0180); "Epstein provides 9,070 completed participants" (section 4).
2. "SocSci210 results" — confirmed and detailed: captured decision gain rises from 0.268 (kernel) to 0.386 (hybrid) at 3 anchors/condition (1.5% coverage), improvement 0.119 [0.014, 0.224]; primary approximation correlation 0.608 -> 0.709 (section 7.2).
