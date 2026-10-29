# amit2026permutation: Permutation-robust decision modeling with candidate-independent block-causal attention

## Identification

- arXiv 2610.01601v1, cs.LG, 01 Oct 2026 (header). Full text: fulltext/2610.01601.html and .txt. License arXiv.org perpetual non-exclusive.
- Author: Guy Amit, Independent Researcher (title block). Affiliation type: independent.

## Task and data

- Own-model paper. A decoder-only transformer scores a variable-sized set of candidate actions serialized in one sequence and returns a softmax distribution over the displayed candidates in one forward pass, no generated text (Sections II-A, III). This fits the typed decision model definition (state plus declared candidate answers, probability distribution out). No Jev or other hosted model is run; Open-Jev is a dataset (Section IV; ref [7], Hugging Face dataset card, 2025).
- Primary data: Open-Jev typed-decision dataset with identical train, validation, test and OOD partitions for every architecture; test sets of 5,000 examples (Gemma 3 1B, Qwen3 1.7B) and 10,208 (Qwen3 4B); shared OOD set of 15,539 (Section IV).
- 250K artifact (Section VI): Qwen3-4B trained on 250,000 examples from six public sources (Open-Jev 79,116; xLAM 57,000; Aegis 2.0 30,007; ToolACE 10,700; repository prompt injection 5,387; WildGuardTrain 67,790). Validation balanced at 3,000 per source (18,000 total).
- Reference labels: not described in the paper. The target is a "categorical target over the displayed candidates" (Section II-A); label provenance is deferred to the dataset cards. Recorded as "not reported".
- Test-set exposure: all sources are public datasets released before 2026 (Open-Jev 2025, xLAM 2024, Aegis 2.0 2025, ToolACE 2024, WildGuard 2024); the prompt-injection repo dataset accessed Sept 2026. No contamination analysis.

## Models evaluated

- CI (candidate-independent block-causal attention) vs standard causal cross-encoder vs dual encoder, on Gemma 3 1B, Qwen3 1.7B and Qwen3 4B backbones (Sections III, IV). No version or revision strings for backbones; the 250K artifact is Qwen/Qwen3-4B, 4096-token context, 4,000 optimizer steps, BF16, 8-bit AdamW, seed 42, released as Guy-Amit/qwen3-4b-ci-decision-4096-poc on Hugging Face.
- Matched runs: two epochs, effective batch 64, BF16 backbone, FP32 heads and loss, same optimizer schedule, checkpoint with the lowest validation NLL (Section IV). Matched backbone runs use a 1024-token limit; the 250K artifact uses 4096, so scores are not interchangeable (Section VI).

## Tuning-budget parity

Matched capacity, data and recipe for causal vs CI (Section IV). The dual encoder is a frozen-backbone contrastive reference, explicitly not optimization-matched (Sections II, III, V-C). The 250K artifact has no causal comparison at that scale (Section VIII). One training seed per condition.

## n, sampling design, intervals

- Each held-out example scored in its original order and under five fixed permutations; predictions mapped back to canonical IDs (Section IV). Paired uncertainty by 5,000 group-level bootstrap resamples (seed 2026) respecting latent groups (Section IV). Table I reports point estimates only; intervals appear in prose for Qwen3 1.7B (Section V-B).

## Key results

- Table I (test accuracy / flip%): Gemma 3 1B causal 84.38 / 8.30, CI 84.66 / .11; Qwen3 1.7B causal 81.84 / 18.16, CI 84.96 / 1.20; Qwen3 4B causal 91.05 / 7.19, CI 92.22 / .67. OOD accuracy: Gemma 80.44 vs 80.71; Qwen 1.7B 75.09 vs 74.37; Qwen 4B 83.43 vs 83.83. OOD NLL is worse for CI on Gemma (.640 vs .723, causal better by 0.082), Qwen 1.7B and Qwen 4B (.738 vs .777).
- Qwen3 1.7B paired difference: accuracy +3.12 [+0.82, +5.63], NLL -0.039 [-.072, -.010], Brier -0.024 [-.045, -.004]; all OOD intervals cross zero (Section V-B). Results heterogeneous across candidate-count and source slices.
- Ablation (Gemma 3 1B, Section V-C): isolation-only cuts test flips 8.30% to 3.82% and OOD flips 7.54% to 3.71%; position-reset-only worse than causal (12.16% flips, 79.64% accuracy); no permutation augmentation keeps near invariance (0.04% flips) but changes OOD quality; dual encoder exactly invariant but 65.68% test accuracy.
- 250K artifact: balanced validation accuracy 95.61%, NLL 0.1014, Brier 0.0595, top-label ECE 0.0085, flip 0.183%; OOD accuracy 83.84%, NLL 0.6762, Brier 0.2519, flip 0.0044 (unit as reported), 88.61% binary, 76.86% three, 82.72% five, 72.69% sixteen candidates, 28.57% on the eight-candidate slice (Section VI, Table II). Per-source validation accuracy: Open-Jev 93.10%, xLAM 100.00%, Aegis 2.0 97.50%, ToolACE 100.00%, repo injection 85.03%, WildGuardTrain 98.00%.
- Calibration: NLL, Brier and top-label ECE reported; ECE binning not stated; no post-hoc calibration.

## Cost and latency

None measured (dense kernels; no serving-cost or latency numbers; Section VIII states block-sparse kernels would be needed to quantify serving efficiency).

## Cascade, option-name, language tests

No cascade. Robustness is permutation of candidate order (five fixed permutations) and candidate-count slices (2 to 16); no option-name or language tests. English only.

## Code and data availability

https://github.com/guyAmit/ci-decision-models and Hugging Face artifact Guy-Amit/qwen3-4b-ci-decision-4096-poc (links in the HTML; the text says "available at the project repository").

## Authors' own limitations (Section VIII)

One training seed per condition; CI evaluated with dense kernels so no serving efficiency; dual encoder not objective-matched; 250K case study has no matched causal data-scale comparison; claim limited to order robustness at comparable quality, not universal quality gains.
