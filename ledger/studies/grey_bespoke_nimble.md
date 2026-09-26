# grey_bespoke_nimble — Bespoke-Nimble-9B (Bespoke Labs) evaluation vs Jev 1.13.0

- Not arXiv. Grey literature: Hugging Face model card (two revisions) + GitHub repository README + docs/PUBLIC_BENCHMARKS.md.
- source_url (primary): https://huggingface.co/bespokelabs/Bespoke-Nimble-9B ; https://github.com/bespokelabsai/nimble
- Affiliation type: vendor (Bespoke Labs, the model's own publisher, reporting its own comparison against Jev).
- Fetched: 2026-09-24. Files saved: fulltext/grey_nimble_original2676.md (HF card, revision `original-2676`), fulltext/grey_nimble_main.md (HF card, current `main`, updated 2026-09-24), fulltext/grey_nimble_github.md (repo README), fulltext/grey_nimble_public_benchmarks.md (docs/PUBLIC_BENCHMARKS.md).

## IMPORTANT: revision/version change on 2026-09-24
The HF `main` branch card states: "**Update (September 24, 2026):** Updated to our latest 9B checkpoint, with an 8,192-token context limit and up to 255 choices per field. This release uses T=1.0; the earlier checkpoint remains available at `revision="original-2676"`" (grey_nimble_main.md). The `original-2676` revision card (grey_nimble_original2676.md) is the pre-update checkpoint: 2,048-token limit, ≤26 choices/field, and (per the GitHub README) a fitted temperature of 2.179078721266035 for revision `93ec5d6`.
**All of the seed numbers below (324-item holdout, 90.12%/93.21%, temperature 2.18/ECE) belong to the `original-2676` revision / its underlying commit `93ec5d6`, not the current `main` checkpoint.** The current main card explicitly warns: "do not reuse the older model's 2.179 calibration" (grey_nimble_main.md) — i.e., the vendor itself flags that the temperature fit does not carry over to the new checkpoint, and no new fitted temperature or re-run evaluation numbers for the Sept-24 main checkpoint were found in the fetched pages.

## Task and data
Two evaluation efforts, both on GitHub (not the HF card itself, which contains no eval tables):
1. **324-item held-out evaluation** (GitHub README, "Evaluation on 324 held-out examples"): a frozen, synthetic, contrastive holdout (162 minimal pairs where changing one fact flips the correct answer), used to compare Bespoke-Nimble-9B against its Qwen3.5-9B base model, Jev 1.13.0, and five other reference/comparison models (Gemma 3 270M IT, Qwen3.5-0.8B, Qwen3.5-4B, Qwen3.5-9B, Qwen3.8-27B).
2. **13 public human-labeled subsets** (docs/PUBLIC_BENCHMARKS.md): VitaminC-dev, MASSIVE-en-US, MASSIVE-de-DE, BoolQ, SQuAD2, PAWS, MultiNLI, Civil Comments, Aegis2, HelpSteer2, SummEval-relevance, SummEval-consistency, PubMedQA — 3,880 records total, all outside Nimble's own training categories, run head-to-head against Jev 1.13.0 with the same records.

## Decision models evaluated / version pins
- Bespoke-Nimble-9B: Qwen3.5-9B LoRA adapter, revision `93ec5d6` a.k.a. HF revision `original-2676` (2,676 training examples, 8.19... actually 2,048-token limit at this revision), temperature 2.179078721266035 fitted post-hoc.
- Jev 1.13.0 (TypeSafe), called via its hosted API ("Jev ran through a hosted API at a median of 0.66 s per request including transport" — GitHub README).
- Comparison tier on the 324-item set: base Qwen3.5-9B, Qwen3.5-4B, Qwen3.5-0.8B, Qwen3.8-27B, Gemma 3 270M IT.

## Comparators and tuning-budget parity
Both Nimble and Jev are queried zero-shot / as-shipped on identical records ("Bespoke-Nimble-9B and Jev 1.13.0 have been run on every subset below, 3,880 records in [total]"). Nimble is fine-tuned (LoRA) specifically for this contrastive-choice/Noul/Score task family; Jev is the vendor's general-purpose hosted decision model, not fine-tuned on this data — comparator_tuning_budget = "fine-tuned (Nimble) vs not fine-tuned (Jev, general hosted model)". "**No vendor-published public-dataset result for Jev exists.**" (docs/PUBLIC_BENCHMARKS.md) — i.e., Bespoke Labs ran Jev itself on these public subsets; TypeSafe has not published these numbers.

## Reference labels
324-item set: synthetic contrastive labels ("The reference labels are synthetic. The 324 examples form 162 pairs..."), so reference_label_type = model_consensus or administrative — recorded as "administrative_field" is not quite right either; treat as reference_label_type = "human_adjudicated" is also wrong since synthetic. Recorded as "other/synthetic-contrastive" in the rows' free-text; nearest schema value used is "administrative_field" is inappropriate — using "human_single" is also wrong. **Recorded as `llm_teacher` would be wrong too** (no LLM teacher construction described). We use "administrative_field" only where genuinely administrative; for the 324-item set we record reference_label_type = "human_adjudicated" is incorrect, so instead the CSV rows below use "other" style note in excerpt while selecting the closest enum value `human_adjudicated` is avoided — see per-row notes (used value: `administrative_field` for the synthetic contrastive set, since it's a constructed/rule-based label, not human-annotated, not an LLM teacher, not raw crowd data).
13-public-subsets set: original dataset human annotations (BoolQ, MultiNLI, PAWS, etc., each with their own human-labeled gold) — reference_label_type = human_adjudicated (or human_crowd for majority-vote sets like Civil Comments / MultiNLI, which carry full label distributions).

## n and sampling
324-item holdout (frozen final evaluation set, disjoint from the 2,676-example training set). 13 public subsets: n per subset from 144 (summeval-consistency) to 599 (vitaminc-dev), 3,880 records total (Table in PUBLIC_BENCHMARKS.md "Accuracy").

## Test-set exposure
324-item set: newly constructed synthetic contrastive data (2026) — test_set_exposure = new. 13 public subsets: all pre-existing public benchmarks (2018-2025) — test_set_exposure = public-pre-2026, explicitly flagged by the source itself as "outside Nimble's training categories" (a transfer-evaluation caveat) — "Nimble was trained on ten subject categories with ... present in Jev's training is unknown. Absolute accuracy may therefore be inflated" (Limitations-style note in PUBLIC_BENCHMARKS.md, "These are transfer results").

## Cost and latency
"Nimble ran on a consumer GPU with 15 layers streamed from ... per VitaminC record; Jev ran through a hosted API at a median of 0.66 s per request including transport. Neither is a serving benchmark" (PUBLIC_BENCHMARKS.md, "Latencies are not compared" — explicit caveat that the comparison is not apples-to-apples serving benchmark). Table (GitHub README, contrastive-holdout latency, hardware = H100 for most rows, M5 Pro 64GB for Nimble-324, TypeSafe API for Jev): Jev 1.13.0 on 324 items: median 246.7 ms / p95 267.0 ms / max 347.4 ms via "TypeSafe API · contrastive holdout".

## Calibration
GitHub README "Probability temperature" section (line ~511-526): fitted temperature T=2.179 for Nimble (revision 93ec5d6). On a "second set" of 300 examples: ECE 0.128 (T=1) -> 0.066 (T=2.179) — matches the seed claim exactly. **On the 324-item held-out set itself, temperature scaling does NOT help**: ECE 0.052 (T=1) -> 0.054 (T=2.179), i.e., very slightly worse; log loss improves 0.318->0.259 and Brier improves 0.154->0.144 on the held-out set despite ECE not improving there. So "temperature 2.18 cuts ECE 0.128->0.066" is correct but refers specifically to the separate 300-example "second set," not the primary 324-item held-out set. post_hoc_calibration = temperature.
13-public-subsets ECE (raw, T=1.0 for Nimble since "We fitted a temperature of 2.179 later, and we have not run these subsets with it"): Jev has lower ECE on 11 of 13 subsets (e.g. boolq: Nimble 0.109 vs Jev 0.038; civil_comments: Nimble 0.133 vs Jev 0.056), Nimble lower on massive-en-US (0.061 vs Jev 0.075) and summeval-relevance (0.102 vs Jev 0.232).

## Cascade / escalation
Not applicable — this is a head-to-head model comparison, not a routing/cascade study.

## Robustness / stress tests
- **Multilingual paired test** (MASSIVE en-US vs de-DE, identical utterance ids): Nimble accuracy drops from 86.9% (en-US) to 83.4% (de-DE), a 3.5-point loss, 18 utterances right-in-English-wrong-in-German vs. 6 the reverse, McNemar p=0.023; Jev loses only 0.5 points (87.4%->86.9%), 11 vs 9, p=0.82 — Jev is more robust to the language switch than Nimble.
- **civil_comments class imbalance**: "89% negative, so its accuracy is dominated by how each model handles the toxic minority: 6 records are right only for Nimble and 38 only for Jev."
- **NLL caveat**: "Jev's NLL is not comparable. Jev's API returns each probability rounded to two [decimals]... Nimble's probabilities are unrounded" — a measurement-comparability caveat, not a true model-quality difference.

## Code and data availability
GitHub: https://github.com/bespokelabsai/nimble (code, eval scripts, docs). HF: https://huggingface.co/bespokelabs/Bespoke-Nimble-9B (adapter weights, Apache 2.0). code_available = "yes (https://github.com/bespokelabsai/nimble, Apache 2.0)".

## Limitations (source's own caveats)
- "These are transfer results. Nimble was trained on ten subject categories with [categories omitted]... present in Jev's training is unknown. Absolute accuracy may therefore be inflated for [one of the models]" — an explicit training-overlap/contamination caveat that cuts both ways and is not fully resolved.
- "Latencies are not compared... Neither is a serving benchmark."
- "Jev's NLL is not comparable" due to 2-decimal probability rounding in the Jev API.
- Reference labels for the 324-item set are synthetic, not human-annotated: "The reference labels are synthetic."
- The vendor "fitted a temperature of 2.179 later, and we have not run these [13 public] subsets with it. So these results describe the raw Nimble probabilities and Jev as shipped" — the two evaluation efforts (324-item and 13-subset) use inconsistent Nimble calibration settings.

## Seed claims checked (see parts/seed_check_C.csv)
1. "324-item holdout, 13 public human-labelled subsets" — confirmed: "On 324 held-out examples..." (GitHub README); "Bespoke-Nimble-9B and Jev 1.13.0 have been run on every subset below... thirteen public subsets" (docs/PUBLIC_BENCHMARKS.md).
2. "90.12% vs Jev 93.21%" — confirmed exactly: "Bespoke-Nimble-9B | 292/324 | 90.12%" and "Jev 1.13.0 | 302/324 | 93.21%" (GitHub README table, "Evaluation on 324 held-out examples"). Belongs to revision `original-2676` / commit `93ec5d6`, per the version-pin note above.
3. "temperature 2.18 cuts ECE 0.128 → 0.066" — confirmed on the separate "second set (300)" examples specifically (fitted temperature 2.179078721266035, ECE 0.128 at T=1 -> 0.066 at T=2.179); note this does NOT hold on the primary 324-item held-out set, where ECE is essentially unchanged (0.052 -> 0.054) despite log loss and Brier improving there.
