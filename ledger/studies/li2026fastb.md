# li2026fastb: Fast Models, Slow Evidence, a paired and self-audited evaluation of System-1 decision models for LLM agent harnesses

(Key carries suffix b because li2026fast.md already exists for a different paper, 2609.23136.)

## Identification

- arXiv 2610.02267v1, cs.AI, 01 Oct 2026 (header). Full text: fulltext/2610.02267.html and .txt.
- Author: Jiawei Li, single author; no affiliation stated in the text read. Affiliation type: independent. Acknowledgments state LLM assistants were used for coding and editing and the author checked all numbers.

## Task and data

- Paired evaluation of an open-weight (Laya 0.3.21) and a hosted (Jev, jev-1.13.0) System-1 model on 11 agent-harness decision points built from 18 public sources: 7,283 base cases plus 6,640 robustness variants (Abstract). Suite A-F (2,100 cases): A model routing (RouterBench, 400), B tool selection (BFCL, 400, K in {2,5,10,20,50}), C tool-call guard (300), D RAG relevance (BEIR x 5 plus BM25 negatives, 1,920), E injection guard (400), F large label set (BANKING77, MASSIVE, 200). Agent-infrastructure suite G-J (1,280): G injection across two channels (480), H groundedness (HaluEval-QA, 200), I pre-execution safety (BeaverTails, HarmBench, Do-Not-Answer, 400), J PII egress (ai4privacy, 200). Controls: B2 hard distractors (400), G2 injection in documents (480), J2 natural redaction (100); S two-tier safety (603) (Table 1, Appendix A).
- Reference labels: dataset labels (BFCL gold function, BEIR relevance judgements, dataset safety and injection labels); routing labels derived from RouterBench per-item outcomes (cheap if a 7B model and GPT-4 both solved the item, strong if only GPT-4 did); positives for D are BEIR judgements with BM25 or random negatives; track S gold comes from a written policy applied by a different LLM (GLM-4.6), which agrees with dataset labels on only 72.8% of 540 items (Section 4, Section 6). The paper quantifies label noise with a blind LLM judge (DeepSeek-V4.1-Flash) on 360 cases: it agrees with dataset labels on 90.0% of items both models got right, 75.7% of disagreements, 12.7% of items both got wrong (Section 8). The ledger codes the main-suite labels as human_adjudicated (dataset labels), with the mixed label types noted here.
- Test-set exposure: all sources are public pre-2026; the author notes near-perfect scores on popular sets (B, E) may partly reflect exposure; controls G2/B2/J2 use newly composed inputs (Section 8).

## Models evaluated

- Laya 0.3.21 (open weights, routes each request to an English or a multilingual checkpoint; transformers 5.17.0, torch 2.14.0). Its typed-decisions checkpoint crashed on the author's GPU and is not evaluated; on the 100-case pilot (CPU) it matched the default router within one point (59% vs 58%).
- Jev, jev-1.13.0, returned on every call across two days. Total Jev spend across all runs $0.52 (Appendix E).
- DeepSeek-V4.1-Flash (temperature 0) as a reference LLM in the controls and as the reviewer in track S; not part of the paired comparison because its input format necessarily differs (Section 3).

## Tuning-budget parity

Both systems receive byte-identical state and questions for every case; confidence = max p for choice and max(p, 1-p) for yes/no, following Laya's own calibration code (Laya's response field "confidence" differs from max p by 0.299 on average vs 0.010 for Jev) (Section 3). Zero-shot only; Laya's fine-tuning path not evaluated. Rewording instructions alone (4 wordings x 2 case samples) moves accuracy by 5 to 15 pp per track for both systems, so any single accuracy carries about a plus or minus 5 pp wording band (Section 5, Figure 3b); Jev leads in 8 of 8 wording-by-sample combinations on B, C, E and F (smallest margin +1.3 pp on E); on A and D the sign flips (6/8 and 7/8). Laya's released code gives all options a 192-token budget, truncating each option to max(4, (192-16)/K) tokens, which explains its drop with many options.

## n, sampling design, intervals

Wilson intervals for accuracies, exact McNemar tests on discordant pairs with an asymptotic CI for the paired difference, no multiplicity correction; differences called only at p < 0.001, ties called at p > 0.4 where the CI is narrow (Section 3). Pilot of 100 cases with case-by-case label checks is disjoint from the 2,100-case suite.

## Key results

- Accuracy: Jev 76.7% vs Laya 63.1% on A-F (455 vs 169 discordant wins), 80.2% vs 66.0% on G-J; Jev significantly more accurate on 9 of 11 decision points (+10.8 to +46.0 pp); F 81.0% vs 35.0% (+46.0 [38.7, 53.3]); A tie at chance (Jev says "cheap" for 99.5% of requests, 50.0%; Laya AUROC 0.48); D 61.0% vs 60.5% (+0.5 [-2.0, 3.0]) with opposite error directions (Section 5).
- Tool selection: random distractors Laya 100% at K = 2 to 53.8% at K = 50, Jev at least 98.8%; nearest-neighbour distractors Laya 54.0% overall and 31.3% at K = 50, Jev 84.5% overall (an LLM audit found another valid tool in 19.8% of B2 items); on the 70.2% of items with a unique correct tool Jev 98.9% vs Laya 61.6% (Section 5).
- Guards: tool-call guard Laya says "call a tool" for 74.7% of no-tool requests (Jev 40.0%); pre-execution safety Laya lets through 81.5% of harmful requests (Jev 25.5%); PII Laya AUROC 0.41 (neither a usable PII gate, J2: Laya 0.40, Jev 0.82; Jev false-positive rate 66% to 63%).
- Order and wording: reversing the option list changes 30.3% of Laya's decisions (53% with 60 to 77 labels) vs 1.8% for Jev; in routing Laya picks "cheap" for 58.5% originally and 82.3% reversed. Multilingual cells n = 10; Laya 0/10 in Arabic and Hindi with 60 labels.
- Calibration: pooled ECE Laya 0.158 vs Jev 0.143 on A-F (Jev's figure dominated by routing where it is confidently constant, ECE 0.477) and 0.198 vs 0.080 on G-J; 26% of Laya's answers with confidence at least 0.9 are wrong; Platt scaling fitted on half of D lowers held-out ECE for Laya 0.22 to 0.027 and Jev 0.21 to 0.10. Binning scheme not stated in the main text.
- Gates: RAG skip-gate at a 5% miss budget keeps 79.8% of LLM calls (Jev) vs 92.4% (Laya), 97.9% of answerable queries still answered, a perfect gate saves at most 58%, Jev AUROC 0.71 vs 0.61. Thresholds chosen on the same data guarantee a 5% target by construction; on held-out halves the 95th-percentile FNR is 6 to 8% for D and 10 to 17% for 100 to 200 positive tracks. Two-tier safety review with Jev pre-screen: cost falls only 4.3% at tau = 0.1 (original claim 23.9%), costs 4.7% more at tau = 0.05; extra miss in 47% of held-out splits; reviewer cost $72 per million requests batched, one Jev call 20% of that. Laya must pass 99.3% of traffic to preserve recall. Laya-then-Jev cascade at confidence 0.9: 41.7% local, 45% Jev spend saved ($16 per million), accuracy 76.7% to 70.7%.
- Reproducibility: Jev changed 1 of 420 re-run decisions, 5 of 1,080 one day later (0.5%); Laya changed 0 of 420 and reproduced 1,180/1,180 on a second machine (max |delta p| = 0.006) (Section 3).
- Self-audit (Table 2): omitted pre-screen cost (23.9% claimed vs 4.3%), gate accuracy reported as end-to-end quality (58% vs 98% retained), in-sample thresholds, and a "channel effect" on injection false positives that disappears with native documents (Jev 0% to 0%; Laya 6.7% to 10.0%, p = 0.34). Latency claim "Jev roughly 10 times slower" withdrawn (83 to 325 ms vs 31 to 200 ms depending on site and hardware).

## Cost and latency

Laya 31 ms p50 on an RTX 2080 Ti, 200 ms on an Apple M4 CPU; Jev 325 ms p50 from one client site and 83 ms from another. Jev 759 tokens per decision, about $32 per million decisions at $0.042/M tokens; Laya marginal cost is local compute (Section 5).

## Code and data availability

All cases, raw outputs and analysis code at https://github.com/David-DL-Space/sys1-eval (Abstract, Appendix E; paper/analysis.py regenerates numbers and figures).

## Authors' own limitations

Two systems at single versions, zero-shot, public English-dominant data with synthetic class mixes; absolute accuracies carry a plus or minus 5 pp wording band; gate savings depend on production base rates; latency from two client sites and two hardware types; safety and PII gold involve LLM annotators with different policies (72.8% agreement); the reference LLM gets a different prompt format; Laya fine-tuning untested; routing labels from single runs with 79% multiple-choice items, so routing result does not measure the limit of routing; the unique-tool subset was filtered by an LLM and may favour LLM-like judgements; judge may share preferences with Jev (the judge sides with Jev in 131 of 145 decided disagreements).
