# lee2026medjev — MedJev: Evaluating Zero-Shot System-One Decision Making in Medicine

arXiv:2610.36006 (version not stated in the HTML text; batch list date 2026-10-26). Full text: fulltext/2610.36006.html and .txt. Own-model paper: the authors release MedJev and evaluate it.

## Authors and affiliation
Simon A. Lee, Jiahang Sha, Moonseong Jeong, Yunbei Pan, Jeffrey N. Chiang; UCLA Computational Medicine (Chiang also UCLA Neurosurgery) (title block). Affiliation type: academic.

## Task and data
Ten medical benchmarks (Sec 3.2, Table 1). Knowledge and diagnosis, Choice requests: MedQA (5-option, test n=1,273), USMLE (4-option, n=1,273), NEJM (n=512; five-option questions the authors constructed from vignettes using clinician-graded wrong GPT responses and other diagnoses), DiagnosisArena (915 public cases, 4 options). Patient-level: MIMIC-IV v2.2 via MEDS (In-Hospital Mortality at 24 h, test n=33,234, 2.2% positive in Table 1; Length of Stay > 7 days; 30-Day Readmission; ED Admission at 2 h) and MIMIC-IV-ED (ED Triage Admission, Noul; ED Triage Disposition, six-option Choice; test n=42,625). Patient-disjoint train/tuning/held-out partitions (Sec 3.2).

## Decision models evaluated
MedJev: OpenJev Flash 9B (MLX 8-bit) "adapt[ed] on medical data (MIMIC-IV Note)" (Sec 3.1). Readout T=1.07, TN=1.0748, b=0, frozen inference helper SHA-256 prefix 81a22f1b. No dated release tag or Hugging Face revision is given in the text; Hugging Face model Simonlee711/MedJev and GitHub Simonlee711/MedJev are cited (abstract). The text mentions Jev (TypeSafe) only as the interface; hosted Jev is not run.

## Comparators and tuning parity
Zero-shot LLMs with the same request construction and option-token probability readout, no generation: Qwen3.5-9B (base of OpenJev), Qwen3.5-2B, Pythia-2.8B, MedGemma-1.5-4B, Gemma-3-4B (Sec 3.3). Published GPT-3.5, GPT-4, GPT-4o, o1 numbers taken from the literature, not re-evaluated, different prompts and formats, no paired tests (Sec 3.3). Supervised XGBoost and TF-IDF + logistic regression trained on local labels with hyperparameters chosen by five-fold cross-validation (Sec 3.3); label budget varied 25 to 1,000 (Sec 4.4). Asymmetry: MedJev is domain-adapted on MIMIC-IV Note, the LLM baselines are not adapted; one prompt and serialization per task, not optimized (Sec 5 Limitations).

## Reference labels
Exam answer keys for MedQA/USMLE; benchmark gold diagnoses for NEJM (options authors-constructed) and DiagnosisArena; observed hospital outcomes (task outcome) for MIMIC tasks (Sec 3.2).

## n and intervals
Test n as above. 95% percentile bootstrap CIs over test examples; paired bootstrap for differences with baselines (Sec 3.4). Label-budget curves are mean +/- SD over 10 random draws (Fig 6).

## Test-data exposure
MedQA public since 2020, MedQA and USMLE share question stems, overlap with pretraining not excluded (Sec 5 Limitations). MIMIC data via PhysioNet credentialed access. MedJev adaptation on MIMIC-IV Note while evaluating on MIMIC-IV tasks: overlap between adaptation text and EHR test patients is not discussed (observation, not a statement of the paper).

## Cost and latency
About 0.5 s per MedQA question and 2 s per serialized MEDS state, local Apple silicon laptop, 48 GB unified memory, 8-bit MLX; no monetary cost, no comparison with API latency (Sec 3.4).

## Calibration
ECE from 15 equal-width bins (Sec 3.4); calibration curves by prediction deciles (Fig 5). Zero-shot knowledge ECE 0.039 (MedQA), 0.028 (USMLE), 0.063 (NEJM); patient level poor: mortality ECE 0.286 (mean predicted 0.312 vs observed 2.6%; Table 1 says 2.2% positive and Table 3 says 2.6%, a small inconsistency in the paper), LOS 0.191, readmission 0.272, ED triage admission 0.147 (Sec 4.3). Platt scaling (binary) and temperature scaling (multiclass), two parameters, fitted on 50-200 local labels; mortality ECE 0.007 after recalibration; a temperature fitted on MedQA does not transfer consistently (Sec 4.3-4.4).

## Cascade or escalation
Selective prediction by confidence only shown as an accuracy-coverage figure (Fig 7); no numeric thresholds, no cascade with a stronger model.

## Option-name, cardinality, robustness tests
None. Choice cardinality differs across tasks (4, 5, 6) but there is no ablation. Single prompt and serialization (Sec 5). English only.

## Code and data availability
Code and evaluation harness released: https://github.com/Simonlee711/MedJev; model on Hugging Face. Calibration parameters fitted on credentialed data not released (Sec 5, Data use and ethics).

## Authors' limitations (Sec 5)
Few positives in some tasks (mortality 2.6%), wide AUROC intervals; single prompt and serialization format; NEJM originally open-ended so GPT references not comparable; possible pretraining overlap for MedQA/USMLE; incomplete ICU item dictionary in MEDS extract; single-center data, generalization unknown.
