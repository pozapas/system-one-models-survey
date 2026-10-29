# sharma2026typedbench — TypedBench: A Benchmark for Calibration, Framing Sensitivity, and Cost in System One Decision Models

arXiv:2610.11392v2 [cs.AI], 9 Oct 2026 (first version 8 Oct 2026; the HTML retrieved is v2). Retrieved from https://arxiv.org/html/2610.11392 (fulltext/2610.11392.html and .txt). The ledger date is the first-version date from the screening file.

## Authors and affiliation

Rahul Sharma, Andrew B. Duncan, Gaetan Marceau Caron, Sebastian J. Vollmer. DFKI GmbH, RPTU Kaiserslautern, Imperial College London, Mila - Quebec AI Institute (title block). Affiliation type academic.

## Task and data

Benchmark for typed decision models built from seven programmatic generators with policy-derived labels (support tickets, phishing email, RAG relevance up to 255 options, log triage, policy compliance, guardrail intent, multilingual tickets in de/es/fr/hi) and nine suites A to I (Sec. 3, Tables 1 and 2). Labels are computed by executing a stated rule over declared facts; unit tests and a frontier-LLM solvability audit check items (Sec. 3.2, App. J). Suite A n = 500 items per generator for tickets and phishing, five paraphrases, three criteria variants, three option permutations plus control arms; sweeps n = 100 to 500 per level; four further generators n = 300 canonical wording only (Sec. 4.1, App. B).

## Decision models evaluated

Jev 1.13.0, hosted, first-party API ("Jev answered every request as jev-1.13.0; a 200-item canary (1,100 answers) recorded at session start showed no drift", App. A). Laya 0.3.4 (421M ModernBERT-large encoder with decision head, English and typed-decisions checkpoints, bf16 local). Kev 0.8B, 4B, 9B (LoRA plus pointer head on Qwen3.5 bases, bf16 local, Jev-compatible API). All local models on one NVIDIA GB10 with 128 GB unified memory. No run dates stated beyond the canary.

## Comparators and tuning parity

Majority prior, generators' regex rules, embedding nearest-description (all-MiniLM-L6-v2), zero-shot NLI (bart-large-mnli), DistilBERT fine-tuned 2 epochs on 2,070 to 5,977 deduplicated items from a disjoint seed (accuracy 1.000 everywhere, showing labels are learnable), and two instruction-tuned LLMs restricted to option letters with first-token log-probabilities (Gemma 4 31B, Qwen3.5-9B; reasoning disabled, via OpenRouter) (Sec. 4.1, App. A). All typed models see identical items and the same wordings, fixed before evaluation. The wording variants were "written to mislead" for adversarial arms, fixed before evaluation (Sec. 3.3). Hosted model ran on sessions with drift canary; no per-model prompt tuning reported.

## Reference labels

Programmatic policy rules over declared facts (synthetic). Coded synthetic.

## n, sampling, intervals

Item-level paired bootstrap (10,000 resamples) and Holm-corrected McNemar's test; at n = 500 the 95% interval near accuracy 0.5 is about +/- 4.4 points (Sec. 3.6, App. C). Accuracy reported as median and [min, max] over friendly wordings. Table 4 intervals resample 15 ticket templates. Single seed (42) for items.

## Test-set exposure

Fresh generated items (hash-verified, version-controlled generators), so "no item can have appeared in a training set" (Sec. 6); but templated text finite (about 590 distinct phishing texts up to digits, App. A). Coded new.

## Cost and latency

Jev p50 233 ms per question via API (includes network) on tickets.priority; hosted latency flat as questions are added, local Kev slows in proportion to question count; Jev's accuracy and latency stay flat up to 255 options and 30k tokens, decoders slow to several seconds, encoders silently truncate (Sec. 4.2, Fig. 3). Jev median 784 billed tokens per request (App. A). One hosted request with a single question costs 41% (phishing) and 46% (tickets) of a request with all questions (Table 13 caption). The paper reports its own evaluation spend; not carried to the ledger.

## Calibration

Top-label ECE with 15 equal-width bins, smooth calibration error, Brier with Murphy decomposition, NLL (floor 1e-4), each ECE as a ratio to its null ECE (200 label resamplings of a perfectly calibrated predictor); temperature refit on one half and evaluated on the other (Sec. 3.4). Jev priority ECE/null 2.2, T = 0.66 (under-confident, all Suite A temperature refits below 1); kept 0.89 mean mass on its top level when the tier cue was removed. Decoders also under-confident, encoders mostly over-confident. Acting on Jev's probabilities (Bayes policy) doubles cost on tickets.priority versus its top answer (1,080 argmax vs 2,300 Bayes per 10^4 decisions, -1,220 [-2,040, -600]); for weaker Kev-0.8B and Kev-4B Bayes saves cost, for Kev-9B it hurts (-3,180). On phishing Bayes flags 498 of 500 emails for Jev (Sec. 4.2).

## Cascade or escalation

Suite H hybrid routing: escalate the encoder's least confident answers to Jev; on phishing, escalating about a third of Laya-english answers (t = 0.7) closes half of the accuracy gap (0.706 alone, 0.858 hybrid, 0.804 random, Jev alone 0.998) but every request still needs a hosted call (Sec. 4.2, App. G, Table 13).

## Option-name, order, language, robustness

Wording sensitivity: tickets.priority median 0.874 with range [0.708, 0.946] (24 points). Option order permuted three times per item with chi-square test for positional bias (Sec. 3.3). Surface perturbations and distractors move Jev and Kev 4B/9B by a few points; both encoders lose a large share; out-of-scope abstention with a "none of the above" option: decoders and English encoder almost always, typed-decisions encoder 3 of 4, Jev about half; prior shift: Jev, Kev 4B and 9B track base rates, encoders anchored (Sec. 4.2, App. E). Negation: Jev and larger decoders return complementary probabilities; paraphrased phishing negation costs Jev 23 points (Table 12). Translated tickets: Jev keeps its English accuracy (0.92 to 0.99 across languages, Table 3).

## Code and data availability

No release statement for the benchmark code or manifests found in the text read (the paper says generators are hash-verified and version-controlled); coded no.

## Paper's own limitations (Sec. 6)

Generated, templated text rather than native text (a fine-tuned encoder solves every question); discrimination among strong models rests on rule-application questions; harder policies and graded answers left to future generators; a native-text tier with human labels proposed.
