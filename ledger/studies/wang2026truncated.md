# wang2026truncated — Truncated Reasoning Under a Budget: Evaluating System-1 Models as Decision-Makers

arXiv:2610.25768v2 [cs.CL], 24 Oct 2026 (v1 first public 2026-10-19 per the batch list). The full text read is v2 (fulltext/2610.25768.html and .txt). CC BY 4.0.

## Authors and affiliation
Zhongyin Wang (University of Illinois Urbana-Champaign), Zhaoqian Xue and Lingyao Li (University of Arizona), Junting Mu (UC Irvine), Haozheng Liu (New York University), Ye Yuan and Haolun Wu (Mila and McGill University) (title block). Affiliation type: academic. LLM tools used for code and text (Statement of LLM Use).

## Task and data
Multiple-choice QA where an LLM reasoner is cut after a token budget B and an answerer chooses the option from the truncated trace: GPQA-Diamond (198), SuperGPQA (500, difficulty-reweighted from 167 easy/166 middle/167 hard), MedQA (500), MedXpertQA-Text (500), MMLU-Pro (500); seven reasoners (DeepSeek V4 Pro, Qwen3.7 Plus, MiniMax M3, GPT-OSS 120B high, GLM-5.3 Flash, Qwen3.8 Flash, DeepSeek V4 Flash), 35 reasoner-benchmark pairs, 15,377 retained runs, 15,376 in the four-way comparison at B=1.5k (Sec 3.2, 3.3, App. B). Reasoners called via Together AI between late September and early October 2026, temperature 1.0 (App. A, Limitations).

## Decision models evaluated
Jev requested as jev-latest; every audited budget response reported jev-1.13.0 (Limitations, App. A). Jev supports 64k input tokens, 32k for state plus longest question (Sec 3.3). GPT-6 Luna through its Decisions API (non-generative) and through a generative interface as the second reader type (Sec 3.3); Luna version not otherwise identified, documentation accessed 2026-10-11 (references). Readers see the question, options and last ~1,000 reasoning tokens.

## Comparators and tuning parity
Forced answering by the reasoner (whole prefix, provider-supported strict or think-close protocol; five strict-protocol reasoners), Luna decision, Luna generative, question-only controls, tuned static caps, native low-effort Luna (App. G). The main comparison gives readers a 1k window while forced answering receives the whole prefix; a post-hoc window control found a 7.96 pp Jev advantage with matched windows (Sec 4.1, Table 4). Policies (caps, thresholds) are selected by five-fold cross-validation inside each pair; the 1.5k display point was chosen after inspecting the curve (Sec 4.2, Limitations). Prior analyses of these traces exist (Limitations).

## Reference labels
Gold answer keys of the public benchmarks. 140 items flagged for model-label disagreement or manual review were removed in a sensitivity analysis (App. L).

## n and intervals
Macro-average over 35 pairs; 2,000 question-bootstrap resamples (100,000 for positive-budget answerer comparisons), Holm correction across 35 pairs for the primary Jev vs forced comparison, other intervals uncorrected (Sec 3.5, App. R). Traces and forced answers are single samples at temperature 1.0 (Limitations).

## Test-data exposure
Public benchmarks released before 2026; "Public-benchmark exposure and label errors remain possible" (Limitations); no contamination check.

## Cost and latency
Cost from recorded token usage and historical list prices: Jev USD 1.29 per 1,000 questions at B=1.5k vs forced 1.46 and full run 4.44; cost ratio 34.5% vs 38.3% (averaged by pair), 29.2% as ratio of means; latency modelled from decoding speed and answer-call latency, 31.5% of full run (Sec 4.2, App. F). Offline replay, not online cancellation; acquisition expenses excluded (Sec 3.4, Limitations).

## Calibration
Confidence and answer stability signals are used for stopping rules (App. I); no calibration metrics (ECE, Brier) are reported.

## Cascade or escalation
Core subject. Fixed-budget cut then Jev answer; adaptive stopping with Jev checked every 500 tokens through 16k; out-of-fold tuned cap saves 63.3% at -0.13 pp; auto policy saves 71.3% at -0.58 pp, with a 2.59 pp loss on GPQA-Diamond (Table 5, Sec 4.2). Jev question-only accuracy as a policy to decide whether reasoning is needed is in Appendix M.

## Option-name, cardinality, robustness tests
Windows control, strict-protocol subset (2.9 pp gap), label-disagreement removal (4.4 pp gap), answered-runs subset (App. O, L, Q). No option-order or option-name perturbation, no language test.

## Code and data availability
No code or data repository stated; saved outputs "document the evaluated snapshot" (Limitations).

## Authors' limitations
Multiple-choice only, one Jev system and one control model; same cut does not mean same input; offline replay and modelled latency; post-hoc 1.5k display point and selection effects; dependent comparisons, mostly uncorrected per-pair intervals; hosted models and prices change (Limitations).
