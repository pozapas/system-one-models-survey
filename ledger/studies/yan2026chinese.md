# yan2026chinese — Chinese Decision: A Family of Language Models for Single-Pass Probabilistic Decision-Making

arXiv:2610.23170, v1 16 Oct 2026; the retrieved HTML is v2 (23 Oct 2026) and its page header reads "Technical report, version 3, October 2026"; revision history in App. E (v2 21 Oct, v3 22 Oct). The first version reported only one completed 0.8B model (§1). HTML retrieved 2026-10-28 (fulltext/2610.23170.html, .txt). Coder: batch V16. Numbers below are from the retrieved (latest) version, whose evidence snapshot is 2026-10-21 (§4.5).

## Authors and affiliation

Qiang Yan (sole author), Institute of Computing Technology, Chinese Academy of Sciences. Academic. Own-model paper.

## Task and data

Chinese-language typed decisions (noul/Boolean, choice, score/ordinal) via option-letter logits read at the final position of a causal LM, single forward pass per question (§3). Training: 13,048,000 decisions (10M general, 3M medical, 24K legal, 24K finance) from the CJ-Dataset (§4.1, Table 2). Test: the full CJ-Bench, 307,900 decisions (304,822 hard targets, 3,078 soft); general 100,000, medical 200,000, legal 4,300, finance 3,600 (Table 2). Accuracy and ECE use hard targets only (§4.3). Prompt compiler hmm-zh-v1 (3.2).

## Models and versions

chinese-decision-0.8b, -2b, -4b (Qwen3.5 backbones, LoRA r=32, merged BF16 plus Q8_0 GGUF); 0.8B trained with CE, 2B and 4B with CE+RLCD; validation-fitted temperatures 1.108133, 1.074872, 1.024758 (Table 3, §3.6). One run per size, seed 42, four GPUs (§4.2). Baselines: hosted Jev (no version, no date), Open-Jev, SemIF, Laya Multilingual, Qwen3.5-2B (undecision-tuned), Chinese-Jev G+S, all imported from Tables 1 and 2 of Chinese-Jev [12] and "we do not rerun those models" (§4.5).

## Comparators and parity

Imported baselines come from another paper's protocol; "Jev is a hosted model" and its version and run date are not given (§4.5). Chinese-Jev uses about 322M-parameter encoders; the authors' models are larger causal models trained on the same CJ-Dataset (§5.1). Parity: asymmetric (the authors' models are trained on the CJ training data and compared with imported zero-shot/other-tuned numbers; Jev's tuning on this data is unknown). Within-family comparisons: 2B vs 4B nearly controlled; 0.8B vs 2B changes size, objective and batch (§4.2).

## Reference labels

Upstream CJ-Bench labels inherited ("We inherit the upstream split construction and labels", §7). Domain sources include exam datasets, matching tasks and rule-application items (Table 8); some soft targets in general-domain score decisions. Label provenance is not examined in this paper. Coded administrative_field.

## n, sampling, intervals

Full benchmark, no sampling. Stratified parent-clustered paired bootstrap (2,000 replicates, domain strata, same draws across models) for our own models; imported baselines carry no intervals (§4.4, §5.1). 55 source-level tests are uncorrected for multiplicity (§4.4). Intervals cover test sampling, not training seeds.

## Test-set exposure

CJ-Bench is a public benchmark released with Chinese-Jev; the same test set was evaluated in full for 14 checkpoints and six files, with checkpoint selection by validation NLL only (§7). Format and checksum audits "do not establish absence of overlap with backbone pretraining" (§7).

## Cost and latency

A800 80GB PCIe shared server, BF16 batch-one median over 25 benchmark inputs x 3 repeats: 44.4 ms (0.8B), 44.8 ms (2B), 60.1 ms (4B); CPU Q8_0 16 threads median 0.43, 0.82, 2.00 s (§6.3, Table 1). Imported baseline latency deliberately omitted because hardware and network differ; no speedup ratio vs Jev (§4.5, §7). No training cost or GPU-hours reported.

## Calibration

15 equal-width bins, ECE on max probability (§4.3). 4B pooled ECE 1.00%; temperature scaling lowers pooled ECE in all members but raises it in some domains (e.g. 0.8B medical 0.17 to 1.13; 4B finance 1.40 to 1.77, Table 9). Larger members have higher ECE (0.27, 0.64, 1.00) but better risk-coverage ranking (E-AURC 1.89, 1.75, 1.48). Brier and NLL given (Table 5). Per-domain: Jev (imported) general ECE 11.45, professional mean 5.57 vs 4B 2.91 and 1.30 (Table 4).

## Cascade or escalation

No cascade. Selective prediction only (Table 10): 4B accuracy 94.72 at 80% coverage. A candidate tournament for more than 16 candidates is described but has no labeled evaluation (§3.7, §7).

## Robustness

Permutation augmentation is used in training but permutation invariance is not measured; paraphrase, distractor, adversarial and OOD tests are not run (§3.4, §7). Merging and quantization each change 0.4 to 1.1% of top-1 predictions (§6.2). One product-catalog source regresses 2B to 4B (-6.38 pp).

## Code and data

Models on Hugging Face and ModelScope, code on GitHub (MIT; RLCD Apache-2.0), Decision Studio workbench (first page links); training data licenses are source-specific (§7).

## Own limitations (§7)

Three runs, one benchmark family; imported baselines not reproduced and differ in capacity and objective; no CE-only 2B/4B so RLCD effect unmeasured; single seeds; repeated test-set inspection; ECE depends on binning; no classwise or shifted-domain calibration; no pretraining contamination check; tournament unevaluated; no "none of the above" option; no robustness evaluation.
