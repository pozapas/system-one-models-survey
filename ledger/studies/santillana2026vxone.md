# santillana2026vxone

arXiv 2610.30090v2 (cs.CR), v2 dated 24 Oct 2026 (the fetched version); first public version 2026-10-21 per the batch screen. "VX-One: Typed, Calibrated Decision Heads for Real-Time Perimeter Triage." (title block)
Author: Juan S. Santillana, independent research. Affiliation type: independent. (title block)

## Task and data
Network and malware triage on tabular features: UNSW-NB15 (149,039 / 26,302 / 82,332 flows; 9 attack families), CIC-IDS2017 (2.83M flows, stratified and by-day splits), EMBER2024 (3.85M binaries). Labels are benchmark capture or ground-truth labels (CIC with documented label errors, audited variant used); severity scores are rubric-derived family-to-level mappings, not human labels. Leave-one-attack-family-out, temporal drift, a Suricata plus VX-One cascade over five CIC days. (Sec. 4, 5, 6)

## Own model (VX-One)
Small multi-head MLP (100K to 10M parameters) with gate, choice (closed set plus unknown or abstention) and ordinal score heads, per-head temperature calibration, trained per dataset. This is a fixed-classifier analogue of the typed primitives (heads are not caller-declared questions), so rows for it are kept few and used mostly as comparator to the vendor models. Baselines: calibrated XGBoost, RF, MLP, Kitsune with the same feature stage and calibration protocol; three seeds; paired bootstrap B=300. (Sec. 3, 4, App. A)

## Commercial decision models (Sec. 5.6, Table 7)
Jev SKU jev-1.13-free ("the same model as the commercial SKU, served through a zero-metered access tier") and Microsoft Decision-1 (Azure AI Foundry deployment decision-1, preview), zero-shot, one API request per flow with the three primitives over the identical frozen feature state, 2,021 stratified UNSW test rows (1,000 benign, 1,021 attack), seed 42. Jev gate AUROC 0.568 versus Decision-1 0.544 versus VX-One 0.981; gate ECE15 0.265 / 0.118 / 0.097; choice macro-F1 0.069 / 0.066 / 0.534; severity MAE 0.809 / 0.969 / 0.333. Jev latency 208 ms p50, 591 ms p95; Decision-1 757 ms p50, 20.4 s p95 (preview cold starts); Jev run about 2.2M input tokens, US$0.09. Repeat variance: Jev N=5 over a 451-row subsample AUROC 0.597 +/- 0.017, 1.1% argmax flips; Decision-1 N=5 over 2,041 rows AUROC 0.540 +/- 0.002, 13.1% flips. Adding an explicit unknown option to Jev's choice question gave gate AUROC 0.476 and macro-F1 0.066. Dates of the vendor runs: "this cycle" (October 2026), no exact days. Tuning: vendors zero-shot, VX-One trained on the dataset (stated limitation).

## VX-One headline results
UNSW gate AUROC 0.9837 +/- 0.0002 versus MLP 0.9835 +/- 0.0013 (three seeds, tie); CIC by-day 0.734 +/- 0.022 versus XGBoost 0.639 +/- 0.027; calibrated XGBoost wins attribution on all three benchmarks; ECE 0.04 to 0.40 under temporal drift for every method; CPU single-event latency p50 about 0.7 to 1.7 ms; cascade by-day wave-day recall 0.339, precision 0.971. (Abstract, Sec. 5.1, 5.4, 6)

## Calibration
15-bin ECE, MCE, Brier, NLL; per-head temperature scaling; walk-forward recalibration and isotonic maps tested (App. A, E8, E9).

## Test-data exposure
Public pre-2026 benchmarks (UNSW-NB15 2015, CIC-IDS2017, EMBER2024).

## Code and data
https://github.com/vectrayx/vx-one and https://huggingface.co/jsantillana/vx-one (code, results, weights).

## Authors' limitations (Sec. 6)
Rubric-derived severity labels; benchmark data and leave-one-family-out not real zero-days; single-seed outside main tables; Phase 1 is a reference implementation; calibration under drift; conformal wrappers not promised; cost per million not measured; vendor comparison is two vendors on one distribution (dense UNSW flows).
