# ling2026when — When Faster Decisions Do Not Make Better Agents: An Empirical Study of Jev in Agent Workflows

- arXiv: 2610.13092v1 [cs.AI], 9 Oct 2026, license CC BY-NC-ND 4.0 (header). Full text: fulltext/2610.13092.html and .txt.
- Authors (header): Yuchen Ling, Zhenyu Chen, Chunrong Fang (Nanjing University); Shengcheng Yu (Technical University of Munich). Affiliation type: academic.
- Code: "The experimental code is available at https://anonymous.4open.science/r/jev-emp-5BF4/" (Section 1). An anonymised link; coded yes with that URL.

## Task and data
Jev as the action selector inside five existing LLM agents on two benchmarks (Section 4.2).
- ALFWorld text environment, all 134 tasks of valid_unseen; agents ReAct and Reflexion with variants B (baseline LLM generates commands), J (Jev selects an admissible command or THINK), C (LLM-Choice: an LLM with Jev's candidate list and instructions) (Table 1).
- AndroidWorld, text-based UI observations, one fixed parameter instance for each of 116 task types; agents T3A, AutoDroid (app memory disabled), Droidrun FastAgent (Direct mode), variants B and J (Table 1).
- Three runs per configuration with seed 0 on the same tasks: 4,500 task executions in total (Abstract; 134 x 3 x 6 plus 116 x 3 x 6 = 4,500; ALFWorld success denominators 402, AndroidWorld 348, Table 5).

## Decision model, versions
"All LLM decisions and auxiliary generation use gpt-5.6-luna, and Jev decisions use jev-1.13.0" (Section 4.2). One logical Jev request per decision step; surrounding observation, history and execution mechanisms retained. Run dates not given. Hosted API.

## Comparators and tuning parity
- B: original LLM decision strategy of each agent (gpt-5.6-luna). C control (ALFWorld only): same LLM with Jev's candidate list. Two interface differences are disclosed: ALFWorld baselines generate commands without candidate lists, and FastAgent-J executes one tool per step while FastAgent-B can emit several (Section 4.2).
- Budgets matched within each family (AndroidWorld 600 s and ceil(10c) steps; ALFWorld ReAct 49 steps, 600 s; Reflexion up to 10 trials of 49 steps, 6,000 s); cross-family comparisons reflect different budgets (Section 4.2).
- No prompt tuning for either side described.

## Reference labels
Benchmark official evaluators (task success; AndroidWorld official score); task_outcome.

## Intervals
Mean and sample SD across three runs; paired J-minus-control differences with 95% task-cluster bootstrap intervals (20,000 replicates, tasks resampled with their three runs together, seed 20261006), pointwise, no multiplicity adjustment (Section 4.3, Appendix A.2).

## Main results
- Success (successes/executions; Table 5): ReAct-B 392/402 (97.51), ReAct-J 386/402 (96.02), ReAct-C 390/402 (97.01); Reflexion-B 401/402 (99.75), -J 394/402 (98.01), -C 394/402 (98.01); T3A-B 200/348 (57.47), -J 154/348 (44.25); AutoDroid-B 65/348 (18.68), -J 57/348 (16.38); FastAgent-B 174/348 (50.00), -J 111/348 (31.90).
- Paired success differences J minus B (Table 10): ReAct -1.49 [-4.48, +1.24]; Reflexion -1.74 [-3.98, +0.00]; T3A -13.22 [-17.82, -8.62]; AutoDroid -2.30 [-5.46, +0.86]; FastAgent -18.10 [-26.44, -9.77]; J minus C: ReAct -1.00 [-3.23, +0.75], Reflexion +0.00 [-1.00, +1.00].
- Decision level: Jev cuts mean decision cost by 66.1% to 78.4% and time by 73.9% to 81.5%; decision times fall from 4.13 to 8.13 s down to 1.04 to 1.75 s; tokens per decision rise 53.5% to 134.9% (Section 5.2).
- Task level: cost falls 50.9% (ReAct), 32.6% (Reflexion), 17.1% (T3A), 68.8% (AutoDroid), 43.0% (FastAgent); time falls 47.6%, 37.8%, 10.6%, 5.7% and rises 0.7% for FastAgent (Section 5.2). Cost per delivered success rises 7.7% for T3A (68.70 to 73.97 mUSD, interval spans zero); FastAgent time per delivered success 239.4 to 377.8 s (Table 2c).
- Reflexion recovery of initial failures: J 11/19 vs B 25/26 vs C 23/31; final success J 394/402 vs B 401/402 (Table 4).
- Trace coding of 251 executions, mean per-label Cohen kappa 0.867 (Section 5.3, Table 3).

## Cost accounting
Prices per million tokens: LLM input $0.20, LLM output $1.20, Jev input $0.042, Jev output zero (Appendix A.1). Costs are token-price estimates, not invoices; retry adjustments and imputed usage add uncertainty (Limitations).

## Test-set exposure
ALFWorld (2021) and AndroidWorld (2025) are public benchmarks; actions are generated online so item answers are not memorised labels; unseen split used. Coded public-pre-2026.

## Calibration, cascade, robustness
No calibration analysis (probabilities not used for decisions beyond argmax); no cascade; no option-name or language tests. The Discussion suggests calibrated confidence as future work (Section 6).

## Limitations (paper)
Selected agent families, language-based observations and bounded action interfaces only; three repetitions on fixed instances with a shared seed measure execution variability, not variation across newly sampled environments; system-level comparisons not attributable to Jev alone; cross-family budgets differ; latency and cost depend on model versions, service conditions and experimental prices (Limitations).
