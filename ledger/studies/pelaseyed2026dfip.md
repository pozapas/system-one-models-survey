# pelaseyed2026dfip — DFIP: Decision-Focused Inference Path for System One Models

arXiv:2610.36804v1 [cs.PF], 27 Oct 2026 (document dated October 19, 2026). Full text: fulltext/2610.36804.html and .txt. Systems study of execution speed and answer fidelity; it states it does not compare task quality, train, quantize or distill (Sec 2).

## Authors and affiliation
Ismail Pelaseyed, Alan Zabihi; Superagent Technologies Inc. (title block). Affiliation type: industry.

## Task and data
Latency of typed decision-model requests (CUDA-graph replay, candidate-token projection, schema-compatible length-aware batching) against native inference. Resident workloads: nine request types (short Boolean and categorical, three questions on one state, medium and long contexts, candidate widths 2/8/16, batch of 8); 50 timed calls per mode after 4 warmup calls (Sec 4.2). Answer audits on 3,024 decisions from LocalLLaMA/typed-decisions (400 cases, 2,000 questions, used during development) and BANKING77-derived records (512 records, 1,024 decisions from 256 test utterances) (Sec 4.3). External arrivals at 5, 15, 30 requests/s for 60 s from a workstation in Sweden (Sec 4.4). GLiNER: 96-record traces (Sec 4.2).

## Decision models evaluated
Four pinned checkpoints (Appendix B): Liquid d1-3B 051bcc46..., Clef-Flash 8b2e5fd1..., PPLX-Decider 6195aa55..., GLiNER2.5-Decide 9d1bfb84... (full 40-character revisions in the paper); analysis commit f2eef1746e5e39b92827759344d4ef47410fc464. Hosted Jev is not evaluated. Models were selected after exploratory development (Sec 2).

## Comparators and tuning parity
"Strengthened" native inference with optional native Qwen kernels (causal-conv1d 1.7.0, fla-core 0.5.2) for Clef and Decider; Liquid's released torch.compile reduce-overhead setting; GLiNER eager and compiled native FIFO batching (Sec 4.1). The DFIP side is authors' engineering; native sides are released engines, strengthened by the authors; compiled GLiNER follow-up is post hoc. Fresh containers need not be independent hosts; images differ between baseline and fallback runs (Sec 4.1).

## Reference labels
None. Fidelity is agreement with native outputs, not accuracy against labels; the paper says the audit does not evaluate task accuracy, calibration quality or downstream utility (Sec 5.1).

## n and intervals
Statistical unit is the container round (5 planned for Decider and Clef, 4 retained for Clef; 3 for Liquid); geometric-mean ratio of paired medians with 95% percentile bootstrap (10,000 resamples) over paired log ratios; failed rounds retained without imputation (Sec 4.2). GLiNER: one worker, five paired timings, no interval. Serving: three planned application rounds per model, one Decider attempt fails with illegal memory access.

## Test-data exposure
Not applicable to latency. Audit corpora (typed-decisions, BANKING77) are public pre-2026; training overlap unknown (Sec 4.3).

## Cost and latency
Resident latency: Decider 74.54 ms native to 30.14 ms DFIP; Clef 51.69 ms to 35.68 ms (Table 2). Hardware: NVIDIA B200 for PPLX-Decider, NVIDIA L40S for the others; GPU latency excludes transport and startup. No monetary cost.

## Calibration
No calibration analysis. Probability and confidence drift audited: Liquid compiler maximum probability drift 0.0220 versus DFIP 7.67e-5; Clef literal score drift 0.0188, confidence drift 0.0129 (Sec 5, Table 6); 21 of 2,473 matched serving pairs cross confidence 0.9.

## Cascade or escalation
None. Native fallback is used for unsupported paths and is not counted as a speed contribution (Sec 1).

## Option-name, cardinality, robustness tests
Candidate widths 2, 8, 16 in the workload set; Figure 1 shows paired speedup across nine workloads (values only in the figure). Diverse arrivals reverse the replay gains (Decider replay loses 23.0% at 5 requests/s with p95 49.41 s). No option-order, option-name or language test.

## Code and data availability
Public repository https://github.com/superagent-ai/dfip, frozen analysis revision, raw timing records and failed attempts retained; reproduction needs a Modal workspace (Appendix A).

## Authors' limitations (Sec 9)
Finite samples, single-worker GLiNER pilots, post hoc follow-ups, container attrition and GPU errors, partially uncontrolled cloud environments and historical dependencies; results are workload-specific and not evidence of production readiness or a universal optimizer.
