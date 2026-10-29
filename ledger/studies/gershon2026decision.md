# gershon2026decision

arXiv 2610.28826 (PDF fetched 2026-10-28; no HTML version exists; version label not printed on the PDF). "Decision language models as affordable and rapid alternatives to LLM judges of clinical generative AI." First public version 2026-10-20 (batch screen).
Authors: Rotem Gershon, Seffi Cohen, Dean Ariel, Havatzelet Bilavsky-Yarden, Amiel Sberro, Shai Yitzhaki, Osnat Tausky, Naama Golan, Maayan Rabinovitch, Ariel Avraham Hasidim, Itay Arianu, Maya Dagan, Ran Balicer, Noa Dagan. Affiliations: Clalit Research Institute and Clalit Health Services (Ramat-Gan), Ben Gurion University of the Negev, Schneider Children's Medical Center, Tel Aviv University, Harvard Medical School collaboration. Affiliation type: academic (health-system research institute plus universities; no vendor authors). (title page)

## Task and data (four use cases; Fig. 1, Methods)
- Use case 1: 118 Hebrew answers of a deployed pediatric retrieval-augmented decision-support system, graded on six rubrics plus total score (ordinal 1 to 5, and binary pass/fail); Jev and the new LLM judges graded English translations (gpt-4o-mini, temperature 0). Reference: panel median of five physicians. (Methods, Use case 1)
- Use case 2: HealthBench meta-evaluation set (release 2025-05-07), 29,511 rows from 3,671 conversations, 34 criteria, 60,896 labels from 186 physicians; Jev answers one yes/no question per criterion. (Methods, Use case 2)
- Use case 3: MedHELM v4.0.0, 45,384 responses of 13 models scored on accuracy, completeness and clarity by a three-LLM jury; 56 clinician-rated responses (ACI-Bench 31, MEDIQA 25; 13 clinicians) give the only human reference. (Methods, Use case 3)
- Use case 4: HealthBench Professional (April 2026), 525 physician-written responses, 1,135 criteria; no physician labels, reference is GPT-5.4 (gpt-5.4-2026-03-05, low reasoning effort), the benchmark's default grader. (Methods, Use case 4)

## Decision model and comparators
- Jev: jev-1.13.0, version pinned, through the TypeSafe API; all runs 13 to 18 October 2026; three runs per use case (stability), analyses use the first run (use case 2 uses the majority of three runs). Score questions for ordinal scales, yes/no for binary (choice questions avoided because of documented first-option bias). Two readings of ordinal scores: most probable level and expected score. List price US$0.042 per million input tokens, output free. (Methods; Ext. Data Table 3 note)
- LLM judges: GPT-6 (gpt-6-astra), Claude Opus 5.5 (claude-opus-5-5), MiMo-V2.6-Pro, GLM-5.3, gpt-oss-120b (all use cases); plus seven published judges (use case 1), GPT-5-nano (gpt-5-nano-2025-08-07, use case 2), the MedHELM jury (use case 3), GPT-5.4 (use case 4). Each LLM judge received the use case prompt template unchanged, no labels. Claude Opus 5.5 and GPT-6 graded only a stratified half sample (1,837 conversations, 14,775 rows) in use case 2. Open-weight judges via hosted API (OpenRouter). Tuning parity: same prompt template for all judges; Jev prompts reproduce original role, scoring instructions and anchors with only structural edits (Supplementary Note 2). (Methods, LLM judges)

## Statistics and intervals
Gwet AC2 (quadratic weights) and AC1, macro F1, ICC(3,2), Spearman, percentage agreement; 95% percentile bootstrap CIs (2,000 resamples of answers in use case 1, conversations in use case 2, the 56 responses in use case 3; 1,000 of responses/criteria elsewhere), paired differences, fixed seeds; no multiplicity adjustment for per-rubric comparisons. Authors note CIs in use cases 3 and 4 may be too narrow (shared inputs). (Methods, Comparisons between judges)

## Test-data exposure
Use case 1 is a private institutional dataset (earlier npj Digit Med study; data on request). Use cases 2 to 4 are public (HealthBench 2025, MedHELM, HealthBench Professional April 2026); authors state Jev's undisclosed training may have contained them. (Discussion, Limitations)

## Cost and latency
Billed tokens at October 2026 prices; Jev US$22 to US$89 per million judgments, frontier judges 73 to 294 times as much, open-weight judges 1.1 to 163 times, MedHELM jury about 184 times (estimate). Jev median 0.12 to 0.55 s per request; frontier judges 7 to 57 times longer, open-weight 31 to 190 times. Timing is client wall-clock from a cloud container in the central United States, six concurrent requests for LLM judges and 16 for Jev and GPT-5.4 in use case 4; not all timings comparable. Costs of the seven published judges are input-token lower bounds. (Results, Cost and time; Table 1; Ext. Data Table 3)

## Calibration and deferral
No ECE or recalibration. Confidence-based deferral: Jev score confidence cutoff 0.5 (use cases 1, 3) and |2p-1| at 0.4 (use cases 2, 4); at these cutoffs Jev kept 68% (UC1), 67% (UC2), 88% (UC4) of judgments, agreement rose (UC1 AC2 0.57/0.60 vs 0.50/0.53; UC2 macro F1 0.735 vs 0.665; UC4 95.0% vs 90.8%). (Results, deferral)

## Cascade or escalation
Hybrid: Jev judgments below confidence 0.4 replaced by an LLM judge. Hybrids added at most 0.04 AC2 (UC1, UC2) and 1.0 to 1.8 points (UC4) at 1.2 to 76 times Jev's cost; in UC2 the hybrids lowered agreement; safety-only routing in UC1 raised sensitivity for physician-failed safety answers from 31% to 49% (Claude Opus 5.5) and 51% (GPT-6) at about a third of their cost. (Results, hybrid; Discussion)

## Option-name, cardinality, language and robustness
Three-run stability: AC2 0.99 to 1.00 (UC1, UC3), identical labels 97.7% and 98.8% (UC2, UC4). Original Hebrew answers differed by at most 0.03 AC2 (Supplementary Table 9). Expected-score reading versus most probable level compared. No option-order test for choice questions (not used). (Results; Limitations)

## Code and data
Outputs and code at https://doi.org/10.5281/zenodo.23491933; use case 1 ratings on request.

## Authors' stated limitations
Use case 1 from a single institution and graded in English translation; use cases 2 to 4 public data possibly in Jev's training; use cases 3 and 4 measure agreement mainly with LLM graders; three of 13 MedHELM models also served as jurors. Jev returns no rationale. (Discussion)
