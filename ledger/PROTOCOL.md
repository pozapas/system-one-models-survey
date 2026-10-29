# Evidence ledger protocol, version 1.0 (frozen 2026-09-24)

Maintainers: the survey authors.

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

For each included study, the ledger holds one row per (study, model, task, metric) in `ledger.csv`. The row fields are listed in `SCHEMA.md`. **Every extracted number carries a verbatim excerpt and a location (page, section, table or figure) from the primary full text.** The proposal's seed numbers are hypotheses to check, not values to copy. Any disagreement goes into `seed_discrepancies.csv`.

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

## Version 1.2 (cutoff 2026-10-28)

The second sweep reruns every arXiv query of version 1.0, adds queries for the models released after the first cutoff (`survey/src/sweep_v12.py`), and covers submissions from 2026-09-14 to 2026-10-28. New records are screened in `candidates_v12.csv`. Included papers are extracted under `EXTRACTION_BRIEF_v12.md` into `parts/ledger_V01.csv` to `parts/ledger_V28.csv`, graded under `GRADING_BRIEF_v12.md` into `parts/rob_G01.csv` to `parts/rob_G14.csv`, and selected for the synthesis under `SELECTION_BRIEF_v12.md` into `selection_parts/`. The rating anchors above apply unchanged. A study that mixes new items with public pre-2026 sets is rated unclear on domain 5.

- `survey/src/merge_ledger.py` and `survey/src/merge_rob.py` rebuild `ledger.csv` and `rob.csv` from the parts. The version 1.1 grades are kept in `parts/rob_v11.csv`.
- `survey/src/verify_excerpts.py 1.2` checks every excerpt of the second sweep against the saved full text and checks that the excerpt shows the row's value (`excerpt_check_v1.2.csv`). A value computed from printed numbers has a location starting "derived from" and quotes each of them. Repairs are logged in `excerpt_repairs_v1.2.md`, `value_repairs_A.md` and `value_repairs_B.md`.
- `comparator_class.csv` codes the comparator of every accuracy contrast that enters `r1Gap` or `gapJevBest` (zero-shot open model or task-trained model for R1; frontier LLM, other LLM, task-trained model or decision model for the gap). It was added on 2026-10-28 after the first version 1.2 synthesis. For the gap it enforces the rule already stated in `synthesis.py` before version 1.2 (frontier comparators only), which the selection coders had applied inconsistently. For R1 it is an exploratory split: the pre-specified R1 estimate remains the pooled best-open-minus-Jev gap, and the split is reported beside it. The classes were coded twice, the second time without the computed contrasts or the numbers in the selection reasons (`comparator_class_blind.csv`, from `comparator_class_blind_todo.csv`), and disagreements were adjudicated in `survey/src/adjudicate_comparators.py`.
- The second rating of version 1.2 covers both sweeps. The first-sweep studies that the version 1.1 rater did not grade were rated by five further raters (`survey/notes/second_rating_v11rest/`, made by `survey/src/make_second_rating_v11rest.py`), adjudicated in `Adjudication_v11rest_returned.xlsx` and applied by `survey/src/apply_adjudication_v11rest.py`. The six studies added at the adjudication of 2026-10-29 were then rated by three further raters (`survey/notes/second_rating_added/`, made by `survey/src/make_second_rating_added.py`, with every source linked at the version the ledger extracted) and adjudicated in `Adjudication_added_returned.xlsx`, so every graded study of both sweeps has an independent second rating. Ten second raters rated a share of every task blind to the first rating (`survey/notes/second_rating_v12/`, made by `survey/src/make_second_rating_v12.py`). Agreement is computed by `survey/src/second_rating_agreement_v12.py`, every disagreement was decided by the author against the full text in `Adjudication_v12_returned.xlsx`, and `survey/src/apply_adjudication_v12.py` applies the decisions and writes `adjudication_log_v12.md`. Six papers excluded at screening were included at adjudication and extracted into `parts/ledger_V23.csv` to `parts/ledger_V28.csv`.

## Rating rules added at adjudication (2026-10-29)

The second rating of version 1.2 showed cases that the anchors above leave open. The author decided the following rules, which apply to every grade from this date, and the disputed cells were decided under them.

- Domain 3 (version). An exact model version or a revision, together with run dates, is enough for low; a revision hash or a dated snapshot is not required. Low requires this for every compared system that contributes to the results, including baselines and scoring judges, but not training-only teachers, and the domain is rated by the weakest. An incomplete version, a minor version such as Jev 1.13, or missing run dates is unclear. A missing version identifier, or an alias that the study does not resolve to a served version, is high. A model name with a version or size token but no dated snapshot or revision is an incomplete version, so unclear; it is an unresolved alias, so high, only when the study itself calls it an alias, latest, preview or a free-tier tag that it does not resolve. Outside knowledge about whether a provider name rolls is not used.
- Domain 5 (exposure). A third-party public set released during 2026 is unclear, because the release date alone does not establish exclusion from training. New items built by the authors and private items are low. A public set released before 2026 with a reported overlap or contamination check is unclear, even when the check is partial. A mixture of new items and public pre-2026 sets is unclear, whatever the share of each.
- Domain 1 (labels). A score from the observed outcome of the system's own actions in an environment, game or simulator is a task outcome, so low. A stored reference answer computed by a program or simulator is a synthetic procedure, so high. When the study does not report how its labels were made, the domain is unclear, and outside knowledge of the dataset is not used. Headline results with different reference types are unclear. An endpoint that needs no external reference label, such as an observed rating change under a controlled manipulation, is low.
- Domain 2 (reporting). A standard deviation or standard error over seeds is not an interval on a headline result or contrast. A confirmed count contradiction is high; rounded percentages alone do not establish one.
- Domain 4 (tuning). A model setting selected with feedback from the scored evaluation items is high, even when disclosed or applied to every system. A disclosed and bounded difference in training, instructions or budget is unclear. A predeclared descriptive operating point of a metric does not by itself establish tuning.
- Decision heads. When the state or a shared prefix is encoded once and every option is scored from that shared encoding in the same pass, the head is coded `b`, even when the card calls the model a cross-encoder. Code `d` is kept for a separate pass per (state, question, option) pair.
