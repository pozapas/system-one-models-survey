# zhang2026general: A general-purpose System One decision model for clinical records

arXiv:2610.27099v1 [cs.AI], 19 Oct 2026 (HTML title block; fulltext/2610.27099.html and .txt). License CC BY-NC-ND 4.0. Extractor batch V18.

## Authors and affiliation
Andrew Zhang, Trinh T.L. Vuong, Sophia J. Wagner, Dongmin Bang, Tong Ding, Yuchang Su, Mary Cipperman, Christina S. Chen, Judith Lefkes, Ramin Kahidi, Ming Y. Lu, Caiwei Tian, Tianhao Luo, Jingnan Ma, Rowland Pettit, Long Phi Le and Faisal Mahmood (co-senior, corresponding) (title block). Mass General Brigham AI Institute; Harvard Medical School; Massachusetts Institute of Technology. Affiliation type: academic.

## Task and data
Clinical System One (CS1-4B): typed questions over clinical notes, diagnostic reports and serialised structured timelines. Training set Klaros-12M: 12,416,448 document-question pairs from 3,643,798 patients across 24 MGB hospital sites. Internal test MGBQA-1M: 963,408 held-out MGB patients, one question each, 28 tasks over six task types; 14 tasks are keyed by rules, observed outcomes, registry or an open LLM (Gemma-4-26B-A4B) and are the primary comparison, 14 are keyed by the training teacher GLM-5.3-Flash and are secondary (Methods 0.9). External evaluation: 21 public data sets (86,830 scored pairs; MIMIC-IV, eICU-CRD, EHRSHOT timelines and composite definitions, outcome forecasting, MedAgentBench, BRIE, EHRNoteQA, LongHealth, MIMIC-III phenotypes, MIMIC-CXR-VQA, ReXVQA, TCGA and HISTAI pathology reports, MIPA, assertion sets) (Methods 0.8, Extended Data Table 4). Agentic uses: whole-record QA examples and screening of 1,000 MIMIC-IV patients against 17 ClinicalTrials.gov trials.

## Decision models evaluated
- CS1-4B: full fine-tune of Decision 2.0 Nox-4B (Qwen3.5 hybrid, 4.2B parameters), trained on Klaros-12M only; three label kinds: GLM-5.3-Flash teacher soft labels (rotation-averaged option probabilities), rule-computed exact answers, observed outcomes; 26,441 steps, 211 GPU-hours on eight B300 GPUs (Methods 0.11, 0.12). Weights "will follow as a credentialed release upon institutional approval" (Discussion).
- Open comparators run through each model's reference implementation: JEV-27B (frozen Qwen3.8-27B with LoRA and decision head distilled from a proprietary decision model), Clef-27B, six Decision 2.0 models (Kai-0.6B, Eos-0.8B, Sol-2B, Nox-4B, Lux-9B, Vega-27B), pplx-decider-v1-27b, BioDecision-4B, MedDecider-9B and -27B (public sets only) (Methods 0.13). The question-format mapping for each baseline was chosen among two or three variants by agreement with the teacher on 20 validation notes, "without benchmark keys".
- Hosted TypeSafe Jev: "run only on openly licensed sets (LongHealth, TCGA pathology reports) and synthetic records" (Methods 0.13; column "TypeSafe API" in Extended Data Table 4). No version string or date is reported for the hosted service in this paper.
- LLM teacher/judge GLM-5.3 (744B MoE) and GLM-5.3-Flash (320B MoE).

## Comparators and tuning-budget parity
CS1-4B is fine-tuned on 12.4M institutional pairs; open decision models and the hosted Jev are used as released (zero-shot with respect to MGB). The paper says so and notes the public-set comparison is "less useful as a direct comparator between CS1-4B and other public models" (Results 0.3). Most-common-answer baseline reported per set. For trial screening, comparators are BM25 keyword search (1,000 patients) and an LLM reading every record (criterion level, 200 patients).

## Reference labels
Mixed. MGBQA-1M primary keys: structured-data rules, observed outcomes, registry, or an open LLM; 14 secondary tasks keyed by the training teacher (agreement with teacher, not independent). Public sets: rule, outcome, human, LLM, registry or teacher (Extended Data Table 4). Public key examples: LongHealth key "human"; TCGA key "registry"; HISTAI key is the teacher's own answer ("CS1, distilled from that teacher, has a built-in advantage"); BRIE keyed by an open LLM; ReXVQA by its authors' LLM pipeline. Trial screening ranking judged by blinded GLM-5.3 (LLM judge, weighted kappa 0.84 between two passes measures consistency, not clinician agreement); note-only criteria keyed by agreement of two full-record GLM-5.3 reads. Ledger rows list the dominant label type and name any exceptions.

## n and sampling
MGBQA-1M one question per patient across 963,408 patients; per-set pairs in Extended Data Table 4; 95% document- or patient-clustered bootstrap intervals (1,000 resamples) and Bayesian bootstrap for some sets (Methods 0.16); main text mostly reports point values with no interval, intervals appear in the figures and Extended Data. Single training run. Trial screening: 1,000 patients, 17 trials, 7 trials and 200 patients for criterion level.

## Test-set exposure
MGBQA-1M: private institutional records, new. Public sets: public data sets that may be in open models' training data ("we cannot exclude that the published benchmarks ... were seen in their training", Results 0.3). The authors use MGBQA-1M as "the only evaluation in this study whose records and keys no open model could have seen".

## Cost and latency
One NVIDIA GB10 (DGX Spark), bf16, synthetic 2,900-token note, median of 10 repetitions after warm-up, back to back, IQR within 4.2% of the median (Extended Data Table 2 caption): CS1-4B 683 ms (1 question), 955 ms (10), 1,801 ms (40 questions); Vega-27B 11.54 s at 40 questions (6.4 times slower); GB10-hours per million documents at 40 questions: CS1-4B 500, Nox-4B 630, Lux-9B 830, Vega-27B 3,210. Decision 2.0 models were run through their official runtime, not optimised; CS1-4B and Nox-4B share an architecture and differ 1.3-fold in time, which the authors attribute to inference code. About 2,000 notes per hour at 40 questions on one GB10. Trial screening: 610 LLM tokens per patient versus 421,136 (690 times fewer), excluding CS1-4B's own compute and verification (Fig. 5e).

## Calibration
Top-label ECE with 15 equal-count bins (Methods 0.16); raw model outputs, the teacher temperature-scaled; no calibration file ships with open models. Public sets: ECE 0.012 to 0.052 across six task types for CS1-4B vs 0.033 to 0.139 for Nox-4B; pooled over five human-keyed public benchmarks (14,756 items) CS1-4B 0.029, Nox-4B 0.058, JEV-27B 0.010, Clef 0.024; per set 0.007 to 0.100. Outcome forecasts: mean predicted risk 0.39 vs observed incidence 0.19 over 27 outcomes of three public prognosis sets, calibration error of predicted risks 0.203, median calibration slope 1.03; after one log-odds shift per outcome (estimated on the other half of patients) calibration error 0.014 and Brier 0.182 to 0.110 (Nox-4B after the same correction 0.118) (Results 0.4). CS1-4B reported without a fitted temperature.

## Cascade or escalation
Confidence routing: answers at P>=0.95 are accepted automatically and others go to a reviewer (Fig. 1f, illustration on a synthetic note). Coverage at 99% precision is tabulated per system in Extended Data Table 2c (not extracted). Agentic harness: GLM-5.3 plans typed sub-questions and CS1-4B answers them (Fig. 4, Fig. 5).

## Option-name, cardinality, language, robustness
Question isolation (each question attends to document and itself only). Layout comparison on MIMIC-IV timelines: all models score higher in the encounter layout CS1-4B was not trained on (Extended Data Table 5). Option order rotation in teacher labels. Questions have at most 11 options. English clinical text only.

## Code and data
Weights via credentialed release pending institutional approval; MGB data restricted; public sets used under PhysioNet credentialed agreements; no code repository stated.

## Authors' own limitations (Discussion)
Data curation choices and rule-based serialiser define concepts; three public keys and 14 secondary MGBQA tasks are model-written; LLM annotators diverge from human keys on phenotypes (90.6% agreement, below the 92.5% majority); not for differential diagnosis; not prospectively validated; must not make autonomous decisions about individual patients.

## Notes for the grader
The abstract's "13 of 14 tasks" and "outperformed open decision models up to 27B" apply to MGBQA-1M, where CS1-4B was trained on the same institution's records while the comparators were not. On the 21 public sets CS1-4B is behind Vega-27B on average (86.7 vs 88.6); it exceeded every open model on 5 of the 21 sets, and a 27B model was the best open model on 20 of 21 (Results 0.3). The 6.4-fold speed claim is against Vega-27B using an unoptimised runtime.
