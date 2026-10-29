# min2026prune — Prune the Summary, Not the History: Source-Judged Compaction for Long-Horizon Agents

arXiv:2610.20927v1 [cs.CL], 14 Oct 2026 (title page). HTML from https://arxiv.org/html/2610.20927. Extractor: batch V15.

## Authors and affiliation
Guanghui Min, Chen Chen (corresponding). Department of Computer Science, University of Virginia (title page). Affiliation type: academic.

## Task and data
Jev is an application component, not the object of study: a training-free post-processing step (SJC) that scores each entry of an agent's compaction summary for whether it has a source in the environment outputs or the previous summary, prunes entries below tau = 0.5 (Sections 4, 5.1; Appendix F). Evaluation on AppWorld test-normal (168 tasks: 57 easy, 48 medium, 63 hard) and the 95-task OfficeBench test set of ACON (42 one-app, 22 two-app, 31 three-app), three runs per configuration (Section 5.1). Failure analysis and judge validation use the AppWorld training split (90 tasks, three runs) (Section 3).

## Decision model
Jev-1.13 (TypeSafe AI), accessed through the OpenRouter API; "a non-generative decision model that answers a typed question with a calibrated probability" (Section 5.1). Question posed as a yes/no decision, p(yes) is the source score; one request per compaction, all entries pooled with BM25-retrieved evidence, 32K context, max request 29.0K tokens (Sections 4, 5.3; Appendix F). No dated revision string is given beyond "Jev-1.13"; blog cited "Accessed: 2026-10-05" (References). Run dates not stated.

## Comparators and tuning budget
Agent and compressor are GPT-5.6 Luna (medium reasoning) or MiniMax-M3, same model for both. Baselines: No compression, FIFO, LLMLingua, LLMLingua-2, Fast-Jev (Jev selects raw history), Prompting (OpenClaw structured compaction prompt), and SJC with the compressor as its own judge (Self) (Sections 5.1, 5.4). All run under the same agent settings (Appendix F); tau was not tuned ("we did not tune tau", Appendix F). The OpenClaw prompt is used as is. Comparators are therefore the same agent and compressor; no per-method tuning is described.

## Reference labels
Main outcome: task success from the benchmark evaluation scripts (task_outcome). Judge validation labels (300 reasoning entries, support and correctness) were produced by LLM annotators under a written protocol, two independent rounds, kappa 0.95 and 0.88, authors resolved disagreements (Appendix G). The failure attribution of 44 failed runs also used LLM annotators (Appendix D; Limitations says so). Coded llm_teacher for the judge-validation rows.

## n, sampling, intervals
168 AppWorld tasks and 95 OfficeBench tasks, 3 runs each; Acc. reported as mean with across-run SD, Pass3 as a point value (Tables 3, 4). No confidence intervals on task metrics. AUROC intervals are 95% bootstrap over task scenarios (Table 12). Differences are in absolute percentage points (Section 5.2).

## Test-data exposure
AppWorld (Trivedi et al., 2024) and OfficeBench (Wang et al., 2024) are public pre-2026 benchmarks. No contamination check reported. Because the metric is task success under a changed compaction step, exposure affects all arms alike.

## Cost and latency
Judge cost $1.19 to $1.52 per 1,000 tasks at $0.042 per million input tokens; SJC lowers cumulative agent plus compressor tokens by 1.3% to 8.0% relative to Prompting (Section 5.3; Table 5). Jev calls are excluded from the token totals and reported separately. No latency measurement.

## Calibration
No calibration metric (no ECE or Brier). Jev scores are described as bimodal (73.9% at least 0.8; 10.6% below 0.2; 8.1% between 0.3 and 0.7; Section 5.4). tau varied 0.3 to 0.7 changes pruned fraction by at most 10.2%. At tau = 0.5 the judge "errs toward pruning" and recovers 64.2% of supported entries (Limitations; Appendix G). Calibration language ("calibrated probability") is asserted, not tested.

## Cascade or escalation
None.

## Option-name, cardinality, language and robustness tests
Repeatability only: the same 40 judge requests (1,598 entries) issued five times, Jev changes answer on 2.1% of entries versus 8.6% for the generative self-judge (Section 5.4). No option-order, language or cardinality test.

## Code and data
Code at https://github.com/GuanghuiMin/sjc (abstract).

## Authors' stated limitations
Provenance is not correctness (supported and unsupported entries correct at 92.2% vs 90.6%); the judge prunes some correct or helpful entries; only two benchmarks, two agent models, one host compressor, small context windows; single-instruction tasks only; external API judge not fully deterministic; failure analysis relies on LLM annotators (Limitations).
