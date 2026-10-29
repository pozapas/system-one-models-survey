# yang2026what — What Can't Jev Decide? Probing the Limits of One-Pass Decision Models

arXiv:2610.24929v1 [cs.CL], 18 Oct 2026. Full text: fulltext/2610.24929.html and .txt (arXiv HTML). Key chosen as yang2026what because the byline "Wang Yang" appears in given-name-first order like the other authors (surname Yang is an inference).

## Authors and affiliation
Wang Yang, Xinpeng Li, Yanyan Zhang, Shouren Wang, Mohsen Hariri, Vipin Chaudhary, Xiaotian Han (Case Western Reserve University); Chuang Ma (NII LLMC, Japan); Jianzhe Wei, Liqin Ye (Georgia Institute of Technology); Xiaoran Cai (Columbia University) (title block). Affiliation type: academic. No funding or conflict statement located in the text.

## Task and data
Two parts. (1) A controlled, program-generated benchmark varying one factor at a time: retrieval, selection (2 to 64 options), and state tracking with k in {1,2,4,8,16} updates of one user interleaved with other users, contexts 1k to 20k tokens, each cell 10 scenarios x 3 option orders; correct answers computed by a program (Sec 3.1). (2) 1,131 real decision items with fixed option lists: public JevBench tiers (231 items), 300 each from PubMedQA, Banking77, HelpSteer2 via Jevals; after excluding HelpSteer2 and 93 items with disputed gold labels, 738 items (646 one-pass solvable, 92 needing reasoning) (Sec 4.1). Reasoning demand is measured by the median thinking tokens of Qwen3.8-27B (reference, not a model of Jev).

## Decision models evaluated
Jev 1.13.0 through its hosted API, 32k-token input limit, weights not public (Sec 2; Table 5); no run dates reported. 23 open configurations: Kev 0.8B/4B/9B/27B, JevK5 4B/9B, Decider 0.8B to 35B-A3B, Open-Jev-27B, OpenJev-27B, LitJev-27B, llm2jev-27B, jqv/SemIf letter-logit readouts of plain Qwen3.5-4B/9B/3.8-27B, CLM-8B (Sec 2, App. A.1, Table 5). Hugging Face revisions pinned: 139fdd94 (Kev-4B), 2629c06a (Kev-9B), 01b81998 (Kev-27B), 27d2d6b8 (JevK5-4B v0.2); the Kev main branch changed on 2026-10-10 (App. A.1). The authors also retrain Kev-4B/9B/0.8B and JevK5-4B with three seeds, with and without hand-off training (Sec 5.3, App. B).

## Comparators and tuning parity
All models see the same state, question, options and option order; inputs beyond a model's limit are recorded unsupported, not truncated; cross-model comparisons use only items every compared model supports (Sec 2). Qwen3.8-27B with thinking (temperature 1.0, top-p 0.95, top-k 20, max 24,000 new tokens) is a reference LLM, not a decision model (Table 2 caption, App. A.1). Prompt variants P1 to P3 and log variants R1 to R4 are tested on Jev, Kev-27B, Kev-4B (Table 1).

## Reference labels
Controlled benchmark: computed by a program (synthetic). Real items: gold labels of JevBench, PubMedQA, Banking77; 93 items with gold labels the authors consider disputed are excluded after seeing model answers (Sec 4.1), a data-dependent exclusion.

## n and intervals
Cells of 10 scenarios x 3 option orders; 738 real items. Figure 5 error bars are 95% Wilson intervals; headline table values carry no intervals; hand-off training results are means over three seeds (Fig 5, Table 4, Table 9).

## Test-data exposure
JevBench and Jevals are 2026 public releases (Jevals data release 2026-09-18, reference list); PubMedQA (2019) and Banking77 (2020) are public. No contamination check stated. Banking77 is part of Kev training data (Fig 6 caption). Controlled benchmark is new.

## Headline results
Jev answers all 105 retrieval/selection/event cells correctly up to 20k tokens and 64 options; final-state accuracy falls to 53 to 80% at 16 updates (abstract), 64% in Table 2; accepts 91% of correct summaries but rejects 62% of stale (70% up to 8k) (Sec 3.5). Real items: 97.5% on one-pass solvable vs 73.9% on items needing reasoning (Table 3). AUROC of 1 - pmax is 0.83 for own errors, 0.53 after stale summary; ECE 0.03 on final-state items (Sec 5.1). Jev takes the hand-off option on 1.6% of items (Sec 5.2).

## Cost and latency
Intro says about 0.2 s per decision, with no measurement or hardware reported (Sec 1). No cost reported.

## Calibration
AUROC of 1 - pmax, ECE 0.03 (binning not stated in the main text), hand-off option versus confidence threshold (Sec 5, Table 4). No recalibration of Jev; JevK5 uses a fitted softmax temperature (App. A).

## Cascade or escalation
Hand-off option and pmax thresholds as routing to a stronger model; Jev's explicit hand-off catches 3 of 40 errors; trained hand-off for open models doubles errors handed off but a threshold routing the same share is still 1.3 to 1.7 points more accurate (Sec 5.2, 5.3, Table 4). Neither reaches errors inherited from a stale summary (Fig 6c).

## Option-name, cardinality, robustness tests
Option count 2 to 64 (cardinality) tested; no accuracy loss for Jev (Sec 3.2). Three option orders per scenario. Prompt variants and log variants (Table 1). No option-name or language perturbation.

## Code and data availability
No statement that the benchmark or code is released. Evaluated open systems are released by their authors (reference list).

## Authors' limitations (Limitations section)
Items are isolated, single-shot decisions; compounding errors in agent loops, retries, memory and summaries need end-to-end evaluation that is not done here.
