"""Paired comparisons for the rendering-sensitivity run of this-that-model-1.0.

Compares the description-only rendering (this-that-1.0-desc) with the original
key-plus-description rendering and with the hosted model on d1_neutral and on the
in-scope d2_k150 items: accuracy difference with a paired cluster-bootstrap interval
and a two-sided bootstrap p-value, clusters being states or items as elsewhere.
Output: results/render_paired.json
"""
import numpy as np

import bench
import common as C

REPS = 10000


def correct_map(model, cond):
    return {r["key"] + "|" + r["qid"]: (float(np.argmax(r["p"]) == r["y"]), r["item_id"])
            for r in bench.decisions(model, cond)
            if r["y"] >= 0 and not np.isnan(r["p"]).any()}


def paired(a, b, cond, seed=C.SEED):
    A, B = correct_map(a, cond), correct_map(b, cond)
    keys = sorted(set(A) & set(B))
    ca = np.array([A[k][0] for k in keys]); cb = np.array([B[k][0] for k in keys])
    items = np.array([A[k][1] for k in keys])
    d = ca - cb
    ug, inv = np.unique(items, return_inverse=True)
    sums = np.bincount(inv, weights=d); cnt = np.bincount(inv)
    rng = np.random.default_rng(seed)
    boots = np.empty(REPS)
    for i in range(REPS):
        pick = rng.integers(0, len(ug), len(ug))
        boots[i] = sums[pick].sum() / cnt[pick].sum()
    diff = d.mean()
    lo, hi = np.percentile(boots, [2.5, 97.5])
    p = min(1.0, 2 * min((boots <= 0).mean(), (boots >= 0).mean()))
    return {"n": int(len(keys)), "acc_a": float(ca.mean()), "acc_b": float(cb.mean()),
            "diff_points": float(100 * diff), "lo": float(100 * lo), "hi": float(100 * hi),
            "p": float(max(p, 1 / REPS))}


def main():
    out = {}
    for cond in ("d1_neutral", "d2_k150"):
        out[cond] = {
            "desc_vs_original": paired("this-that-1.0-desc", "this-that-1.0", cond),
            "desc_vs_jev": paired("this-that-1.0-desc", bench.JEV, cond),
            "original_vs_jev": paired("this-that-1.0", bench.JEV, cond),
        }
        print(cond, {k: (round(v["diff_points"], 1), round(v["lo"], 1), round(v["hi"], 1),
                         round(v["p"], 4)) for k, v in out[cond].items()})
    C.dump(out, "render_paired.json")


if __name__ == "__main__":
    main()
