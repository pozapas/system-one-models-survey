# Zhang (2026), "Jev-Mobile: Jev as an Executor for Mobile GUI Agents"

## Identification
- arXiv 2609.30186v1 [cs.AI], 24 Sep 2026 (header). License CC Zero. Full text fulltext/2609.30186.html and .txt.
- Single author Linghua Zhang, email lz101@rice.edu (byline); no affiliation line, but the email domain indicates Rice University. affiliation_type = academic (inferred from email domain).

## Task and data
- Mobile GUI agent: a VLM (Qwen3.8-Max, OpenRouter ID qwen/qwen3.8-max-0902) specifies local goals and exact text, Jev repeatedly selects an action ID from program-enumerated accessibility-tree candidates or returns DONE/BLOCKED, with re-observation after each action (Sections 3.1 to 3.3).
- Evaluated on the full AndroidWorld suite with its task initialization and independent terminal evaluators (Section 5.1). Number of task instances not stated in the text. Single run per system; no repeats or seeds stated.

## Decision model
- Jev as a remote typed Decisions service; Jev receives only the textual tree, current local goal, prior actions in the delegation and candidate descriptions (Section 2). No version string, run date or endpoint identifier reported.

## Comparators and tuning parity
- Step-wise VLM (shared general VLM chooses each action) and SeeAct-V (same VLM plus UI-TARS-1.5-7B as visual grounder, substituted for UGround, so an adaptation of the published controller) (Section 5.1). "The systems differ in observation and action interfaces ... their outcomes characterize complete systems rather than the isolated effect of Jev" (Introduction). No tuning budget stated for any system; Jev-Mobile not compared with a small VLM replacing Jev (Limitations).

## Reference labels
- AndroidWorld terminal device-state evaluators (task outcome). Hidden task state kept out of prompts.

## n, sampling, intervals
- Success rate over all evaluated task instances; time and cost metrics conditional on each system's own successful trajectories, so cohorts differ between systems (Section 5.2). No confidence intervals.

## Results (Table 1)
- Success 0.84 Step-wise VLM, 0.78 SeeAct-V, 0.79 Jev-Mobile. Mean total time per success 197.21, 162.63, 132.67 s. Executor time 94.30, 12.37, 5.16 s. Mean all-model API cost per success $0.273694, $0.193207, $0.072744. Executor cost summed over successful trajectories $0.694774, $0.030579, $0.013091.
- Text: 32.7% lower total time and 73.4% lower model API cost than Step-wise VLM; execution-model time down 94.5% (Section 7).

## Calibration, cascade, robustness
- None reported. No probability analysis. Failures are diagnosed as coverage / selection / handoff but no numbers in the main text.

## Cost and latency
- Reported as above, from API charges and online wall time including planning, waits and retries; no hardware or network details.

## Test-set exposure
- AndroidWorld is a public benchmark (2025); no contamination check.

## Code and data
- None stated.

## Paper's own limitations (Section 8)
- AndroidWorld only (no web); two baselines; no small-VLM replacement for Jev; depends on accessibility tree (visual-only targets unreachable); ASCII-only text input; long histories may need compaction.
