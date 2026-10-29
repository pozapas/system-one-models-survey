# Liu et al. (2026), "RoboICL: Embodied In-Context Learning with GPT-6 Astra"

## Identification
- arXiv 2609.34261, 28 Sep 2026 per batch file. Authors: Fangcheng Liu, Yeqing Shen, Anda Cheng, Weishi Mi, Chao Tang, Chenyuan Liu, Yushun Xiang, Tingguang Li, Yong-Lu Li, Yehui Tang (byline); affiliations Samsung Robotics eXperience, Samsung Research Beijing, Shanghai Jiao Tong University. affiliation_type = mixed.
- Code: https://github.com/Mosi-AI/RoboICL (Abstract).

## Scope of the Jev component
- RoboICL is a robot in-context-learning framework around GPT-6 Astra. Jev is only an optional, minor component, evaluated in one subsection (Section 4.5, Appendix C.2) and a clause of the Abstract and Conclusion: "On two development tasks, optional Jev-gated action reuse reduces GPT-6 Astra calls by 33-48%" (Abstract). The Jev result is the only part relevant to the ledger; the main RoboICL benchmarks (RoboDojo, real robot) evaluate GPT-6 Astra without any decision model and are not extracted.
- This is a borderline inclusion. Jev is not scored on decision accuracy; it is a gate whose effect is measured through downstream task success, GPT-6 Astra call counts, tokens, wall time and gate latency, against the same pipeline without the gate. Included because a measured quantity exists for Jev against a stated reference (task outcome in the same simulator).

## Task and data
- Zero-shot RoboDojo simulator study on two tasks, Align Blocks and General Pickup, standard layouts 0-4, five episodes per task and condition, 20 scored outcomes in total (Section 4.5, Table 6). Success is a progress score of 100 (scores in this panel are 0 or 100); a failed episode runs the 200-step limit (Table 6 caption). Reference = task outcome (simulator success).
- The gate configuration "was selected on these layouts, making this a development-set evaluation" (Section 4.5); "Jev is evaluated on its development layouts. ... held-out Jev evaluation are the next tests" (Section 5). So test_set_exposure = unclear (selected on test layouts).

## Systems
- Pure GPT-6 Astra (xhigh reasoning, same task prompt, cameras, action constraints, 20 predicted actions per request, up to five executed per segment, 25 interaction-memory slots) replans after each segment. GPT-6 Astra+Jev: Jev may approve one further five-action segment using proprioception, execution tracking and the plan note (no RGB); Jev "controls action reuse without generating actions" (Section 4.5). The Jev model identifier and version are not reported ("Jev AI (2026) developer documentation" only), so version_pin = not reported. Run dates not stated (references accessed September 2026). Question wording, thresholds and vote rule are not described in the main text.
- Tuning parity: the Jev gate was configured on the same layouts used for reporting; the pure condition has no gate parameters. Compared pipelines share the task prompt and settings.

## Statistics
- Counts over five layouts per task; single run per layout; no intervals or tests. Paired wall time summed over layouts successful in both conditions (n = 1 for Align Blocks, n = 4 for General Pickup) (Table 5).

## Cost and latency
- GPT-6 Astra requests fall from 181 to 121 (Align Blocks) and 116 to 60 (General Pickup); provider-reported tokens fall from 9.53 to 5.08 million and 4.95 to 1.39 million; "Jev adds approximately 0.86 seconds per gate call" (Section 4.5, Table 7). Wall time falls 36.1 percent on the four jointly successful General Pickup layouts. Hardware for the simulator and Jev route not stated.

## Calibration, cascade, option-name, robustness
- No calibration analysis. The Jev gate is an accept-or-replan cascade (reuse an existing action segment instead of calling GPT-6 Astra again); Table 7 reports Jev votes and reused steps (113 votes, 315 reused steps on Align Blocks; 53 votes, 140 reused steps on General Pickup). Success tradeoff: General Pickup 4/5 to 5/5, Align Blocks 3/5 to 2/5. No option-name or cardinality tests.

## Authors' stated limitations (Section 5)
- Experiments cover GPT-6 Astra, RoboDojo and three real-robot tasks; Jev evaluated only on its development layouts; broader models, hardware platforms and held-out Jev evaluation are future work.
