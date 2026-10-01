"""Distribution-free risk control of the selective threshold (fourth revision).

The held-out thresholds of a09 section B target five percent risk on held-out data but give no
guarantee. This script chooses the threshold by Learn-then-Test (Angelopoulos et al., 2021) on
a fixed, data-independent grid GRID of candidate thresholds. For each t it tests
H0(t): risk(t) > alpha with the exact binomial p-value
    p(t) = P(Binomial(n_t, alpha) <= k_t),
where n_t calibration decisions have confidence at least t and k_t of them are wrong, and it
rejects where p(t) <= delta / |GRID| (Bonferroni, family-wise error at most delta). The lowest
rejected threshold is used. With probability at least 1 - delta over the calibration draw, the
risk of the accepted decisions on exchangeable new data is at most alpha. A fixed-sequence
walk from the top is not used, because for a model with continuous confidences the highest
candidates accept one or two decisions and the walk stops at once.

Splits follow a09's held-out analysis: on D1 the threshold is chosen on d1_calib and applied
to d1_neutral; on D2 (the 600 in-scope CLINC-150 items) it is chosen on four item folds and
applied to the fifth, with a09's fold map. Reported per model: the coverage and realized risk
on the scored items, and the number of accepted decisions.

Output: results/risk_control.json
"""
import numpy as np
from scipy.stats import binom

import bench
import common as C
import a09_revision_stats as R

ALPHA, DELTA = 0.05, 0.10
MODELS = [bench.JEV] + bench.MODELS_OPEN + ["comparator-open", "comparator-open2",
                                            "comparator-open2-ll", "comparator-gemma",
                                            "comparator-gemma-ll", "comparator-mistral",
                                            "comparator-mistral-ll", "comparator-open2-think"]


def conf_correct(model, cond, in_scope_only=False):
    rows = [r for r in R.dec(model, cond) if r["y"] >= 0 and not np.isnan(r["p"]).any()
            and (not in_scope_only or r["meta"].get("in_scope", True))]
    conf = np.array([float(r["p"].max()) for r in rows])
    cor = np.array([float(np.argmax(r["p"]) == r["y"]) for r in rows])
    items = np.array([r["item_id"] for r in rows])
    return conf, cor, items


# 25 linear steps from 0.50 to 0.98 and 25 log steps from 1 - 10**-2 to 1 - 10**-8, fixed in
# advance, so models whose confidences crowd near one still have usable candidates
GRID = np.unique(np.concatenate([np.round(np.arange(0.50, 0.99, 0.02), 4),
                                 1.0 - 10.0 ** -np.arange(2.0, 8.01, 0.25)]))


def ltt_threshold(conf, cor, alpha=ALPHA, delta=DELTA):
    """Lowest grid threshold whose Bonferroni-corrected binomial test rejects risk > alpha;
    inf if none does."""
    level = delta / len(GRID)
    thr = np.inf
    for t in GRID:
        acc = conf >= t
        n = int(acc.sum())
        if n == 0:
            continue
        k = int((acc & (cor == 0)).sum())
        if binom.cdf(k, n, alpha) <= level:
            thr = min(thr, float(t))
    return thr


def summarize(conf, cor, thr):
    acc = conf >= thr
    n = int(acc.sum())
    k = int((acc & (cor == 0)).sum())
    return {"coverage": n / len(conf), "accepted": n, "errors": k,
            "risk": k / n if n else None}


def main():
    out = {"alpha": ALPHA, "delta": DELTA, "grid": [float(g) for g in GRID], "d1": {}, "d2": {}}
    for m in MODELS:
        cc, kc, _ = conf_correct(m, "d1_calib")
        ct, kt, _ = conf_correct(m, "d1_neutral")
        if len(cc) and len(ct):
            t = ltt_threshold(cc, kc)
            out["d1"][m] = dict(summarize(ct, kt, t), threshold=None if np.isinf(t) else float(t))
        conf, cor, items = conf_correct(m, "d2_k150", in_scope_only=True)
        if len(conf):
            f = R.folds_of(items)
            acc = np.zeros(len(conf), bool)
            for k in range(R.FOLDS):
                t = ltt_threshold(conf[f != k], cor[f != k])
                acc[f == k] = conf[f == k] >= t
            n, e = int(acc.sum()), int((acc & (cor == 0)).sum())
            out["d2"][m] = {"coverage": n / len(conf), "accepted": n, "errors": e,
                            "risk": e / n if n else None}
        print(m, {d: (round(out[d][m]["coverage"], 3), out[d][m]["risk"] and round(out[d][m]["risk"], 3))
                  for d in ("d1", "d2") if m in out[d]}, flush=True)
    C.dump(out, "risk_control.json")


if __name__ == "__main__":
    main()
