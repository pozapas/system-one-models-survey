# grey_robbalian_rev — Rev (robbalian): decision models trained to beat Jev on accuracy, speed and cost

- Not arXiv. Grey literature: GitHub repository README.
- source_url: https://github.com/robbalian/rev (raw README fetched from `main` branch)
- Affiliation type: independent (individual GitHub project, "robbalian"; credits Jared Palmer's Kev as the architectural inspiration).
- Fetched: 2026-09-24. File: fulltext/grey_rev_repo.md.
- No seed claims assigned to this specific source beyond the ECE/probe seed that belongs to the Archer Hume essay (grey_archerhume_jev) — recorded there. This source's own numbers are extracted per the brief's general instruction to record measured quantities from assigned grey-literature sources.

## Task and data
A 975-question frozen public holdout, built from the validation splits of five public multiple-choice/entailment datasets: ContractNLI (175 items, 3-way support/contradict/not-mention over NDAs), RACE (200, 4-way reading comprehension), CosmosQA (200, 4-way commonsense reading), MultiRC (200, 2-way candidate-answer correctness), Social IQa (200, 3-way social commonsense). Training used 19,792 public decisions from the train splits of the same five datasets plus classification/policy rows from 13 other public sets; "training excluded every one of these [975 holdout] questions and every document they come from."

## Decision models / version pins
- **Rev-Qwen3.5-4B / Rev-Qwen3.5-9B / Rev-Qwen3.8-27B**: LoRA tune + small pointer head on top of Qwen3.5-4B/9B and Qwen3.8-27B respectively (head picks one offered option directly; nothing generated). Weights on Hugging Face (`robbalian/rev-qwen3.5-4b`, `robbalian/rev-qwen3.5-9b`, `robbalian/rev-qwen3.8-27b`), 60-200 MB each (adapter + head only). "We borrowed the recipe, a LoRA and a pointer head on Qwen, from Jared Palmer's Kev" — i.e., architecturally derived from grey_kev's approach, independently trained.
- **Hosted Jev**: accessed as `typesafe/jev-1.13` through OpenRouter for the main comparisons ("Speed and cost use one B200 per model on Modal... Jev is typesafe/jev-1.13 through OpenRouter, where its servers sit isn't public").

## Comparators and tuning-budget parity
Rev models are fine-tuned (LoRA) specifically on the 19,792-decision training pool; Jev is queried as a general hosted decision model with no task-specific tuning by this source. comparator_tuning_budget = "fine-tuned (Rev) vs not reported/general hosted model (Jev)". The source explicitly controls for a caching confound: "Hosted Jev does prompt caching on repeated questions which reduced their latency. We ended up building in a cache-buster at the top of requests for all of them to make the comparison more fair" — a methodological parity fix worth noting.

## Reference labels
Original dataset gold labels for the 975-item holdout (ContractNLI/RACE/CosmosQA/MultiRC/Social IQa's own validation-split labels) — reference_label_type = human_adjudicated. For the two outside leaderboards (JevBench, Decision Index), reference labels belong to those leaderboards' own harnesses, not directly characterized here; recorded as "unclear" for those specific rows.

## n and sampling
975-item frozen public holdout (checksum-verified, `eval_sets/public_holdout_975.jsonl`); training pool 19,792 decisions. Multi-question latency test: 4 synthetic invoices x {1, 5, 20} questions each. Speed-by-input-length test: same 975-question run, bucketed by input token count into 5 buckets (under 256 / 256-512 / 512-1k / 1k-2k / over 2k tokens). Outside leaderboards: JevBench 231 public items; Decision Index "all 19 benchmarks, 77,591 requests." Snake game: 10 games per player, 1,000-move cap (200-move cap for the vision variant).

## Test-set exposure
The 975-item holdout draws from public pre-2026 dataset validation splits (RACE, CosmosQA, MultiRC, Social IQa, ContractNLI) — test_set_exposure = public-pre-2026, with the source's own contamination control ("Training excluded every one of these questions and every document they come from" for Rev's own training; the source cannot make the same claim about Jev's unknown training data). JevBench and Decision Index are 2026 community leaderboards — recorded as "unclear" for pretraining exposure.

## Cost and latency
Hardware: "one B200 per model on Modal" for Rev; Jev accessed via OpenRouter (hosted, location undisclosed). Headline table: Hosted Jev 85.0% accuracy / 142 ms / $0.0366 per 1k; Qwen3.5-4B (Rev) 87.7% / 37 ms / $0.0220; Qwen3.5-9B (Rev) 88.7% / 40 ms / $0.0297; Qwen3.8-27B (Rev) 92.0% / 75 ms / $0.0819. "Cost is Modal's list price for the GPU plus its CPU and RAM, divided by the answers per second we measured with the GPU fully busy" (i.e., a saturated-GPU cost floor, not typical/average utilization) — flagged by the source itself: "Self-hosting is only cheap when the GPU is busy. At one request in flight our cost per answer is several times Jev's." On the cheaper RunPod B200 price ($5.98/h), Rev's 4B drops to $0.0178/1,000 (about half Jev's price) and the 27B to $0.0662/1,000. hardware_or_provider = "1x NVIDIA B200 per model, Modal serverless (list price) / RunPod pricing comparison; Jev via OpenRouter, hosted, location undisclosed".

## Calibration
Not a focus of this source; a calibration-temperature fitting script (`train/fit_temperature.py`) is referenced in the repo structure but no ECE/Brier numbers are reported in the fetched README text. calibration_quantity = "not reported (temperature-fitting script exists in repo but no calibration metric quoted in README)".

## Cascade / escalation
Not applicable — a direct multi-model accuracy/speed/cost comparison, not a routing/cascade design.

## Robustness / stress tests
- **Question-count and input-length scaling ("reverse engineering Jev")**: Rev's architecture "scaled well from 1, 5, 20 questions but hosted Jev is impressively flat" and "Our method gets slower while theirs is flat, indicating either constant-state prefill or prefill that is so fast it's drowned by other overhead" — an architectural inference about Jev's serving design, paralleling the Archer Hume essay's independent latency-scaling probes.
- **What didn't work (ablations)**: "JSON on hosted models" — accuracy fine but serial generation made 20 questions take 5.10s vs Jev's 0.27s, at 15x cost/decision; "single-token outputs per question" — accuracy fell, latency barely improved; "train a head only" (frozen backbone) — best accuracy 80% on dev but "much poorer on external test sets"; final "LoRA plus head" design adopted.
- **Snake game (informal robustness/behavioral test)**: average moves survived per game (10 games, 1,000-move cap, same seeds): Qwen3.8-27B (Rev) 187, Qwen3.5-4B (Rev) 172, Qwen3.5-9B (Rev) 144, Hosted Jev 113. "Jev is text only, so there's no Jev number" for the vision-board variant, where the 27B (from images) survived 64 moves/game vs 176 from text under a 200-move cap.
- **Speed by input length**: Jev's latency is flat 140-150 ms across all bucket ranges (under 256 tokens to over 2,000 tokens); Rev's 4B/9B stay under Jev's latency up to the longest contracts, but the 27B crosses above Jev beyond 2,000 tokens.
- **External leaderboards**: on the source's own run of JevBench (231 public items), Rev's 27B scores 89.6% vs Hosted Jev 86.6% vs best other open model 87.0%; on the Decision Index (19 benchmarks, 77,591 requests), Rev's 27B scores 59.8 vs Jev 59.5 vs best other open model 55.7 — "The Decision Index lead is narrow: we're well ahead on contracts and tools and well behind on knowledge questions like GPQA and MMLU." Explicit caveat: "These are our measurements with each board's own scoring, not the boards' runs."
- **Accuracy run-to-run variability**: "Jev's accuracy also moves by a few questions between runs, 84.7% to 85.2% across ours" — an explicit measurement-noise caveat for the headline 85.0% Jev accuracy figure.

## Code and data availability
Full training/serving/benchmark code, eval sets (with checksum), and weights on Hugging Face: https://github.com/robbalian/rev (code + eval_sets), https://huggingface.co/robbalian/rev-qwen3.5-4b (and 9b/27b siblings). code_available = "yes (https://github.com/robbalian/rev, weights on Hugging Face)".

## Limitations (source's own caveats)
- "95% intervals are about plus or minus 2 points, so the 4B's lead over Jev is at the edge of a tie; the 9B and 27B are clearly ahead" — explicit statistical-uncertainty caveat on the headline accuracy comparison for the smallest Rev model.
- "Latency shifts by tens of milliseconds between runs depending on where the client container lands, so compare within a table, not across tables."
- "Self-hosting is only cheap when the GPU is busy" — the cost comparison assumes full GPU utilization, not realistic average load.
- On the JevBench leaderboard: "No JevBench item was trained on, but we read our first model's misses on its public items to decide what synthetic data to make" — an acknowledged (mild) form of target-leaking via iterative synthetic-data design informed by held-out failures, a methodological caveat for that specific external comparison.
