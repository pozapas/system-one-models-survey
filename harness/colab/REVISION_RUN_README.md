# Revision runs of the open models on Colab

This run answers two reviewer points for the open models. Jev's part is already done locally.

1. **Option count.** Each open model runs on two more independent option permutations of the cardinality sweep: `d2_k{5,20,50,150}_p2` and `d2_k{5,20,50,150}_p3`.
2. **Rendering.** this-that-1.0 runs on `d1_neutral` and `d2_k150` with each option given as its description alone, without the key. The answer tag is `this-that-1.0-desc`.

It also runs a rep-2 retest of every open model on `e2_d3_conv_go_awry_kny` and `e2_d3_wiki_corpus_kny`. That gives the binary D3 sets the same run-to-run floor that Jev already has.

## What to upload

Both files are in `paper4/shared/colab/`:

| File | Contents |
|---|---|
| `revision_upload.zip` | 3.7 MB: the source files `common.py`, `harness.py` and `adapters.py`, the 14 input files the run needs, and `manifest.json` |
| `run_revision.ipynb` | the notebook |

The zip's SHA-256 is printed by `build_revision_notebook.py` and embedded in the notebook. The notebook also checks every file inside the zip against its SHA-256 and stops if one differs.

## Steps

1. In Google Drive, open `My Drive/Jev/paper4/colab/`, the same folder as the first run. Upload `revision_upload.zip` there. Do not unzip it.
2. Open `run_revision.ipynb` in Colab: File, Upload notebook, or open it from Drive.
3. Choose Runtime, Change runtime type, **L4 GPU**, then save.
4. Choose Runtime, Run all, and allow the Drive access request.
   - The first cell mounts Drive.
   - The unpack cell must print `14 input files and 3 source files verified`.
   - Each model cell prints its env build, a 5-request smoke test with a time estimate, and then one line per condition.
5. Keep the browser tab open.
   - If the runtime disconnects, reconnect and choose Run all again. Answers are written line by line to Drive, and finished requests are skipped.
   - If one model ends with `ERROR_revision.txt`, the others still run. Re-running that model's cell resumes it.
6. The last cell lists every planned answer file, its count of answered requests, and whether its recorded revision equals the pin.
   - When everything is complete, it writes `ALL_DONE_revision`.
   - In every case it writes `My Drive/Jev/paper4/colab/answers_revision.zip`.
7. Download `answers_revision.zip` from Drive and hand it back. That archive is the only thing needed.

The comparator is optional and off by default. To run it, set `RUN_COMPARATOR = True` in its cell before Run all. It covers the eight permutation conditions plus `d2_k5` and `d2_k50`, and it adds about 1.5 hours and 7 compute units.

## Expected time and compute units

These estimates come from the per-request latencies each model recorded on the L4 in the first run, for the same conditions. The inference times are:

| Model | Minutes |
|---|---|
| laya-en | 3 |
| laya-ml | 3 |
| kev-0.8b | 7 |
| decider-2b | 9 |
| this-that-1.0, including this-that-1.0-desc | 11 |
| kev-9b | 19 |
| nimble-9b | 57 |
| **Total** | **about 110** |

Env builds, weight downloads (about 50 GB in all), and one model load per condition add roughly 1 to 1.5 hours. Expect about 3 to 3.5 hours in total. At 4.8 compute units per hour on an L4, that is about 15 to 17 compute units. The 4.8 per hour rate is the assumption the first notebook also used; it was not measured. Each model cell prints its own estimate after its smoke test.

## What the notebook pins

| Item | Pinned to |
|---|---|
| Model weights | The revision recorded in the original answer files of each model, through the `P4_REVISIONS` variable read by `adapters.py`. The first run's `run_log.json` holds no revisions, so the pins were taken from the `revision` field of `shared/answers/<tag>/*.jsonl`. |
| laya-en and laya-ml | `convaiinnovations/laya@55cf4c4e` |
| kev-0.8b | `9a45d25e` |
| kev-9b | `2629c06a` |
| decider-2b | `d61c1c16` |
| this-that-1.0 | `3d927195` |
| nimble-9b | `bd792f44` |
| comparator | `Qwen/Qwen3-14B-AWQ@31c69efc` |
| Packages | The same as the first run: `laya==0.3.20`, kev at GitHub commit `73504e51`, thisthat at commit `542d445e`, `torch==2.8.0` from the CUDA 12.8 wheel index, and the Nimble pins |

## After hand-back

1. Unzip `answers_revision.zip` into `paper4/shared/answers/`.
   - Its layout is `<tag>/<cond>__rep<k>.jsonl`, the same as the existing folders.
   - Every file name in it is new, so nothing existing is overwritten.
   - Besides the answer files, it holds `<tag>/DONE_revision` markers and `run_log_revision.json`.
   - The per-model console logs (`run_log_<tag>.txt`) and any `ERROR_revision.txt` stay on Drive, for troubleshooting only.
2. From `paper4/shared/src`, run:

   ```
   D:/p4env/venv/Scripts/python.exe a10_permutations.py
   D:/p4env/venv/Scripts/python.exe a05_retest.py
   D:/p4env/venv/Scripts/python.exe a11_laya_budget.py
   ```

   - `a10_permutations.py` fills in the open models in `results/e3_permutations.json` and writes the this-that rendering comparison.
   - `a05_retest.py` adds the open-model D3 floors to `results/retest.json`.
   - `a11_laya_budget.py` checks the Laya replay against the new Laya answers.

## Rebuilding the package

If `adapters.py`, `harness.py` or any shipped input changes, rebuild both files:

```
D:/p4env/venv/Scripts/python.exe build_revision_notebook.py --check
```

The builder never rebuilds `run_open.ipynb` or `run_comparator.ipynb`.
