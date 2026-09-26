"""Test-retest agreement: how often a repeated identical request changes the answer.

For every model and condition with at least two repeats, this reports the share of
decisions whose top option changes between repeats, the mean absolute change in the
top probability, and the share of requests whose full distribution is bit-identical.
Jev has three repeats of every condition and five on the 40-state subset of
d1_neutral; the open models have a second repeat on that subset only.

Output: results/retest.json
"""
import itertools

import numpy as np

import bench
import common as C

MODELS = [bench.JEV] + bench.MODELS_OPEN + ["comparator-open"]


def pair_stats(model, cond, r1, r2, only=None):
    a = {(r["item_id"], r["qid"]): r["p"] for r in bench.decisions(model, cond, r1)
         if not np.isnan(r["p"]).any()}
    b = {(r["item_id"], r["qid"]): r["p"] for r in bench.decisions(model, cond, r2)
         if not np.isnan(r["p"]).any()}
    keys = sorted(set(a) & set(b))
    if only is not None:
        keys = [k for k in keys if k[0] in only]
    if not keys:
        return None
    flip = np.mean([np.argmax(a[k]) != np.argmax(b[k]) for k in keys])
    dtop = np.mean([abs(a[k].max() - b[k].max()) for k in keys])
    same = np.mean([np.array_equal(a[k], b[k]) for k in keys])
    return {"n": len(keys), "flip_rate": float(flip), "mean_abs_dtop": float(dtop),
            "identical_share": float(same)}


def main():
    import json
    import os
    man = json.load(open(os.path.join(C.INPUTS, "manifest.json"), encoding="utf-8"))
    subset = set(man["_retest_subset"]["item_ids"])
    res = {}
    for m in MODELS:
        mres = {}
        for cond in [c for c in man if not c.startswith("_")]:
            reps = bench.available_reps(m, cond)
            if len(reps) < 2:
                continue
            only = subset if cond == "d1_neutral" else None
            stats = [pair_stats(m, cond, x, y, only) for x, y in itertools.combinations(reps, 2)]
            stats = [s for s in stats if s]
            if not stats:
                continue
            mres[cond] = {"pairs": len(stats),
                          "flip_rate": float(np.mean([s["flip_rate"] for s in stats])),
                          "mean_abs_dtop": float(np.mean([s["mean_abs_dtop"] for s in stats])),
                          "identical_share": float(np.mean([s["identical_share"] for s in stats])),
                          "n": stats[0]["n"]}
        if mres:
            allf = [v["flip_rate"] for v in mres.values()]
            mres["_overall"] = {"median_flip_rate": float(np.median(allf)),
                                "max_flip_rate": float(np.max(allf))}
            res[m] = mres
            print(m, {k: round(v.get("flip_rate", v.get("median_flip_rate")), 4)
                      for k, v in mres.items()})
    C.dump(res, "retest.json")


if __name__ == "__main__":
    main()
