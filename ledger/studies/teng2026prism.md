# teng2026prism — Prism-1: Position- and Rival-Independent Scoring for System One Models

arXiv:2610.22066v2 [cs.AI], 16 Oct 2026 as retrieved (first version 15 Oct 2026 per the batch list); CC BY 4.0. HTML from https://arxiv.org/html/2610.22066. Extractor: batch V15.

## Authors and affiliation
Yao Long Teng, Jianguo Huang, Jiayi Cai, Yanchen Deng (corresponding), Bo An, Nanyang Technological University, Singapore (title page). Affiliation type: academic.

## Task and data
Axioms for decision reads: order invariance and Luce's choice axiom (Section 2). Tests: flip rate (share of answers changed by one seeded shuffle), switch rate and probability drift when one irrelevant option is added, steering rate (worst of 10 added candidates), order-robust accuracy (right in both source and shuffled order), injected-option redirect (Section 2 Metrics; 5.3). Benchmark of five sets, 2,521 evaluation questions: Banking20 (300 test messages, 20 intents), Newsgroups (300 posts, 20 topics), BEV (1,182 choice questions, 100 from each of 12 domains of the test split, revision 11ed9b5 of avbiswas/bev-decision), Typed Decisions (600), JevBench (139 public choice tasks, no training data, held-out) (Section 5.1; Table 3). Training set 9,100 questions (Appendix B).

## Decision models evaluated
Prism-1 (authors' method) on Gemma 4 12B (google/gemma-4-12B-it at revision 707f0a3) and Qwen3-8B with LoRA rank 16, trained on the shared 9.1k questions (Section 5.1; Appendix B). Closed commercial: "Jev 1.13.0 through TypeSafe's API" and "Mercury Decide's release of 30 September 2026 through OpenRouter's Decisions API" (Appendix C.1). Published: Torchcast Decision 12B, served with a pinned vLLM 0.30.0 image, reproducing its published JevBench score (203 of 231) (Appendix B). No run dates for Jev or Mercury. Neither API is deterministic: the identical question changes its answer in 1.3% (Jev) and 0.7% (Mercury) of cases (Appendix C.1).

## Comparators and tuning budget
Trained SCQ (single-choice-question letter read), cyclic averaging, SCQ with sorted options, Set-Based Prompting (training-free), Set-LLM (the authors' re-implementation, since its code is not public). "Every trained method uses the same data and budget"; SCQ and Prism-1 three seeds, Set-LLM two (Section 5.1). Jev, Mercury Decide and Torchcast Decision are used as published and "not trained on our data" (Table 1 caption), so they are not tuning-matched to Prism-1; the paper reports them as published references. The Jev rows therefore measure an order-robustness property of a hosted API, not a trained-vs-trained comparison. Jev rows have accuracy only on tasks where the authors sent questions in the listed order.

## Reference labels
Dataset-native keys: public classification datasets (Banking, 20 Newsgroups) and the benchmark creators' keys for BEV, Typed Decisions and JevBench; how those keys were produced is not described here. Coded unclear. Flip, drift and steering rates require no labels.

## n, sampling and intervals
Exact two-sided McNemar tests per set or pooled over 2,521 questions (Appendix B). Table 1 values are point means over five sets and 1 to 3 seeds; no confidence intervals around the means. Pooled differences between Prism-1 and trained SCQ were not significant (p at least 0.13). Jev flip rate has a noise floor from 31 identical copies per question (Appendix C.1).

## Test-data exposure
Banking and Newsgroups are old public datasets; BEV, Typed Decisions and JevBench are 2026 public benchmarks. JevBench was held out of Prism-1 training; whether Jev, Mercury or the base models trained on any set is unknown. No contamination check. Coded public-pre-2026 for Banking20 and unclear for the pooled rows.

## Cost and latency
Prism-1 processes 221 tokens versus 282 for SCQ and 322 for Set-LLM on Banking20, 356 versus 417 and 413 on Newsgroups; 58 and 60 ms on one H100 with Gemma 4 12B versus 60 to 63 ms for SCQ (Table 5). One epoch of training is 284 steps, 50 to 85 minutes on one H100 (Appendix B). No cost or latency for Jev or Mercury.

## Calibration
Prism-1 ECE 5.3% and 5.4% versus SCQ 4.9% and 5.4% and Set-LLM 9.3% and 7.5%, "without any calibration step"; at 95% accuracy Prism-1 decides 61.5% and 51.4% of questions, 3.1 and 2.9 points fewer than SCQ (Section 5.2; Appendix C.3). Binning not stated. ECE for Jev and Mercury Decide is not reported (Jev rounds probabilities to two decimals so the authors take its reported choice).

## Cascade or escalation
None.

## Option-name, cardinality, language and robustness tests
This is the core of the paper: shuffles (Jev flips 4.7%, Mercury Decide 7.6%, Torchcast 9.1%, trained SCQ about 7%), added irrelevant option (Jev drift 2.9 points, steering 10.9%), injected options naming a wrong option as correct (Jev 3.9% to the named option, 9.3% to any other), sorted-order change Z-A vs A-Z (7.2 to 8.5% for SCQ), growth to 5, 10, 20 options (Figure 5), per-domain breakdown on BEV (Figure 3). Only English text sets.

## Code and data
No repository link found for Prism-1 in the text or HTML links; Set-LLM code is not public. Coded no.

## Authors' stated limitations
Prism-1 needs fine-tuning (untrained it answers 28.5% and 32.5% of validation questions correctly); gives up comparison between options (poor fit for "none of the above" or "odd one out"); does not protect the state from injected text; near-duplicate treatment follows the choice axiom; trails SCQ by 3.6 and 4.1 points on held-out JevBench; at most 20 options; two open models of 8 to 12B parameters; one to three seeds per configuration; Set-LLM is a re-implementation (Section 7).
