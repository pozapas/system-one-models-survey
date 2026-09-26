"""E1 and E4: same-harness accuracy and calibration for every model on D1 to D3.

For each model and main condition this reports accuracy with a state-clustered
bootstrap interval, macro-F1 where classes are nominal, the multi-class Brier score,
NLL, and top-label equal-mass ECE in three forms:

    shipped   the probabilities as the service or checkpoint serves them
    raw       T = 1 logits, which differ from shipped only for checkpoints that
              apply a stored temperature (Kev, decider)
    scaled    shipped probabilities after one temperature per primitive type,
              fitted on a disjoint slice (D1 on d1_calib; D2 and D3 by five-fold
              cross-fitting disjoint by item)

plus the Murphy decomposition of the top-label Brier score, AURC and coverage at 1
and 5 percent risk. D1 additionally gets soft accuracy and soft Brier against the
teacher distribution, which is what its leaderboard reports.

Output: results/e1_main.json
"""
import numpy as np

import bench
import common as C
import metrics as M

MAIN = ["d1_native", "d1_neutral", "d2_k150", "d3_conv_go_awry", "d3_wiki_corpus",
        "d3_emotion", "d3_wiki_politeness"]
ALL_MODELS = [bench.JEV] + bench.MODELS_OPEN + ["comparator-open"]


def fit_types(model, rep=1):
    """Temperatures per primitive type fitted on d1_calib."""
    rows = [r for r in bench.decisions(model, "d1_calib", rep)
            if r["y"] >= 0 and not np.isnan(r["p"]).any()]
    out = {}
    for t in ("choice", "noul", "score"):
        rs = [r for r in rows if r["type"] == t]
        if len(rs) >= 30:
            out[t] = M.fit_T([r["p"] for r in rs], [r["y"] for r in rs])
    return out


def summarize(model, cond, rep=1, T_types=None):
    rows = bench.decisions(model, cond, rep)
    ok, n = bench.coverage(rows)
    if ok == 0:
        return None
    rs = [r for r in rows if r["y"] >= 0 and not np.isnan(r["p"]).any()]
    raw_rows = {r["key"] + r["qid"]: r for r in bench.decisions(model, cond, rep, raw=True)}
    P = [r["p"] for r in rs]
    y = np.array([r["y"] for r in rs])
    groups = np.array([r["item_id"] for r in rs])
    conf = np.array([p.max() for p in P])
    correct = np.array([float(np.argmax(p) == k) for p, k in zip(P, y)])
    Praw = [raw_rows[r["key"] + r["qid"]]["p"] for r in rs]
    conf_raw = np.array([p.max() for p in Praw])
    corr_raw = np.array([float(np.argmax(p) == k) for p, k in zip(Praw, y)])

    # temperature scaling on a disjoint slice
    if cond.startswith("d1") and T_types:
        Ps = [M.apply_T(p, T_types.get(r["type"], 1.0)) for p, r in zip(P, rs)]
        T_used = T_types
    else:
        Ps, Ts = M.crossfit_T(P, y, groups)
        T_used = {"crossfit_folds": Ts}
    conf_s = np.array([p.max() for p in Ps])
    corr_s = np.array([float(np.argmax(p) == k) for p, k in zip(Ps, y)])

    acc = float(correct.mean())
    out = {"model": model, "condition": cond, "rep": rep, "n_decisions": n,
           "n_answered": ok, "n_scored": len(rs),
           "accuracy": acc,
           "accuracy_ci": M.cluster_boot(lambda i: correct[i].mean(), groups),
           "brier": M.brier_multi(P, y), "nll": M.nll(P, y),
           "ece_shipped": M.ece(conf, correct),
           "ece_shipped_ci": M.cluster_boot(lambda i: M.ece(conf[i], correct[i]), groups,
                                            reps=400),
           "ece_raw": M.ece(conf_raw, corr_raw),
           "ece_scaled": M.ece(conf_s, corr_s),
           "ece_scaled_ci": M.cluster_boot(lambda i: M.ece(conf_s[i], corr_s[i]), groups,
                                           reps=400),
           "nll_scaled": M.nll(Ps, y), "brier_scaled": M.brier_multi(Ps, y),
           "temperature": T_used,
           "murphy_shipped": M.murphy(conf, correct),
           "murphy_scaled": M.murphy(conf_s, corr_s),
           "aurc_shipped": M.aurc(conf, correct), "aurc_scaled": M.aurc(conf_s, corr_s),
           "mean_confidence": float(conf.mean()),
           "share_conf_ge_0_9": float(np.mean(conf >= 0.9)),
           "acc_when_conf_ge_0_9": float(correct[conf >= 0.9].mean()) if np.any(conf >= 0.9)
           else None,
           "distinct_prob_values": int(len(np.unique(np.round(np.concatenate(P), 6))))}
    for risk in (0.01, 0.05):
        cov, thr = M.coverage_at_risk(conf, correct, risk)
        cov_s, thr_s = M.coverage_at_risk(conf_s, corr_s, risk)
        out[f"coverage_at_{int(risk * 100)}pct"] = cov
        out[f"threshold_at_{int(risk * 100)}pct"] = thr
        out[f"coverage_at_{int(risk * 100)}pct_scaled"] = cov_s
        out[f"review_budget_at_{int(risk * 100)}pct"] = 1 - cov
    if cond.startswith("d3"):
        k = len(rs[0]["options"])
        out["macro_f1"] = M.macro_f1([int(np.argmax(p)) for p in P], y, k)
    if cond.startswith("d1"):
        out["soft_accuracy"] = float(np.mean([r["soft"][np.argmax(r["p"])] for r in rs]))
        out["brier_soft"] = float(np.mean([np.sum((r["p"] - r["soft"]) ** 2) for r in rs]))
        by = {}
        for t in ("choice", "noul", "score"):
            m = np.array([r["type"] == t for r in rs])
            by[t] = {"n": int(m.sum()), "accuracy": float(correct[m].mean()),
                     "ece_shipped": M.ece(conf[m], correct[m]),
                     "ece_scaled": M.ece(conf_s[m], corr_s[m])}
        out["by_type"] = by
    if cond == "d2_k150":
        ins = np.array([r["meta"]["in_scope"] for r in rs])
        out["n_in_scope"] = int(ins.sum())
    return out


def d2_oos(model, rep=1):
    """Out-of-scope detection on d2_k150 by the top probability: AUROC for separating
    in-scope from out-of-scope inputs, and in-scope accuracy."""
    rows = [r for r in bench.decisions(model, "d2_k150", rep) if not np.isnan(r["p"]).any()]
    if not rows:
        return None
    conf = np.array([r["p"].max() for r in rows])
    ins = np.array([r["meta"]["in_scope"] for r in rows])
    return {"auroc_in_vs_oos": M.auroc(conf, ins),
            "mean_conf_in": float(conf[ins].mean()), "mean_conf_oos": float(conf[~ins].mean()),
            "share_oos_conf_ge_0_9": float(np.mean(conf[~ins] >= 0.9)),
            "n_in": int(ins.sum()), "n_oos": int((~ins).sum())}


def main():
    res = {}
    for m in ALL_MODELS:
        T_types = fit_types(m) if bench.available_reps(m, "d1_calib") else None
        for cond in MAIN:
            if not bench.available_reps(m, cond):
                continue
            s = summarize(m, cond, 1, T_types)
            if s is None:
                continue
            res[f"{m}|{cond}"] = s
            print(f"{m:16s} {cond:20s} n={s['n_scored']:5d} acc={s['accuracy']:.3f} "
                  f"ece={s['ece_shipped']:.3f}->{s['ece_scaled']:.3f} "
                  f"cov5={s['coverage_at_5pct']:.2f}", flush=True)
        o = d2_oos(m) if bench.available_reps(m, "d2_k150") else None
        if o:
            res[f"{m}|d2_oos"] = o
    C.dump(res, "e1_main.json")


if __name__ == "__main__":
    main()
