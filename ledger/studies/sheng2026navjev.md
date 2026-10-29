# Sheng, Wang, Li, Dai, Liu & Chen (2026), "NavJev: Efficient Vision-Language Navigation via Action-Centric Visual Compression and Discriminative Action-Semantic Memory"

Coder: batch V04. Full text: fulltext/2609.34969.html and .txt (arXiv HTML v1).

## Identification
- arXiv 2609.34969v1 [cs.RO], 28 Sep 2026.
- Authors: Kai Sheng, Liuyi Wang, Jinlong Li, Haojie Dai, Chengju Liu, Qijun Chen; College of Electronic and Information Engineering, Tongji University, Shanghai (author block). Affiliation type: academic.

## Task and data
- Zero-shot vision-and-language navigation in continuous environments. Each step selects one of up to five waypoint candidates or Stop through a typed option-label interface (Sections 4.4, 3).
- Data: 100 episodes from R2R-CE val-unseen under the Open-Nav evaluation framework (Section 5.1). The sampling rule for the 100 episodes is not described beyond "following recent zero-shot VLN methods". Real-world test: office and cafe, 10 tasks per scene, 20 in total (Section 5.7, Table 5).
- Labels: task outcome (success within goal region, SPL, nDTW, OSR).
- Test exposure: R2R-CE is public and pre-2026; no contamination check. Real-world tasks are private.

## Decision model
- Jev "accessed through its official API" (Section 5.1). No version identifier, no access dates. Version coded "not reported" (no match for "1.13" or "1.14" in the text).
- Pipeline: BLIP captions + RAM tags + waypoint geometry (ACVC), discriminative semantic memory (DASM), then Jev Choice over actions (Section 4).

## Comparators and tuning parity
- Controlled comparison (Section 5.4, Table 3): GPT-4o and "Qwen3.8-Max" replace Jev, keeping the same ACVC-DASM state and pipeline; reasoning disabled for both; "all three models receive the same structured textual state." Prompts for the autoregressive models are not shown in the text. The real-world comparison (Table 5) uses Qwen3.8-Max only.
- Table 1 zero-shot rows (Open-Nav, SmartWay, P2DNav, MapGPT, DiscussNav, CA-Nav) and supervised rows are numbers from other papers; they use different pipelines and MLLM backbones, and the supervised rows are on the full val-unseen split. The best zero-shot SR in Table 1 is P2DNav 50.0, far above NavJev 27.0.

## Results
- Table 3 (100 episodes): SR 14.0 (GPT-4o), 25.0 (Qwen3.8-Max), 27.0 (NavJev); SPL 8.5, 16.0, 22.4; OSR 42.0, 46.0, 35.0; nDTW 23.8, 34.2, 43.5; decision latency 1.54, 1.03, 0.53 s; total API cost USD 3.67, 2.19, 0.06 (Section 5.4).
- Table 1: NavJev NE 7.48, OSR 35.0, SR 27.0, SPL 22.4.
- Latency: 0.65 s per step; Open-Nav 27.00 s, SmartWay 5.30 s, P2DNav 4.92 s (Section 5.3, Figure 3a). Breakdown: Jev API 534.6 ms of 647.9 ms (82.5%). Local hardware NVIDIA RTX PRO 6000 GPU (Section 5.1).
- Real world (Table 5): NavJev OSR 60.0, SR 50.0 vs Qwen3.8-Max 35.0 and 35.0; decision latency 0.65 vs 1.10 s.
- Failure analysis: 73 of 100 episodes failed, 60 (82.2%) from incorrect waypoint selection (Section 5.6).

## Sampling design and intervals
- n = 100 episodes, one run each. The "±" values on latency are given without stating whether they are standard deviations. No confidence intervals or significance tests for SR or SPL. With n = 100, the 2-point SR gap to Qwen3.8-Max is within sampling noise of a binomial proportion, but the paper does not test it.

## Calibration and cascade
- Jev's probabilities are not analysed; only the argmax action is used. No calibration or escalation analysis.

## Robustness
- Ablation of BLIP, RAM and DASM components (Table 4: SR 19.0, 21.0, 27.0). No option-order, option-name or action-cardinality test (maximum five candidates).

## Code and data
- Project page https://kai-sheng-caesar.github.io/NavJev/ (Abstract). No code repository is stated in the text.

## Authors' stated limitations
- No separate limitations section; Section 5.6 states that fine-grained spatial grounding and relational reasoning remain the bottleneck.

## Coder notes
- Jev's OSR (35.0) is lower than Qwen3.8-Max (46.0) in Table 3; the row is kept.
- Jev's API latency (534.6 ms) dominates the 0.65 s step time.
