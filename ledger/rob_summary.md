# Risk of bias, summary notes (ledger v1.0, graded 2026-09-24)

These are working notes for survey section 7.2, not manuscript prose. The per-study ratings and reasons are in `rob.csv`, and the counts that become manuscript macros are in `rob_counts.json`. The same script generated both files, and `overall` was computed from the five ratings, not typed by hand.

## Distribution

- 25 studies were graded: 17 arXiv papers and 8 grey-literature sources.
- Overall: 0 low, 15 some concerns, 10 high.
- Per domain (high / unclear / low):
  - D1 reference labels: 3 / 15 / 7
  - D2 sampling and reporting: 4 / 14 / 7
  - D3 version pinning and run dates: 6 / 16 / 3
  - D4 tuning-budget parity: 8 / 7 / 10
  - D5 test-set exposure: 5 / 13 / 7
- The overall rule was applied mechanically:
  - low means all five domains are low, or exactly one is unclear and none is high.
  - high means D1 or D5 is high, or two or more domains are high.
  - Everything else is some concerns.
- No study reaches low. The closest is ibrahim2026evaluating, which is low on D1 to D4 and high only on D5.

## What drives the high ratings

- Of the 10 high studies, 4 are high on D5 alone: ibrahim2026evaluating, li2026jevasajudge, yu2026visual and zhang2026same. All four use public pre-2026 benchmarks with released answer keys and no contamination check. These are otherwise among the better-designed studies.
- 3 are high through D1:
  - jiang2026jevmem uses an LLM judge.
  - grey_localllama_typed_decisions uses an LLM teacher for its gold labels.
  - grey_typesafe_evals scores against a consensus of two frontier models.
  - jiang and typesafe_evals are also high on two or more other domains.
- 3 are high because two or more domains other than D1 and D5 are high:
  - cheng2026thisthatmodel (D3 and D4)
  - grey_kev (D3 and D4)
  - grey_vercel_p95 (D2 and D3)
- D4 has the most high ratings of any domain (8). On its own it gives only some concerns, as it does for ma2026jevstar, ren2026openjev, robitza2026jevqa, Nimble, Laya and Rev.
- Sensitivity check: suppose public pre-2026 benchmarks were graded unclear instead of high on D5. `survey/src/t_s3_rob.py` computes the result as macros rob.sensLow, rob.sensSome and rob.sensHigh.
  - The distribution becomes 1 low, 18 some concerns and 6 high.
  - Of the four D5-only studies, ibrahim2026evaluating moves to low, because its other four domains are all low. li-judge, yu and zhang move to some concerns.
  - jiang stays high through D1.
  - An earlier draft of these notes said 0 / 19 / 6. That was an arithmetic slip, corrected here from the script output.

## Pattern by evidence role

- **independent_evaluation (8): 5 some concerns, 3 high.** All 3 highs come from D5, public benchmarks: ibrahim, li-judge and zhang. This group has the best D1, D2 and D4 profiles. Its weak point is test-set exposure. The survey authors' own paper (rafe2026calibrated) is graded some concerns. It has four unclears (D1 to D4) and one low (D5). There are no highs, but it gets no domain-level credit that another study would not get.
- **method_paper_with_evaluation (9): 6 some concerns, 3 high.**
  - The 3 highs are cheng, jiang and yu.
  - This group holds 3 of the 8 D4 highs. cheng trains its model on the task family, ren tunes its recipe on the test items, and in ma the system comparison is confounded by concurrent interface changes.
- **vendor_evaluation (5): 3 some concerns, 2 high.** The four open-replica cards (Nimble, Kev, Laya, Rev) are all high on D4, because each compares a model tuned for the task against Jev used zero-shot, or against Jev figures quoted from another harness. The TypeSafe evals site is unclear on D4 but high on D1, D2 and D3.
- **dataset_card (1): high** on D1, because of the LLM-teacher soft gold.
- **practitioner_report (1): high.** grey_vercel_p95 reports no n, no version and no protocol.
- **reverse_engineering (1): some concerns.** grey_archerhume_jev is one of only three studies that are low on D3.

## The two most common threats

**Tuning-budget asymmetry (D4).** Eight studies are high on D4, more than on any other domain. The pattern takes three forms:
- An open or in-house model is trained or temperature-fitted on the task family being scored, while hosted Jev is queried zero-shot. This covers cheng, Nimble, Kev and Rev, and Laya adds Jev numbers copied from other samples and prompts.
- The decision system's configuration is chosen on the evaluation items themselves: ren's recipe and robitza's input state. wu2026reflex's threshold sweep on its test tasks is unclear, because the text does not say whether τ = 0.5 was fixed in advance.
- The compared systems differ in more than the component under test (ma).

Head-to-head claims of the form "X beats Jev" in this literature are therefore mostly specialist-against-generalist comparisons, not like-for-like ones. The studies that match budgets closely are yu2026visual (identical update budget across arms) and ibrahim2026evaluating, li2026jevasajudge and zhang2026same (the same prompts, with thresholds frozen on a selection set). They are the ones to lean on for parity-sensitive statements.

**Missing run dates and version pins (D3).** Only 3 of 25 studies are low on D3: ibrahim2026evaluating, li2026replacing and grey_archerhume_jev. 16 studies are unclear, for three reasons:
- Most name the exact jev-1.13.0 build but give no run or collection date. Documentation and price-page access dates are the usual substitute, and they do not count.
- Some give only a minor-version alias: deng, li2026fast, ma, robitza and Rev.
- LocalLLaMA dates its Jev run, but its second decision model has no build string. Six studies are high because they give no version for a decision model at all: cheng (Jev), jiang, sun, grey_kev (Jev), grey_typesafe_evals and grey_vercel_p95. Every study falls inside roughly a ten-day window after the 15 September release, so drift is not yet a large practical risk. The gap will matter once jev-latest resolves to a newer build.

D5 is the third threat and the most consequential one for overall grades. Five studies are high on D5, 13 are unclear and only 7 are low. The unclear group is mostly mixed-source headlines and access-controlled data.

## Grading rules applied uniformly (for the methods paragraph)

**Headline estimates.** These are the quantities that a study's abstract, lead table or seed claims report and that the ledger extracts as headline rows. D1, D2 and D5 are graded over all of a study's headline estimates:
- low if every headline estimate is low.
- high if every headline estimate is high.
- unclear if the ratings are mixed.

D5 covers only accuracy, agreement and calibration estimates. Cost and latency estimates are exempt, because training data cannot contaminate them. D3 and D4 are graded at study level. Where a mixed D1 hides a clear per-outcome answer, `notes` gives it (huang, li2026replacing, rafe).

**D1, reference labels.**
- low: expert or adjudicated labels; a crowd with an agreement check; published benchmark gold from human-annotated source datasets (Ziems, ContractNLI, RACE and similar); or an objectively scored outcome (game result, latency, simulator truth, exact answer key).
- unclear: a single annotator; an administrative field; author-authored canonical labels; programmatic or transferred gold (GQA from scene graphs, SNLI-VE); gold of undescribed provenance; a computed proxy metric (VMAF); or no information at all.
- high: an LLM judge or teacher, a model consensus, vendor labels, or synthetic labels.

**D2, sampling and reporting.**
- low: n is stated, the sample is the official split or a documented draw, and headline estimates carry intervals.
- high: n is missing, or every headline estimate rests on a small convenience set with no intervals.
- unclear: everything else. This includes missing intervals on a documented sample, a small head-to-head set alongside larger unintervalled sets (cheng, ma), and preregistered outcomes that go unreported.

**D3, version pinning and run dates.** This domain is graded on every decision model in the headline comparison. Comparators that are only named by alias are noted but do not change the rating.
- low: a patch-level or dated build string, or a SHA, plus an explicit run or collection date. Access dates for documentation and prices do not count.
- unclear: a minor-version alias only, or no run date, or a self-trained model whose weights and identifier are unreleased.
- high: no version at all for a decision model.

**D4, tuning-budget parity.** A configuration chosen on the evaluation items (a recipe, an input state or a threshold) is graded here, not in D5, because D5 asks whether test items could be in the training data.
- low: the same information and contract for every system, and no system-specific tuning. A study with no between-system comparison is also low.
- unclear: a prompt or schema developed on development data using the decision model's outputs and then given verbatim to the comparators (rafe, kite); substituted comparator backends (huang); a harness designed by the vendor (typesafe_evals); or a threshold sweep on the test items where the text does not say when the primary value was fixed (wu).
- high: the decision model or the authors' own model is trained on the task family, or its configuration is explicitly selected on the evaluation items, while the comparators are not; or comparator numbers come from another harness; or the compared systems are confounded.

Because of this placement, ren2026openjev's admitted test-set selection makes it high on D4, and its newly generated test calls make it low on D5.

**D5, test-set exposure.**
- low: new, private, post-release or live data.
- high: verbatim items with answer keys from openly distributed pre-2026 benchmarks, with no contamination check.
- unclear: public raw material recast into new items; public data with credentialed access; vendor-built data; undisclosed provenance; an inconclusive contamination check; or headline estimates that mix these sources.

**Evidence role.**
- method_paper_with_evaluation: a research paper that introduces a new model or system architecture.
- independent_evaluation: a measurement study whose authors have no stake in the model being evaluated, including studies that build an application pipeline on top of it (rafe, huang, robitza).
- vendor_evaluation: a model publisher's own documentation (model card, README or evals site) reporting on its own model. This applies whatever the publisher's affiliation type, so Kev and Rev count as vendor_evaluation even though the ledger codes their affiliation as independent.

## Notes too thin to grade fully

- grey_vercel_p95 has no n, no reference, no version and no protocol. It arguably fails the PROTOCOL inclusion rule ("marketing copy that has no protocol") and is graded only because it is in the ledger. It is a candidate for exclusion in v1.1.
- jiang2026jevmem does not state n, and its setup mentions "two widely used benchmarks" but reports only LoCoMo.
- grey_typesafe_evals gives no item counts per workflow.
- sun2026typesafe does not describe where its gold labels come from, and it defers model versions to the harness. Its four predicates match the LocalLLaMA typed-decisions workflows, whose gold is LLM-teacher, which is a probable but unstated lineage. Its headline numbers are for the open marker head, not Jev.
- The notes for wu2026reflex and yu2026visual do not resolve their code URLs.
- For the Group A studies (ibrahim, huang, li-judge, rafe, sun and zhang) there is no `parts/ledger_A.csv`. They were graded from the study notes and full text only, with no cross-check against ledger rows.
- li2026fast and li2026replacing share an author group and a testbed. This is a dependence to handle in synthesis, not a risk-of-bias domain.
