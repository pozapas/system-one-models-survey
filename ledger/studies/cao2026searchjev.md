# cao2026searchjev — SearchJev: A Calibrated System-1 Model for Search Agents

arXiv:2610.05107, first submitted 2026-10-04 (batch CSV); text read is v2. HTML from https://arxiv.org/html/2610.05107 (fulltext/2610.05107.html and .txt); the version string was not printed in the text read.

## Authors and affiliation
Congfeng Cao, Lipeng Zuo, Konstantinos Papakostas, Qiwei Xu, Songwei Xu, Qianru Meng, Lun Zhou, Zhaochun Ren (Leiden University), Yougang Lyu, Xiaohui Yan (corresponding); all others Huawei Technologies Co., Ltd. (front matter). Affiliation type: mixed (industry with one academic coauthor); an own-model paper by the developers.

## Task and data
SearchDecision-Bench, built by the authors: six search-decision families (routing, rewriting, relevance, sufficiency, navigation, verification) in Choice, Score and Noul formats, converted from heterogeneous public resources into state-schema pairs (§2, Table 1; Table 2 counts: training routing 77,627, rewriting 74,318, relevance 153,990, sufficiency 14,652, navigation 56,981, verification 47,830; ID test 26,427 / 32,746 / 17,581 / 1,036 / 10,213 / 10,334; OOD test 10,000 routing, 10,000 rewriting, 5,976 relevance, 20,631 verification, none for sufficiency and navigation). 683,130 training decisions in total (App.). Splits by identity key and query text; conflicting labels removed (56 rows); train/validation inputs also in a test set removed (185 and 407 rows) (App.). End-to-end test: 100 randomly sampled BrowseComp-Plus questions, one run per question, Qwen3.5-27B as System 2, BM25 retriever (§4.3).

## Decision models evaluated
SearchJev-0.8B and SearchJev-4B (LoRA on Qwen3.5-0.8B/4B, first-token option scoring, Soft-Label Learning for Calibrated Decisions plus temperature scaling fitted on 5,000 validation decisions) and their one-hot variants (§3, §4.3); comparators: Qwen3.5-0.8B/4B AR (JSON) (constrained JSON decoding on the same prompts, untrained for the task, confidence from option log-probabilities), Jev 1.13 queried through its API on the same items (named only as "Jev 1.13"; no dated build or run date) and used inside the dual-system agent, and System-2-only Qwen3.5-27B (§4.1). Peer System-1 models from the JevBench leaderboard are compared by their self-reported numbers on different test samples in App. Table 9 (not entered in the ledger).

## Comparators, tuning-budget parity
SearchJev is trained on the 683K-decision in-domain mixture while the AR (JSON) baselines are the same backbones "before task-specific training" and Jev 1.13 is used zero-shot through its API; the quality comparison is therefore trained-specialist versus untrained/general (not budget-matched), and the one-hot ablation is the only matched-budget comparison (§4.1, Table 3 notes). Latency measured at batch size 1 with the same inference code for open models.

## Reference labels
Mixed: original annotations, derived labels, and LLM-assisted supervision; "LLMs participate in labelling about a third of our training rows" (§7). Test labels come from the source benchmarks; the BrowseComp-Plus judge is an LLM comparing answers with the reference answer (§4.2). Coded administrative_field / task_outcome as appropriate.

## n, sampling, intervals
Per-family test counts in Table 2 and Table 7 (per-dataset accuracies with n). No intervals or seeds reported for Tables 3, 4, 5. End-to-end evaluation is one run on 100 questions; the authors say verification differences reflect run-to-run variation (§5, Table 4 note) and larger samples would be more robust (§7).

## Test-data exposure
Public pre-2026 source datasets (e.g. VitaminC, LCQMC, PAWS-X, FRAMES, BrowseComp-Plus) and new constructed sets (query assessment and query-document quality). Table 11 licences checked 1 October 2026. No contamination check reported for Jev 1.13 or Qwen.

## Cost, latency, hardware
Median decision latency (ms, batch 1): Jev 1.13 265.4; Qwen3.5-0.8B AR 144.2; Qwen3.5-4B AR 195.2; SearchJev-0.8B 27.6; SearchJev-4B 37.1 (Table 3). Jev latency is an API round trip. Hardware for the open models is in App. I (not extracted). End-to-end median active time per question: System-2 only 4080 s; with Jev 1018 s; with SearchJev-0.8B 868 s; with SearchJev-4B 1102 s; output tokens 73.7k / 18.3k / 15.5k / 22.1k (Table 4). No dollar cost.

## Calibration
ECE (scaled by 100) per family; SLCD with output-type temperatures; one-hot variant requires temperatures 1.10-1.56 while soft targets keep 0.82-1.11 (§5). Mean ECE decreases by 74.4% (0.8B) and 40.7% (4B) relative to same-size AR (JSON); Jev 1.13 keeps the lowest mean ECE, especially on navigation (1.5) and verification (1.6) (Table 3, §5). ECE binning is not stated in the text read (ledger coded "ECE (binning not stated)").

## Cascade
Confidence-gated delegation: System-1 decision accepted if max calibrated probability >= delta, else System 2 chooses among the same options (§3.3). Reported end-to-end: SearchJev-4B agent 54.0% answer accuracy vs 45.0% for System-2 only and 46.0% with Jev 1.13; SearchJev-0.8B 46.0%; the delegation threshold value and fraction delegated are not stated in the text read (§5 Table 4).

## Robustness
OOD test sets for routing, rewriting, relevance and verification (Table 5): routing SearchJev-4B 55.8 vs Jev 62.3, verification 65.0 vs 84.5; chinese and English both included (§7). No option-name or order test.

## Code and data
https://github.com/EvoScientist/SearchJev (Abstract).

## Paper's own limitations (§7)
Text-only search decisions in Chinese and English; end-to-end evaluation uses 100 BrowseComp-Plus questions with one run each; interface assumes enumerable options; other languages, modalities and domains untested; about a third of training rows LLM-labelled; training-data bias can affect generalisation.

## Notes for the grader
Own-model paper by the model's developers, compared against Jev 1.13 through its API with no stated run date. Headline gains versus Jev's decision accuracy are on a benchmark built by the authors with the trained models seeing in-domain data.
