# Wang (2026), "Mnemon: Raw Records, Fast Judgments, Slow Thoughts"

Coder: batch V04. Full text: fulltext/2609.36059.html and .txt (arXiv HTML v1).

## Identification
- arXiv 2609.36059v1 [cs.CL], 28 Sep 2026.
- Author: Guangren Wang. No affiliation in the extracted text; coded independent, affiliation not stated.

## Task and data
- Long-term conversational memory agent. An LLM (System 2) plans searches over raw dated records; Jev (System 1) judges, by typed yes/no propositions, which records and index items a reply needs; rules with budgets build a View for an unchanged answering model (Abstract, Sections 3 to 5).
- Benchmarks: LoCoMo (1,540 non-adversarial questions; also reported on revised labels that drop 44 and correct 25), LongMemEval-S (500), HaluMem Medium (3,467), BEAM-100K (400), BEAM-10M (200) (Section 6.1).
- Jev-versus-LLM judging test (Section 6.5): 599 LoCoMo and LongMemEval-S questions, 14,359 records, 1,004 gold evidence records; the gold evidence labels come from the benchmarks (annotation process not described here; coded administrative_field).
- End-to-end accuracy is graded by gpt-4.1-mini (and DeepSeek-V4.1-Flash as second grader), so the label type for system accuracy rows is an LLM grader against benchmark gold answers (coded llm_teacher). The two graders agree on 96 to 97% of answers (kappa 0.85 to 0.89) on LoCoMo and LongMemEval-S (Section 6.1).
- Test exposure: all benchmarks are public and pre-2026; no contamination check.

## Decision model
- "System 1 is Jev 1.13, which judges up to 40 records per call" (Section 5, Models). Exact version string "Jev 1.13"; model documentation cited as docs.typesafe.ai/model-jaggedness/jev-1.13. No run dates stated. Hosted proprietary API; Jev list price USD 0.042 per million input tokens (Section 6.1).

## Comparators and tuning parity
- Judging test: gpt-4.1-mini and DeepSeek-V4.1-Flash "the proposition Jev answers, with the same dialogue and records" (Section 6.5). Prompts for the LLM judges are not shown in the main text.
- End-to-end: the 14 systems re-evaluated by OmniMemEval with gpt-4.1-mini answering, using their published numbers; OmniMemEval grades with gpt-4o-mini versus gpt-4.1-mini here, "a grader difference of 1-2 points" (Section 6.1). Not run by the author.
- Jev-Mem: released code, default profile, Jev 1.13, run under the Mnemon protocol on the same 1,540 LoCoMo questions; the runner's default selection by comparison to the gold answer and per-category prompt were switched off (Section 6.6). Both systems use Jev, so "this is not an ablation".

## Results
- Judging: AUC 0.942 overall (DeepSeek 0.900, gpt-4.1-mini 0.853); LongMemEval-S 0.939 (0.872, 0.798). A Jev call on 24 records takes 0.34 s answering two propositions per record; the LLMs take 1.05 to 3.74 s for one; "3-11 times faster" (Section 6.5, Figure 3).
- System accuracy with gpt-4.1-mini: LoCoMo 91.7 (MemOS 88.83), LongMemEval-S 83.8 (MemOS 89.2), HaluMem 73.3, BEAM-100K 64.5, BEAM-10M 51.2 (Section 6.2, Table 4). Effective cost index LoCoMo 0.259 vs mem9 0.337; LongMemEval-S 0.198 vs MemOS 0.147.
- Jev-Mem scores 84.4% on LoCoMo (82.1% under the DeepSeek grader), 7.3 points below Mnemon (95% CI +5.5 to +9.2); 4.1 Jev calls per question on average; 9.5 times the write-time cost per history.
- Latency: 5 to 10 Jev calls per question in 4 to 7 waves, 1.4 to 2.4 s at 0.34 s a wave; a question takes 10 to 15 s end to end at the median on a laptop with public APIs (Section 6.4, Section 7).
- Consolidation adds 2.5 (LoCoMo) to 6.2 (BEAM-100K) points (Section 6.7); not extracted.

## Sampling design and intervals
- "Each configuration ran once per setting, and two identical runs of an earlier configuration differed by up to 2.6 points" (Section 7). Paired differences between configurations carry 95% CIs. The AUC values have no intervals.
- "Mnemon was developed on LoCoMo and LongMemEval-S, and consolidation was designed after we had seen results on HaluMem and BEAM-100K, so none of the benchmarks is held out" (Section 7).

## Calibration and cascade
- Jev probabilities are used as a ranking score (AUC) and thresholded by rules; no calibration analysis. No escalation analysis for Jev; the planner/judge split is a fixed architecture.

## Cost
- Token-based list-price costs per 1,000 questions (USD 3.27 on LoCoMo) cover answering, planning and Jev; the author's total spend is not extracted.

## Robustness
- Scale test 100K to 10M tokens of history on BEAM (cost per question grows by a factor of 1.11). No option-order, option-name or language tests for Jev.

## Code and data
- https://github.com/Grivn/mnemon-memory-agent (MIT licence; run records under each benchmark's terms; HaluMem excepted) (reference [49], Conclusion).

## Authors' stated limitations (Section 7)
- Development on the evaluation benchmarks, grader differences, single run per configuration, only conversational memory tested, dependence on a hosted proprietary model with "no substitute tested in the full system", latency and privacy.
