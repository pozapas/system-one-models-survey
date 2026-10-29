# xu2026trustjev

arXiv 2610.34826v1 (cs.AI), 26 Oct 2026. "TrustJev: Separating Policy Authority from Untrusted Evidence in LLM-Based Decisions." Authors Zhiwei Xu, Xuyang Liu, Xiaolin Peng, Weixian Deng, Jiabao Gao, Zirui Li, Tian Qiu, Hai Wan, Xibin Zhao (KLISS, BNRist, School of Software, Tsinghua University) and Boya Zhou, Wei Jiao (ChinaBond Finance and Information Technology Co., Ltd., Beijing). Affiliation type: mixed (academic plus industry co-authors). (title block)

## Task and data
- Policy-guided candidate decisions under prompt injection: input x = (trusted policy P, external evidence D, candidates C); model must resist injected instructions in D while following changed facts. Metrics: Utility (accuracy on non-attack views), Robustness (accuracy on attack views), Balance (harmonic mean). (Sec. II, IV-A2)
- TensorTrust adapted (authentication, 2 candidates; 512/256/783 train/val/test groups; 1,566 test views, 783 attack), IHEval adapted (language identification and Slack shortest-username, 3 candidates; 384 test groups, 1,728 views, 1,152 attack), AuthorityEvidenceBench AEB (authors' benchmark, 7 task types, executable-rule labels, 512 test groups, 3,072 views, 1,024 attack). Splits by base case with duplicate checks. (Table II)
- Reference labels: TensorTrust and IHEval dataset labels; AEB labels from executable rules (synthetic). RQ5 industrial alerts: 178 source cases from 10,349 logs of about ten subsidiaries, 1,242 views including 581 author-crafted attacks, private. (Sec. IV-A1, IV-F)
- TensorTrust and IHEval are public prior datasets; AEB new; no contamination check for Jev 1.13.0. (Sec. IV-A1)

## Decision models
- TrustJev: Qwen3-0.6B, rank-8 LoRA, trainable readouts, single Transformer forward pass, three runs; no checkpoint hash. (Sec. IV-A4)
- Evaluated third-party decision systems: Jev 1.13.0 (hosted, native Choice interface, no fine-tuning), Kev-0.8B (Git revision 54f4f877; native and fine-tuned), SecJev-0.8B (native and fine-tuned). No run dates given. (Sec. IV-A3, IV-A4)

## Comparators and tuning parity
- 14 baselines: Jev, Kev, SecJev, Kev and SecJev fine-tuned, StruQ, SecAlign, PIGuard, DRIP, Flat SFT, Structured SFT, R-Drop, Group DRO, DPO. Defenses and training baselines share TrustJev's backbone and are trained on the same data; checkpoints selected on validation Balance. Native Jev, Kev, SecJev were not tuned (asymmetry: Jev cannot be fine-tuned); PIGuard uses a different encoder (DeBERTa-v3-base). Authors flag implementation, training and calibration differences as a validity threat. (Sec. IV-A3, VI)

## Results
Balance (mean of 3 runs): TrustJev 90.11 (TensorTrust), 99.44 (IHEval), 99.46 (AEB), exceeding the strongest baseline by 1.05, 0.57, 0.87 points; Jev 1.13.0 76.56, 98.83, 94.96; native Kev 56.10, 40.52, 46.77; fine-tuned Kev 88.83, 98.35, 98.59. Cumulative robust accuracy over a fixed 32-attack pool: TrustJev 95.77% vs fine-tuned Kev 80.98%. Industrial triage: TrustJev 97.65% attack-view accuracy vs direct Jev 92.56%, Jev downgrade error 16.53%. Reporting is mean and sample SD over three runs; Jev and native Kev/SecJev are single deterministic evaluations without SD. No hypothesis tests. (Table III, Sec. IV-D, Table VII)

## Cost and latency
Median latency near 40-41 ms for TrustJev (batch 1, one RTX 4090), P95 45.2 and 43.3 ms on IHEval and TensorTrust; direct Jev P50 201.47 ms in industrial study (API, includes network, different infrastructure). Training 0.815 GPU h vs 0.568 to 0.629 for four baselines. Inference memory about 1.2 GiB for all methods. (Sec. IV-E, IV-F, Table VI, VII)

## Calibration
None reported; authentication threshold chosen on development data for Balance. No ECE or Brier. (Sec. III-B, IV-A4)

## Cascade or escalation
None.

## Robustness
Attack variants (16 existing, 16 new per source), composition (authority spoofing, fake verification, combined), multiple attempts (cumulative robust accuracy to 32); ablations A1-A7. Candidate count only two or three. No option-name or language tests. (Sec. IV-C, IV-D)

## Code and data
Code at https://github.com/xu-zhiwei/trustjev. (Sec. I, contributions)

## Authors' limitations (Sec. VI)
Adapted defenses vs native decision systems confounded by implementation and calibration differences; semantic overlap across splits not ruled out; small differences uncertain with three runs; attacks sharing a source not independent; no adaptive attackers; one model scale and two or three candidates; AEB underrepresents ambiguous policies; Balance omits unequal error costs; local latency excludes network and queueing.
