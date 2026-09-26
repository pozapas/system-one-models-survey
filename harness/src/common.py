"""Shared paths, metrics and calibration helpers for the benchmark.

Adapted from paper3/src/common.py. Every analysis script imports this first,
because it sets the BLAS thread limits before numpy is imported.
"""
import os

for _v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[_v] = "1"

import json
import pickle

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # paper4/shared/
BASE = os.path.dirname(os.path.dirname(ROOT))                         # project root
DATA = os.path.join(ROOT, "data")
INPUTS = os.path.join(ROOT, "colab", "inputs")
ANSWERS = os.path.join(ROOT, "answers")
RESULTS = os.path.join(ROOT, "results")
FIGURES = os.path.join(ROOT, "figures")
TABLES = os.path.join(ROOT, "tables")

MODEL = "jev-1.13.0"
PRICE_PER_MTOK = 0.042      # USD per million input tokens, docs.typesafe.ai, accessed 2026-09-24

SEED = 20260924


def _p(*parts):
    return os.path.join(BASE, *parts)


def ensure_dirs():
    for d in (RESULTS, FIGURES, TABLES):
        os.makedirs(d, exist_ok=True)


def dump(obj, name):
    """Write a result file incrementally so a crash does not cost the sweep."""
    ensure_dirs()
    path = os.path.join(RESULTS, name)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, indent=2, sort_keys=True, default=_jsonable)
    os.replace(tmp, path)
    return path


def _jsonable(o):
    if isinstance(o, (np.floating,)):
        return float(o)
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    raise TypeError(repr(o))


def normalize(P):
    P = np.clip(np.asarray(P, dtype=float), 1e-6, None)
    return P / P.sum(1, keepdims=True)


# ------------------------------------------------------------------ metrics

def nll(P, y):
    P = normalize(P)
    return float(-np.mean(np.log(P[np.arange(len(y)), y])))


def brier(P, y):
    P = normalize(P)
    Y = np.zeros_like(P)
    Y[np.arange(len(y)), y] = 1.0
    return float(np.mean(np.sum((P - Y) ** 2, axis=1)))


def accuracy(P, y):
    return float(np.mean(np.argmax(P, 1) == y))


def macro_f1(P, y, k):
    pred = np.argmax(P, 1)
    fs = []
    for c in range(k):
        tp = np.sum((pred == c) & (y == c))
        fp = np.sum((pred == c) & (y != c))
        fn = np.sum((pred != c) & (y == c))
        fs.append(0.0 if tp == 0 else 2 * tp / (2 * tp + fp + fn))
    return float(np.mean(fs))


def ece_equal_mass(P, y, bins=10):
    """Expected calibration error of the top-class probability, equal-mass bins."""
    P = normalize(P)
    conf = P.max(1)
    correct = (np.argmax(P, 1) == y).astype(float)
    order = np.argsort(conf)
    n = len(conf)
    edges = [int(round(i * n / bins)) for i in range(bins + 1)]
    tot = 0.0
    for a, b in zip(edges[:-1], edges[1:]):
        if b <= a:
            continue
        idx = order[a:b]
        tot += (b - a) / n * abs(conf[idx].mean() - correct[idx].mean())
    return float(tot)


def reliability(P, y, bins=10):
    """Equal-mass reliability curve of the top-class probability."""
    P = normalize(P)
    conf = P.max(1)
    correct = (np.argmax(P, 1) == y).astype(float)
    order = np.argsort(conf)
    n = len(conf)
    edges = [int(round(i * n / bins)) for i in range(bins + 1)]
    out = []
    for a, b in zip(edges[:-1], edges[1:]):
        if b <= a:
            continue
        idx = order[a:b]
        out.append({"n": int(b - a),
                    "mean_confidence": float(conf[idx].mean()),
                    "observed_accuracy": float(correct[idx].mean())})
    return out


def scores(P, y, k):
    return {"nll": nll(P, y), "brier": brier(P, y), "accuracy": accuracy(P, y),
            "macro_f1": macro_f1(P, y, k), "ece": ece_equal_mass(P, y)}


def bootstrap_nll(P, y, groups, reps=400, seed=SEED):
    """Cluster bootstrap over pedestrians, because rows within a pedestrian are dependent."""
    rng = np.random.default_rng(seed)
    uniq = np.unique(groups)
    index = {g: np.where(groups == g)[0] for g in uniq}
    vals = []
    for _ in range(reps):
        pick = rng.choice(uniq, size=len(uniq), replace=True)
        idx = np.concatenate([index[g] for g in pick])
        vals.append(nll(P[idx], y[idx]))
    lo, hi = np.percentile(vals, [2.5, 97.5])
    return float(lo), float(hi)


# ------------------------------------------- temperature scaling and fitting

def apply_T(P, T):
    Q = np.exp(np.log(normalize(P)) / T)
    return Q / Q.sum(1, keepdims=True)


def fit_T(P, y, grid=None):
    grid = grid if grid is not None else np.exp(np.linspace(np.log(0.25), np.log(8.0), 60))
    best, bt = np.inf, 1.0
    for T in grid:
        v = nll(apply_T(P, T), y)
        if v < best:
            best, bt = v, float(T)
    return bt


def group_folds(groups, n_splits=5, seed=SEED):
    """Grouped folds balanced by size, shuffled so fold membership is not run order.

    sklearn's GroupKFold is deterministic and orders by group size, which for these
    datasets puts whole experimental runs together. Shuffling the group order first
    keeps folds disjoint by pedestrian while removing that structure.
    """
    rng = np.random.default_rng(seed)
    uniq = np.unique(groups)
    rng.shuffle(uniq)
    sizes = {g: int(np.sum(groups == g)) for g in uniq}
    loads = np.zeros(n_splits)
    assign = {}
    for g in sorted(uniq, key=lambda g: -sizes[g]):
        f = int(np.argmin(loads))
        assign[g] = f
        loads[f] += sizes[g]
    fold_of = np.array([assign[g] for g in groups])
    return [(np.where(fold_of != f)[0], np.where(fold_of == f)[0]) for f in range(n_splits)]


def cv_logit(X, y, k, folds, C=0.5, max_iter=3000, subsample=None, rng=None):
    """Out-of-fold probabilities from a multinomial logit on X.

    subsample, when set, limits each training fold to that many rows, which is how
    the learning curves are produced. Test folds are never subsampled.
    """
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler

    P = np.full((len(y), k), np.nan)
    for tr, te in folds:
        if subsample is not None and subsample < len(tr):
            tr = rng.choice(tr, size=subsample, replace=False)
        if len(np.unique(y[tr])) < 2:
            P[te] = np.bincount(y[tr], minlength=k) / len(tr)
            continue
        m = make_pipeline(StandardScaler(),
                          LogisticRegression(C=C, max_iter=max_iter))
        m.fit(X[tr], y[tr])
        pp = np.zeros((len(te), k))
        pp[:, m.classes_] = m.predict_proba(X[te])
        # classes absent from this training subset get the smoothed prior
        missing = [c for c in range(k) if c not in set(m.classes_)]
        if missing:
            pp = (pp + 1e-4) / (pp + 1e-4).sum(1, keepdims=True)
        P[te] = pp
    return normalize(P)


def cv_freq(y, k, folds):
    P = np.zeros((len(y), k))
    for tr, te in folds:
        P[te] = (np.bincount(y[tr], minlength=k) + 0.5) / (len(tr) + 0.5 * k)
    return normalize(P)


def cv_temp_scaled(P_raw, y, folds):
    """Temperature fitted inside the training folds only."""
    out = np.zeros_like(P_raw)
    for tr, te in folds:
        T = fit_T(P_raw[tr], y[tr])
        out[te] = apply_T(P_raw[te], T)
    return normalize(out)
