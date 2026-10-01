# Fourth revision runs on Colab

This run reduces every limitation that more data can reduce. Jev already answered the new conditions locally; the only Jev call here is an optional latency sample from the cloud.

1. **Two new tasks for the open models.** `d3_goemotions` (492 Reddit comments with a rater-agreed Ekman emotion, frozen by `src/s00e_freeze_goemotions.py`) and `d2_banking77` (616 banking queries, 8 per intent, all 77 intents as options, frozen by `src/s00f_freeze_banking77.py`). The open decision models, the four untuned Qwen3.5 backbones (key scoring) and Qwen3-14B answer both.
2. **The two 9B description-scoring backbones**, which ran out of memory in the third revision.
3. **Stronger trained baselines.** DeBERTa-v3-large fine-tuned per task (`src/b05_strong_classifiers.py`) on CLINC-150, the four D3 tasks, GoEmotions, Banking77, and D1 (a cross-encoder trained on the teacher's soft labels).
4. **Comparators from three model families at full parity.** Gemma-4-31B-it and Mistral-Small-24B-Instruct-2501, each read as a verbalized-JSON and an option-key-likelihood comparator, on every condition Qwen3.6-27B covers, stress conditions included.
5. **A deliberating comparator.** Qwen3.6-27B with thinking on (`comparator-open2-think`), the same weights as `comparator-open2`, so any difference is due to deliberation.
6. **Latency.** Batch-1 latency samples of every new comparator (`comparator-open-b1`, `comparator-gemma-b1`, `comparator-gemma-ll-b1`, `comparator-mistral-b1`, `comparator-mistral-ll-b1`), the first 40 requests of `d1_neutral` one request at a time, as the second revision did for Qwen3.6-27B, and an optional Jev sample from the cloud (the same 40 requests).

The run has five parts. Part A and Part B each need an L4. Parts C1, C2 and C3 each need an A100 80GB. All five can run at the same time on five runtimes. They write to the same Drive folder, and the last cell of whichever runtime finishes last lists and archives every part's files.

## What to upload

Both files are in `paper4/shared/colab/`:

| File | Contents |
|---|---|
| `revision4_upload.zip` | 12.7 MB: `common.py`, `harness.py`, `adapters.py`, `metrics.py` and `b05_strong_classifiers.py`, the 25 input files the run needs with `manifest.json`, and the frozen DeBERTa training rows under `shared/data/b05/` (eight task files and `b05_meta.json`) |
| `run_revision4.ipynb` | the notebook |

The notebook checks every input against its manifest SHA-256, and every source and training file against the SHA-256 recorded when the notebook was built, and stops if one differs.

## Switches

All switches are in the first code cell. Set exactly one part switch to `True` per runtime.

| Switch | Default | Effect |
|---|---|---|
| `RUN_PART_A` | `True` | Part A on this runtime |
| `RUN_PART_B` | `False` | Part B on this runtime |
| `RUN_PART_C1` | `False` | Part C1, the Gemma pair; its cell skips on a GPU that is not an A100 or H100 |
| `RUN_PART_C2` | `False` | Part C2, the Mistral pair; same GPU rule |
| `RUN_PART_C3` | `False` | Part C3, the Qwen3.6-27B thinking tag, then the Qwen3.6-27B pair; same GPU rule |
| `RUN_DECISION_MODELS`, `RUN_BACKBONE_KEY`, `RUN_COMPARATOR_OPEN`, `RUN_BACKBONE_DESC`, `RUN_JEV_LATENCY` | `True` | the five blocks of Part A |
| `B05_GROUPS` | `['clinc', 'goemo', 'banking', 'd3', 'd1']` | the Part B groups and their order |
| `RUN_THINK`, `RUN_QWEN36` | `True` | the two blocks of Part C3; with only one of them on, the run log is named `C3think` or `C3qwen`, so the two can run on two runtimes |
| `QWEN36_SMOKE` | `False` | smoke-test the Qwen3.6 pair too (it ran twice before with the same env and pins) |
| `FREE_DISK_AFTER_DONE` | `True` | remove a comparator's downloaded weights from the runtime disk once all its tags on that part are done |
| `HF_TOKEN_FROM_SECRETS` | `False` | read `HF_TOKEN` from the Colab secrets for faster downloads |
| `UNITS_PER_HOUR` | L4 4.8, A100 11.8 | assumed compute-unit rates, used only for printed estimates |

## Part A (L4)

**(a) Open decision models.** `laya-en`, `laya-ml`, `kev-0.8b`, `decider-2b`, `this-that-1.0`, `kev-9b` and `nimble-9b`, in that order, with the first revision's envs, package lists and pins. Each runs `d3_goemotions` and then `d2_banking77`. Each cell smoke-tests 3 requests of each condition, prints an estimate, then runs each condition and retries it once if it is incomplete. `laya-en` is the exception in the smoke test, which covers `d3_goemotions` only. Its English head shares 192 minus 16 tokens among the option labels. It refused every 150-option question (1 token per label) and answered every 50-option one (3 per label). At 77 options it has 2 per label. The option text of a `d2_banking77` item is 1,947 characters, between `d2_k50` (830) and `d2_k150` (2,559). If it refuses, the `d2_banking77` file of `laya-en` fills with error lines and its cell ends with `ERROR_revision4.txt`, while its `d3_goemotions` answers stay complete.

**(b) Untuned backbones, key scoring.** The four `backbone-qwen35-*` tags of the second revision (`BackboneOptScoreBackend`) on `d3_goemotions` and `d2_banking77`, in the second revision's `backbone` env with its pins. Each cell smoke-tests 2 requests of each condition with the cached-versus-full-sequence self-check on (the key-scoring check passed on `d2_k150` for all four in the second revision), then runs both conditions in one process.

**(c) comparator-open.** Qwen3-14B-AWQ through vLLM 0.30.0 with the settings of its earlier runs, on `d3_goemotions` and `d2_banking77`, after a smoke test of 3 requests of each. The next cell runs `comparator-open-b1` in the same env: the first 40 requests of `d1_neutral`, one request at a time, with the Qwen3-14B-AWQ engine profile `adapters.py` adds for it (12,288-token context, as the first run).

**(d) The 9B description-scoring backbones.** `backbone-desc-qwen35-9b-base` and `backbone-desc-qwen35-9b` on the six conditions of the third revision (`d1_neutral`, `d2_k150` and the four D3 tasks), with `P4_DESC_ROWS=4` and `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True`. The third-revision logs show where they failed. The smoke self-check on `d2_k150` asked for 2.40 GiB, which is exactly the float64 log-softmax over a 1300-token prompt and the 248,320-token vocabulary in `desc_logprobs_naive`, the full-sequence recomputation of the self-check. The row loop of the scoring path, which `adapters.py` now retries with fewer rows, was not the problem, and the full run never takes the self-check path. The notebook therefore runs the self-check smoke on 2 requests each of `d1_neutral` and `d3_emotion`, where it passed before, and a second smoke of 2 requests each of `d2_k150` and `d3_conv_go_awry` (prompts up to 8,000 tokens) with the check off, on the cached path the full run uses. All six conditions then run in one process, and any condition left incomplete is retried on its own.

**(e) Optional Jev latency.** `harness.py --model jev --cond d1_neutral --rep 6 --limit 40`, the first 40 requests of `d1_neutral`, through `typesafe-sdk==0.7.1` (the version of the local runs) with the model pinned to `jev-1.13.0`. Reps 1 to 5 exist locally (reps 1 to 3 hold all 400 requests, reps 4 and 5 the 40-state retest subset), so this is rep 6, and its answers go to `jev-1.13.0/d1_neutral__rep6.jsonl`. The cell reads the API key from the Colab secret `TYPESAFE_API_KEY` (the key icon on the left, with notebook access switched on) and hands it to the harness process through its environment only. The key is never printed, logged or written to a file. Without the secret, the cell prints that it is skipped and why. The status cell lists this file as optional, so its absence does not block `ALL_DONE_revision4`.

## Part B (L4)

`b05_strong_classifiers.py` fine-tunes `microsoft/deberta-v3-large` at revision `64a8c8ea` (resolved on 2026-09-29), one model per task, in its own `b05` env (`torch==2.8.0`, `transformers==5.17.0`, `sentencepiece`, `protobuf`).

| Tag | Condition | Training rows |
|---|---|---|
| `baseline-deberta-large-clinc` | `d2_k150` | the `bert-base-clinc` rows of `b01`: CLINC-150 train and oos_train (15,245), validation val and oos_val (3,099), 151-way head, the out-of-scope logit dropped when serving, max 64 tokens |
| `baseline-deberta-large-goemo` | `d3_goemotions` | `data/goemotions/train.jsonl` after removing test texts, `b04.cap_and_split` (8,000 train, 540 in the class-balanced validation part), class-weighted loss, max 512 tokens |
| `baseline-deberta-large-banking` | `d2_banking77` | `data/banking77/train.jsonl` after removing test texts; 20% of every intent held out as validation (7,999 train, 1,998 validation), unweighted loss as for CLINC, max 128 tokens |
| `baseline-deberta-large-d3` | the four D3 tasks | exactly the training and balanced validation rows of `bge-small-lr-d3` (test conversations removed as `b04` removes them), class-weighted loss, max 512 tokens |
| `baseline-deberta-large-d1` | `d1_neutral`, `d1_calib` | the 900 typed-decisions training states of `bge-small-lr-d1` (outside `d1_calib` and `d1_neutral`), 720 for training and 180 held out for validation (20% of every workflow) |

The D1 model is a cross-encoder. Each pair of the state text (as `b01.state_text` renders it) and the question's instructions followed by one option's description gets one logit. A softmax runs over the question's options. The loss is the cross-entropy against the teacher's soft distribution, the target `b01` builds in `d1_train_states`. A noul question without criteria uses "Yes." and "No." as its descriptions. Every test option text occurs in the training rows, which the freeze asserts. The model is selected by validation soft cross-entropy (the rule `b01` uses for its D1 regression, ties by accuracy), and one temperature per question type is fitted on the validation states. Each optimizer step uses 8 questions, about 27 option rows. Latency is timed per state, all its questions in one pass, as `b01` times `bge-small-lr-d1`.

The training rows were frozen at build time from the local `b01` and `b04` caches and the typed-decisions dataset. The D3 rows were checked against the `train_src` and `val_src` lists `b04` stored. Training follows `b01`'s BERT loop: AdamW with weight decay 0.01, batch 32 (8 questions for D1), 10% warm-up, gradient clipping at 1.0, fp32 weights with bf16 autocast, and a grid of learning rates 1e-5 and 2e-5 by epochs 1 to 4. The grid is lower than `b01`'s 3e-5 and 5e-5 because DeBERTa-v3-large often diverges at those rates. One temperature is fitted on the validation rows (per question type for D1). Next to each answer file, `<cond>__fit.json` holds the grid, the selection, the temperatures, row and truncation counts, the hardware and the test log-probabilities.

The cell first runs `--smoke` with the real pinned checkpoint, on a few rows of every task (48 training rows with the 4 longest, 24 validation rows, 6 test items; for D1, 16 training states, 8 validation states and 6 test items per condition), for one epoch. It checks that every smoke answer file has 6 lines with the record fields of the earlier baselines and the pinned revision. The smoke run prints the training throughput and an estimate for each task. The full run then goes group by group, in the order CLINC, GoEmotions, Banking77, D3, D1. A group with an incomplete condition is run once more, and complete conditions are skipped.

## Parts C1, C2 and C3 (A100 80GB)

All three use the `vllm_env` env of the third revision's part 2 (`vllm==0.30.0`).

| Part | Model | Tags | Pin | Conditions |
|---|---|---|---|---|
| C1 | `google/gemma-4-31B-it`, FP8 on load | `comparator-gemma`, `comparator-gemma-ll` | `842da379` | 25: `adapters.COMPARATOR_CONDITIONS` (8), `d3_goemotions`, `d2_banking77`, `d2_k150_oos`, then `adapters.STRESS_CONDITIONS` without the duplicate `d2_k20` (`d2_k5`, `d2_k50`, the twelve `e2_*` name files) |
| C2 | `mistralai/Mistral-Small-24B-Instruct-2501`, FP8 on load | `comparator-mistral`, `comparator-mistral-ll` | `9527884be6` (full sha `9527884be6e5616bdd54de542f9ae13384489724`) | the same 25 conditions |
| C3 | `Qwen/Qwen3.6-27B-FP8`, thinking on | `comparator-open2-think` | `e89b16eb`, revision 2 profile, 24,576-token context | 10: `d1_neutral`, `d1_calib`, `d2_k150`, the four D3 tasks, `d2_k150_oos`, `d3_goemotions`, `d2_banking77` |
| C3 | `Qwen/Qwen3.6-27B-FP8` | `comparator-open2`, `comparator-open2-ll` | `e89b16eb`, revision 2 profile | 16: `d3_goemotions`, `d2_banking77`, then `adapters.STRESS_CONDITIONS` without `d2_k20` |

With these runs every comparator covers every condition Qwen3.6-27B covers, which the builder asserts. `d2_k20` is left out for Qwen3.6 only because both of its tags already answered it in the second revision, and unpacking the hand-back archive would overwrite those files. The builder asserts that no planned answer file exists in `shared/answers`.

For Gemma and Mistral, both modes are smoke-tested first, on 3 requests each of `d1_neutral` (three question types), `d2_k150` (150 options) and `d3_conv_go_awry` (the longest prompts, up to 8,000 tokens). A mode whose smoke test fails is marked and skipped, and the other mode still runs. Each mode then runs all its conditions in one process, and any condition left incomplete is retried on its own. At the end of each part, a batch-1 cell runs the two batch-1 tags of that model (`comparator-gemma-b1` and `comparator-gemma-ll-b1` in C1, `comparator-mistral-b1` and `comparator-mistral-ll-b1` in C2) on the first 40 requests of `d1_neutral`, one request at a time, as the second revision did for Qwen3.6-27B. The cell prints the median latency per request, and the status cell reports every batch-1 file with its counts. These files are optional: a failure never blocks `ALL_DONE_revision4`. The batch-1 cell is the last one that needs the weights, so the disk cleanup runs there.

`comparator-open2-think` (`Comparator2ThinkBackend`) generates up to 8,192 tokens with the sampling of `THINK_SAMPLING` (temperature 0.6, top-p 0.95, top-k 20, fixed seed) and parses the JSON object after the closing think tag. Its smoke test covers 5 requests each of `d1_neutral` and `d2_k150`. The tag stops if more than half the smoke replies are error lines. After the smoke test the cell prints the mean output tokens per question, the output tokens this means for the 8,204 questions, and a time estimate. A reply that fails to parse is an error line, and under the fixed seed it would fail again. The full run therefore retries only requests that got no line at all, after a crash. A condition with parse failures stays INCOMPLETE in the status, with its count, and those error lines are part of the result.

The bf16 Gemma checkpoint is about 62 GB to download and the Mistral repository about 47 GB. The Mistral repository ships both `consolidated.safetensors` and sharded weights, so if vLLM fetches both, it is about 94 GB. The Qwen3.6 FP8 checkpoint is 31 GB. Each cell prints the free disk. With `FREE_DISK_AFTER_DONE`, a model's weights are removed from `/content/hf` once all its tags on that part are done. Part C3 keeps the Qwen3.6 weights until its last cell.

## Job list

| Part | Tag | Conditions | Requests |
|---|---|---|---|
| A (a) | `laya-en`, `laya-ml`, `kev-0.8b`, `decider-2b`, `this-that-1.0`, `kev-9b`, `nimble-9b` | `d3_goemotions`, `d2_banking77` | 1,108 each, 7,756 in all |
| A (b) | `backbone-qwen35-0.8b-base`, `-2b-base`, `-9b-base`, `-9b` | `d3_goemotions`, `d2_banking77` | 1,108 each, 4,432 in all |
| A (c) | `comparator-open` | `d3_goemotions`, `d2_banking77` | 1,108 |
| A (c) | `comparator-open-b1`, optional | `d1_neutral`, first 40 | 40 |
| A (d) | `backbone-desc-qwen35-9b-base`, `backbone-desc-qwen35-9b` | six conditions | 3,196 each, 6,392 in all |
| A (e) | `jev-1.13.0`, optional | `d1_neutral`, rep 6 | 40 |
| B | `baseline-deberta-large-clinc` | `d2_k150` | 800 |
| B | `baseline-deberta-large-goemo` | `d3_goemotions` | 492 |
| B | `baseline-deberta-large-banking` | `d2_banking77` | 616 |
| B | `baseline-deberta-large-d3` | four D3 tasks | 1,996 |
| B | `baseline-deberta-large-d1` | `d1_neutral`, `d1_calib` | 700 |
| C1 | `comparator-gemma`, `comparator-gemma-ll` | 25 conditions | 12,804 each |
| C1 | `comparator-gemma-b1`, `comparator-gemma-ll-b1`, optional | `d1_neutral`, first 40 | 40 each |
| C2 | `comparator-mistral`, `comparator-mistral-ll` | 25 conditions | 12,804 each |
| C2 | `comparator-mistral-b1`, `comparator-mistral-ll-b1`, optional | `d1_neutral`, first 40 | 40 each |
| C3 | `comparator-open2-think` | 10 conditions | 5,404 (8,204 questions) |
| C3 | `comparator-open2`, `comparator-open2-ll` | 16 conditions | 7,908 each |

| Part | Answer files | Requests | Questions |
|---|---|---|---|
| A | 38 (two optional) | 19,768 | 22,968 |
| B | 9 | 4,604 | 7,404 |
| C1 | 52 (two optional) | 25,688 | 32,888 |
| C2 | 52 (two optional) | 25,688 | 32,888 |
| C3 | 42 | 21,220 | 25,620 |

## Expected time and compute units

These are estimates, not measurements. The comparator and backbone figures come from the batch times recorded in the answer files and from `answers/run_log_revision2.json` and `answers/run_log_revision3.json`. The GPUs of those runs were an L4 and an A100-SXM4-80GB. The unit rates are the assumed 4.8 per hour for an L4 and 11.8 for an A100.

| Part | Runtime | Inference or training | Envs, downloads, loads, smoke tests | Total | Units |
|---|---|---|---|---|---|
| A (a) | L4 | about 30 min | about 30 to 40 min | 1 to 1.25 h | 5 to 6 |
| A (b) | L4 | about 20 min | about 15 to 25 min | 0.6 to 0.8 h | 3 to 4 |
| A (c) | L4 | about 10 min, batch 1 about 3 to 5 min | about 20 min | about 0.5 h | 2 to 3 |
| A (d) | L4 | 2 to 2.7 h | about 15 min | 2.2 to 3 h | 11 to 14 |
| A (e) | L4 | under 1 min | about 2 min | under 0.1 h | under 0.5 |
| A in all | L4 | | | 4.4 to 5.6 h | 21 to 28 |
| B | L4 | 2.2 to 3.6 h | about 15 min | 2.4 to 3.9 h | 12 to 19 |
| C1, Gemma | A100 | verbalized 85 to 96 min, likelihood 200 to 230 min, batch 1 about 10 to 12 min | about 25 min | 5.4 to 6 h | 64 to 71 |
| C2, Mistral | A100 | verbalized 63 to 74 min, likelihood 150 to 175 min, batch 1 about 8 to 12 min | about 25 to 35 min | 4.2 to 4.9 h | 50 to 58 |
| C3, thinking | A100 | 1.2 to 4.6 h | about 15 min | 1.5 to 4.9 h | 18 to 58 |
| C3, Qwen3.6 pair | A100 | verbalized about 36 min, likelihood about 58 min | about 15 min | about 1.8 h | about 21 |
| C3 in all | A100 | | | 3.3 to 6.7 h | 39 to 79 |
| All five parts | | | | | 186 to 255 |

How the figures were reached:

- **A (a).** The third revision ran the same models on `d2_k150_oos`, 800 requests with 150 options: `laya-ml` 0.7 min, `kev-0.8b` 1.3, `decider-2b` 2.2, `this-that-1.0` 2.3, `kev-9b` 6.2 and `nimble-9b` 23.1. The 77 Banking77 intent names hold about as many tokens as the 150 CLINC names, so `d2_banking77` should take about 616/800 of those times, about 27 minutes. `d3_goemotions` should cost what `d3_emotion` cost in the first run, 4.6 minutes for all seven models. Each model loads three times (smoke test and two conditions).
- **A (b).** Key scoring took 1.0 to 1.5 minutes per backbone for the 498 `d3_emotion` requests and 7.1 to 13.6 minutes for the 800 `d2_k150` requests in the second revision. Banking77, with about half the options and 616 requests, should take about 3 to 5 minutes per backbone. The 9B downloads here are reused by (d).
- **A (c).** `comparator-open` on an L4 needed 2.1 minutes for `d3_emotion` and 15.3 minutes for the 800 `d2_k150` questions. That gives about 2 minutes for GoEmotions and about 8 for Banking77. The third revision's smoke test took 244 s including the engine start.
- **A (d).** Description scoring of the 0.8B and 2B backbones took 26.6 and 28.2 minutes in the third revision, 1.8 times their key-scoring time. Key scoring of each 9B backbone took 28 minutes on the same six conditions, so description scoring at 16 rows would take about 50 minutes. At 4 rows per pass, a `d2_k150` question needs about 38 passes instead of 10, which may double that condition's 24 minutes. That gives 60 to 80 minutes for each 9B backbone.
- **A (e).** The local Jev runs took about 0.15 to 0.2 s per request.
- **Batch-1 samples.** In the second revision, the 40 batch-1 requests of Qwen3.6-27B took 6.8 minutes verbalized and 1.8 minutes in the likelihood mode on this A100, engine starts included. Gemma and Mistral are scaled as below; Qwen3-14B-AWQ on an L4 is assumed at 3 to 5 minutes.
- **B.** No earlier run fine-tuned on an L4, and the local `b01` BERT run used a T1000. The figures count the training tokens of the frozen rows. Per epoch, `wiki_corpus` has 1.84 million, D1 3.37 million (each state repeats once per option row), `conv_go_awry` 0.65 million, and each short-text task 0.11 to 0.17 million. Every task trains 8 epochs, 2 learning rates by 4 epochs. The assumptions are 6,000 to 10,000 padded training tokens per second for the long-text tasks (31 to 51 minutes for `wiki_corpus`, 11 to 18 for `conv_go_awry`, 50 to 85 for D1), and 0.15 to 0.25 s per optimizer step for the short-text tasks (about 10,600 steps, 27 to 44 minutes). The smoke run prints the measured throughput and a per-task estimate, which shows at once whether this holds.
- **C1 and C2.** Qwen3.6-27B-FP8 on this A100 took these batch times. Verbalized: 7.2 min for `d1_neutral`, 5.4 for `d1_calib`, 7.7 for `d2_k150`, 4.6 for `d2_k20`, 1.2 to 1.7 for each D3 task, and 7.7 for `d2_k150_oos`. Likelihood: 5.9, 4.4, 48.1, 3.9, 1.1 to 2.2, and 48.6. The likelihood cost grows with the number of options, which puts Banking77 at about 20 minutes and `d2_k50` at about 12. The stress conditions are scaled by decisions and options (the `e2_d1_*` files have 600 decisions each against 2,000 in `d1_neutral`). For the 25 conditions that makes about 74 minutes verbalized and 175 minutes likelihood at Qwen3.6 speed. Gemma-4-31B is scaled by 1.15 to 1.3 for its size and Mistral-Small-24B by 0.85 to 1.0.
- **C3.** No thinking run has been measured. The 8,204 questions at 800 to 2,000 output tokens each make 6.6 to 16.4 million tokens. With up to 32 sequences at once, the engine should decode about 1,000 to 1,500 tokens per second on this A100, which gives 1.2 to 4.6 hours. The smoke test prints the measured mean output tokens and the time per question, which narrow this at once. The Qwen3.6 pair's figures are its measured times scaled as above.

## Running the parts in parallel

Every part writes only its own answer folders and its own run log (`run_log_revision4_partA.json`, `_partB`, `_partC1`, `_partC2`, `_partC3`), so the parts can run at the same time.

- **If the Colab plan allows five GPU runtimes at once, run A, B, C1, C2 and C3 together.** The longest part, C1 or C3, sets the finish, about 6 to 7 hours.
- **With fewer runtimes, keep the two L4 parts and one A100 part in each wave.** For example, run A with C1 first (about 5.5 to 6 hours), then B with C2 (about 4 to 5 hours), then C3 (3.3 to 6.7 hours).
- **If the thinking smoke test predicts more than about 3.5 hours,** part C3 can itself be split. Run one A100 runtime with `RUN_PART_C3 = True` and `RUN_QWEN36 = False`, and another with `RUN_PART_C3 = True` and `RUN_THINK = False`. Their run logs are named `C3think` and `C3qwen`.

The compute units are the same whichever way the parts are arranged, about 186 to 255 in all.

## Steps

1. In Google Drive, open `My Drive/Jev/paper4/colab/`. Upload `revision4_upload.zip` there and do not unzip it.
2. For the optional Jev latency sample, add a Colab secret named `TYPESAFE_API_KEY` (the key icon on the left) and switch on its notebook access. Without it, that one cell is skipped.
3. Open one tab per runtime, each with the notebook (File, Upload notebook, or open it again from Drive). In each tab choose the GPU (Runtime, Change runtime type), set exactly one part switch to `True` in the first code cell, then choose Runtime, Run all and allow Drive access.
   - **Part A:** an **L4 GPU**, `RUN_PART_A = True`.
   - **Part B:** an **L4 GPU**, `RUN_PART_B = True`.
   - **Part C1:** an **A100 GPU** (80 GB), `RUN_PART_C1 = True`.
   - **Part C2:** an **A100 GPU** (80 GB), `RUN_PART_C2 = True`.
   - **Part C3:** an **A100 GPU** (80 GB), `RUN_PART_C3 = True`.
   - The other part switches stay `False`. Start as many at once as the plan allows (see above).
4. In every runtime the unpack cell must print `25 input files, 5 source files and 9 training data files verified`.
5. Keep the tabs open. If a runtime disconnects, reconnect and choose Run all again with the same switches. Answers are on Drive, and finished requests and finished DeBERTa conditions are skipped.
6. The last cell of every runtime reads the shared Drive folder and lists all planned files of all five parts, then a summary per part. A part that has not run yet shows as MISSING. For each file it shows the answered count, the error lines, the longest prompt and whether the recorded revision equals the pin. When every non-optional file is complete it writes `ALL_DONE_revision4`. In every case it merges the run logs of all runtimes into `run_log_revision4.json` and writes `My Drive/Jev/paper4/colab/answers_revision4.zip` with every part's files found on Drive.
7. When the last runtime has finished, check that its status cell shows every part complete. Files that another runtime wrote in the last few minutes can take a moment to appear on this one; if a finished part shows as MISSING, run the last cell again. Then download `answers_revision4.zip` and hand it back. That archive is the only thing needed.

A model that fails writes `ERROR_revision4.txt` in its folder, and the next cell continues. A later successful attempt keeps the old marker as `ERROR_revision4_earlier.txt`. `harness.py` records a failing request as an error line and still exits normally, so every smoke test reads its own answer files. A condition counts as done only when all its requests are answered.

## What the notebook pins

| Item | Pinned to |
|---|---|
| Decision models and Qwen3-14B-AWQ | the revisions of their original answers (`build_revision_notebook.py`) |
| Qwen3.5 backbones, Qwen3.6-27B-FP8 | the revisions of `build_revision2_notebook.py` |
| Gemma-4-31B-it | `842da3794eaa0b77d5f08bae87a17459d91ff475` |
| Mistral-Small-24B-Instruct-2501 | `9527884be6e5616bdd54de542f9ae13384489724` |
| DeBERTa-v3-large | `64a8c8eab3e352a784c658aef62be1662607476f`, in `b05_strong_classifiers.py` |
| Jev | `jev-1.13.0` through `typesafe-sdk==0.7.1` |
| Decision model envs | the first revision's package lists |
| Backbone env | `torch==2.8.0`, `transformers==5.17.0`, `flash-linear-attention` optional |
| vLLM env | `vllm==0.30.0`, `VLLM_USE_FLASHINFER_SAMPLER=0`, the env's bin folder on `PATH` |
| `b05` env | `torch==2.8.0` (CUDA 12.8 wheels), `transformers==5.17.0`, `sentencepiece==0.2.2`, `protobuf` |

## After hand-back

1. Unzip `answers_revision4.zip` into `paper4/shared/answers/`. Every answer file in it is new. Its layout is `<tag>/<cond>__rep1.jsonl` (and `jev-1.13.0/d1_neutral__rep6.jsonl`), plus `<tag>/<cond>__fit.json` for the five DeBERTa tags, `<tag>/DONE_revision4` markers and the run logs.
2. Existing answer files are not touched, so every earlier result stays as it is.

## Rebuilding the package

If `adapters.py`, `harness.py`, `b05_strong_classifiers.py` or any shipped input changes, rebuild:

```
D:/p4env/venv/Scripts/python.exe build_revision4_notebook.py --check
```

The build freezes the DeBERTa training rows again from the `b01` and `b04` caches and the typed-decisions dataset, and checks the D3 rows against the lists `b04` stored. The check compiles every code cell and the shipped sources, and confirms that every name a cell uses is defined in an earlier cell. It checks each input in the zip against the manifest SHA-256, and each source and training file against the build. It also confirms that no marker or file name of the earlier runs is left in the notebook.

To test `b05_strong_classifiers.py` locally on the CPU with a tiny test model:

```
D:/p4env/venv/Scripts/python.exe b05_strong_classifiers.py freeze --out <scratch>/b05data
D:/p4env/venv/Scripts/python.exe b05_strong_classifiers.py run --smoke --device cpu --data <scratch>/b05data --answers <scratch>/smoke_answers
```
