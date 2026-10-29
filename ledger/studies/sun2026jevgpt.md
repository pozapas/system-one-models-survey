# sun2026jevgpt: JevGPT, Thinking Fast and Slow in Autonomous Research

arXiv:2610.18272v1 [cs.CL], 13 Oct 2026 (license arXiv perpetual non-exclusive). Full text: `fulltext/2610.18272.html` and `.txt`. Extractor batch V12. Key `sun2026jevgpt` differs from the existing `sun2026typesafe`.

## Authors and affiliations

Yasheng Sun, Yanning Dai, Yimeng Chen, Nanbo Li, Firas Laakom, Yifan Xu, Piotr Piękos, Mateusz Ostaszewski, Wenyi Wang, Cheng Luo, Yuhui Wang, Jürgen Schmidhuber; King Abdullah University of Science and Technology (KAUST) is the listed affiliation (contact yasheng.sun@kaust.edu.sa); the HTML author block lists three affiliation groups, only KAUST is named. Affiliation type: academic. Project page https://sunyasheng.github.io/projects/JevGPT.

## Jev identity

The Jev here is TypeSafe's Jev: "Jev (Almeida, 2026) serves as System One" and the implementation section pins "Jev-1.13.0 as System One" (App. A.1), so the screen note's doubt about identity is resolved. The paper is an application, not a stand-alone evaluation of Jev: it studies a dual-system research agent whose System One uses Jev for typed yes/no (Noul), Choice and Score judgments and whose System Two is a GPT model.

## Task and data

JevGPT couples System Two (a GPT model that plans searches, sets evidence objectives and integrates findings) with System One (Jev) that localises supporting passages (Noul probability of addressing a local question, Choice distribution over text blocks), scores relevance (four-level Score) and proactively inspects candidates (Evidence Discovery with inspection depth K = 60) (Sec. 3). Benchmarks: BrowseComp-Plus, all 830 questions over a 100,195-document corpus, answer accuracy graded with the official template using GPT-5.5 at medium effort; NeuCLIRBench, all 105 topics (54 from 2023, 51 from 2024), English topics searched over English machine translations of Persian, Russian, Chinese documents, nDCG@20 and F1@20 (Sec. 4.1, App. A.2). Main budget 300 s per task; ablations and System Two comparisons use 415 BrowseComp-Plus questions (every second question ID); the System One comparison uses a 3,600 s budget (App. A.2).

## Decision models evaluated and versions

Jev-1.13.0 as System One (App. A.1). System Two: GPT-5.5 at medium reasoning effort (main), plus GPT-5.2, 5.4, 5.4 mini, 5.6 Terra, 6.1 Sol in comparisons (Table 4). In Table 7 GPT-5.5 is also used as System One for comparison. No API access dates are given.

## Comparators and tuning-budget parity

Agent baselines (BCP/ReAct, Reason-ColBERT, Pi-Serini, Agentica, AtlasNav, RISE) are listed from their own papers, so retriever, planner model, budget and run conditions differ (Table 1; the budget follows Pi-Serini's time-budget protocol). The System One comparison (Jev versus GPT-5.5 as System One) holds System Two fixed at GPT-5.5 and uses the same prompts and budget (Table 7). JevGPT uses Hybrid BM25, which the ablation shows contributes a large accuracy gain (Pi-Serini 72.05 to 79.52 on 415 matched questions with GPT-5.6 Terra), so the full system gap to baselines mixes retrieval and System One effects.

## Reference labels

BrowseComp-Plus gold answers graded by an LLM (GPT-5.5) using the official template; NeuCLIRBench official relevance judgments (human assessors). Coded human_adjudicated for the main outcomes, with the LLM grading caveat noted.

## n, sampling, intervals

n = 830 questions and 105 topics for main results; 415 questions for ablations. All values are point estimates without intervals or seeds; "highest observed accuracy" is the paper's phrasing (Sec. 4.2). Tables 1 and 2 give per-question and per-topic resource means.

## Test-set exposure

BrowseComp-Plus and NeuCLIRBench are public benchmarks released in 2025 (citations Chen et al. 2026, Lawrie et al. 2025). No contamination analysis.

## Cost and latency

Table 1 (BrowseComp-Plus, per question): JevGPT 433K System Two tokens, 9.13 searches, 91.7 s; System Two cost $0.6081, System One (Jev) cost $0.0600. Table 2 (NeuCLIRBench, per topic): 158K tokens, 2.68 searches, 79.3 s, S2 $0.5756, S1 $0.0082. Table 7 (NeuCLIRBench, K = 60): Jev as System One 74.8 s and $0.0093 per topic versus GPT-5.5 as System One 344.7 s and $2.0550. No Jev per-call latency or hardware is stated. The costs are those of the evaluated system per task, not the authors' own research spending.

## Calibration

None reported. Jev probabilities are thresholded (evidence threshold tau_loc 0.5, relevance cutoff theta 0.25, usefulness 0.5, continuation 0.5) and not evaluated for calibration (App. A.1).

## Cascade or escalation

Architecture-level two-system delegation: confident local judgments return original passages to the planner; Jev's Choice judgment decides whether to read more context, inspect further candidates or return (adaptive reading, Sec. 3.3). No confidence-threshold cascade metric in the quality-retained / cost-fraction form is reported.

## Option-name, cardinality, language, robustness

NeuCLIRBench uses English machine translations of Persian, Russian and Chinese documents; no language-specific or option-name tests of Jev. Inspection depth K in {0, 20, 60, 120} varied (Table 7): ranking quality is non-monotonic in K.

## Code and data availability

Project page named; no repository URL found in the text read. Coded partial (project page, code not confirmed).

## Authors' stated limitations

Studies architecture coordination only; hopes for a unified model that learns when to judge quickly or reason; evaluation limited to fixed-corpus QA and ranking, not open-web or long-form synthesis (Limitations).
