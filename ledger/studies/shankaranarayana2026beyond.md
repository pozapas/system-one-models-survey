# shankaranarayana2026beyond: Beyond Answer Confidence, a controlled audit of self-knowledge in a black-box decision model

## Identification

- arXiv 2610.01006v1, cs.AI, 01 Oct 2026 (header). Full text: fulltext/2610.01006.html and .txt.
- Authors: Sharath M Shankaranarayana, Davor Runje, Jan Jannink. Affiliation: Synthpop.AI (title block). Affiliation type: industry (independent of the model vendor; no vendor tie stated).

## Task and data

- A behavioural audit of whether a decision model's confidence reflects missing knowledge. About 575,000 calls (575,442 paid calls, 573,234 feeding reported analyses) across 15 public datasets and 6 generated task families (Abstract, Section 1, Appendix D).
- Main studies (Section 3): intent dose-response on Banking77 (770 test items, 77 intents) and CLINC150 (1,500 items, 150 intents) with opaque codes; 480 generated knowledge-by-chance questions; knowledge boundary (PopQA by popularity, 1,600 fabricated-entity questions, Daily Oracle yes/no news questions Jan 2020 to Jul 2026, 3,360 questions in the balanced panel); evidence in context (HotpotQA, Quizbowl, 600 generated policy cases); random devices (dice, coins, cards over all option orders). Appendix C adds TriviaQA, SimpleQA Verified, TruthfulQA, MMLU-Redux, MMLU-CF, ANLI, SelfAware, AmbigQA, ChaosNLI, out-of-scope detection.
- Free-text benchmarks were converted to four-option Choice (Section 3).
- Test-set exposure: public benchmarks (pinned revisions in Table 14, public before 2026) plus new generated items. Dated news runs to July 2026, which the authors use as the post-cutoff probe.

## Decision models evaluated

- Jev. The API exposes only aliases; the authors requested jev-latest and every response reported jev-1.13.0 (collection 26-30 September 2026; surface-cue controls and verification variants run on 30 September) (Section 3). Choice (up to 255 named options), Noul yes/no, Score (up to ten ordered levels). Each cell queried three times; the mean distribution is analysed. Replicate SD about 0.04 near p = 0.5; probabilities quantised to 0.01 (Section 3). Input $0.042 per million tokens, output free at the time; costs estimated from token counts, not invoices.
- Open comparator on the opaque-code probe only: GLiNER2.5-Decide (Fastino, model card created 23 September 2026, revision 7ee5da4c) (Section 4.1, reference [12]). A deep ensemble is used in Appendix C.3.
- No LLM comparators; this is a case study of one version of one closed model (Limitations).

## Tuning-budget parity

Not applicable for the audit. The follow-up questions are fixed wordings; fourteen rewordings tested (AUROC 0.87-1.00 for the relevant contrasts, Appendix C). Thresholds for the answer-filter comparisons were set on held-out questions.

## Reference labels

Benchmark answer keys (human-made), real-world news outcomes (Daily Oracle), and synthetic generated items with known ideal distributions. The date-removal answer-preservation labels (240 pairs) were provisionally annotated by one AI assistant under a written protocol (Section 4.1, Limitations).

## n, sampling design, intervals

- Metrics: top-label SmoothECE, AUROC, normalised entropy, total variation. Intervals: 95% item-clustered bootstrap (month-clustered for dated news) (Section 3). Several controls and robustness analyses were added after the main studies (exploratory); the equivalence margin of 0.05 was chosen after the main studies (Section 4.2, Limitations).
- "Calibrated" is defined as SmoothECE at most 0.05 on the closed-choice form (Section 3).

## Key results

- Confidence is calibrated on familiar closed-choice tasks: CLINC150 SmoothECE 0.015-0.025 at informative levels, PopQA 0.020-0.033 per popularity quintile, MMLU-Redux 0.016, TriviaQA 0.031, SimpleQA Verified 0.051, TruthfulQA binary 0.041 (Section 4.1, Appendix C). Banking77 with 8 examples SmoothECE .037 (Table 2).
- No information: Banking77/CLINC150 opaque codes give p_max .32/.36 against ideal .013/.007; the open GLiNER2.5-Decide gives .017/.010; fair die 0.80 on "one" against ideal .17; fabricated entities 0.52 against uniform reference .25 (Table 3).
- Knowledge boundary: after the change point, accuracy 0.511 at confidence 0.816 (gap +0.305, n = 1,680; Table 12); abstract range 0.21-0.33. Jev answers "no" to 92% of post-boundary questions against 61% before while the true share is about 51%; log loss 0.71 against 0.69 for always 50/50. Forward recalibration on earlier months leaves 0.19-0.23 overconfidence; no order-preserving map brings period-conditional error below 0.047 (Section 4.1, Table 6).
- Follow-up questions (Table 1): settled AUROC 1.00 (answer uncertainty 0.96 only via mode concentration); enough 0.95 (confidence 0.85, text length 0.65); known 0.88 to 0.91 on the original contrasts but 0.74 with look-alike names and 0.58 with dates removed (answer uncertainty 0.76 and 0.56); a text-only classifier separates the original contrasts at 1.00 and 0.997.
- Stated chances: Choice puts 0.98 on the 40% outcome of a stated 40/30/20/10 draw; one yes/no question per outcome is within 0.030 mean absolute error of the stated chance, and rescaling to sum to one gives 0.012 (Section 4.4, Table 4).
- Escalation-like result: a "not known" answer option beats a confidence threshold at matched coverage by +0.051 [0.016, 0.092] when half the questions lie past the boundary, +0.010 [-0.002, 0.043] at 27%, and -0.034 [-0.045, -0.005] at 5% (Appendix C); a rule skipping the most recent dates comes within 0.01-0.02 of it.
- Call-count robustness: a single call's SmoothECE stays within 0.010 of the three-call value in all 36 calibration sets (Section 3, Table 5).

## Option-name, cardinality, language, robustness tests

Intent-code swaps (opaque codes, name, examples, swapped examples where Jev follows the swapped mapping in 90% / 98% of items); CLINC150 with 5 to 150 options (Figure 8b); all 720 option orders for dice (tied stated chances follow mention order 99.6%, not display order); fourteen question rewordings. English only.

## Cost and latency

Estimated cost only (input $0.042 per million tokens, output free). No latency reported.

## Code and data availability

https://github.com/Syntheme/beyond-answer-confidence (Abstract, Code availability). Cached responses ledger in Appendix D; datasets with pinned revisions in Table 14.

## Authors' own limitations (Limitations section)

One version of one closed model; surface-cue controls and recalibration bounds added after the main studies and reuse the same news panel (not replicated on a fresh panel); the knowledge boundary is an accuracy change point, not a verified training cutoff; date removal can alter propositions; fabricated-entity questions have no valid answer; vendor does not specify whether a Choice models the realised outcome or the best answer; follow-up answers are rankings, not probabilities; no cost-based utility or deployment routing policy evaluated.
