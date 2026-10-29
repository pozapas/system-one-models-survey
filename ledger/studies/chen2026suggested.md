# chen2026suggested

arXiv 2610.15710v1 (cs.AI), 11 Oct 2026. "Suggested Is Not Superseded: A Pre-Registered Evaluation of a System-One Model as a Memory-Retirement Gate."
Authors: Xupeng Chen (Dimension Gate), Chenqian Le (New York University). Affiliation type: mixed (company plus university). Competing interests: no affiliation with or funding from TypeSafe AI; Jev accessed through public API. (title block, Sec. Competing interests)

## Task and data
- Decide whether a new utterance retires a stored claim. Three-way contract: superseded, needs-confirmation, compatible. Gate action retire or keep. (Sec. 2)
- Data: pairs drawn from STALE (Chao et al. 2026, arXiv 2605.06527, public benchmark of 400 conflict scenarios), excluding scenarios touched in pilot. Split by scenario: dev (49 scenarios), test (179), sealed vault (63). Test n=500 pairs (179 change, 179 cross-session controls, 142 within-session controls); vault 176 (63, 63, 50). Test gold 72 superseded, 97 needs-confirmation, 331 compatible. (Sec. 3)
- Reference labels: three LLM annotators (A1 Claude Sonnet 5 via CLI, A2 Claude subagents, A3 GPT-6 Astra) with three-way majority gold; 72 test items human-labelled (one author for a 41-item first batch; second recruited annotator for 68 items whose first fill was done by a Codex agent running the A3 model, which was discarded, then relabelled by author and second annotator). Vault gold for 37 items with any superseded vote is the second annotator's labels. Authors call the 68 labels "a reading that two people confirmed after a model fill, not an independent human reading". Contract amended in eight dated addenda, three after human labels existed. (Sec. 3, Limitations)
- Exposure: STALE items are public (2026-05) but labels are newly made by the authors; Jev v1.13 (Sept 2026) postdates. Treated as new.

## Decision model
- Jev jev-1.13.0, run 23-24 Sept 2026 (dev and test) and 27 Sept 2026 (vault). S2 binary Noul (score in [0,1], retire at tau = .5); S3 three-way Choice with the contract's label names and definitions (developed on dev only); S3n neutral letter names; S3x definitions given another label's name. Each decision from one request, not re-sent. (Sec. 4, App. D)
- Vendor price cited: 0.042 USD per million input tokens (Sec. 1); no cost or latency analysed (Limitations).

## Comparators and tuning
S0 rule (cue plus word overlap), S1 MiniLM cosine >= .5 (cutoffs fixed before outputs), S4 Claude Sonnet 5 with contract text on change pairs only (shares family with annotators A1 and A2, which the authors say favours it). Jev three-way developed on dev; cascade M4 (keep if S2 < .3, retire if S2 >= .9, else ask S4) and threshold M5 (tau = .7) selected on dev among 26 candidates by the written rule (highest detection subject to P <= .15 and F <= .05). (Sec. 4, 6)

## Design and uncertainty
Pre-registered H1 to H3 (H1 within-session clause and scoring rules added in dated amendments after sampling but before human labels or outputs read). Wilson 95% intervals; exact McNemar tests, unadjusted. Gold revised twice for provenance after first scoring; no verdict changed under three readings of gold. (Sec. 2, 4, 5)

## Headline results (test n=500)
Jev binary Noul: detection 93.1 [84.8, 97.0], premature retirement 39.2 [30.0, 49.1], false invalidation 1.2 pooled, 0.0 within-session (0 of 141), AUROC 0.963. Three-way Choice: 77.8 / 15.5 [9.6, 24.0] / 0.9 / AUROC 0.957; detection loss 15.3 points (H3 budget 10 points missed). Same as threshold shift: S2 at tau .65 gives 79.2 / 17.5 (not pre-registered). S4 80.6 / 14.6 (n=89). H1 binary fails premature bar P <= .20; H2 not testable (11 items). (Table 1, Sec. 5)

## Option-name and robustness
Neutral names change 3.6% of S3 decisions, permuted names 10.2%; detection falls 77.8 -> 69.4 (neutral) and 51.4 (swapped) while AUROC stays within .01. Label-free option-prior division does not remove the name effect. (Sec. 5)

## Calibration
No ECE or reliability analysis; AUROC and threshold sweep only. Threshold (tau) shifts treated as post-hoc recalibration-like operating-point choice. (Table 1, Fig. 2)

## Cascade or escalation
Vault (held-out, second-annotator gold): cascade M4 (escalate [.3, .9) band to Sonnet; 22.2% of vault items escalated) reached detection 95.0 [76.4, 99.1] and premature 26.8 [15.7, 41.9], identical to simply raising threshold M5 (tau .7); S2 at tau .5 is 100.0 / 43.9. On dev M4 looked like 94.4 / 6.5 against M5 77.8 / 9.7. (Table 2, Sec. 6)

## Cost and latency
Not analysed. Vendor price 0.042 USD per million input tokens quoted from blog. (Sec. 1, Limitations)

## Code and data
"Will be released upon publication" (contract, item identifiers, labels, system outputs, code). Not yet available. (App. A)

## Authors' limitations (Sec. 8)
Single adjudicator per human-labelled item; gold on 428 test items is LLM majority (random audit overturned 5 of 20); H2 had 11 items; the three-way Choice was not run on vault; one model version, one English benchmark; hosted service near-deterministic, decisions not re-sent; vault spent; no cost or latency analysis.
