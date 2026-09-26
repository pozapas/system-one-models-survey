"""Metrics of the benchmark: calibration, scoring rules, selective prediction.

Every quantity here is computed from top-label probabilities or full distributions
over the options of each decision. Intervals are percentile bootstraps that resample
states (clusters), because the questions asked about one state are dependent.
"""
import numpy as np

import common as C

EPS = 1e-6


def norm(P):
    P = np.clip(np.asarray(P, dtype=float), EPS, None)
    return P / P.sum(-1, keepdims=True)


# ------------------------------------------------------------------ calibration

def ece(conf, correct, bins=10):
    """Top-label expected calibration error with equal-mass bins."""
    conf, correct = np.asarray(conf), np.asarray(correct, dtype=float)
    n = len(conf)
    if n == 0:
        return np.nan
    order = np.argsort(conf, kind="mergesort")
    edges = np.linspace(0, n, bins + 1).round().astype(int)
    tot = 0.0
    for a, b in zip(edges[:-1], edges[1:]):
        if b > a:
            idx = order[a:b]
            tot += (b - a) / n * abs(conf[idx].mean() - correct[idx].mean())
    return float(tot)


def reliability(conf, correct, bins=10):
    conf, correct = np.asarray(conf), np.asarray(correct, dtype=float)
    n = len(conf)
    order = np.argsort(conf, kind="mergesort")
    edges = np.linspace(0, n, bins + 1).round().astype(int)
    out = []
    for a, b in zip(edges[:-1], edges[1:]):
        if b > a:
            idx = order[a:b]
            out.append({"n": int(b - a), "conf": float(conf[idx].mean()),
                        "acc": float(correct[idx].mean())})
    return out


def brier_multi(P, y):
    """Multi-class Brier score, sum over options, mean over decisions (0 to 2)."""
    return float(np.mean([np.sum((p - np.eye(len(p))[k]) ** 2) for p, k in zip(P, y)]))


def nll(P, y):
    return float(np.mean([-np.log(max(p[k], EPS)) for p, k in zip(P, y)]))


def murphy(conf, correct, bins=10):
    """Murphy decomposition of the top-label Brier score, (conf - correct)^2, on
    equal-mass bins: reliability - resolution + uncertainty (plus a small binning
    residual, which is reported)."""
    conf, correct = np.asarray(conf), np.asarray(correct, dtype=float)
    n = len(conf)
    bs = float(np.mean((conf - correct) ** 2))
    obar = correct.mean()
    order = np.argsort(conf, kind="mergesort")
    edges = np.linspace(0, n, bins + 1).round().astype(int)
    rel = res = 0.0
    for a, b in zip(edges[:-1], edges[1:]):
        if b > a:
            idx = order[a:b]
            w = (b - a) / n
            rel += w * (conf[idx].mean() - correct[idx].mean()) ** 2
            res += w * (correct[idx].mean() - obar) ** 2
    unc = obar * (1 - obar)
    return {"brier_top": bs, "reliability": float(rel), "resolution": float(res),
            "uncertainty": float(unc), "residual": float(bs - (rel - res + unc))}


# ------------------------------------------------------------------ temperature

def apply_T(p, T):
    q = np.exp(np.log(np.clip(p, EPS, None)) / T)
    return q / q.sum()


def fit_T(Ps, ys, grid=None):
    """One temperature minimizing NLL over decisions that may differ in option count."""
    grid = grid if grid is not None else np.exp(np.linspace(np.log(0.2), np.log(20), 120))
    logs = [np.log(np.clip(p, EPS, None)) for p in Ps]
    best, bt = np.inf, 1.0
    for T in grid:
        v = 0.0
        for lp, k in zip(logs, ys):
            z = lp / T
            z = z - z.max()
            v -= z[k] - np.log(np.exp(z).sum())
        if v < best:
            best, bt = v, float(T)
    return bt


def crossfit_T(Ps, ys, groups, folds=5, seed=C.SEED):
    """Out-of-fold temperature scaling: each fold is scaled with a temperature fitted
    on the other folds, with folds disjoint by group."""
    rng = np.random.default_rng(seed)
    ug = np.unique(groups)
    rng.shuffle(ug)
    fold_of = {g: i % folds for i, g in enumerate(ug)}
    f = np.array([fold_of[g] for g in groups])
    out = [None] * len(Ps)
    Ts = []
    for k in range(folds):
        tr = np.where(f != k)[0]
        te = np.where(f == k)[0]
        T = fit_T([Ps[i] for i in tr], [ys[i] for i in tr])
        Ts.append(T)
        for i in te:
            out[i] = apply_T(Ps[i], T)
    return out, Ts


# ------------------------------------------------------------------ selective prediction

def risk_coverage(conf, correct):
    """Risk-coverage curve accepting decisions in order of decreasing confidence.
    Ties are accepted together, so the curve is defined by thresholds."""
    conf, correct = np.asarray(conf), np.asarray(correct, dtype=float)
    order = np.argsort(-conf, kind="mergesort")
    c, e = conf[order], 1 - correct[order]
    n = len(c)
    cum_err = np.cumsum(e)
    idx = np.r_[np.where(np.diff(c) != 0)[0], n - 1]      # last index of each tie block
    cov = (idx + 1) / n
    risk = cum_err[idx] / (idx + 1)
    thr = c[idx]
    return cov, risk, thr


def aurc(conf, correct):
    cov, risk, _ = risk_coverage(conf, correct)
    # step integral over coverage
    widths = np.diff(np.r_[0.0, cov])
    return float(np.sum(widths * risk))


def coverage_at_risk(conf, correct, target):
    """Largest coverage whose accepted-set risk is at most target, and its threshold."""
    cov, risk, thr = risk_coverage(conf, correct)
    ok = np.where(risk <= target)[0]
    if len(ok) == 0:
        return 0.0, None
    i = ok[np.argmax(cov[ok])]
    return float(cov[i]), float(thr[i])


def auroc(score, label):
    """Mann-Whitney AUROC with ties counted half."""
    score, label = np.asarray(score, dtype=float), np.asarray(label).astype(bool)
    pos, neg = score[label], score[~label]
    if len(pos) == 0 or len(neg) == 0:
        return np.nan
    from scipy.stats import rankdata
    r = rankdata(np.r_[pos, neg])
    return float((r[:len(pos)].sum() - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg)))


# ------------------------------------------------------------------ intervals

def cluster_boot(stat, groups, reps=1000, seed=C.SEED):
    """Percentile interval of stat(idx) under resampling of clusters."""
    rng = np.random.default_rng(seed)
    groups = np.asarray(groups)
    ug, inv = np.unique(groups, return_inverse=True)
    members = [np.where(inv == g)[0] for g in range(len(ug))]
    vals = []
    for _ in range(reps):
        pick = rng.integers(0, len(ug), len(ug))
        idx = np.concatenate([members[g] for g in pick])
        v = stat(idx)
        if v is not None and not np.isnan(v):
            vals.append(v)
    lo, hi = np.percentile(vals, [2.5, 97.5])
    return float(lo), float(hi)


def clopper_pearson(k, n, alpha=0.05):
    from scipy.stats import beta
    lo = 0.0 if k == 0 else beta.ppf(alpha / 2, k, n - k + 1)
    hi = 1.0 if k == n else beta.ppf(1 - alpha / 2, k + 1, n - k)
    return float(lo), float(hi)


def mcnemar(a_correct, b_correct):
    """Exact McNemar test on paired correctness."""
    from scipy.stats import binomtest
    a, b = np.asarray(a_correct, bool), np.asarray(b_correct, bool)
    n01 = int(np.sum(a & ~b))
    n10 = int(np.sum(~a & b))
    if n01 + n10 == 0:
        return {"n01": n01, "n10": n10, "p": 1.0}
    return {"n01": n01, "n10": n10,
            "p": float(binomtest(n01, n01 + n10, 0.5).pvalue)}


def macro_f1(pred, y, k):
    pred, y = np.asarray(pred), np.asarray(y)
    fs = []
    for c in range(k):
        tp = np.sum((pred == c) & (y == c))
        fp = np.sum((pred == c) & (y != c))
        fn = np.sum((pred != c) & (y == c))
        if tp + fp + fn == 0:
            continue
        fs.append(0.0 if tp == 0 else 2 * tp / (2 * tp + fp + fn))
    return float(np.mean(fs))
