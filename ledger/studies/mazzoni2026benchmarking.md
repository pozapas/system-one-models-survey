# mazzoni2026benchmarking

arXiv 2610.07953 (v1, 06 Oct 2026). "Benchmarking System One Models in Online Moderation". Full text: fulltext/2610.07953.html and .txt. Extractor batch V08.

**Authors and affiliation.** Federico Mazzoni (independent researcher) and Andrea Failla (Institute of Information Science and Technologies, ISTI, National Research Council CNR, Italy) (title page). Mixed (independent plus academic or public research institute).

**Task and data.** Online moderation in two forms (Section 3). Policy-violation detection with explicit rules: PluRule (Reddit, discussion pairs, one violating and one compliant comment; six largest communities with 12,742 comments; published test intersection 2,829 pairs, 5,658 targets, 99.82% of the released test set) and HateModerate (Facebook hate-speech policy, 41 policy labels, 3,309 training and 3,302 test sentences after cleaning). Harmful-content detection: OLID (14,046 posts), HateXplain offensive/normal subset (14,123), ModerationBench text adaptation of Bluesky posts (3,689 posts; 2,584 Safe, 1,105 Unsafe; media described by InternVL3_5-4B-Instruct captions) (Section 3.1).

**Decision models.** Jev v1.13 and Laya v0.3 (Section 3 opening), through Choice, Noul and Score interfaces (Section 3.3). Jev-full (original rendering) and Jev-compact (same content as Laya) (Section 3.4). Run dates and API endpoints are not reported.

**Comparators and parity.** Laya under identical shared request content (Jev-compact versus Laya); five Detoxify variants as task-specific external references that did not see the datasets in training (Section 3.1); published PluRule systems (Qwen3-VL 8B Instruct, GPT-5.2 Low and High, best full context 57.7 EMA) as external reference points, not input-matched (Table 3). No tuning of any system; information conditions Direct, NAD (rules), RAD (five retrieved precedents), General (both); retrieval by qwen3-embedding:4b cosine similarity, five nearest same-subreddit leave-one-out precedents (Section 3.2). Parity asymmetry: Detoxify and published GPT-5.2 are references only.

**Reference labels.** PluRule: moderator-enforced subreddit rules (administrative field). HateModerate, OLID, HateXplain: dataset annotations (crowd or trained annotators; human_crowd). ModerationBench: real Bluesky moderation decisions with Safe/Unsafe (treated as administrative_field). Exact duplicates and contradictory annotations removed (Section 3.1).

**n, sampling, intervals.** 95% bootstrap CIs on the natural sampling unit (pair for PluRule, target for others), paired for contrasts, unadjusted for multiple comparisons (Section 3.5). Main tables report point estimates; CIs are given in text for matched contrasts.

**Exposure.** Public benchmarks with released labels (PluRule, OLID, HateXplain, HateModerate, ModerationBench); no contamination analysis. Detoxify stated not to have seen these datasets. Held-out train-sourced PluRule evaluation in Appendix B.

**Cost and latency.** Not reported.

**Calibration.** Predictive Brier on class probabilities, confidence Brier against exact correctness, correctness AUC, and coverage and accuracy at confidence >= 0.8 (Section 3.5, Table 8). Binned calibration measures only in the appendix (not extracted). The paper states Jev confidence is not consistently calibrated (Abstract). No post-hoc recalibration.

**Cascade or escalation.** Selective review: Jev at confidence >= 0.8 retains coverage 71.9% with accepted accuracy 94.3% on ModerationBench (Table 8); PluRule six communities coverage 45.0%, accepted 79.5%; Laya coverage 2.0% and 5.2% on PluRule and HateModerate respectively with weak accuracy. No second-tier model.

**Option-name, answer-space and robustness tests.** Answer-space restriction (all, represented, retrieved rules) separates information from answer-space effects (Section 3.2); opaque vs semantic policy labels in RAD (HateModerate: semantic labels lower Jev binary accuracy by 5.06 points and EMA by 1.64); Jev-full vs Jev-compact check (11.7 vs 12.35 EMA gain); caption-generator sensitivity in Appendix E. No language tests (English only).

**Code and data.** https://github.com/FedericoMz/som-moderation-benchmark (Section 3).

**Authors' limitations.** Only two SOM implementations, so Jev-Laya differences should not be generalized or attributed solely to architecture; retrieved precedents may reproduce historical inconsistency or bias; single-policy formulation excludes multi-violation cases; no generative-model baselines under the same conditions (Limitations).
