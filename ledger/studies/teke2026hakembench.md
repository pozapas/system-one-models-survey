# teke2026hakembench: HakemBench, a Turkish benchmark of typed decisions

## Identification

- arXiv 2610.02293v1, cs.CL, 01 Oct 2026 (header); dated October 2026. Full text: fulltext/2610.02293.html and .txt. (Key `teke2026ufakzeka` already exists for the companion model paper; this is the benchmark paper.)
- Author: Sait Furkan Teke, ufak AI (furkan@ufakai.com). Affiliation type: industry. Conflict: ufak AI's own model ufakzeka-karar is on the board (7th); its numbers are not blind (Section 6). Self-funded: US$236.90 for benchmark and model together (Section 8).

## Task and data

- Benchmark of typed decisions: Turkish text (state), one or more questions (choice, yes/no "noul", score), model returns a probability for every option. v1.0 open set: 2,346 items and 4,275 questions (1,605 choice, 1,715 yes/no, 955 score) in seven tracks: fact-check triage (305 items), education (320), guardrails (418), legal routing (308), moderation (353), spam and phishing (307), customer support (335) (Table 1). Frozen 26 September 2026, released 1 October 2026 under CC BY 4.0.
- Sources: 305 parliamentary sentences (TBMM); 181 Constitutional Court application summaries (test split of a public dataset) plus 127 written court-routing scenes; 28 guardrail items from two public prompt-injection sets; 1,832 items written by various LLMs from briefs (Section 3). Names of living people masked.
- Splits: part A (1,198 items) and part B (1,148), no sibling across parts; post-hoc temperature fitted on part A (2,166 questions); A-minus-B macro-F1 gap flagged above 0.10; no model hit the flag.
- Probes: permutations (10,038 items; 521 of the 1,605 choice questions), paraphrase (162), English translation (131), slot substitution (423 items on 215 part A items) (Section 4).
- Test-set exposure: new items, but open release with no hidden test set; protection rests on a canary string and the slot signal (Section 4). Items written by LLMs.

## Gold labels

- Mostly AI-made: one AI model family answered every question blind in several passes (one with web search by topical keywords), a stronger model of the family made another blind pass; where the build-process proposal (panel of two or three LLMs from two other families, source label or writer intent) and all passes agree that is gold; disagreements settled by a model of the same family; "every pass agrees" means at most two independent votes (Section 3.1). Subjective scales (fact-check triage, message type) re-decided by an AI model under a written procedure derived from the human answers; customer support gold from two blind passes under a rubric written into the options; Constitutional Court items use the court's record (181); 260 questions have human-decided gold by the author (252 owner-blind, 5 owner-chose, 3 consistency pair); 84 human-check questions are not gold (Table 2).
- Gold source counts (Table 2): ai_ensemble_unanimous 1,659; ai_rubric_agreed 1,157; ai_owner_reading 829; ai_ensemble_adjudicated 111; writer_family_adjudicated 39; ai_rubric_adjudicated 37; owner_blind 252; source_label 181.
- Human audits (single annotator, the author): gold differed from human answers on 3 of 53 objective and 39 of 90 subjective questions; re-decided subjective gold agreed with a re-audit on 54 of 62; support rubric gold agreed with 88 of 119 human answers (Section 3.1). The author does not call the gold human-verified. Coded model_consensus; human-check and human-gold rows coded human_single.

## Models evaluated

Hosted: Gemini 3.8 Flash, GPT-5.6 Sol, GLM 5.3 (structured probability answers), DeepSeek V4 Pro (option-label log-probabilities), Jev 1.13 (hosted typed-decision endpoint, own probabilities). Queried between 23:56 UTC on 26 September and 03:21 UTC on 27 September 2026. Open: Kev 4B and 9B, Laya (two checkpoints, each at shipped and full input length), decider-2b, open-jev (DeBERTa-v3-large; truncates to 256 tokens, no option descriptions), Qwen3.5-4B through an open decision server with no calibration (read through option-letter probabilities, so position and letter bias mix), the lab's ufakzeka-karar (options scored blind to each other, so order sensitivity zero by construction), and a surface-cue baseline (Section 6). 16 rows. Exact revision strings are not given for the open models in the text read.

## Tuning-budget parity

All models are scored on the question text exactly as in the files with shipped temperatures; for customer support the option descriptions include the gold rubric. Hosted models differ in elicitation (stated probabilities vs log-probabilities), acknowledged as a source of calibration differences (Section 6). Axes are computed on raw answers; post-hoc temperature is fitted per model on part A and reported (T column). Hosted chat models have no probe rows. ufakzeka-karar's data shaped by reading test results in guardrails, moderation and customer support (flagged).

## Scoring and intervals

Macro F1 (decision quality); calibration = 1 minus Brier divided by the uniform-guess Brier, floored at 0 (smooth ECE reported per track in the board file); selective automation = 1 minus AUGRC divided by the all-wrong value, floored at 0; composite = equal-weight geometric mean of the three axes averaged over tracks. 95% intervals from 2,000 bootstrap resamples over items (an item's questions drawn together). Written items from one generation request are correlated, so intervals are likely too narrow; no bootstrap over writer requests (Section 7).

## Key results

- Table 3 composite (rank): Gemini 3.8 Flash 0.888 [0.876, 0.898]; GPT-5.6 Sol 0.842; GLM 5.3 0.827; Jev 1.13 0.825 [0.811, 0.837] (decision quality 0.851, calibration 0.706, selective automation 0.935, median 135.0 ms, human check 0.762, human gold 0.665, T = 1.1058); Kev 4B 0.688; Kev 9B 0.666; ufakzeka-karar 0.660; Qwen3.5-4B 0.653; DeepSeek V4 Pro 0.633; decider-2b 0.491; Laya multilingual 0.298 / 0.275; surface-cue baseline 0.272; open-jev 0.234; Laya 0.081 / 0.075. The ranks 5, 6, 8 and 9 intervals overlap that of ufakzeka-karar.
- Jev's probes (Table 4): order sensitivity 0.039 [0.029, 0.050]; paraphrase agreement 0.926 [0.889, 0.963]; English gap 0.009 [-0.031, 0.045]; slot signal 0.059 [0.020, 0.107], which the author says may point to contamination but does not prove it; robustness 0.943.
- Fact-check triage is hardest (leader 0.768 macro F1, every other row at or below 0.619). Surface cues alone separate six options with balanced accuracy 0.75 to 0.87 (Section 6).
- Human check (84 questions): four leaders 0.738 to 0.786, surface-cue baseline 0.619 (partly in-sample); human-decided gold: top nine rows 0.642 to 0.704.
- Cost and latency: median per-question milliseconds on different hardware (Mac CPU, NVIDIA L4, GPU, network) so not comparable across rows; not in the composite.
- Calibration reporting: Brier-based axis plus per-track smooth ECE in the board file; post-hoc temperature T per model (Jev 1.1058; DeepSeek V4 Pro 4.7382; Laya 3.33 to 4.33).
- Cascade: none.

## Code and data availability

Data and card https://huggingface.co/datasets/ufakai/HakemBench; harness, scorer and board https://github.com/ufakai/hakembench; board recomputation and lab model https://github.com/ufakai/ufakzeka-karar; weights https://huggingface.co/ufakai/ufakzeka-karar; write-up https://ufakai.com/research/hakembench. Every board model's rows on open items and the 84 human-check answers are public; a recomputation on another machine gave the same ranking.

## Authors' own limitations (Section 7)

Gold mostly AI-made by one model family with disputes settled by that family; all human answers from one person (no inter-annotator agreement); subjective scales and six surface-cue options; written text by models may favour models trained in their style; guardrail source stratum only 28 items; correlated written items make intervals too narrow; no hidden test set; hosted models differ in elicitation; parliamentary coverage 2011 to 2023.
