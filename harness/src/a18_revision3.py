"""Third-revision results: the explicit out-of-scope option and description scoring.

A. Out-of-scope option (d2_k150_oos, frozen by s00d_freeze_oos_option.py). The 800 CLINC-150
   requests of d2_k150 with the 150 intents plus o151 "out of scope". Per model:
     acc_in          accuracy on the 600 in-scope requests (o151 counts as an error)
     oos_recall      share of the 200 out-of-scope requests answered with o151
     false_reject    share of in-scope requests answered with o151
   and two gates for the intent-routing case, reported like the gate of a09 section B:
     option          route every request not answered with o151
     option_gate     route a request only when it is not answered with o151 AND its top
                     probability reaches a threshold that targets 5 percent risk on the in-scope
                     decisions of the other folds (a09's fold map, thr_at_risk and apply_thr)
   with coverage, realized risk and its one-sided Clopper-Pearson bound on the in-scope
   requests, and false acceptance on the out-of-scope requests. The option gate carries
   cluster-bootstrap intervals whose replicates refit the thresholds (a09's B_REFIT).

B. Description scoring of the untuned backbones (backbone-desc-*). Accuracy on each benchmark
   next to the key-scoring accuracy of the same backbone (a15), for the backbones whose runs
   are complete.

Output: results/revision3.json
"""
import numpy as np

import bench
import common as C
import a09_revision_stats as R

OOS_COND = "d2_k150_oos"
OOS_IDX = 150
MODELS = [bench.JEV, "laya-ml", "kev-0.8b", "decider-2b", "this-that-1.0", "kev-9b", "nimble-9b",
          "comparator-open", "comparator-open2", "comparator-open2-ll", "comparator-gemma",
          "comparator-gemma-ll", "comparator-mistral", "comparator-mistral-ll",
          "comparator-open2-think"]
DESC = {"backbone-desc-qwen35-0.8b-base": "backbone-qwen35-0.8b-base",
        "backbone-desc-qwen35-2b-base": "backbone-qwen35-2b-base",
        "backbone-desc-qwen35-9b-base": "backbone-qwen35-9b-base",
        "backbone-desc-qwen35-9b": "backbone-qwen35-9b"}
DESC_CONDS = ["d1_neutral", "d2_k150", "d3_conv_go_awry", "d3_wiki_corpus", "d3_emotion",
              "d3_wiki_politeness"]


def oos_option(m):
    rows = [r for r in R.dec(m, OOS_COND) if not np.isnan(r["p"]).any()]
    if len(rows) < 800:
        return None
    pred = np.array([int(np.argmax(r["p"])) for r in rows])
    conf = np.array([float(r["p"].max()) for r in rows])
    ins = np.array([bool(r["meta"]["in_scope"]) for r in rows])
    cor = np.array([float(int(np.argmax(r["p"])) == r["y"]) for r in rows])
    items = np.array([r["item_id"] for r in rows])
    say_oos = pred == OOS_IDX
    # a request answered with o151 is never routed, whatever its confidence
    conf_route = np.where(say_oos, -1.0, conf)

    def summary(acc_mask):
        i_in, i_oos = ins, ~ins
        n_acc = int(acc_mask[i_in].sum())
        n_err = int(np.sum(acc_mask[i_in] & (cor[i_in] == 0)))
        return {"coverage_in": n_acc / int(i_in.sum()),
                "risk_in": n_err / n_acc if n_acc else None,
                "risk_in_upper_95_one_sided_cp": R.cp_upper_one_sided(n_err, n_acc),
                "oos_false_acceptance": float(acc_mask[i_oos].mean())}

    def gate(ii, fr):
        acc = np.zeros(len(ii), bool)
        for k in range(R.FOLDS):
            trm = (fr[ii] != k) & ins[ii]
            t = R.thr_at_risk(conf_route[ii][trm], cor[ii][trm], 0.05)
            te = fr[ii] == k
            acc[te] = R.apply_thr(conf_route[ii][te], t) & (conf_route[ii][te] >= 0)
        i_in, i_oos = ins[ii], ~ins[ii]
        n_in_acc = int(acc[i_in].sum())
        n_err = int(np.sum(acc[i_in] & (cor[ii][i_in] == 0)))
        return (float(n_in_acc / i_in.sum()), n_err / n_in_acc if n_in_acc else np.nan,
                float(acc[i_oos].mean()), n_in_acc, n_err)

    f = R.folds_of(items)
    allidx = np.arange(len(rows))
    cov, risk, far, n_acc, n_err = gate(allidx, f)
    cla = R.Clusters(items)
    rng = np.random.default_rng(C.SEED)
    bs = []
    for _ in range(R.B_REFIT):
        pick, ii = cla.draw(rng)
        fr = cla.fold_rows(pick, rng)
        bs.append(gate(ii, fr))
    bs = np.array(bs)
    out = {"n_in": int(ins.sum()), "n_oos": int((~ins).sum()),
           "acc_in": float(cor[ins].mean()),
           "oos_recall": float(say_oos[~ins].mean()),
           "false_reject": float(say_oos[ins].mean()),
           "option": summary(~say_oos),
           "option_gate": {"coverage_in": cov, "coverage_in_ci": R.pct(bs[:, 0]),
                           "risk_in": risk, "risk_in_ci": R.pct(bs[:, 1]),
                           "accepted_in": n_acc, "errors_in": n_err,
                           "risk_in_upper_95_one_sided_cp": R.cp_upper_one_sided(n_err, n_acc),
                           "oos_false_acceptance": far,
                           "oos_false_acceptance_ci": R.pct(bs[:, 2])}}
    print(m, {k: (round(v, 3) if isinstance(v, float) else v) for k, v in out.items()
              if not isinstance(v, dict)}, "gate", round(cov, 3), round(far, 3), flush=True)
    return out


def acc_of(m, cond):
    rows = [r for r in R.dec(m, cond) if not np.isnan(r["p"]).any() and r["y"] >= 0
            and (r.get("meta") or {}).get("in_scope", True)]
    if not rows:
        return None, 0
    return float(np.mean([np.argmax(r["p"]) == r["y"] for r in rows])), len(rows)


def desc_scoring():
    out = {}
    for d, k in DESC.items():
        if not all(bench.available_reps(d, c) for c in DESC_CONDS):
            continue
        res = {}
        for c in DESC_CONDS:
            a_d, n_d = acc_of(d, c)
            a_k, n_k = acc_of(k, c)
            if n_d < n_k:          # an incomplete description run is not reported
                res = None
                break
            res[c] = {"acc_desc": a_d, "acc_key": a_k, "n": n_d}
        if res:
            out[d] = res
            print(d, {c: (round(v["acc_desc"], 3), round(v["acc_key"], 3)) for c, v in res.items()})
    return out


def main():
    res = {"oos_option": {}, "desc_scoring": desc_scoring()}
    for m in MODELS:
        if bench.available_reps(m, OOS_COND):
            r = oos_option(m)
            if r:
                res["oos_option"][m] = r
    C.dump(res, "revision3.json")


if __name__ == "__main__":
    main()
