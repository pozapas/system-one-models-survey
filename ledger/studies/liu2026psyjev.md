# liu2026psyjev — PsyJev: Psychological Analysis via System-1 Judgment

arXiv:2610.36689v1 [cs.AI], 27 Oct 2026. Full text: fulltext/2610.36689.html and .txt. Own-model paper: a new benchmark (PsyJudgeBench) and a new System-1 style model (PsyJev) trained by SFT plus an RLCD variant (JA-RLCD).

## Authors and affiliation
Fangyuan Liu, Sirui Zhao, Xiaohao Wang, Peng Zhang, Enhong Chen (State Key Laboratory of Cognitive Intelligence, University of Science and Technology of China, Hefei), Guo Cheng (Beijing University of Technology) (title block). Affiliation type: academic.

## Task and data
PsyJudgeBench: 13 existing annotated datasets, 82 registered questions (79 binary, 3 multiclass) in six psychological content areas, 53,775 source records and 222,191 observed judgments; 33,511 train, 5,852 validation, 14,412 test source records; test judgments number 44,999 (Sec 3; Appendix B.3). Coordinated splits group identical texts and near-duplicates; labels not observed for a question are masked (Sec 3). Metric: positive-class F1 (binary) or macro-F1 (multiclass), averaged within each dataset, then unweighted over 13 datasets (Sec 5.1.1). Transfer: Dreaddit, 715 test examples, excluded from training (Sec 5.7).

## Decision models evaluated
PsyJev-2B, -4B, -9B, built on Qwen3.5-2B/4B/9B (revision prefixes for 4B 851bf6e8 and 9B c2022362 in Appendix B.1), constrained scoring over legal answer-identifier logits, joint SFT then JA-RLCD, one epoch per stage; 2B full-parameter, 4B/9B LoRA rank 16 (Sec 5.1.3). Zero-shot Jev (jev-1.14.0) via the official API on all 44,999 test judgments; Noul for binary and Choice for multiclass; 84 invalid responses counted as incorrect (Appendix B.3). Laya-multilingual revision 1720e3e3 adapted by SFT plus native RLCD (Appendix B.3). Jev API run date is not given.

## Comparators and tuning parity
18 baselines all adapted on the benchmark training partition (MentalBERT, MentalRoBERTa, ModernBERT-large, GLiClass, GLiNER2, Laya, FLAN-T5-XL, Qwen3.5-2B/4B, Llama-3.2-3B, Phi-4-mini, Gemma-3-4B, MentaLLaMA-7B, Qwen2.5-7B, Llama-3.1-8B, Qwen3-8B, Gemma-2-9B, Qwen3.5-9B) (Sec 5.1.2). Jev API is zero-shot without fine-tuning or demonstrations, so it receives a different budget than every other row; the paper frames it as a zero-shot reference. Matched 2B ablations share SFT initialization, records, optimizer and 524 additional updates (Sec 5.3). No hyperparameter tuning budget is reported for baselines.

## Reference labels
Source-dataset annotations converted to question-defined judgments; gold/silver distinctions preserved; two conflicting TherapistQA records removed and 22 conflicting judgments masked (Sec 3). Annotation provenance for each dataset not described in the main text.

## n and intervals
Test: 14,412 source records, 44,999 judgments; Table 1 gives point values only, no intervals. One interval: paired text-group 95% CI of 1.73 to 5.96 points for the improvement of PsyJev-4B over the answer model on 35,992 opposite-label pairs (Sec 5.4). Single run per configuration; no seeds reported.

## Test-data exposure
All 13 sources and Dreaddit are public pre-2026 datasets; PsyJev is trained on their training partitions; zero-shot Jev may have seen them. No contamination check.

## Cost and latency
Model computation time per judgment on a single H100 80GB with CUDA Graphs, one text per request, fixed 13-text training probe: PsyJev-2B 4.38 ms, 4B 12.01 ms, 9B 17.12 ms, Laya 1.31 ms, Qwen3.5-4B full-answer scoring 25.25 ms, first-token scoring 11.87 ms (Table 1, Fig 3). Jev API latency not reported. No monetary cost.

## Calibration
15 equal-width bin ECE, Brier, NLL normalized by log of answer-set size, source-balanced; PsyJev-4B ECE 4.58%, Brier 0.2777, NLL 0.536, lowest among the six displayed models (Table 5, Fig 4). No post-hoc recalibration. Jev API calibration is not reported.

## Cascade or escalation
None.

## Option-name, cardinality, robustness tests
Question-conditioned discrimination on 35,992 opposite-label question pairs (Sec 5.4): 70.06% both correct for PsyJev-4B versus 66.24% for the answer model. Unseen-dataset transfer on Dreaddit (Sec 5.7). No option-order or option-name perturbation, no language test (English Web text).

## Code and data availability
No repository or release link in the extracted text; reproducibility details (revisions, hyperparameters) in Appendix B.

## Authors' limitations
No dedicated limitations section. A closing note says the judgments describe annotated textual content and do not establish clinical diagnoses and that reuse should follow source-dataset terms and safeguard privacy (end of Sec 5.7). Comparison with adapted RLCD does not isolate reward or gradient estimator (Sec 5.3).
