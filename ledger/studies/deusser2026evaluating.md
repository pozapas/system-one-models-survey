# deusser2026evaluating

Evaluating and Benchmarking the System One Model Jev. arXiv 2609.37647v1 (cs.CL), 2026-09-29. Extractor: batch V05. Ledger rows: L944 to L948 (earlier round) and L1800 to L1820 (this batch).

## Authors and affiliation
Tobias Deußer, Lorenz Sparrenberg (University of Bonn; Lamarr Institute for Machine Learning and Artificial Intelligence, Bonn), Rafet Sifa (University of Bonn; Lamarr Institute; Fraunhofer IAIS). Affiliation type: academic (title block). Funding: German Federal Ministry of Education and Research and the state of North Rhine-Westphalia via the Lamarr Institute (Acknowledgments). No TypeSafe affiliation or funding stated. An LLM (Claude Opus 5.5) assisted with text and code (Acknowledgments).

## Task and data
Zero-shot evaluation of the hosted Jev API on 37 public datasets in seven families: text classification, intent and topic routing, NLI/paraphrase/grounding, reading comprehension and knowledge, commonsense and reasoning, safety/moderation/legal, rubric scoring (Table 1, Sec. 3.2). Full evaluation splits, 346,009 unique requests (Sec. 3.5, Table 7). Where test labels are not public (SST-2, HellaSwag, WinoGrande, CommonsenseQA, alphaNLI, BoolQ) the validation split is used (Sec. 3.2). BIG-bench: 93 multiple-choice tasks capped at 500 examples (13,228 examples; 13,227 scored because one item exceeded the context limit) (Sec. 3.2, 3.5). One SIB-200 entry skipped. All datasets predate 2026 (public Hugging Face datasets, Table 1), so training-data exposure is possible; the authors state Jev's training data are not public and probe MMLU for memorization (Sec. 2.4, 4.6).

## Decision model and versions
Jev, pinned `jev-1.13.0` for all requests (Sec. 3.1). Primitives: Choice (up to 255 options), Score (2 to 10 levels), Noul (yes/no probability). Price quoted US$0.042 per million input tokens (Sec. 3.1). No run dates beyond the document access date 2026-09-29 (footnote Sec. 1); the paper says nothing about when requests were sent. Requests sent once each, no run-to-run variance measured (Sec. 5).

## Comparators and tuning-budget parity
Qwen3.8-27B (27.8B params) and Gemma-4-E4B (8.0B, about 4B effective), instruction-tuned open-weight LLMs, scored on identical requests via exact next-token probabilities over single-token option codes, renormalized, thinking disabled, no generated text (Sec. 3.6). One chat prompt per question, frozen after a pilot on 20 training/validation examples per dataset; prompts were written for Jev rather than tuned for the open models (Sec. 3.6, 5). Jev templates: one per dataset, tested on 20 examples from a training or validation split, frozen before the evaluation split, no in-context examples, no tuning on evaluation data (Sec. 3.3). Threshold tuning (Table 4) applies the same procedure to all three models, on each model's own answers, with 1,000 training/validation examples (Sec. 3.4, 4.3). Hardware for the open models: Gemma on NVIDIA A40, Qwen on NVIDIA A100 80 GB, bf16 (Sec. 3.6). Parity is therefore same-prompt with a disclosed asymmetry (prompts authored for Jev; no reasoning for the open models, Sec. 5).

## Reference labels
Public benchmark gold labels (dataset annotations: crowd, expert or administrative fields such as IMDB review polarity and hashtag-derived Emotion labels, Sec. 4.1.4). No new human labelling. Labels are therefore a mix of types; per-row types in the ledger are approximate.

## Sampling and intervals
Complete evaluation splits (no sampling). 95% percentile bootstrap CIs over examples, 500 resamples (Sec. 3.4, Table 2). No intervals on cross-model differences beyond the statement that 11 of Jev's leads over Qwen and 31 over Gemma have non-overlapping intervals (Sec. 4.2).

## Headline results
Jev beats Qwen on 27 of 37 datasets (lower on 9, one tie) and Gemma on all 37 (Sec. 4.2, Table 3). Examples: MMLU 0.918, Belebele 0.867, WinoGrande 0.914, IMDB 0.965, ARC 0.988 (Table 2). Weak spots: Emotion 0.585, GoEmotions macro-F1 0.243, AGB-DE F1 0.204, UNFAIR-ToS micro-F1 0.499 at a fixed 0.5 threshold, low-resource languages (Sec. 4.1.4, 4.5). Rubric scoring: Qwen on par or slightly ahead (higher on 9 of 12 dimensions, Sec. 4.4).

## Calibration
ECE over 15 equal-width bins with the top-option probability for Choices and P(yes) for Nouls; Brier also computed (Sec. 3.4). No post-hoc recalibration of probabilities; threshold tuning for Noul decisions only. Pooled Choice ECE 0.028 over 22 datasets and 279,925 answers; median per-dataset 0.028, unweighted mean 0.061; overconfident on 20 of 22 datasets (Sec. 4.3). Single Noul ECE 0.052 (under-confident); multi-label Noul ECE 0.168 (over-predicts yes). Qwen pooled Choice ECE 0.063, Gemma 0.208 (Sec. 4.3). Reliability diagrams in Figure 2.

## Cascade and escalation
No cascade run. Selective prediction with Jev's confidence: at 50% coverage accuracy rises from 79.7% to 96.3% on Banking77, 81.5% to 98.2% on SIB-200, 73.9% to 86.9% on ANLI, 58.5% to 73.3% on Emotion (Sec. 4.3, Figure 3). Open models' own-confidence selection is similar on four datasets (Figure 4). The paper endorses a confidence-gated route to a human or larger model but computes no cost fraction.

## Option, cardinality, language and robustness tests
Cardinality: CLINC150 with 151 options in one Choice, 89.5% (Sec. 4.1.1); BIG-bench options 2 to 118. Option rotation on MMLU calculation-heavy subjects leaves Jev at 0.943 (Table 6). Question withheld drops Jev to 0.315 on MMLU (chance 0.25) (Table 6). Languages: Belebele English 97.2%, median over 122 varieties 91.1%, lowest 37.4% (Nigerian Fulfulde); AfriXNLI English 90.5% versus 16 African languages 33.8 to 70.3% (Sec. 4.5). Numeric answer keys avoided because "36" coincided with an answer in an early version (Sec. 3.3). Unexplained MMLU calculation-heavy result (0.943 versus 0.913 other subjects) that neither open model shows; the authors cannot rule out question-answer memorization (Sec. 4.6).

## Cost and latency
Main evaluation US$9.15 for 217.9M input tokens (630 per request), mean client-side latency 0.36 s at 32 concurrent connections, run time 5 h 15 min; total study US$9.40 including pilot and extra analyses (Sec. 3.5, 4.7, Table 7). Open models: 6.4 A40 GPU-hours (Gemma) and 17.4 A100 GPU-hours (Qwen), stated as not directly comparable with API prices (Sec. 4.7).

## Code and data availability
Code and harness at github.com/AppliedMachineLearning-Lab/jev-benchmarking; all raw responses on Zenodo DOI 10.5281/zenodo.23039006 (Sec. 3.7).

## Authors' stated limitations (Sec. 5)
One untuned template per dataset; open models scored with Jev-authored prompts and no reasoning; no generative proprietary models; Noul decisions use a fixed 0.5 threshold except Table 4 with 1,000 tuning examples; memorization probes cover only shallow forms; several datasets use validation splits; single run, no run-to-run variance; client-side latency includes network time; no relevance-judgment task; results refer to jev-1.13.0 only.
