# Risk-of-bias grading brief, version 1.2 (cutoff 2026-10-28)

Read `PROTOCOL.md` first, above all the section "Risk of bias" with its rating anchors, then `rob.csv` for the format and the depth of reasoning expected. Each study has already been extracted, and is graded as follows.

1. The grader reads the study note `studies/<study_key>.md` and checks every claim a rating relies on against the full text in `fulltext/<arxiv_id>.txt`, `.html` or `.pdf`. The note can be wrong; the full text decides.
2. Rate the five domains as `low`, `high` or `unclear`, applying the written anchors literally. Each reason is one sentence that names the deciding fact and cites a location, for example "(Section 4.2)" or "(note Reference labels; fulltext Table 3)".
3. Derive `overall` mechanically: `high` if domain 1 or domain 5 is high, or if any two domains are high; `low` if all five are low, or if exactly one is unclear and none is high; otherwise `some_concerns`.
4. Set `evidence_role` to one of `independent_evaluation`, `method_paper_with_evaluation`, `vendor_evaluation`, `application_study`, `reverse_engineering`, `dataset_card`, `practitioner_report`. A paper whose authors build or sell the model they evaluate is `method_paper_with_evaluation` or `vendor_evaluation`, never `independent_evaluation`.
5. `notes` holds anything a reader of the synthesis must know: internal inconsistencies between text and tables, conflicts of interest, an evaluation that reuses another paper's numbers.

Grades go to the grading group's part file `parts/rob_Gnn.csv`, with exactly the `rob.csv` header and column order and the study_key and arXiv ID that the ledger rows carry. Only studies with ledger rows are graded. `survey/src/merge_rob.py` combines the parts into `rob.csv` and checks every rating and the overall rule.
