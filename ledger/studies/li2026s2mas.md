# li2026s2mas: S2-MAS: A Society-Scale Multi-Agent Simulation Framework with 500 Million Household Persona Agents

arXiv:2610.27746, text read from the HTML page which shows v4 [cs.MA], 23 Oct 2026 (the batch list dates the first version 2026-10-20; later versions may differ, and the GPT-6 rows were evaluated 20 to 22 October 2026 so they cannot be in v1) (fulltext/2610.27746.html and .txt). Extractor batch V18.

## Authors and affiliation
Yang Li, Yike Wang, Di Wan, Chujun He, Zongsi Xu, Yitao Yu, Quanfeng Lu and others (22 authors), corresponding author Ye Luo. The University of Hong Kong (main), HKU Business School Shenzhen Research Institutes, Risk Management Institute NUS, Jiangxi Science and Technology Normal University, Nanyang Technological University, University of Michigan, Chinese University of Hong Kong (title block). Affiliation type: academic.

## Task and data
A simulation framework (500 million synthetic household personas, Genese engine, financial application ledgers, 12 million simulated agents). The part that measures decision models is §5.3 and Supplementary M5: a one-shot consumer financial-choice benchmark where each model predicts recorded survey answers and coded respondent targets (financial, occupation, education categories) from a household state, a question and named alternatives. Test: 240,458 held-out QA records, 119 question versions, 8,275 household/respondent groups, from a real-survey corpus of 4,172,421 QA observations in 1,211 question or task versions (M1, Table 4a). English questions by default. The source survey is not named in the portions read.

## Decision models evaluated
- sharp-421m-mlx (the authors' model): Laya (421M encoder) adapted by SFT + RLCD on 2,925,263 examples in MLX CUDA FP16; also sharp-4b (Kev-style 4B LoRA plus decision head), sharp-9b, sharp-322m (Chinese, multilingual base) (Table 2).
- Comparators in Table 4a: Jev 1.13 ("jev-1.13.0 typed-choice outputs", API, provider precision; size not disclosed); Kev 4B (CUDA BF16); Clef Flash 9B (BF16); Tev1 4B (BF16); Base Laya 421M; Laya-Finance (hravi) 421M FP32. Text-output LLMs: GLM-5.3-Flash (320B), DeepSeek-V4.1-Flash-1017 (thinking off, 4,096 output tokens), GPT-6-Luna and GPT-6-Astra (evaluated 20 to 22 October 2026, low reasoning effort, 4,096-token budget; Astra on a 500-group sample of 14,441 records). Some rows (GLiNER, OpenDecider) appear in the figure and supplementary tables and are not extracted.
- Jev run dates for the benchmark are not given; the returned version string jev-1.13.0 is recorded for the 11 October 2026 latency benchmark (M9) and "Jev uses jev-1.13.0 typed-choice outputs" for the accuracy benchmark (M5).

## Comparators and tuning-budget parity
All models receive the same states, questions and semantic alternatives with model-specific adapters (M5); text-output adapters use compact JSON, one retry for transport failures, no repair of invalid answers. sharp-421m is trained on 2.93 million in-domain survey examples (48 times the Laya-Fintiment training set); Jev, Kev, Clef, Tev1, GLM, DeepSeek and GPT are used zero-shot as released. Question-majority baseline uses training labels. The authors acknowledge the supervised adaptation as the source of gains ("supervised adaptation supplies most of the encoder's predictive gain", §5.2). Input caps differ by model (512 input / 256 head tokens for sharp and base Laya MLX, 2,048 for OpenDecider; M5).

## Reference labels
Recorded questionnaire answers by real survey respondents and targets coded from observed financial, occupation and education categories (M1, M5). Coded human_single (self-reported survey answers); a mix of answers and coded respondent attributes.

## n and sampling
240,458 records; paired intervals use 1,000 joint bootstrap resamples of the 8,275 household/respondent groups (accuracy and F1 differences for sharp vs Jev, GLM, Clef, Laya-Finance). Per-model accuracy has no interval in Table 4a; question-macro F1 gives equal weight to each of the 119 question versions. Invalid responses count as incorrect (GLM 98, DeepSeek 58).

## Test-set exposure
Survey-derived QA under restricted access; test questions are held out from sharp training by household/respondent group split. Whether the survey data are public is not stated; coded private. The comparator models could not have been trained on these private survey records, though public surveys of the same type could be in pretraining.

## Cost and latency
M9 single-request deployment benchmark on one NVIDIA A100 PCIe 40GB, batch size and concurrency one, three fixed Chinese financial-choice cases, 20 timed repetitions per case (60 calls per arm), measured 11 October 2026 with the sharp-322m checkpoint: mean latency 9.10 ms (sharp-322m-mlx), 22.06 ms (PyTorch), 206.77 ms (Jev 1.13 API including HTTPS round trip); choices per second 109.88 vs 4.84; input-token throughput 36,955 vs 1,627 tokens/s, a ratio of 22.72 (Table S5b). Jev server hardware and precision are provider-managed; no money cost reported.

## Calibration
None reported for Jev or others (probabilities are consumed by the simulation only).

## Cascade or escalation
None.

## Option-name, cardinality, language, robustness
Matched information controls on 20,000 held-out records (Table 3): sharp-421m full profile 74.40, no profile 71.19, wrong same-question profile 69.56 against the question-majority baseline 71.71 on accuracy; 119 question versions with varying option sets. Chinese and English views exist; most evaluations are English; sharp-322m is evaluated in Chinese.

## Code and data
Weights at https://huggingface.co/ya9919/sharp-4b, sharp-421m, sharp-421m-mlx under noncommercial research terms; reproduction code and aggregates accompany the repository; survey-derived QA and trajectories restricted; GENESE/MAS engine private (Data and code availability).

## Authors' own limitations
No dedicated limitations section. The Discussion (§7) states "The evidence supports in-scenario response prediction and one-shot scalability; it does not establish generalization to other decision domains", and that all 2,364,307 households aged 65 or above select deferral in both conditions, a boundary whose correspondence to observed lifecycle demand "remains untested". The paper also states that Clef Flash 9B has the highest F1 (38.5193) and that sharp-421m reaches a similar F1 with higher accuracy (M5).

## Notes for the grader
The headline contrast is between a model trained on 2.93 million in-domain survey examples and zero-shot hosted or open models. Jev 1.13 (65.26%) scores below the question-majority baseline (71.77%) on accuracy and is within 0.6 F1 points of sharp-421m-mlx (37.48 vs 38.37). The abstract's accuracy superiority statement holds for the full test only against GLM, Jev, DeepSeek and GPT-6-Luna, with GPT-6-Astra on a 500-group sample. The paper's main contribution is the simulation framework, not the decision-model comparison.
