# mu2026hydrojev: HydroJEV, a one-second, training-free screen for cyber-attack and fault attribution in water distribution networks

## Identification

- arXiv 2610.02048v1, cs.AI, 01 Oct 2026 (header). Full text: fulltext/2610.02048.html and .txt. Supplementary notes S1-S12 and figures S1-S13 are referenced but not in the text read.
- Authors: Tianwei Mu, Shengyan Jiang, Mingzhe Yuan, Qing Luo, Min Xiao, Wenhong Wang, Jun Li, Manhong Huang. Affiliations: Shenyang Jianzhu University; Guangzhou Institute of Industrial Intelligence; Shenyang Institute of Automation, CAS; Shenyang University; Donghua University. Affiliation type: academic. No competing interests declared; funded by Guangdong, Shenyang University and Liaoning education grants.

## Task and data

- Four-class cause attribution for SCADA alarms in a water distribution network: cyberattack, physical fault, normal transient, sensor fault (Section 2.1). Window = 6 h of simulated SCADA record from stochastic EPANET simulations of C-Town via WNTR; reference family supplies 200 training windows (50 per class), 40 development windows and in-distribution sealed sets; three unseen subtype families (A, B, C; C is a look-alike family) used only for sealed sets. 1,279 windows evaluated in four sealed rounds on C-Town (Figure 1 caption); rounds 5 and 6 transfer the round-4 screen to EPANET Net3 and Net1 (200 windows per set).
- Reference labels are the simulator's event generator (synthetic); one hydraulic model generates both events and the digital twin (Section 4.4). A preliminary BATADAL study uses public data (64 attack windows vs 43 benign-alarm windows; Note S8).
- Test-set exposure: new simulated windows generated after design freeze from reserved seed ladders; cryptographic hashes of question, code and analysis script frozen before each sealed set (Section 2.7).
- Every method receives the same machine-readable evidence state (six parts; token scan confirmed no class or mechanism names) (Section 2.2).

## Decision model and comparators

- Jev, jev-1.13.0 for every call, single-choice question over five options (four classes plus "insufficient evidence"); prompt fixed on the 40 development windows; class definitions instruct equal priors. A label-free inductive prior correction (mean Jev answer on 40 unlabelled development windows, pi = 0.302, 0.429, 0.146, 0.121) divides the probabilities before argmax (Eqs. 1 and 2). Failed calls count as wrong. Each window sent once.
- Comparators: hand-written six-rule tree R1 (fixed before any Jev call); logistic regression R2 trained on 200 labelled windows, with leave-one-subtype-out retraining (R2 LOSO) and k-labels-per-class curves (k = 1 to 40, 200 draws); seven cloud LLMs through Ollama (deepseek-v4-pro, glm-5.2, gpt-oss:120b, gpt-oss:20b, gemma4, gemma4:31b, minimax-m2.7) receiving the same state and question at temperature 0 with fixed seed and a JSON schema returning five probabilities, each with the same label-free prior correction (Sections 2.4, 2.5).
- Cascades: rule cascade (accept every benign Jev verdict, otherwise R1) and LLM cascade (accept a benign Jev verdict only when R1 agrees, otherwise glm-5.2, secondary deepseek-v4-pro) (Section 2.6).

## Tuning-budget parity

Same evidence state and question for Jev and the seven LLMs, same label-free calibration (Section 2.5). R2 is given 200 labels (and more labelled variants). Cascade design was fixed on round-2 sets, confirmed on round 3 against a pre-set criterion (loses at most 0.03 macro-F1, accepts at least 15%), then tested on fresh sealed round-4 sets (Section 2.7). LLM times from rounds 2 and 3 were measured under concurrent load and are descriptive only; round-4 timings were strictly one request at a time on a subset of 20 windows per set (Section 2.9).

## n, sampling design, intervals

Sealed sets of 200 windows (50 per class; 10 per class in round 1). Primary metric four-class macro-F1; class-stratified paired bootstrap B = 10,000; non-inferiority margin 0.03; Holm correction within each round's pre-registered primary family; Wilson 95% intervals for proportions (Section 2.8, Table 2). With only two or four sets per condition, the SD is described as indicating spread only.

## Key results

- Jev macro-F1 in distribution 0.620, 0.628, 0.628, 0.644 (mean 0.63) vs R1 0.557, 0.606, 0.602, 0.590 (mean 0.59); no single difference significant; on new-family sets 0.51 vs 0.50; supervised R2 0.887-0.934 in distribution (mean 0.91) and 0.69 on new families (Sections 3.1, 3.2).
- Leave-one-subtype-out: R2 collapsed to 0.259, 0.240, 0.238, 0.227; Jev exceeded it by +0.361 [0.189, 0.523], +0.387 [0.318, 0.455], +0.390 [0.321, 0.458], +0.417 [0.344, 0.488] in rounds 1 to 4 (Holm-corrected primary tests) (Section 3.2). R2 overtook Jev at four labels per class on 7 of 8 sets (40 on E2); at one label per class R2 was below Jev in 96-97% of draws (Section 3.3).
- LLMs (round 2, E1r2 and E2r2): glm-5.2 0.706 and 0.697, deepseek-v4-pro 0.722 and 0.637 vs Jev 0.628 and 0.434; four of 14 Holm-corrected comparisons significant, all favouring an LLM (Section 3.4). Median time per decision: Jev 1.22 s over 2,722 calls (round 4: 1.18 s) vs glm-5.2 30.6-31.7 s and deepseek-v4-pro 39.3-46.4 s one at a time (means 43.5 and 48.0 s); 20 to 40 times faster; LLMs generate about 2,300-8,600 output tokens per decision.
- Cascade (Section 3.5): on fresh round-4 sets the glm-5.2 agreement-gated cascade differed from the reviewer by +0.011 [-0.011, 0.033] in distribution and +0.016 [0.003, 0.033] on the unseen family (non-inferior); deepseek-v4-pro +0.010 [-0.016, 0.035] and -0.009 [-0.038, 0.018]. The gate settled 34.5% and 38.0% of windows; mean time 43.5 s to 30.6 s (glm-5.2). Ungated rule cascade matched its components (-0.001 vs R1, -0.035 vs Jev on fresh sets). Accept precision 0.84 [0.74, 0.91] on E1c vs 0.58 [0.47, 0.68] on E4c. Cyber recall unchanged by the screen. Transfer to Net3 and Net1: gated cascade stayed within the margin on all four sets (Note S11, Figures S8; numbers not in the text).
- Prior-correction ablation: raw probabilities mean macro-F1 0.41 vs 0.57 with the label-free prior over rounds 1-3; transductive prior 0.58 (Section 3.6). Concealed cyberattack recall 0.34 (R1 0.32, R2 0.87). BATADAL: Jev AUROC 0.884 vs Mahalanobis 0.934 vs supervised 0.967; as a veto, FPR 25.6% to 7.0% at TPR 81.2%.
- Calibration: no ECE or Brier is reported; only the prior correction and accept precision are reported.

## Option-name, cardinality, language, robustness tests

Evidence format 2 vs 3 (three physics checks added) did not help Jev (0.60 vs 0.63). Subtype held-out and look-alike family tests. No option-name or language tests.

## Cost and latency

Latency reported as above; no dollar costs. Jev time is the service-reported compute time; client wall-clock also reported (Note S9).

## Code and data availability

https://github.com/mutianwei521/hydrojev: hydrojev library, generators, frozen questions and prompts, every Jev and LLM response, analysis scripts (Code and Data availability).

## Authors' own limitations (Section 4.4)

All windows simulated and one hydraulic model generates both events and twin; cloud LLM weights and serving conditions change without notice and timings come from one client at one time; gate accepts attacks that both Jev and R1 judge benign; concealed manipulation hardest class and best LLMs more accurate than Jev; ungated rule cascade does not improve on R1; accept precision lower on the unseen family; on Net1 bursts resemble demand changes and were rarely recognised.
