# li2026cana

(key suffix a because studies/li2026can.md already exists)

arXiv 2610.34816v1 (cs.LG), 26 Oct 2026. "Can System-1-Style Decision Models Replace Dedicated Rerankers in RAG? A Systems Evaluation." Authors Qiaomu Li, Ying Xie, College of Computing and Software Engineering, Kennesaw State University, Marietta GA. Affiliation type: academic. (title block)

## Task and data
- Reranking a fixed Top-20 candidate list to a Top-5 in a RAG pipeline; decision-model policy versus dedicated reranker with retrieval held fixed. Broad screen: 21 open-weight models (nine rerankers, 12 decision models, 0.02B to 35B) on 11 benchmarks, 10,079 queries, 104 model-benchmark runs from earlier project stages with heterogeneous protocols (Table I, II).
- Controlled study on BRIGHT: 1,384 queries, 12 domains, official BM25 Top-20 lists frozen in original order; only 607 candidate sets hold a judged positive (777 score zero for every policy). Transfer checks: EnterpriseRAG-Bench (500 requests, 443 labelled) and MuSiQue (2,167), hybrid BM25+dense lists, FS@5; frozen confirmation on CQADupStack (BEIR test, 12 forums, 13,145 queries, 13,125 scored). (Sec. III-C, Tables II, VIII)
- Reference labels: benchmark relevance annotations (incomplete). All benchmarks public and pre-2026; no contamination check. (Sec. III-C, V)

## Decision models
- PPLX Decider (27B, open weights, Perplexity; official decision interface, calibrated probabilities, one score per candidate in one call), selected as the single model for the controlled study; "PPLX Decider v1.1 (revision 14c9d90)" is named for the earlier selection runs; the version used on BRIGHT is not stated. Screen also includes Laya, Amos 1 Small, Liquid d1-3B, Intern-Decision-4B, StartLux-Decision-4B, Drex-DLM, Kev-9B, Nimble-9B-v2, Clef-Flash, Winnow-12B, Drex-v2. Hosted Jev excluded (no isolable latency). (Sec. III-A, III-B)
- Comparator: Jina v3.5 (0.6B dedicated reranker) as incumbent, plus eight other rerankers in the screen. (Sec. III-B)

## Comparators and tuning parity
- Selection of PPLX and Jina was "outcome-informed" after exploratory runs; Winnow-12B with fallback scored higher on BRIGHT (0.2011 vs 0.1928) and was not carried forward without documented reason. Models differ 45-fold in size. Decision-model input handling (equal-prefix truncation, token budget sweep over six budgets, two-stage selection, BM25 fallback) was tuned on BRIGHT results; the quality margin delta=0.02 and rho=128 were set after first results; the sweep headline is exploratory. A tuned Jina (truncated to 8,192) is reported as a control; the screen runs used different input views and caps. (Sec. III-B, III-C, IV-C, V)
- Replacement criteria: reliability >=99% valid Top-5, quality non-inferior within 0.02 nDCG@5 (lower 95% bound), p95 latency <= 2x Jina. (Sec. III-C)

## Results
Default PPLX valid Top-5 on 44.1% of BRIGHT queries; completed-only +0.0371 nDCG@5 vs Jina, all-request -0.1031. Truncated 8,192: 0.1928 (99.7% valid) vs full-text Jina 0.1844. 4,096-token single call 0.1875, 99.2% valid; 6,144 0.1886. Two-stage PPLX 8,192: 0.2108. EnterpriseRAG FS@5: PPLX two-stage 0.6704 vs Jina two-stage 0.5688 (diff +0.102); MuSiQue 0.1823 vs 0.2026 (diff -0.020). CQADupStack forum-mean nDCG@5 diff vs full-text Jina +0.0092 at 4,096 tokens. Intervals: 40,000-draw bootstrap resampling 12 BRIGHT domains, exact sign-flip tests, Holm adjustment. (Tables III-VIII, Sec. IV)

## Cost and latency
Serial single-request latency on one NVIDIA A100-SXM4-80GB: Jina full text p95 1,211 ms; PPLX 4,096 tokens 1,101 ms (0.91x); 6,144 1,735 ms (1.43x); 8,192 2,397 ms (2.0x); two-stage 8,192 6,700 ms (5.9x); tuned Jina 245 ms (0.20x). Peak memory PPLX about 50 GiB vs Jina 4.3 GiB (1.9 GiB truncated). Some rows from 120-query cohort timed three times; earlier decision models timed on shared nodes. No batching or concurrency; no dollar cost. (Sec. III-C, IV-C, IV-D, Tables VI, VII)

## Calibration
Not evaluated.

## Cascade or escalation
Two-stage selection (two windows of 10, then 10 to 5) as a quality-for-latency trade; BM25 fallback on failure. No confidence cascade. (Sec. IV-B)

## Robustness
Candidate order (reversed and five shuffles): PPLX BM25-minus-shuffled +0.0131 nDCG@5, Top-5 changed for 97% of queries (Jina 78%); input budget sweep 1,024 to 8,192; workload transfer reverses the ranking (Enterprise vs MuSiQue); equal-prefix truncation harms Jina on Enterprise (-0.054). No option-name or language tests. (Sec. IV-B, IV-E)

## Code and data
No code or data availability statement found in the text; protocol SHA-256 hash recorded for the CQADupStack run. (Sec. III-C)

## Authors' limitations (Sec. V)
Heterogeneous screen protocols; one outcome-selected pair differing 45-fold in size; incomplete relevance judgments; transfer sets examined before; CQADupStack is duplicate-question retrieval with sparse labels and a single GPU with 2,000 queries for latency; no batched throughput or cost; thresholds illustrative; margin and fallback chosen after earlier results; budget settings chosen on one benchmark and only partly confirmed.
