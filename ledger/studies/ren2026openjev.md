# ren2026openjev — Open-Jev Judgments on CallScreenBench: Calibrated One-Pass Scam Screening with a Small Language Model

arXiv:2609.23959v1 [cs.CL], submitted 21 Sep 2026, CC BY-NC-SA 4.0. HTML retrieved from https://arxiv.org/html/2609.23959v1.

## Authors and affiliation

Simiao Ren (corresponding, benren@scam.ai), Kidus Zewde, Xingyu Shen, Yuchen Zhou, Dennis Ng, Ankit Raj, Tommy Duong, Yuxin Zhang, Neo Tiangratanakul (all but Ren marked equal contribution). Affiliation: Scam.ai (Reality Inc.). Affiliation type: **industry**.

## Task and data

Per-turn scam-call screening: after every caller turn in a phone conversation, a model must return a calibrated P(scam). **JevLite** is the paper's open implementation of the Jev-style typed-decision readout: Qwen3-4B + LoRA, trained so the temperature-scaled softmax over exactly the two allowed-label logits (yes/no) is read in one forward pass with no generated text (Eq. 1; Table 1 contrasts this against "parsed label" and "label-token readout" alternatives on the *same* fine-tuned weights). Data: **CallScreenBench** [Gan et al. 2026, arXiv:2608.01033] — 48 core scenarios (24 scam, 15 legitimate, 9 gray with a designated ground-truth side), LLM-caller (MiniMax-Text-01) transcripts against 16 secretary agents. Split by scenario: 40 training (3,187 turn-prefix decisions), 8 validation (650). Test: 41 evaluation-only scenarios never in training/validation, with new calls generated using the benchmark's own caller plus two scripted secretaries — 82 calls, 577 turn-end decisions (§4 "Data"; Appendix B).

## Decision models / systems evaluated

- **JevLite (3-seed ensemble)** — the paper's headline model: Qwen3-4B, LoRA rank 16/α 32/dropout .05 on all attention+MLP projections, one epoch at lr 5e-5, CE+Brier loss on the label logits only, temperature fitted per-model on validation, three training seeds averaged (`version_pin`: no upstream TypeSafe Jev version — this is an independent open reimplementation of the *interface*, not a fine-tune of or wrapper around the commercial Jev model). Single-seed AUROCs span .969–.977 (logit correlation ≥.987 across seeds); "a deployed screener would use a single model, and all latencies refer to one model" (§3 "Calibration and aggregation").
- **LLM judge** — MiniMax-M3, prompted via "TypeSafe's official LLM adapter" to return a JSON probability; prompt not tuned (§4 "Baselines").
- **ModernBERT-large** (fine-tuned binary classifier) and **ModernBERT-large + auxiliary heads** (matched teacher-labeled intent questions) — comparator encoders.
- **Qwen3 fine-tune of the same backbone** — same weights as JevLite's base recipe, but trained with ordinary next-token loss to generate `{"scam":"yes"}`; read three ways in the ablation (parsed label / verbalized confidence / label-token probability "the Jev way") — Table 1, Table 4 (Appendix D).
- **Zero-shot Qwen3-4B** — untuned backbone, read out exactly as JevLite.
- **Linear classification head** (arm C, Appendix D ablation) on the same frozen backbone.

Comparator tuning-budget parity: the judge's prompt "was not tuned" (same prompt, zero-shot); ModernBERT and its aux-head variant are trained on the *same* training prefixes as JevLite, the aux-head variant additionally matched on the same teacher-labeled auxiliary questions ("the fair comparison," §5) — coded `comparator_tuning_budget = matched` in spirit though the schema's closest literal value used is "same training prefixes...matched" text in the ledger's cost_or_latency/excerpt fields.

## Reference labels

CallScreenBench scenarios carry an author-designed ground truth (scam/legit/gray-with-designated-side) rather than a human-adjudicated or LLM-teacher label per item — coded `administrative_field`. Two auxiliary intent questions used only during training are labeled by MiniMax-M3 as a teacher (`llm_teacher` for that specific sub-supervision, not the headline scam/legit label).

## n, sampling design

577 turn-end decisions from 41 held-out test scenarios (82 calls); 2,000-bootstrap-resample 95% percentile intervals over test *scenarios* (not decisions, since decisions within a scenario are correlated), with paired differences resampled jointly (§4 "Metrics"; Appendix C). Streaming/mid-utterance analysis scored only for seed 0 of the headline recipe (the 3-seed ensemble was not scored this way).

## Test-set exposure

Self-admitted and central to the paper's own honesty framing: "the recipe was selected with test-set exposure" (Abstract) — about ten recipes were scored on the test set before the model-selection rule was written, and the eligible recipes' statistic (mean single-seed test AUROC .972 vs .930) is explicitly flagged as subject to "winner's-curse inflation" (§4 "Model selection"). Coded `test_set_exposure = unclear` for all JevLite/ablation rows in the ledger, per the paper's own caveat. CallScreenBench itself: all callers are synthetic (LLM-generated), so this is not a public-pre-2026 corpus in the usual sense.

## Cost and latency

Hardware: one RTX 3090, batch size 1, no other job running, for JevLite/encoder/Qwen3-FT measurements; judge latency is "remote API wall time under 8 concurrent requests, including about 108 reasoning tokens per decision" (§4 "Metrics", Table 2 footnote). Headline: JevLite 64.5 ms median (p95 110.5 ms) — ~30× faster than the judge at median, 52× at p95; 4.9× faster than the same backbone fine-tuned to generate its JSON answer (317 ms). Each additional question on the same call adds 21.8 ms on the shared prefix (5 questions: 168.7 ms vs 321.6 ms if each were encoded afresh, argmax changing in 6/1500 decisions) (§5 "Latency").

## Calibration analysis

Expected calibration error, ten equal-width bins (§4 "Metrics"). All trained systems (JevLite, encoders, Qwen3 FT variants, but not the untuned zero-shot backbone) are temperature-scaled with T fitted on validation-set NLL (`post_hoc_calibration = temperature` for JevLite and comparators). Untuned zero-shot backbone: ECE .170 ("badly over-confident," §5 "Ranking and calibration"). JevLite ECE .052 vs judge .054 (difference −.002 [−.048, .036]); after also temperature-scaling the judge on validation (T=1.49), judge ECE .049 (paired difference +.003 [−.056, .030]) — i.e., calibration parity survives giving the judge the same post-hoc treatment. Bins merged when equal-width bins would leave points within 5 points of each other (Fig. 3 caption note); a separate figure shows all trained systems concentrate predictions above 90% confidence, "which is why bin choice matters."

## Cascade / escalation results

Not a model-routing cascade, but an "owner-facing" hang-up-rule replay is functionally analogous: hang up once two consecutive caller turns reach P(scam) ≥ τ (τ fitted per-system on validation: 0.92 for JevLite, 0.97 for the judge). Both hang up on a similar share of scam-side calls (40/52 vs 41/52) and on no legitimate call; JevLite decides 1.14 turns earlier on average [0.55, 1.67] on the 36 calls where both hang up, "at the cost of one fewer detection" (§5 "Owner-facing decisions").

## Option-name / robustness stress tests

Two explicit stress tests (§5 "Recipe and robustness"): (1) swapping the order of the two answer options flips 2.6% of decisions [0.2, 5.8]%, "in line with known option-order sensitivity"; (2) a held-out paraphrase of the scam question flips 5.2% [2.0, 9.4]% of decisions, 28 of 30 toward "legitimate" — flagged in the Ethics Statement as the exploitable direction for an attacker probing the screener. Unseen-question generalization probes (five questions never trained on) show gains on extraction-like questions (a stated amount, a callback number) but not on judgment-like ones (urgency, sympathy) — Appendix D.

## Code and data availability

"The code, LoRA adapters, per-decision predictions and the 82 generated test calls will be released" (Conclusion; Ethics Statement) — future tense, **no repository URL, commit hash, or Hugging Face model id is given anywhere in the paper text** (checked by full-text search; confirmed via `parts/seed_check_B.csv`). `code_available = partial` in the ledger.

## Paper's own stated limitations

Explicit in the Abstract and reinforced in §6/§7: "the recipe was selected with test-set exposure," "a fine-tuned ModernBERT encoder is not significantly worse," "all callers are synthetic." Non-inferiority is established against only one judge (MiniMax-M3), which is also the model family that wrote the calls and supplied the auxiliary training labels — a potential same-family advantage the authors flag directly (§5 "Ranking and calibration"). Single-seed models clear the pre-registered −.02 non-inferiority margin "only narrowly" (two of three by "a few thousandths"). Gray-family accuracies rest on only 5 (gray/scam) and 3 (gray/legit) test scenarios and vary by up to ~30 points across seeds — "within seed noise" (Table 3 note). Mid-utterance accuracy drops 3.8 points vs turn-end, concentrated on the first turn. Ethics Statement: the method is dual-use (a fast oracle a scammer could probe/tune against), and release "lowers an attacker's cost of probing the screener." Future work: real callers with independent labels, holding out entire scam archetypes, testing whether calibration on complete calls transfers to partial ones.

## Notes on seed claims (see also parts/seed_check_B.csv)

- Backbone Qwen3-4B + LoRA: **confirmed** (§3 "Training"; Appendix A).
- 577 decisions: **confirmed** (Table 2 caption, Abstract).
- AUROC 0.974: **confirmed**, but this is the three-seed ensemble's figure, not a single deployed model's (single-seed mean is 97.2%) — noted, not a contradiction, since the abstract itself states "a three-seed ensemble reaches AUROC .974."
- Calibration error 0.052: **confirmed** (ECE, ten equal-width bins, three-seed ensemble; Table 2).
- "The gain is in the readout and calibration, not accuracy": **confirmed** as a verbatim quote from the Abstract, and substantiated by the interface-vs-fine-tuning ablation (§5 "Interface versus fine-tuning": the parsed label is about as accurate as the readout, .892 vs .894; a linear classification head on the same backbone is at least as accurate, .927).
- Exact HF id of the released model: **not_found**. No Hugging Face repository, GitHub URL, or model id string appears anywhere in the paper's main text, references, or ethics statement — only a promise that code/adapters "will be released."
