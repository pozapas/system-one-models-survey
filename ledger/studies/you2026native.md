# you2026native — Native Probability Outputs for Clinical Triage: An Evaluation of Calibration and Decision Accuracy

arXiv:2610.24692v1 [cs.LG], 17 Oct 2026 (paper dated September 21, 2026). Full text: fulltext/2610.24692.html and .txt (arXiv HTML).

## Authors and affiliation
Liang You (University of Pittsburgh), Zhiyin Zhou (Pratt Institute), Dawei Tang (Icahn School of Medicine at Mount Sinai), Chuchu Wu (Carnegie Mellon University), Jingzhuo Hu (University of Pennsylvania) (title block). Affiliation type: academic. Author reports no relationship with TypeSafe/Jev; no external funding (App. B). AI assistance used for drafting (App. B).

## Task and data
Primary: CARE-Bench (Hua et al. 2026, arXiv 2608.03731) patient-facing triage, four actions (Info, Self-Care/Monitor, Nonurgent Care, Urgent Care). Public release has 925 decision points from 439 cases (dev 609/284, validation 181/93, Public Test 1 135/62); the main comparison is on Public Test 1; 134 controlled-access points are not used (Sec 3.1). Secondary: HealthBench emergency-referral theme, 453 of 482 conversations with a unique physician-majority category (emergency 139, conditionally emergent 180, non-emergent 134), 29 excluded (Sec 3.5).

## Decision models and comparators
- Jev version 1.13.0, identifier jev-1.13.0, accessed 21 September 2026 UTC; Choice interface with four options, plus Noul (yes/no) for information sufficiency (Sec 3.2, App. B). The matched follow-up ran 24 September (Sec 3.4).
- Comparators are general-purpose LLMs asked for four probabilities in one prompt, no explanation: DeepSeek Flash (deepseek-flash), Gemini 2.5 Flash (google/gemini-2.5-flash), GPT Luna (openai/gpt-5.6-luna), GPT Sol (openai/gpt-5.6-sol) (App. B). Same action instruction and label descriptions; reasoning disabled/minimized, 256 max output tokens; temperature and seed not set; no few-shot, no system message (Sec 3.2, App. C). Tuning-budget parity: same prompt for all, no training or fine-tuning (Sec 3.1).
- Three input-independent baselines: uniform, development majority, development empirical prior (Sec 3.3).

## Reference labels
CARE-Bench reference actions and an existing missing-information label from the benchmark (Sec 3.1, 3.4); how they were made is not described here (deferred to Hua et al.), so coded as administrative_field in the ledger. HealthBench: physician-majority category (Sec 3.5), coded human_crowd.

## n, design, intervals
Test n = 135 decision points from 62 cases; 2,000 paired case-bootstrap replicates preserving within-case dependence, seed 20260921; no multiplicity adjustment (Sec 3.3). HealthBench: 2,000 conversation-level replicates, seed 20260922 (Sec 3.5). Study is exploratory, not preregistered; labels and earlier results were inspected before analysis; follow-up plan frozen after prior public-test inspection (Sec 3.1, App. D).

## Test-data exposure
CARE-Bench (2026 release) and HealthBench (2025). "Training exposure is unknown for both datasets" (Sec 6).

## Headline findings
Jev macro-F1 0.461, fourth of five; lowest Brier 0.610 (18.7% better than uniform, CI 4.9 to 31.1); ECE 0.226; detects 3 of 37 clarification points (Table 1, Sec 4.1, 4.2). Independent Noul sufficiency question raises recall to 36/37 with 54/98 false positives; matched Choice binary gives the same recall, Noul has lower binary Brier (0.21466 vs 0.27624) (Sec 4.2). HealthBench: Jev macro-F1 0.788, Brier 0.299, ECE 0.081 (Table 2, Sec 4.4).

## Cost and latency
Jev USD 0.0193 per 1,000 calls, 106.56 s for 925 calls at four concurrent requests, median 0.401 s, p95 0.499 s; GPT Sol USD 0.7192 and 484.03 s (Table 4, Table S7). Jev and DeepSeek costs use vendor tariffs, others OpenRouter-reported; estimates, not invoices (App. F). Wall-clock includes batch overhead, single run.

## Calibration
Multiclass Brier, top-label ECE with ten equal-width bins, NLL, class-specific reliability with 5/10/15 bins (Sec 3.3, 3.4). No post-hoc recalibration (Sec 6, App. D). Development-selected thresholds at 10% FPR cap gave higher test FPRs (Sec 4.2).

## Cascade or escalation
None. Threshold-based clarification only.

## Option, wording, robustness tests
Reversed option order changes 5 Choice and 1 Noul decisions, alternate wording 17 and 15, identical repeat 2 and 1, on 135 points (Sec 4.2, Table S3). Definition sensitivity of the HealthBench conditional criterion changes 10/453 Jev decisions (Sec 4.4). No cardinality or language test.

## Code and data availability
Code, templates and version records "maintained internally"; no public repository link; Hugging Face reproducibility release in preparation (App. B, App. D).

## Authors' limitations (Sec 6)
Exploratory, public benchmarks, 62 test cases with reconstructed encounters; agreement with benchmark references only, no clinician adjudication; labels inspected before follow-up; unknown training exposure; low-latency configurations without recalibration; matched formulation experiments Jev-only; HealthBench uses category classification rather than rubric scoring.
