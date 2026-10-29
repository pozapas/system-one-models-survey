# Zheng and Chen 2026, Selective Reasoning for Typed Decision Models: When to Start, Read, and Stop

arXiv:2610.19644v1 [cs.CL], 14 Oct 2026. The HTML version returned 404, so the full text is the PDF (fulltext/2610.19644.pdf) converted with pdftotext (fulltext/2610.19644.txt). Glyphs such as tau are lost in the text conversion.

## Authors and affiliations

Bin Zheng (equal contribution) and Zheng Chen, University of Electronic Science and Technology of China (page 1). Affiliation type: academic.

## Task and data

768 questions, 256 each from ProofWriter (open-world logical judgments), LogiQA 2.0 and ARC-Challenge (Section 4.1). ProofWriter and LogiQA contribute one question per reserved official-training material group, disjoint from fitting and development; ARC uses an official-test subset with development overlap excluded (Section 4.1). Labels are the benchmark answer keys. All three benchmarks predate 2026 (Tafjord 2021, Liu 2023, Clark 2018); material-group splitting is the only separation, no contamination check for the Qwen3.5-4B backbone. Fitting uses 1,024 training and 256 development questions (Section 4.1). Follow-up policy revisions reuse the observed questions and the paper says a revised controller requires fresh data (Limitations). The study is a controller-design paper; the typed reader is the authors' own construction, so the "model" is not an externally released version.

## Decision model

Shared candidate-answer reader: bias-free linear head (10,240 parameters, 4x2560) on the answer-cue state of a frozen Qwen3.5-4B backbone, producing candidate probabilities from empty or partial reasoning prefixes (Section 3.1, Eq. 1). Controller: benefit gate (logistic correction-minus-regression estimate), natural-state read trigger, entropy-certainty acceptance with thresholds 0.70, 0.85, 0.95 fixed before evaluation (Sections 3.2 to 3.4, 4.1). Kev (Palmer 2026, source commit 0fe8fc9, accessed 2026-10-11) is evaluated in a routing study only (Appendix, Table 19). No Jev.

## Comparators and tuning parity

Eight shared-reader configurations with identical backbone and reader (direct read; terminal read at 512, 1,024, 2,048 tokens; simple controller; three thresholds) plus generated-answer baselines: forced terminal answer, Answer Consistency (k = 10), Qwen-adapted DEER at 1,024 and 2,048 tokens, native 8,192-token generation (Section 4.2). Gate and trigger are trained on the authors' fitting data; DEER trial thresholds and read intervals for the simple controller are selected on 48 development questions disjoint from evaluation (Section 4.2). The authors' controller is therefore tuned for the setting and the baselines receive adapted rather than native tuning, a disclosed asymmetry.

## Headline results

Table 1: direct read 70.96, terminal 512 77.08, terminal 1,024 85.55, terminal 2,048 87.11, forced terminal 84.64, DEER 1,024 85.29, DEER 2,048 87.63, native answer 74.74, Ours 84.38 average accuracy; mean pipeline time 0.080, 4.773, 9.410, 17.414, 9.446, 9.582, 18.500, 38.213, 5.053 s. Paired contrasts with 95% bootstrap intervals (Table 11): Ours vs direct +13.41 pp (10.42 to 16.28), vs terminal-512 +7.29 pp (4.69 to 9.90), vs terminal-1,024 -1.17 pp (-2.60 to 0.26), time saved 46.30% (43.84 to 48.79); acceptance and cancellation save 34.09% (31.88 to 36.28) with 654 vs 652 correct. Learned reads make 42.75% fewer queries but no latency advantage (Section 5.3). Kev routing study: direct Kev 311/512, reasoning then Kev 461/512, hidden benefit gate 455 with 28.3% fewer calls (Table 19).

## Calibration

None reported as ECE or Brier. Entropy certainty is used as an acceptance signal and the paper states "its threshold does not specify a probability of correctness" (Section 3.4). Gate calibration uses Brier score to select regularisation (Appendix A).

## Cascade and escalation

The core contribution: direct decision, then reasoning on demand, then early acceptance of an intermediate read; quality-cost trade given above (Section 5, Tables 1, 2, 11).

## Option-name, cardinality, language, robustness

Candidate order preserved; K up to 4 uses the linear head, more candidates use native logits (Section 3.1). No robustness test of option names or order. ARC is a transfer test from ProofWriter and LogiQA fitting.

## Cost and latency

Single NVIDIA A100 80GB, BF16 vLLM, greedy decoding, disabled cross-request prefix caching; pipeline time per question; timing subset of 48 questions with repeated executions (Sections 4.3, Table 7). Energy and throughput unmeasured (Limitations).

## Code and data availability

https://github.com/binzheng-joey/selective-reasoning with code, reader weights, control parameters, evaluation manifests and per-question measurements (Appendix).

## Paper's own limitations

One frozen Qwen3.5-4B backbone; fitting on ProofWriter and LogiQA with ARC as transfer; entropy certainty measures concentration only; single-question latency, no energy or throughput; greedy runs can diverge so comparisons use local paired executions; follow-up policies reuse observed questions (Limitations).
