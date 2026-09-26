# Harness

This folder holds the same-harness evaluation of the benchmark paper, *Six Decision Models, One Harness*. Every model receives the same semantic request in the TypeSafe `/v1/systemone` wire format, with the same state, question and option texts in the same order. The rendering into tokens is each model's own, and `results/analysis/rendering_examples.json` shows it for every family.

## Layout

| Path | Contents |
|---|---|
| `src/s00b_prepare_d3.py` | Rebuilds the four D3 social-science tasks from their public sources at pinned commits. |
| `src/s00_freeze_inputs.py` | Freezes every condition (D1 typed-decisions, D2 CLINC-150, D3, E2 naming conditions) into `inputs/*.jsonl`, with the SHA-256 manifest `inputs/manifest.json`. |
| `src/harness.py` | The runner. Output is append-only JSONL with resume. It includes the Jev backend (model pinned to `jev-1.13.0`) and a generic `/v1/systemone` HTTP backend. |
| `src/adapters.py` | In-process backends for Laya (English and multilingual), Kev-0.8B, Kev-9B, decider-2b, this-that-model-1.0, Nimble-9B and the vLLM comparator. Each backend pins its Hugging Face revision and records the served temperature and the T = 1 probabilities. |
| `src/a01`–`a08_*.py` | The analyses behind E1 to E6, plus retest, exposure and paired tests. `collect_numbers.py` builds `numbers.json`. |
| `src/a09`–`a13_*.py` | The revision analyses: clustered and Holm-corrected paired tests, out-of-fold cascades with itemwise costs, distractor permutations, the Laya token budget, the run manifest and the rendering comparison. |
| `src/b01`–`b03_*.py` | Conventional baselines (trained CLINC-150 and typed-decisions classifiers, zero-shot NLI), the CLINC-150 exposure audit and the license audit. |
| `src/s00c_freeze_permutations.py` | Freezes the two extra distractor permutations of the D2 cardinality conditions. |
| `src/f07`–`f12_*.py`, `src/t01_tables.py` | Figures and tables. |
| `colab/run_open.ipynb`, `colab/run_comparator.ipynb`, `colab/run_revision.ipynb` | The Colab notebooks that ran the open models, the comparator and the revision runs on an NVIDIA L4. |
| `colab/cards/` | The model and dataset cards as read on 2026-09-24. |
| `inputs/*.jsonl.gz` | The frozen D1 and D2 requests. `manifest.json` lists the digest of each uncompressed file, D3 included. |
| `inputs/d3_item_ids.json` | The item identifiers of every D3 condition. The D3 texts are not redistributed, and step 1 below rebuilds them. |

## Reproduce

1. Build the inputs:
   ```
   python src/s00b_prepare_d3.py
   python src/s00_freeze_inputs.py
   ```
   Then check the digests against `inputs/manifest.json`.
2. Run a model:
   ```
   python src/harness.py --model jev --cond all --rep 1
   ```
   Running the hosted model needs `TYPESAFE_API_KEY`. For the open models, use the notebooks.
3. Run `a01` to `a08`, then `collect_numbers.py`, then the figure and table scripts.
