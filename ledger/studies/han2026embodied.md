# han2026embodied

arXiv 2610.16238v1 (cs.RO), 12 Oct 2026. "Embodied Skill Bench: Benchmarking How Well Agents with Embodied Skills Perform on Physical Tasks."
Authors: Zhi Han, Zihan Guo, Chenxi Zeng, Zicai Cui, Yue Xin, Ming Zhou, Dongzhan Zhou, Weinan Zhang, Yang Li (Shanghai Jiao Tong University; Shanghai Artificial Intelligence Laboratory; Sun Yat-Sen University; Jilin University; Beihang University). Affiliation type: academic. (title block)

Scope: the benchmark paper evaluates agents with embodied skills. Jev appears only as one component, a single "Jev waypoint execution skill" (RQ3, Table 3, Appendix C). I extract only that arm. Evaluation of Jev is peripheral: the unit under test is the GPT-6-astra agent plus Jev, not Jev alone.

## Task and data
- LIBERO-Pro "Clean100": 100 perturbed task cases (language, object, task, swap perturbations; 25 each) across four domains L10/Goal/Object/Spatial (24, 28, 24, 24 tasks). Closed observation-action loop; success, actions, tokens, time recorded. Environment seed 26. (Table 1 to 3 captions, Sec. 5)
- Reference: task-outcome (simulator official success condition). Reference label type task_outcome.
- Items are public LIBERO-Pro tasks (Zhou et al. 2025); no contamination check.

## Decision model and configuration
- Jev 1.13.0 (as stated in App. C.2) used by GPT-6-astra/medium via Codex CLI v0.148.0. The skill follows EmbodiedJev's waypoint controller: for each local decision Jev chooses one option for each of six motion channels ({negative, hold, positive}) and the gripper ({open, hold, close}); executor uses the returned choice, probabilities are recorded but not used. 40-waypoint budget, 10,000 simulator steps, 5,400-second rollout timeout. Jev skill is evaluated separately from the 250-skill repository. Run dates not given. (App. C.2)

## Comparators and tuning
GPT-6-astra with no skill (native control), with skills (skill-only), and Agent-Directed Reuse (ADR). Same agent, tasks and seed. No tuning stated for the Jev condition beyond the described wrapper (developer instruction and plan schema designed by the authors; the waypoint-controller design follows an existing project). (Table 3)

## Results (Table 3, GPT-6-astra, Clean100 seed 26)
No skill: SR 92.0%, 16.59 actions, 2,300.6k tokens, 20.52 min. With skills: 61.0, 2.24, 563.5k, 3.40. With Jev skill: 81.0 (L10 58.3, Goal 92.9, Object 79.2, Spatial 91.7), 20.90 actions, 1,142.0k tokens, 8.74 min. ADR: 85.0, 12.87, 1,976.3k, 18.09. Abstract claims "50% fewer tokens and 57% less time" for Jev relative to native control (1,142.0 vs 2,300.6; 8.74 vs 20.52). Token counts include GPT-6 tokens (in the case study 431.3k GPT-6 tokens and 201.5k Jev tokens). Single seed, single run, no confidence intervals or repeats reported.

## Uncertainty
None reported (one seed, one run per setting, mean values with failures included).

## Calibration
None.

## Cascade or escalation
Not a cascade in the confidence sense; GPT-6 delegates local motion choices to Jev and keeps planning and recovery.

## Cost and latency
Mean elapsed minutes and recorded tokens per task (including failures); Jev token counts included in tokens. No dollar cost; no per-call Jev latency.

## Robustness
Perturbation-level and domain-level success only (language, object, task, swap). No option-name or cardinality tests for Jev.

## Code and data
Code at https://github.com/HanZhi306/EmbodiedSkill-Bench (abstract).

## Authors' limitations
No dedicated limitations section found; text notes multi-stage tasks remain challenging for the Jev configuration and that preserving native-control success remains challenging.
