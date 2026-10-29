# liu2026multimodal: Multimodal Reranking Is a System One Decision

arXiv:2610.28435v1 [cs.IR], 20 Oct 2026 (fulltext/2610.28435.html and .txt; the HTML omits the author block and abstract, so authors, affiliation and code link were read from the PDF first page, fulltext/2610.28435.pdf, and the arXiv abstract page, fulltext/2610.28435.abs.html). Extractor batch V18. The first author's key shares surname and year with liu2026timesjev and liu2026adversarial (different papers).

## Authors and affiliation
Zhuchenyang Liu, Yao Zhang, Yu Xiao, Aalto University (PDF page 1). Affiliation type: academic. Code: github.com/Rynehails/rerank-as-decision (PDF page 1; "We release the code", §1).

## Task and data
Position paper with experiments: multimodal reranking posed as one typed "choice" decision over the top K=16 candidates of a first-stage retriever (Qwen3-VL-Embedding-2B, revision 9f2f7e7), candidates labelled A to P, probabilities read from label-token logits in one forward pass (§3, Figure 1). Benchmarks: MMEB-V2 image retrieval (12 tasks, hit@1), MMEB-V2 visual-document retrieval (24 tasks, nDCG@5), ViDoRe V3 (8 datasets, six languages pooled within dataset, nDCG@10); MMEB-V2 video tasks left out because JEV-27B-VL takes no video (§4). Per-query counts are not given in the main text. Latency uses 100 English ViDoRe V3 queries from two domains (Table 4).

## Decision models evaluated
- JEV-27B-VL (AutoTrust, Hugging Face autotrust/JEV-27B-VL): Qwen3.8-27B with a LoRA adapter and a decision head trained on text decisions only; model revision fee8c1d, served with vLLM 0.30.0 on one NVIDIA H200 (Appendix B). "No image enters the training, so every image decision JEV-27B-VL makes, ours included, is zero-shot for the decision head" (§3.4). Run dates not stated.
- Qwen3.8-27B as released, thinking disabled, read through label logits ("no decision tuning"), a Jev-style readout with no trained head (§3.4).
- Gemma 4 E2B, E4B, 12B, 26B-A4B, 31B read with the same choice readout (§7.1).
- Hosted Jev is not run; it is cited as the System One exemplar.
- Dedicated references: Qwen3-VL-Reranker-2B (revision 4bd860a) and -8B (b212dc8), released code at commit 393e297, bf16, pointwise yes/no (Appendix B).

## Comparators and tuning-budget parity
All rerankers receive the same top-16 candidates and an image budget of at most 1,800 visual tokens (Gemma 4 uses 280 by default, a disclosed difference). The authors flag the confound: the zero-shot 27B model is larger than the supervised 2B and 8B rerankers and of a newer generation, so the comparison "changes supervision together with scale and generation" (§9 AV1). The controlled pair (Qwen3.8-27B vs JEV-27B-VL) shares every weight except the adapter and head (§3.4). No prompt tuning against test data is described; prompts are fixed (Appendix A).

## Reference labels
Benchmark relevance annotations of MMEB-V2 and ViDoRe V3 (produced by the benchmark authors; not described in this paper). Coded administrative_field.

## n and sampling
Means over 12, 24 and 8 tasks or datasets, no per-query intervals. Sign tests over tasks for the decision-tuning difference: p=0.017 (MMEB-V2 visual documents, 17 of 24 tasks higher, two ties) and p=0.008 (ViDoRe V3, all 8 datasets) (§6.2). Single run per configuration.

## Test-set exposure
Public benchmarks (MMEB-V2, ViDoRe V3), pre-2026; no contamination check reported.

## Cost and latency
Table 4: one NVIDIA H200, concurrency 1, same top-16 ViDoRe V3 pages, 100 English queries, seconds per query: Qwen3-VL-Reranker-2B 2.75 (16 calls), -8B 3.67 (16 calls), Qwen3.8-27B choice 3.97 (1 call, 28.8k input tokens), JEV-27B-VL choice 4.48 (1 call, 28.9k), Gemma 4 E2B 0.47, E4B 0.49, 12B 0.55, 26B-A4B 0.78, 31B 1.27 (about 4.4k tokens). With batched pair scoring Reranker-2B and -8B take 1.68 and 2.61 s, so the choice pass takes 1.5 times as long as Reranker-8B (§7.2).

## Calibration
None reported; the authors list measuring calibration of the choice probabilities as future work (§10).

## Cascade or escalation
None.

## Option-name, cardinality, language, robustness
Choice (one question over 16 candidates) vs yes/no (16 questions) on MMEB-V2 image retrieval: Qwen3.8-27B 76.76 vs 69.50, JEV-27B-VL 76.80 vs 71.42, first stage 74.85 (Table 2). The choice loses on three image-only-query tasks (MSCOCO image-to-text -4.1, VisualNews image-to-text -1.7, NIGHTS -0.7; JEV-27B-VL loses on the same three) (§8.1). Candidates are presented in first-stage order only; order dependence is untested and labelled a limit (§9 AV5, §10). Maximum 16 candidates (labels A to P). Model size: Gemma 4 E2B and E4B lower the first stage on all three benchmarks (§7.1). Six languages pooled in ViDoRe V3.

## Code and data
Code released (PDF page 1); public benchmarks and open weights.

## Authors' own limitations (§9, §11)
Confounded comparison (size, generation, supervision); fits only sufficiently large VLMs; 27B model more expensive than 8B reranker; limited to 16 candidates; position-order sensitivity and calibration not tested.

## Notes for the grader
The paper frames itself as a position paper and is explicit that findings are "encouraging but confounded". The headline decision-tuning gain is 0.04 hit@1 on images (tie), 0.63 nDCG@5 and 1.09 nDCG@10 on pages.
