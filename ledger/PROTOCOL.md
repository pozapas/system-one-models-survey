# Evidence ledger protocol, version 1.0 (frozen 2026-09-24)

Maintainers: the survey authors. Source documents: `Paper4_Survey_Concept_Proposal_System_One_Models.md` §6 and `Paper4_Outline_Survey_and_Benchmark_System_One_Models.md` §7 and Appendix B.

## Cutoff

The literature cutoff is **2026-09-24**, the date of the sweep. Both manuscripts state this date. One re-sweep before delivery is allowed only as a versioned addendum (ledger v1.1). Its rows carry `ledger_version = 1.1`, and the v1.0 rows stay unchanged.

## Sources

1. arXiv API queries, each recorded with its date and hit count in `sweep_log.csv`: `all:Jev`, `all:"System One model"`, `all:"System One models"`, `all:"decision model" AND all:typed`, `all:"typed decision"`, `all:Laya AND all:calibrat*`, `all:Kev AND all:decision`, `all:Nimble AND all:decision`, `all:TypeSafe`, and `all:"decision models" AND all:calibration`, restricted to submissions from 2026-09-14 onward.
2. OpenAlex citation chasing from arXiv 2609.24052 and 2609.23986 and from the launch post. Semantic Scholar is used where it responds.
3. Hugging Face model and dataset search, and GitHub search (these feed the census; any measurement they report also enters the ledger).
4. The curated grey-literature list in the proposal's appendix.

## Inclusion and exclusion

Include any study that reports a measured quantity for a typed probabilistic decision model on a stated task against a stated reference. Exclude tutorials that report no measurement, SEO directories (which the census lists but the ledger does not), and marketing copy that has no protocol.

## Extraction

For each included study, the ledger holds one row per (study, model, task, metric) in `ledger.csv`. The row fields are listed in the outline, Appendix B. **Every extracted number carries a verbatim excerpt and a location (page, section, table or figure) from the primary full text.** The proposal's seed numbers are hypotheses to check, not values to copy. Any disagreement goes into `seed_discrepancies.csv`.

## Risk of bias

Each study is rated on five domains, adapted from PROBAST and QUADAS-AI. The ratings go in `rob.csv` as low, high or unclear, each with a one-line justification.

1. Reference-label independence. Human adjudicated counts as low. Human crowd counts as low or unclear. An LLM teacher, a model consensus or a vendor label counts as high. An administrative field counts as unclear.
2. Sampling design and reporting.
3. Version pinning and access dates.
4. Tuning-budget parity between compared systems.
5. Test-set exposure.

Rating anchors (written 2026-09-26 from the reasons recorded with the first ratings, after a second rater showed that domains 2 to 5 needed explicit rules):

- Domain 1: low for human adjudicated or task-outcome labels; unclear for a human crowd, an administrative field, or headline results that mix label types; high for an LLM teacher, a model consensus, a synthetic procedure or a vendor label.
- Domain 2: low when n is stated, the sampling design is described and the headline results carry intervals; unclear when some but not all of these hold; high when none holds or the counts do not reconcile.
- Domain 3: low for an exact model version or revision together with run dates; unclear for a version or a date alone, or a minor version only; high when no version identifier is given for the evaluated models.
- Domain 4: low when every compared system receives the same instructions and budget, or when a single system is studied; unclear for a disclosed and bounded asymmetry; high when one system is tuned on test data or selected after seeing results.
- Domain 5: low for new or private items; unclear for public items seen only through derived features, credentialed access or partly public data; high for verbatim public benchmark items with answer keys released before 2026 and no contamination check.

## Synthesis

`synthesis.json` holds per-regularity pooled statements, with bootstrap intervals over studies wherever at least three studies report a compatible estimand. It does not build a leaderboard across papers from incompatible estimands.

## Stability of value keys (added 2026-09-24)

The companion benchmark cites ledger rows through `lit.<value_key>` labels in `shared/results/numbers.json`. **Existing value_key strings are therefore frozen.** A corrected value gets a new row that supersedes the old one, and its key is never renamed.

## Rows from later sources (added 2026-10-01)

Rows from sources dated after the cutoff may be appended for the benchmark paper, for example L937 to L939 from the community Decision Index (2026-09-28). They carry their own source date and are not risk-of-bias graded, so the survey synthesis counts only the studies graded in `rob.csv`. A later sweep that grades them releases them as part of a new minor version.
