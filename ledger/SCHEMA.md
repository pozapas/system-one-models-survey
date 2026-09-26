# ledger.csv schema (v1.0)

Each row holds one measured quantity: one study, one model, one task, one metric. Column order:

| column | content |
|---|---|
| row_id | L001, L002 and so on, stable once assigned |
| study_key | the citation key used in the bibliography, for example `ibrahim2026` (firstauthor + year + firstword, lower case) |
| arxiv_id | for example 2609.24574, or empty for grey literature |
| source_url | the abs page, the repository or the blog post |
| date | the first public version date (YYYY-MM-DD) |
| authors | "Surname, Surname, ..." (et al. after 6) |
| affiliation_type | academic / industry / vendor / independent / mixed |
| model | for example Jev, Laya, Kev-9B |
| version_pin | the exact version string reported, or `not reported` |
| task_family | document coding / social-science annotation / judging / agent control / memory / retrieval / classification / extraction / safety / QA / scientific workflow / other |
| dataset | name |
| n | number of items or decisions scored (as reported) |
| reference_label_type | human_adjudicated / human_crowd / human_single / llm_teacher / model_consensus / synthetic / vendor_label / administrative_field / task_outcome / none |
| metric | for example macro_F1, accuracy, ECE, AUROC, Brier, kendall_tau, success_rate, cost_ratio, latency_ms_p50 |
| value | **as reported, with the reported precision** (for example 0.908) |
| interval_low / interval_high | as reported, or empty |
| interval_type | for example 95% bootstrap CI, or empty |
| value_key | `studykey.camelCaseMetric` (for example `ibrahim2026.jevMedianF1Gap`), unique, [A-Za-z0-9.] only |
| comparator | the best or named comparator system for this row |
| comparator_value | its value on the same metric |
| comparator_tuning_budget | same prompt / tuned / few-shot / fine-tuned / not reported |
| cost_or_latency | as reported, with units |
| hardware_or_provider | as reported |
| calibration_quantity | ECE-equal-width / ECE-equal-mass / Brier / reliability diagram / none |
| post_hoc_calibration | none / temperature / isotonic / Platt / other |
| cascade_result | a free-text summary of any escalation result (quality retained, cost fraction) |
| test_set_exposure | public-pre-2026 / new / private / unclear |
| code_available | yes (URL) / no / partial |
| excerpt | **a verbatim sentence or table cell from the primary full text that supports `value`** |
| location | page, section, table or figure |
| extractor | the agent name |
| ledger_version | 1.0 |
