# ma2026jevstar — JEV-Star: Fast, Low-Cost StarCraft II Control with Language-Model Planning

- arXiv: 2609.27331v1 [cs.GT], submitted 23 Sep 2026. License CC BY 4.0.
- Authors: Weiyu Ma, Liangbing Zhao, Yongcheng Zeng (Institute of Automation, Chinese Academy of Sciences), Jian Zhao (Beijing Zhongguancun Academy). Affiliation type: academic. (Byline formatting in the HTML export runs "Weiyu Ma" and "Liangbing Zhao" together without a separating space; author list taken as printed.)
- Source: fulltext/2609.27331.html / .txt (fetched via `https://arxiv.org/html/2609.27331v1`, 2026-09-24).
- No seed claims assigned to this paper in the extraction brief (agent control / game-playing paper included for its own decision-model measurements).
- Code: https://github.com/sc2musa/Jev_Star (stated in Abstract).

## Task and data
StarCraft II control, two settings: (1) full-game macro control (Protoss vs. built-in Zerg AI on map AltitudeLE, difficulties Lv2/Lv5/Lv6/Lv7/Lv8, StarCraft II 5.0.16), and (2) micromanagement on 35 SMAC-Hard local battle maps, 3 episodes per map per method (105 episodes each). JEV selects a structured action identifier from an executable candidate set at each decision point (Eq. 1); in the combined system, GPT-6 (Astra, medium reasoning effort) supplies a persistent plan (goals, resource reservations, army posture) that both conditions JEV's context and constrains its candidate set (Eq. 2, §3.2).

## Decision models evaluated / version pin
JEV 1.13 (macro and micro action selection, "JEV-only" system) and JEV 1.13 + GPT-6 Astra (medium reasoning effort) as the combined planning system (§4.1, "Setup and measurements": "The runs use JEV 1.13, GPT-6 Astra with medium reasoning effort, and StarCraft II 5.0.16"). No fine-tuning: "Neither method fine-tunes JEV or GPT-6" (§3.3).

## Comparators and tuning-budget parity
JEV-only vs. JEV+GPT-6 is the paper's central comparison — an ablation-style comparison of complete systems, explicitly NOT a controlled planner-only ablation: "The comparison evaluates complete systems; concurrent interface improvements mean that planning's contribution is not isolated by a controlled ablation" (Abstract); "candidate descriptions and execution handling also improved between the two controllers" (§4.1). No external LLM-router or generative-cascade baseline is used; the only external comparison is a qualitative difficulty-milestone comparison to LLM Play SC2's GPT-4-Turbo/GPT-3.5 results (§4.2), explicitly flagged as not a matched win-rate comparison because game versions/starting conditions differ.

## Reference labels
Game outcomes (win/draw/loss, terminal state) and enemy-elimination fractions are read directly from the StarCraft II engine/replays — reference_label_type = task_outcome. "Macro outcomes and game durations are checked against replays" (§4.1).

## n and sampling
Full-game: 1 JEV-only game (Lv2) + 4 JEV+GPT-6 games (Lv5, Lv6, Lv7 x2) as the main comparison, plus 1 separate Lv8 stress-test game (JEV+GPT-6 only, vision-advantaged opponent). Micromanagement: 35 SMAC-Hard maps x 3 episodes x 2 methods = 105 episodes per method (also reported for a 33-map subset excluding 2 local development maps, 99 episodes). JEV decision counts: 1,020 (JEV-only full game) vs. 737/583/701/850 (four combined full games); response-latency table pools 1,023-9,743 JEV responses and 0-62 GPT-6 planning responses per setting/method (Table 5).

## Test-set exposure
Not a static benchmark with public/pretraining exposure concerns in the usual sense — these are live, freshly-played StarCraft II games/episodes against the built-in AI on 2026-09-22, so recorded as "new."

## Cost and latency
Table 5 (response latency, pooled): JEV macro P50/P95 = 0.406/0.579 s (JEV-only, n=1,023) vs. 0.422/0.531 s (JEV+GPT-6, n=2,905); JEV micro P50/P95 = 0.485/0.688 s (JEV-only, n=8,189) vs. 0.500/0.594 s (JEV+GPT-6, n=9,743); GPT-6 planning P50/P95 = 27.601/36.492 s (macro, n=62) and 37.172/43.725 s (micro, n=35). Table 6 (cost per episode): macro JEV-only $0.1069/episode (all JEV, $0 GPT-6); macro JEV+GPT-6 $3.7103/episode ($0.1499 JEV + $3.5604 GPT-6, "planning contributes 96.0% of the total"); micro JEV-only $0.0448/episode; micro JEV+GPT-6 $0.1486/episode ($0.0588 JEV + $0.0898 GPT-6). "JEV's recorded macro usage costs approximately USD 0.21 per 1,000 responses" (§4.6). hardware_or_provider: standard-API-equivalent cost estimates at provider rates "on September 22, 2026"; GPT-6 runs used via Codex, so "the reported amount is an equivalent API estimate" (§4.6, "Accounting basis").

## Calibration
Not applicable / not reported — this is an action-selection/game-outcome paper, not a probability-calibration study.

## Cascade / escalation
Not a confidence-gated cascade; JEV always acts, GPT-6 plans on a fixed ~60-game-second interval plus relevant events (§3.3) — a scheduled/periodic two-tier system rather than a confidence-triggered escalation. No cascade_result field applicable in the REFLEX sense.

## Robustness / stress tests
- Lv8 stress test (built-in opponent with vision/information advantage): JEV+GPT-6 loses at 10:14; at 5 minutes the agent's army resource value is 900 vs. opponent's 1,525, and it never issues an attack command (§4.2, "Stress test with privileged vision").
- Micromanagement fine-grained behavior counts: 2,629/2,662 (98.8%) unit decisions with ready weapon + in-range target choose an in-range attack (sensible default), but only 63/930 (6.8%) decisions with long cooldown + melee pressure + a separating movement option choose to separate ("the controller often fails to use movement during downtime") (§4.5, "Shared intent does not resolve all coordination"). Healing-target conflicts: 500 healing rejections for already-targeted allies, 243/378 (64.3%) repeated decisions re-select a previously rejected target.
- Attack/retreat reversal robustness: JEV-only full game shows 5 attack-to-retreat reversals within 2 game seconds; none of the 4 combined-system wins shows such a reversal (§4.5, "Maintaining an army objective").

## Code and data availability
"Code is available at https://github.com/sc2musa/Jev_Star" (Abstract). code_available = "yes (https://github.com/sc2musa/Jev_Star)".

## Limitations (paper's own, from "Discussion and limitations")
- "The comparison remains observational. The standalone and combined controllers also differ in candidate descriptions and execution handling, and the macro opponents are not matched. Four successful macro games and three micro episodes per map cannot establish broad reliability."
- "A controlled next experiment should use the same curator and seeds with the planner enabled or disabled" — planning's isolated contribution is not established.
- "The scope is also restricted: one macro race and matchup, one macro map, a custom starting-worker count, centralized micro observations, and separate macro and micro implementations. Low battle win counts remain a material weakness."
- "Inexpensive JEV inference does not make the combined system's planning free... GPT-6 dominates observed full-game cost."

## Notes on JEV-Star vs. other papers
This paper uses the vendor's actual Jev (spelled "JEV" in this paper's typography) at version "JEV 1.13," consistent with jev-1.13 used in deng2026jev and wu2026reflex (jev-1.13.0). It is paired with GPT-6 Astra as a persistent planner, not evaluated as a standalone decision-quality benchmark against other LLMs — the central comparison is JEV-only vs. JEV+GPT-6, an ablation of the paper's own two-tier architecture, not a leaderboard-style multi-vendor comparison.
