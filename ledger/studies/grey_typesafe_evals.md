# grey_typesafe_evals — TypeSafe AI's own "Workflow evals" (evals.typesafe.ai)

- Not arXiv. Grey literature: the vendor's own published evaluation site.
- source_url: https://evals.typesafe.ai/
- Affiliation type: **vendor** (TypeSafe AI evaluating its own Jev against other providers' models on its own harness and reference labels).
- Fetched fresh in this pass via `curl` (raw HTML contains the chart data as inline static text, no JS execution needed); saved as fulltext/grey_evals_typesafe.html and a stripped-tag plaintext extract fulltext/grey_evals_typesafe_plaintext.txt. A prior capture of this same page also exists at references/web/ts_evals.md (captured earlier in this session), which this note supplements with the full per-workflow numeric breakdown not fully transcribed there.
- Per the extraction brief: "reference = a consensus of strong LLMs, so reference_label_type = model_consensus."

## Task and data
Four example "workflows," each a hand-decomposed task turned into a harness of typed sub-questions (Noul/Choice/Score primitives) plus deterministic code rules, evaluated against consensus reference labels:
1. **Security Incidents**: given an alert and machine history, decide close / pass-to-analyst / contain-now.
2. **Agent Trace Observability**: given a full agent run (including tool calls), decide whether a person needs to review it and how soon.
3. **Invoice Processing**: given a bill, the order, and what was delivered, decide pay / hold / send-back.
4. **Customer Service**: given a support thread and account state, decide what the assistant should say/do next.
Each model configuration is run two ways: as a decomposed "workflow" (the vendor's own recommended pattern) and as a single "prompt" (the whole task in one shot) — the site's headline claim is that workflow decomposition beats single-prompt for every model on accuracy, cost and time simultaneously.

## Decision models / version pins
Jev (version not printed on this page as a pinned string, referred to simply as "Jev"), compared against: Claude Haiku 4.5, Claude Opus 5, Claude Sonnet 5 (Anthropic); GPT-5.6 Luna, GPT-5.6 Sol, GPT-5.6 Terra (OpenAI, informal lowercase names matching the "GPT-5.6" family seen elsewhere in this ledger); DeepSeek V4 Flash, DeepSeek V4 Pro (Fireworks-hosted, per the chart's "TypeSafe / OpenAI / Anthropic / Fireworks" legend).

## Comparators and tuning-budget parity
"Every model runs at its provider's default reasoning setting" (both workflow and prompt modes) — same-prompt/default-settings parity, not individually tuned per model. Workflow mode uses the vendor's own decomposition (code + typed sub-questions); prompt mode uses "the same policy as a prompt," i.e., a single free-form instruction covering the whole task — this is the vendor's own within-model ablation (workflow vs. prompt), reported alongside the cross-model comparison.

## Reference labels
"**Assume the harness is correct.** Instead of debating the correctness of the harness and labels, we assume that the code is correct, and measure against the current smartest large models. For this eval, the reference labels are generated via an average of the responses of GPT-6 Astra and Claude Fable 5.1, both at high thinking, answering every question in the harness." reference_label_type = **model_consensus** (per the brief's own instruction and the page's explicit description) — this is NOT human-adjudicated ground truth; it is an averaged pair of frontier-model responses at high reasoning effort, self-selected by the vendor as "the current smartest large models."

## n and sampling
Not stated as an item count on this page; each point on the scatter plots represents one model configuration's accuracy/cost/time "averaged... over the four workflows with equal weight, against the consensus labels" (mean-of-workflow-means methodology, not a pooled per-item average). No confidence intervals or sample sizes are shown for any point.

## Test-set exposure
Not stated; these appear to be the vendor's own constructed example workflows (not a public academic benchmark), so recorded as "new," though no explicit construction date is given on this page.

## Cost and latency (central content of this page)
Four-workflow mean, workflow mode: **Jev 67.8% accuracy, $0.0004/case, 0.4 s/case** — by a wide margin the cheapest and fastest point on both scatter plots ("frontier: nothing is both cheaper and more accurate" / "nothing is both faster and more accurate," with Jev sitting at the frontier corner on both). Comparators (workflow mode, mean of 4 workflows): Claude Opus 5 73.1% / $0.1761 / 37.8s; GPT-5.6 Sol 74.1% / $0.0836 / 23.3s (the two highest-accuracy configurations, both far more expensive and slower than Jev); Claude Sonnet 5 67.8% / $0.1174 / 78.1s (same accuracy as Jev at ~293x the cost and ~195x the latency); GPT-5.6 Luna (cheapest LLM comparator) 66.8% / $0.0033 / 12.9s (still ~8x Jev's cost and ~32x its latency). Per-workflow Jev figures: Security Incidents 61.7% / $0.0001 / 0.3s; Agent Trace Observability 71.6% / $0.0003 / 0.5s; Invoice Processing 61.8% / $0.0011 / 0.5s; Customer Service 76.0% / $0.0001 / 0.4s. hardware_or_provider = "TypeSafe hosted API (Jev); OpenAI / Anthropic / Fireworks hosted APIs for comparators."

## Calibration
The page documents Jev's typed-primitive outputs (Noul gives "P(yes)"; Choice gives "a distribution over the choices, as well as confidence"; Score gives "a score, distribution over the levels, and confidence") but reports no calibration metric (ECE/Brier) on this page — calibration_quantity = "none reported on this page."

## Cascade / escalation
Not a cascade/routing study; a workflow-decomposition-vs-single-prompt and cross-model comparison. "Averaged across the four example tasks, every model is more accurate, cheaper and faster in the workflow than it is with the same policy as a prompt" — this is the page's central within-model ablation finding (decomposition helps every model, not specific to Jev).

## Robustness / stress tests
Within-model workflow-vs-prompt gaps vary by task and model, e.g. Claude Haiku 4.5 on Security Incidents: workflow 58.8% vs prompt 17.1% (a 41.7-point gap, the largest observed); GPT-5.6 Terra on Agent Trace Observability: workflow 73.0% vs prompt 72.5% (a 0.5-point gap, near-negligible) — illustrating that the workflow-decomposition benefit is highly model- and task-dependent, not a uniform effect size.

## Code and data availability
Not applicable — a marketing/demo page with inline chart data, no downloadable dataset or code repository referenced on this page. code_available = "no."

## Limitations (page's own caveats, explicit)
- "**Assume the harness is correct**... we assume that the code is correct" — an explicit, acknowledged assumption rather than a validated one; the vendor is not claiming the harness or reference labels are independently verified.
- The reference labels are model-generated (GPT-6 Astra + Claude Fable 5.1 consensus), not human-adjudicated ground truth — a first-party vendor evaluation with no independent human reference, and Jev is being scored against labels produced by two of its own comparators' sibling/related models.
- No confidence intervals, sample sizes, or variance are shown for any point on either scatter plot.

## Notes
This source overlaps substantially with references/web/ts_evals.md (an earlier capture) but that capture recorded only two illustrative example data points, not the full per-workflow table; the rows below use the complete numbers read directly from this pass's raw-HTML fetch.
