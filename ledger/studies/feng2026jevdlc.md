# feng2026jevdlc

arXiv 2610.31521v1 (cs.AI), 22 Oct 2026. "Jev-DLC: Decision-Level Continual Learning from Typed Feedback." Authors Yangyang Feng, Jianle Gan (equal contribution), Zhuoyan Feng, Chengwei Qin (corresponding), at The Hong Kong University of Science and Technology (Guangzhou) and Sun Yat-sen University. Affiliation type: academic. (title block)

Study type: method paper (own-model). Jev-DLC is a per-user state (two bounded channels) placed above a frozen typed scorer; the decision models measured are the frozen local scorer JEV-SFT and the hosted Jev as a frozen anchor.

## Task and data
- TCPA-Repeat: LaMP-2 converted into 15-way movie-tag decisions with chronological per-user streams. Users disjoint across splits: train 747 users and 5,216 events, development 90 and 556, test 92 and 711; slate size 15. (App. A.3, Table 6)
- TCPA-Open: derived from MIND impression logs, four-item news slates; train, development, test 79,849, 10,221 and 9,845 events; test has 4,209 users. (App. A.4)
- TCPA-Dynamics: synthetic streams (stable, partial shift, recurrence, 20% label noise), eight users and 512 events per regime. (App. A.4, F.3)
- Reference labels: the original LaMP-2 tag (a user-assigned tag from the source dataset) for Repeat; the clicked item for Open. Not independent of the source datasets; typed feedback is simulated from these labels (accept if prediction equals target, revoke otherwise). (Sec. 3.2, 6.1, App. A.1)
- Datasets are public and predate 2026 (LaMP 2024, MIND 2020); the paper does not discuss pretraining exposure of Qwen. The JEV-SFT scorer was trained on balanced TCPA-Repeat and TCPA-Open training records (users disjoint from test). (App. B.2)
- Primary metric user-macro accuracy; also event-micro accuracy, NLL, ten-bin ECE and Brier are said to be secondary (App. A.6). ECE and Brier values are not given in the tables; NLL appears only in Table 13.

## Decision models
- Frozen local scorer JEV-SFT: Qwen3.8-27B adapted with LoRA rank 8, scale 16, 300 optimizer steps, lr 1e-4, max length 2,048; scores option letters at the first output position; no model revision string. (Sec. 4.1, App. B.2)
- Hosted Jev: endpoint api.typesafe.ai/v1/systemone, requested jev-latest, returned jev-1.13.0 on every call (711 Repeat and 9,845 Open events, zero residual failures); UTC dates recorded in traces but not stated. Receives no history. (App. G.3, Table 28)
- Raw Qwen option logprob baseline (unadapted). (App. D.1, Table 8)
- Jev-DLC: two channels (conservative with count prior and local repair, responsive with correction direction) with adaptive fixed-share weights; PA-I update; 32-dim projection fitted on training users; state 324 B. (Sec. 4)

## Comparators and tuning parity
- Recent-4 reruns the same JEV-SFT with four typed interactions in the prompt (K=4 chosen over K=8 on development). PPlug, TAP-PER and MRM are the authors' own matched re-implementations sharing the learned projection and cache; AdaGrad, ONS, DER++-8 and Directional Drift are archived rows whose representation provenance "requires reconciliation" before being called matched controls. Shared components fitted on training users, configurations selected on development users. (Sec. 7.1, App. B.5)
- Channel and fusion comparisons (Table 20) use a "collaborator-supplied aggregate" package retained separately. (App. H.1, H.4)
- Hosted Jev is a current-event anchor only and is not a personalised baseline. (Table 28)

## Results
TCPA-Repeat user-macro accuracy: Frozen JEV-SFT 39.44, Recent-4 42.40, AdaGrad 41.99, PPlug 40.37, TAP-PER 41.99, MRM-style 40.67, Jev-DLC 44.83 (gain over frozen +5.39, 95% CI [+2.04, +8.74]; over Recent-4 +2.43, CI [-1.33, +6.30], includes zero; over PPlug +4.47 and MRM +4.16, intervals exclude zero). After at least two earlier feedback events Jev-DLC 56.07 (+14.49 over frozen, CI [+7.42, +22.63]); depth cells shrink to 15 users at d>=8. Channel ablation: C only 43.12, R only 41.50. Adaptive versus development-fixed fusion +0.68 (CI [+0.16, +1.20]). Hosted Jev frozen anchor 41.22 on Repeat and 24.05 on Open; frozen JEV-SFT 39.44 and 28.04. (Tables 1, 2, 8, 9, 16, 20, 21, 28)
TCPA-Open: Jev-DLC 29.74 versus PPlug 31.30 (paired difference CI [-2.17, -0.92]), so the method does not win there; depth-8 stratum gain -0.59. Dynamics synthetic regimes: full-method replay gives no consistent gain over frozen (Table 27). (App. F)

## Cost and latency
State 324 B per user, no retained history, no extra scorer call; Recent-4 retains 1,166.5 B raw history and adds 262.8 tokens per event. State computation 0.1781 ms (prediction) plus 0.0810 ms (feedback) on CPU; scorer forward 300.54 ms (K=0) versus 449.90 ms (Recent-4), batch 4, max length 4,096, same server (GPU model not given). Compute: one scheduled GPU job each for SFT, cache export, Recent-K and base-forward timing. (Sec. 7.3, App. B.6, H.2, Tables 3, 13)

## Calibration
Defined as secondary metrics but no ECE or Brier numbers reported. No post-hoc calibration.

## Cascade or escalation
None.

## Robustness
Controlled shift, recurrence and noise streams (Table 25, 27) are synthetic; no option-name, cardinality, or language tests. Seeds: projection seed 20260927, bootstrap seed 20260928; a seed analysis is mentioned in App. E but the table is not present.

## Code and data
No repository link given. The paper describes a frozen result package with hashes (App. H.1) but no public URL.

## Authors' limitations (Limitations section)
Immediate accept and revoke feedback over a finite candidate set; delayed or free-form feedback not handled; repeated-action setting gives the clearest evidence, changing-item recommendation favours PPlug overall; storage bound depends on evaluated semantic vocabularies.
