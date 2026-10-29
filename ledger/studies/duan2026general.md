# duan2026general — General Decision Models: Benchmarking and Insights Beyond Jev (JEVal, SII-Decision)

arXiv:2610.03935, first submitted 2026-10-02 (batch CSV); text read is v2 ([cs.CL], 12 Oct 2026) from https://arxiv.org/html/2610.03935 (fulltext/2610.03935.html and .txt). v1 was not read.

## Authors and affiliation
Feiyu Duan, Jiayu Lin, Jia Wang, Jun Xiang (equal contribution), Jialiang Wu, Xinnong Zhang, Hanqi Yan, Siyuan Wang, Zhongyu Wei (corresponding). Shanghai Innovation Institute, Fudan University, Tongji University, King's College London, Chinese University of Hong Kong (front matter). Affiliation type: academic. The authors also build and evaluate their own models (SII-Decision-4B/27B), so some rows are own-model results.

## Task and data
JEVal, a bilingual benchmark of 11,257 instances from 36 public datasets, 58 subtasks, 10 domains (general knowledge and reasoning 23.1%, law and personalization 16.0% each, etc.); 9,457 English and 1,800 Chinese; choice 85.1%, noul 12.0%, score 2.8%; choice candidates 2 to 255, median five (§3.3). Main metrics computed on the 10,938 choice and noul instances (Table 1). Sampling: at most 200 instances per subtask from the official test split (or validation/train when there is none); exact-string deduplication left more than 202K candidates before resampling; inputs capped at 20,480 tokens (§3.2). Two human experts inspected tasks and kept only datasets with manually verified reference answers (§3.2). Extra analyses: four 100-item computation/probability tasks (Table 2), LongBench/BABILong/NoLiMa-MC (Fig. 9), tau-bench Retail and Airline with Jev replacing action selection (Table 3), user-interest profiling of 898 accounts (Table 4), SocioBench with 277,500 respondent-question pairs (Table 5), ElectionSim (about 330,000 voters, Fig. 14).

## Decision models evaluated
25 configurations (§4.1, App. C.3): Jev (hosted TypeSafe API; "Jev 1.13" named for the profiling and SocioBench experiments, no version string for the main Table 1 runs); Kev 0.8B/4B/9B/27B; Intern-Decision 0.8B/2B/4B; Laya; OpenJev-4B-v5; Nimble-9B; NanoJev; LightJev; JevForge-0.8B; and the authors' SII-Decision-4B and SII-Decision-27B (first-token readout of Qwen3.5-4B / Qwen3.8-27B with Reasoning-to-Readout Self-Distillation, 39,279 training questions for the 27B). Generative comparators: Qwen3.5-4B, Qwen3.8-27B, DeepSeek-V4-Flash, GPT-6-Luna, GPT-6-Sol (non-thinking) and Qwen3.5-4B, Qwen3.8-27B (xhigh), DeepSeek-V4-Flash (high), GLM-5.3-Flash (high) (thinking). No run dates or per-model checkpoint hashes in the text read.

## Comparators, tuning-budget parity
All 25 configurations answer the same instances; generative LLMs get a shared system message and JSON schema (strict), temperature 1.0, 8,192-token output budget incl. 4,096 thinking budget; open decision models keep released precision and calibration parameters; Laya and several encoders had input limits raised (Table 9 caption). Calibration parameters for Kev/Intern-Decision (task temperatures) are reported in Table 9. Generative LLMs' probabilities are self-reported in JSON, a different mechanism from decision models (§C.1). No prompt tuning on test data is described; SII-Decision models selected checkpoints on a frozen development set (App. F.2) and the authors' later "newly constructed questions" test is separate (§6.3).

## Reference labels
Source dataset gold labels across 36 datasets (human-annotated, exam keys, benchmark labels; mixed), with two experts verifying that reference answers are manually verified (§3.2). Coded administrative_field in the ledger because the headline mixes label types. Social-survey task uses real respondent answers (SocioBench); the interest-profiling comparison treats a frozen Qwen3-Max profile as reference but "None of the outputs is treated as ground truth" (§5.4.1) (agreement, not accuracy).

## n, sampling, intervals
Headline Table 1 reports point estimates only (no intervals); Fig. 9 uses 95% Wilson intervals; tau-bench run once per test task (single run, temperature 0). Latency on a separate 200-question test stratified into six length bins to 16K tokens (§4.1).

## Test-data exposure
Public benchmarks (e.g. MMLU-type, CLINC150, GPQA, MMLU-Pro, TruthfulQA, AgentHarm, GoEmotions named in §6.3) all predate 2026; no contamination check found. The authors mention newly constructed questions that played no role in training or selection (§6.3).

## Cost, latency, hardware
Local models on NVIDIA H100 (eight H100 80 GB, vLLM 0.29.1rc1, App. C.3; latency bins on RTX 4090 per Fig. 4 caption; single H100 for Fig. 16); Jev and GPT-6 via hosted APIs including network transport. Jev's hosted latency below one second at every length; on inputs up to 1K tokens every local model is faster (SII-Decision-4B under 0.1 s, SII-Decision-27B about 0.2 s); 27B models become slower than Jev at about 2K tokens (§4.2 Finding 4). SocioBench mean latency per item: Jev 0.496 s (Overall), SII-Decision-27B 8.357 s, DeepSeek-V4-Flash-0731 thinking 211.649 s (Table 5). No dollar costs reported in the text read.

## Calibration
ECE with ten equal-width bins over valid responses, plus Brier_raw (§4.1). Jev ECE 0.0532, SII-Decision-27B 0.0149 (lowest in Table 1), best generative GLM-5.3-Flash (high) 0.0784. The authors stress that Jev picks the mode but overstates its probability: on prior items it puts 89.35% mass on the true mode versus 35.60% true (§5.1, Fig. 5). Temperatures for Kev/Intern-Decision are fixed per Table 9 (no new recalibration step described).

## Cascade
None.

## Robustness / other
Long-context degradation (Jev LongBench 93.5% at 4-8k to 74.5% near 20k; middle-position dip 80.4% on BABILong) (§5.2). No option-name or permutation test. English and Chinese instances present (1,800 Chinese) but no per-language table found in the text read.

## Code and data
JEVal data https://huggingface.co/datasets/carlosxiang/JEVal; code https://github.com/amazingljy1206/SII-Decision; models and training data on Hugging Face; project page https://sii-research.github.io/sii-decision/ (front matter).

## Paper's own limitations (§9)
Agentic evaluation limited to tool-using agents and social simulation; limited set of decision models with Jev the primary representative; Reasoning-to-Readout Self-Distillation is one initial training paradigm.

## Notes for the grader
Own-model results (SII-Decision) are reported next to the benchmark on a benchmark the authors built. Election and SocioBench results used an "earlier checkpoint" of SII-Decision-27B for the election (§5.4). Two Jev ElectionSim runs are described as preliminary.
