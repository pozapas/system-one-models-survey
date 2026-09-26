# dossantos2026calibrated — Calibrated Decision Models for Autonomous Penetration-Testing Harnesses: JEV and Laya as System One Decision Layers for LLM-Driven Pentest Agents

arXiv:2609.28940v1 [cs.CR], submitted 24 Sep 2026. HTML retrieved from https://arxiv.org/html/2609.28940v1.

## Authors and affiliation

Joas Antonio dos Santos (joas.santos@redteamleaders.com), sole author. Affiliation: "Independent Researcher — AI and Offensive Security," São Paulo, SP, Brazil (title-page). Affiliation type: **independent**. Acknowledgements state that "Generative language-model tooling assisted with drafting and reference verification; all sources were checked by the author against their original records, and the author takes full responsibility for the content."

## Task and data

An architecture/position paper (five contributions per the Abstract) built around one small **exploratory case study**: NeuroSploit, the author's own open-source Rust autonomous-pentest harness (github.com/JoasASantos/NeuroSploit), run against "NimbusCart (BenchMarkBurpAT), localhost:3000," a web target seeded with "13 seeded vulnerabilities: IDOR, BOLA, five SQL injection variants ..., four XSS variants ..., open redirect, and CRLF injection" (Table V, §IX-A). The paper is explicit about its own evidentiary weight: "We conducted an exploratory case study comparing a single run with and a single run without the System One decision layer. Because each condition was executed once against a single target, the results are observations that motivate the architecture, not statistically powered experimental evidence" (§IX-A).

## Decision models evaluated

**Jev** (TypeSafe), commercial, invoked via NeuroSploit's `--typesafe` flag; System One model field in the benchmark configuration is given only as `jev-latest` (Table V) — no patch-level version string and no explicit run/collection date beyond the paper's own submission date. The curator LLM in both arms is `claude-opus-4-8` (subscription access), vote count 1 (single model), max agents 15, recon intensity 2, black-box (Table V). **Laya** (open-source, ModernBERT-large, Apache 2.0) is discussed only through its own published documentation/benchmarks (§XIII-C) and is **not run in the NeuroSploit case study** — the paper's own limitations list states "No Laya comparison. The Laya comparison uses published benchmarks on general-purpose tasks, not offensive-security evaluations" (§XV-A).

## Comparators

Within the case study, Run A (no TypeSafe, LLM-only adjudication/grading) is the comparator to Run B (with TypeSafe/Jev); both arms use the identical target, harness, curator model, and CLI parameters, with `--typesafe` as "the sole variable" (Table V caption). Comparator_tuning_budget = "same prompt" (same harness, same curator, same target). Outside the case study, Table IX and §VIII-B/D compare Jev's and Laya's *separately published* specifications (different tasks, different hardware) explicitly flagged as "informational, not a controlled benchmark" (Table IX caption) and not usable as a like-for-like comparator row.

## Reference labels

For the case study, "ground truth" is the known set of 13 deliberately seeded vulnerabilities in NimbusCart (`task_outcome`: each vulnerability is either found/confirmed or not, an objectively verifiable outcome). Severity grades (Critical/High/Low/Informational) are the harness's own CVSS-calculator output, gated by System One (Jev) probabilities in the `--typesafe on` arm and by LLM narrative judgment in the `--typesafe off` arm — there is no independent gold severity label; the paper narrates specific cases (e.g., the BOLA finding) where it argues one arm's grade is closer to "demonstrated impact" than the other, but this is the author's own post hoc judgment, not an external adjudication.

## n, sampling design

One run per arm (n=1 harness execution per condition) against one target (NimbusCart) with 13 seeded vulnerabilities; a separate, non-comparable "gap re-test" after harness code changes re-confirmed 7 previously-missed scenarios in both arms (Table VII) and reported a severity distribution over "22 total findings in both arms" (Table VIII) — but this re-test used a modified harness and explicitly "cannot be compared with the initial run as a controlled pair" (§IX-C, §IX-D). The paper's own limitations (§XV-A) state "Single target. NimbusCart is one data point; external validity requires diverse targets with ≥3 runs each" and "Single-vote configuration."

## Test-set exposure

"Possible memorization. NimbusCart may appear in training data; partly-private targets are needed for external validity" (§XV-A, the paper's own stated limitation) — classified `unclear` (an author-built benchmark target of undisclosed public exposure, with the authors themselves flagging possible contamination).

## Cost and latency

Case study (Table VI): Model cost Run A "$0 (sub.)" (subscription pricing), Run B "$0 + TS (<< $5)"; §IX-G: "TypeSafe API cost was under $5." Wall-clock time: Run A 32m 12s, Run B 26m 53s — "Run B completed 5 minutes 19 seconds faster," with the paper immediately cautioning that "with a single run per condition, the time difference could also reflect stochastic variation in LLM response times, network latency, or target-server load" (§IX-G). Separately, Table III reports latency **as published by each vendor/source, not measured head-to-head by this paper**: "Jev and Laya values are from their published documentation on different tasks and hardware; LLM baseline from observed claude-opus-4-8 response times in our setup. Direct comparison is informational, not a controlled benchmark" — Jev (API) 236–276 ms p50 (217–254 decisions/min, 1 batched call for 15 questions); Laya (T4 GPU) 33–40 ms (1,500–1,818 decisions/min; batched-10 throughput 7.2 ms/q, 8,333 decisions/min); LLM (claude-opus) 1.5–3.0 s (20–40 decisions/min, 15 sequential calls for the same 15-question batch). The Cost-Benefit analysis (§XI) is explicitly labelled non-measured: "The following profiles are analytical projections based on published API costs and assumed automation rates. They have not been validated by production measurement" (§XI-B) — its dollar figures (e.g., Jev $0.019 for ~300 calls, Laya $0.0000007/decision) are vendor list-price arithmetic, not observed spend, and are excluded from headline ledger rows.

## Calibration analysis

No calibration is measured by this paper on its own pentest data. §VIII-B/D report **secondary, vendor-published** figures with an explicit non-comparability caveat: "Published data from Laya [9] reports ECE of 0.081 (post-temperature scaling on their evaluation set); TypeSafe reports ECE of 0.246 for Jev on their own evaluation set [8]. These values were measured on different tasks and datasets and therefore cannot be directly compared as if they represented performance on the same benchmark" (§VIII-B). "Laya documents that its raw ECE is 0.466, reduced to 0.081 after temperature scaling on a validation set [9]" (§VIII-D, `post_hoc_calibration = temperature` for the Laya vendor figure only). §VIII-E is explicitly a **non-empirical illustration**: "we construct a purely hypothetical scenario. The numbers below are illustrative; they are not measured on Jev, Laya, or any real dataset" — excluded from the ledger.

## Cascade / escalation results

No cascade/escalation experiment is run. §XII discusses "Multi-Model Orchestration" (judge-curator separation, cascading decision chains) as proposed architecture, not a measured result.

## Option-name / robustness stress tests

The credential-dump BOLA case (§IX-E) is a single worked example showing System One severity output moving between "before" and "after" an evidence-pipeline fix: Run B initial (structured field empty) gave the Noul impact question p(impact)=0.3 and CVSS collapsed to Low (3.1); after a "salvage step" copied narrative evidence to the structured field, the data-type Score returned p(secrets)=0.94 and the CVSS calculator restored Critical (9.1) — a single-item illustration of sensitivity to evidence engineering, not a systematic robustness sweep.

## Code and data availability

NeuroSploit harness: "J. A. dos Santos, 'NeuroSploit: AI-powered autonomous penetration testing framework,' GitHub, 2026. [Online]. Available: https://github.com/JoasASantos/NeuroSploit" (reference list) — `code_available = yes (https://github.com/JoasASantos/NeuroSploit)`. No separate dataset release; NimbusCart (BenchMarkBurpAT) is referenced as the target application, not released by this paper.

## Paper's own stated limitations (§XV)

Four "benchmark limitations" (§XV-A): single target (NimbusCart, "one data point"), single-vote configuration, no Laya comparison on offensive-security tasks, and possible target memorization in training data. §XV-B/C discuss the "additive design principle" and adversarial robustness: a miscalibrated System One layer cannot introduce false positives (deterministic validators gate the pipeline) but can suppress true positives (false negatives) if it assigns low confidence to a real finding, which the paper calls a worse failure mode than running without the layer. §XV-D notes cross-domain transfer from general-purpose training to offensive security is only "suggested," not established, by a single run. §XV-F notes Jev's context window is unpublished and Laya's is 512–1024 tokens, a potential truncation risk for long evidence.

## Notes on seed claims

No seed claims were pre-registered for this paper (added to the sweep late, per the task brief); this extraction is a first pass, not a seed-check.
