# Zhang et al. 2026, JevCoder: When Does Decision Delegation Pay Off in Code Repair?

arXiv:2610.19596v1 [cs.SE], 14 Oct 2026, CC BY 4.0 (fulltext/2610.19596.txt, header). Application paper with embedded judgment-quality evaluation of Jev.

## Authors and affiliations

Jiahao Zhang, Yifan Zhang, Yu Huang, all Vanderbilt University, Nashville, Tennessee, USA. Affiliation type: academic (title block).

## Task and data

Repository-level issue repair by a coding agent. Full-workflow evaluation on 400 tasks, 200 from SWE-bench Verified and 200 from SWE-Bench Pro Verified, in Python, Go, JavaScript, TypeScript (Section 3). Component studies use balanced samples (DeepSeek: 72 SWE-bench Verified plus 118 SWE-Bench Pro Verified tasks, all baseline failures plus an equal number of random successes; Qwen similar; Section 3). Patch-outcome study: 1,192 submitted-patch records from 343 tasks (Section 3). Labels come from reference patches (files modified, lines removed) and official test outcomes; repair-state labels are program rules and are called proxies in Limitations (Section 3, Limitations). Benchmarks predate 2026 (SWE-bench Verified 2024, SWE-Bench Pro ICML 2026 proceedings); no contamination check reported.

## Decision model

Jev, "jev-1.13.0 endpoint", a fixed model ID, remote API; binary (probability of yes), Choice and Score (ordered levels) question types, probability fields only, no explanations (Appendix A.2). Service limits 64k tokens evidence plus questions. Run dates not stated; pricing pages accessed 13 Oct 2026.

## Comparators and tuning parity

Same-model judges: DeepSeek-V4.1-Flash (temperature 1) and Qwen3.8-27B-FP8 (revision 017b9c7a..., temperature 0) read probabilities of answer tokens with the same question and evidence as Jev (Section 3, Appendix A). Small model Qwen3.5-2B for file relevance and repetition. Gemini 3.8 Flash has no same-model judge because its API hides token probabilities. Unguided repair is the baseline for the workflow comparison. Question wording and evidence are identical across judges. Intervention thresholds were chosen from component studies on the same task pools (Appendix D.4 "Component selection for JevCoder"), a selection-after-seeing-results risk for the full-workflow comparison.

## Headline results

Judgment quality (Table 1): top-1 file hit 75.9 vs 29.0 (Qwen3.5-2B) on 162 tasks (Section 4.1); selection recall 81.6 vs 78.0 (DeepSeek) on 189 tasks; AUROC for code located 0.738 vs 0.701, issue reproduced 0.822 vs 0.804, stalled repair 0.968 vs 0.931, post-edit check 0.802 vs 0.797; patch outcome binary 0.595 vs 0.684 (Jev worse), score 0.642 vs 0.652; successful-check signal 0.990 vs 0.974 on 52 states (Sections 4.1 to 4.3). Repeated-command recall 99.4% at 0.6% false-positive rate vs 95.5% and 17.6% for Qwen3.5-2B on 883 pairs (Section 4.2).

Workflow (Table 3, 400 tasks, one run per task and condition): repair rate DeepSeek 76.25 to 77.25, Qwen 45.00 to 46.75, Gemini 68.25 to 71.00; total repair-model tokens down 21.6%, 50.6%, 26.9%; Qwen saving 0.756M tokens per task, 95% paired bootstrap CI 0.590M to 0.931M (Section 7). Same-model judging: total tokens down 13.7% (DeepSeek) and 35.5% (Qwen); JevCoder uses 9.1% (DeepSeek, CI includes zero in Appendix E) and 23.3% (Qwen) fewer than same-model judging (Introduction, Appendix E).

Cost: Jev list price US$0.042 per million input tokens, output free; Jev usage 0.152M to 0.193M tokens per task; estimated API cost down 4.2% (DeepSeek) and 29.7% (Gemini) including Jev charges (Appendix E, Tables 14, 15).

## Calibration

No ECE or reliability analysis. Probabilities are used as rankings (AUROC) and thresholds; thresholds are calibrated on one model's trajectories and reused (Appendix C.2). Related work cites SWE-RM on calibration, not measured here.

## Cascade and escalation

Judge-gated interventions: snippet ranking, action-type guidance, early submission when successful-check probability meets a threshold; "half of Jev's 32 reminders are followed by submission within five requests" (Section 5.3). Command blocking and file-recommendation Score interface failed the prespecified repair-loss criterion on Qwen and DeepSeek respectively (Table 2, Section 5.1 to 5.2).

## Option-name, cardinality, language, robustness

None; fixed question wording. Binary relevance over 100 candidate files versus Choice over 10 files and Score interface compared (Table 1 footnotes).

## Cost, hardware

Local inference on two NVIDIA L40S, about 200 GPU-hours; Jev, DeepSeek, Gemini by remote API; runtime with fixed connection delay subtracted (Appendix A, Limitations). Authors' own spend (US$1,500) is not recorded in the ledger.

## Code and data availability

Anonymous artifact link https://anonymous.4open.science/r/jevcoder-artifact-8E62; saved answers allow replay without calling the service (Introduction, Limitations).

## Paper's own limitations

One Jev version, three repair models, 400 tasks, one agent framework; one run per task and condition so no run-to-run variance; file relevance and repair-state labels are proxies; runtime depends on serving conditions (Limitations).
