# Loi (2026), "The Argument and the Letterhead: Source-position coherence in AI evaluation: two studies and a preregistered Jev supplement"

Coder: batch V04. Full text: fulltext/2609.35286.html and .txt (arXiv HTML v1).

## Identification
- arXiv 2609.35286v1 [cs.AI], 28 Sep 2026; CC BY-NC-SA 4.0 (header).
- Author: Michele Loi. No affiliation appears in the extracted text (checked byline and document); coded independent, affiliation not stated.
- The study was conducted by an AI system under the author's direction (Abstract: "documents the human decisions and delegated checks behind an AI-conducted study").

## Task and data
- Descriptive audit of whether AI evaluators rate the same argument differently when its attributed source changes. Six fixed texts (US AI policy, Germany's debt brake, Swiss nuclear energy) under several attributed organisations; the key statistic is the interaction I = (gap on text A) - (gap on text B) between two sources (Section 2, Appendix A).
- Jev portion: US Study 1 (24 Sep 2026; 4 sources x 2 texts x 32 ratings = 256 Jev ratings, Appendix A.2) and a later European supplement (26-27 Sep 2026; 18 cells x 16 ratings = 288 usable ratings: 160 German, 128 Swiss; Section 1, Appendix A.4). Total across all systems 2,976 ratings.
- Reference label: none. The study measures source sensitivity, not accuracy.
- Test exposure: new, constructed stimuli and attributions. Topic selection was partly informed by earlier explorations (Section 1).

## Decision model
- Jev through the `typesafe-ai/jev` alias, native scoring request with a five-anchor rubric scored 0 to 4, divided by 4 for plotting (Appendix A.2). Version: "the presumed underlying version was 1.13.0, based on documentation checked for collection, rather than a provider-verified snapshot returned with each score" (Appendix A.2); "Jev 1.13.0 remains a documentary presumption rather than a verified served snapshot" (A.4).
- Routing: 266 final responses from TypeSafe AI and 22 from DigitalOcean (A.4). The routing varied during collection.

## Comparators and tuning parity
- Chat models: GPT-4o, Sonnet 4.5, Gemini 3.5 Flash (Study 1), plus GPT-6 Sol and Sonnet 5 in the extension; chat models were asked for a 0 to 1 argument-strength rating plus strongest point, weakest point and overall assessment. Instructions differ from Jev's native rubric, so cross-system comparison is not parity-controlled; the paper says the Jev panel "cannot establish an impartiality ranking against chat systems" (Figure 2 caption).

## Results (Jev)
- US interactions on the 0-1 scale: CODEPINK - College Republicans -0.0197, Carnegie - AEI -0.0030 (Appendix B.3; Section 4.1). Chat comparators on CODEPINK - College Republicans: Sonnet 4.5 -0.319, Gemini Flash -0.449, Sol -0.301, Sonnet 5 -0.154 (Section 4.1).
- European interactions (Table 2): DE GJ - JL +0.0102, DE DIW - IFO +0.0014, DE AfD - JL +0.0080, CH JG - JF -0.0061, CH SES - AV -0.0314; all five below the adopted 0.05 descriptive reference (Section 4.4).
- Native score concentration: 1.80 to 2.43 for US responses, 2.03 to 2.31 (Germany) and 2.00 to 2.37 (Switzerland), modal level 2 (Appendix A.2, Section 4.4). Earlier neutral checks reached 0 and 3.87-3.89.

## Sampling design and intervals
- Preregistered descriptive design (first two studies registered before collection; the Jev supplement planned after earlier outcomes were known, Section 1). Randomised block order, first usable rating per cell. Six operational amendments, two ratings admitted by retrospective eligibility review, 57 HTTP 429 and two HTTP 403 failures, multi-day interruptions (Appendix A.4).
- US Study 1 has post hoc p-values (Appendix B); "No new p-values, confidence intervals, equivalence tests or provider-effect estimates were computed for this supplement" (Section 4.4). Planned-half splits only.

## Calibration and cascade
- Not evaluated. The paper states the results "do not demonstrate that Jev is unbiased, equivalent across sources, or better calibrated" (Section 4.4). Jev returns score, probabilities over rubric levels and confidence, with no written explanation (Section 5.2).

## Robustness
- Source-pair and topic variation; reasoning on/off for Sol and Sonnet 5 only. No option-order or language tests for Jev.

## Code and data
- Preregistrations, materials and frozen code public in the Petri_studies releases (https://github.com/MicheleLoi/Petri_studies; Jev supplement tag `preregistered-source-attribution-jev-europe-descriptive-v1`). Raw API records held in a private archive (Availability section).
- The paper reports a planning-cost ledger of the author's own spending (Appendix A.3); not extracted.

## Authors' stated limitations
- Rubric, score concentration, service timing, serving route and retrospective eligibility decisions limit the comparison of Jev with chat systems (Section 4.4, Appendix A.4); source label is the only manipulated factor and credibility, authenticity and expected position are not separated (Section 5.1).
