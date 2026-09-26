"""Versioned run manifest: the immutable identifiers behind every answer file.

For every model it collects, from the answer records themselves, the resolved model
revision, the model identifier the service returned, the served temperature, the run
dates, and any environment fields the adapters recorded (package versions, GPU,
serving settings). The result is results/run_manifest.json, which the release
archives next to the raw answers and the manuscript cites.
"""
import collections
import glob
import json
import os

import common as C

FIELDS_ENV = ("env", "versions", "package_versions", "torch", "transformers", "vllm",
              "gpu", "cuda", "tokenizer_revision", "adapter_revision", "sdk_version",
              "weights_sha", "latency_mode")


def main():
    out = {}
    for mdir in sorted(glob.glob(os.path.join(C.ANSWERS, "*"))):
        if not os.path.isdir(mdir):
            continue
        model = os.path.basename(mdir)
        info = collections.defaultdict(collections.Counter)
        files = {}
        for fn in sorted(glob.glob(os.path.join(mdir, "*.jsonl"))):
            n = 0
            with open(fn, encoding="utf-8") as fh:
                for line in fh:
                    line = line.strip()
                    if not line.startswith("{"):
                        continue
                    try:
                        j = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    n += 1
                    for k in ("revision", "model_returned", "served_temperature", "run_date"):
                        if k in j:
                            info[k][json.dumps(j[k])] += 1
                    for k in FIELDS_ENV:
                        if k in j:
                            info[k][json.dumps(j[k], sort_keys=True)] += 1
                    raw = j.get("raw") if isinstance(j.get("raw"), dict) else {}
                    for k in FIELDS_ENV:
                        if k in raw:
                            info["raw." + k][json.dumps(raw[k], sort_keys=True)] += 1
            files[os.path.basename(fn)] = n
        out[model] = {k: dict(v) for k, v in info.items()}
        out[model]["records_per_file"] = files
    C.dump(out, "run_manifest.json")
    for m, v in out.items():
        print(m, {k: list(vv)[:3] for k, vv in v.items() if k != "records_per_file"})


if __name__ == "__main__":
    main()
