# Changelog

Releases v1.0 and v1.1 describe the literature and ecosystem as of 2026-09-24. Release v1.2 moves the cutoff to 2026-10-28.

## v1.2.1 (2026-10-29)

This release adds the second rating of the v1.2 sweep and its adjudication. The cutoff is unchanged.

- **Second rating.** Ten second raters, blind to the first rating, screened all 249 candidates of `ledger/candidates_v12.csv`, rated the five risk-of-bias domains for all 215 studies graded in v1.2, read 295 extracted values from their sources and coded 38 decision heads. The guide, the returned workbooks, the key used to score them and the agreement are in `ledger/second_rating_v12/` (scripts `make_second_rating_v12.py` and `second_rating_agreement_v12.py`).
- **Adjudication.** Every disagreement was decided by the authors against the full text in `ledger/second_rating_v12/Adjudication_v12_returned.xlsx`, and `apply_adjudication_v12.py` applied the decisions. Each changed rating records the adjudication in its reason, and `adjudication_log_v12.md` lists every decision. The rating rules written for the cases the anchors left open are at the end of `ledger/PROTOCOL.md`.
- **New studies.** Six papers excluded at screening were included at adjudication and extracted into `ledger/parts/ledger_V23.csv` to `ledger_V28.csv`, graded in `ledger/parts/rob_G14.csv` and `rob_G15.csv`, and selected in `ledger/selection_parts/sel_S09.csv` and `sel_S10.csv`. `ledger/ledger.csv` now holds 3,519 rows from 250 studies, 248 of them graded.
- **Corrections from the raters' notes.** Row L3299 names the model of its value (Qwen3.5-35B-A3B), the liu2026timesjev rows name the printed Overall column, and row L1333 has a complete value key. No value changed.
- **Census.** Three decision heads are recoded from pair scoring to option markers under the adjudicated shared-pass rule (`census/head_check_H2.csv`, `head_check_H4.csv`).

## v1.2 (2026-10-28)

This release adds a second literature sweep and extends the census to the new cutoff. No existing ledger value was changed.

- **Sweep.** Every arXiv query of v1.0 was rerun over submissions from 2026-09-14 to 2026-10-28, with added queries for the models released after the first cutoff (`ledger/scripts/sweep_v12.py`). New records and their screening are in `ledger/candidates_v12.csv`.
- **Ledger.** Rows L1000 to L5311 extract the included papers under `ledger/EXTRACTION_BRIEF_v12.md`, and `ledger/ledger.csv` now holds 3,396 rows from 244 studies.
  - Every excerpt of the new rows is checked against the paper's full text (`ledger/excerpt_check_v1.2.csv`); repairs are logged in `ledger/excerpt_repairs_v1.2.md`.
  - Rows L934 to L949, added after the first cutoff, are now kept in `ledger/parts/ledger_Y.csv` so that a merge reproduces them.
  - `ledger/SCHEMA.md` adds the label types `mixed` and `not_reported` and an `other` calibration quantity.
- **Risk of bias.** All 242 studies with ledger rows are graded in `ledger/rob.csv` under the written anchors (`ledger/GRADING_BRIEF_v12.md`). The second rating of v1.1 covered the first sweep only.
- **Synthesis.** The new selection lines are in `ledger/selection_parts/`. `ledger/comparator_class.csv` codes the comparator of every accuracy contrast, coded twice (once blind to results) and adjudicated; the split by class was added after the first synthesis of this release.
- **Census.** `census/census_screened_v12_final.csv` adds 2,645 Hugging Face entries created to 2026-10-28, with every rule-tiered original implementation checked by hand (`census/t1_check_C*.csv`). `census/census_github_screened_v12.csv` adds GitHub repositories, and `census/hosted_models_v12.csv` records the hosted and vendor models released after the first cutoff.

## v1.2 (2026-10-11)

This release narrows the repository to what reproduces the reported results. No answer, result or ledger value changed.

- **Removed manuscript tooling.** Scripts that built manuscript packages, LaTeX tables and manuscript figures, checked the manuscript text and references, or generated the Colab notebooks were removed, together with internal run notes and audit outputs of the manuscript text. The notebooks themselves, every analysis script and every result file remain.
- **`collect_numbers.py`** now writes only `results/analysis/numbers.json`, and `b03_licenses.py` keeps only the dataset license audit.
- **Paths.** Local cache paths default to `~/.cache`, and provenance strings point to files inside this repository.

## v1.1 (2026-09-27)

This release adds the revisions made while the two manuscripts were prepared. The cutoff is unchanged.

- **Second rating.** An independent second rater repeated the screening of all arXiv candidates, a random sample of 40 ledger values and the risk-of-bias ratings of 8 studies.
  - Written rating anchors for all five risk-of-bias domains were added to `ledger/PROTOCOL.md`.
  - The authors adjudicated every disagreement. Six ratings changed in `ledger/rob.csv`, each with a note in its reason field, and `ledger/rob_counts.json` was updated.
- **Ledger.** Three rows were appended; no existing value was changed.
  - L934 and L935 add the second frontier arm and the calibration test of rafe2026calibrated.
  - L936 supersedes L491 with the full breakdown by card position.
  - The extractor field now names the extraction batch.
- **Census.** this-that-model 1.0 to 1.2 are reclassified as domain fine-tunes of decider-2b. There are now 101 original implementations in 67 families and 259 derivatives.
- **Benchmark.**
  - New analyses and results: revision statistics, conventional baselines on every task family, distractor permutations, the Laya token budget, rendering comparisons, backbone controls, a second open comparator and the license audit.
  - New and updated harness scripts.
  - New answer files. `results/answers/SHA256SUMS.txt` now covers every answer file.
- **Data licensing.**
  - The D3 texts are not redistributed. `harness/inputs/d3_item_ids.json` and `harness/src/s00b_prepare_d3.py` rebuild them.
  - `DATA_LICENSES.md` states the terms of each dataset.
- **Titles.** The READMEs carry the final titles of the survey and the benchmark paper.

## v1.0 (2026-09-24)

This is the first release: the census, the evidence ledger, the benchmark harness and the results at the cutoff.
