# sautenkov2026uavswarmagent

arXiv 2610.32559v1 (cs.RO), 23 Oct 2026. "UAV-SwarmAgent: Scalable Multi-UAV Reconnaissance and Task Allocation via Code Generation and Vision-Language Reasoning." Authors Oleg Sautenkov, Yasheerah Yaqoot, Muhammad Ahsan Mustafa, Grigorii Kalinin, Dzmitry Tsetserukou (Intelligent Space Robotics Laboratory, Skolkovo Institute of Science and Technology, Moscow) and Chih-Yung Wen (AiRo Lab, Hong Kong Polytechnic University). Affiliation type: academic. Late-breaking report; no human participants. (title block, Sec. 1)

Study type: application. The decision model is a component (onboard verifier), not the object of study. Weak fit: no accuracy, calibration or comparison for the verifier is reported on its own; only downstream frame precision and mission outcomes. Flagged in the report.

## Task and data
- Simulated multi-UAV reconnaissance: an operator sentence is turned into per-UAV routes by a ground-station LLM agent writing Python; each UAV scores camera frames along its route with the verifier. (Sec. 3)
- Maps: satellite maps of rural settlements from the UAV-VLA benchmark (about 1.4 x 1.4 km each) plus five coastal scenes from public web map imagery; incidents are synthetic and composited into the target map: structure fire (30 maps), wildfire (5), vehicle collision (5), oil spill (5). (Sec. 4)
- Mission counts: scaling study 30 fire maps x N=1..5 with gemini-3.8-flash = 150 missions; cross-model study N=3, every scenario with 3 models = 135 missions (30 Gemini fire missions shared); 255 missions reported. (Sec. 4)
- Success rule: at least one reported frame whose 128 x 128 px footprint contains the incident centre (overlap for larger incidents). Precision is the share of reported frames meeting the same rule. Reference is therefore synthetic (known composited incident location). (Sec. 4 Measures)
- Test data are new composites but built from public map imagery; thresholds and verifier questions were chosen on the benchmark maps with no held-out set, and for collision and oil spill the questions were "later refined and the Gemini missions repeated". (Sec. 4, 6)

## Decision model
- Valen-Preview-0923, a 2B-parameter vision-language decision model returning the probability of "yes" for a scenario-specific question in a single forward pass without generating text; scores a frame every 16 m of route; a frame is reported when probability exceeds a per-scenario threshold tau (0.55 to 0.74). Run locally on a laptop GPU (RTX 4050, 6 GB); Jetson deployment stated as possible, not tested. No revision hash, no run dates. (Sec. 3.4, 4)
- Planner LLMs: gemini-3.8-flash, gpt-6.1-sol, qwen3.8-max (through a gateway). (Sec. 4)

## Comparators and tuning parity
No comparator for the verifier. Planner models compared at the mission level only (41/45, 44/45, 42/45 success). (Table 1)

## Results (verifier-relevant)
Median frame precision at N=3: structure fire 0.68, wildfire 0.57, vehicle collision 0.74, oil spill 0.95 (the pooling across the three planner models is not stated). Median 37 reported frames per mission. Mission success 244 of 255 (95.7%). Of 11 failed missions, 5 were planning failures and 6 were verifier misses (drone overflew the incident). No false-alarm rate per frame or recall is given as numbers. No confidence intervals for success or precision; bootstrap intervals (10,000 resamples of maps) are for the time-scaling analysis. (Sec. 5.1, 5.3, Table 1)

## Cost and latency
Agent time median 152 s (Gemini), 180 s (GPT), 135 s (Qwen) per mission, including planning, simulation and onboard inference; verifier latency alone not reported. (Table 1)

## Calibration
Not evaluated. Probabilities are thresholded; threshold values per scenario not tabulated beyond the range.

## Cascade or escalation
Not applicable (single stage, though frames above tau are escalated to the operator in the design).

## Robustness
None for the verifier. Each configuration was run once.

## Code and data
No repository or data link in the paper text.

## Authors' limitations (Sec. 6)
Simulation with synthetic incidents and a kinematic flight model without wind, batteries or obstacles; verifier questions and thresholds chosen on the benchmark maps with no held-out set; each configuration run once; fixed operator sentences; no human participants.
