"""Revision statistics: fully specified estimators, intervals that refit, held-out
selective prediction, itemwise cascades, clustered paired tests, option-name
uncertainty, failure counts, cardinality diagnostics and metric definitions.

Every quantity is computed from the stored answers (no new model calls) through
bench.decisions, so decision filtering, option order and probability normalization
are identical to a01 to a08. Rep 1 is the analyzed run for every model; Jev's reps
2 and 3 enter only the service-variability block of section E.

Sections (top-level keys of results/revision_stats.json):
    A_temperature_scaling    estimator documented from metrics.fit_T / crossfit_T;
                             per task shipped, raw and scaled ECE, scaled intervals
                             that refit the cross-fitted temperatures per replicate
    B_selective_prediction   in-sample coverage at risk with intervals, AURC, OOS
                             AUROC; held-out coverage with a one-sided Clopper-Pearson
                             bound on realized risk; the intent-gate operating point
    C_raw_arm                which models carry an exact temperature-one distribution
    D_cascades               itemwise costs, cross-fitted thresholds, bootstrap that
                             refits thresholds, D1 request-level variant, composed
                             latency, cost sensitivity
    E_paired                 paired cluster bootstrap against Jev with Holm correction,
                             exact McNemar alongside, Jev service variability
    F_option_names           flips and delta AUC with intervals, retest floors
    G_failures               answered, error, refusal and truncation counts per file
    H_cardinality            accuracy by gold-option position, predicted positions,
                             option-list length in characters
    I_definitions            soft accuracy, soft Brier, the teacher self-agreement
                             reference
    consistency              regression checks against e1_main, e6_cascade,
                             cost_latency and paired

Output: results/revision_stats.json
"""
import json
import os
import re
import time
from collections import Counter, defaultdict
from functools import lru_cache

import common as C  # noqa: I100  (sets thread limits before numpy)

import numpy as np
from scipy.stats import beta

import a02_e2_names as A2
import a06_e6_cascade as A6
import bench
import metrics as M

OUT = "revision_stats.json"
MODELS = [bench.JEV] + bench.MODELS_OPEN + ["comparator-open"]
COMP = "comparator-open"
D3 = ["d3_conv_go_awry", "d3_wiki_corpus", "d3_emotion", "d3_wiki_politeness"]
TASKS = ["d1_neutral", "d2_k150"] + D3
FOLDS = 5
B_REFIT = 1000        # replicates for every interval that refits temperatures or thresholds
B_BOOT = 1000         # replicates for the other sort-based intervals (ECE, coverage, AURC, AUROC)
B_PAIRED = 10000      # replicates for paired mean differences and flip rates (vectorized)
LEVEL = 95
ALPHAS = (0.01, 0.05)
GRID = np.exp(np.linspace(np.log(0.2), np.log(20), 120))   # identical to metrics.fit_T
EPS = M.EPS
TAU_TOP = 1.0 + 1e-9                                       # identical to a06
AWORD = {0.01: "1pct", 0.05: "5pct"}
if os.environ.get("A09_QUICK"):          # smoke test only, never the reported run
    B_REFIT, B_BOOT, B_PAIRED, OUT = 20, 20, 200, "revision_stats.quick.json"

T0 = time.time()
RES = {}


def log(*a):
    print(f"[{time.time() - T0:7.1f}s]", *a, flush=True)


def _clean(o):
    """NaN (an undefined risk at zero coverage, say) is written as null, keeping the
    file strict JSON."""
    if isinstance(o, dict):
        return {k: _clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_clean(v) for v in o]
    if isinstance(o, (float, np.floating)) and np.isnan(o):
        return None
    return o


def dump():
    C.dump(_clean(RES), OUT)


# ------------------------------------------------------------------ loading

@lru_cache(maxsize=None)
def dec(model, cond, rep=1, raw=False):
    return bench.decisions(model, cond, rep, raw)


@lru_cache(maxsize=None)
def ans(model, cond, rep=1):
    return bench.answers(model, cond, rep)


def has(model, cond, rep=1):
    return rep in bench.available_reps(model, cond)


@lru_cache(maxsize=None)
def scored(model, cond, rep=1):
    """Rows with a gold label and an answer, in bench order (as a01.summarize)."""
    rs = [r for r in dec(model, cond, rep) if r["y"] >= 0 and not np.isnan(r["p"]).any()]
    if not rs:
        return None
    P = [r["p"] for r in rs]
    y = np.array([r["y"] for r in rs])
    return {"rs": rs, "P": P, "y": y,
            "groups": np.array([r["item_id"] for r in rs]),
            "types": np.array([r["type"] for r in rs]),
            "conf": np.array([p.max() for p in P]),
            "correct": np.array([float(np.argmax(p) == k) for p, k in zip(P, y)]),
            "keys": [r["key"] + "|" + r["qid"] for r in rs]}


def usd_per_gpu_hour():
    p = os.path.join(C.RESULTS, "cost_latency.json")
    cl = json.load(open(p, encoding="utf-8"))
    return cl["assumptions"]["usd_per_gpu_hour"], cl


USD_H, CL = usd_per_gpu_hour()


# ------------------------------------------------------------------ bootstrap helpers

class Clusters:
    """Cluster index structure for fast resampling with duplicates kept."""

    def __init__(self, groups):
        groups = np.asarray(groups)
        self.ug, inv = np.unique(groups, return_inverse=True)
        order = np.argsort(inv, kind="mergesort")
        self.order = order
        self.len = np.bincount(inv, minlength=len(self.ug))
        self.start = np.r_[0, np.cumsum(self.len)[:-1]]
        self.inv = inv
        self.G = len(self.ug)

    def expand(self, pick):
        lens = self.len[pick]
        tot = int(lens.sum())
        offs = np.repeat(self.start[pick] - np.r_[0, np.cumsum(lens)[:-1]], lens)
        return self.order[np.arange(tot) + offs]

    def draw(self, rng):
        pick = rng.integers(0, self.G, self.G)
        return pick, self.expand(pick)

    def fold_rows(self, pick, rng, k=FOLDS):
        """Fold per row for a replicate: the drawn distinct clusters are shuffled and
        assigned i mod k, as crossfit_T does; copies of one cluster share a fold."""
        u = np.unique(pick)
        rng.shuffle(u)
        fc = np.full(self.G, -1)
        fc[u] = np.arange(len(u)) % k
        return fc[self.inv]


def folds_of(groups, seed=C.SEED, k=FOLDS):
    """The fold construction of metrics.crossfit_T and a06.heldout."""
    rng = np.random.default_rng(seed)
    ug = np.unique(groups)
    rng.shuffle(ug)
    fold = {g: i % k for i, g in enumerate(ug)}
    return np.array([fold[g] for g in groups])


def pct(vals):
    vals = np.asarray([v for v in vals if v is not None and not np.isnan(v)], float)
    if len(vals) == 0:
        return None
    lo, hi = np.percentile(vals, [(100 - LEVEL) / 2, 100 - (100 - LEVEL) / 2])
    return [float(lo), float(hi)]


def boot_p_le0(vals):
    vals = np.asarray(vals, float)
    return float((1 + np.sum(vals <= 0)) / (len(vals) + 1))


def boot_p_two(vals):
    vals = np.asarray(vals, float)
    B = len(vals)
    lo = (1 + np.sum(vals <= 0)) / (B + 1)
    hi = (1 + np.sum(vals >= 0)) / (B + 1)
    return float(min(1.0, 2 * min(lo, hi)))


def holm(ps):
    ps = np.asarray(ps, float)
    m = len(ps)
    order = np.argsort(ps, kind="mergesort")
    adj = np.empty(m)
    run = 0.0
    for r, i in enumerate(order):
        run = max(run, min(1.0, (m - r) * ps[i]))
        adj[i] = run
    return adj


def cp_upper_one_sided(k, n, level=0.95):
    if n == 0:
        return None
    return 1.0 if k == n else float(beta.ppf(level, k + 1, n - k))


# ------------------------------------------------------------------ temperature kernels

def t_mats(P, ys):
    """Per decision NLL and scaled top confidence on the fit_T grid, using the same
    log(clip(p, EPS)) / T construction as metrics.fit_T and metrics.apply_T."""
    n = len(P)
    NLL = np.empty((n, len(GRID)))
    CONF = np.empty((n, len(GRID)))
    for i, (p, k) in enumerate(zip(P, ys)):
        lp = np.log(np.clip(p, EPS, None))
        z = lp[None, :] / GRID[:, None]
        zm = z - z.max(1, keepdims=True)
        NLL[i] = -(zm[:, k] - np.log(np.exp(zm).sum(1)))
        q = np.exp(z)
        CONF[i] = q.max(1) / q.sum(1)
    return NLL, CONF


def conf_at_T1(P):
    return np.array([M.apply_T(p, 1.0).max() for p in P])


def argmin_T(NLL, w):
    """Grid index minimizing the weighted NLL sum (first minimum, as fit_T's strict <)."""
    v = w @ NLL
    return int(np.argmin(v))


# ------------------------------------------------------------------ A. temperature scaling

ESTIMATOR = {
    "loss": ("negative log-likelihood of the gold option, summed over decisions, of the "
             "temperature-scaled shipped distribution softmax(log(clip(p, 1e-6)) / T); the "
             "shipped probabilities stand in for logits, so scaling composes with any "
             "temperature the model already serves; option counts may differ across "
             "decisions; a per-decision max is subtracted before the log-sum-exp"),
    "grid": "120 values of T spaced evenly in log T from 0.2 to 20 inclusive",
    "bounds": [0.2, 20.0],
    "search": ("exhaustive over the grid; the first grid value with the smallest loss is "
               "kept (strict less-than), default 1.0 is never returned because every loss "
               "is finite"),
    "eps_clipping": "probabilities clipped below at 1e-6 before the log (metrics.EPS)",
    "apply": "q = exp(log(clip(p, 1e-6)) / T), renormalized; argmax is unchanged",
    "crossfit": ("five folds; the distinct cluster ids are sorted (numpy.unique), shuffled "
                 "with numpy.random.default_rng(20260924) and assigned fold i mod 5; each "
                 "fold is scaled with the temperature fitted on the other four folds"),
    "disjointness_unit": ("item_id: the state for D1 (five decisions per state), the "
                          "utterance for D2, the item for D3"),
    "d1": ("no cross-fitting on d1_neutral: one temperature per primitive type (choice, "
           "noul, score) fitted on d1_calib (training-split states, disjoint from the test "
           "states) with at least 30 calibration decisions per type, else T = 1; applied "
           "to d1_neutral by type (a01_e1_main.fit_types, verified below)"),
    "ece": "top-label ECE with 10 equal-mass bins (metrics.ece), stable mergesort order",
    "interval_shipped": "cluster bootstrap over item_id, percentile 95 percent",
    "interval_scaled_refit": ("cluster bootstrap over item_id; within each replicate the "
                              "fold map is rebuilt on the drawn distinct clusters (shuffled, "
                              "i mod 5, copies of one cluster share a fold) and each fold's "
                              "temperature is refit on the other folds' replicate rows with "
                              "multiplicity; for D1 each replicate independently resamples "
                              "d1_calib states and refits the per-type temperatures, and "
                              "resamples d1_neutral states"),
    "replicates": B_REFIT,
}


def fit_types_exact(model):
    """a01_e1_main.fit_types, reproduced."""
    S = scored(model, "d1_calib")
    out = {}
    if S is None:
        return out, S
    for t in ("choice", "noul", "score"):
        m = S["types"] == t
        if m.sum() >= 30:
            out[t] = M.fit_T([p for p, k in zip(S["P"], m) if k], list(S["y"][m]))
    return out, S


def section_A(raw_ok):
    out = {"estimator": ESTIMATOR, "results": {}, "d3_pooled": {}}
    checks = []
    e1 = json.load(open(os.path.join(C.RESULTS, "e1_main.json"), encoding="utf-8"))
    for m in MODELS:
        pooled = {"conf": [], "correct": [], "conf_raw": [], "correct_raw": [], "conf_s": []}
        for cond in TASKS:
            if not has(m, cond):
                continue
            S = scored(m, cond)
            if S is None:
                continue
            conf, cor, groups, P, y = S["conf"], S["correct"], S["groups"], S["P"], S["y"]
            rawp = None
            if raw_ok.get(m):
                rr = {r["key"] + r["qid"]: r for r in dec(m, cond, 1, True)}
                Praw = [rr[r["key"] + r["qid"]]["p"] for r in S["rs"]]
                conf_raw = np.array([p.max() for p in Praw])
                cor_raw = np.array([float(np.argmax(p) == k) for p, k in zip(Praw, y)])
                rawp = M.ece(conf_raw, cor_raw)
            NLL, CONF = t_mats(P, y)
            rng = np.random.default_rng(C.SEED)
            cl = Clusters(groups)
            ship_b, scal_b = [], []
            if cond == "d1_neutral":
                T_types, Sc = fit_types_exact(m)
                if not T_types:
                    continue
                Ps = [M.apply_T(p, T_types.get(t, 1.0)) for p, t in zip(P, S["types"])]
                conf_s = np.array([p.max() for p in Ps])
                temps = {"per_type_from_d1_calib": T_types,
                         "at_grid_bound": {t: bool(T <= GRID[0] * (1 + 1e-9)
                                                   or T >= GRID[-1] * (1 - 1e-9))
                                           for t, T in T_types.items()}}
                NLLc, _ = t_mats(Sc["P"], Sc["y"])
                clc = Clusters(Sc["groups"])
                # column -1 holds the T = 1 confidence for a type left unscaled
                CONF1 = np.c_[CONF, conf_at_T1(P)]
                TYPES = ("choice", "noul", "score")
                ti = np.array([TYPES.index(t) for t in S["types"]])
                # matrix path reproduces the exact per-type fit
                for t in T_types:
                    msk = (Sc["types"] == t).astype(float)
                    checks.append({"what": f"A {m} d1 type {t} matrix fit equals fit_T",
                                   "ok": bool(abs(GRID[argmin_T(NLLc, msk)] - T_types[t]) < 1e-12)})
                for _ in range(B_REFIT):
                    _, ic = clc.draw(rng)
                    wc = np.bincount(ic, minlength=len(Sc["y"])).astype(float)
                    gsel = np.full(3, len(GRID))
                    for j, t in enumerate(TYPES):
                        msk = (Sc["types"] == t)
                        if (wc * msk).sum() >= 30:
                            gsel[j] = argmin_T(NLLc, wc * msk)
                    _, ii = cl.draw(rng)
                    cs = CONF1[ii, gsel[ti[ii]]]
                    ship_b.append(M.ece(conf[ii], cor[ii]))
                    scal_b.append(M.ece(cs, cor[ii]))
            else:
                Ps, Ts = M.crossfit_T(P, y, groups)
                conf_s = np.array([p.max() for p in Ps])
                temps = {"crossfit_folds": Ts,
                         "at_grid_bound": [bool(T <= GRID[0] * (1 + 1e-9)
                                                or T >= GRID[-1] * (1 - 1e-9)) for T in Ts]}
                # the matrix path reproduces crossfit_T's fold temperatures and scaled conf
                f = folds_of(groups)
                ok = True
                conf_chk = np.empty(len(y))
                for k in range(FOLDS):
                    g = argmin_T(NLL, (f != k).astype(float))
                    ok &= abs(GRID[g] - Ts[k]) < 1e-12
                    conf_chk[f == k] = CONF[f == k, g]
                checks.append({"what": f"A {m} {cond} matrix fold temperatures equal crossfit_T",
                               "ok": bool(ok),
                               "max_abs_conf_diff": float(np.max(np.abs(conf_chk - conf_s)))})
                for _ in range(B_REFIT):
                    pick, ii = cl.draw(rng)
                    fr = cl.fold_rows(pick, rng)
                    w = np.bincount(ii, minlength=len(y)).astype(float)
                    cs = np.empty(len(y))
                    for k in range(FOLDS):
                        wk = w * ((fr != k) & (fr >= 0))
                        g = argmin_T(NLL, wk)
                        sel = fr == k
                        cs[sel] = CONF[sel, g]
                    ship_b.append(M.ece(conf[ii], cor[ii]))
                    scal_b.append(M.ece(cs[ii], cor[ii]))
            d = {"n": int(len(y)), "ece_shipped": M.ece(conf, cor),
                 "ece_shipped_ci": pct(ship_b),
                 "ece_raw": rawp,
                 "ece_scaled": M.ece(conf_s, cor),
                 "ece_scaled_ci_refit": pct(scal_b),
                 "temperatures": temps,
                 "replicates": B_REFIT,
                 "boot_mean_shipped": float(np.mean(ship_b)),
                 "boot_mean_scaled": float(np.mean(scal_b)),
                 "note_bias": ("ECE is biased upward in resamples (duplicated clusters, "
                               "refit noise), so for small values the percentile interval "
                               "can sit above the point estimate; boot means show the shift")}
            d["scaled_point_inside_ci"] = bool(d["ece_scaled_ci_refit"][0] <= d["ece_scaled"]
                                               <= d["ece_scaled_ci_refit"][1])
            ref = e1.get(f"{m}|{cond}")
            if ref:
                checks.append({"what": f"A {m} {cond} equals e1_main",
                               "ok": bool(abs(ref["ece_shipped"] - d["ece_shipped"]) < 1e-12
                                          and abs(ref["ece_scaled"] - d["ece_scaled"]) < 1e-12
                                          and (rawp is None
                                               or abs(ref["ece_raw"] - rawp) < 1e-12))})
            out["results"][f"{m}|{cond}"] = d
            if cond in D3:
                pooled["conf"].append(conf)
                pooled["correct"].append(cor)
                pooled["conf_s"].append(conf_s)
                if rawp is not None:
                    pooled["conf_raw"].append(conf_raw)
                    pooled["correct_raw"].append(cor_raw)
            log("A", m, cond, round(d["ece_shipped"], 3), "->", round(d["ece_scaled"], 3),
                d["ece_scaled_ci_refit"])
        if pooled["conf"]:
            cc = np.concatenate(pooled["conf"])
            kk = np.concatenate(pooled["correct"])
            per = [out["results"][f"{m}|{c}"]["ece_scaled"] for c in D3
                   if f"{m}|{c}" in out["results"]]
            out["d3_pooled"][m] = {
                "n": int(len(cc)), "ece_shipped": M.ece(cc, kk),
                "ece_raw": (M.ece(np.concatenate(pooled["conf_raw"]),
                                  np.concatenate(pooled["correct_raw"]))
                            if pooled["conf_raw"] else None),
                "ece_scaled": M.ece(np.concatenate(pooled["conf_s"]), kk),
                "per_task_scaled_min": float(min(per)), "per_task_scaled_max": float(max(per)),
                "note": ("pooled as collect_numbers.pool_d3: temperatures cross-fit within each "
                         "task, decisions concatenated across the four tasks")}
    RES["A_temperature_scaling"] = out
    RES.setdefault("consistency", {})["A"] = checks


# ------------------------------------------------------------------ B. selective prediction

def thr_at_risk(conf, correct, alpha):
    """Lowest threshold whose accepted set (conf >= threshold, ties accepted together)
    has empirical risk at most alpha; None when no threshold qualifies."""
    if len(conf) == 0:
        return None
    return M.coverage_at_risk(conf, correct, alpha)[1]


def apply_thr(conf, thr):
    return np.zeros(len(conf), bool) if thr is None else conf >= thr


def realized(acc_mask, correct):
    n_acc = int(acc_mask.sum())
    err = int(np.sum(acc_mask & (correct == 0)))
    return {"n": int(len(correct)), "accepted": n_acc, "errors": err,
            "coverage": n_acc / len(correct) if len(correct) else None,
            "risk": err / n_acc if n_acc else None,
            "risk_upper_95_one_sided_cp": cp_upper_one_sided(err, n_acc)}


def section_B():
    out = {"definitions": {
        "coverage_at_risk": ("metrics.coverage_at_risk on shipped top-label confidence: "
                             "decisions accepted in order of decreasing confidence, ties "
                             "accepted together; the largest coverage whose accepted-set "
                             "error rate is at most alpha, i.e. the lowest qualifying threshold"),
        "heldout": ("threshold chosen on training data by the same rule, applied to held-out "
                    "decisions as confidence >= threshold (none accepted when no threshold "
                    "qualifies); D2 and D3 by five-fold cross-fitting disjoint by item_id "
                    "with the crossfit_T fold map; D1 chosen on d1_calib and applied to "
                    "d1_neutral; realized risk bound is the one-sided 95 percent "
                    "Clopper-Pearson upper limit beta.ppf(0.95, k + 1, n - k)"),
        "gate": ("d2_k150: folds over all 800 utterances (in and out of scope) with the "
                 "crossfit_T fold map; each fold's threshold targets 5 percent risk on the "
                 "in-scope decisions of the other folds; out-of-scope false acceptance is the "
                 "share of out-of-scope utterances with confidence >= threshold"),
        "replicates": B_BOOT, "refit_replicates": B_REFIT},
        "insample": {}, "heldout": {}, "gate": {}}
    for m in MODELS:
        for cond in TASKS:
            if not has(m, cond):
                continue
            S = scored(m, cond)
            if S is None:
                continue
            conf, cor, groups = S["conf"], S["correct"], S["groups"]
            cl = Clusters(groups)
            rng = np.random.default_rng(C.SEED)
            bs = defaultdict(list)
            for _ in range(B_BOOT):
                _, ii = cl.draw(rng)
                c, k = conf[ii], cor[ii]
                for a in ALPHAS:
                    bs[a].append(M.coverage_at_risk(c, k, a)[0])
                bs["aurc"].append(M.aurc(c, k))
            d = {"n": int(len(conf)), "aurc": M.aurc(conf, cor), "aurc_ci": pct(bs["aurc"])}
            for a in ALPHAS:
                cov, thr = M.coverage_at_risk(conf, cor, a)
                d[f"coverage_at_{AWORD[a]}"] = cov
                d[f"coverage_at_{AWORD[a]}_ci"] = pct(bs[a])
                d[f"threshold_at_{AWORD[a]}"] = thr
            if cond == "d2_k150":
                rows = [r for r in dec(m, cond) if not np.isnan(r["p"]).any()]
                ca = np.array([r["p"].max() for r in rows])
                ins = np.array([r["meta"]["in_scope"] for r in rows])
                cla = Clusters(np.array([r["item_id"] for r in rows]))
                rng2 = np.random.default_rng(C.SEED)
                au = []
                for _ in range(B_BOOT):
                    _, ii = cla.draw(rng2)
                    au.append(M.auroc(ca[ii], ins[ii]))
                d["auroc_in_vs_oos"] = M.auroc(ca, ins)
                d["auroc_in_vs_oos_ci"] = pct(au)
            out["insample"][f"{m}|{cond}"] = d

            # held-out coverage
            h = {}
            if cond == "d1_neutral":
                Sc = scored(m, "d1_calib") if has(m, "d1_calib") else None
                if Sc is None:
                    h = None
                else:
                    for a in ALPHAS:
                        thr = thr_at_risk(Sc["conf"], Sc["correct"], a)
                        r = realized(apply_thr(conf, thr), cor)
                        r.update({"threshold": thr, "selection": "d1_calib",
                                  "insample_coverage": d[f"coverage_at_{AWORD[a]}"]})
                        h[AWORD[a]] = r
            else:
                f = folds_of(groups)
                for a in ALPHAS:
                    acc = np.zeros(len(conf), bool)
                    thrs = []
                    for k in range(FOLDS):
                        tr, te = f != k, f == k
                        t = thr_at_risk(conf[tr], cor[tr], a)
                        thrs.append(t)
                        acc[te] = apply_thr(conf[te], t)
                    r = realized(acc, cor)
                    r.update({"fold_thresholds": thrs, "selection": "5-fold cross-fitting",
                              "deployable_threshold": thr_at_risk(conf, cor, a),
                              "insample_coverage": d[f"coverage_at_{AWORD[a]}"]})
                    h[AWORD[a]] = r
            if h is not None:
                out["heldout"][f"{m}|{cond}"] = h
            log("B", m, cond, {a: (round(d[f'coverage_at_{AWORD[a]}'], 3),
                                   h[AWORD[a]]["coverage"] if h else None) for a in ALPHAS})

        # intent gate
        if has(m, "d2_k150"):
            rows = [r for r in dec(m, "d2_k150") if not np.isnan(r["p"]).any()]
            if rows:
                ca = np.array([r["p"].max() for r in rows])
                ins = np.array([bool(r["meta"]["in_scope"]) for r in rows])
                cor = np.array([float(r["y"] >= 0 and np.argmax(r["p"]) == r["y"])
                                for r in rows])
                items = np.array([r["item_id"] for r in rows])

                def gate(ii, fr):
                    acc = np.zeros(len(ii), bool)
                    for k in range(FOLDS):
                        trm = (fr[ii] != k) & ins[ii]
                        t = thr_at_risk(ca[ii][trm], cor[ii][trm], 0.05)
                        te = fr[ii] == k
                        acc[te] = apply_thr(ca[ii][te], t)
                    i_in, i_oos = ins[ii], ~ins[ii]
                    n_in_acc = int(acc[i_in].sum())
                    n_err = int(np.sum(acc[i_in] & (cor[ii][i_in] == 0)))
                    return (float(n_in_acc / i_in.sum()),
                            n_err / n_in_acc if n_in_acc else np.nan,
                            float(acc[i_oos].mean()) if i_oos.any() else np.nan,
                            n_in_acc, n_err)

                f = folds_of(items)
                allidx = np.arange(len(rows))
                cov, risk, far, n_acc_pt, n_err_pt = gate(allidx, f)
                cla = Clusters(items)
                rng = np.random.default_rng(C.SEED)
                bs = []
                for _ in range(B_REFIT):
                    pick, ii = cla.draw(rng)
                    fr = cla.fold_rows(pick, rng)
                    bs.append(gate(ii, fr))
                bs = np.array(bs)
                t_dep = thr_at_risk(ca[ins], cor[ins], 0.05)
                acc_dep = apply_thr(ca, t_dep)
                n_in_acc = int(acc_dep[ins].sum())
                n_err = int(np.sum(acc_dep[ins] & (cor[ins] == 0)))
                out["gate"][m] = {
                    "target_risk": 0.05, "n_in": int(ins.sum()), "n_oos": int((~ins).sum()),
                    "coverage_in": cov, "coverage_in_ci": pct(bs[:, 0]),
                    "risk_in": risk, "risk_in_ci": pct(bs[:, 1]),
                    "accepted_in": n_acc_pt, "errors_in": n_err_pt,
                    "risk_in_upper_95_one_sided_cp": cp_upper_one_sided(n_err_pt, n_acc_pt),
                    "oos_false_acceptance": far, "oos_false_acceptance_ci": pct(bs[:, 2]),
                    "deployable_threshold": t_dep,
                    "deployable_insample": {
                        "coverage_in": n_in_acc / int(ins.sum()),
                        "risk_in": n_err / n_in_acc if n_in_acc else None,
                        "oos_false_acceptance": float(acc_dep[~ins].mean())},
                    "replicates": B_REFIT}
                log("B gate", m, round(cov, 3), risk, round(far, 3))
    RES["B_selective_prediction"] = out


# ------------------------------------------------------------------ C. raw arm

def section_C():
    out = {}
    for m in MODELS:
        n_q = n_t1 = 0
        maxdiff = 0.0
        temps = Counter()
        two_dec = n_vals = 0
        for cond in TASKS:
            for a in ans(m, cond).values():
                temps[str(a.get("served_temperature"))] += 1
                for q in a["answers"].values():
                    if not q.get("probs"):
                        continue
                    n_q += 1
                    raw = q.get("raw") if isinstance(q.get("raw"), dict) else {}
                    t1 = q.get("probs_t1") or raw.get("probs_t1")
                    for v in q["probs"].values():
                        n_vals += 1
                        two_dec += abs(v * 100 - round(v * 100)) < 1e-9
                    if t1:
                        n_t1 += 1
                        maxdiff = max(maxdiff, max(abs(float(t1[o]) - float(q["probs"][o]))
                                                   for o in q["probs"]))
        rec = {"answers_checked": n_q, "share_with_probs_t1": n_t1 / n_q if n_q else None,
               "max_abs_diff_t1_vs_shipped": maxdiff,
               "served_temperature_values": dict(temps.most_common(5)),
               "share_prob_values_on_two_decimals": two_dec / n_vals if n_vals else None}
        if m == bench.JEV:
            rec.update(raw_available=False, reason=(
                "hosted service; served temperature undisclosed (served_temperature is null "
                "in every record) and probabilities are returned rounded to two decimals, so "
                "no temperature-one distribution can be recovered"))
        elif m == COMP:
            rec.update(raw_available=False, reason=(
                "generative comparator; probabilities are numbers written in the requested "
                "JSON under greedy decoding (served_temperature 0.0), renormalized by the "
                "adapter; probs_t1 only repeats them; at more than 20 options only the top "
                "5 are reported (adapters.COMPARATOR_FULL_COVERAGE_MAX_K, COMPARATOR_TOP_N) "
                "and the rest are zero"))
        elif m in ("this-that-1.0", "nimble-9b"):
            rec.update(raw_available=True, reason=(
                "served at temperature 1.0 with unrounded probabilities; probs_t1 is stored "
                "and identical to the shipped distribution, so raw equals shipped"))
        elif m.startswith("laya"):
            rec.update(raw_available=True, reason=(
                "exact temperature-one distribution stored per answer in raw.probs_t1; the "
                "shipped distribution applies a per-bucket temperature (by question type and "
                "option count) that one scalar cannot undo"))
        else:
            rec.update(raw_available=True, reason=(
                "exact temperature-one distribution stored per answer in raw.probs_t1; the "
                "checkpoint serves a stored temperature (Kev about 2.3, decider 1.3)"))
        out[m] = rec
        log("C", m, rec["raw_available"], rec["share_with_probs_t1"], round(maxdiff, 4))
    RES["C_raw_arm"] = out
    return {m: v["raw_available"] for m, v in out.items()}


# ------------------------------------------------------------------ D. cascades

@lru_cache(maxsize=None)
def req_info(model, cond):
    """Per request cost (USD) and latency (s), and per decision cost and latency,
    from the answer records themselves, with a04's constants."""
    A = ans(model, cond)
    info = {}
    for key, a in A.items():
        qs = list(a["answers"])
        nq = len(qs)
        if model == COMP:
            share = {q: a["answers"][q]["raw"]["batch_wall_s"] / a["answers"][q]["raw"]["n_requests"]
                     for q in qs}
            lat_r = sum(share.values())
            cost_r = lat_r / 3600 * USD_H
            dcost = {q: share[q] / 3600 * USD_H for q in qs}
            dlat = dict(share)
        elif model == bench.JEV:
            cost_r = (a.get("usage_in") or 0) * C.PRICE_PER_MTOK / 1e6
            lat_r = a.get("latency_s") or 0.0
            dcost = {q: cost_r / nq for q in qs}
            dlat = {q: lat_r for q in qs}
        else:
            lat_r = a.get("latency_s") or 0.0
            cost_r = lat_r / 3600 * USD_H
            dcost = {q: cost_r / nq for q in qs}
            dlat = {q: lat_r for q in qs}
        info[key] = {"cost": cost_r, "lat": lat_r, "dcost": dcost, "dlat": dlat, "nq": nq}
    return info


def cost_check(model, cond):
    info = req_info(model, cond)
    tot = sum(v["cost"] for v in info.values())
    ndec = sum(v["nq"] for v in info.values())
    mine = tot / ndec * 1000 if ndec else None
    ref = CL.get(model, {}).get(cond, {}).get("usd_per_1000_decisions")
    return mine, ref


def best_tau_fast(conf, a1, a2):
    """a06.best_tau with integer counts: maximize kept-plus-escalated correct decisions,
    ties to the smallest threshold (least escalation)."""
    taus = np.unique(np.r_[0.0, conf, TAU_TOP])
    order = np.argsort(conf, kind="mergesort")
    cs = conf[order]
    cum = np.r_[0, np.cumsum((a2 - a1)[order])]
    val = cum[np.searchsorted(cs, taus, side="left")]
    return float(taus[int(np.flatnonzero(val == val.max())[0])])


def aligned_full(first, second, cond):
    a = {r["key"] + "|" + r["qid"]: r for r in dec(first, cond)
         if r["y"] >= 0 and not np.isnan(r["p"]).any()}
    b = {r["key"] + "|" + r["qid"]: r for r in dec(second, cond)
         if r["y"] >= 0 and not np.isnan(r["p"]).any()}
    keys = sorted(set(a) & set(b))
    if not keys:
        return None
    i1, i2 = req_info(first, cond), req_info(second, cond)
    D = {"keys": keys,
         "conf": np.array([a[k]["p"].max() for k in keys]),
         "c1": np.array([int(np.argmax(a[k]["p"]) == a[k]["y"]) for k in keys]),
         "c2": np.array([int(np.argmax(b[k]["p"]) == b[k]["y"]) for k in keys]),
         "item": np.array([a[k]["item_id"] for k in keys]),
         "req": np.array([a[k]["key"] for k in keys])}
    D["k1"] = np.array([i1[a[k]["key"]]["dcost"][a[k]["qid"]] for k in keys])
    D["k2"] = np.array([i2[b[k]["key"]]["dcost"][b[k]["qid"]] for k in keys])
    D["l1"] = np.array([i1[a[k]["key"]]["dlat"][a[k]["qid"]] for k in keys])
    D["l2"] = np.array([i2[b[k]["key"]]["dlat"][b[k]["qid"]] for k in keys])
    ur, inv = np.unique(D["req"], return_inverse=True)
    D["rinv"] = inv
    D["R"] = {"g": np.array([D["conf"][inv == j].min() for j in range(len(ur))]),
              "a1": np.bincount(inv, weights=D["c1"]).astype(int),
              "a2": np.bincount(inv, weights=D["c2"]).astype(int),
              "n": np.bincount(inv).astype(int),
              "k1": np.array([i1[r]["cost"] for r in ur]),
              "k2": np.array([i2[r]["cost"] for r in ur]),
              "l1": np.array([i1[r]["lat"] for r in ur]),
              "l2": np.array([i2[r]["lat"] for r in ur])}
    item_of = dict(zip(D["req"], D["item"]))
    D["R"]["item"] = np.array([item_of[r] for r in ur])
    return D


def casc_stats(c1, c2, esc, k1, k2):
    n = len(c1)
    acc1, acc2 = c1.mean(), c2.mean()
    corr = np.where(esc, c2, c1)
    acc = corr.mean()
    return {"accuracy": float(acc), "acc_first": float(acc1), "acc_second": float(acc2),
            "gain": float(acc - max(acc1, acc2)),
            "gain_decisions": int(corr.sum() - max(c1.sum(), c2.sum())),
            "escalated": float(esc.mean()),
            "cost_fraction": float((k1.sum() + k2[esc].sum()) / k2.sum()) if k2.sum() > 0 else None,
            "n": int(n)}


def req_stats(R, esc_r, rinv, c1, c2, esc_dec):
    """Request-level escalation: whole requests re-sent; accuracy over decisions with
    esc_dec telling which decisions take the second-stage answer."""
    corr = np.where(esc_dec, c2, c1)
    acc = corr.mean()
    return {"accuracy": float(acc), "acc_first": float(c1.mean()), "acc_second": float(c2.mean()),
            "gain": float(acc - max(c1.mean(), c2.mean())),
            "gain_decisions": int(corr.sum() - max(c1.sum(), c2.sum())),
            "escalated_requests": float(esc_r.mean()),
            "escalated_decisions": float(esc_dec.mean()),
            "cost_fraction": float((R["k1"].sum() + R["k2"][esc_r].sum()) / R["k2"].sum())
            if R["k2"].sum() > 0 else None,
            "n": int(len(c1)), "n_requests": int(len(esc_r))}


def lat_pcts(x):
    return {"p50_s": float(np.percentile(x, 50)), "p95_s": float(np.percentile(x, 95))}


def section_D():
    firsts = [bench.JEV] + bench.MODELS_OPEN
    pairs = [(f, COMP) for f in firsts] + [(f, bench.JEV) for f in bench.MODELS_OPEN]
    e6 = json.load(open(os.path.join(C.RESULTS, "e6_cascade.json"), encoding="utf-8"))
    out = {"definitions": {
        "confidence_arm": "shipped top-label probability of the first stage",
        "candidates": "observed first-stage confidences plus 0 and 1 + 1e-9 (a06)",
        "escalation": "a decision is escalated when its first-stage confidence < tau",
        "objective": ("maximize cascade accuracy on the selection data, ties to the smallest "
                      "tau (least escalation), as a06.best_tau"),
        "selection": ("D1: selected on d1_calib (both models' rep 1), applied to d1_neutral; "
                      "D2 in-scope and each D3 task: five-fold cross-fitting disjoint by "
                      "item_id with the a06 fold map; the deployable threshold is fitted once "
                      "on all selection data"),
        "costs": ("per request from the answer records: Jev recorded input tokens x "
                  f"{C.PRICE_PER_MTOK} USD per million; local open models recorded latency_s x "
                  f"{USD_H:.5f} USD per GPU hour / 3600 (a04 assumptions); comparator "
                  "batch_wall_s / n_requests per question (a04's amortized batched time); a "
                  "decision's cost is the request cost divided by the request's answered "
                  "questions (comparator: its own question's share)"),
        "cost_fraction": ("(sum of first-stage decision costs + sum of second-stage costs of "
                          "escalated decisions) / sum of second-stage decision costs"),
        "d1_request_level": ("a request (state) is escalated when any of its aligned "
                             "decisions has confidence < tau and is charged the full "
                             "second-stage request cost; policy replace_all: every decision of "
                             "an escalated request takes the second-stage answer, tau selected "
                             "on d1_calib by the same objective at request level; policy "
                             "replace_low: tau is the decision-level tau and only decisions "
                             "below it take the second-stage answer; decisions a model left "
                             "unanswered are excluded from both stages (aligned set) and do "
                             "not gate the request"),
        "latency": ("offline composition of recorded latencies: kept decisions take the "
                    "first-stage latency, escalated ones first plus second; a decision's "
                    "latency is its request's latency (comparator: its question's amortized "
                    "batched share, flagged amortized); Jev latency is client-side with 10 "
                    "requests in flight"),
        "bootstrap": ("cluster bootstrap over item_id (states for D1); each replicate refits "
                      "the fold thresholds on the replicate (fold map rebuilt on the drawn "
                      "distinct clusters, copies share a fold); for D1 each replicate also "
                      "resamples d1_calib states and reselects tau; p-value one-sided "
                      "(1 + #{gain* <= 0}) / (B + 1)"),
        "replicates": B_REFIT},
        "pairs": {}, "costs": {}, "cost_sensitivity": {}}
    checks = []
    for f, s in pairs:
        for cond in A6.CONDS:
            if not (has(f, cond) and has(s, cond)):
                continue
            D = aligned_full(f, s, cond)
            if D is None or len(D["conf"]) < 50:
                continue
            conf, c1, c2, k1, k2 = D["conf"], D["c1"], D["c2"], D["k1"], D["k2"]
            key = f"{f}>{s}|{cond}"
            rng = np.random.default_rng(C.SEED)
            rec = {"k1_usd_per_1000": float(k1.mean() * 1000),
                   "k2_usd_per_1000": float(k2.mean() * 1000)}
            if cond == "d1_neutral":
                Dc = aligned_full(f, s, "d1_calib") if (has(f, "d1_calib") and has(s, "d1_calib")) else None
                if Dc is None:
                    continue
                tau = best_tau_fast(Dc["conf"], Dc["c1"], Dc["c2"])
                checks.append({"what": f"D {key} best_tau equals a06 on d1_calib",
                               "ok": tau == A6.best_tau(Dc["conf"], Dc["c1"].astype(bool),
                                                        Dc["c2"].astype(bool))})
                esc = conf < tau
                dl = casc_stats(c1, c2, esc, k1, k2)
                dl.update({"tau": tau, "deployable_tau": tau,
                           "latency": lat_pcts(D["l1"] + esc * D["l2"])})
                # request level
                R, Rc = D["R"], Dc["R"]
                tau_r = best_tau_fast(Rc["g"], Rc["a1"], Rc["a2"])
                esc_r = R["g"] < tau_r
                rl_all = req_stats(R, esc_r, D["rinv"], c1, c2, esc_r[D["rinv"]])
                rl_all.update({"tau": tau_r, "latency": lat_pcts(R["l1"] + esc_r * R["l2"])})
                esc_r_low = R["g"] < tau
                rl_low = req_stats(R, esc_r_low, D["rinv"], c1, c2, esc)
                rl_low.update({"tau": tau, "latency": lat_pcts(R["l1"] + esc_r_low * R["l2"])})
                # bootstrap
                clN, clC = Clusters(D["item"]), Clusters(Dc["item"])
                clNR, clCR = Clusters(R["item"]), Clusters(Rc["item"])
                # one request per state on D1, so the state draws index requests directly
                assert np.array_equal(clN.ug, clNR.ug) and np.array_equal(clC.ug, clCR.ug)
                rows_of = [np.flatnonzero(D["rinv"] == j) for j in range(len(R["g"]))]
                bd, ba, bl = [], [], []
                for _ in range(B_REFIT):
                    pc, ic = clC.draw(rng)
                    t = best_tau_fast(Dc["conf"][ic], Dc["c1"][ic], Dc["c2"][ic])
                    pn, ii = clN.draw(rng)
                    e = conf[ii] < t
                    bd.append(casc_stats(c1[ii], c2[ii], e, k1[ii], k2[ii]))
                    # request level: the same state draws, mapped to requests
                    icr = clCR.expand(pc)
                    tr = best_tau_fast(Rc["g"][icr], Rc["a1"][icr], Rc["a2"][icr])
                    inr = clNR.expand(pn)
                    er = R["g"][inr] < tr
                    Rb = {"k1": R["k1"][inr], "k2": R["k2"][inr]}
                    # decisions of the drawn requests, in the drawn order
                    dmask = np.concatenate([rows_of[j] for j in inr])
                    er_dec = np.repeat(er, R["n"][inr])
                    ba.append(req_stats(Rb, er, None, c1[dmask], c2[dmask], er_dec))
                    erl = R["g"][inr] < t
                    bl.append(req_stats(Rb, erl, None, c1[dmask], c2[dmask], conf[dmask] < t))
                for name, pt, bb in (("decision_level", dl, bd), ("request_level_replace_all", rl_all, ba),
                                     ("request_level_replace_low", rl_low, bl)):
                    esc_key = "escalated" if "escalated" in pt else "escalated_requests"
                    pt["ci"] = {k: pct([b[k] for b in bb])
                                for k in ("accuracy", "gain", esc_key, "cost_fraction", "gain_decisions")
                                if pt.get(k) is not None}
                    pt["p_gain_le_0"] = boot_p_le0([b["gain"] for b in bb])
                rec.update({"n": int(len(conf)), "decision_level": dl,
                            "request_level_replace_all": rl_all,
                            "request_level_replace_low": rl_low,
                            "selection_n": int(len(Dc["conf"]))})
                ref = e6.get(key, {}).get("heldout")
                if ref:
                    checks.append({"what": f"D {key} decision level equals e6 heldout",
                                   "ok": bool(abs(ref["accuracy"] - dl["accuracy"]) < 1e-12
                                              and abs(ref["escalated"] - dl["escalated"]) < 1e-12
                                              and ref["tau"] == [tau])})
            else:
                fo = folds_of(D["item"])
                esc = np.zeros(len(conf), bool)
                taus = []
                for k in range(FOLDS):
                    tr, te = fo != k, fo == k
                    t = best_tau_fast(conf[tr], c1[tr], c2[tr])
                    checks.append({"what": f"D {key} fold {k} best_tau equals a06",
                                   "ok": t == A6.best_tau(conf[tr], c1[tr].astype(bool),
                                                          c2[tr].astype(bool))})
                    taus.append(t)
                    esc[te] = conf[te] < t
                dl = casc_stats(c1, c2, esc, k1, k2)
                t_dep = best_tau_fast(conf, c1, c2)
                e_dep = conf < t_dep
                dl.update({"fold_taus": taus, "deployable_tau": t_dep,
                           "deployable_insample": {"accuracy": float(np.where(e_dep, c2, c1).mean()),
                                                   "escalated": float(e_dep.mean())},
                           "latency": lat_pcts(D["l1"] + esc * D["l2"])})
                cl = Clusters(D["item"])
                bd = []
                for _ in range(B_REFIT):
                    pick, ii = cl.draw(rng)
                    fr = cl.fold_rows(pick, rng)
                    e = np.zeros(len(ii), bool)
                    fri = fr[ii]
                    ci, c1i, c2i = conf[ii], c1[ii], c2[ii]
                    for k in range(FOLDS):
                        tr, te = fri != k, fri == k
                        if not te.any():
                            continue
                        t = best_tau_fast(ci[tr], c1i[tr], c2i[tr])
                        e[te] = ci[te] < t
                    bd.append(casc_stats(c1i, c2i, e, k1[ii], k2[ii]))
                dl["ci"] = {k: pct([b[k] for b in bd])
                            for k in ("accuracy", "gain", "escalated", "cost_fraction", "gain_decisions")
                            if dl.get(k) is not None}
                dl["p_gain_le_0"] = boot_p_le0([b["gain"] for b in bd])
                rec.update({"n": int(len(conf)), "decision_level": dl})
                ref = e6.get(key, {}).get("heldout")
                if ref:
                    checks.append({"what": f"D {key} decision level equals e6 heldout",
                                   "ok": bool(abs(ref["accuracy"] - dl["accuracy"]) < 1e-12
                                              and abs(ref["escalated"] - dl["escalated"]) < 1e-12
                                              and ref["tau"] == taus)})
            rec["latency_first_amortized"] = f == COMP
            rec["latency_second_amortized"] = s == COMP
            out["pairs"][key] = rec
            dlv = rec["decision_level"]
            log("D", key, "gain", round(100 * dlv["gain"], 2), dlv["ci"]["gain"],
                "p", round(dlv["p_gain_le_0"], 4))
            dump_partial("D_cascades", out)

    # per model and condition costs, cost checks, and cost sensitivity
    for m in MODELS:
        for cond in ["d1_neutral", "d2_k150", "d2_k5", "d2_k20"] + D3:
            if not has(m, cond) or not ans(m, cond):
                continue
            mine, ref = cost_check(m, cond)
            info = req_info(m, cond)
            ndec = sum(v["nq"] for v in info.values())
            out["costs"][f"{m}|{cond}"] = {"usd_per_1000_decisions": mine,
                                          "requests": len(info), "decisions": ndec}
            if ref is not None:
                checks.append({"what": f"D cost {m} {cond} equals cost_latency",
                               "ok": bool(abs(mine - ref) < 1e-12 * max(1.0, abs(ref)))})
            if m != bench.JEV and has(bench.JEV, cond):
                hosted = cost_check(bench.JEV, cond)[0]
                gpu_s = sum(v["lat"] for v in info.values()) / ndec
                out["cost_sensitivity"][f"{m}|{cond}"] = {
                    "gpu_seconds_per_decision": gpu_s,
                    "hosted_usd_per_1000_decisions": hosted,
                    "breakeven_usd_per_gpu_hour": hosted / 1000 * 3600 / gpu_s if gpu_s else None,
                    "usd_per_1000_at_utilization": {
                        "0.25": mine / 0.25, "0.5": mine / 0.5, "1.0": mine},
                    "assumed_usd_per_gpu_hour": USD_H,
                    "note": ("utilization u bills busy GPU seconds / u; at 100 percent this is "
                             "a04's figure")}
    RES["D_cascades"] = out
    RES.setdefault("consistency", {})["D"] = checks


def dump_partial(name, obj):
    RES[name] = obj
    dump()


# ------------------------------------------------------------------ E. paired comparisons

def section_E():
    pr = json.load(open(os.path.join(C.RESULTS, "paired.json"), encoding="utf-8"))
    out = {"definitions": {
        "difference": "accuracy of the other model minus Jev on identical decisions (a08)",
        "interval": ("paired cluster bootstrap over item_id (states on D1, five decisions "
                     "each), percentile 95 percent"),
        "p_value": ("two-sided bootstrap p = min(1, 2 min((1 + #{d* <= 0}), (1 + #{d* >= 0})) "
                    "/ (B + 1))"),
        "holm": "Holm step-down within each dataset across the compared models",
        "mcnemar": ("exact McNemar from a08 on decision pairs; ignores clustering on D1 where "
                    "five decisions share a state; on D2 and D3 one decision per item"),
        "estimand": ("the hosted model is analyzed on its rep 1 (bench.decisions default rep=1; "
                     "a01.main calls summarize(m, cond, 1)); reps 2 and 3 give the service "
                     "variability below"),
        "replicates": B_PAIRED},
        "families": {}, "jev_reps": {}}
    checks = []
    others = bench.MODELS_OPEN + [COMP]
    for cond in TASKS:
        fam = {}
        if not has(bench.JEV, cond):
            continue
        ja = {(r["item_id"], r["qid"]): float(np.argmax(r["p"]) == r["y"])
              for r in dec(bench.JEV, cond) if r["y"] >= 0 and not np.isnan(r["p"]).any()}
        for m in others:
            if not has(m, cond):
                continue
            ob = {(r["item_id"], r["qid"]): float(np.argmax(r["p"]) == r["y"])
                  for r in dec(m, cond) if r["y"] >= 0 and not np.isnan(r["p"]).any()}
            keys = sorted(set(ja) & set(ob))
            if len(keys) < 30:
                continue
            ca = np.array([ja[k] for k in keys])
            cb = np.array([ob[k] for k in keys])
            diff = cb - ca
            g = np.array([k[0] for k in keys])
            ug, inv = np.unique(g, return_inverse=True)
            s = np.bincount(inv, weights=diff)
            nn = np.bincount(inv).astype(float)
            rng = np.random.default_rng(C.SEED)
            pick = rng.integers(0, len(ug), (B_PAIRED, len(ug)))
            bd = s[pick].sum(1) / nn[pick].sum(1)
            mc = M.mcnemar(ca.astype(bool), cb.astype(bool))
            fam[m] = {"n": len(keys), "n_clusters": int(len(ug)), "acc_jev": float(ca.mean()),
                      "acc_other": float(cb.mean()), "diff": float(diff.mean()),
                      "diff_ci": pct(bd), "p_boot": boot_p_two(bd),
                      "mcnemar_p": mc["p"], "mcnemar_n01": mc["n01"], "mcnemar_n10": mc["n10"],
                      "mcnemar_ignores_clustering": cond == "d1_neutral",
                      "a08_diff_ci_1000": pr.get(f"{m}|{cond}", {}).get("diff_ci")}
            ref = pr.get(f"{m}|{cond}")
            if ref:
                checks.append({"what": f"E {m} {cond} diff and McNemar equal paired.json",
                               "ok": bool(abs(ref["diff"] - fam[m]["diff"]) < 1e-12
                                          and abs(ref["mcnemar_p"] - mc["p"]) < 1e-12)})
        if fam:
            ms = list(fam)
            adj = holm([fam[m]["p_boot"] for m in ms])
            adjm = holm([fam[m]["mcnemar_p"] for m in ms])
            for m, a, b in zip(ms, adj, adjm):
                fam[m]["p_holm"] = float(a)
                fam[m]["mcnemar_p_holm"] = float(b)
            out["families"][cond] = fam
            log("E", cond, {m: (round(100 * v["diff"], 1), round(v["p_holm"], 4)) for m, v in fam.items()})

        # Jev service variability
        reps = [r for r in bench.available_reps(bench.JEV, cond) if r <= 3]
        per = {}
        for r in reps:
            S = scored(bench.JEV, cond, r)
            if S is not None:
                per[str(r)] = {"n": int(len(S["y"])), "accuracy": float(S["correct"].mean()),
                               "ece": M.ece(S["conf"], S["correct"])}
        if per:
            accs = [v["accuracy"] for v in per.values()]
            eces = [v["ece"] for v in per.values()]
            jr = {"reps": per, "accuracy_range": [min(accs), max(accs)],
                  "ece_range": [min(eces), max(eces)],
                  "accuracy_spread": max(accs) - min(accs), "ece_spread": max(eces) - min(eces)}
            if cond == "d1_neutral":
                man = json.load(open(os.path.join(C.INPUTS, "manifest.json"), encoding="utf-8"))
                sub = set(man["_retest_subset"]["item_ids"])
                sp = {}
                for r in bench.available_reps(bench.JEV, cond):
                    S = scored(bench.JEV, cond, r)
                    msk = np.array([g in sub for g in S["groups"]])
                    sp[str(r)] = {"n": int(msk.sum()), "accuracy": float(S["correct"][msk].mean())}
                jr["retest_subset_reps"] = sp
            out["jev_reps"][cond] = jr
    RES["E_paired"] = out
    RES.setdefault("consistency", {})["E"] = checks


# ------------------------------------------------------------------ F. option names

def section_F():
    e2 = json.load(open(os.path.join(C.RESULTS, "e2_names.json"), encoding="utf-8"))
    rt = json.load(open(os.path.join(C.RESULTS, "retest.json"), encoding="utf-8"))
    out = {"definitions": {
        "flips": ("a02: share per hundred of decisions whose side of 0.5 on the positive-rubric "
                  "probability differs from the aligned no/yes condition, over the keys both "
                  "conditions answered"),
        "flips_interval": f"cluster bootstrap over item_id, {B_PAIRED} replicates",
        "delta_auc_interval": ("a02.delta_auc_ci: paired bootstrap over items, 1000 replicates, "
                               "AUC(naming) - AUC(kny) on the same draw"),
        "floor": ("test-retest flips per hundred: Jev measured on every binary set as kny rep 1 "
                  "vs rep 2 (a02) and as the mean over the three rep pairs (retest.json); open "
                  "models measured only as determinism on the 40-state d1_neutral subset "
                  "(rep 1 vs rep 2, 0 flips), not on the option-name sets themselves")},
        "results": {}}
    checks = []
    for m in A2.MODELS:
        for ds, pats in A2.SETS.items():
            conds = {n: pats[0].format(n) for n in A2.NAMINGS}
            if not all(has(m, c) for c in conds.values()):
                continue
            pp = {n: A2.pos_prob(m, c) for n, c in conds.items()}
            ref = pp["kny"]
            d = {}
            for n in ("k01", "krand", "kswap"):
                keys = sorted(set(ref) & set(pp[n]))
                fl = np.array([float((ref[k][0] >= 0.5) != (pp[n][k][0] >= 0.5)) for k in keys])
                g = np.array([k[0] for k in keys])
                ug, inv = np.unique(g, return_inverse=True)
                s = np.bincount(inv, weights=fl)
                nn = np.bincount(inv).astype(float)
                rng = np.random.default_rng(C.SEED)
                pick = rng.integers(0, len(ug), (B_PAIRED, len(ug)))
                bf = 100 * s[pick].sum(1) / nn[pick].sum(1)
                ev = e2[m][ds][n]
                d[n] = {"flips_per_100": 100 * float(fl.mean()), "flips_ci": pct(bf),
                        "n": len(keys), "n_clusters": int(len(ug)),
                        "delta_auc": ev["delta_auc_vs_kny"], "delta_auc_ci": ev["delta_auc_ci"]}
                checks.append({"what": f"F {m} {ds} {n} flips equal e2_names",
                               "ok": bool(abs(d[n]["flips_per_100"] - ev["flips_per_100_vs_kny"]) < 1e-9)})
            if m == bench.JEV:
                fl = e2[m]["retest_floor"].get(ds)
                cname = pats[0].format("kny")
                d["floor"] = {"measured": True,
                              "flips_per_100_rep1_vs_rep2": fl["flips_per_100"] if fl else None,
                              "argmax_flip_per_100_mean_over_rep_pairs":
                                  100 * rt[m][cname]["flip_rate"] if cname in rt[m] else None,
                              "n": fl["n"] if fl else None}
            else:
                d["floor"] = {"measured": False,
                              "determinism_d1_neutral_subset_flips_per_100":
                                  100 * rt.get(m, {}).get("d1_neutral", {}).get("flip_rate", np.nan),
                              "note": "no repeat of this option-name set was run"}
            out["results"][f"{m}|{ds}"] = d
            log("F", m, ds, {n: (round(d[n]["flips_per_100"], 1), d[n]["flips_ci"]) for n in ("k01", "krand", "kswap")})
    RES["F_option_names"] = out
    RES.setdefault("consistency", {})["F"] = checks


# ------------------------------------------------------------------ G. failures

def section_G():
    man = json.load(open(os.path.join(C.INPUTS, "manifest.json"), encoding="utf-8"))
    out = {"definitions": {
        "answered": "records without an error field (what bench.answers keeps)",
        "errors": "records with an error field, read from the raw files",
        "refusals": ("errors whose message states a length budget (Laya's head_max_len, the "
                     "comparator's prompt budget)"),
        "retries": ("not recorded: the harness retries transient failures (429, 529, 502, 503, "
                    "timeouts, connection errors) up to 7 attempts (6 for the Jev runner) with "
                    "exponential backoff and writes only the final outcome"),
        "truncation": ("not recorded for the decision models (Laya records its budgets "
                       "head_max_len and max_len but not whether an input was cut); for the "
                       "comparator, generations reaching max_tokens = 768 are counted as "
                       "truncated"),
        "superseded": ("answers/run_log.json lists this-that-1.0 as MISSING and comparator-open "
                       "as ERROR, and colab/answers_colab/.../comparator-open/ERROR.txt exists; "
                       "both predate the completed files in answers/, which are what is counted"),
        "scope": ("every answer file of the nine models except the D2 option-permutation "
                  "reruns (conditions ending _p2, _p3), which are counted by their own analysis")},
        "files": {}, "by_model": {}, "distinct_errors": {}}
    n_sub = len(man["_retest_subset"]["item_ids"])
    for m in MODELS:
        d = os.path.join(C.ANSWERS, m)
        tot = Counter()
        for fn in sorted(os.listdir(d)):
            if not fn.endswith(".jsonl"):
                continue
            cond, rep = fn[:-6].split("__rep")
            if re.search(r"_p\d+$", cond):
                continue            # permutation reruns of D2, counted by their own analysis
            lines = ok = err = refus = bad = empty = trunc = renorm = pct_scale = 0
            ok_keys, err_keys = set(), set()
            nq = 0
            for line in open(os.path.join(d, fn), encoding="utf-8"):
                if not line.strip():
                    continue
                lines += 1
                try:
                    j = json.loads(line)
                except json.JSONDecodeError:
                    bad += 1
                    continue
                if j.get("error"):
                    err += 1
                    err_keys.add(j["key"])
                    msg = str(j["error"])
                    if "head_max_len" in msg or "budget" in msg:
                        refus += 1
                    out["distinct_errors"].setdefault(msg, Counter())[f"{m}|{cond}|rep{rep}"] += 1
                    continue
                ok += 1
                ok_keys.add(j["key"])
                for q in j.get("answers", {}).values():
                    nq += 1
                    if not q.get("probs"):
                        empty += 1
                    if m == COMP:
                        raw = q.get("raw", {})
                        if (raw.get("usage_out") or 0) >= 768:
                            trunc += 1
                        try:
                            ps = [float(x["p"]) for x in json.loads(raw["raw_text"])["probabilities"]]
                            if abs(sum(ps) - 1) > 0.01:
                                renorm += 1
                            if any(p > 1 for p in ps):
                                pct_scale += 1
                        except Exception:  # noqa: BLE001
                            pass
            exp_req = man.get(cond, {}).get("requests")
            if cond == "d1_neutral" and lines <= n_sub < (exp_req or 0):
                exp_req = n_sub          # the retest subset repeats
            rec = {"condition": cond, "rep": int(rep), "lines": lines,
                   "expected_requests": exp_req,
                   "missing_requests": (exp_req - len(ok_keys)) if exp_req else None,
                   "answered": ok, "errors": err, "refusals": refus, "unparseable_lines": bad,
                   "keys_with_error_and_answer": len(ok_keys & err_keys),
                   "answered_questions": nq, "empty_probability_answers": empty,
                   "retries": "not recorded",
                   "truncation": trunc if m == COMP else "not recorded"}
            if m == COMP:
                rec["verbalized_not_summing_to_one"] = renorm
                rec["verbalized_on_percent_scale"] = pct_scale
            out["files"][f"{m}|{cond}|rep{rep}"] = rec
            tot["files"] += 1
            tot["answered"] += ok
            tot["errors"] += err
            tot["refusals"] += refus
            tot["answered_questions"] += nq
            if m == COMP:
                tot["truncated"] += trunc
                tot["verbalized_not_summing_to_one"] += renorm
                tot["verbalized_on_percent_scale"] += pct_scale
        out["by_model"][m] = dict(tot)
        log("G", m, dict(tot))
    out["distinct_errors"] = {k: dict(v) for k, v in out["distinct_errors"].items()}
    RES["G_failures"] = out


# ------------------------------------------------------------------ H. cardinality

def render_chars(crit):
    return len("\n".join(f"{k}: {v}" for k, v in crit.items()))


def section_H():
    QN = ["q1", "q2", "q3", "q4", "q5"]
    out = {"definitions": {
        "position": ("0-based index of the gold option in the rendered option list; quintile "
                     "= floor(5 x position / K), q1 the first fifth of the list"),
        "predicted_position": "quintile of the argmax option's position",
        "chars": ("characters of the rendered option list, 'key: text' lines joined by "
                  "newlines, and of the option texts alone, over the 600 in-scope utterances; "
                  "a proxy for option-token budgets until token counts are available")},
        "accuracy_by_position": {}, "predicted_position": {}, "chars": {}}
    for m in MODELS:
        for K in (20, 50, 150):
            cond = f"d2_k{K}"
            if not has(m, cond):
                continue
            S = scored(m, cond)
            if S is None:
                out["accuracy_by_position"][f"{m}|{cond}"] = {
                    "n": 0, "note": "no answered decision (every request refused, see G)"}
                continue
            pos = S["y"]
            q = np.floor(5 * pos / K).astype(int)
            pred = np.array([int(np.argmax(p)) for p in S["P"]])
            pq = np.floor(5 * pred / K).astype(int)
            d = {"n": int(len(pos))}
            for i, name in enumerate(QN):
                msk = q == i
                d[name] = {"n": int(msk.sum()),
                           "accuracy": float(S["correct"][msk].mean()) if msk.any() else None}
            out["accuracy_by_position"][f"{m}|{cond}"] = d
            pd_ = {name: float(np.mean(pq == i)) for i, name in enumerate(QN)}
            pd_["first_option"] = float(np.mean(pred == 0))
            pd_["last_option"] = float(np.mean(pred == K - 1))
            pd_["gold_share"] = {name: float(np.mean(q == i)) for i, name in enumerate(QN)}
            out["predicted_position"][f"{m}|{cond}"] = pd_
        log("H", m)
    for K in (5, 20, 50, 150):
        recs = [r for r in bench.inputs(f"d2_k{K}") if r["meta"]["in_scope"]]
        rc = np.array([render_chars(next(iter(r["questions"].values()))["criteria"]) for r in recs])
        tc = np.array([sum(len(v) for v in next(iter(r["questions"].values()))["criteria"].values())
                       for r in recs])
        out["chars"][str(K)] = {"n": len(recs), "rendered_mean": float(rc.mean()),
                                "rendered_median": float(np.median(rc)),
                                "rendered_min": int(rc.min()), "rendered_max": int(rc.max()),
                                "text_only_mean": float(tc.mean())}
    RES["H_cardinality"] = out


# ------------------------------------------------------------------ I. definitions

def section_I():
    RES["I_definitions"] = {
        "soft_accuracy": {
            "words": ("for each D1 decision, the teacher gold probability assigned to the option "
                      "the model ranks first, averaged over decisions (a01_e1_main.summarize)"),
            "symbols": "softacc = (1/N) sum_i s_i[argmax_o p_io]",
            "notes": ("s_i is the gold 'soft' distribution of decision i (the mean of three "
                      "teacher samples), renormalized to sum to one over the options; p_i is "
                      "the shipped distribution after bench.decisions renormalization; ties in "
                      "argmax go to the first option in request order")},
        "brier_soft": {
            "words": ("squared distance between the model's distribution and the teacher gold "
                      "distribution, summed over options and averaged over decisions"),
            "symbols": "briersoft = (1/N) sum_i sum_o (p_io - s_io)^2",
            "notes": "range 0 to 2; computed on shipped probabilities only"},
        "teacher_self_agreement": {
            "value": 0.735,
            "label": "p.anchor.ceiling",
            "source": ("collect_numbers.collect_params, typed down from the typed-decisions "
                       "dataset card (colab/cards/typed-decisions.md), not computed in this "
                       "repository"),
            "definition": ("the card describes it as a fresh teacher sample scored against gold "
                           "built from the other teacher samples; the gold is the mean of three "
                           "samples from a teacher endpoint at temperature 0.7"),
            "scale": ("an accuracy (argmax of the fresh sample against the argmax gold label), "
                      "listed in the card's Acc column, not a soft accuracy"),
            "population": ("the card states its three reference points were measured on the "
                           "1600-case set, while its leaderboard (Jev 0.727) is the 400-case test "
                           "split; our d1_neutral uses the 400 test states"),
            "other_references": {"majority_baseline": 0.520, "factor_ceiling": 0.704,
                                 "prior": 0.470}}}


# ------------------------------------------------------------------ main

def main():
    RES["meta"] = {"script": "src/a09_revision_stats.py", "seed": C.SEED, "folds": FOLDS,
                   "replicates_refit": B_REFIT, "replicates_boot": B_BOOT,
                   "replicates_paired": B_PAIRED, "level": LEVEL,
                   "usd_per_gpu_hour": USD_H, "jev_usd_per_mtok": C.PRICE_PER_MTOK,
                   "analyzed_rep": 1, "models": MODELS, "tasks": TASKS}
    raw_ok = section_C()
    dump()
    section_I()
    section_G()
    dump()
    section_H()
    dump()
    section_E()
    dump()
    section_F()
    dump()
    section_B()
    dump()
    section_A(raw_ok)
    dump()
    section_D()
    ch = RES["consistency"]
    RES["consistency"]["summary"] = {k: {"checks": len(v), "failed": sum(not c["ok"] for c in v)}
                                     for k, v in ch.items() if isinstance(v, list)}
    dump()
    log("done", RES["consistency"]["summary"])


if __name__ == "__main__":
    main()
