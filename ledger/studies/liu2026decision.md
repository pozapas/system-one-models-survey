# liu2026decision

arXiv 2610.34124v1 (cs.IR), 25 Oct 2026. "Decision-Native Recommendation with Large Language Models." Authors Daoxuan Liu, Jiayi Liao (Independent Researcher, Beijing), Jiancan Wu, An Zhang, Xiang Wang, Xiangnan He (University of Science and Technology of China, Hefei). Affiliation type: academic (one independent co-author). (title block)

## Task and data
- Sequential next-item recommendation framed as a choice among K supplied candidates (main K=20: target plus 19 uniformly sampled negatives; candidate order randomized per example). Goodreads (6,031 users, 4,500 items, 220,100 interactions), LastFM (1,220 users, 4,606 items, 73,510), Amazon Reviews 2023 Industrial and Scientific (51,000 users, 25,800 items, 412,900). Chronological 8:1:1 split following S-DPO and NAPO. Test-set sizes are not stated. (Sec. 4.1, App. A.1, Table 7)
- Reference label: observed next interaction (task outcome). (Sec. 3, App. A.1)
- Public data (Goodreads, HetRec 2011 LastFM, Amazon Reviews 2023); item titles may be in LLM pretraining; no contamination check. Cold items "may have appeared in LLM pretraining". (Sec. 4.1, App. A.2)

## Decision model
- DICE (Direct Item Choice Estimation): Qwen3-0.6B frozen backbone, LoRA rank 8 alpha 32 on attention projections, scalar choice head, softmax over candidates, one forward pass with tree-structured attention; DICE-I (independent scoring, main) and DICE-S (candidate-interaction extension). Qwen3-1.7B and 4B variants in Table 2. Trained 3 epochs, epoch-3 checkpoint, AdamW lr 1e-5, batch 128. No version or revision hash; anonymous repository. Not a hosted Jev model; the paper says it is inspired by Jev (Almeida 2026) and does not evaluate Jev. (Sec. 3, App. A.3)

## Comparators and tuning parity
- GRU4Rec, Caser, SASRec (L2 tuned over 5 values); Qwen3 base, SFT, S-DPO, NAPO, RE2-SFT+GRPO, SelfDR-style student; direct-ranking LlamaRec and InvariRank. LLM baselines use the same Qwen3-0.6B backbone, data, candidates, and "follow their original training procedures and method-specific hyperparameters"; generation-based baselines are scored by item-name log-likelihood in the main table and by greedy generation separately (Table 4). S-DPO was selected by development answer-generation accuracy. (Sec. 4.1, App. A.3, A.5, A.7)
- Means over three random seeds; DICE-I HR@1 sample SD at most 0.0017 (Table 8). No significance tests, no confidence intervals on test sets.

## Results
HR@1 DICE-I 0.5332 Goodreads (LlamaRec 0.4718), 0.6160 LastFM (0.5960), 0.3767 Amazon Industrial (0.3650); DICE-S 0.5349 / 0.6096 / 0.3834. 4B backbone LastFM 0.7018. Cold-start HR@1 DICE-I 0.2397 / 0.2303 / 0.2495 (Goodreads: SFT and S-DPO 0.2562 higher). At K=100 DICE-I beats S-DPO by 16.45 pp (Goodreads) and 26.09 pp (LastFM). (Table 1, 2, 3, Sec. 4.3)

## Cost and latency
End-to-end mean latency K=20, 200 examples per run, on one NVIDIA H20 (FP32): DICE-I tree 51.27 / 38.34 ms (Goodreads / LastFM) versus SFT 316.81 / 119.41 ms and S-DPO 320.93 / 116.44 ms; tree is 4.53x and 2.40x faster than DICE-I flat encoding. 4B tree 139.85 ms on LastFM. Model loading and warm-up excluded. (Fig. 3, App. A.7, A.11)

## Calibration
ECE with ten equal-width bins, per run then averaged; single temperature fitted on a held-out development set (D_T), also applied to LlamaRec and InvariRank. Raw ECE 0.0606 / 0.0730 (Goodreads / LastFM), calibrated 0.0538 / 0.0203; LlamaRec calibrated 0.0631 / 0.0336, InvariRank 0.0584 / 0.0287. (Table 6, App. A.10)

## Cascade or escalation
Confidence-based selective recommendation (thresholds frozen on disjoint dev set): about 25% coverage gives 88.82% (Goodreads) and 94.42% (LastFM) accuracy. Offline 0.6B to 4B routing on LastFM: escalating 47.78% gives HR@1 0.6986, over 99.5% of the 4B-only 0.7018, estimated sequential latency 105.16 ms, 24.8% below 4B-only; latency is estimated from component costs, not an online cascade. (Sec. 4.4, Fig. 5-6, App. A.11)

## Robustness
Candidate-order FlipRate over 64 examples x 20 reorderings per run: DICE 0.0000, SFT 0.3180 / 0.2984, S-DPO 0.4500 / 0.3125 (Goodreads / LastFM). ValidRatio 100% versus SFT 80.55% / 92.58%. Candidate-count sensitivity K=5 to 100. No option-name or language tests. (Table 5, Table 9, Fig. 4)

## Code and data
Anonymous repository https://anonymous.4open.science/r/dice-73B3/. Datasets public. (App. A)

## Authors' limitations
No dedicated limitations section. Future work notes the candidate pool is supplied (no retrieval or abstention when target is absent), calibration is static, routing is offline only. Appendix C notes controls differ in capacity and information. (Sec. 5, App. C)
