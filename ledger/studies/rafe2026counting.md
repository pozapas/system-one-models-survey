# Rafe & Das (2026), "Counting the Uncounted: Population-Level Surveillance of Documented Pregnancy and Fetal Harm in Police Crash Narratives with a System One Model (Jev)"

## Identification
- arXiv 2610.00213v1 [stat.AP], 21 Sep 2026 (header). License arXiv perpetual non-exclusive. Full text fulltext/2610.00213.html and .txt.
- Authors: Amir Rafe, Subasish Das; Civil Engineering, Texas State University, San Marcos TX (byline). affiliation_type = academic. Application study rather than a model evaluation.

## Task and data
- Population-level extraction of documented pregnancy in Texas CRIS police crash narratives 2017 to 2025: 5,109,746 rows, 5,018,079 after dropping empty and under 41 characters (Section 3.1).
- Three stages (Section 3.2). Stage A regex screen hits 6,840 narratives (core tier 5,416; everyday-English tier adds 1,424). Stage B sends all 6,840 to Jev under the eight-question pregnancy_v1 schema (one presence question, three gated choice questions, four others; Table B.1); presence threshold tau = 0.5. Stage C reuses presence answers on 499,306 random non-hit narratives, 45 positives, 14 of 42 adjudicated candidates confirmed.
- Headline: 5,333 confirmed in Stage B; Rogan-Gladen corrected total 5,467 [5,306, 5,577] documented crashes, 58 with fetal harm (Abstract; Table 3).

## Decision model
- Jev only, "pinned to the single version jev-1.13.0, recorded on every call" (Section 5 limitations; Data and code availability). No run dates stated. Closed model; results may not reproduce on a later version.
- Typed output: probabilities over analyst-defined options, no text (Section 3.2). Gated choices forced to no_pregnancy when presence p <= 0.5.

## Comparators and tuning parity
- No comparator decision model or LLM. The regex screen is the only baseline (prefilter). Single system studied, so tuning parity is not applicable.
- One composition check: the presence question asked alone versus in company of nine others on 590 paired narratives, binary agreement 100.0%, Pearson 0.998, mean absolute probability difference 0.0034 (Section 3.2).

## Reference labels
- Human adjudication, blind (narrative text only, model probabilities withheld, order shuffled) against written criteria (Section 3.3; Appendix C). 407 narratives read: 229 read by two coders (Cohen kappa 0.944 over 212 definitive pairs), 178 by a third coder. 15 marked uncertain and set aside, leaving 174 Stage-A and 218 Stage-C narratives. Five outright opposite calls settled by the study lead; original readings retained.
- Validation sample stratified on the model's own probability (ambiguous band 0.30 < p <= 0.95 over-sampled, random tail draws), Horvitz-Thompson weighted back to hit population (Section 3.3; Table C.1). Stage-C positives and borderline narratives adjudicated as a census.
- Role and outcome: three coders read a random 300 driver-role confirmations and all 58 fetal-harm candidates, each twice; agreement before adjudication 96.7% (role), 96.6% (outcome) (Section 4.1).

## n, sampling, intervals
- Weighted sensitivity 0.999 [0.997, 1.000], specificity 1.000 [1.000, 1.000], PPV 1.000 from 174 Stage-A narratives (Section 3.3; Table 3). Unweighted sensitivity 0.9932 (146 TP, 1 FN, 0 FP, 27 TN; Table C.2). Specificity rests on only 27 true negatives; bootstrap draws it from a Jeffreys posterior.
- 2,000-draw single bootstrap chain, resampling validation within stratum (Section 3.3).
- Additional checks: chi-square homogeneity of nine annual Stage-C screens chi2 = 6.52, 8 df, p = 0.59; worst-case assignment of 15 unsettled rows gives sensitivity no lower than 0.9973, specificity no lower than 0.9714; 546 narratives scoring >= 0.10 read blind with zero misses (Section 4.1).

## Calibration
- No ECE or Brier. Figure 3 panel (a) compares mean model probability to weighted adjudicated share per decision group: "conservative" (observed further from threshold than stated); panel (d) shows coder agreement lowest in the middle probability bins (Section 4.1). No post-hoc recalibration. Calibration is asserted partly through a companion paper (Introduction).

## Cost, latency, hardware
- Not reported beyond the statement that the corpus can be read "on ordinary research infrastructure" (Introduction).

## Cascade or escalation
- None. The regex screen to model to human audit pipeline is a sampling design, not a model escalation.

## Option-name, cardinality, language, robustness
- Call-composition test (above). Per-year versus pooled screen-miss rate: 142 versus 148 missed cases (Section 4.1). No option-name or language tests.

## Test-set exposure
- Private Texas CRIS narratives not released (Data and code availability); outcome not a public benchmark, so exposure to training is unlikely.

## Code and data
- MIT-licensed schema, async runner, analysis scripts, adjudication tool and coder instructions at https://github.com/pozapas/pregnancy-crash-narratives. Narratives not releasable (TxDOT agreement, Transportation Code 550.065(c)). Residual identifiers survive two redaction passes in 43% (25 of 58) fetal-harm narratives (Section 3.1).

## Paper's own limitations (Section 5)
- Documentation is not prevalence; fetal harm undercounted; validation on a few hundred narratives; specificity 1.000 from 27 true negatives; Stage-C term rests on 42 candidates; no passenger denominator; expected counts from live births only; closed pinned model; one state.

## Notes for the grader
- Application and measurement-error study. Reference label type human adjudicated (low on domain 1).
