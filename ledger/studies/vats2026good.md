# vats2026good — Good Judgment, Bad Advice: Decision-Model Controllers Raise Agent Cost Without Improving Success

arXiv:2610.24649v1 [cs.AI], 17 Oct 2026. HTML retrieved 2026-10-28 (fulltext/2610.24649.html, .txt). Coder: batch V16.

## Authors and affiliation

Naman Vats (sole author); contact email at bitmesra.ac.in (BIT Mesra); no affiliation line in the extracted text, so academic is inferred from the email domain. Independent of TypeSafe.

## Task and data

Pre-specified, placebo-controlled study of whether a typed decision model consulted at four deterministic decision points (T1 repeated failure, T2 no progress, T3 finish request, T4 checkpoint every 10 steps) makes a Claude Sonnet 5.5 terminal agent cheaper without hurting success (§3). Terminal-Bench 2.1 (89 tasks pinned by content digest; two tasks with timeouts over 60 min and one refusal excluded). Calibration on 30 tasks, split into 8 development and 21 held-out tasks (14 easy, 3 mid, 4 hard). Evaluation: 21 tasks x 5 arms x 3 attempts = 315 trials; caps 60 steps and $1.00 per trial (§3 Protocol). Questions: Q-progress (continue, investigate, recover, abandon) and Q-finish (finish, verify).

## Models and versions

Jev: typesafe/jev-1.13, served snapshot jev-1.13-20260917, choice questions with shared option descriptions (§3 Controllers). Small LLM: Claude Haiku 5.5, reasoning disabled, JSON schema. Rules controller and a placebo (samples Jev's development-phase choice frequencies: Q-progress continue 0.625, investigate 0.125, recover 0.25, abandon 0; Q-finish finish 0.652, verify 0.348). Reasoning model Claude Sonnet 5.5 (effort high, no temperature parameter). Harbor 0.24.0, Daytona sandboxes, OpenRouter hosts (94.6% Claude Platform on AWS, 5.4% Azure). Run dates not given beyond the snapshot id.

## Comparators and parity

Same agent loop, same caps, same guards (G1 to G4) for all five arms; Jev and the small LLM receive the same state and option descriptions. Arm order randomized within task-attempt blocks. Parity: same prompt/questions. Nothing was tuned on evaluation data; development runs only supplied the placebo distribution (§3).

## Reference labels

Task outcome: Terminal-Bench verifier reward (1 = pass) (§3). Offline decision quality is labeled with the trial's grader outcome, not the counterfactual outcome of another decision (§6).

## n, sampling, intervals

21 held-out tasks, 3 attempts each, 63 attempts per arm; paired bootstrap resampling tasks 10,000 times for percentile 95% intervals; Holm adjustment across C2 to C4; C1 non-inferiority margin of -10 pp (one-sided lower bound -9.5 pp) (§3 Statistics, §4.1). Offline replay n = 53 Q-finish and 72 Q-progress states (Table 3). Pass-rate intervals about +/-11 to 13 pp (§6).

## Test-set exposure

Terminal-Bench 2.1 is a public benchmark from 2026 (not pre-2026 strictly; contributors cited as 2026). Coded public-pre-2026 with the caveat that the benchmark post-dates 2025. No contamination analysis. The Jev decisions are on logged agent transcripts, not benchmark answers.

## Cost and latency

Jev 1.13 priced at $0.042 per million input tokens; about $0.00008 per decision; 0.52 s per decision and 0.11% of spend; small LLM 1.46 s and 0.47% (§1, §4.4). Cost per attempt: native $0.177, rules $0.191, small LLM $0.213, Jev $0.206, placebo $0.156 (Table 1). The authors' own total spend is also reported in §3 (not coded in the ledger).

## Calibration

Jev ranked finish requests best (AUROC 0.78) but was miscalibrated toward "not done": mean P(finish) 0.50 when 87% passed; ECE 0.37 (rules 0.55, small LLM 0.70); chose verify for 29 of 53 finish requests (Table 3, §4.3). Binning for ECE not described in the extracted text. No recalibration was applied; a base-rate-aware threshold is suggested as a follow-up.

## Cascade or escalation

Not a model cascade; Jev acts as an advisory controller. Pass rate 73.0% in both native and Jev arms, cost 1.19 times native, no abandon ever chosen; placebo matched pass rate (71.4%) at ratio 0.98 (Tables 1, 2).

## Robustness

Per-task results (App. C), leave-one-out ratio 1.16 to 1.25, 15 of 21 tasks costlier (§4.4). Calibration-phase states show the same AUROC pattern (0.77 for Jev, 111 states). No option-name, order or language tests; one agent, one decision model.

## Code and data

https://github.com/namanvats/decision-model-controllers (harness, configurations, analysis scripts); config fingerprints and lockfile hashes recorded per trial.

## Own limitations (§6)

Only 21 held-out tasks, mostly easy; wide pass-rate intervals; one reasoning model, one loop, Jev 1.13 with the authors' option wording; pre-specified open-weight replication not run; nondeterminism and unpinned hosts; placebo distribution from a small development sample (8 progress, 23 finish decisions) with zero abandon mass; strata from two calibration attempts; offline labels use realized outcomes. App. D lists deviations from the pre-specified plan.
