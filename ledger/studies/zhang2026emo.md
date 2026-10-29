# Zhang and Yu (2026), "Emo-Jev: Probabilistic Reasoning for Emotion Classification with Jev"

## Identification
- arXiv 2610.08829v1 [cs.CL], 27 Sep 2026 (header). License CC BY 4.0. The arXiv ID prefix is 2610 although the header date is 27 Sep 2026.
- Authors: Yazhou Zhang, Junhao Yu; "School of Computer Science and Technology, Tianjin University, Tianjin, China" (byline). affiliation_type = academic.
- Code/data availability: no repository, supplement or artifact statement in the text (searched for github, code, available). code_available = no. Dataset links: Humor Detection Dataset on Kaggle (footnote 1).
- Note: another study by the batch has the key `zhang2026same` (a different paper); this key is `zhang2026emo`.

## Task and data
- Eight text-classification benchmarks in four tasks (Section 4.1, Table 1): sentiment SST-5 (5 labels, test 2,210) and TweetEval-Sentiment (3, 12,284); emotion SemEval-2018 Task 1 E-c (11 labels, multi-label, 3,259) and text-only CMMA (Chinese, 7, 3,961); sarcasm SemEval-2018 Task 3A (binary, 784) and iSarcasmEval Task A (binary, 1,400); humor Humor Detection (HD) Dataset (binary, test 50) and HaHackathon Task 1A (binary, 1,000). Test sizes from Table 1. Multi-label threshold fixed at tau = 0.5 (Section 4.2).
- Gold labels are the datasets' own annotations (crowd or annotator-collected); ledger codes human_crowd. Label provenance is not described in the paper. All public datasets released before 2026; no contamination check. HD has only 50 test items.
- No sampling design beyond "Test size"; unclear whether full test sets or subsets were used for the five LLMs.

## Models and comparators
- Jev `jev-1.13.0` (Table 2 caption): "Jev uses jev-1.13.0; D uses lambda = 0.5, and SC uses M = 3 with path-selection seed 42". Training-free frozen Jev. Jev-Direct baseline = direct label question; Emo-Jev-D = atomic judgments plus decision rules fused with direct probabilities at lambda = 0.5; Emo-Jev-SC = multiple judgment paths aggregated (Sections 3.3, 3.4). Run dates and API access route not stated.
- Comparators: GPT-6 Luna, Gemini 3.8 Flash, Qwen 3.7 Plus, DeepSeek V4.1 Flash, Doubao-Seed-2.0-mini, each under Input-Output (IO) and Chain-of-Thought (CoT) prompting, zero-shot with no demonstrations; Qwen, DeepSeek and Doubao receive fixed Chinese instructions, GPT-6 Luna and Gemini English instructions (Section 4.2). Model identifiers are product names only (no dated revisions). Tuning parity: same zero-shot prompt per model; Jev uses author-designed predefined question inventories (Sections 3.3, Limitations), so Jev's question wording received design effort not matched by tuning the LLM prompts; the paper does not describe prompt selection on test data.
- Reported hyperparameters lambda = 0.5 and M = 3 are fixed for the main experiments; Table 4 averages five path-selection seeds (42-46) for M sweeps (Section 4.4). Whether lambda or the path inventory was chosen with test-set feedback is not stated.

## Statistics
- Accuracy and macro-F1 per dataset, single run, no confidence intervals or significance tests (Table 2). Average macro-F1 is an unweighted mean of eight datasets (Section 4.3: "62.93% average macro-F1"). Differences between configurations are stated as relative percentages.
- Calibration: none reported. Jev probabilities are used for argmax and composition only. calibration_quantity none; post_hoc_calibration none.

## Cost and latency
- Table 5 (across eight benchmarks): Jev-Direct 403.02 input and 64.53 output tokens, median latency 250 ms, P95 313 ms, cost 0.0169 per 1K texts (USD); Gemini 3.8 Flash IO median 3,156 ms, 0.47043 per 1K; DeepSeek V4.1 Flash IO median 453 ms, 0.13958 per 1K; Emo-Jev-D median 613 ms, at least 0.0403 per 1K; Emo-Jev-SC median 1,826 ms, at least 0.1282 per 1K (lower bounds because retry usage is missing) (Section 4.5, Table 5). Jev cost reflects free outputs under the applied pricing (Section 4.5). Hardware/provider for latency not stated ("observed" client-side latency).

## Cascade, option-name, cardinality, robustness
- No cascade or escalation analysis. The SC path-count sweep (M = 1, 3, 5, 10) is the only robustness analysis (Table 4). No option-name or order test. Label cardinality ranges 2 to 11.

## Authors' stated limitations (Limitations section after Conclusion)
- Two datasets per task family, text only; may not generalize to other domains, languages or multimodal settings; predefined question inventories and fixed composition rules; alternative decompositions may differ.
