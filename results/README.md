# Results

This folder holds the results of the benchmark paper, *Six Decision Models, One Harness*.

| Path | Contents |
|---|---|
| `answers/<model>/<condition>__rep<r>.jsonl.gz` | Every raw answer, one line per request. Each line records the model, the pinned revision, the served temperature, the run date, the latency, the input tokens where reported, the request hash, and the probabilities per option. For the open models it also records the T = 1 probabilities in `raw.probs_t1`. |
| `answers/SHA256SUMS.txt` | The SHA-256 digest of each uncompressed answer file. |
| `answers/run_log.json`, `answers/run_log_revision.json` | The Colab runtime of the open-model run and of the revision run (GPU and driver). |
| `answers/baseline-*/` | The answers of the conventional baselines in the same format. |
| `answers/this-that-1.0-desc/` | this-that-model-1.0 rerun with option descriptions alone. |
| `analysis/*.json` | One file per analysis: `e1_main`, `e2_names`, `e3_cardinality`, `cost_latency`, `retest`, `e6_cascade`, `exposure`, `paired`, and from the revision `revision_stats`, `baselines`, `e3_permutations`, `laya_budget`, `render_paired`, `rendering_examples`, `clinc_overlap`, `licenses_audit` and `run_manifest`. |
| `analysis/numbers.json` | Every number cited in either manuscript, with its source. |

## Scope and dates

The hosted model (`jev-1.13.0`) was queried on 2026-09-24, with three repeats of every condition. The open models ran on 2026-09-24 and the comparator (Qwen3-14B-AWQ) on 2026-09-25, all on one NVIDIA L4 in Google Colab. The baselines ran on 2026-09-25, and the distractor permutations, the description-only rerun and the added naming retests ran on 2026-09-26.
