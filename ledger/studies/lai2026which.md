# lai2026which

arXiv 2610.30045v1 (cs.AI), 21 Oct 2026. "Which Differences Matter? Controlled Tests of Rule Transfer, Joint Reliability, and Information Use in Decision Models." (title block)
Authors: Tianyou Lai (Carnegie Mellon University), Wentao Yue (Shenzhen University), Zhiwei Zuo, Qilei Li (Central China Normal University; corresponding). Affiliation type: academic. (title block)

## Task and data
Executable arithmetic rules over three integer fields in {-12..12}, four task families (binary, ordinal rating, minimum routing, maximum selection), options 2 to 8. Programmatic oracle labels, semantic rule separation between source, development and reserved pools, crossed rule-by-state quartets (QAcc = all four correct). Interventions: equivalent rewrites of rules, table value and mapping alterations (D2 complete values, D3 missing, altered targets). Synthetic items generated for this study. (Sec. 3, 4.1, App. A)

## Models
Controlled local models on Qwen3.5-2B-Base (Base, rank-4 readout, LoRA rank 16 trained on 2,880 source questions per cell, source-selected MLP readouts); Qwen3.5-9B instruction model; Decider, StartLux-Decision-2B, MedJev-type systems in Appendix. Jev is the only hosted decision service: "jev-latest" request alias; all successful responses report jev-1.13.0 (Table 7, App. B); jev-1.13.0 for the 1,920 repeated-request measurements (App. L.5). Native structured requests (App. L.10). Jev is zero-shot; LoRA models are fine-tuned on source-rule data, so budgets are not matched (authors note source competence unmatched). (Sec. 4.1, 5, App. B)

## Results used
Development rules: Jev natural 60.44, diagnostic item 55.34, QAcc 22.05; LoRA 58.03, 53.13, 13.19; Controlled Base 38.67, 33.81, 0.52 (Table 1). Reference ranges for QAcc via 1,000 stratified reassociations (Table 3). Table interventions: Jev switches to the altered-table target on 76.82% (formula rows, 169/220), 91.05% (record columns, 173/190) and 75.94% (target values, 243/320) of conflicts (Table 4). Wording: cross-wording disagreement exceeds identical-text disagreement in every elapsed-time stratum with both comparisons (Table 23); pooled rates are shown only in Fig. 3, not in text. Jev semantic agreement across 32 repeated requests 90.625% (max probability change 0.12) and 93.02% across 43 option-reversal comparisons (App. B). Binding study: Jev correct under D2 but wrong under D6 on 21.88% of items, reverse 4.17% (App. L).

## Intervals and statistics
Quartet-resampling 95% intervals, paired bootstrap, 1,000 reassociations, no multiplicity adjustment stated for task-level results; Jev's repeats estimate within-window variability only, not variation across service versions. (Sec. 4, Limitations)

## Calibration, cost, cascade
No ECE for Jev; QAcc calibration is a joint-correctness reference, not probability calibration. No cost or latency reported. No cascade.

## Test-data exposure
New synthetic items; no pretraining overlap claim made ("they make no assertion about an external model's pretraining data").

## Code and data
"Code and data will be made available" (abstract); none at time of writing.

## Authors' limitations
Fixed-depth arithmetic rules on bounded integers; fully conflicting cohorts only 39 and 32 quartet memberships; LoRA-versus-readout compares attained outcomes; QAcc describes constructed quartets; Jev's repeats limited to the observed service window; model comparisons concern these diagnostics only.
