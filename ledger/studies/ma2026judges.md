# ma2026judges — Judges Follow the Reference: The Derivation Gap in Verifying Tool-Call Arguments

- arXiv: 2610.18497v1 [cs.AI], 13 Oct 2026 (title page). Full text: fulltext/2610.18497.html and .txt (fetched 2026-10-28 from arxiv.org/html).
- Authors: Linhai Ma, Yan Wang, Lingfei Qian, Yupeng Cao (The Fin AI, USA, and Yale University, USA), Victor Gutierrez-Basulto (Cardiff University, UK). Affiliation type: academic (title page). No funding or competing-interest statement seen.
- Code: https://github.com/SarielMa/DeRef_release (abstract); "After review, we will release our code, the path labels, and the two controlled sets" (Artifact Use and Licensing).

## Task and data
Argument-level judging of tool calls: a judge sees context X and one proposed argument value and returns a probability that the value is correct (3.1). Five derivation paths (Visible, History-only, Format, Default, No-source) are assigned by text-matching rules (3.1, App. B). Three benchmarks (3.2): FC-RewardBench (FCRB, 630 single-turn requests, each with a correct and a wrong call made by a real model), ComplexFuncBench (CFB, 347 correct and 644 wrong calls, wrong calls from 30 models' trajectories), FinTrace (2,334 golden calls and 2,334 wrong calls made by changing one argument by rule). Two controlled sets: FCRB-Relocate (257 states) and FinTrace-HC (106 pairs). Main method DeRef: a separate Qwen3.8-27B deriver reads the full history without the candidate and writes a reference that is inserted into the judge input (4).

## Decision models and versions
Seven judges (3.2, App. F Table 11): Jev = "typesafe/jev-1.13-20260917 ... called through OpenRouter", no sampling parameters, reads up to 32,831 tokens (App. F). CLM = CLM-v0.1-8B (Kwok et al., 2026), checkpoint SHA-256 b2b4a8c9, vLLM 0.30.0, bf16, inputs truncated to 2,048 tokens. Five LLM judges: Qwen3-4B, Qwen3-8B, Qwen3.8-27B, Llama-3.1-8B-Instruct, Mistral-7B-Instruct-v0.3 (revisions given, thinking off, score = softmax over "Yes"/"No" first-token logits). No run dates for the Jev calls are given; dataset access date 2026-10-04 (reference list, AgentSuite). Main experiments use four judges: CLM, Jev, Qwen3-8B, Qwen3.8-27B (5.1).

## Comparators and tuning-budget parity
Same Plain input for every judge (3.2). Prior evidence methods ProvenanceGuard evidence, RevisEval (both Qwen3.8-27B, same settings as deriver, see the candidate), Self-generated reference (needs a text-writing judge, so Qwen only), Full history (5.1). "We train no model and search no hyperparameters" (App. F). The deriver is fixed and held across judges. Thresholds tau are set per judge, dataset and input so that 80% of correct arguments are accepted (3.3). Ablations (Tables 3, 4) are run only on CFB with Qwen3.8-27B.

## Reference labels
Gold calls from the benchmarks: FCRB labels "follow the official BFCL checker and are not independently audited"; CFB and FinTrace wrong labels are the authors' construction, and an audit of 100 items per dataset by two annotators could not confirm 3% and 4% of them (Limitations). No crowd workers (Ethical Considerations). Ledger label type: task_outcome for FCRB and CFB, synthetic for FinTrace wrong calls.

## n, sampling and intervals
All 95% CIs are bootstrap over 1,000 resamples of queries; a difference is significant when its CI excludes zero (3.2, App. C). Deriver re-sampled with two extra seeds, no significant seed effect (App. G). Seed 20260930 fixes all random steps (App. F).

## Test-set exposure
FCRB (Agarwal et al., 2025) and CFB (Zhong et al., 2025) are public benchmarks from 2025; FinTrace is cited as arXiv 2604.10015 (April 2026), also public. No contamination check reported for Jev. Ledger: public-pre-2026 for FCRB and CFB rows, unclear for FinTrace rows and the pooled cost row.

## Cost and latency
Jev: "325,637 billed calls for $23.01, and 47,514 more for variants that we do not report" (App. F Compute). Local models on one NVIDIA B200 GPU, 41.98 GPU hours for reported results. Table 13: CLM 8.7, 8.0, 8.0 ms per DeRef input (FCRB, CFB, FinTrace); Qwen3-8B 34.7 to 66.9 ms; Qwen3.8-27B 52.9 to 120.4 ms; the deriver needs 2.44 to 7.27 s per reference (shared by all candidates of an argument slot). Table 12 gives token counts.

## Main results
- Derivation gap (out-of-view minus in-view acceptance at the 80% threshold) is significant on CFB and FinTrace for all seven judges: Jev 22.67 and 27.78 points; on FCRB Jev 8.11 (Table 1). Jev's history-only gap on CFB is 59.39.
- Argument AUROC, Plain vs DeRef (Table 2): Jev 90.83/75.01/89.11 to 93.30/88.73/93.10 (FCRB/CFB/FinTrace); CLM 72.51/63.41/83.36 to 89.59/85.55/89.10; Qwen3.8-27B 91.95/78.92/89.31 to 93.39/95.09/92.25. RevisEval is the strongest prior method; DeRef is above it in 10 of 12 pairs, significantly in 8.
- FCRB-Relocate: burying the source drops AUROC to between 39.80 and 49.03 for all four judges; DeRef returns them to between 98.40 and 99.59 (3.4, 5.2). Figure values only partly labelled.
- Reference swap test (5.4): Jev acceptance of correct values falls by 3.00 points on FinTrace; AUROC falls on CFB and FCRB for all four judges (all 24 changes significant).

## Calibration, cascade, robustness
No calibration analysis (scores used via a per-judge threshold; AUROC only). No cascade. Robustness is the central topic (source relocation, reference swap, truncation window) but no option-name, cardinality or language test.

## Limitations (paper's own)
One gold value per argument; CFB/FinTrace wrong labels self-constructed (3% and 4% unconfirmed); FCRB labels not audited; DeRef does not shrink no-source gap on FinTrace for three of four judges; one deriver model only; no general-purpose frontier LLM judges tested (Limitations).
