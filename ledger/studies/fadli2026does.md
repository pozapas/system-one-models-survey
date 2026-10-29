# fadli2026does — Does System One Transfer? Calibrated Typed-Decision Models, Label Budgets, and Translation for Indonesian Regional Languages

- arXiv: 2610.14112 (first version, submitted 9 Oct 2026 per the screening list). The arXiv HTML build is unavailable ("No HTML for '2610.14112'"), so the PDF was downloaded (fulltext/2610.14112.pdf) and converted with pdftotext (fulltext/2610.14112.txt). Page numbers below follow the PDF (11 pages of text). Special characters (en dashes, apostrophes) are garbled in the text copy.
- Authors: Romi Fadli, Rusdah, Wahyu Ramadani Putri Utami, Zulfa Malika Amana; Faculty of Information Technology, Universitas Budi Luhur, Jakarta (title block). Affiliation type: academic. Funding: none, "all costs were covered personally by the authors" (Statements).
- Code and data: pre-registration, fixed subsets, learning-curve splits, all predictions and code at https://github.com/tnromy/evaluating-system-one-models-for-indonesian-regional-languages (Availability of Data and Materials; Code Availability), tagged prereg-v1. Jev outputs released for benchmarking only.

## Task and data
Sentiment and emotion classification in Indonesian regional languages (Section 3.1, Table 1).
- NusaX-senti: 1,000 parallel sentences in 10 regional languages plus Indonesian and English, three labels; 12 languages, 400 test sentences per language, 4,800 test items.
- NusaTranslation sentiment (NT-senti, two labels, 7 languages, 1,200 test per language, 8,400 items) and emotion (NT-emot, five labels, 7 languages, 1,000 per language, 7,000 items).
- Fixed stratified test subsets for the LLM ladder: 100 per language for NusaX (1,200), 200 for NT-senti and NT-emot (1,400 each) (Table 1).
- Reference labels: the benchmark annotations by the dataset authors; the paper does not describe their production beyond sentences "written or translated by native speakers". Coded human_single as "dataset labels, process not described".

## Models and versions
- Jev: "queried through the System One endpoint of OpenRouter; every response came from the snapshot typesafe/jev-1.13-20260917" (Section 3.2). Two pre-registered formulations: A1 noul_en (one yes/no question per label, probabilities normalised; chosen on the validation pilot) and A1-choice choice_en (native choice distribution, used for calibration). A4 presents the Indonesian source sentence; A3 translates with NLLB-200 600M first. Same English instruction and label descriptions for all zero-shot arms; option names held fixed. Query dates not stated.
- Open decision model: Laya-multilingual (322M, mmBERT encoder), zero-shot (C2) and fine-tuned with the official RLCD recipe, per language and pooled (C1), temperature fitted on validation (Section 3.3). No revision hash.
- Comparators: DeepSeek V4.1 Flash without reasoning, temperature 1, token log-probabilities (D1, primary LLM); ladder on subsets: Claude Haiku 4.5, Sonnet 5, Opus 5.5 and GPT-6 Luna, GPT-6 Sol, GPT-5.6 Terra at low reasoning effort via Claude Code and Codex CLI with a JSON schema and verbalised probabilities (D3, D4); trained arms B1 (NB, SVM, logistic regression, TF-IDF/BoW), B2 IndoBERT-base, B3 XLM-R-base, three seeds each (Sections 3.2, 3.3).

## Tuning-budget parity
Zero-shot arms share one specification. Trained arms get the full training data (500 per language for NusaX, 3,400/3,000 for NT) and nested subsets n = 10 to 500 (up to 1,000 for NT), hyperparameters selected on validation (B2/B3 on a 20-point grid on the Indonesian NusaX validation split). Jev's cascade fraction r chosen on a validation pilot. Jev query formulation chosen by a rule committed before the first call. The LLM ladder uses different elicitation (CLI clients, verbalised confidence), so latency and calibration are not like for like (Section 4.6, 4.10).

## Design, n and intervals
Pre-registered (prereg-v1) before test splits were opened (Section 3.5); deviations logged (Section 3.6). Paired exact McNemar tests with Holm correction; cluster bootstrap resampling sentences with all language versions (B = 2,000); logistic mixed model for H1a. 1,270 fine-tuning runs on Tesla T4 GPUs (24.3 GPU-hours); 102,400 zero-shot test predictions (Section 3.3). Unparseable answers count wrong, at most 0.086% per arm.

## Results (selected)
- Table 3 macro-F1 (NusaX / NT-senti / NT-emot): Jev A1 0.782 / 0.781 / 0.629; A1-choice 0.785 / 0.783 / 0.631; DeepSeek 0.786 / 0.795 / 0.658; B1-LR 0.752 / 0.805 / 0.603; IndoBERT per language 0.792 / 0.824 / 0.647; XLM-R per language 0.783 / 0.827 / 0.647; XLM-R pooled NusaX 0.806; Laya fine-tuned pooled 0.786 / 0.815 / 0.611; Laya zero-shot 0.502 / 0.590 / 0.367. Cost per 1,000 decisions Jev USD 0.015 to 0.019, DeepSeek 0.085 to 0.119; median latency Jev 355 to 369 ms, DeepSeek 763 to 853 ms.
- RQ1 (Table 4): overlap effect on log-odds per SD 0.33 [0.17, 0.49] NusaX, 0.14 [0.03, 0.24] NT-senti, 0.42 [0.31, 0.55] NT-emot; Indonesian source sentence raises accuracy by 0.5 to 37.2 points on NusaX (largest Buginese +37.2), 1.6 to 16.2 on NT-senti, 5.0 to 34.1 on NT-emot; H1b not confirmed (NT-senti 3 of 7).
- RQ2 (Table 5): ECE regional minus Indonesian: NusaX -0.036 [-0.054, -0.018], NT-senti -0.020 [-0.037, -0.010], NT-emot 0.010 [-0.013, 0.024]; AURC +0.058, +0.039, +0.090 (all intervals above zero). Jev ECE lower than DeepSeek by 0.039 to 0.127; 15 equal-width bins with equal-mass check (Section 3.4). No post-hoc recalibration for Jev.
- RQ3 (Table 6): classical baseline at n = 500 falls short of Jev in 9 of 10 NusaX regional languages; Buginese Jev 0.514, 25 labels suffice; H3a not confirmed (Spearman 0.52, p = 0.061).
- RQ4 (Table 7): cascades at r chosen on validation: NT-emot IndoBERT r = 30% macro-F1 0.676, +2.9 [1.2, 4.5] over IndoBERT; NusaX DeepSeek r = 60% 0.789, +0.2 [0.1, 0.4] at USD 0.078 per 1,000; NT-senti Laya-ft -2.1 [-3.8, -0.4]. "8 of 9 cascades are at least as accurate as the better of their two components"; routing to DeepSeek matches DeepSeek at 24 to 77% lower API cost (Section 4.5, Abstract).
- LLM ladder (Table 8, subsets): Claude Opus 5.5 0.890 / 0.877 / 0.770 against Jev 0.783 / 0.783 / 0.640; accuracy difference to Jev +10.2 / +7.5 / +13.6; Sonnet 5 +7.8 / +6.5 / +9.1; GPT-6 Sol +8.1 / +6.8 / +9.4; Haiku 4.5 -6.5 / -4.4 / -1.6. Sonnet and Opus cost 347 to 618 times as much as Jev per decision; GPT cost not reported (subscription).
- Translate-test lowers accuracy in 6 of 13 versions (Section 4.7). Three Jev formulations differ by at most 1.1 macro-F1 points, Cohen kappa 0.87 to 0.95 (option names held fixed).

## Cost, latency, hardware
API cost of all Jev arms USD 0.98 and DeepSeek USD 2.04 at list prices (Section 3.3) are the authors' spending and are not coded. Per-decision cost and latency are coded from Table 3. Local fallbacks measured on a laptop RTX 3050 Ti (5.9 ms IndoBERT, 79 ms Laya per routed decision); calls from Jakarta.

## Test-set exposure
NusaX public since 2022 (closed models may have seen it; "Jev cannot be probed for memorisation because it does not generate text"); NusaTranslation more recent; both public before 2026 (Section 4.10).

## Limitations (Section 4.10, Conclusion)
Two task families; translated rather than spontaneous regional text; one dated snapshot of a commercial service; low power of the H3a test (nine of ten budgets tied); LLM ladder via CLI clients on subsets with verbalised confidences not comparable to model probabilities; local latency on one laptop GPU.
