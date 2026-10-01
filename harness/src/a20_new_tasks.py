"""The two benchmarks of the fourth revision: GoEmotions (human-rated emotion, s00e) and Banking77
(intents with the exposure of CLINC-150 reversed, s00f).

For every model with answers, per benchmark: accuracy with a percentile bootstrap interval over
items, macro-F1 in percent, top-label calibration error as shipped, and the paired accuracy
difference from Jev on identical items (a14.paired: paired bootstrap over items, two-sided p),
Holm-adjusted across all models compared with Jev on that benchmark. Parse failures of the
generative readouts count as uniform distributions (bench.decisions).

Output: results/new_tasks.json
"""
import numpy as np

import bench
import common as C
import metrics as M
from a14_baseline_paired import cmap, holm, paired

CONDS = ["d3_goemotions", "d2_banking77"]
MODELS = ([bench.JEV] + bench.MODELS_OPEN + ["comparator-open"]
          + bench.COMPARATORS_2 + bench.BACKBONES
          + ["baseline-nli-deberta-v3-base", "baseline-bge-small-lr-goemo",
             "baseline-bge-small-lr-banking", "baseline-deberta-large-goemo",
             "baseline-deberta-large-banking"])


def summary(model, cond):
    rows = [r for r in bench.decisions(model, cond) if r["y"] >= 0 and not np.isnan(r["p"]).any()]
    if not rows:
        return None
    P = np.array([r["p"] for r in rows])
    y = np.array([r["y"] for r in rows])
    cor = (P.argmax(1) == y).astype(float)
    rng = np.random.default_rng(C.SEED)
    boots = [cor[rng.integers(0, len(cor), len(cor))].mean() for _ in range(2000)]
    return {"n": len(rows), "accuracy": float(cor.mean()),
            "accuracy_ci": [float(v) for v in np.percentile(boots, [2.5, 97.5])],
            "macro_f1": 100 * C.macro_f1(P, y, P.shape[1]),
            "ece_shipped": M.ece(P.max(1), cor),
            "parse_failed": int(sum(r.get("parse_failed", False) for r in rows))}


def main():
    out = {}
    for cond in CONDS:
        res = {}
        for m in bench.present(MODELS):
            if bench.available_reps(m, cond):
                s = summary(m, cond)
                if s:
                    res[m] = s
        J = cmap(bench.JEV, cond)
        tests = {}
        for m in res:
            if m == bench.JEV:
                continue
            r = paired(cmap(m, cond), J, C.SEED)
            if r:
                tests[m] = r
        for (m, v), a in zip(tests.items(), holm([v["p"] for v in tests.values()])):
            v["holm"] = a
            res[m]["vs_jev"] = v
        out[cond] = res
        print(cond, {m: round(v["accuracy"], 3) for m, v in res.items()}, flush=True)
    C.dump(out, "new_tasks.json")


if __name__ == "__main__":
    main()
