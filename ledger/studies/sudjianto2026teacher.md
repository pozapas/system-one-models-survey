# sudjianto2026teacher: Teacher Supervision, Fixed Representations and Calibration: Exact Risk Calculations for Candidate-Scoring Decision Models

arXiv:2610.26797v1 [stat.ML], 19 Oct 2026 (HTML title block; fulltext/2610.26797.html and .txt). Extractor batch V18.

## Authors and affiliation
Agus Sudjianto, Denis Burakov, dated October 2026 (title block). No affiliation, email or funding statement appears in the HTML text, so affiliation type is not determinable from the paper; coded independent. No code or data repository for this paper is given (a companion book repository by Burakov is cited as a reference, https://github.com/deburky/inference-machines-book).

## Task and data
Mostly theory: exact finite-sample risk of least squares and probit students trained on teacher targets, fixed representations, recalibration, and Luce-axiom coherence (§§2 to 6), with Monte Carlo checks (§7). The only empirical decision-model section is §8 (application). Credit card complaints from the CFPB Consumer Complaint Database narratives archive (up to 14 August 2026), closed with monetary relief, non-monetary relief or explanation; 231,521 complaints in total. Splits by year received: 37,520 (2015 to 2018) train the teacher; 97,835 (2019 to 2023) train the students (each student n=64,000 from 93,835, 4,000 held out for early stopping); 34,957 (2024) for calibration (5,000 used); 61,209 (2025 to 2026) test, of which a fixed 10,000 are scored in every model (§8.1). 1,088 narratives occurring in more than one split removed. The share with monetary relief is 0.206 in teacher years and 0.166 to 0.169 in the test years (§8.1, Table 4 caption).

## Decision models evaluated
All are typed-decision-style readers rather than the hosted product:
- "the method published as a local Jev [8]": Qwen2.5-0.5B-Instruct, next-token distribution renormalised over lettered options, fixed threshold (§8.1; the reference is a blog post by D. García "Build your own Jev (100% local)", 21 September 2026). Not the hosted Jev and not versioned.
- Qwen3-30B-A3B-Instruct read zero-shot as a lettered choice and renormalised, served with vLLM (§8.1). No revision hash.
- "Students" following the JevAny design: Qwen2.5-0.5B with rank-8 LoRA adapters, a linear score at each candidate closing bracket normalised over the candidates, one student trained on company responses (outcomes), one on the teacher probabilities (soft cross-entropy), questions with two or three options in random order (§8.1, Figure 2).
- Two fixed representations (frozen Qwen2.5-0.5B mean-pooled last layer; word2vec) with logistic heads trained on outcomes (comparators, not typed models).
- Teacher: multinomial logistic regression on TF-IDF word and bigram features with company and issue indicators (the scorecard analogue).
Each complaint read with three options and with two options, each in two orders, averaged over orders.

## Comparators and tuning-budget parity
Constant forecast at the 2024 rate; teacher (recalibrated on 2024 with a Tasche rank-based curve); Qwen3-30B recalibrated on 2024 with the same curve fitted on 5,000 calibration complaints. Students and fixed representations are reported without recalibration. One training run per student and one training size (§9). Zero-shot readers receive no tuning; the teacher and students are trained on thousands of labelled complaints, so tuning budgets are far from matched, which the paper treats as the design (it is a study of training ingredients).

## Reference labels
The company's closing decision on each complaint (monetary relief or not). The paper notes the label "encodes the company's policy as well as the content of the complaint" (§9). Coded administrative_field.

## n and sampling
10,000 fixed test complaints from 2025 to 2026; paired bootstrap 95% intervals over complaints on Brier differences and per-1,000 decision cost differences; calibration slope fitted on 2024 data (§8.2, §8.3). "The separation of the two students at this n rests on one training run each" (§8.3).

## Test-set exposure
Public archive; the test complaints were received 2025 to 2026, partly after the likely training cutoffs of the models, but the complaints are public and no contamination check is reported. Coded unclear.

## Cost and latency
Not reported. "Cost" in the paper means decision cost per 1,000 complaints under an asymmetric loss (an unneeded escalation costs c, a missed relief 1-c), not compute cost.

## Calibration
Brier score relative to the unknown true probability via difference in Brier between models on the same complaints; Turing's check E(V)=1 (V is odds against the realised outcome); calibration slope of the outcome on the logit of the forecast; decile reliability plots (Figure 3a). Post hoc: rank-based robust logit curve of Tasche (quasi moment matching on 5,000 2024 complaints) for the teacher and Qwen3-30B. Results (Table 4): Qwen3-30B zero-shot mean forecast 0.509 against 0.169 observed, Brier 0.364, Turing mean V 219 (dominated by confident wrong forecasts), calibration slope 0.128; after recalibration Brier 0.137 and mean V 0.96, still worse than the teacher by 0.0133 Brier (0.0101 to 0.0166). Turing's check passes the constant forecast (0.99) and the 0.5B letter reading that ranks at chance (0.95, AUC 0.48) and fails the best student (1.70).

## Cascade or escalation
Not a cascade. The decision rule escalates a complaint when forecast exceeds cutoff c (c=0.2 and 0.3); cost per 1,000 complaints at c=0.2: constant 135.4, letter reading 0.5B 164.3, Qwen3-30B zero-shot 100.2 and recalibrated 100.7, teacher 90.0, student on outcomes 82.7, student on teacher 89.6.

## Option-name, cardinality, language, robustness
Coherence under refinement of "no monetary relief" into two subevents (three-option vs two-option set): Qwen3-30B departs from the Luce condition by 17.5 decibans (mean probability 0.51 with three options, 0.31 with two); the 0.5B letter reading by 5.0 decibans; students by 0.20 (teacher-trained) and 0.69 (outcome-trained). Reversing option order moves the letter reading's answer by 0.40 on average and students' by 0.007 and 0.012 (§8.3).

## Code and data
CFPB data public. No code release for the experiments stated.

## Authors' own limitations (§9)
One training run per student and one training size; label encodes company policy; models lie outside the Gaussian, probit and fixed-representation assumptions so §8 tests direction only and "their values do not carry over"; LoRA adapters make the representation label dependent and are not covered by theory; the proposed serialization-perturbation test on a fixed tabular record is run only as a version (wording and order of candidates), and the paper does not predict the outcome of the comparison with a frozen embedding plus calibrated classifier.

## Notes for the grader
The headline empirical claims (student on outcomes 8% below teacher cost at c=0.2; recalibrated 30B model worse than teacher; 17.5 decibans) come from a single seed on 10,000 test complaints. The paper does not evaluate hosted Jev; the "Jev" readings are a 0.5B local imitation and the JevAny training design.
