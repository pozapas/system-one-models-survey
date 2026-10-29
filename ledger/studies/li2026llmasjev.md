# li2026llmasjev: LLM-as-Jev, LLMs are already Jev-style decision models, when and how to fine-tune them

## Identification

- arXiv 2610.02076; first public version 2026-10-01 (screen file). The HTML retrieved on 2026-10-28 is v3, "arXiv:2610.02076v3 [cs.CL] 13 Oct 2026". Numbers extracted from v3; v1 and v2 were not inspected, so differences are unknown. Full text: fulltext/2610.02076.html and .txt.
- Authors: Yinheng Li and Justin Wagle; contact email yinhengli@microsoft.com (affiliation line not given beyond the email domain). Affiliation type: industry.

## Task and data

- Own-model paper. Turns a causal LLM into a Jev-style decision model: options rendered as "[k]" identifiers, candidate suffix scored by summed log-probabilities after the prefix "Best answer: [", softmax over candidates (Section 3). Training-free recipe plus a fine-tuning recipe (tree-factorised listwise loss with three KL anchors, Section 3.4). A "Thinking Jev" variant allows a budgeted thinking block before the readout (Section 4.5). Output is a probability distribution over declared options in a few forward passes, so it meets the decision-model definition.
- Evaluation (Section 4.1): seven external benchmarks (BoolQ, MMLU, MMLU-Pro, ARC-C, WinoGrande, SciQ, Banking77) with full candidate sets; JevBench public items (231, v1.4.2.2, Benchmark Heaven; easy, standard, hard); general capabilities (GSM8K, IFEval, TriviaQA, LAMBADA, WikiText-2); multimodal MMBench and MMStar; conversational stability on Dolly-15k and MT-Bench. Reference labels for JevBench are not described in the text read (recorded "not reported").
- Training data: public human-annotated datasets only, no teacher or synthetic labels, filtered for 13-word n-gram overlap with evaluation benchmarks (Section 3.5, Appendix E). Training mixtures were developed with error analysis on public JevBench samples, so the authors call the Section 4.3 evaluations exploratory; JevBench was excluded from hyperparameter tuning and checkpoint selection.
- Test-set exposure: external benchmarks are public pre-2026; JevBench public items are 2026 and partly visible to the authors through error analysis (recorded unclear); the JevBench sealed split (308 items) is private.

## Decision models evaluated

- LLM-as-Jev on Qwen3.5-4B (thinking disabled except in Section 4.5) and Qwen3-0.6B, six training configurations at 4B and five at 0.6B (Table 7), no revision strings.
- Community baselines run with official implementations (SemIf, reflex 4B, open-alternative-jev, Winnow-12B) and GPT-5.6 Sol (generation, no reasoning); reruns reproduce official leaderboard results within four items (Section 4.1). Other community models (Plumb-4B, decider-4b v2, JevK5, Cygnet, Hopper, Imajev-4B, LLM2Jev, jqv, Kev-0.6B, Decision Fast) and Jev 1.13.0 appear only in Table 15 with figures from the evaluator or projects, accessed 2026-09-28 (LLM2Jev 2026-10-04).
- Jev 1.13.0 itself was not run by the authors: Table 15 lists JevBench public 86.6 and sealed 36.7; Table 17 lists Jev at 86.6 with $0.042 per million input tokens and free output.

## Tuning-budget parity

Comparisons against community models are of finished systems with their own training (frozen, LoRA, pointer heads, private teacher data). Same-backbone comparison with SemIf (frozen letter logits) is the cleanest. The authors' training mixtures were iterated using public JevBench error analysis (Section 3.5). Significance via two-sided exact sign tests over diverging predictions.

## n, intervals

JevBench public n = 231 (188/231 correct for the training-free 4B); sealed n = 308 with chance about 29.3%. No confidence intervals; won/lost counts and sign-test p-values (for example 313 wins vs 154 losses for macro external accuracy against SemIf; 13 wins vs 7 losses for LoRA vs training-free on JevBench).

## Key results

- Table 1 (JevBench accuracy / hard / ECE; External macro; Banking77): GPT-5.6 Sol generation 94.4 / 88.3 / - / 91.5 / 86.0; Winnow-12B 86.6 / 74.8 / .058 / 82.2; 4B training-free 81.4 / 64.9 / .057 / 78.6 / 69.0; 4B fine-tuned 80.1 / 61.3 / .070 / 78.9 / 75.2; 4B LoRA 84.0 / 68.5 / .050 / 78.9 / 75.4; 4B generation 81.4 / 64.9 / - / 78.4 / 68.5; SemIf 80.5 / 60.4 / .061 / 75.4; reflex 4B 79.7 / 59.5 / .070 / 78.8; open-alternative-jev 75.8 / 59.5 / .108 / 75.5; 0.6B training-free 56.7 / 33.3 / .278 / 57.9 / 22.2; 0.6B fine-tuned 58.0 / 37.8 / .118 / 59.1 / 60.5; 0.6B LoRA 61.0 / 39.6 / .121 / 58.5 / 59.0. Inconsistency: Table 1 gives Winnow-12B 86.6 on public JevBench whereas Table 15 gives Winnow-12B 85.7 and Jev 1.13.0 86.6; the Table 1 value may be a transcription error.
- Calibration: ECE with 15 bins on raw distributions without post-hoc scaling (Section 2, Appendix A); binning scheme (width vs mass) not stated. Training-free 4B ECE 0.057; intent-only tuning raises ECE to 0.134 with mean confidence in wrong answers 0.73 vs 0.60 (Appendix G).
- Fine-tuning: gains concentrate on seen domains (Banking77 +4.9 to +7.7 at 4B, +37 to +42 at 0.6B); intent-only training causes a "yes" bias and drops JevBench from 81.4% to 74.9%; unanchored 4B emits trailing text after the closing bracket in 69 of 231 queries, lambda = 1 gives none (Section 4.4).
- Thinking Jev: JevBench 84.8 / 89.2 / 91.8 / 94.8 at 512 / 1,024 / 2,048 / 4,096 thinking tokens (Table 17); the 4,096-token point was a supplementary run on another GPU (Figure 6 caption).
- Multimodal: MMBench CircularEval 82.4%, MMStar 64.6%; with images withheld 15.2% and 28.8%.
- Cost: FLOP-based model, not invoices: 4B readout $30 per million JevBench decisions, Jev $27, GPT-5.6 Sol $2,477 (API price on 2026-10-12, promotional through 2026-11-21); thinking at 4,096 tokens about $450 per million decisions; no wall-clock latency measured (Appendix L).
- Cascade: none.

## Option-name, cardinality, language, robustness tests

High-cardinality options (Banking77 with 77, CLINC150 with 151); prefix-free suffix design supports arbitrary K; random option shuffling during fine-tuning to counter position bias, with joint scoring "susceptible to option order"; tokenizer differences (digit grouping) in Appendix C including an option-10 isolation. English text only.

## Code and data availability

No code or model release statement or URL for LLM-as-Jev in the text read; the linked repositories are those of the baselines. Recorded as no. Training data are public datasets.

## Authors' own limitations

Not collected in a dedicated section in the text read. They state: the Section 4.3 evaluations are exploratory because data iterations were guided by public JevBench error analysis; joint contextual scoring has minor option-order susceptibility; latency and price depend on serving stack (so FLOPs are counted instead).
