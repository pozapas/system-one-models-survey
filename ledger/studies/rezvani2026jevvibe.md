# Rezvani, Behrouzi & Sadeghi (2026), "JevVibe: Efficient Classification-Guided Secure Code Generation"

Coder: batch V04. Full text: fulltext/2609.34963.html and .txt (arXiv HTML v1).

## Identification
- arXiv 2609.34963v1 [cs.CR], 28 Sep 2026 (header).
- Authors: Arshak Rezvani, Sasha Behrouzi, Ahmad-Reza Sadeghi, Technical University of Darmstadt, Germany (author block). Affiliation type: academic.

## Task and data
- 50-way CWE classification of code snippets, then a diagnosis-guided repair agent (Abstract; Section III).
- Data: CyberSecEval Instruct subset (instruct.json), 1,916 tasks, 50 distinct CWE identifiers; input is the `origin_code` field, label is the `cwe_identifier` field, called the "benchmark label" and explicitly not a manually verified label (Section III-A1). Label type coded administrative_field.
- Test exposure: CyberSecEval was released by Meta in 2023 (reference [1], arXiv 2312.04724); no contamination check reported. Coded public-pre-2026.

## Decision model
- Jev, "At the time of writing, we use Jev-1.13.0" (Section II-B). No run dates beyond "accessed 2026" in the reference list.
- Typed Choice question over a fixed 50-candidate catalog, same CWE names and descriptions as given to the baselines (Section III-A3). Responses missing the choice or probability map count as inference failures. Jev returned valid output for all 1,916 examples (Section IV-A).

## Comparators and tuning parity
- Six open-weight instruction-tuned models (Qwen2.5-Coder-7B/32B, DeepSeek-Coder-6.7B/33B, Llama-3.1-8B, CodeLlama-34B) via vLLM, plus GPT-5.6-Sol via the OpenAI API (Section III-A2). Temperature 0, top-p 1, seed 42.
- Each autoregressive model receives the source code and the full 50-class catalog and must return a ranked top-5 JSON list; a regex fallback parses malformed output. No prompt tuning, few-shot examples or fine-tuning described; no tuning on test data described. Autoregressive models yield no probability distribution, so no proper scoring rules or calibration are reported (Section III-A2). A softmax over per-candidate log-likelihoods was tried only in preliminary experiments and judged too costly (Section VI).

## Results
- Table I (n = 1,916): Jev top-1 0.458, top-3 0.766, top-5 0.836, macro-F1 0.269, MRR 0.624, coverage 1.0000. GPT-5.6-Sol 0.495 / 0.757 / 0.814 / 0.360 / 0.628 / 0.9995. Best open-weight (Qwen2.5-Coder-32B) top-1 0.335. Coverage of open models ranges 0.7114 to 1.0000 (Section IV-A).
- Table II: estimated API cost USD 0.283 (Jev) vs 15.83 (GPT-5.6-Sol), 55.9x; median latency 0.244 s vs 1.531 s, 6.27x; p95 0.292 s vs 3.737 s, 12.8x. Cost and latency are end-to-end API figures at the provider pricing in effect; provider hardware not stated (Section IV-A).
- Repair agent (Section IV-B, Figure 5): security pass rate 0.635 baseline, 0.661 LLM-guided, 0.707 Jev-guided, scored by CyberSecEval's official Insecure Code Detector on the same 1,916 tasks. Of 700 baseline-vulnerable samples, Jev-guided fixes 228 (32.6%) and LLM-guided 129 (18.4%); regressions 89 vs 79. Same repair model and prompt in both arms.
- Note: the "LLM-guided" arm uses Qwen2.5-Coder-32B-Instruct's own diagnosis, not GPT-5.6-Sol's.

## Sampling design and intervals
- Single pass over all 1,916 items, one run per model. No confidence intervals, bootstrap or significance tests reported for any quantity. Per-class and per-language breakdowns are in Figure 4 (figure only, values not labelled).

## Calibration and cascade
- No calibration analysis of Jev. The paper states "our experiments do not establish whether its reported confidence consistently corresponds to empirical correctness" (Section VI). No escalation or cascade analysis.

## Robustness
- Programming-language subsets are descriptive only. No option-order, option-name, cardinality or language-of-prompt tests.

## Code and data
- No repository or data release statement found in the full text. Dataset is the public CyberSecEval file.

## Authors' stated limitations (Section VII)
- One repair backbone and top-1 diagnosis only; single benchmark and a single external detector, both imperfect proxies for verified ground truth; Jev is a commercial system documented only by its vendor; cost and latency reflect one provider's pricing at one time.

## Coder notes
- The abstract's "6.27x lower median API latency and 55.9x lower estimated API cost" are ratios against GPT-5.6-Sol.
- Jev is above GPT-5.6-Sol on top-3 and top-5 and 0.004 below on MRR; GPT-5.6-Sol wins top-1 and macro-F1. Rows keep both directions.
