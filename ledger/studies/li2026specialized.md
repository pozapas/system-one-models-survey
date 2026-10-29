# li2026specialized — Specialized Decision Models vs. General-Purpose LLMs: Benchmarking Jev Across Knowledge, Reasoning, and Multilingual Tasks

- arXiv: 2610.11978v1 [cs.CL], 8 Oct 2026; license arXiv.org perpetual non-exclusive (header). Full text: fulltext/2610.11978.html and .txt.
- Authors (header): Xing Li, Qingcheng Chang, Jinzhong Ning, Changfeng Xu, Shenlong Zhang, Yijia Zhang, Ling Luo, Hongfei Lin. Dalian Maritime University and Dalian University of Technology. Affiliation type: academic. (Sister paper to li2026can, same first author and group.)
- Code and data: no repository or data statement found in the text. Appendix C lists sources of published scores. code_available = no.

## Task and data
Accuracy of Jev's Choice interface on 13 standard multiple-choice benchmarks: MMLU-Pro (10 options), MMLU-Redux, MMLU, GPQA Diamond, C-Eval (Chinese), HellaSwag, WinoGrande, TruthfulQA, ARC-Challenge, MathQA, AQuA-RAT, MMLU-ProX (29 languages), MMMLU (14 languages) (Table 1, Section 3.1). Standard evaluation splits. Item counts given in Appendix A only for MMLU 14,042, TruthfulQA 817, GPQA Diamond 198, ARC-Challenge 1,172, AQuA-RAT 254; Table 3 lists 12,342 (C-Eval), 10,042 (HellaSwag), 1,267 (WinoGrande), 3,548 (ARC) as the item counts of Deussers evaluation. Other n not stated.
Reference labels: the benchmark answer keys (not further described). Coded human_single as "benchmark answer key".

## Decision model, exact version
Jev, "a single Choice request" per item containing the question and candidate answers; selected option is the prediction; single run (Section 3.1). No version string or run date is given for Jev (searched for jev-1.x and dates: none). Version coded "not reported".

## Comparators and tuning parity
19 LLMs in three tiers (Section 3.1): six frontier (GPT-5.6 Sol, Claude Opus 5.5, Gemini 3.8 Flash, Qwen3.8-Flash, Qwen3.8-Max, DeepSeek-V4.1-Flash), seven representative (GPT-4o, Claude 3.5 Sonnet, DeepSeek-R1, DeepSeek-V3, Qwen3-32B, Qwen2.5-72B-Instruct, Llama-3.1-405B-Instruct), six small (Qwen3-8B, Qwen3-4B, Llama-3.1-8B-Instruct, Phi-4-mini-instruct, Gemma-3-4B-IT, Mistral-7B-v0.3).
Jev and the frontier LLMs were evaluated by the authors with a single run each; on GPQA Diamond three frontier scores are vendor reports. Of 169 representative/small model-benchmark pairs, 104 are published scores and 65 were evaluated by the authors; "Published scores differ in prompts, few-shot examples, and reasoning settings, so we use them only for rough comparison" (Section 3.1). The LLM prompting protocol and reasoning settings for the authors' own LLM runs are not described. The paper states "In future work, we will evaluate all tiers under one protocol" (Section 4), so tuning/protocol parity is not established.

## Main results (Table 2 accuracy %, Table 4 frontier median and rank)
Jev: MMLU-Pro 82.3, MMLU-Redux 95.0, MMLU 91.3, GPQA Diamond 74.2, C-Eval 85.3, HellaSwag 89.3, WinoGrande 91.8, TruthfulQA 87.5, ARC-Challenge 97.6, MathQA 75.0, AQuA-RAT 83.1, MMLU-ProX 83.2, MMMLU 85.0.
Frontier median in Table 4 (Jev minus median, rank among evaluated models): MMLU-Redux 93.2 (+1.8, 1/7), ARC-C 95.5 (+2.1, 1/7), TruthfulQA 83.0 (+4.5, 3/7), WinoGrande 92.1 (-0.3), MMLU 92.5 (-1.2), MMLU-ProX 84.5 (-1.3), MMMLU 88.6 (-3.6), HellaSwag 93.8 (-4.5), MMLU-Pro 88.1 (-5.8, 7/7), AQuA-RAT 91.0 (-7.9, 7/7), C-Eval 93.6 (-8.3), GPQA Diamond 83.1 (-8.9, 4/4), MathQA 92.7 (-17.7, 7/7). Jev is below all 19 LLMs on MathQA (Section 3.2, Abstract). TruthfulQA published scores for some comparators use MC2 and are excluded from some counts (Appendix A).
Intervals: 95% Wilson intervals for Jev only on GPQA Diamond [67.7, 79.8], AQuA-RAT [78.0, 87.2], ARC-Challenge [96.6, 98.3] (Appendix A, Uncertainty). No intervals elsewhere; no paired tests.
Cross-check with an independent evaluation (Table 3, Deusser et al. 2026): MMLU 91.3 vs 91.8, C-Eval 85.3 vs 83.9, HellaSwag 89.3 vs 95.5 (6.2 points lower here, attributed to request template and option presentation), WinoGrande 91.8 vs 91.4, ARC 97.6 vs 98.8 (different subset).

## Cost, latency, calibration, cascade
No cost or latency reported. No calibration analysis; option probabilities are not used. No cascade evaluated; the Conclusion lists whether option probabilities can indicate when to pass a question to a reasoning model as future work (Section 4). Option-name and template sensitivity is cited, not tested here, though the HellaSwag gap to an independent evaluation is attributed to the request template (Section 3.2).

## Test-set exposure
All 13 benchmarks are public before 2026 with answer keys public; no contamination check described. The paper itself notes that results on knowledge benchmarks may reflect how much knowledge Jev stores (Section 3.2) but does not test memorisation.

## Limitations (paper)
No dedicated limitations section. Stated caveats: published scores are only for rough comparison (Section 3.1); the HellaSwag gap to an independent evaluation may partly reflect the authors' template (Section 3.2); future work will use one protocol for all tiers (Section 4). Single runs, no variance estimate for the LLMs.
