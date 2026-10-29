# Adjudication of the second rating of the studies added at adjudication

Source: Adjudication_added_returned.xlsx. Every disagreement between the first rating and the second rating was decided by the author against the saved v1 full text that the ledger extracted and the raters read. Rows whose final value equals the first rating are not listed, and the author's note on every cell follows.

## Risk of bias

| id | study | domain | first | second | final | reason |
|---|---|---|---|---|---|---|

## Author's notes

| id | study | domain | first | second | final | note |
|---|---|---|---|---|---|---|
| RB001 | wu2026covnav | 5 | unclear | high | unclear | Retain unclear. Habitat scores live rollouts, and the decision stage receives generated object-pair questions. Public episode exposure is through derived inputs. Source: saved Section III-D.1 and Section IV-A. This follows the earlier first-sweep RB014 reading. |
| RB002 | zhan2026dyad | 4 | unclear | low | unclear | Retain unclear under C2. Dyad receives RL training and its headline reasoning variant generates 120.44 tokens. Jev runs as released in one pass. The matched RL comparisons do not cover this Jev comparison. Source: Section 5.4, Table 5, Appendix B.3. |
| RB003 | zhan2026dyad | 5 | unclear | high | unclear | Retain unclear under G3. Older public benchmarks appear with 2026 third-party sets, including JevBench and HMMT February 2026. Source: Section 5.1, Appendices B.1 to B.3. The older subsets alone do not describe the complete evaluation. |
| RB004 | li2026sok | 1 | high | unclear | high | Retain high under G5. The model correctness endpoints use stored answers computed from feasibility and cost predicates. Literature-coding labels assess the review, rather than model correctness. Timing endpoints introduce no additional correctness reference. Source: Tables IX and XI, Section IX. |
| RB005 | li2026sok | 3 | high | unclear | high | Retain high under G2. MiniLM has compared correctness rows, but the saved text gives no size, checkpoint or version identifier. Other models' incomplete versions do not resolve this missing baseline identifier. Source: Tables X and XIX. |
| RB006 | li2026sok | 4 | unclear | high | unclear | Retain unclear. Section VI-D gives ranges of ±3 percentage points and ±50 ms but does not date their selection. Later choice is not established. The earlier v1.2 RB093 and RB148 margins were explicitly post hoc. Exploratory synthesis questions alone do not establish model tuning. Undescribed model instructions and bundled workflow changes remain. Source: Section VI-D, Figure 7, Section IX. |
| RB007 | besanson2026probabilistic | 4 | low | unclear | low | Retain low for the registered E1 and E2 comparisons. The earlier E0 Haiku arm failed on code-fenced replies. Its repair was registered, and E0 is reported separately. Main thresholds were committed before test calls, after validation health checks. The first-sweep RB020 changed semantic handling after target failures. This record does not establish score-driven selection. Source: Sections 5, 6 and 7.1, Appendix B. |
