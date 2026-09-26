# grey_laya — Laya / Laya Multilingual / laya-typed-decisions (ConvAI Innovations) model cards

- Not arXiv. Grey literature: three Hugging Face model cards (one family, three checkpoints).
- source_url: https://huggingface.co/convaiinnovations/laya ; https://huggingface.co/convaiinnovations/laya-multilingual ; https://huggingface.co/convaiinnovations/laya-typed-decisions (root/English card also documents the typed-decisions checkpoint's headline numbers)
- Affiliation type: vendor (ConvAI Innovations / Nandakishor Mukkunnoth, the model's own publisher; see also the priority-claim narrative captured separately in references/web/mukkunnoth_laya_priority.md).
- Fetched: 2026-09-24. Files: fulltext/grey_laya_card.md (English root card, holds cross-checkpoint comparison tables incl. vs. Jev), fulltext/grey_laya_multilingual_card.md (multilingual card).
- License: Apache 2.0 (all three checkpoints).

## Task and data
Typed-decision benchmarking across several tasks: (1) an internal "typed-decisions" benchmark (400 cases, 2,000 decisions, four workflows: invoice processing, security incidents, customer service, agent-trace observability); (2) MASSIVE intent classification (English and 13-51 other languages depending on table); (3) XNLI (English + 14 other languages); (4) AG News (4 labels); (5) DAIR Emotion (6 labels); (6) Banking77 (72-77 labels, a high-cardinality stress test); (7) SST-5 (ordinal score, 5 levels).

## Decision models / version pins
- `convaiinnovations/laya` (English): ModernBERT-large backbone, 421M params, 512-token context (`head_max_len=192`), Apache 2.0.
- `convaiinnovations/laya-multilingual`: mmBERT-base backbone, 322M params, 1024-token context (up to 8,192 with `max_len=8192`), covers 100+ languages, ~2.2x faster than English checkpoint.
- `convaiinnovations/laya-typed-decisions`: ModernBERT-large, 421M, 1024-token context, fine-tuned specifically on the typed-decisions benchmark's own training split.
- Comparator: **Jev 1.13.0**, described in this source as "third-party published, never measured here (no TypeSafe API access); sample sizes and prompts differ" — i.e., the Jev numbers in the comparison table are NOT independently re-run by ConvAI on the same harness; they are pulled from elsewhere (most likely from the typed-decisions benchmark's own published numbers, given the matching 0.727 accuracy / 0.735 teacher-ceiling figures that also appear in the LocalLLaMA typed-decisions dataset card).

## Comparators and tuning-budget parity
Laya checkpoints run zero-shot except `laya-typed-decisions`, which is explicitly fine-tuned on that benchmark's training split ("The 0.766 belongs to the checkpoint fine-tuned on that benchmark's own training split... The base checkpoints sit below the majority-class baseline here"). Jev's comparison numbers are described as third-party/published rather than run by this source, so comparator_tuning_budget for the Jev rows = "not reported (third-party published figures, not independently re-measured, sample sizes and prompts differ)". This is an important source-acknowledged apples-to-oranges caveat that should temper any head-to-head reading of the Laya-vs-Jev table.

## Reference labels
Public benchmark gold labels (MASSIVE, XNLI, AG News, DAIR Emotion, Banking77, SST-5) — reference_label_type = human_adjudicated. For the typed-decisions benchmark specifically, the reference is a "teacher self-agreement ceiling" of 0.735 — i.e., an LLM-teacher-constructed soft-gold reference (reference_label_type = llm_teacher for typed-decisions rows specifically; this matches the LocalLLaMA/typed-decisions dataset card's own description of "soft-gold construction" and teacher self-agreement 0.735, suggesting the same underlying benchmark/dataset is being reused across these grey-literature sources).

## n and sampling
Speed/comparison benchmarks: "17,416 questions, one T4 GPU, identical questions per model" (MASSIVE+XNLI routing-evidence table). MASSIVE-51-language table: "all 51 MASSIVE languages... both checkpoints answering byte-identical questions" (multilingual card). typed-decisions: 400 cases / 2,000 decisions, four workflows, "measured here" (i.e., directly run by the source on all three Laya checkpoints; Jev row marked *published*, not measured here). act_probability AUROC check: 396 labelled decisions. Long-document accuracy check: 20 requests per document-length bucket.

## Test-set exposure
All public pre-2026 benchmarks (MASSIVE, XNLI, AG News, DAIR Emotion, Banking77, SST-5) — test_set_exposure = public-pre-2026. The typed-decisions benchmark is presumably the same one referenced by the LocalLLaMA dataset card and by other Jev papers in this ledger; not clearly dated in this source, recorded as "unclear."

## Cost and latency
Hardware: "Measured on a Tesla T4; every checkpoint answered byte-identical questions in the same run" (Benchmarks section). Per-question latency (T4, 1 question): laya (English) 39.5 ms, laya-multilingual 32.8 ms; batched (10 questions): 158.6 ms (15.9 ms/q) vs 72.3 ms (7.2 ms/q); 103-332 questions/sec batched on one T4. Jev comparator latency: "236-276 ms p50" cited from two independent third-party GitHub benchmark repos (AbdelStark/jev-benchmarks, nibzard/decision-model-benchmark), not measured by ConvAI itself — "so Laya answers a single question roughly 6-8x faster." Cost comparison (vendor's own table): Jev "$0.042 / 1M tokens" vs Laya "$0 self-hosted."

## Calibration (central topic of this source)
- **Laya English**: "Ships over-confident: Refitting one temperature per (question type, option count) moves mean ECE 0.466 -> 0.081 (`laya`)" (Honest Limits section) — matches the seed claim exactly.
- **Laya multilingual**: "Ships uncalibrated... systematically over-confident (mean confidence 0.75-0.83 against much lower accuracy). Refitting one temperature per (question type, option count) on held-out data moves mean ECE 0.314 -> 0.106."
- Comparison table (vs. Jev): "ECE (lower better) | 0.246 (Jev) | 0.081 (Laya, post-temperature) | 3x better (post-temperature)"; and separately "Out-of-the-box raw calibration: Before temperature scaling, the base checkpoint has higher raw ECE (0.213 vs 0.144 [Jev]). Laya achieves its 0.081 ECE after domain temperature fitting" — i.e., Jev's *raw* (as-shipped) ECE (0.144) is actually better than Laya's *raw* ECE (0.213); Laya only surpasses Jev's raw figure after its own post-hoc temperature fit. calibration_quantity = ECE (binning method not specified); post_hoc_calibration = temperature (per question-type/option-count bucket).
- **Non-Latin-script overconfidence**: Khmer 0.000 accuracy at 0.952 confidence (English checkpoint on non-Latin script); "Its mean confidence never drops below 0.885 at any accuracy level, so confidence gating cannot catch it" (multilingual card).

## Cascade / escalation
`Router` performs script/language-based routing between `laya` (English) and `laya-multilingual` checkpoints, decided from input script "before the forward pass," explicitly NOT confidence-gated ("the model's confidence gives no warning when a checkpoint cannot read its input"). This is a rule-based dispatch, not a confidence-threshold cascade in the REFLEX/KITE sense — recorded as such in cascade_result fields (routing evidence table, `Router` accuracy = max(English, Multilingual) per task by design).

## Robustness / stress tests
- **High-cardinality (Banking77, 72-77 labels)**: Jev 0.870 (72 labels) vs. Laya (routed) 0.425 (77 labels, default 256-token head budget) — "Jev leads on >20 options... 77 options receive only ~3 to 4 tokens per label, causing text to become indistinguishable." This is the one clear "Jev wins" result the vendor itself reports.
- **Multilingual collapse (English checkpoint on non-Latin scripts)**: Khmer 0.000, Hebrew 0.060, Armenian 0.050 (=random), Bengali 0.080 — all reported at 0.89-0.96 confidence.
- **Soft-distribution matching**: "On typed-decisions, while Laya achieves higher argmax accuracy (0.766 vs 0.727), Jev achieves higher soft accuracy (0.580 vs 0.471) against the teacher's full probability distributions" — a robustness-relevant nuance favoring Jev on distributional fidelity even where Laya wins on argmax.
- **Position bias (multilingual, ordinal score questions)**: "it rarely picks the first-listed level, in any language, including English (0 of 290 in one independent run)."
- **act_probability signal is broken**: "carries no usable signal yet... AUROC 0.30 on 396 labelled decisions. Gate on `confidence` instead, which reaches an AUROC of 0.77 on the same items."

## Source-internal inconsistency flagged during extraction
The English-root card's "Honest Limits" section states multilingual zero-shot typed-decisions accuracy as "0.352 for multilingual," but (a) the comparison table two sections earlier in the SAME card gives `laya-multilingual` = 0.342 accuracy on typed-decisions, and (b) the multilingual card's own "Limits" section states "Near chance on typed-decisions zero-shot -- 0.342." The two authoritative instances (table + the model's own card) agree on 0.342; "0.352" appears to be a typo in one prose sentence of the English root card. Recorded as 0.342 in the ledger, with this discrepancy noted.

## Code and data availability
GitHub: https://github.com/NandhaKishorM/laya (Apache 2.0); PyPI: laya; full benchmark data on the GitHub `research` branch; BENCHMARKS.md referenced but not separately fetched in this pass. code_available = "yes (https://github.com/NandhaKishorM/laya, Apache 2.0)".

## Limitations (source's own, "Honest Limits" / "Limits" sections)
- "Base checkpoints are near chance on typed-decisions zero-shot -- 0.362 here and 0.34-0.35 for multilingual, against a 0.318 random and 0.461 majority-class baseline. ... Laya is a fast base to specialise, not a zero-shot decision engine."
- High-cardinality choice questions need manual budget tuning (`head_max_len`) or hierarchical splitting to avoid the Banking77-style collapse.
- "Ordinal `score` questions are the weakest primitive" for both checkpoints (SST-5 0.372 English / 0.282 multilingual).
- `noul` (yes/no) primitive can anchor on its own option-label tokens rather than the state content; documented GitHub issue #156.
- "`action.act_probability` carries no usable signal yet" (GitHub issue #185).
- "Ships over-confident" / "Ships uncalibrated" for both checkpoints pre-temperature-fit; users are explicitly told to refit temperature on their own data before trusting probabilities.

## Seed claims checked (see parts/seed_check_C.csv)
1. "ships over-confident, ECE 0.466 before and 0.081 after temperature scaling" — confirmed exactly: "Refitting one temperature per (question type, option count) moves mean ECE 0.466 -> 0.081 (`laya`)."
2. "0.362 zero-shot on typed-decisions" — confirmed exactly: `laya` accuracy 0.362 on the 2,000-decision typed-decisions benchmark (comparison table; also restated in "Honest Limits": "0.362 here").
3. "0% accuracy on Khmer at 0.952 reported confidence" — confirmed exactly: "Khmer scores 0.000 accuracy at 0.952 confidence" (English checkpoint on non-Latin script, multilingual card and root card both state this).
4. "33-39 ms on a T4" — confirmed approximately: laya (English) 39.5 ms and laya-multilingual 32.8 ms per single question on a Tesla T4 (both fall within/near the claimed 33-39 ms range; multilingual's 32.8 ms rounds to ~33 ms).
