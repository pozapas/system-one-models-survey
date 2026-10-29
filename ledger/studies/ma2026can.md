# ma2026can — Can Jev be Your Q or Policy in Reinforcement Learning?

- arXiv: 2610.11692v1 [cs.LG], 8 Oct 2026, CC BY 4.0 (header). Full text: fulltext/2610.11692.html and .txt.
- Authors (header): Yi Ma (Shanxi University), Tianpei Yang (Nanjing University), Yaodong Yang (The Chinese University of Hong Kong), Weixun Wang (Independent Researcher), Hongyao Tang (Tianjin University). Affiliation type: academic.
- Code and data: no repository URL. Reproducibility Statement says "The accompanying source files contain the figure inputs and plotting scripts" and direct-model trajectories are retained (Reproducibility Statement, after Section 6). code_available coded "partial".
- Application paper, not mainly an accuracy study. Most results are bar charts (Figures 2 to 5) with no numeric labels in the text; only Table 2 and a few appendix sentences give numbers.

## Task and data
Use of a frozen decision model inside reinforcement learning (Sections 3 and 4). Nine MiniGrid tasks (DoorKey at three sizes, Empty, FourRooms, two MultiRoom variants, SimpleCrossing, LavaGap) and three Atari games (Seaquest, Freeway, SpaceInvaders) (Section 5, Experimental setup). Jev is used as (1) reference policy (Jev-BC, Jev-PEX, Jev-Mixed Sampling), (2) exploration judge (Jev-Gate, Jev-Bonus), (3) replay rater (Jev-Reweighted Replay), plus a subgoal channel in Appendix E.

## Decision model, exact version
"The experiments use jev-1.13.0 as a fixed external decision model" (Appendix A). Query primitive choice; MiniGrid 7 actions; Atari 18/3/6 actions; rating options five ordered levels plus unknown; exploration gate GREEDY/RANDOM (Appendix A, Table 3). Jev stays frozen. Jev takes the most probable action in pure-Jev evaluation (Section 5.1). Run dates not stated.

## Comparators and tuning parity
- Direct control: Qwen3-8B served by vLLM, non-thinking, temperature 0, 48-token limit, JSON action label, same structured inputs, questions, legal-action descriptions and seeds (Section 5.1, Appendix C). Inputs may carry information the RL student does not get (Section 5).
- Learning: DQN baseline and TD-error PER replay baseline under a fixed interaction budget (Section 5, setup). Baseline tuning not described in the main text.

## Reference labels
Environment outcomes (episode success, native return); task_outcome.

## n and intervals
MiniGrid: 50 fixed evaluation seeds (700000 to 700049), Wilson 95% intervals in Figure 2; Atari: 5 fixed seeds, mean return with SEM; learning results mean and SEM across three training seeds (some methods five seeds); fixed-experience diagnostics 100 evaluation seeds (Section 5, Appendix C). Table 2: 50 paired environment seeds per task, no intervals.

## Results with numbers in text
- Jev matches or exceeds Qwen3-8B on all nine MiniGrid tasks; Atari mixed (Section 5.1, Figure 2, values only in the figure).
- Table 2 (pure Jev, success with vs without engineered navigation features): DoorKey-8x8 100/100, MultiRoom-N2 100/90, FourRooms 96/40, MultiRoom-N4 100/38; episode lengths in the same table.
- Subgoal channel (Appendix E.2): Seaquest 382.7 (Jev-weighted goals) vs 345.3 uniform; Freeway 17.2 vs 19.7; Montezuma runs: 77.1% of goal selections go to the key, completed twice in 481,153 selections; overall selected-goal completion 0.36% vs 1.98% for uniform selection.
- RL gains (Jev-BC, PEX, Gate, Bonus, Reweighted Replay) beat DQN on selected tasks, none uniformly best; Jev replay does not consistently beat PER (Sections 5.3 to 5.5, figures only).

## Test-set exposure
Simulated environments with fixed seeds; no static test set. MiniGrid and Atari are public, so exposure of environment descriptions is possible but unmeasured; coded "new" (fresh episodes).

## Cost, latency, calibration, cascade
Not reported with numbers (Section 2.2 defers latency and cost to Appendix A, which lists only interface settings). No calibration analysis, no cascade, no option-name or language robustness test. Jev answers are called "calibrated" in the introduction as a premise, not measured here (Section 1).

## Paper's own limitations
Inputs to Jev may carry information the student lacks; high success with engineered navigation shows use of supplied route structure (Finding 2); ranking of methods varies by task, no configuration uniformly best (Sections 5.3, 5.4); sparse-reward tasks remain unsolved; the subgoal channel does not obtain effective temporal guidance from Jev (Appendix E.2); cardinal value use excluded (Section 3.1). Judgments are task- and input-dependent, no real-world safety claim (Ethics Statement).
