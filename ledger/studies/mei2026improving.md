# mei2026improving

arXiv 2610.35654v1 (cs.CL), 26 Oct 2026. "Improving JEV Entailment Reranking with Span Readouts and Selective Adaptation." Authors Haocheng Mei, Yuchuan Tian, Chao Xu (Peking University), Ye Yuan (SUIBE), Enhua Wu (University of Macau), Allen Chen (Tsinghua University), Kai Han, Yunhe Wang (TokenRhythm Technologies). Affiliation type: mixed. (title block)

## Task and data
- Multiple-choice answering framed as entailment reranking: each candidate answer is a separate three-option NLI request (entailment, neutral, contradiction); candidates ranked by entailment probability. MC11 averages accuracy over eleven configurations from seven public sources (ARC-Easy, ARC-Challenge, GSM8K 4- and 10-option, GPQA and MMLU with and without demonstrations, HellaSwag, WinoGrande, synthetic chess). Additional: PIQA (1,838 validation questions), CommonsenseQA (1,221), SocialIQA (1,954), JevBench (18 families, 231 questions), Kev suites (eight selections). Number of questions per MC11 configuration is in App. A (Table 7), not extracted. (Sec. 3, Sec. 4, App. A.1)
- Training mixture: public-source labels plus model-generated reference answers, 17,661 records and 24,001 questions in eight grouped pools; each fold trains on seven pools, 2 folds x 2 seeds = four matched settings. (Sec. 3)
- Reference labels: benchmark gold answers (administrative). Public benchmarks pre-2026; no contamination check for the backbone. (Sec. 3, App. A)

## Decision models
- Open Jev-style models built here on TokenRhythm/NeoHorse-1-4B (Qwen3.5-4B repackaging, attention + gated DeltaNet), revision 56f0584b, bilinear head width 256, rank-64 LoRA (alpha 128), one epoch OneCycle, peak lr 1.25e-5; plus a Qwen3-4B comparison. Hosted Jev is not evaluated. (Sec. 3, App. A.3)

## Comparators and tuning parity
- Internal comparison of readouts (option-ending pointer, last-content pointer, mean-span) and adapter scopes (all-module, no-FFN, rank-28 all-module), each trained afresh with matched initial tensors, data order and augmentation. The one-epoch lower-rate recipe was chosen from learning-rate and epoch diagnostics run on the same MC11 evaluation, so the "reference" pointer was tuned on the evaluation metric; a head-first schedule giving 53.54% with a no-FFN pointer was not combined with pooling. No external baseline. (Sec. 5.4, App. B.3)

## Results
MC11 accuracy (four-setting mean +/- descriptive SE): all-module pointer 50.28 +/- 1.02; all-module mean-span 51.00 +/- 0.21; no-FFN pointer 52.49 +/- 0.46 (paired +2.21 +/- 0.66); no-FFN mean-span 53.39 +/- 0.24 (+0.91 +/- 0.35). Trainable parameters 58.82M vs 131.17M (-55.2%). Fixed-checkpoint PIQA: pooling minus pointer -0.12 pp direct, +8.07 pp NLI. Direct selection: no-FFN mean-span JevBench 73.79 and Kev 78.12 vs all-module pointer 77.11 and 81.37. Qwen3-4B: pooling 51.70 vs pointer 52.17 MC11. Intervals are descriptive SEs over four settings sharing pools and questions, not confidence intervals. (Sec. 4-7, Tables 1-6)

## Cost and latency
Trainable parameters only; no latency or cost; H100 used for training. Pooling needs one projected key per option; reranking costs one backbone request per candidate. (Sec. 2.3, App. A)

## Calibration
Not evaluated.

## Cascade or escalation
None.

## Robustness
NLI option wording and label order sensitivity on PIQA (18 combinations; pooling advantage +3.18 +/- 3.27 pp, one description set favours the pointer by 1.80 pp); learning-rate and epoch sensitivity (two-epoch pointer 43.96%); candidate counts 2 to 10 across configurations. No language tests. (Sec. 4, Sec. 5.4, App. B.4)

## Code and data
Project page https://github.com/Mei-TN/Jev-reranking. (Abstract)

## Authors' limitations
No dedicated limitations section. Stated caveats: final no-FFN pooling model not evaluated on PIQA/CommonsenseQA; combined model loses accuracy on direct JevBench and Kev suites; pooling does not improve aggregate MC11 on Qwen3-4B; head-first schedule not combined with pooling; CUDA determinism disabled and repeated runs can diverge; SEs descriptive. (Sec. 5.4, 6, 7, App. A)
