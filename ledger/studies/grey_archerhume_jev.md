# grey_archerhume_jev — "Jev's Architecture Unmasked" (Archer Hume)

- Not arXiv. Grey literature: personal blog essay (independent reverse-engineering investigation of the vendor's hosted Jev API).
- source_url: https://archerhume.com/posts/jevs-architecture-unmasked/
- Affiliation type: independent (personal blog, archerhume.com; no institutional affiliation stated).
- Fetched fresh in this pass via `curl` of the live page (2026-09-24); saved as fulltext/grey_archerhume_raw.html and a stripped-tag plaintext extract fulltext/grey_archerhume_plaintext.txt. A prior capture of this same page also exists at references/web/archerhume_architecture.md (an earlier capture); that earlier capture explicitly flagged uncertainty about the "~10,000 API calls" figure, saying it "could NOT be located anywhere in the actual retrieved article text" and might be a WebSearch-tool fabrication. **This re-fetch of the raw HTML directly confirms the figure is genuinely present** in both the page's meta description and its visible body text (see Seed claims below) — the earlier flag was a false negative, not a fabrication; it should be treated as resolved.
- The essay's page metadata gives `datePublished`/`dateModified` both 2026-09-17T00:00:00.000Z; the essay itself states "This essay is based on a 17 September 2026 investigation of jev-1.13.0, using one early-access account and one observed service region" (Methods section).

## Task and data
Not a benchmark evaluation in the usual sense; a black-box probing study of the hosted Jev API (jev-1.13.0) to infer its architecture, tokenizer, option-handling mechanism, and calibration, using deliberately constructed API request batteries: latency-vs-input-length probes, latency-vs-question-count probes, a tokenizer fingerprint experiment (445 requests, compared against 192 public tokenizers), option-order/option-count probes, an irrelevant-added-option experiment (ten randomized blocks), and a calibration analysis on a 1,200-item MMLU sample plus a small "fresh maths" generated-word-problem set (8 families, 20-30 items each).

## Decision model / version pin
Jev, pinned as "jev-1.13.0" throughout (Methods: "investigation of jev-1.13.0"), accessed via one early-access account against one observed API service region.

## Comparators and tuning-budget parity
Not a model-vs-model accuracy comparison; this is a single-model (Jev) black-box characterization study. The only "comparator" concept is against reference tokenizers (192 public tokenizers tested) and against theoretical models of the scoring mechanism (fixed independent logits vs. joint/listwise readout).

## Reference labels
For the MMLU calibration analysis: reference_label_type = human_adjudicated (the standard MMLU answer key / gold labels). Per the extraction brief's own instruction, these reference labels are rated as the canonical MMLU answer key, not an LLM-teacher or crowd label.

## n and sampling (Methods section, verbatim counts)
"The source study contains 1,029 instrumented probe records (including the 190 generated-math items), 6,800 benchmark records, and separate factual checks. Follow-up studies added 146 relational and option-interaction requests." Specific sub-experiments: tokenizer fingerprint experiment, 445 requests, compared against 192 public tokenizers; option-order experiment (Figure 3), 2 tasks x 2 card values x 2 repeats per order x multiple orders; irrelevant-added-option experiment (Figure 4), 10 randomized blocks; MMLU calibration sample, 1,200 items (ten equal-width probability bins: [0,0.1), [0.1,0.2), ... , with 990 of 1,200 items falling in the 0.9-1.0 bin); "fresh maths" calibration check, 8 generated problem families, 20-30 items each.

## Test-set exposure
MMLU is a public pre-2026 benchmark, so classed as public-pre-2026 for the calibration analysis (a possible training-data-overlap caveat the essay itself raises: "family averages agreeing is weaker evidence than bins agreeing... That gap does not establish benchmark [contamination]" — the essay explicitly contrasts MMLU-Pro accuracy (84.6%) against "newly generated word problems," which "were much harder," to probe whether performance reflects genuine capability vs. memorized benchmark exposure). The "fresh maths" generated items are new/synthetic (2026), reducing contamination risk for that sub-check specifically.

## Cost and latency
Not a cost study; latency figures are used only as an architectural probe (input-length scaling, question-count scaling), not as a serving benchmark. hardware_or_provider = "TypeSafe hosted API, one early-access account, one observed service region" (not the author's own hardware).

## Calibration — the central quantitative result relevant to this ledger
"On the 1,200-item MMLU sample, ten-bin expected calibration error was 0.0313" (rounds to the seed's "ECE 0.031"). Binning: "ten equal-width bins: [0, 0.1), [0.1, 0.2), and so on" (Methods/footnote), "probabilities rounded to two decimals before binning." Most predictions (990/1,200) fell in the top bin (0.9-1.0), predicted mean 98.7% vs. observed accuracy 96.3% (95% Wilson interval 95-97%) in that bin — i.e., Jev is very slightly overconfident in its most common (near-certain) bin on MMLU, but the overall 10-bin ECE is low (0.031). MMLU-Pro accuracy separately cited as 84.6% (a capability figure, not calibration). calibration_quantity = "ECE, ten equal-width bins, probabilities rounded to 2 decimals"; post_hoc_calibration = none (this measures Jev's calibration as-shipped via its API, no recalibration applied by the author).

## Cascade / escalation
Not applicable — a single-model probing study, no routing/cascade design.

## Robustness / stress tests (the essay's main architectural-inference content)
- **Tokenizer fingerprinting**: Jev's token counts match none of 192 public tokenizers across 415 probes; closest public match (Qwen family) agrees on only 348/415 probes — evidence against an unmodified public tokenizer (though not against a public base model with a replaced/extended vocabulary).
- **Option-order sensitivity** (Figure 3): with a reference-card option placed last, 16/16 (and pooled 48/48 when in shared state) correct with mean probability ~0.87-1.00; with the card first or in the middle, correctness fell to 11-12/16 and probabilities "scattered widely around 0.5" — "order sensitivity, not a recovered attention mask." Reversing options in an ordinary technical-support classification task shifted the correct-class probability from ~0.84-0.89 to ~0.93-0.96 (option_order probes).
- **Irrelevant-added-option experiment** (Figure 4): adding an irrelevant 5th option ("weather: Bad weather caused it") to a 4-option question shifted the log-odds between two existing, unrelated options from a mean of +0.38 to +0.11 across ten randomized blocks (mean change -0.28, descriptive 95% paired-t interval [-0.36, -0.19], decrease in every block) — evidence against independent per-option logits with a shared-denominator softmax (a fixed-logit model predicts no change); consistent with a listwise/joint readout over the full option list.
- **Fresh-math calibration check**: on generated 3-digit-product problems, accuracy 86.7% vs. mean top probability 83.0% (close); on two-step word problems, accuracy fell to 32.0% vs. mean top probability 30.4% (still close); "modular exponentiation is the clear exception, right 56% of the time at a mean probability of 35%" (underconfident on that specific family) — overall reasonable per-family calibration on freshly generated, non-benchmark items.
- **200-option / injected-fake-option check**: with 200 offered options, a copied answer scored 1.00 "at every position and errors didn't spill onto neighbouring options" (consistent with a pointer-style scorer); injected fake options "never displaced the real ones."

## Code and data availability
Probe scripts, request payloads, and per-item MMLU predictions are linked from footnotes ("bin definitions and item-level predictions," "Request payloads and answers," "Reliability data") but specific repository URLs were not resolved as plain-text links in this pass (the site renders citation links as numbered footnote anchors); code_available = "not reported (footnoted data links present on page, exact repository URL not extracted in this pass)".

## Limitations (essay's own explicit caveats)
- "This essay is based on a 17 September 2026 investigation of jev-1.13.0, using one early-access account and one observed service region" — single account, single region, single time window; results may not generalize across accounts/regions/later Jev versions.
- "The exact [RLCD training] recipe is unpublished... It does not establish which loss TypeSafe uses, whether its pipeline is reinforcement learning in a narrow algorithmic sense, or whether every backbone weight is updated" — explicit acknowledgment that architectural/training claims are inference, not confirmed vendor disclosure (also flagged in the earlier session capture, references/web/archerhume_architecture.md).
- "Black box APIs make it shockingly easy to throw a blanket over the ghost and get a rough shape of what the architecture looks like" — author's own methodological caveat about the limits of black-box inference.
- "Family averages agreeing is weaker evidence than bins agreeing, since over- and underconfidence can cancel within a family" and "Vertical lines are 95% Wilson intervals, which cover sampling noise only, not benchmark selection or training exposure" — explicit statistical-scope caveats on the calibration claims.
- "Neither result is decisive" (on the pointer-vs-final-position-head readout question) — architecture inference explicitly left unresolved between two candidate mechanisms.

## Seed claims checked (see parts/seed_check_C.csv)
1. "ECE 0.031 on 1,200 MMLU items" — confirmed exactly: "On the 1,200-item MMLU sample, ten-bin expected calibration error was 0.0313" and the figure panel is directly labeled "MMLU sample 1,200 items · ECE 0.031."
2. "10,000+ API probes" — confirmed: the page's own meta description and body state "I probed Jev with 10,000 API calls to work out roughly how it's built." The itemized Methods breakdown (1,029 instrumented probe records + 6,800 benchmark records + 146 follow-up relational/option-interaction requests + a 445-request tokenizer fingerprint experiment, etc.) sums to roughly 8,400-8,800 explicitly itemized requests, somewhat below a literal 10,000, so "10,000" reads as the author's rounded headline total across all probes/sub-experiments rather than an exact sum of the itemized figures; treated as confirmed (the source's own stated headline number) with this itemization caveat noted.
