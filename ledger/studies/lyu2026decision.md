# lyu2026decision

Decision-Oriented Recommendation Reranking: An Empirical Study of Its Promise and Limitations. arXiv 2609.40241; first version 2026-09-30, saved full text is v2 (12 Oct 2026). Extractor: batch V05. Ledger rows L1883 to L1896.

## Authors and affiliation
Hanjia Lyu (Singapore Management University), Yinglong Xia (Meta AI) (title block). Affiliation type: mixed (academic plus industry). No TypeSafe or OpenAI affiliation stated; no funding statement seen.

## Task and data
Second-stage recommendation reranking posed as a structured choice among K candidates. Amazon Reviews 2023, 5-core leave-last-out configurations, domains Movies and TV, Video Games, Books (Sec. 4.1, Table 1). SASRec trained per domain is the first-stage retriever; users are kept only if the held-out next item is in SASRec's top 200 (Eq. 5). Evaluated users: 954 (Movies and TV), 1,000 (Video Games, capped), 626 (Books) (Sec. 4.2). Candidate set = ground-truth item plus K-1 highly ranked SASRec non-targets, K in {20, 50, 100, 200}, deterministically shuffled so the order does not reveal the SASRec ranking (Sec. 3.2, 4.2). The 10 most recent interactions with title, category and the first 250 characters of the description form the text (Sec. 4.1). Methods are compared on the common set of users with successful inference in each setting (Sec. 4.2). Data are public and predate 2026; the authors note that differing training cutoffs may affect familiarity with items and that this cannot be disentangled (Sec. 6.2). A generalisation test uses LightGCN candidates at K=20 (Table 3, Appendix B.7).

## Decision models and versions
Jev through the TypeSafe hosted API, pinned `jev-1.13.0`, choice-type question with the 10 recent interactions as state, candidate probabilities used as ranking scores, no calibration or post-processing (Appendix B.6, Sec. 4.3). No access dates or run dates given. OpenAI Decisions with GPT-6-Luna (gpt-6-luna) through the Decisions API, same input, no snapshot date (Appendix B.5).

## Comparators and tuning-budget parity
SASRec (retriever ranking), DCNv2 (trained per domain), Qwen2.5 7B and 32B Instruct pointwise and listwise (logit-based, no generation), GPT-6-Sol and GPT-6-Luna listwise via generated permutation (reasoning effort none, temperature 0) (Sec. 4.3, Appendix B.4). Each LLM or system has its own prompt (Appendix A.1 to A.5); the paper does not describe any prompt tuning or selection on test users. SASRec and DCNv2 are trained on the domain data, Jev and Decisions are used zero-shot. The paper states that GPT listwise and Qwen listwise use different scoring procedures because GPT exposes only the top 20 log probabilities (Table 2 caption).

## Reference labels
Task outcome: the held-out next interaction in the Amazon Reviews 2023 leave-last-out split (Sec. 3.1, 4.1).

## Sampling and intervals
Fixed evaluation users (above); one run per setting except three repeated runs on identical candidate presentations to check inference stability (Sec. 5.2). Paired two-sided permutation tests with Holm-Bonferroni correction and unadjusted 95% paired bootstrap CIs for differences from GPT-6-Sol (Appendix C.2, Table 7); the main Table 2 reports point estimates without intervals. GPT-6-Sol significantly outperforms Jev in six of 12 settings after correction (Sec. 5.1, Appendix C.2).

## Headline results
GPT-6-Sol has the highest NDCG@10 in all 12 settings. Jev is second in 11 of 12, outperforms all Qwen variants and GPT-6-Luna in all settings, and outperforms Decisions in the primary evaluation (Sec. 5.1, Table 2). In Movies and TV, Jev at K=200 (0.077) falls below SASRec (0.096). With LightGCN candidates Decisions outperforms Jev in all three domains (Table 3). Order robustness (Movies and TV, three permutations): aggregate NDCG@10 differences non-significant, but at K=20 mean absolute NDCG@10 change is 0.138 for Jev and 0.176 for Decisions, Hit@10 flip rates 26.8% and 34.9%; only 13.9% (Jev) and 7.2% (Decisions) of informative users keep identical NDCG@10 across permutations (Table 4, Sec. 5.2).

## Calibration
No calibration analysis. Probabilities are used only for ranking (Sec. 3.4). Tie-aware robustness variants in Appendix Table 8.

## Cascade and escalation
None. The quality-latency Pareto comparison (Figure 1) places Jev on the frontier in many settings; no explicit escalation policy.

## Option-name, cardinality, language and robustness tests
Candidate count K = 20 to 200 (Sec. 5.1). Candidate order: three permutations per user (one original, two shuffled) on Movies and TV (Sec. 5.2); the authors state that the order change also modifies position-dependent candidate labels, so positional effects are not isolated (Sec. 6.2). English only.

## Cost and latency
Jev median per-user observed hosted-API latency 152 to 155 ms at K=20 and 198 to 293 ms at K=200 (across domains); Decisions 92 to 137 ms and 161 to 196 ms; GPT-6-Sol 1.27 to 1.55 s and 6.38 to 9.02 s (Sec. 5.3, Appendix Table 9). Jev and GPT figures include network time and provider processing and are not hardware-normalised against local models (A800-SXM4-80GB for SASRec, DCNv2, Qwen) (Sec. 4.5). No dollar costs.

## Code and data availability
Not stated in the text (no repository link found); prompts are in Appendix A and implementation details in Appendix B.

## Authors' stated limitations (Sec. 6.2)
Three Amazon domains from one source; controlled candidate sets always contain the ground truth, so end-to-end retrieval failure is not assessed; eligible user populations differ; knowledge-cutoff differences across models; two opaque decision implementations so differences cannot be attributed to decision-oriented specialisation; order experiments change candidate labels; latency is observed deployment latency, not hardware-normalised; reranking captures only one aspect of decision-oriented inference.
