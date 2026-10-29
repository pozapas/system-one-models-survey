# wu2026poisoned

arXiv 2610.15537v1 (cs.CR), 11 Oct 2026. "Poisoned into Action: Context Attacks on Typed Decision Workflows."
Authors: Chenkai Wu (Monash University), Xing Chang (SUTD), Jun Yan (SHOU). Affiliation type: academic. (title block)
Note: an earlier ledger study wu2026reflex exists (different paper, different Wu). This key is wu2026poisoned.

## Task and data
- Execution-aware security protocol: poisoned evidence -> retrieval -> typed choice -> mechanical execution -> persisted sandbox state -> evaluator. Two synthetic workflows, document release and incident response, 10 tasks each (20 development tasks) selected from a development split by workflow-balanced public task hash. Three canonical actions per task. (Sec. 3.1, 4.1)
- Reference labels: synthetic, generated offline by fixed policy rules independent of Jev outputs; project owner approved split after mechanical audits; not a blinded multi-reviewer process; hash-checked private labels opened only for scoring. (Sec. 4.1)
- Tasks and the frozen carrier-payload pair were used in earlier development studies, so the study tests the measurement pipeline, not transfer to unseen text or families. (Sec. 3.2, 5.6)

## Decision model
- jev-1.13.0, hosted, System One Choice interface; version validated on parsed valid responses. Acquisition 07:31:04 to 07:47:22 UTC on 5 October 2026. 1,659 decision POSTs, 1,654 valid decisions, 5 format errors, no automatic retry. (Sec. 4.5)
- Only Jev evaluated (one model, one acquisition period).

## Comparators and tuning
- Within-study comparisons: ungated vs source-exclusion gate vs scope-aware repair (zero-call replay); probability-threshold gates (raw max probability 0.82, API confidence 0.73) with and without temperature scaling fitted on a historical calibration split (clean-only T = 0.151856545, mixture T = 9.786044907). Thresholds chosen from evaluation clean scores to match the source gate's clean coverage (44/60), descriptive not prospective. The scope-aware repair was designed after seeing gate failures (post hoc). (Sec. 4.3 CS5 CS6, App. A)
- No other decision model or LLM comparator.

## Design and uncertainty
- Conditions: CS1 channel (state, appended document, outer instructions) x content (neutral, opinion, semantic, command); CS2 evidence competition (correct evidence presence x payload x rank); CS3 natural retrieval (clean, carrier, payload, pair, neutral pair); CS4 repeat stability; CS5 gating; CS6 calibration. Three draws per task and condition; 60 planned draws per cell. (Sec. 4.3)
- Request queue, primary contrasts, hashes frozen before acquisition; three prespecified contrasts, Holm corrected, none significant. Unit is the task (20), bootstrap 5,000 resamples of tasks, sign randomization. Supplemental rules saved after 394 responses were acquired, exploratory. (Sec. 4.4, 5.4, 5.6)
- Draw-level rates are descriptive, not independent-task intervals. (Fig. 2 caption)

## Headline results (per 60 planned draws unless noted)
- Instruction channel semantic: 60/60 wrong executions, 30 security violations, 30 with API confidence >= 0.8. State channel semantic: 10 wrong, 2 unavailable. Appended document semantic: 0 wrong. (Sec. 5.1, Table 2)
- Natural retrieval: payload alone reaches 60/60 draws, 5 wrong executions (all security violations, three incident tasks); carrier-payload pair payload visible in 57/60, 1 violation; errors have API confidence 0.19 to 0.29. (Table 4, Sec. 5.2)
- Evidence competition: semantic arm wrong execution 119/120 without correct reference vs 55/120 with; neutral arm 60/120 vs 0/120. (Table 3)
- Source gate: clean correct 44/60 (original), 56/60 (scope repair), ungated 60/60; pair correct 49/60 gated, zero wrong; 16 correct clean decisions withheld by original gate, 12 restored, 4 withheld. (Table 5)
- Coverage-matched replay at 44/60 clean: pair correct 49 (source gate), 46 (max probability, API confidence, clean temperature), 44 (mixture temperature), 10 (pristine sensitivity); all zero wrong. (App. A.2, Table 8)

## Calibration
- Temperature scaling transfer measured with negative log likelihood (NLL), not ECE or binning. Clean-only T improves natural clean NLL 0.1279 -> 0.0007 and pair 0.1900 -> 0.0468 but worsens instruction-semantic NLL 2.2525 -> 13.5138; mixture T lowers the latter to 1.0195 while raising natural clean NLL to 0.6836. Positive temperature scaling preserves the argmax. (App. A.1, Table 7)
- Repeat stability: clean draws all 60 correct; cyclic pairwise total variation mean 0.022, median 0.010, max 0.110. (Sec. 5.4)

## Cost and latency
Cost not reported in money. 1,659 requests; acquisition window about 16 minutes 18 seconds (07:31:04 to 07:47:22 UTC); counterfactual gate calls add acquisition cost. No latency metric. (Sec. 4.5, 5.5)

## Cascade or escalation
Not a model cascade; gate withholds execution (selective execution). Results as above.

## Robustness
Input surface (state/document/instruction) and speech act (neutral/opinion/semantic/command) effects; evidence presence; rank placement; natural retrieval. Option-name and cardinality tests not done (cites other studies).

## Test-data exposure
Synthetic private worlds generated from rules; tasks previously used in development; not in any public benchmark (labels private, hash-checked). Items new to model training.

## Code and data
Code available at https://github.com/WuXixiong/jev-poisoning-bench. (Abstract)

## Authors' limitations (Sec. 5.6)
20 development tasks from two synthetic templates; frozen pair not a new attack family; one model version in one acquisition period; threat models differ across arms and should not be pooled; no human review, multistep recovery, real authorization; five malformed responses lack raw fields; no equivalence margin; thresholds use evaluation clean scores.
