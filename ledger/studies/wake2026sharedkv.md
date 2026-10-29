# wake2026sharedkv

arXiv 2610.07327 (v1, 05 Oct 2026). "SharedKV-BT: Node-Local Typed Decisions for Behavior-Tree Agents". Full text: fulltext/2610.07327.html and .txt. Extractor batch V08.

**Authors and affiliation.** Naoki Wake and Justin Wagle, Microsoft (title page). Industry.

**Task and data.** Agent control. Robot manipulation (Robosuite Stack, full PickPlace, NutAssemblySquare, Door; 30 episodes each), mobile navigation (RoboCasa NavigateKitchen, seeds 0-9), computer use (WindowsAgentArena Clock, Notepad, File Explorer; four runs each), and a controlled Adaptive PickPlace variant with 120 saved pre-execution states (seeds 0-29, rotated object schedule, manually specified structured states) plus 30 closed-loop episodes per condition (Sections III-C, III-E).

**Decision model.** SharedKV-BT: a Jev-style typed-decision interface for behavior-tree nodes. A task-state prefix is encoded once and its key-value cache is reused to score complete candidates for each field in one batch; fieldwise argmax gives the decision. Score is the mean token log-probability of the candidate; the paper says the scores rank candidates and are not treated as reliable probabilities of correctness (Section III-A). It is therefore a typed candidate-scoring model without calibrated probability output; included because it implements the typed-decision interface (state, declared fields and candidates, scoring in parallel, no free text). Base model Qwen2.5-3B-Instruct for all primary experiments; Qwen3-4B non-thinking for a robustness check (Section III). No revision hash given. The hosted Jev is cited as the interface source [7] but is not evaluated.

**Comparators and tuning parity.** Autoregressive (AR) unconstrained generation; prompt-matched constrained AR (greedy with token trie, same prefix, field suffix and candidates); sequential scoring; full-prefix batch scoring; global-interface Shared-KV exposing all five skills, four objects, four destinations; AR-flat, SharedKV-flat, AR-BT, SharedKV-BT; fixed-score policy replay (Sections III-A, III-D). Same model, observations, actions, skills, initial states and evaluator across conditions. The constrained AR baseline uses Python-level token-trie masking, not an optimized grammar decoder (Section VI). Authors note that masking stage-invalid choices in the global interface would give the same routing effect as node-local interfaces (Section V).

**Reference labels.** Simulator postconditions (Boolean from simulator state), platform evaluators in WindowsAgentArena (task_outcome); decision correctness in Adaptive PickPlace comes from a manually specified deterministic schedule of required skills and objects (synthetic) (Sections III-C, III-E).

**n, sampling, intervals.** Latency: two warm-up and ten measured trials; matched-batch values mean plus or minus 95% confidence intervals over ten runs (Table I). End-to-end values are means without intervals. Adaptive PickPlace counts are descriptive because typed states repeat across seeds (Section III-E, Fig. 4). Small closed-loop samples (10 seeds for Stack and NavigateKitchen; 10 for Qwen3-4B check). No inferential tests reported.

**Exposure.** Simulated environments built by the authors' configurations; no static benchmark answer key. Recorded as new.

**Cost and latency.** One NVIDIA RTX 2080 Ti 11 GB, FP16, PyTorch 2.7.1+cu126, Transformers 4.57.6, CUDA 12.6. End-to-end Shared-KV 99.8 ms vs constrained AR 413.8 ms on Stack (4.15 times), 121.4 vs 286.0 ms NavigateKitchen (2.36 times), 134.2 vs 318.8 ms Clock (2.38 times) (Table I). Cache-reuse-only speedups 2.09, 1.75, 1.29 times; speedup 0.51 with two candidates and 4.29 at 283 prefix tokens (Section IV-A). Peak memory comparable. Adaptive PickPlace per-decision latency 128 ms vs 316 ms global vs 625 ms constrained AR (Section IV-B).

**Calibration.** None; the paper declines to treat scores as probabilities (Section III-A, IV-F).

**Cascade or escalation.** None. BT retry and recovery: MAP_REPLAN chosen in 10 of 10 injected-failure episodes, recovery restored first-goal progress in one (Section IV-E). ABSTAIN candidate experiment: rejected 28 of 30 invalid cases, correct value in 17 of 30 valid cases; AR 51/60 vs Shared-KV with ABSTAIN 45/60 (Section IV-F).

**Option-name, order, cardinality, robustness.** Candidate order changed selected Acquire values in 46/120 node-local states and all 120 global states across seven fixed orders; node-local correct 90-113/120 vs global 14-90/120 (Section IV-B). Complete-candidate scoring matched 27/28 labels vs 14/28 for first-token scoring on observed first-token collisions (Section IV-F). Constrained AR selected different valid candidates than Shared-KV on NavigateKitchen and Clock (Section IV-A).

**Code and data availability.** No repository or data URL in the text (a supplementary evidence file is mentioned in Section IV-D, no link).

**Authors' limitations (Section VI).** Simulated robot domains and three fixed computer-use tasks; no unseen tasks, hardware or real perception; one injected planner failure; Qwen3 check limited; manually specified structured states; repeated states; seven permutations only, closed-loop order robustness untested; predefined BTs, candidate sets, compatible combinations and postconditions assumed; rejection when no candidate is valid and automatic compatibility enforcement unresolved; some postconditions use simulator-internal state; speedups depend on models, hardware, prompts, implementations.
