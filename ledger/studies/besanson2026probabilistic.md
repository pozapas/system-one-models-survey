# besanson2026probabilistic: Probabilistic Sensing, Deterministic Authority: Admitting Model-Produced Observations into Sufficiency-Checked Governance Contracts

arXiv:2610.10978v1 [cs.SE], 07 Oct 2026 (HTML header line). Full text: `fulltext/2610.10978.html` and `.txt`. Licence CC BY 4.0 (HTML header). Sixth paper of a single-author series on governance gates for automated actions (Sec 1). Extractor batch V26.

## Authors and affiliation

Gaston Besanson, Universidad Torcuato Di Tella (title block). Affiliation type: academic. Single author.

## Task and data

A model reads an unstructured evidence document (a synthetic change-management record) and reports what the document asserts about a field; an admission policy maps each score to true, false or unknown; a deterministic, sufficiency-checked contract then computes allow or deny (Sec 2, Sec 3, Figure 1). The sensor is asked only what the document asserts, never whether an approval is valid (invariant I2, Sec 3). Task family coded as extraction (reading a field from a document).

- E1 on CH-C1 (paper 5's 35-property domain, contract K): two sensed fields, `approval_assertion` (not_recorded or one of six registered dates) and `data_residency_region` (us, eu, apac); 27,000 reachable tuples, 1,000 items drawn (seed 20261101), validation split 300 (seed 20261102), test split 700 (Sec 6).
- E2 on CH-B1 (code and cloud domain): two seven-attribute reducts R_branch and R_env; arm 1 senses branch, arm 2 senses environment, both read the approval field; same 700-item test split per cell (Sec 6, Sec 7.4).
- E3 re-reads the E1 caches at ceilings 1% and 5%, with unknown routed to deny or to escalation; E4 runs two negative witnesses on 10,000 synthetic items each with no model; E5 measures calibration (Sec 6).
- Three noise levels 0%, 10%, 30%: each sensed statement independently made missing or contradictory (a comment asserting a different value is appended); noise nested across levels (Sec 6, "Documents and labels").
- Validation split divided once into split A (thresholds) and split B (error-rate estimates), 150 items each, seed 20261107 (Sec 5).

## Decision models evaluated

Jev, "System One, model jev-latest, returned as jev-1.13.0", from TypeSafe, one question per candidate value (Sec 6, "Sensors"); returned model strings jev-1.13.0 in both E1 and E2 (Sec 7, "Runs"). Questions are Noul (binary) questions asking what the record states, listed verbatim in Appendix B. No run dates in the text; the paper says run dates are recorded in the manifests (Sec 10, "Two sensor configurations").

## Comparators and tuning parity

Claude Haiku 4.5 (`claude-haiku-4-5-20251001`), a generative model prompted once per field to return a JSON object of probabilities; temperature zero, no system prompt, prefill `{`, max_tokens 64 or 128 for the CH-C1 approval field (Sec 6; Appendix B). Both sensors read the same documents (Sec 6) and get thresholds fitted by the same rule on split A at a 1% false-positive ceiling, 5% as ablation (Sec 5; thresholds in Appendix B). The interfaces differ (per-value binary questions versus one multi-value prompt per field), which is a disclosed asymmetry of request format, not of tuning budget. Haiku's `not_recorded` value on CH-C1 met the 1% ceiling in neither direction ("never true", "never false"), so that value can never be admitted and drives Haiku's high unknown rate on the approval field (Sec 7.2; Appendix B E1 thresholds). Design registered before any experiment code (prereg-p6-v1, then re-registered as prereg-p6-v1.1 after an external review; Sec 6).

## Reference labels

Synthetic. Each item gets a seeded synthetic record per noise level, never edited; each item and field has a truth label (the item's true value) and an assertion label (every value the record states, so a contradictory record asserts two values) (Sec 6, "Documents and labels"). Error rates and verdict exposure are scored against the truth label, so a faithful reading of a contradictory document counts as a wrong admission (Sec 5). The reference verdict is g(t) from the declared contract (Sec 2, "Exposure"). Thresholds and calibration use the assertion label (Sec 5, Sec 7.7).

## n, sampling and intervals

700 test items per sensor and noise cell; E1 4,200 test verdicts, E2 16,800 (Sec 7.3). 36,000 calls in total (12,000 in E1, 24,000 in E2) with 0 invalid replies (Sec 7, "Runs"). E1 rates carry Clopper-Pearson 95% intervals (Sec 7.2). Bounds are one-sided 95% Clopper-Pearson upper limits on split B (150 records), with a Bonferroni-adjusted simultaneous version beside each (Sec 5, Sec 7.2). H1 and four H2 tests with Holm's correction at alpha 0.05; H2 by exact McNemar test with item-clustered bootstrap intervals, 10000 resamples, seed 20261104 (Sec 7.8). Calibration on 21000 answers per domain and sensor (Sec 7.7).

## Headline results (Jev and Haiku on the same items)

- E1 per-field test-split rates at 30% noise: Jev approval wrong 0.0514, unknown 0.1714, residency wrong 0.0186, unknown 0.2700; Haiku 0.0400, 0.4014, 0.0100, 0.3071. At 0% noise Jev is 0.0000 on all four; Haiku approval unknown 0.2443 (Sec 7.2, per-field table).
- E1 verdict change rate: Jev 0.0000, 0.0429, 0.1071 at 0%, 10%, 30%; Haiku 0.0643, 0.0943, 0.1471 (Sec 7.2, E1 table). Unsafe (deny to allow) 1/700 for Jev at 30% and 0/700 in every other E1 cell (Sec 7.2).
- No cell's unsafe rate exceeded its registered bound B+ (H1 not refuted, Sec 7.2, Sec 7.8). Every B+ is at least 0.0395; where verdicts changed, B was 6.6 to 7.3 times the observed change rate (Sec 7.2). Haiku's B at 30% noise (1.0761) is vacuous (Sec 7.2).
- 13 of 21,000 test verdicts flipped deny to allow, traced to 3 contradictory records; in every flip the approval field was the only wrongly admitted field (Sec 7.3).
- E2: in both arms and for both sensors the rule picked the reduct that senses only the approval field; at 30% noise the picked reduct changed fewer verdicts in all four registered comparisons; H2 estimates Jev -0.1000 (arm 1) and -0.1029 (arm 2), Haiku -0.0657 and -0.0743 (Sec 7.4, Sec 7.8).
- E5 calibration against the assertion label: Brier Jev 0.0065 (CH-C1) and 0.0113 (CH-B1), Haiku 0.0142 and 0.0315; BSS from 0.8655 to 0.9566; Spiegelhalter test rejected calibration in all four cases (largest p 0.0003) (Sec 7.7).

## Test-data exposure

New. All documents are synthetic, generated per item from a seeded generator (Sec 6). Validation and test draw statements from disjoint phrase banks, but header lines, filler bank, noise templates, date set, names and layout are shared across splits (Sec 10, "Constructed corpora").

## Cost and latency

36,000 calls, USD 8.26 in total, both sensors pooled (Sec 7, "Runs"); a cap of USD 60 covered E1 to E5 (Sec 6). No per-sensor cost and no latency are reported. Provider: hosted TypeSafe and Anthropic interfaces (Sec 6; Sec 10).

## Calibration

Spiegelhalter Z test, Brier score and Brier skill score on test-split scores of every field and value question (Sec 7.7). Jev Z = -40.5181 (CH-C1) and -48.8080 (CH-B1); Haiku 7.1036 and -3.6214 (Sec 7.7 table). No binned ECE and no post hoc recalibration: thresholds are fitted on held-out data instead (Sec 7.7). Earlier probe jev-v1 also refuted calibration for Jev (Spiegelhalter Z = -15.0268) (Sec 7.1; quoted from tag jev-probes-final, not re-run).

## Cascade or escalation

E3 routes unknown to escalation instead of deny. At the 1% ceiling and 30% noise, Jev coverage 0.6000 with exposure among decided 0.0167 (versus 1.0000 and 0.1071 under deny); Haiku 0.4086 and 0.0175 (Sec 7.5 table). Raising the ceiling to 5% raised coverage under escalation in every cell below one; the unsafe rate did not move (Sec 7.5). Descriptive only, no registered hypothesis (Sec 7.5).

## Option-name, cardinality, language or robustness tests

Noise robustness at 0%, 10%, 30% (missing and contradictory statements) is the main manipulation (Sec 6). Admission ceiling ablation 1% versus 5% (Sec 7.5). No option-name, cardinality or language test; English templated documents only (Sec 10).

## Code and data availability

Repository archived at DOI 10.5281/zenodo.23224016, tag v1.0.1; raw responses committed in `responses/p6-E1.jsonl` and `responses/p6-E2.jsonl`; analysis reproduced byte for byte by an independent researcher (Sec 11; Acknowledgements).

## Authors' limitations (Sec 10)

Constructed corpora with shared surface regularities across splits; loose bounds (Clopper-Pearson floor, overlapping union terms, contradictory readings counted wrong); low power of H1; transfer from split B to test not ensured and marginal limits carry no joint level; one configuration of each sensor family; shared approval field makes E2 flips dependent; stamp enforcement covered by unit tests only; general proofs pending human review. The non-claims exclude any claim about Jev or Haiku beyond the tested configurations (Sec 9).
