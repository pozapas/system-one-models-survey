# chen2026qwen — Qwen-Audio-Jev: A Unified Interface for Audio Decisions

arXiv:2610.21614v2 [cs.SD], 22 Oct 2026 as retrieved (first version 15 Oct 2026 per the batch list); CC BY 4.0. HTML from https://arxiv.org/html/2610.21614. Extractor: batch V15.

## Authors and affiliation
"Token Foundry, Alibaba Group" (title page); 29 authors listed alphabetically by last name starting with Peixin Chen, Zhigao Chen, Zhiyun Fan, Ying Fang, Zhifu Gao (Section 6). Affiliation type: industry (vendor-side technical report from the Qwen-Audio group).

## Task and data
A decision head added to Qwen-Audio-3.1-ASR-Flash-Next that reads the decoder state at the last prefix token and returns typed outputs: Choice (2 to 64 candidates, softmax), Noul (a binary proposition, sigmoid probability) and Score (2 to 10 ordered levels, softmax with expected level) (Sections 2.2, 2.3; Table 1). Evaluation: 18 dataset-task configurations: eight Choice (CochlScene, NSynth, NonSpeech7k, DiDiSpeech, MELD, MMAU, MMSU, MMAR), four Noul (VoxCeleb1-O, Clotho-AQA binary, PodSarc, In-the-Wild), six Score (NISQA overall, noise, coloration, discontinuity, loudness; BVCC/VoiceMOS) (Section 4.1). Sample sizes per configuration and the evaluated splits are not reported.

## Decision model
Qwen-Audio-Jev; the Jev name refers to the typed-primitive interface "inspired by Jev's typed decision primitives (Almeida, 2026)". It is the authors' own model, not the hosted Jev; Jev itself is not evaluated. No checkpoint name, release date or version identifier. Two training stages: SFT jointly updating encoder, adaptor, backbone and head with cross-entropy, binary cross-entropy and a score loss (cross-entropy plus CDF term plus SmoothL1), and an optional "RLCD-inspired" Brier-and-ranked-probability policy-gradient stage (Sections 3.1, 3.2). The text does not say whether the evaluated results come from the SFT or the RLCD checkpoint.

## Comparators and tuning budget
No comparator is reported in the paper: no baselines, no ablation of SFT versus RLCD, no comparison with the original backbone. The abstract-level contribution says it will "assess inference efficiency relative to the original backbone," but no efficiency result appears in the text. Because there is no comparator, `comparator` is "none reported" on all rows.

## Reference labels
Dataset-native labels: categorical labels for classification sets, multiple-choice keys for MMAU, MMSU, MMAR, speaker-trial labels for VoxCeleb1-O, binary labels for Clotho-AQA, PodSarc and In-the-Wild, and human mean opinion ratings for NISQA and BVCC (Section 4.1). Label provenance is not described beyond that; MOS rows coded human_crowd, others unclear.

## n, sampling and intervals
Not reported; no intervals, seeds or repeated runs. Tables give four to six decimals, but no uncertainty. Choice accuracies such as 100.0000 on DiDiSpeech carry no sample-size context.

## Test-data exposure
All benchmarks are public (2017 to 2026 publications). The model is jointly trained on "heterogeneous audio datasets" including MELD and VoxCeleb as named examples (Section 1), but the train/test split used for each evaluation configuration, and whether the evaluation items overlap training data, are not stated. Coded public-pre-2026. High risk of train-test overlap cannot be excluded or confirmed from the text.

## Cost and latency
None reported (no latency, throughput or cost). The motivating claim about overhead of autoregressive generation is not measured. Current implementation processes multiple questions separately, one forward pass each (Section 2.2).

## Calibration
Brier score is reported for the four Noul configurations (VoxCeleb1-O 0.047376, Clotho-AQA 0.148500, PodSarc 0.003059, In-the-Wild 0.167138; Table 3), along with AUC and EER. No ECE or reliability analysis for Choice or Score. The paper says calibration "remains an empirical property" of the RLCD stage (Section 3.2.3); no before/after calibration comparison is given.

## Cascade or escalation
None.

## Option-name, cardinality, language and robustness tests
Training randomly permutes Choice alternatives with descriptions and targets reordered (Section 3.1.2); no test of option order, naming, cardinality or language at evaluation time. Cardinality limits are 2 to 64 options and 2 to 10 levels.

## Internal inconsistency
The Conclusion reports 93.54% accuracy on VoxCeleb1-O while the Abstract and Table 3 give 93.76% (93.7595). Rows use the Table 3 value.

## Code and data
No release; future work mentions a lighter-weight version (Section 5). Coded no.

## Authors' stated limitations
Framed as "remaining areas for improvement": MELD emotion recognition, MMAR complex audio QA, scene and instrument recognition, In-the-Wild threshold and discrimination, noisiness and loudness quality scoring; planned lightweight and streaming versions (Sections 4.2, 5). No separate limitations section.
