# Zhang, Wang, Wang & Feng (2026), "Decide, Don't Generate: Competitive Dimensional ABSA with Jev's Typed Decisions"

Coder: batch V04. Full text: fulltext/2609.35293.html and .txt (arXiv HTML v1).

## Identification
- arXiv 2609.35293v1 [cs.CL], 28 Sep 2026.
- Authors: Yiqun Zhang, Peidong Wang, Zihan Wang, Shi Feng; Northeastern University, China (author block). Affiliation type: academic.

## Task and data
- SemEval-2026 Task III (DimABSA) Track A: Task 1 given-aspect valence-arousal regression over ten corpora in six languages, Task 2 triplet extraction and Task 3 quadruplet prediction over eight corpora (Section 1, 4.1).
- Test sets: Task 1 has 9,658 reviews and 16,186 aspect annotations; Tasks 2 and 3 share 6,690 reviews with 14,262 triplets and 14,263 quadruplets (Section 4.1).
- Reference labels: the official gold annotations; how the annotators worked is not described in this paper, so coded human_single provisionally.
- Test exposure: public Track A splits ("We use the public Track A splits", Section 4.1); the paper states test labels were used only for evaluation. Whether labels predate Jev's training is not addressed; coded unclear.

## Decision model
- "We use jev-1.13.0 with the official data and scorer" (Section 4.1). Choice, Noul and Score interfaces.
- No text is generated. Task adaptation is "488 coefficients fitted on CPU" (100 in Task 1 ridge models, 332 in Task 2 rerankers, 32 pair-level VA maps, 24 category fusion), using training labels, except the Task 2 reranker which uses development labels (Sections 3, 4.1, Appendix B). The system therefore uses labeled data; it is not zero-shot.
- BM25 retrieved annotated examples are placed in the Jev state for Task 2 checks and Task 3 category questions.

## Comparators and tuning parity
- Table 1 compares with six SemEval participant systems whose aggregates the authors reconstructed from per-corpus scores in Yu et al. (2026), plus Llama-3.3-70B and GPT-OSS-120B (4-bit QLoRA) and one-shot Kimi K2 Thinking from Lee et al. (2026). The comparators differ in backbone, supervision and tuning; the paper says the comparison "places our results in context rather than isolating the effect of generation" (Section 4.2). No comparator was run by the authors.
- Development data selected all design choices and thresholds (Section 4.1).

## Results
- Task 1 micro RMSE 1.0645 (PAI 1.0663; Llama-3.3-70B QLoRA 2.5683; GPT-OSS-120B 1.2362; Kimi K2 one-shot 1.8873). Raw uncalibrated scores 2.0731. The 0.0018 margin to PAI "cannot be tested for significance" (Section 4.2).
- Task 2 macro cF1 52.09 (best published complete-coverage PAI 57.73; Llama 46.40; GPT-OSS 45.71). Task 3 cF1 44.06 (PALI 49.20; Llama 38.62; GPT-OSS 37.27). Table 1.
- Per corpus (Table 2): Jev system beats the best published score on English laptop and Tatar restaurant only for Task 1; trails elsewhere.
- Ablations (Table 3): removing calibration +1.0086 RMSE; removing the reranker -15.31 exact-match pair F1; removing the model category decision -6.03 cF1. Gold VA would add +4.46 cF1 to Task 2. Category accuracy on matched pairs 85.0 (Table 2).
- Table 4: 21.7% of gold pairs never proposed, 26.8% proposed but not selected (macro, Section 4.4).

## Sampling design and intervals
- Single run on the official test sets, no intervals for headline numbers. A paired bootstrap 95% interval is given only for a development-set ablation (joint terms, -0.0506 [-0.0626, -0.0395]; Section 4.3).

## Calibration and cascade
- Supervised calibration of Jev's rubric scores is part of the method (ridge map), and it roughly halves RMSE (Abstract, Table 3). It is a regression fit against benchmark labels, not a probability calibration analysis (no ECE or Brier). No cascade.

## Cost and latency
- Not reported (searched for latency, cost and API terms).

## Robustness
- Six languages and four domains are covered by corpus (Table 2). No option-order or option-name tests.

## Code and data
- Code: https://github.com/ZhangYiqun018/jev-dimabsa (first-page footnote).

## Authors' stated limitations
- No limitations section. The comparison caveats above are in Section 4.2.
