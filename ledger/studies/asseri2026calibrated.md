# Asseri & Asseri (2026), "Calibrated to Whom? Persona and Language Effects on Cultural Values in JEV"

Coder: batch V04. Full text: fulltext/2609.36399.html and .txt. The text read is arXiv **v2** (03 Oct 2026); the first public version is 2026-09-28 (batch file).

## Identification
- arXiv 2609.36399v2 [cs.CL]. CC BY 4.0.
- Authors: Bushra Asseri (College of Engineering and Advanced Computing, Alfaisal University, Riyadh; Proxa.sa, Riyadh) and Abdulaziz Asseri (Proxa.sa) (author block). Affiliation type: mixed.

## Task and data
- Audit of the cultural values a decision-only model reports, using the 24 content items of the Values Survey Module 2013 answered by 12 matched Saudi and 12 matched American personas (country alone, with gender, with age, or both) plus a no-persona baseline, in English and Arabic (Section 3.2, 3.3).
- 1,200 prompts x 30 repeats x 8 request set-ups = 288,000 answers; 36,000 answers per set-up (Section 3.3). Headline set-up is the "documented" one: persona in the state, item and five labelled options in a Choice question.
- Reference: the Saudi-minus-US difference in Hofstede country scores (Hofstede Insights 2022; Hofstede et al. 2010), 94.3 index points long, used "as a reference benchmark ... not as a target"; an alternative Saudi profile from Almutairi et al. (2021). These come from unmatched samples, periods and survey versions (Section 3.2). Coded human_crowd (aggregated survey scores) with that caveat. Item-level reliability and confidence rows have no reference.
- Test exposure: new prompts; published VSM 2013 items and Hofstede scores are public.

## Decision model
- "We sent all requests to TypeSafe's API and asked explicitly for version jev-1.13.0, which every response reported. The data were collected on 28 and 29 September 2026" (Section 3.1). Choice and Score question types. Probabilities returned with two decimals and renormalised. No temperature or seed parameter.

## Comparators and tuning parity
- No comparator model. The comparison is within Jev across eight request designs (documented, chat-style prompt, no format sentence, Score, Score reversed, third person, 24 items per call, other-language framing; Table 1) and against Hofstede's scores. Every finding was re-estimated in all eight set-ups.

## Results (documented set-up unless stated)
- Reliability: ICC of expected answer over 30 calls 0.997 (0.995 to 0.998 in other set-ups); most probable option identical in all 30 calls for 83 to 89% of prompts; mean confidence 0.49 to 0.58 across set-ups (Section 4.1).
- Default without persona lies at 0.08 (English) and 0.06 (Arabic) on the American (0) to Saudi (1) persona axis, 61.5 and 111.0 index points from the American and Saudi centroids in English (Section 4.2).
- Share of the Hofstede Saudi-US difference covered along its direction: 87.1% English (95% CI 80.5 to 93.9), 62.0% Arabic (56.3 to 67.9). Relative discrepancy from the reference: 62.3% (58.5 to 67.6) English, 59.9% (55.8 to 64.2) Arabic. Long-term orientation reversed: -33.0 points (-40.6 to -25.4) against Hofstede +10 (Sections 4.3, 4.4).
- Language cross: Arabic items lower the share by 29.5 points (26.1 to 33.1); Arabic framing changes it by -3.9 (-8.9 to 1.5) (Section 4.4).
- Confidence in Arabic lower by 0.090 (two-way cluster bootstrap 0.048 to 0.132) (Section 4.6). Rank test: four of six dimensions in Hofstede order in both languages, mean tau 0.33 (Section 4.8).
- Across set-ups the English share ranges 87.1% to 106.8%, the Arabic share 42.1% to 72.2%; direction of the national difference preserved in all eight (Section 4.7).

## Sampling design and intervals
- Repeated calls are not independent; the unit of replication is the matched persona profile (12 pairs). Intervals are 95% t-intervals across profiles or percentile bootstrap (4,000 resamples) over profiles; they exclude translation error, persona-wording variation and error in the reference scores (Section 3.6). Analysis exploratory, not preregistered.

## Calibration
- "Calibrated" in the title refers to the vendor's description; no probability calibration against human answer distributions is tested. The paper says confidence "measures the model's certainty, not the agreement among people" and names World Values Survey or Arab Barometer comparison as the next step (Section 5.5). No post-hoc calibration; no cascade.

## Robustness
- Eight request set-ups and a language cross are the core robustness tests (Section 3.4, 4.7). One Arabic translation only.

## Cost
- Appendix F reports a total run cost and token counts for the authors' own run; not extracted.

## Code and data
- "The prompts, all responses and the analysis code will be released" (Ethical Considerations; Appendix F). No URL; coded partial.

## Authors' stated limitations (Limitations section)
- One version of one model with undisclosed training; one official Arabic translation; Hofstede scores from unmatched samples and periods, partly extensions or estimates; intervals cover only 12 constructed personas and 24 items; exploratory analysis; other request formulations may give other effect sizes.
