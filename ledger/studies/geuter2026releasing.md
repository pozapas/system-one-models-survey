# geuter2026releasing: Releasing the Inner Jev, A Simple Recipe for Open Decision Models

arXiv:2610.17205v1 [cs.AI], 12 Oct 2026 (header line; license arXiv perpetual non-exclusive). Full text: `fulltext/2610.17205.html` and `.txt`. Extractor batch V12.

## Authors and affiliations

Jonathan Geuter (Harvard University; Kempner Institute; equal contribution), Andrew Cheng (Harvard University), David Alvarez-Melis (Harvard University; Kempner Institute). Funding: Kempner Graduate Fellowship, NSF award 2229881 (Acknowledgments). Affiliation type: academic. AI statement: authors used AI agents for code, experiments and writing.

## Task and data

Own-model paper. Open instruction-tuned LLMs read out answer-letter logits (A to P, up to 16 options) at the last prompt position, softmax over the K valid letters, to produce a probability per option in one forward pass (Sec. 4, Eq. 1). A "decision head" z = W0 h + A std(h) + b starts at the LM-head letter rows (correction initialised at zero), trained with rank-32 LoRA (alpha 64) on all attention and MLP projections for 400 steps (Sec. 4). Four backbones, each zero-shot and trained: Gemma 4 31B, Gemma 4 12B, Qwen3.6-27B, Qwen3.5-4B (Sec. 5 Setup). The trained 31B is released as Jeff-1.0-Large (seed 1); other releases are Jeff-1.0-Qwen-27B, Jeff-1.0-Medium (Gemma 4 12B), Jeff-1.0-Qwen-4B (Sec. 5.2).

New evaluation set OpenDecisions: 2,352 questions in 11 families (1,178 choice, 586 yes/no, 588 score), four difficulty tiers, 23 languages (78% English), designed to follow the published composition of JevBench v1.6 (Sec. 3, Table 1). Capability = (I + C) / 2, I chance-corrected accuracy with tier weights 0.1, 0.2, 0.3, 0.4, C an ECE/RPS-based score 100(1 - ECE/0.5) (Sec. 3 Scoring).

Other evaluation sets (Sec. 5.3, App. D): JevBench-Open (231 public items); official JevBench leaderboard (1,500-item draws, 300 public and 1,200 sealed); seven held-out public decision datasets, 9,212 items (TREC 500, CB 56, WANLI 256, SemIf authored 144, SemIf perturbation 108, TypeSafe 348, decider 29 held-out tasks 7,800; Table 4); six knowledge-heavy MC benchmarks in seeded samples (BoolQ 500, MMLU 1,200, MMLU-Pro 800, ARC-Challenge 600, WinoGrande 500, SciQ 400; Table 15).

Training pool 417,825 rows: decider public mixture 300,042 (79 tasks), Civil Comments 30,000, Measuring Hate Speech 30,000, STS-B 4,760, ChaosNLI 2,886, synthetic documents 30,641, decider custom questions 19,496 (Table 2). 50,137 rows carry soft labels from two LLM teachers (Qwen3.5-122B-A10B and Qwen3.6-27B).

## Decision models and versions

- Jev: "Jev 1.13.0 (API)" in Tables 3, 4, 14, 15, 19; accessed through the API; JevBench accessed October 10, 2026; paper reports JevBench versions 1.6.x and 1.7 (reference list, JevBench maintainers entry). Exact Jev API run dates are not stated beyond "October 2026".
- 13 public open systems "using their authors' implementations": Eikos-27B, Quyet-1.0-Large/Medium, deck31b, AutoJev-27B, Torchcast-decision-12B, Winnow-12B, Cygnet, Clef, Plumb-4B, Open-Jev-27B, decider-4b-v2, SemIf (Table 3). Plus 17 public systems run in App. C for the leaderboard-agreement check.
- Authors' models above. Backbone checkpoint names: gemma-4-31b-it, gemma-4-12b-it, Qwen3.6-27B, Qwen3.5-4B (reference list), accessed October 2026.

## Comparators and tuning-budget parity

Competing systems are run as their authors serve them. For each public system the authors report the better of original predictions and predictions recalibrated with the authors' own temperatures, "based on its OpenDecisions score. This favors the competing systems" (Sec. 5 Setup, Table 19). Jev is reported without extra calibration because temperature scaling lowers its Capability from 80.1 to 78.8. The authors' own recipe was chosen on OpenDecisions ("Since we selected our training recipe using OpenDecisions"), so OpenDecisions is a development set; seven held-out datasets and the leaderboard serve as external checks (Sec. 5 Setup; App. C.1). For Qwen3.5-4B three recipe changes were added after the base recipe failed (Sec. 4).

## Reference labels

OpenDecisions: 599 items written and labelled by code; 1,443 written by LLM authoring agents (Claude Opus 4.8 and 5.5) and kept only if a blind panel of three open models (Qwen3.8-27B, gpt-oss-120b, GLM-4.7-Flash) agreed with the author's answer (all three, or two with mean probability at least 0.5 on that answer); 310 real user requests answered by the same panel and kept when all agree (Sec. 3 Labels, Table 1). No human labelling of OpenDecisions. 35 plus 94 calibration items have exact answer probabilities. Held-out public sets: TREC, CB, WANLI with dataset gold labels; SemIf authored and perturbation fixtures; TypeSafe example set with "reference answers written by strong LLMs" scored as agreement with the most likely reference (App. D). JevBench-Open label provenance is not described in the paper. Training target: dataset labels, human annotator vote distributions and LLM teacher soft labels.

## n, sampling and intervals

OpenDecisions n = 2,352. Intervals are value +/- 1.96 SE, SE combining a paired bootstrap over question groups (1,000 resamples) and training-seed variation (Sec. 3 Scoring). Trained rows are mean of three seeds. Gains over Jev: trained 31B +4.3 +/- 2.5; over Eikos-27B +1.3 +/- 2.0; over deck31b +3.1 +/- 1.9 (Sec. 5.2). Held-out decider margin over Jev 2.2 +/- 0.7 (trained 31B), 1.6 +/- 0.7 (trained 27B) (Sec. 5.3). On 231 items one system's Capability has bootstrap SD of about 3 points (Sec. 5.3). Table 3 rows for Capability have no per-cell intervals.

## Test-set exposure

OpenDecisions is new (2026) and the authors check for overlap: 43 samples removed for overlap with training data and the public JevBench questions (Sec. 3); no exact matches among 2,389 draw questions (App. C.1); paraphrase and pretraining overlap not ruled out. Held-out sets: 13-word n-gram check finds no overlap for six sets and 71 of 7,800 decider items sharing template phrases (App. D). Jev "is best on SemIf's authored set (97.2), which is public and may have been used in its training" (Sec. 5.3). Knowledge-heavy MC benchmarks include seen tasks with unseen items for BoolQ, ARC, MMLU, WinoGrande (App. D). Spearman 0.90 with the JevBench leaderboard across 14 public systems (Sec. 3 Validity).

## Cost and latency

Training Gemma 4 31B takes 78 minutes on four H200 GPUs (about five GPU-hours); Qwen3.6-27B 64 minutes, Gemma 4 12B 40 minutes, Qwen3.5-4B 23 minutes (Sec. 4 Training). A run processes about 76,000 questions, 18% of the pool. No inference latency or cost per decision is reported for any model. The number-readout alternative of Li & Wagle needs several forward passes while the letter readout needs one (Sec. 2).

## Calibration

Capability includes a calibration score. Temperature scaling fitted per question type by NLL on 3,884 held-out questions of the training distribution; temperatures restricted to at least 1 (Sec. 4 Calibration). Gemma 4 31B zero-shot raw Capability 72.9 rises to 79.6 with temperatures 6.0 (choice) and 7.2 (yes/no) (Sec. 5.1, Table 18). Mean ECE over the six hard-label held-out sets: trained 31B 0.047 versus Jev 0.066 (Table 4). On knowledge MC, ECE 0.111 to 0.051 after training for 31B; Jev .032 (Table 15, Sec. 5.3). ECE bins: 15 on raw probabilities (Table 15 caption); equal-width versus equal-mass not stated. Training lowers Calibration for the 27B, 12B and 4B models (Sec. 5.2). Readout discards little mass: 99.99% on valid letters for Gemma 4 31B, over 99.4% on average (Sec. 5.1).

## Cascade or escalation

None.

## Option-name, cardinality, language, robustness

OpenDecisions includes option-order, perturbation, negation, fairness-pair and 23-language families (Table 1); per-family results in App. C (not extracted). Order-invariant encoding tested on Qwen3.5-4B gives no clear benefit; variants score 0.6 to 2.4 points below the letter format (Sec. 5.4, App. F). Supports up to 16 options.

## Code and data availability

Models, serving code (github.com/j-geuter/jeff-serve) and OpenDecisions (huggingface.co/datasets/jgeuter/OpenDecisions) released; links found in the HTML source. Hugging Face collection jgeuter/jeff-10.

## Internal inconsistencies noted

The text of Sec. 5.3 says the leaderboard result is on JevBench v1.7 (Jev 77.1), while Table 14 labels the revision v1.6.7 with Jeff draw v1.6.2 and Jev draw v1.6.1 (Jev 77.1 in both). The abstract also says "JevBench v1.7". Row values follow the text and abstract; the discrepancy is noted in the ledger location field.

## Authors' stated limitations

OpenDecisions may not represent real-world applications; 78% English; many questions LLM-generated; Qwen3.6-27B contributes training supervision while related Qwen3.8-27B participates in evaluation labelling, which "may introduce bias"; at most 16 options (Sec. 6). The recipe was chosen on OpenDecisions (App. C.1).
