# Sun & Xu (2026) — "Type-Safe Is Not Error-Free: A Constrained Decision Head Follows the Option Name, Not the Rubric Bound to It"

## Identification

- arXiv id: 2609.26758v1, cs.AI. "arXiv:2609.26758v1 [cs.AI] 22 Sep 2026" (header, p.1 / line 61).
- License: CC BY 4.0 (page header).
- Authors: Yu Sun and Junhao Xu, marked equal contribution ("†thanks: Equal contribution", byline).
  - Yu Sun — affiliation "National University of Singapore", email sun.yu@u.nus.edu (byline, p.1).
  - Junhao Xu — affiliation "Fudan University", email junhaoxu23@m.fudan.edu.cn (byline, p.1).
  - **affiliation_type = academic** for both authors — both affiliations are universities (National University of Singapore, Fudan University) and both emails are university domains (u.nus.edu, m.fudan.edu.cn); no industry/vendor affiliation is stated anywhere in the paper.

## Task and data

- The object of study is a "typed decision model": "The interface takes a typed question, a state, and a declared set of options; the model returns a probability distribution whose support is exactly that set." (§1, p.1, line 73). This is what the paper calls a "workflow decision."
- Corpus: "1200 binary workflow decisions over 4 predicates (300 each), every item carrying the dataset's own task-specific rubric text, one item per record, gold-positive rate .5750." (§3 "Data", line 128).
- The 4 predicates (Appendix A, Table 8, line 317-323): invoice reconciliation ("The invoice reconciles with the purchase order and the recorded delivery."), agent-trace triage ("This trace requires human review."), security-alert classification ("This alert reflects genuinely malicious or unauthorised activity."), customer-service escalation ("This conversation requires a human agent rather than automated handling."). n=300 each.
- Task-specific rubrics: "The rubric is the text the task ships to define the predicate; the name is an identifier." (§3 "Rendering", line 116). Each option is rendered "no: <rubric>" / "yes: <rubric>", i.e. option-name plus its bound rubric text.
- A further 600 items use "a generic rubric wording whose own first word is the opposite-polarity label," where name and definition are confounded by construction; these are excluded from the main 1200-item numbers and reported separately as an upper bound in Appendix C (§3 "Data", line 128; Appendix C, line 334-336).
- A separate multi-way arm: "683 genuine multi-way questions" with k ∈ {3,4,5,6,16} (§4.5, Table 4, line 213-215).

## Decision models evaluated

The paper states in the abstract: "We study Jev and two Jev-like models with open weights" (Abstract, line 69). Three "read-out families" are defined in §2 "Three read-out families" (line 108-110):

1. **Marker read-out** (open weights) — "a ModernBERT-large encoder with a two-layer transformer head, where each option contributes a [MASK] marker token whose contextual embedding is scored, with a question-type embedding and a per-(type, k) temperature." (line 110).
2. **Span-mean read-out** (open weights) — "a DeBERTa-v3-large encoder in which an option's score is the mean over the tokens of its entire rendered span — name and rubric — with a single scalar temperature." (line 110).
3. **Hosted read-out** — "the vendor's own product, queried over HTTP, whose weights we cannot inspect... it is the artifact for which the 0% type-error rate is advertised." (line 110). This is **Jev**, the hosted commercial model (confirmed by the abstract's "We study Jev and two Jev-like models with open weights" — Jev = the hosted one; the two open-weight checkpoints are the "Jev-like" models, i.e. the marker and span-mean read-outs).

**Exact version strings are NOT given in the paper body.** Footnote 2 states explicitly: "The two checkpoints are open weights on the Hugging Face Hub; we give the exact repository names and revisions in the released harness rather than in this paragraph, and all evaluation code, per-item probabilities and raw hosted responses are released with the paper." (line 110, footnote 2). So `version_pin` for the two open models = **not reported** (in the paper text itself); for Jev, no model/API version string is given either — only "the vendor's own product, queried over HTTP" and a caveat in Limitations that "the model served under that name may change" (§7, line 291).

### Which model is "the constrained decision head"?

The phrase "constrained decision head" appears **only in the title**; it is not used again in the body as a name for one specific model. Read in context, it is generic framing for the class of typed/schema-constrained decision heads the paper studies (all three families satisfy Lemma 1's masked-renormalized-softmax guarantee, §2). However, **the paper's headline numbers — the ones quoted in the Abstract and driving §4.1–§4.5 (70.4 more answers per hundred, AUROC .9376→.2315, balanced accuracy .8719→.2839, Table 1, Table 2, Table 3, Table 4) — are all measured on the marker read-out**, i.e. **one of the two open-weight "Jev-like" models (the ModernBERT-large marker head), not on Jev itself.** This is confirmed by cross-referencing Table 5/Table 6, where the marker head's no/yes flip rate on the shared 1200-item stratum is 76.92% (matching Table 1) versus 80.50% on the pooled 1800-item corpus, while Jev (the "hosted" column) gets its own, separately reported and smaller effect in §4.6 (AUC .8146→.5806, 32.50% flip, discussed below). So: **the model that carries the paper's central "constrained decision head follows the option name" claim is the open-weight marker-head model, not the hosted Jev** — Jev is presented as a confirmatory "third family" replication with its own, smaller-magnitude numbers (§4.6, line 235-237: "The effect replicates on an independently built read-out... The magnitudes do not: the marker head flips 2.4× as often as the hosted model on no/yes").

## Comparators and prompting/tuning parity

- All three families are evaluated with the identical instrument (§3 "The instrument"): "Fix an item and a pair of option names (ℓ₀, ℓ₁). The aligned arm binds each name to its own rubric, as shipped. The swapped arm exchanges the two rubrics between the two names... Nothing else changes: identical question, identical state, identical rubric strings, identical option set, identical number of options." (line 120). This is a within-model design (each model compared to its own aligned-arm baseline and to a neutral-name control), not a cross-vendor comparator study — there is no external baseline system. Comparator_tuning_budget: not applicable / not reported — no fine-tuning or prompt tuning is performed on any model; both open checkpoints are used "as shipped," the hosted model is queried as-is via API.

## Reference labels

- Gold is "keyed to the rubric throughout" (§3 "The instrument", line 120) — i.e., gold labels come from the task-specific rubric definitions bound to each workflow-decision item, not from a separate annotation/crowd process. The paper does not describe a human-adjudication or crowd-labeling procedure for how the underlying gold labels for the 1200 workflow decisions were originally produced; it treats the dataset's rubric-based gold as given. Given the paper never describes an annotation pipeline, **reference_label_type is best coded `administrative_field`** (the rubric/task definition determines gold) or, if stricter, **`none` explicitly described** — the study note flags this as **not explicitly stated** how the 1200 decisions' gold labels were originally created (only that "Gold is keyed to the rubric").
- n = 1200 for the main binary arm (300 per predicate ×4); n = 600 for the confounded stratum (Appendix C); n = 683 for the multi-way arm (§4.5); n = 1668 for the no-rubric span-mean arm (Appendix D, Table 9); n = 1800 for the pooled marker/span-mean geometry comparison (Table 5/6) = 1200 + 600.

## Sampling design / test-set exposure

- Not explicitly discussed. The paper does not state whether the 1200 workflow decisions (or their rubrics) could appear in any model's training data. There is no train/test contamination analysis. **test_set_exposure = unclear** (not addressed in the paper).

## Cost / latency / hardware

- Not reported. This is a robustness study, not a cost/latency study; no cost, latency, or hardware/provider information is given for any of the three model families beyond "queried over HTTP" for Jev.

## Calibration analysis

- **None.** No ECE, no reliability diagram, no post-hoc recalibration (temperature scaling beyond the models' own trained/learned τ) is reported. The paper explicitly argues recalibration would not help: "A model that had become uncertain would lose ranking information, and AUROC would fall toward .5; recalibration or a new threshold could recover part of the decision. Instead AUROC falls from .9376 to .2315... far below chance." (§4.2, line 170) — i.e. it discusses calibration only conceptually, to argue the failure is inversion rather than something recalibration could fix, but performs no calibration analysis itself.

## Cascade / escalation result

- **None reported.** No escalation, routing, or cascade-to-human-review experiment is described anywhere in the paper.

## The option-name / robustness stress test (full detail)

### Core instrument (§3)
Fix an item and name pair (ℓ0, ℓ1). **Aligned arm**: each name bound to its shipped rubric. **Swapped arm**: the two rubrics are exchanged between the two names, with question/state/rubric text/option set held byte-identical. **Control arm**: identical operation performed with polarity-free names, 0/1 and A/B, "to isolate the word from the channel." Metrics: balanced accuracy at p≥.5; AUROC (threshold-free); flip rate (fraction of items whose returned option changes, label-free); difference-in-differences (DiD) vs. neutral control, 95% CI from bootstrap of 2000 resamples clustered on records; for the hosted model only, a test-retest floor (aligned arm asked twice, byte-identically). Type-error rate reported throughout, always 0% (Lemma 1: masked-softmax output support guarantee).

### Table 1 — main result, marker head, n=1200 (§4.1, location: Table 1 / §4.1)
| option names | in voc. | bal.acc aligned→swapped | AUROC aligned→swapped | flip | DiD vs 0/1 (pts, 95% CI) |
|---|---|---|---|---|---|
| no/yes | ✓ | .8719→.2839 | .9376→.2315 | 76.92% | +70.42 [+67.58, +73.08] |
| false/true | ✓ | .9012→.4861 | .9623→.5773 | 49.67% | +43.17 [+40.25, +46.08] |
| absent/present | | .8593→.5350 | .9447→.5432 | 47.75% | +41.25 [+38.17, +44.17] |
| negative/positive | | .7531→.6728 | .8258→.7579 | 48.25% | +41.75 [+38.75, +44.83] |
| rejected/accepted | | .7914→.6619 | .9083→.6355 | 45.75% | +39.25 [+36.33, +42.25] |
| 0/1 | | .8368→.8322 | .9420→.9243 | 6.50% | — |
| A/B | | .8417→.8220 | .9422→.9405 | 6.00% | — |

Abstract summary: "renaming the two options from 0/1 to no/yes changes 70.4 more answers per hundred (95% CI: [67.6, 73.1]) and shifts AUC from .94 to .23" (Abstract, line 69).

### Inversion, not confusion (§4.2)
"AUROC falls from .9376 to .2315 (Figure 1a) — far below chance. The ranking is intact and pointed the wrong way: inverting the swapped scores recovers AUROC .77." (line 170). negative/positive: "flips 48.25% of answers yet keeps AUROC at .7579 (from .8258)" — flip rate overstates damage there since ranking survives; only pairs whose AUROC crosses .5 have "lost the decision itself."

### Per-predicate effects (§4.3, Table 2)
"no/yes never falls below 56.7%, and the neutral control never exceeds 11.3%... predicate by predicate it flips at least 7.4× as often as that control." Per-predicate % answers changed (invoice/agent/security/customer/min): no/yes 92.7/83.3/75.0/56.7 → min 56.7; false/true 63.0/39.3/29.0/67.3 → min 29.0; absent/present 56.0/76.7/39.7/18.7 → min 18.7; negative/positive 90.3/31.7/13.0/58.0 → min 13.0; rejected/accepted 92.0/37.0/12.3/41.7 → min 12.3; 0/1 (control) 2.7/11.3/6.3/5.7 → min 2.7 (i.e., max 11.3%). Per-predicate effect-size range across the 5 polar pairs: 12.3% to 92.7% (min flip across pairs/predicates 12.3%, max 92.7%).

### Polarity vs. familiarity (§4.4, Table 3)
"Moving from neutral names to unfamiliar polar names costs 41.00 pts; moving from unfamiliar polar names to the two familiar ones costs a further 16.04 pts." Flip means: neutral 6.25% (range 2.7–11.3%); polar unseen-in-vocab (3 pairs) 47.25% (range 12.3–92.0%); polar in-vocab (2 pairs) 63.29% (range 29.0–92.7%).

### Above binary / multi-way (§4.5, Table 4, n=683, k∈{3,4,5,6,16})
"renaming the members to neutral letters — without touching a single description — changes 52.42% of answers and drops accuracy from .5637 to .2782." Rotated names (advertising the wrong neighbour's content): 79.65% changed, accuracy .1552. Numbered ("option 1"): 55.78% changed, accuracy .2592. At k=16, neutral renaming lands at accuracy .141, "exactly the share of those items whose gold member happens to sit first (.1406)" — i.e. positional, not semantic.

### Read-out geometry / mean-pooling family flip-reduction (§4.6, Table 5, n=1800 pooled corpus)
"Running the identical swap on the same 1800 items through the span-mean head changes 19.50% of answers for no/yes, against 80.50% for the marker head — 4.1× smaller." Mechanistic account: "when an option's score is the mean over its entire rendered span, a one-token name is averaged against a rubric an order of magnitude longer, and its influence is diluted." Note the marker column here (80.50%) is on the pooled 1800-item corpus and differs from Table 1's 76.92% (1200-item stratum) — both are valid, scored on different item pools, explicitly flagged in the paper (line 233).

### Hosted Jev-specific numbers (§4.6)
"Exchanging the rubrics behind no and yes changes 32.50% of its answers against 2.08% and 1.67% for the two neutral controls, a contrast of 30.42 pts (95% CI [27.58, 33.33]), and balanced accuracy moves .7127 → .5163." Test-retest floor: "the aligned arm asked twice... the answer changes at most 1.33% of the time when nothing changes. The swap is 24× that floor, and the two neutral controls sit on it." AUROC: "its AUROC falling from .8146 to .5806, toward chance rather than past it" (line 237) — this is the paper's own precision for the abstract's rounded ".81 to .58." Also: "the marker head flips 2.4× as often as the hosted model on no/yes" (line 237).

### Random-string / opaque-name control (§4.7, Table 7)
15 random 5-character opaque name pairs (letters+digits, no ordinal/prefix relation; e.g. "xg6a6/e97ce"), run through both local read-outs (15 draws) and the first 5 through the hosted model. Result: "Opaque names land on the neutral class in all three families. They change 6.86%, 11.67% and 2.02% of answers against 7.94%, 14.83% and 1.88% for 0/1 and A/B: at most 3.16 pts apart in any family... indistinguishable from them on the hosted model (0.14 pts, [-0.38, 0.67])." Aligned balanced accuracy retained ("differs from the neutral class by at most .03"), so "the low flip rate is a decision still being made, not a channel switched off." Polar names on the same items: 32.21% to 70.72% changed. Conclusion: "with polarity absent, the name's semantic content is worth at most 3.16 pts" — i.e., **random-character-string names return the effect to the neutral-control regime without reducing accuracy**, confirming the seed claim. Spread across the 15 draws: marker head 3.22–13.28% (s.d. 2.46); hosted 1.67–2.42% (s.d. 0.34); span-mean 2.00–31.61% (s.d. 8.66) — on span-mean, "the widest opaque draw moves more answers than no/yes itself does on that read-out (19.50%)."

### Type-error rate
"Across all conditions, the type-error rate remains 0substantially [0% — abstract typo/OCR artifact, clearly '0%']." (Abstract, line 69). Also: "the type-error rate is 0% in every one of them" (§4 preamble, line 160), and for the hosted model specifically: "its type-error rate is 0% as well, by Lemma 1" (§4.6, line 237). This is a structural/analytic guarantee (masked-softmax normalization), not a measured reliability property (§2, Lemma 1).

## Code / data availability

Footnote 2 (§2, line 110): "all evaluation code, per-item probabilities and raw hosted responses are released with the paper." No explicit repository URL appears in the paper text or in the extracted HTML (checked for github.com / huggingface.co / zenodo / osf.io links — none found besides arXiv's own feedback-tool links). Exact Hugging Face repository names/revisions for the two open checkpoints are stated to be given "in the released harness," not in the paper body itself.

## Stated limitations (§7, verbatim-paraphrased with quotes)

"We audit two encoder checkpoints, one per read-out geometry, in English; whether the dilution account transfers quantitatively to other architectures is untested." "The third family is a black box we reached over a network at one point in time: we observe only its returned distribution, it is not deterministic — hence the measured floor of §4.6 — and the model served under that name may change." "Relabelings differ in how far they preserve meaning, which is why §4.3 reports the per-predicate minimum rather than the mean; a human annotation of meaning preservation across relabelings would sharpen the middle rows of Table 3 and is the natural next step." "Polarity and training-vocabulary familiarity are not separated by our arms." "The multi-way arm rests on a pool whose shipped accuracy is .5637, so we treat it as directional." "We report the vulnerability and two mitigations but evaluate neither." (§7 Limitations, line 291)
