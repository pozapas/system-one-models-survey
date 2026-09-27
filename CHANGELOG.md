# Changelog

Both releases describe the literature and ecosystem as of the same cutoff, 2026-09-24.

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
