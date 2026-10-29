# Synthesis selection brief, version 1.2

The survey's synthesis (`survey/src/synthesis.py`, read its docstring and `read_selection`) types no number. It reads `synthesis_selection.csv`, where every line says which ledger row enters which analysis, in which role, and how the number is read from the row. The version 1.2 studies get lines of the same kind, and the 160 lines of `synthesis_selection.csv` with their `reason` texts set the standard.

## Columns

`analysis,row_id,role,include,reason,record,group,subset,a_field,a_pattern,a_stage,b_row,b_field,b_pattern,expr,ref_override,fit`

- `row_id`: the ledger row (from `parts/ledger_Vnn.csv`). `b_row`: a second row when the second number sits in another row; empty means the same row.
- `a_field`, `b_field`: the column the number is read from (`value`, `comparator_value`, `cost_or_latency`, `excerpt`, `n`). `a_pattern`, `b_pattern`: optional regular expression with exactly one capture group that must match the field exactly once (needed when the field holds text, for example `^([\d.]+) \(`). Without a pattern the field must be a bare number.
- `expr`: one of `a`, `-a`, `a-b`, `b-a`, `a/b`, `b/a`, `a/100`, `1-a/100`, `-100*a`, `100*(a-b)`, `100*(b-a)`, `1/(1-a/100)`.
- `role`: `estimate` enters the pooled summary; `context` is reported but not pooled; `comparator` only in `r2LlmTemp`.
- `subset`: `primary` for the one headline estimate per study and analysis; `sensitivity` for an alternative reading; empty for context.
- `record`: a short camelCase label unique within the analysis (for example `zhangAbsa`); lines of different analyses that describe the same experiment share it.
- `include`: `yes`, or `no` with the reason why a tempting row was left out.
- `reason`: one line saying what the number is, which systems, which items, and anything a reader must know (own model, transferred fit, oracle comparator).
- `ref_override`: only when the study note shows the ledger's `reference_label_type` is wrong for this number.
- `fit`: for recalibrated ECE, where the recalibration was fitted (`same items`, `held-out split`, `transferred (A to B)`).

## Analyses

- `r1Gap` (R1): the best open or reproduced decision model minus Jev, on the same items, in points on a 0 to 100 accuracy-type scale (`group` accuracy, macroF1, F1 or score; AUROC as context). Positive means the open model is ahead.
- `r1Readout` (R1): within-backbone contrasts of a typed decision readout versus another readout (label probabilities, generated answer, fine-tuned answer) on the same backbone; context only.
- `gapJevBest`: Jev minus the best comparator of any kind (LLM, fine-tuned classifier) on the same items, points on a 0 to 100 scale, so negative means Jev is behind. `group` names the metric. One primary line per study.
- `costRatio`: comparator cost over Jev cost on the same workload (above 1 means Jev is cheaper). `speedRatio`: comparator latency over Jev latency, same rule. Group `cost ratio` or `latency ratio`.
- `r2JevEce` (R2): Jev's raw ECE as `a` with `a_stage` `raw`, and its recalibrated ECE as the second number (`b_row` or `b_field`) when reported. `group` names the binning exactly (for example `equal-width 15 bins`, `equal-mass 10 bins`, `not specified`). Never put SmoothECE or another estimand in an ECE group; make it context with the estimand in `group`.
- `r2OpenEce`: the same for open decision models. `r2LlmTemp`: LLM comparators' ECE with role `comparator`.
- `r2Cbw` (R2, confidence informativeness): accuracy in a high-confidence subset minus the base rate, AUROC of confidence for correctness, flip rates, confident-error shares; `group` names the quantity.
- `r3Retained` (R3): cascade quality over the quality of the strong model alone (`accuracy ratio`, `error ratio`, `success ratio`). `r3FeeFrac`: the share of the strong model's fee the cascade pays. `r3StrongFrac`: the share of items escalated. Lines of one cascade share `record`. `r3Context`: deferral budgets and other escalation numbers that are not a cascade against a strong model.
- `typeErrors`: the rate of answers outside the declared option set.

## Rules

1. Only quantities on the same items for both numbers of a contrast. If a contrast mixes item sets, models or metrics, leave it out or make it context, and say why.
2. At most one `primary` estimate per study and analysis. Choose the paper's own headline; record the others as context or sensitivity.
3. Open-model-only papers enter `r1Gap` only when Jev was scored on the same items in the same paper; a Jev number quoted from another source is context with that said in `reason`.
4. Every line is checked with `read_selection`'s parsing, so that no pattern fails or matches twice.

Lines go to `selection_parts/sel_Snn.csv`, one file per selection group, which `synthesis.py` reads after `synthesis_selection.csv`.
