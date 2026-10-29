# fernandes2026jevasajudge — Jev-as-a-Judge for Brazilian Portuguese Information Retrieval: Relevance Assessment and Reranking

arXiv:2610.23346v1 [cs.IR], 16 Oct 2026. HTML retrieved 2026-10-28 (fulltext/2610.23346.html, .txt). Coder: batch V16. Distinct from `li2026jevasajudge` (JEV-as-a-judge, accept or escalate).

## Authors and affiliation

Leandro Carísio Fernandes (Câmara dos Deputados, Brasília), Jayr Pereira (Universidade Federal do Cariri; Unicamp). Affiliation type: mixed (government legislature plus universities). Independent evaluation of a vendor model. Several of the authors built the collections used (NormasTCU, JurisTCU, Ulysses-RFCorpus), so they know the reference labels.

## Task and data

(1) Relevance assessment: Jev labels query-document pairs on four Brazilian Portuguese collections and the labels are compared with each collection's official qrels (Table 1): Quati test set (50 queries, 1,933 pairs, 4 levels, LLM-generated reference labels), JurisTCU (150 queries, 2,250 pairs, 4 levels, LLM-generated and reviewed by one domain expert), NormasTCU (46 queries, 812 pairs, 3 levels, up to four expert judgments), Ulysses-RFCorpus (692 queries, 8,205 pairs, 3 levels, one expert per pair) (§3.1). (2) System-ranking preservation: nDCG@10 and MRR for 15 NormasTCU systems and 16 Ulysses systems recomputed with Jev qrels and compared by Kendall tau (§3.1, Tables 2, 3, 8). (3) Reranking: Jev reorders the top 1,000 BM25 candidates for each of the 50 Quati test queries on the 1M-passage corpus (§3.2, Table 9).

## Decision model and version

"Jev version jev-1.13" for relevance assessment (§3.1 text); "Jev version jev-1.13.0" for reranking (§3.2). No run dates and no provider details. Assessment: one typed choice question per pair with the original collections' label wording. Reranking: probability that the document directly answers the query, 10 document-specific questions per request, 100 requests per query, no calibration and no fusion with BM25 score.

## Comparators and parity

Assessment has no comparator system; reference qrels are the standard. Human-human kappa from earlier work is quoted for context (pairwise 0.55 to 0.73 in NormasTCU; McDonnell et al. 0.34 to 0.85) with the caveat that protocols differ (§4.1). Reranking: BM25 from the same run, and a published BM25 + mT5-XL result (nDCG@10 0.6593, BM25 0.3991) reproduced from Bueno et al. (2024) with a different BM25 configuration; the authors state it is not a controlled comparison (§4.2). No tuning budget for Jev (zero-shot) is described; reranking depth, batch size and text limit are called "configurable experimental parameters" without selection details.

## Reference labels

Quati and JurisTCU: LLM-generated (JurisTCU reviewed by one expert); coded llm_teacher. NormasTCU: up to four expert judgments, aggregation unstated (coded human_adjudicated). Ulysses: single expert (human_single) (Table 1).

## n, sampling, intervals

n as in Table 1; all available pairs, not a sample. No confidence intervals, no bootstrap, no significance tests for assessment or reranking ("We report descriptive differences without claiming statistical significance", §4.2). Kendall tau on 15 and 16 systems.

## Test-set exposure

All collections are recent public releases (Quati 2024, JurisTCU 2026, NormasTCU, Ulysses); relationship to Jev training not discussed. Exposure coded public-pre-2026 with the caveat that some collection papers are dated 2026.

## Cost and latency

"We did not evaluate latency or monetary cost" (§4.2). Request structure only (100 requests per query).

## Calibration, cascade

None. Probabilities are used directly as rank scores. No cascade.

## Key results

Exact agreement 52.9 (Quati), 64.3 (JurisTCU), 54.8 (NormasTCU), 64.9 (Ulysses); kappa 0.68, 0.82, 0.52, 0.65; at least 94.5% of annotations match or differ by one level (§4.1). Kendall tau nDCG@10/MRR: NormasTCU 0.92/0.90, Ulysses 0.93/0.92 (Table 8); Quati and JurisTCU not ranked (no system runs). Reranking nDCG@10 0.3329 to 0.6331 (+90.2%), MRR 0.6852 to 0.9033 (+31.8%) (Table 9).

## Robustness

None beyond four collections and two domains; no order, option-name or prompt-variation tests. Reranking covers a single collection of web passages.

## Code and data

No code or data link in the text I read; collections are public.

## Own limitations

Reranking covers one collection and does not generalize to full-length legal documents; no latency or cost; no statistical tests; published mT5-XL comparison not controlled; kappa comparison with human studies limited by protocol differences; future work lists additional collections, paired significance tests, pointwise vs listwise, latency and cost, human-in-the-loop (§4.2, §5).
