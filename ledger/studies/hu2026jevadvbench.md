# hu2026jevadvbench — JevAdvBench: A Benchmark and Black-Box Attacks for Reinforcement Learning for Calibrated Decisions Models

arXiv:2609.31142v2 [cs.CR], v2 dated 26 Oct 2026 (first version 2026-09-25 per the batch file). HTML retrieved 2026-10-28 from https://arxiv.org/html/2609.31142; saved as fulltext/2609.31142.html and .txt. Numbers below are from v2 (the text cites sources accessed 19 Oct 2026, so v2 may differ from v1).

## Authors and affiliation

Jianyi Hu, Hangtao Zhang, Yi Liu, Yeqi Zeng, Li Zeng, Xianlong Wang, Rui Wang, Leo Yu Zhang (title block). Institute of Information Engineering CAS, Huazhong University of Science and Technology, Griffith University, Changsha University of Science and Technology, City University of Hong Kong, University of Chinese Academy of Sciences. Affiliation type: academic.

## Task and data

Adversarial robustness of typed decision models (TDMs) used in confidence-gated web services (Abstract, §1). Dataset: 862 clean questions over 71 scenarios in eight web-facing domains, 334 Noul, 357 Choice, 171 Score (§3.1, Fig. 2a). Starts from the TypeSafe documentation examples plus authors' own questions (§1). Twelve black-box attack methods in four families (Table 1) produce 7,802 candidate variants; an LLM answer-preservation review keeps 5,586 (Table 1, §3.4). Attacks are only counted on questions the model answers correctly when clean (§3.5); 461 variants dropped for wrong clean answers leave 5,125 evaluated (App. D).

## Decision models evaluated

- Target: TypeSafe Jev pinned at jev-1.13.0, "every response resolved to this version" (§4.1). Adaptive search against Jev only (§3.3, §4.1). Run dates are not stated; sources were accessed 18 to 19 Oct 2026 (references).
- Open TDMs receive the same variants once, no search (§4.1): Open-Jev-9B (rev 47e9668), Kev-4B (rev 139fdd9), Decider-4B v2.1 (rev eb5fbdf), StartLux-Decision v1.1 4B-Instant, Von 1.3 (rev 43bbca0), jevhome-ettin-1b (rev 3d0d41c), jevhome-E (rev d1415a6), CLM v0.1 (rev e939398); RL pairs decider-2b v8 (7789eb6) and v10 (d61c1c1), StartLux 4B-AutoThink (rev 23dd4c5) (References, App. E).
- Attack generator: DeepSeek Flash; review: three DeepSeek Flash votes with GPT-6.1 confirming each removal; Claude Opus 5.5 labelled 52 variants for an agreement check (§4.1, App. C).

## Comparators and tuning-budget parity

No baseline LLM judge is compared. Jev receives adaptive search with per-method query budgets (Table 1); open TDMs get only the transferred variants, so their ASRs are "lower bounds" (§7 Limitations). This is a disclosed asymmetry between target and transfer models. Adaptive vs single proposal is compared on 465 sampled pairs (§4.3).

## Reference labels

Fig. 2b and §3.1: people reviewed or adjudicated 185 labels (including 29 of 56 interval labels), a blind three-LLM consensus settled 41, an oracle computes the 50 multi-hop labels, and the remaining 586 labels are the model's own stable answers from ten repeated runs. A blind three-LLM consensus agrees with 584 of the 591 model-derived labels (98.8%); five of seven disputes were corrected (§3.1, App. C). So most labels derive from Jev's own answers, audited by LLM consensus. Answer preservation of variants is judged by an LLM review; agreement with Claude Opus 5.5 on 52 variants is 75.0% (kappa 0.14) for first review, 74.0% (kappa 0.41, n=50) strict, 69.2% for one GPT-6.1 vote, 65.2% for confirmations (App. C).

## Sampling and intervals

Each clean and attacked request is sent 3 times; eligible if at least 2 clean answers correct; success if at least 2 attacked answers wrong (§3.5, Eq. 6). Intervals are a 2,000-resample bootstrap over the 71 scenarios, seed 0 (App. D). Noise floor 0.17% (4 of 2,388 clean calls wrong; Wilson 95% 0.07 to 0.43%) (§3.5).

## Test-set exposure

Questions start from official TypeSafe documentation examples plus new authored questions (§1); variants are new. Public release after generation. No contamination check described.

## Cost and latency

No cost or latency in USD or ms reported. Query counts: 381,284 queries for eleven methods and 633,022 for L1 (§3.3); median queries per successful search 24 for contextual and hijacking, 578 for L1 (Table 5, §4.3).

## Calibration and confidence gating

No ECE or Brier. Confidence gate at 0.8: Jev coverage 58.7%, selective risk 23.5%, wrong automated actions 13.8% of attacked requests (Table 3, §4.5); at 0.99 Jev still has 7.9% wrong of executed answers with 37.7% automation (§4.5). No recalibration.

## Cascade or escalation

The confidence gate is the escalation mechanism (to a human): "Without attack, Jev keeps 99.4% of the answers that were confident and correct before the search above this gate"; under attack only 58.7% stay above it (§4.5).

## Option-name, cardinality, language and robustness tests

Robustness is the main subject: option order (S1) flips 2.4%, near-miss options (S3) 8.3%, evidence order (S2) 72.0% on 25 eligible questions (Table 5, §4.2). English only (no language test reported).

## Case study

Agentgateway v1.6.0 with its official Jev webhook (model name changed to jev-1.13.0): a DAN jailbreak is rejected in 3 of 3 clean trials (jailbreak score 2.5, HTTP 403); a C3 variant lowers the score to 1.8 and the request reaches the backend in all three trials (Fig. 5, §5).

## Code and data availability

Benchmark, requests, raw responses, analysis scripts at https://JevAdvBench.github.io/JevAdvBench/ (App. F, §1).

## Limitations stated by the authors

Adaptive search only against Jev to limit query cost; open TDMs get the variants once, so ASRs are lower bounds; nine of twelve methods edit the state, none edits the question instructions; no defences evaluated (§7).
