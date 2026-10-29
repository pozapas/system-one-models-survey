# du2026reliable — How Reliable Are System-One Decisions in Medicine? A Comparative Study of Jev, Jev-like Models, and LLMs

- arXiv: 2610.18529v2 [cs.CL], 16 Oct 2026 (v1 13 Oct 2026). Full text: fulltext/2610.18529.html and .txt (v2 HTML fetched 2026-10-28).
- Authors: Yanrui Du, Danyang Zhao (equal contribution), Sendong Zhao, Wenhao Li, Yibo Gao, Haochun Wang, Bing Qin (Harbin Institute of Technology), Zhuoer Xu, Shiwen Cui (Ant Group); Du also lists Ant Group. Affiliation type: mixed (academic plus industry).
- Code and data: no repository link found in the text; benchmark composition tables are in Appendix B (Table 6).

## Task and data
Unified comparison of "system-one" medical decision models on 15 datasets, 8,742 entries, four families (Section 3): A Triage and Navigation (3,095), B Clinical Judgment (2,501; MedQA, MedXpertQA, ICD-proxy, MIMIC-CDM, SCT and one more), C Safety Review (1,812; MEDEC, MedVAL, RxSafe), D Physiological Assessment (1,334; CTG-21, VitalDB). Each input has evidence, instructions and candidate decisions. Four evaluation dimensions: accuracy and macro-F1 (Section 4), format robustness under relabeling, reordering and option-wise binary scoring OBS (Section 5), abstention awareness via correct-answer replacement by NONE (2,382 entries) and optional ABSTAIN (2,501 entries) (Section 6), and probability-based reliability by threshold and matched coverage (Section 7).

## Decision models and versions
23 configurations (Section 1, Appendix D Table 11): two Jev service versions (Jev-1.13, Jev-1.14; "Jev refers to the model family; the evaluated service versions are Jev-1.13 and Jev-1.14", App. D), ten Jev-like configurations (GLiNER2.5-Decide, SemIf, Kev-4B, AnyJev, OpenJev on diffusiongemma-26B-A4B-it, StartLux 0.8B/4B/9B/27B, D3-27B) and eleven LLMs (Qwen3.5-0.8B/4B/9B, Qwen3.6-27B, Qwen3.8-27B, Gemma4-12B-IT, Gemma4-31B-IT, Kimi-K2.6, MedGemma-4B/27B-IT, Baichuan-M3-235B). Model cards accessed 2026-10-02 to 2026-10-09 (reference list). No run date for the Jev calls and no hardware are reported.

## Comparators and tuning-budget parity
"They receive matched task content, excluding reference answers" (Section 3). Jev-like models get complete Jev-format requests; LLMs get chat-formatted inputs with forced prefill "The answer is \boxed{" and candidate-normalised next-token probabilities (App. D). SemIf, GLiNER and AnyJev use content-preserving adapters (not native heads), so robustness is that of the model-adapter pair (App. D). No tuning on test data described; no few-shot prompting.

## Reference labels
Dataset answer keys: exam questions and clinical records (MedQA, MIMIC-CDM, ICD-proxy), ESI triage labels, expert-annotated error and risk labels, and observed future measurements for VitalDB/CTG ("The reference is derived from future measurements", Table 10). Mixed benchmark answer keys (some records are administrative or outcome-derived); the ledger codes aggregate rows human_adjudicated, following the existing convention for public benchmark answer keys (MMLU, BFCL, BANKING77 in ledger.csv).

## n, sampling, intervals
Equal weight per dataset (Section 4.1). No confidence intervals, bootstrap or significance tests are reported for any headline number; single run per model. N counts entries, not independent patients (Table 6 caption).

## Test-set exposure
Sources mix older public benchmarks and databases (MedQA, MIMIC-IV, VitalDB, CTG, MEDEC) with 2026 sources (for example CARE-bench, Hua et al. 2026, cited in Appendix B.1); ledger test_set_exposure is therefore unclear for the aggregate rows. No contamination check reported.

## Cost and latency
Not reported.

## Calibration and cascade
No ECE, Brier or reliability diagram: figures 2 and 3 captions say "These are selection results, not calibration curves." Probability-based selection (retained accuracy and coverage at thresholds 0.70 to 0.90 and top 5 to 25%) is framed as routing signal for "which answers to accept and which to defer" (Section 7). OBS (normalised option-wise binary scores) raises Jev retained accuracy at 0.90 from 79.43-80.31% to 90.34-96.96% at coverage 18.84-24.74% vs 39.85-42.32% (Section 7.2). Benefit is model-dependent (D3-27B and StartLux get lower retained accuracy under OBS).

## Option-name, cardinality, robustness tests
Relabeling (letters to numbers), reordering, and conversion to binary judgments (Section 5, Table 2). Jev accuracy changes within 0.45 pp, variance 1.09 to 1.70 pp2, mean reversal 5.69 to 6.17% (Section 5.2). Correct-answer replacement with NONE lowers Jev accuracy by 11.4 to 12.0 pp (Table 4). Optional abstention gives only +0.3 to +0.5 pp (Table 5). No language test.

## Limitations (paper's own)
Snapshot of representative Jev-like configurations; no interactive medical workflows or agent settings, so results "do not establish Jev's effectiveness in agent-based settings" (Limitations).
