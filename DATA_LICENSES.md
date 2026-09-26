# Licenses

## Code

All code in this repository (`harness/src/`, `harness/colab/`, `ledger/scripts/`) is released under the MIT License. See `LICENSE`.

## Curated data

The census cards and screens (`census/`), the evidence ledger, the risk-of-bias ratings and the synthesis (`ledger/`), and the analysis results (`results/analysis/`) are released under the Creative Commons Attribution 4.0 International License (CC BY 4.0). Excerpts quoted in the ledger are short passages from the cited works, included for verification, and remain the property of their authors.

## Third-party benchmark inputs and model answers

`harness/inputs/` redistributes the D1 and D2 inputs in the frozen form the harness builds, with attribution. The four D3 tasks are not redistributed. `harness/inputs/d3_item_ids.json` lists their item identifiers, and `harness/src/s00b_prepare_d3.py` followed by `harness/src/s00_freeze_inputs.py` rebuilds the frozen files from the original sources, whose SHA-256 digests are listed in `harness/inputs/manifest.json`. The files in `results/answers/` hold item identifiers and probabilities, not the input texts.

| Dataset | Used as | Upstream license | In this repository |
|---|---|---|---|
| LocalLLaMA/typed-decisions | D1 | Apache-2.0 (dataset card at the evaluated revision c76749ec and at every later revision) | Redistributed. The option keys were renamed to neutral identifiers (`o1`, `o2`, ...) and the native keys kept in `d1_native`; this is a modification of the original files |
| CLINC-150 (clinc_oos) | D2 | CC BY 3.0 | Redistributed with attribution. The benchmark adds a fixed option permutation, neutral keys and three distractor permutations |
| Conversations Gone Awry (ConvoKit), via Ziems et al. (2024) | D3 | Wikipedia talk-page text, CC BY-SA | Item identifiers and rebuild script only |
| Wikipedia Politeness (ConvoKit), via Ziems et al. (2024) | D3 | CC BY 4.0, as stated on the ConvoKit page | Item identifiers and rebuild script only |
| Wikipedia talk corpus (ConvoKit), via Ziems et al. (2024) | D3 | CC BY-SA 4.0, as stated on the ConvoKit page | Item identifiers and rebuild script only |
| dair-ai/emotion | D3 | For educational and research purposes only, per the dataset card | Item identifiers and rebuild script only |

The D1 inputs are derived from LocalLLaMA/typed-decisions, licensed under the Apache License, Version 2.0 (https://www.apache.org/licenses/LICENSE-2.0). The D2 inputs are derived from CLINC-150 by Larson et al. (2019), licensed under CC BY 3.0 (https://creativecommons.org/licenses/by/3.0/). `harness/inputs/D3_README.md` gives the per-task details and sources, and `results/analysis/licenses_audit.json` records the license check behind this table. In `results/analysis/clinc_overlap.json` the quoted emotion examples are removed and only their item identifiers are kept.

Third-party model and repository cards quoted in `census/cards/` and `harness/colab/cards/` belong to their authors.
