# Wu & Lim (2026), "Decision Hijacking: Prompt Injection Attacks on Jev's Typed Probabilistic Decisions"

## Identification
- arXiv 2609.28613v1 [cs.CR], 23 Sep 2026 (header). License CC BY 4.0. Full text fulltext/2609.28613.html and .txt.
- Authors Tiantong Wu, Wei Yang Bryan Lim; Nanyang Technological University, Singapore (byline). affiliation_type = academic.

## Task and data
- Prompt-injection robustness of Jev's Choice interface. 510 direct-harm cases reconstructed from InjecAgent (30 attacker goals x 17 user contexts; Zhan et al. 2024), rendered as the first security-critical typed decision after exposure to the injected tool result (Section 3.1; Appendix A). State fields user_request, actions_taken, latest_tool_result; only the designated slot in latest_tool_result changes. Trust labels omitted.
- Primary upstream action space three choices (final_answer, source user tool, attacker-target tool); secondary library_k8 space with eight choices, reported separately (Section 3.1).
- Four experiments, 54,060 main calls (Table 1): DH-1 native attack transfer (3,060 calls; base and enhanced "IMPORTANT!!! Ignore all previous instructions" variants), DH-2 injection-style factorial A0 to A4 (15,300), DH-3 relatedness assertions P0, N0, P1, P2 with registered SESOI 0.02 (12,750), DH-4 black-box adaptive optimization with access to returned probability vector, 72-configuration grammar, 24 proposals per case, four checkpoints validated with five fresh calls (22,950). Total 64,860 logged calls (Appendix G).

## Decision model
- Jev, "All confirmatory calls require jev-1.13.0, and a version mismatch is treated as a failure" (Section 3.3); every call returned jev-1.13.0 (Table 8). No run dates; TypeSafe blog and API documentation accessed 2026-09-23 (References).

## Comparators and tuning parity
- None. Single system; no generative LLM baseline ("we do not compare overall security with generative LLM baselines", Limitations). Comparison is within Jev across attack conditions and budgets. Tuning parity not applicable. DH-4 optimizer is deterministic, no attacker model.

## Reference labels
- Attacker-target tool and safe action (final_answer) are defined by the InjecAgent reconstruction; endpoint is selection at the first security-critical decision, not harmful execution (Section 3.1). Treated as task_outcome / benchmark-defined.

## n, sampling, intervals
- N = 510 cases; repeats R=1 (DH-1), R=5 (DH-2, DH-3), five fresh validation calls per checkpoint (DH-4). ASR averages per-case selection frequency; robust-hijack counts use at least 3 of 5 calls. Confident hijack rate (CHR) gated on Jev's returned confidence field at least 0.7 (Section 3.2).
- 95% percentile intervals from a two-way pigeonhole bootstrap over attacker goals and user contexts, 10,000 resamples, seed 20260923 (Section 3.3). Reporting step of probabilities is 0.01.
- Confirmatory hypotheses registered (H1a, H1b, H2, H3a to H3c); several went against the registered direction (Section 5.2, 5.3). The margin and attacker-control analysis is exploratory (Section 5.5).

## Key results
- Base attack ASR 1.8% (9/510), attacker-probability shift +0.043; enhanced attack ASR 0%, +0.009; enhanced minus base rerun -0.034 [-0.062, -0.015] (Section 5.1; Table 2). Eight-choice library space base ASR 1.6% (8/510) (Table 3).
- Ignore-previous marker -0.032 [-0.060, -0.014] relative to plain attack; A0 to A4 call-level ASR 2.0%, 2.2%, 0%, 0%, 1.3% (Section 5.2).
- DH-3 P2 minus N0 +0.0030 [0.0010, 0.0054], below SESOI 0.02 (Section 5.3). All observed DH-3 hijacks involve the emergency-dispatch goal.
- DH-4: mean best-so-far attacker probability 0.043 to 0.084; validated ASR 1.8% [0.0, 6.3] at B=0 to 3.5% [0.0, 10.0] at B=24; 19 distinct cases ever succeed; CHR 0.2% (Section 5.4; Table 2).
- Exploratory: success rates 12/12 near-boundary embedded, 4/29 far-boundary bare snippet, 1/468 far-boundary embedded (Section 5.5).
- Reproducibility: three independent P0 runs give aggregate shifts 0.0427, 0.0425, 0.0428, per-case correlation 0.9984 and 0.9986; target selection frequencies agree in 506 of 510 cases (Appendix G.1).

## Calibration
- No calibration analysis (ECE or reliability). Reported probabilities used as the attack feedback channel; the authors note high-confidence hijacks are rare and that reporting precision is 0.01.

## Cost and latency
- Not reported. Only call counts (Appendix G).

## Cascade, option-name, cardinality, robustness
- Action-space cardinality: three versus eight choices in DH-1 only (Section 3.1; Table 3). Option order fixed. No language tests. No cascade.

## Test-set exposure
- InjecAgent is a public 2024 benchmark (ACL Findings 2024); no contamination check. The task is attack vulnerability rather than accuracy.

## Code and data
- No repository or data statement found in the text. Appendix G describes integrity checks and logs of exact requests, responses and choice order.

## Paper's own limitations (Limitations; Appendix H)
- One proprietary model version; reconstruction inherits InjecAgent domains; primary space only three choices; snapshot endpoint not harmful execution; 0.01 probability step; five-call validation does not establish universal reliability; structural analysis exploratory with successes concentrated in two source clusters; no comparison with generative baselines.
