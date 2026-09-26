# grey_localllama_typed_decisions — LocalLLaMA/typed-decisions dataset card (Hugging Face)

- Not arXiv. Grey literature: Hugging Face dataset card / leaderboard.
- source_url: https://huggingface.co/datasets/LocalLLaMA/typed-decisions
- Affiliation type: independent (community-built benchmark; explicitly states "This benchmark is independent. It is not affiliated with TypeSafe and it does not reproduce their Jev model.").
- Fetched: 2026-09-24. File: fulltext/grey_localllama_typed_decisions.md.
- License: Apache 2.0. This is the same "typed-decisions" benchmark referenced by grey_laya (0.727 Jev accuracy / 0.735 teacher-ceiling appear identically there) and grey_kev's `evals/v7` framing shares the same noul/choice/score primitive vocabulary — this dataset card is very likely the primary source both of those vendor pages' Jev comparison numbers were pulled from.

## Task and data
Four synthetic decision workflows, each asking 5 typed questions (noul/choice/score) over one shared unstructured state: `agent_trace_observability` (assess an agent run, decide review need/urgency), `customer_service` (determine assistant response/action from thread + account state), `invoice_processing` (review a bill against order/delivery, decide pay/hold/reject), `security_incidents` (decide close/investigate/contain from alert + machine history). 300 train / 100 test cases per workflow (1,200 train / 400 test cases total; 2,000 test decisions at 5 questions/case).

## Decision models / version pins
- **TypeSafe Jev 1.13.0**: "a measurement, taken on 2026-09-18 through the TypeSafe API (`POST /v1/systemone`, `model: jev-latest`, which reported itself as `jev-1.13.0`)" — directly confirms the memory note that `jev-latest` resolves to jev-1.13.0, and gives an exact measurement date.
- **meraGPT Decider 1** (`sd-1`): meraGPT's proprietary System One model, current SOTA on this leaderboard as of 2026-09-22, scored zero-shot (never trained on these workflows/schemas).
- **ModernBERT-base (149M)** and **MiniLM-L6 (22M)**: specialist baselines, one Adaptive Classifier (v0.2.0) head per question, encoder frozen, fitted on the `train` split of these exact four workflows — explicitly NOT comparable to the zero-shot generalist rows (Jev, Decider 1).
- Reference rows: Uniform (reads nothing), Prior (per-question label-frequency baseline fit on `train`), Perfect scenario understanding (ceiling: a model fit to the latent generating factors, cross-validated), Teacher self-agreement (ceiling: a fresh teacher sample scored against gold built from other samples).

## Comparators and tuning-budget parity
Jev and Decider 1 are both scored zero-shot/generalist (no training on these workflows); ModernBERT/MiniLM are specialists fine-tuned on the `train` split of the exact same workflows being scored — the card explicitly warns "Specialist and generalist are not comparable" and "A specialist number sitting next to a generalist number, unlabelled, misleads the reader." comparator_tuning_budget = "zero-shot (Jev, Decider 1)" vs "fine-tuned/fitted per workflow (ModernBERT, MiniLM)".

## Reference labels — "soft-gold" construction (seed topic)
"Label it with a teacher endpoint, sampled 3 times per case at temperature 0.7. The gold is the mean of the sampled distributions. Averaging distributions instead of argmax labels is what leaves the gold soft where a decision is genuinely ambiguous." reference_label_type = **llm_teacher**. The teacher is described as "roughly 4B-class capability." Per-question label-agreement is also recorded as a `label_agreement` column showing "how much the teacher samples disagreed."

## n and sampling
Test split: 400 cases (100/workflow), 2,000 decisions (5 questions/case). Train split: 1,200 cases (300/workflow), from "a separate run at a different seed, with prefixed case ids"; packaging verifies no case id or state overlaps between splits.

## Test-set exposure
Synthetic, generated data (2026): "Sample a latent skeleton... States essentially never repeat" — test_set_exposure = new. Not derived from any pre-existing public corpus.

## Cost and latency
Jev: "p50 710ms per case, $0.016 total at the published $0.042/1M input rate" for all 400 cases/2,000 decisions, zero errors. meraGPT Decider 1: "about half a second at the median" (526 ms p50 end-to-end from a client, one request at a time, matching Jev's measurement protocol), "$0.03 per million input tokens against Jev's $0.042." hardware_or_provider = "TypeSafe hosted API (`POST /v1/systemone`) for Jev; meragpt.com hosted API (`POST /v1/systemone`-compatible) for Decider 1; local GPU/CPU for ModernBERT/MiniLM (22-349 ms/case, hardware not specified)."

## Calibration
Full table (Baseline results): Jev Brier 0.148, ECE 0.144, KL-from-gold 1.442, TV 0.251. "Jev is not badly calibrated in absolute terms (ECE 0.144, overconfidence +0.023); it is confident because it is usually correct. The KL gap is mostly that this gold is a three-sample teacher spread and Jev does not reproduce that spread" — i.e., Jev commits to a near-one-hot distribution (matching the archerhume_jev finding that 990/1,200 MMLU predictions fell in the 0.9-1.0 confidence bin), while the soft teacher-averaged gold retains genuine spread, inflating KL divergence even though argmax accuracy and scalar ECE both look reasonable. meraGPT Decider 1: Brier 0.052, ECE 0.180 (worse ECE than Jev despite much better Brier/KL — the card notes ECE can be a misleading single-number summary here: "Prior also has the best ECE on the table, at 0.088, while knowing nothing... That is the clearest argument for reading KL and Brier here instead of ECE"). calibration_quantity = "ECE / Brier / KL-from-gold / TV (binning method for ECE not specified)"; post_hoc_calibration = none for any listed model (all "as shipped").

## Cascade / escalation
Not applicable — a static leaderboard comparison, no routing/cascade design.

## Robustness / stress tests
- **Ceiling analysis**: "Jev scores 0.727 against a 0.735 [teacher self-agreement] ceiling, so it has effectively saturated this benchmark. It also clears the 0.704 factor ceiling, meaning it reads these scenarios better than a model that recovers the generating factors exactly" — i.e., Jev is essentially at the noise floor of the labeling process on this specific benchmark.
- **Per-primitive breakdown** (Jev vs. Decider 1): noul 0.775 (Jev) vs 0.840 (Decider 1); choice 0.720 vs 0.733; score 0.696 vs 0.739 — Decider 1 leads on every primitive type, with the largest gap on `noul`.
- **Per-question ceiling variation**: "Per-question ceilings vary a lot, from 0.560 on `agent_trace/urgency` to 0.937 on `customer_service/category`. Read every score against its own question, not against the mean."
- **"A better model can score worse here"**: explicit example given — "the teacher missed a duplicate invoice whose ID literally matched a prior one," so a model that correctly catches this duplicate is *penalized* for disagreeing with the flawed gold.
- **Encoder specialist tradeoff**: ModernBERT-base (149M) vs MiniLM-L6 (22M): 0.646 vs 0.587 accuracy (6-point gap) at 349ms vs 22ms per case (16x latency) — "the gap between the two encoders is the trade-off this benchmark exists to measure."
- **Soft-target training detail**: for the specialist baselines, "Adaptive Classifier trains on hard labels, so the gold distribution is normally thrown away at fit time. Each case is instead entered four times, apportioned across labels in proportion to its gold... That single change cut KL by a third and score MAE by 15%, while barely moving accuracy" — a reproducibility-relevant implementation detail.

## Code and data availability
Dataset and card on Hugging Face (Apache 2.0): https://huggingface.co/datasets/LocalLLaMA/typed-decisions; specialist-baseline code via Adaptive Classifier 0.2.0 (https://github.com/codelion/adaptive-classifier, external tool, not this repo's own code). code_available = "yes (dataset + card on HF, Apache 2.0; baseline reproduction uses external Adaptive Classifier library)".

## Limitations (card's own explicit caveats)
- "Gold is the mean of three samples from a teacher endpoint of roughly 4B-class capability. A score measures agreement with that teacher. It does not measure correctness."
- "A score much above 0.75 means a model has learned the teacher's quirks rather than the task" — an explicit overfitting-to-labeler-idiosyncrasy warning that bounds how the leaderboard should be read.
- "Specialist and generalist are not comparable" — repeated, explicit warning against naive cross-row comparison.
- "Which number matters depends on whether you consume the argmax or the distribution" — explicit statement that accuracy and KL/Brier can disagree on model ranking (Jev beats ModernBERT on accuracy by 8 points but loses to it 6x on KL).
- "Earlier revisions of this card carried an estimated range here instead; that estimate is gone" — the Jev row was previously an estimate and has since been replaced with a direct measurement (2026-09-18), a version-history transparency note relevant to how much to trust the current figures vs. any cached/older copies of this card.

## Seed claims checked (see parts/seed_check_C.csv)
1. "teacher self-agreement 0.735" — confirmed exactly: "Teacher self-agreement | ceiling | 0.735 | a fresh teacher sample scored against gold built from the others" (also restated in prose: "Jev scores 0.727 against a 0.735 ceiling").
2. "the soft-gold construction" — confirmed: "Label it with a teacher endpoint, sampled 3 times per case at temperature 0.7. The gold is the mean of the sampled distributions. Averaging distributions instead of argmax labels is what leaves the gold soft where a decision is genuinely ambiguous" ("How it was built," step 3).
