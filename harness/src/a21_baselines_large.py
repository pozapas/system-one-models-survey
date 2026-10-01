"""Metrics of the fourth-revision baselines with b01's evaluate(), in b01's format.

The DeBERTa-v3-large classifiers fine-tuned by b05 (on D1 with soft labels, CLINC-150, the four
D3 tasks, GoEmotions and Banking77) and the small embedding classifiers of b06/b07 on GoEmotions
and Banking77 are scored exactly as the earlier baselines: accuracy with its cluster interval,
calibration error as shipped and after the temperature each baseline fitted on held-out data
(read from its answer records), Brier score, NLL, coverage at five percent risk, out-of-scope
AUROC on CLINC-150, soft accuracy on D1 and macro-F1 on the D3-style tasks.

Output: results/baselines_large.json (same structure as results/baselines.json)
"""
import json
import os

import bench
import common as C
import b01_baselines as B1

RUNS = {"deberta-large-d1": ("baseline-deberta-large-d1", ["d1_neutral"]),
        "deberta-large-clinc": ("baseline-deberta-large-clinc", ["d2_k150"]),
        "deberta-large-d3": ("baseline-deberta-large-d3", ["d3_conv_go_awry", "d3_wiki_corpus",
                                                           "d3_emotion", "d3_wiki_politeness"]),
        "deberta-large-goemo": ("baseline-deberta-large-goemo", ["d3_goemotions"]),
        "deberta-large-banking": ("baseline-deberta-large-banking", ["d2_banking77"]),
        "bge-small-lr-goemo": ("baseline-bge-small-lr-goemo", ["d3_goemotions"]),
        "bge-small-lr-banking": ("baseline-bge-small-lr-banking", ["d2_banking77"])}


def fitted_T(model, cond):
    """The held-out temperature each answer record carries: one value, or one per question
    type on D1."""
    path = os.path.join(C.ANSWERS, model, f"{cond}__rep1.jsonl")
    inp = {r["key"]: r for r in bench.inputs(cond)}
    per_type = {}
    for line in open(path, encoding="utf-8"):
        j = json.loads(line)
        for qid, a in j["answers"].items():
            T = (a.get("raw") or {}).get("fitted_temperature")
            if T is not None:
                per_type.setdefault(inp[j["key"]]["gold"][qid]["type"], T)
    if not per_type:
        return 1.0
    vals = set(per_type.values())
    return vals.pop() if len(vals) == 1 and not cond.startswith("d1") else per_type


def main():
    out = {}
    for tag, (model, conds) in RUNS.items():
        if not bench.present([model]):
            continue
        B1.TAGS[tag] = model
        out[tag] = {"answers_dir": f"shared/answers/{model}"}
        for cond in conds:
            if not bench.available_reps(model, cond):
                continue
            T = fitted_T(model, cond)
            out[tag][cond] = B1.evaluate(tag, cond, ("fixed", T, "held-out temperature of b05/b06/b07"))
            # median batch-1 latency that b05 timed on its Colab L4 (per state on D1)
            fit = os.path.join(C.ANSWERS, model, f"{cond}__fit.json")
            if os.path.exists(fit):
                lat = json.load(open(fit, encoding="utf-8")).get("latency_s_batch1_p50")
                if lat is not None:
                    out[tag][cond]["latency_ms_p50_l4"] = 1000 * lat
            print(tag, cond, round(out[tag][cond]["acc"], 3), flush=True)
    C.dump(out, "baselines_large.json")


if __name__ == "__main__":
    main()
