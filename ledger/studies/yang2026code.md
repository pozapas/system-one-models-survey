# yang2026code: Code Owns the Simulation, Jev Owns the Evaluation

## Identification

- arXiv 2610.01834; first public version 2026-10-01 (screen file); the HTML retrieved on 2026-10-28 is v2 dated 10 Oct 2026 ("arXiv:2610.01834v2 [cs.AI] 10 Oct 2026"). Numbers extracted from v2; v1 text not inspected, so v1/v2 differences are unknown. Full text: fulltext/2610.01834.html and .txt.
- Authors: Yaodong Yang (CUHK), Hongyao Tang (Tianjin University), Yi Ma (Shanxi University), Xingyu Fan (CUHK), Weixun Wang (Independent Researcher), Jinpeng Li (CAIR, Hong Kong Institute of Science & Innovation, CAS), Tianpei Yang (Nanjing University). Affiliation type: academic.

## Task and data

- Tests which decisions a judgment model can be trusted with, defined as "evaluation" (right option judged from the input) vs "simulation" (right option needs a prediction not in the input) (Section 2).
- Four settings: (1) Cognitive Reflection Test, 150 new questions of Hagendorff et al. (2023), each as four options in four orders, plus control versions with no trap (Section 3, Table 1); (2) 210 random 3x3 matrix games, 30 games for D=0 and 30 for each of D = 1, 2, 3 x aligned/misleading, three option orders (Section 4.1); (3) ALFWorld, 134 unseen and 140 seen games; single-decision replay of the expert's successful trajectories (116 seen games solved by the expert) and closed-loop play with at most 50 steps (Section 5, Appendix D); (4) DeepMind Control Suite Stacker robot control, 20 native-task episodes and five new instructions x 8 seeds (Section 6).
- Reference labels: task outcome or environment-derived correct set; CRT answer keys from Hagendorff et al. (2023). Whether a decision needs simulation and whether it is aligned or misleading is computed from the environment, never from Jev's choices (Section 2).
- Test-set exposure: all benchmarks public before 2026; no contamination analysis (the generated games are new). The ALFWorld surface shortcut was defined on the unseen games and tested on the seen games (Section 5.1).

## Decision model

- Jev, jev-1.13.0, TypeSafe public API, zero-shot with one fixed instruction per condition (Section 2, Appendix A). One choice question per request (Stacker raw torques: one per actuator). Choice probabilities averaged over several option orders (Section 2). Repeating a call changes probabilities by 0.04 on average (Reproducibility Statement).
- No LLM comparators. Reference points: published human and ChatGPT results on the CRT (open-ended answers, reference only; Table 1), a word-overlap rule given the same lookahead (18 of 134 ALFWorld games), uniform random choice, a hand-written Stacker controller (Table 3).

## Tuning-budget parity

Not applicable for most comparisons (single system). Stacker skills were "tuned on the native task" (Appendix E) and then generalised to the five new instructions where the hand-written controller was run unchanged (Table 3). Dates of runs are not stated in the text read.

## n, sampling design, intervals

CRT 150 questions x 4 orders, 95% interval [0.97, 1.00] for the lure correct rate. Games: 210 games x 3 orders, 95% bootstrap over games. ALFWorld: 134 unseen games (CIs on solved fraction in Table 6); a second run repeats the Jev conditions. Stacker: 20 and 40 episodes, counts only. "Analysis of which predictions Jev can make from the input is partly post hoc" (Section 8).

## Key results

- CRT: Jev correct 0.99 and intuitive 0.01 on lure questions; control versions correct 0.96; published ChatGPT-4 0.96, humans 0.38 (Table 1).
- Games: dominant action (D=0) 100%; aligned games 77-93%; misleading games 28-37% with lure picked 53-71%; an instruction to reason leaves misleading games at 37-38%; when code states the opponent's action 97-99% (Section 4.1). Jev predicts the opponent's action correctly 90% of the time in a separate call but chooses correctly 32% / 35% of the time whether its prediction was right or wrong; two-call chain 33% to 94% (Section 4.3, Table 2). Level-1 quantal rule fits best (Table 4).
- ALFWorld single steps (seen games): 93% at E steps that take, put or clean, 99% at aligned S-known steps, 36% at misleading S-known steps with lure 56% (Section 5.1). Separate next-subgoal prediction correct 100% (ordered form) vs 33% (goal form) (Table 2). Closed loop (unseen, 134 games): Jev alone 42 (31%), 39 on Run 2; + next observation 79; + newly possible commands 116 (87%), 117 on Run 2; word-overlap rule with the same lookahead 18 (Section 5.3, Table 6).
- Stacker: raw torques 0/20 (random 0/20); skills simulated by code 9/20 vs hand-written 8/20 vs random 1/20; five new instructions 22/40 vs hand-written 3/40 vs random 0/40 (Table 3).
- Option-order sensitivity: handled by averaging over orders; ties and order effects are a stated nuisance. In Example 4 (Section 8, Appendix F) Jev follows the order in which the task mentions actions: 24% correct when "putting" is mentioned first vs 69% when "cleaning" is first.

## Cost and latency

About 94M input tokens in total, about $4 at the TypeSafe price of $0.042 per million input tokens listed in September 2026; closed-loop ALFWorld about $2.2; Stacker about $0.9; environments on CPUs of a single server (Appendix H, Table 7). Latency not reported.

## Calibration and cascade

No calibration analysis. The two-call chain (predict, then decide) and the code lookahead are escalation-like architectures, but there is no confidence-gated cascade.

## Code and data availability

Promised only: "We will release the code, the raw runs and these scripts." No URL in the text (Reproducibility Statement). Recorded as no.

## Authors' own limitations (Section 8)

One model and one API version; other no-reasoning-text models and reasoning-enabled variants untested; the lookahead and Stacker simulation use an exact environment copy a real agent may not have; ALFWorld lookahead is one command deep; analysis of which predictions Jev can make is partly post hoc; some relational facts (dominated actions) are missed even in a separate call (19% identified).
