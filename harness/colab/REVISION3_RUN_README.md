# Third revision runs on Colab

This run adds two things. Nothing in it calls the hosted model.

1. **An explicit out-of-scope option.** `d2_k150` offers the 150 CLINC-150 intents and no answer for a request that fits none of them. `d2_k150_oos` asks the same 800 requests with the same 150 options in the same order, plus `o151` "out of scope" appended last. The 200 out-of-scope items take `o151` as their reference label. It was frozen by `src/s00d_freeze_oos_option.py`. The open decision models and all three generative comparator tags answer it.
2. **Backbones scored on option descriptions.** Part 1 of the second revision scored the untuned Qwen3.5 backbones on option keys such as `o17`. Here the same backbones are scored on each option's own description text, the classic zero-shot readout of a language model (`adapters.BackboneDescScoreBackend`).

The run has two parts. Run Part 1 on an L4 and Part 2 on an A100, in two separate runtimes, or both on one A100.

## What to upload

Both files are in `paper4/shared/colab/`:

| File | Contents |
|---|---|
| `revision3_upload.zip` | 2.3 MB: `common.py`, `harness.py` and `adapters.py`, the 7 input files the run needs, and `manifest.json` |
| `run_revision3.ipynb` | the notebook |

The 7 inputs are `d2_k150_oos`, `d1_neutral`, `d2_k150` and the four `d3_*` tasks. The notebook checks every file in the zip against its SHA-256 and stops if one differs.

## Switches

All switches are in the first code cell.

| Switch | Default | Effect |
|---|---|---|
| `RUN_PART1` | `True` | Part 1 on this runtime. With it off, every Part 1 cell prints "skipped". |
| `RUN_COMPARATOR` | `True` | Part 1b, `comparator-open` on `d2_k150_oos`. Needs `RUN_PART1`. |
| `RUN_BACKBONE_DESC` | `True` | Part 1c, the four description-scoring backbones. Needs `RUN_PART1`. |
| `RUN_PART2` | `True` | Part 2, the Qwen3.6-27B comparator. |
| `COMPARATOR2_VARIANT` | `'fp8'` | `'awq'` switches Part 2 to the L4 fallback, as in the second revision. |
| `UNITS_PER_HOUR` | L4 4.8, A100 11.8 | Assumed compute-unit rates, used only for printed estimates. |

The status cell lists the Part 1b and Part 1c files only when their switch is on, so `ALL_DONE_revision3` can be reached with either of them off.

## Part 1 (L4)

The cells run in this order, so the cheapest and most important jobs finish first.

**1a. Open decision models on `d2_k150_oos`.** The tags are `laya-ml`, `kev-0.8b`, `decider-2b`, `this-that-1.0`, `kev-9b` and `nimble-9b`, at rep 1, with 800 requests each. They use the first revision's uv envs (`laya`, `kev_decider_tt`, `nimble`), its package lists and its pins, all imported from `build_revision_notebook.py`. Each cell smoke-tests 5 requests, prints a time estimate, then runs the condition. `laya-en` is not run. Its English head refuses every 150-option question, because the option text exceeds its head budget. It did so on `d2_k150` and on both permutations, so it would only add 800 error lines.

**1b. Qwen3-14B comparator on `d2_k150_oos`.** The tag is `comparator-open`, with `Qwen/Qwen3-14B-AWQ` pinned to the revision of its earlier answers. The settings are the same as before: greedy, thinking off, verbalized JSON, 12,288-token engine length. The cell smoke-tests 5 requests, then runs the 800 in one process.

**1c. Backbones scored on descriptions.** The tags are `backbone-desc-qwen35-0.8b-base`, `-2b-base`, `-9b-base` and `-9b`. They load the same checkpoints and revisions as the second revision's key-scoring tags, in the same `backbone` env. The conditions are `adapters.BACKBONE_DESC_CONDITIONS`: `d1_neutral`, `d2_k150`, `d3_conv_go_awry`, `d3_wiki_corpus`, `d3_emotion` and `d3_wiki_politeness`. That makes 3,196 requests per backbone.

Scoring works as follows. The prompt carries the state, the question and the `- key: description` lines, then asks for the description of the best option and ends with the cue `Answer:`. Each option's score is the mean log-probability per token of `" " + description` after that cue. The option probability is the softmax of these scores at temperature 1.

Each 1c cell first runs a smoke test with the self-check on (`P4_OPTSCORE_CHECK`), over 2 requests each of `d2_k150`, `d1_neutral` and `d3_emotion`. Every description is scored a second time by a plain full-sequence pass without the cache. The cell prints the largest difference between the two option distributions. It stops that backbone before the full run if the difference exceeds 0.15, or if the top options clearly disagree on more than one question. All six conditions then run in one process, and a condition left incomplete is retried on its own.

## Part 2 (A100)

The tags are `comparator-open2` (verbalized JSON) and `comparator-open2-ll` (option-key likelihood). Both run `Qwen/Qwen3.6-27B-FP8` (`e89b16eb`) through vLLM 0.30.0 on `d2_k150_oos` only, at rep 1. The env, the pins and the engine profile are those of the second revision. `adapters.py` picks the engine settings from the checkpoint, so they cannot drift. There is no batch-1 latency sample this time.

The cell builds the `vllm_env` env, then smoke-tests 5 requests of each mode. Both smoke tests run on `d2_k150_oos` rather than on `d1_neutral` and `d2_k150` as in the second revision, so the new `o151` key goes through both modes before the full run. After each smoke test, the cell prints the engine time per question and an estimate for the 800 questions. It then runs the verbalized mode and the likelihood mode, each in a fresh process.

With `COMPARATOR2_VARIANT = 'awq'`, Part 2 uses `cyankiwi/Qwen3.6-27B-AWQ-INT4` (`e5cc0400`) under the tags `comparator-open2-awq` and `comparator-open2-awq-ll`. This fallback is untested and close to the L4 memory limit.

## Job list

| Part | Tag | Conditions | Requests |
|---|---|---|---|
| 1a | `laya-ml`, `kev-0.8b`, `decider-2b`, `this-that-1.0`, `kev-9b`, `nimble-9b` | `d2_k150_oos` | 800 each, 4,800 in all |
| 1b | `comparator-open` | `d2_k150_oos` | 800 |
| 1c | four `backbone-desc-qwen35-*` tags | six conditions | 3,196 each, 12,784 in all |
| 2 | `comparator-open2`, `comparator-open2-ll` | `d2_k150_oos` | 800 each, 1,600 in all |

## Steps

1. In Google Drive, open `My Drive/Jev/paper4/colab/`, the folder of the earlier runs. Upload `revision3_upload.zip` there and do not unzip it.
2. Open `run_revision3.ipynb` in Colab (File, Upload notebook).
3. **Runtime 1, Part 1.**
   - Choose Runtime, Change runtime type, **L4 GPU**.
   - In the first code cell, set `RUN_PART1 = True` and `RUN_PART2 = False`. Leave `RUN_COMPARATOR` and `RUN_BACKBONE_DESC` on.
   - Choose Runtime, Run all, and allow Drive access.
   - The unpack cell must print `7 input files and 3 source files verified`.
   - The GPU cell prints the free disk. Part 1 builds five envs and downloads roughly 70 to 90 GB of weights on one runtime, which the earlier runs never did. If the cell shows less than about 150 GB free, set `RUN_BACKBONE_DESC = False` for this runtime and run Part 1c later on a fresh runtime, with `RUN_PART1 = True` and `RUN_COMPARATOR = False`. The 1a cells then rebuild their envs and repeat their 5-request smoke tests, but skip every finished request, which costs about 30 minutes.
   - Each model cell prints its env build, its smoke test, the run and `DONE`.
4. **Runtime 2, Part 2.**
   - Disconnect and delete the runtime, then choose **A100 GPU**.
   - Set `RUN_PART1 = False` and `RUN_PART2 = True`, then Run all.
   - With every switch on, one A100 runtime runs both parts.
5. Keep the tab open. If the runtime disconnects, reconnect and choose Run all again with the same switches. Answers are on Drive line by line, and finished requests are skipped.
6. The last cell lists every planned file. A part not run yet shows as MISSING.
   - For each file, it shows the answered count, the error lines, the longest prompt and whether the recorded revision equals the pin.
   - When everything is complete, it writes `ALL_DONE_revision3`.
   - In every case it writes `My Drive/Jev/paper4/colab/answers_revision3.zip`.
7. After the last runtime, download `answers_revision3.zip` and hand it back. That archive is the only thing needed.

A model that fails writes `ERROR_revision3.txt` in its folder, and the next cell continues. `harness.py` records a failing request as an error line and still exits normally. For that reason every smoke test here reads its own answer files and stops the model on any error line, including a failed self-check. A condition counts as done only when all its requests are answered.

## Expected time and compute units

These are estimates, not measurements. They come from the earlier runs: the per-request `latency_s` of the answer files, the batch wall times of the comparators, and the start and end times in `answers/run_log_revision.json` and `answers/run_log_revision2.json`.

The first revision ran from 03:08 to 06:32 on an L4. Its 204 minutes held 168 minutes of inference, so env builds, downloads and model loads took about 35 minutes for four envs and eight models. The second revision's Part 1 took 163 minutes on an L4, with 152 minutes of inference. Its Part 2 took 129 minutes on an **A100-SXM4-80GB**, with 106 minutes of engine time.

| Part | Runtime | Inference | Envs, downloads, loads | Total | Units |
|---|---|---|---|---|---|
| 1a, six decision models | L4 | about 35 min (nimble-9b 23, kev-9b 6, the other four 1 to 2 each) | about 20 to 30 min | about 1 h | about 5 |
| 1b, comparator-open | L4 | about 15 min | about 10 to 15 min (env and two engine starts) | about 0.5 h | about 2 to 3 |
| 1c, four backbones | L4 | about 2 to 5 h | about 20 to 30 min | 2.5 to 5.5 h | 12 to 26 |
| Part 1 in all | L4 | | | 4 to 7 h | 19 to 34 |
| 2, Qwen3.6-27B | A100 | verbalized about 8 min, likelihood about 50 min | about 20 min (env, 31 GB download, four engine starts) | 1.3 to 1.6 h | 15 to 19 |

- The 1a figures are the first run's per-request `d2_k150` latencies times 800. One more option changes them very little.
- The 1b figure is the batch wall time of `comparator-open` on `d2_k150` on an L4, 15.3 minutes.
- The 1c figures have no direct measurement. They start from the key-scoring times of the same backbones on the same six conditions: 15 min for 0.8B, 16 min for 2B, and 28 min for each 9B. `d2_k150` dominates. Key scoring there needed one batched pass of 16 short paths per question. Description scoring needs about ten batched passes of 16 descriptions each. A local CPU test of the notebook cells with the 0.8B backbone gave about 16 s per `d2_k150` request under description scoring against about 3 s under key scoring. CPU time is bound by compute and the L4 is mostly bound by reading weights, so on the GPU the factor should be smaller. The table assumes two to six times the key-scoring time for `d2_k150`. The five other conditions have only 2 to 6 options and cost about what key scoring did. This gives about 25 to 55 minutes for each of the two smaller backbones and 45 to 105 minutes for each 9B. The full run prints its progress every 200 requests, which shows early whether the estimate holds.
- The Part 2 figures are the second revision's `d2_k150` times on an 80 GB A100: 7.7 minutes verbalized and 48 minutes in the likelihood mode. On a 40 GB A100, the likelihood mode may take longer, because less memory is left for cached prompt blocks.

## What the notebook pins

| Item | Pinned to |
|---|---|
| Decision models and Qwen3-14B-AWQ | the revisions of their original answers, the same `REVISIONS` as `build_revision_notebook.py` |
| Backbones, Qwen3.6-27B-FP8 and the AWQ fallback | the revisions of `build_revision2_notebook.py` |
| Decision model envs | the first revision's package lists (`torch==2.8.0` from the CUDA 12.8 wheels, `kev` and `thisthat` at fixed commits, `laya==0.3.20`, the fixed nimble set) |
| Backbone env | `torch==2.8.0`, `transformers==5.17.0`, `flash-linear-attention` optional |
| Both comparator envs | `vllm==0.30.0`, `VLLM_USE_FLASHINFER_SAMPLER=0`, the env's bin folder on `PATH` for ninja |

The first revision installed `vllm` without a version for `comparator-open`. Here it is pinned to 0.30.0, the version the first `comparator-open` run logged, which is also the version of Part 2. Both parts use `/content/envs/vllm_env`, so with both parts on one runtime the two comparators run on the same engine.

## After hand-back

1. Unzip `answers_revision3.zip` into `paper4/shared/answers/`. Every file name in it is new. Its layout is `<tag>/<cond>__rep1.jsonl`, plus `<tag>/DONE_revision3` markers and `run_log_revision3.json`. The new files are `d2_k150_oos__rep1.jsonl` in the folders of the six decision models, `comparator-open`, `comparator-open2` and `comparator-open2-ll`, and the four new `backbone-desc-qwen35-*` folders.
2. Existing answer files are not touched, so every earlier result stays as it is.

## Rebuilding the package

If `adapters.py`, `harness.py` or any shipped input changes, rebuild:

```
D:/p4env/venv/Scripts/python.exe build_revision3_notebook.py --check
```

The check compiles every code cell of the notebook and the three source files. It checks each input in the zip against the manifest SHA-256 and confirms that no marker or file name of the earlier runs is left in the notebook.
