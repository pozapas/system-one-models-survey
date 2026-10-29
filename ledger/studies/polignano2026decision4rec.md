# polignano2026decision4rec: Decision4Rec: A Jev-Inspired Framework of Decision Models on Knowledge and Active Graphs for Multi-Agent Recommender Systems

arXiv:2610.26035v1 [cs.AI], 19 Oct 2026 (HTML title block; fulltext/2610.26035.html and .txt). Extractor batch V18.

## Authors and affiliation
Marco Polignano, Pasquale Lops, Giovanni Semeraro (Università degli studi di Bari Aldo Moro); Het Darshan Mehta, Ernesto William De Luca (Otto-von-Guericke University Magdeburg; Leibniz Institute for Educational Media | Georg Eckert Institute) (title block). Affiliation type: academic. The paper states "Decision4Rec is not affiliated with TypeSafe" (§9.1). Code https://github.com/marcopoli/decision4rec; trained models https://huggingface.co/m-polignano (§6.4).

## Task and data
Sequential next-item recommendation framed as a typed choice among up to 30 candidates (Figure 2, §5). Datasets after 5-core filtering (Table 5): Amazon Video Games (94,745 users), Musical Instruments (57,432), Steam (99,571 sampled), all used as sources for training the decision model; Amazon Industrial and Scientific (50,985) and MovieLens-1M (6,040) held out (§6.1). Last item per user is the test target, the one before it is validation. Main results use "2,000 development test users per domain" (Table 7 caption), drawn once with a fixed seed; the plan is to confirm on 10,000 fresh users per domain, "with an analysis plan written before scoring them" (§6.3, §9.2), but those results are not in this version. NDCG@10 is computed over the whole catalogue (9,000 to 26,000 items); a target outside the 30 candidates counts as a miss (§6.3).

## Decision models evaluated
- Jev: "the hosted jev-1.13.0 (https://typesafe.ai/), pinned to one version", through the paid API, "as released" (§1, §8). It cannot be fine-tuned by users. Run dates are not given ("at the time of our runs"); no per-run timestamps. Answers saved but not redistributed.
- Kev (released open weights, same protocol): Kev-0.8B, Kev-4B, Kev-27B as released (jaredpalmer/kev-0.8b, kev-4b on Hugging Face, built on Qwen3.5 base; Kev-27B from jaredpalmer/kev-27b tag v1-lora) (§3, Table 15).
- Kev trained by the authors on real next-choice records from the three source domains (LoRA rank 16; 34,667 records for 0.8B and 4B; random 8,000 for 9B and 27B) (§3, §6.4, Table 7 caption). One training run per model; "two more seeds moved the fused NDCG@10 by up to 3%" for the 0.8B model (§9.1).
- Decision4Rec itself is a framework (knowledge graph statements + multi-agent pool + residual ranker + decision model + fusion).

## Comparators and tuning-budget parity
Baselines trained by the authors with 4 to 9 configurations each: GRU4Rec, SASRec, BERT4Rec, SASRecF (Table 6); training-free popularity, item kNN, sequential rules, content kNN; PrepRec (authors' code, trained on Video Games and Musical Instruments, transferred) (§6.2, §9.1). Every claim is against the best trained baseline of each domain. Jev and released Kev receive exactly the same requests as trained Kev (same users, candidates, statements, "found by" lines) (§8), so the Jev comparison is zero-shot versus trained Kev. The authors call "the fair comparisons" those with released Kev-4B and trained Kev-0.8B. Fusion weights are fitted on 1,000 validation users per domain. Design choices were made on the same development users that are reported (§6.3), which is a selection-on-test-users risk the paper acknowledges by reserving fresh users (not yet scored).

## Reference labels
Held-out true next interaction of each user (task outcome / logged behaviour), not a judged label.

## n and sampling
2,000 development test users per domain (Tables 7 to 15); paired randomization test (10,000 sign flips) and 95% bootstrap intervals over users (2,000 resamples); asterisk marks p<0.05 without correction; Holm correction promised for the confirmation over nine hypotheses (§6.3). "With 2,000 users per domain a difference below about 10% is often not significant" (§7).

## Test-set exposure
Public datasets from before 2026 (Amazon Reviews 2023, Steam, MovieLens-1M). The authors state "No dataset of this study can be assumed new for the language models we use". Controls: empty-history and no-title requests change scores by -7 to 0%; with the 4B model on MovieLens-1M removing titles costs 3% after fusion (§9.1). The global-timeline leakage caveat (split by last item per user) is stated (§9.1).

## Cost and latency
Table 14 (one request per user, 30 candidates, two orders): Kev-0.8B trained 157 to 167 ms per user on one RTX 3090 (24 GB), Kev-4B 565 ms, Jev paid API 310 to 340 ms; input tokens 3.9k to 4.4k (Kev) and 3.6k to 5.1k (Jev). Jev money per 1,000 users $0.15 to $0.22, input priced at $0.042 per million tokens; "this whole section cost $4.89" (§8; that is the authors' own spending, not coded as a result). 9B and 27B models run on one NVIDIA DGX Spark with 128 GB.

## Calibration
Table 13, trained Kev-0.8B only (not Jev): ECE of the first-choice probability, raw 0.019 / 0.015 / 0.015 / 0.031 (Video Games / Musical Instruments / Steam / Industrial); after temperature scaling on validation users 0.030 / 0.025 / 0.015 / 0.031 (fitted temperatures 0.95 to 1.20). Binning not stated. Computed only on users whose target is among the 30 candidates. NLL of the next item 3.07 to 3.20 versus 3.40 for a uniform guess, so probabilities "are calibrated but flat". Conformal sets at 90% target coverage give 0.917 to 0.957 coverage with sizes 23.0 to 25.3 of 30. No calibration analysis for Jev itself in this paper.

## Cascade or escalation
None. Fusion of the decision-model score with the ranker score is not a confidence cascade.

## Option-name, cardinality, language, robustness
Candidate order: deviation from a Luce model between the two orders of a request 0.0010 to 0.0015; largest position effect -0.11 to -0.05 log probability (Table 13). Jev determinism: the same 1,200 requests sent a few hours later gave only 0.3 to 0.7% identical answers and the first choice changed in 7% of requests (§8). Raw counts versus scale words in statements: no significant loss (§4.2). 50 versus 30 candidates: no lasting change (§9.1).

## Code and data
Code, configurations, trained models and dataset rebuild scripts released; Jev answers are not redistributed (Jev terms) (§6.4).

## Authors' own limitations (§9.1)
Overlap of the decision model with the ranker; dense domains show no significant gain; ceiling of two-stage reranking (target among 30 candidates for 9 to 25% of users); last-item split can leak future interactions; baselines are the authors' own implementations; few domains, one training run per model; contamination cannot be fully excluded; Jev cannot be trained, is not repeatable, and its version can change. Fresh-user confirmation and further experiments are "running or prepared" (§9.2).

## Notes for the grader
Absolute NDCG@10 values are small (0.02 to 0.19). The headline "25 to 36% above the best trained baseline" is Decision4Rec-Full with Kev-4B on Video Games and Musical Instruments; the residual ranker alone is already +17% and +26% above SASRecF, so most of the gain comes from the pool, not the decision model. "A trained 0.8B open model beats the released Jev in eleven of fifteen settings and is never worse" is a comparison of a model trained on the authors' recommendation data with a zero-shot hosted model.
