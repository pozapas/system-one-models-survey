"""Paired comparisons of every open decision model (and the comparator) against the hosted
model on identical decisions: accuracy difference with a state-clustered paired bootstrap
interval and an exact McNemar test, per main condition, plus the pooled D3 difference.

Output: results/paired.json
"""
import numpy as np

import bench
import common as C
import metrics as M

CONDS = ["d1_neutral", "d2_k150", "d3_conv_go_awry", "d3_wiki_corpus", "d3_emotion",
         "d3_wiki_politeness"]
OTHERS = bench.MODELS_OPEN + ["comparator-open"]


def correct_map(model, cond):
    return {(r["item_id"], r["qid"]): float(np.argmax(r["p"]) == r["y"])
            for r in bench.decisions(model, cond)
            if r["y"] >= 0 and not np.isnan(r["p"]).any()}


def compare(a, b):
    keys = sorted(set(a) & set(b))
    if len(keys) < 30:
        return None
    ca = np.array([a[k] for k in keys])
    cb = np.array([b[k] for k in keys])
    groups = np.array([k[0] for k in keys])
    diff = cb - ca
    lo, hi = M.cluster_boot(lambda i: diff[i].mean(), groups)
    mc = M.mcnemar(ca.astype(bool), cb.astype(bool))
    return {"n": len(keys), "acc_jev": float(ca.mean()), "acc_other": float(cb.mean()),
            "diff": float(diff.mean()), "diff_ci": [lo, hi], "mcnemar_p": mc["p"]}


def main():
    res = {}
    for m in OTHERS:
        pooled_a, pooled_b = {}, {}
        for cond in CONDS:
            if not (bench.available_reps(m, cond) and bench.available_reps(bench.JEV, cond)):
                continue
            a, b = correct_map(bench.JEV, cond), correct_map(m, cond)
            c = compare(a, b)
            if c:
                res[f"{m}|{cond}"] = c
                print(f"{m:16s} {cond:20s} diff={c['diff']:+.3f} [{c['diff_ci'][0]:+.3f},"
                      f"{c['diff_ci'][1]:+.3f}] p={c['mcnemar_p']:.2g}")
            if cond.startswith("d3"):
                pooled_a.update({(cond,) + k: v for k, v in a.items()})
                pooled_b.update({(cond,) + k: v for k, v in b.items()})
        if pooled_a:
            # group by task and item so the bootstrap resamples items within the pool
            pa = {(k[0] + ":" + k[1], k[2]): v for k, v in pooled_a.items()}
            pb = {(k[0] + ":" + k[1], k[2]): v for k, v in pooled_b.items()}
            c = compare(pa, pb)
            if c:
                res[f"{m}|d3_pooled"] = c
                print(f"{m:16s} {'d3_pooled':20s} diff={c['diff']:+.3f}")
    C.dump(res, "paired.json")


if __name__ == "__main__":
    main()
