# Wang and Gao (2026), "JEV as a Judge for Agent Trace Security: An Empirical Comparison with Generative LLM Judges"

## Identification
- arXiv 2609.34862v1 [cs.CR], 28 Sep 2026 (header); byline date "September 2026". License arXiv perpetual non-exclusive.
- Authors: Zhiqiang Wang, Yichao Gao; "University of Science and Technology of China" (byline, ustc.edu.cn emails). affiliation_type = academic.
- Code: none released; the Data Availability section points to the public benchmarks and says the appendices give "the scoring rubric, pricing assumptions, sample counts, and supplementary analyses" (Data Availability). code_available = no.
- Another study in the ledger uses the key `li2026jevasajudge` (a different paper); this key is `wang2026jev`.

## Task and data
- Retrospective trace-level security classification of agent trajectories: every judge assigns a risk score s in {1,...,5} on a shared rubric and the binary prediction is s >= 3 (Eq. 1, Section 3.1, Appendix A). Positive class = unsafe or unauthorized behavior.
- Four collections, 5,219 trajectories (Section 4.1, Table 1): R-Judge 564 (298 positive), ATBench500 500 (250), a TraceSafe subset 540 (270), MCPHunt 3,615 (797). "R-Judge and ATBench500 retain their benchmark labels; TraceSafe and MCPHunt use the study's revised labels, which distinguish resisted injections and signal-only cases from unsafe behavior" (Section 4.1). The paper does not describe who revised the labels or how; ledger codes the labels as administrative_field (benchmark-supplied, partly revised by the study); the limitations say future studies "could use independently reviewed labels" (Section 6). Benchmark-level rows therefore carry mixed label provenance.
- Exposure: public benchmarks (R-Judge, ATBench, TraceSafe, MCPHunt) all cited as released before the study; no contamination check; coded public-pre-2026.

## Models and comparators
- JEV: four typed questions in one request (overall risk score, authorization, intrinsic safety, severity), returns bounded answers with probabilities; the overall risk score decides the prediction (Section 3.2). Version identifier not reported (no jev-x.y string); pricing USD 0.042 per million input tokens, 0 for output (Appendix C). Run dates and API route not stated.
- Generative judges: GLM-5.2-Tencent, DeepSeek-V4-Flash, DeepSeek-V4-Pro-Seed, Qwen3-Next-80B, returning the same assessment fields plus a rationale and evidence; Chinese explanations in the human-review contract (Section 3.2, Appendix A). Inference settings, temperatures and exact revisions are not given in the text read (Section 4.2 lists only names).
- Tuning parity: shared trace rendering and risk anchors, same threshold; "differ in detailed instructions, output requirements, and serving conditions" (Section 6); the LLM prompt adds detailed counterevidence and action-stage rules, while JEV gets score instructions (Appendix A). Disclosed, bounded asymmetry. Whether prompts were selected using the benchmark labels is not stated. The threshold s >= 3 is common and fixed; per-judge thresholding sensitivity is reported only in appendices not extracted.

## Statistics
- Positive-class precision, recall, F1 and accuracy on valid judgments; overall F1 is the unweighted mean of the four benchmark F1 scores; coverage pooled over 5,219 trajectories; correct-decision yield counts missing outputs as errors (Section 4.3, Tables 2 and 3). Because each judge's metrics use its own valid responses, comparisons depend on missingness; a common-valid-sample comparison with exploratory paired bootstrap (2,000 replicates within each benchmark, equal benchmark weights) gives JEV 76.8 versus GLM 74.1 F1, difference +2.7, 95 percent interval [0.5, 4.8] (Appendix B, Section 5.1). No intervals on the headline F1 values in Tables 2 and 3.
- No calibration analysis (probabilities not evaluated): calibration_quantity none; post_hoc_calibration none.

## Cost and latency
- Latency measures successful single-call evaluations only; costs estimated from recorded token usage and fixed configured prices (Section 4.4, Appendix C). Table 4 (pooled, four benchmarks): JEV timed n 4,921, median 0.99 s, mean 1.18 s, p95 2.02 s, 4,644 input and 128 output tokens, USD 0.000195 per valid result; GLM-5.2 median 33.29 s, mean 37.34 s, USD 0.014887; "ratio of means is approximately 8.1-31.7, including 31.6 against GLM" (Section 5.3). Hardware or provider locations not stated; latencies include whatever serving route each configuration used.

## Cascade, robustness
- The discussion proposes, but does not test, "a screening-and-escalation pipeline" (Section 6). Trace-length analysis: JEV F1 85.2, 67.4, 57.5 at 5-8, 9-16 and >16 steps versus GLM 78.5, 58.4, 50.6; token bins and common-sample checks in Appendix E (Section 5.4). Excluding MCPHunt changes rankings in long bins (Table 11 caption). No option-name or order test; score scale is 5-level.

## Authors' stated limitations (Section 6)
- Judge configurations share trace content and risk anchors but differ in detailed instructions, output requirements and serving conditions; resource measurements cover successful calls and estimated token charges; revised labels, missing outputs and benchmark composition influence metrics; length analysis describes the observed workload; independently reviewed labels and controlled trace-length variation are future work.
