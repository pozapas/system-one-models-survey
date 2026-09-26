# grey_vercel_p95 — Vercel "18x p95" claim (no dedicated report page found)

- Not arXiv. Grey literature: checked for a dedicated Vercel production report page; **none exists**. The "18x p95" figure lives only in two X/Twitter posts, not on any Vercel-owned property.
- Verification performed in this pass: directly fetched and grepped three Vercel-owned pages for "18x"/"p95" — https://vercel.com/blog/ai-gateway-jev-model-launch (saved fulltext/grey_vercel_blog.html), https://vercel.com/changelog/typesafe-ai-jev-now-available-on-ai-gateway (fulltext/grey_vercel_changelog.html), and https://vercel.com/i/what-is-jev (fulltext/grey_vercel_whatisjev.html). **Zero matches for "18x" or "p95" in any of the three.** This independently confirms the finding already on record in references/web/vercel_p95_report.md (an earlier capture): "this specific blog post does NOT contain the '18x p95' figure... The 18x p95 claim comes from a separate source" (the X posts).
- The claim's only sources are: Guillermo Rauch (Vercel CEO, @rauchg) on X — "Jev is up to 18x faster (p95) *and* more accurate" — and Pranit (@fazxes) on X, the underlying benchmark Rauch was citing — "we benchmarked fx auto mode (safety) classifier with @typesafeai's Jev. tl;dr: ~5-18x faster and more accurate than gpt-5.6-luna, our current top choice." Both captured (via search-engine indexing, X's bot-wall prevents direct raw-HTML fetch) in references/web/vercel_p95_report.md.
- Affiliation type: industry (Vercel and its CEO, a customer/partner of TypeSafe, not TypeSafe itself, and not an independent evaluator).

## Assessment against inclusion criteria
Per PROTOCOL.md: "Exclude... marketing copy that has no protocol." The "18x p95" figure is an unpublished internal benchmark (fx's safety-classifier comparison) reported second-hand in social-media posts, with no stated methodology, sample size, task definition, or dataset — Pranit's own post frames it as a *range* ("~5-18x faster"), and Rauch's "up to 18x" is the ceiling of that range, not a single reproducible number. No protocol, no n, no reference labels, no independent replication. **This is recorded in the ledger for completeness (it is a claim TypeSafe's own ecosystem repeats and the extraction brief specifically asked to check), but it does not meet the bar of a fully protocoled evaluation** — it is flagged as marketing-adjacent social-media commentary, closer to the excluded category than the included one. The row below is included with reference_label_type = none and an explicit low-confidence caveat.

## Task and data
Vercel's `fx` coding-agent "auto mode" safety reviewer/classifier task: comparing Jev against "gpt-5.6-luna" (per Pranit's post) as the safety-classification model for reviewing agent commands.

## Decision model / version pin
Jev (no version string given in either post).

## Reference labels
None stated; reference_label_type = none.

## n and sampling
Not stated in either post.

## Cost and latency
"~5-18x faster and more accurate" (Pranit); "up to 18x faster (p95) and more accurate" (Rauch, citing Pranit's range's ceiling). Both p95-based per Rauch's framing.

## Code and data availability
None — unpublished internal benchmark, no repository or dataset referenced.

## Seed claims checked (see parts/seed_check_C.csv)
"The Vercel production report (18x p95)" — **not_found as a page/report**: no Vercel-owned property (blog, changelog, or product page) contains this figure; independently re-verified by direct fetch and grep of all three candidate URLs in this pass (zero matches for "18x" or "p95"). The number exists only as an unattributed-methodology social-media claim (X posts by Vercel's CEO and a Vercel engineer), not as a citable "report." Recorded as `not_found` for the specific claim "a page with that number exists," while still logging the underlying social-media figure as a low-confidence, no-protocol data point.
