# sakhawat2026literal — Literal Lock-In: How Test Language Shifts Literal Attraction in Typed Decision Models on Bengali Idioms

arXiv:2610.22526v1 [cs.CL], 15 Oct 2026. HTML retrieved 2026-10-28 (fulltext/2610.22526.html, .txt). Coder: batch V16.

## Authors and affiliation

Adib Sakhawat (equal contribution), Syed Rifat Raiyan. Systems and Software Lab, Department of Computer Science and Engineering, Islamic University of Technology, Dhaka, Bangladesh (title block). Affiliation type: academic. Independent audit; no vendor involvement.

## Task and data

Black-box behavioral audit of three typed decision models through interventions on the option list. Task: given a Bengali idiom, choose its gold figurative meaning from k=4 options (chance 0.250; §4.1). Corpus: Bangla Bagdhara (Sakhawat et al., 2026), 10,361 published idioms, 10,359 in the distributed file, 8,876 with all required fields; expert-consensus annotation under a 19-field schema (§3). Five distractor families (d-rand, d-surf, d-sem, d-lit, d-hard), seven interventions E1 to E7 (§4.2, §4.3). Literal Attraction Rate (lar) = share of items where the chosen option is the idiom's own expert literal gloss. Main matrix: model x language on a shared pool of 3,265 items with a usable English literal gloss (36.8% of corpus; §5.1, App. J). Other n: Laya-ml 8,876, Lod-lille a fixed 10% subset of 888 outside the matrix, Jev-1.13 8,761 on the English ladder (§5.1, Table 18); order audit 300 items x 24 permutations for Jev (App. R).

## Decision models and exact versions

- Laya-ml: convaiinnovations/laya, subfolder multilingual; bidirectional encoder with marker-position scoring; one Tesla T4; "bf16 requested" falls back to fp32; per-bucket temperatures not applied, so ECE is raw (§4.4, App. R). No revision hash.
- Lod-lille: mrn-dk/lod-lille-0.6B; decoder with independent-option scoring, fp32, T4, temperature 1.0 by design (§4.4, App. R). No revision hash.
- Jev-1.13: typesafe/jev-1.13 over OpenRouter /api/alpha/decisions. "That alias is mutable: at the time of our run it resolved to the 20260917 build" (App. R). No run dates beyond that. Documentation names English as primary language (§4.4).

## Comparators and parity

Three models are compared against each other with the same instruction string, k and per-item order seeds (§4.1, App. C); no LLM baseline, no tuning, all zero-shot (Limitations). Models differ in n per experiment, so some comparisons are unpaired (E7). Parity: same prompt/zero-shot; no tuning budget.

## Reference labels

Expert-annotated gold figurative meaning and expert literal gloss from the published corpus (human adjudicated by expert consensus, §3). The English cell uses the English parenthetical of the same annotated field, not a translation (App. J). Semantics-free control (o4) has no information in options (chance).

## n, sampling design, intervals

95% percentile bootstrap over items (2,000 resamples, seed 0), McNemar exact test for pairs, ECE with 15 equal-width bins, AURC against a random-gate baseline, binning-free Brier and AUGRC (§4.3, §5.2, App. R). Per-item option order randomized and seeded. The two open arms were built independently; gold key and position agree at 1.000 on 4,440 overlapping rows (App. R).

## Test-set exposure

Corpus published in 2026 by the same group; whether any model saw it is not discussed. Coded unclear. Jev training data are unpublished. The Limitations section notes models are used zero-shot out of their trained task set, so part of the effect may be out-of-distribution transfer.

## Cost and latency

Jev: 56,533 calls for $0.9348 at $0.042 per million input tokens, output free; matrix run 6,531 calls for $0.1152; total $1.05 (App. R). Laya-ml 27.2 ms per call, Lod-lille 86.1 ms per call on one T4 (App. R). These are the authors' own audit costs, reported in the primary source.

## Calibration

ECE (15 equal-width bins), equal-mass bins (no ECE moves by more than 0.011), Brier, AURC, AUGRC (§5.2, App. F). Open arms are untempered. Jev English d-lit ECE 0.014, Brier 0.107; Jev Bengali ECE 0.135, Brier 0.604 (§5.2). Open-arm ECE under d-lit 0.385 (Laya-ml), 0.679 (Lod-lille). Confidence is anti-diagnostic on both open arms; Jev not inverted.

## Cascade or selective prediction

Confidence-gated selective prediction is worse than random gating for both open arms: Laya-ml top 5% confidence gives 0.007 accuracy against 0.151 at full coverage (§5.2). Jev AURC 0.013 vs random 0.069 in English (Table 2). No cascade built; the paper bounds the cascade designs of Li et al. (2026).

## Robustness

Language effect: lar falls Bengali to English 0.731 to 0.379 (Laya-ml), 0.918 to 0.241 (Lod-lille), 0.304 to 0.047 (Jev) (§5.1). Option-order: marker scorer changes its chosen option on 83.7% of items vs 10.7% (Lod-lille) and 13.3% (Jev), but slot and label are confounded (§5.4). Option text scramble, idiom-unit perturbation, option ablation and semantics-free control are reported (§5.3 to 5.5). Jev under the semantics-free control reports 0.815 mean confidence at 0.254 accuracy.

## Code and data

Instrument, per-item outputs, analysis scripts, figure sources released under CC BY-SA 4.0: https://github.com/sakhadib/literal-lock-in.

## Paper's own limitations (Limitations section)

All zero-shot; possible out-of-distribution task transfer; Laya-ml temperatures unset and bf16 fallback; Lod-lille on a 10% subset (about +/-3 points); E7 cannot separate position from labeling; E3 under d-lit has floor effects; E6 under d-rand; matrix pool is not neutral (levels inflated by the English parenthetical cue, worth +0.165 lar on Laya-ml); the two language cells are paired entries, not translations, and asymmetric in four ways; one corpus, one language, two small open models, one commercial endpoint; Jev results are a dated snapshot of a mutable alias.
