"""E6: confidence-gated cascades.

A first-stage model answers every decision; decisions whose top probability falls
below a threshold tau are escalated to a second-stage model, whose answer replaces
the first. Sweeping tau over the observed confidences traces retained quality
(cascade accuracy over second-stage accuracy) against cost fraction (the cascade's
cost per decision over the second stage's cost per decision, with the first stage
always paid). Costs per decision come from results/cost_latency.json.

Pairs: every decision model first with the generative comparator second, and each
open decision model first with the hosted model second.

Output: results/e6_cascade.json
"""
import json
import os

import numpy as np

import bench
import common as C

CONDS = ["d1_neutral", "d2_k150", "d3_conv_go_awry", "d3_wiki_corpus", "d3_emotion",
         "d3_wiki_politeness"]
COMPARATORS = ["comparator-open"]


def aligned(first, second, cond, with_items=False):
    a = {r["key"] + "|" + r["qid"]: r for r in bench.decisions(first, cond)
         if r["y"] >= 0 and not np.isnan(r["p"]).any()}
    b = {r["key"] + "|" + r["qid"]: r for r in bench.decisions(second, cond)
         if r["y"] >= 0 and not np.isnan(r["p"]).any()}
    keys = sorted(set(a) & set(b))
    conf = np.array([a[k]["p"].max() for k in keys])
    c1 = np.array([np.argmax(a[k]["p"]) == a[k]["y"] for k in keys])
    c2 = np.array([np.argmax(b[k]["p"]) == b[k]["y"] for k in keys])
    if with_items:
        return conf, c1, c2, [a[k]["item_id"] for k in keys]
    return conf, c1, c2


def cost_per_decision(cl, model, cond):
    v = cl.get(model, {}).get(cond) or cl.get(model, {}).get("d1_neutral")
    if not v or v.get("usd_per_1000_decisions") is None:
        return None
    return v["usd_per_1000_decisions"] / 1000


def curve(conf, c1, c2, k1, k2):
    taus = np.unique(np.r_[0.0, conf, 1.0 + 1e-9])
    acc2 = c2.mean()
    pts = []
    for t in taus:
        esc = conf < t
        acc = np.where(esc, c2, c1).mean()
        cf = None if (k1 is None or k2 in (None, 0)) else (k1 + esc.mean() * k2) / k2
        pts.append({"tau": float(t), "escalated": float(esc.mean()), "accuracy": float(acc),
                    "retained": float(acc / acc2) if acc2 > 0 else None, "cost_fraction": cf})
    return pts


def summary(pts, acc2):
    match = [p for p in pts if p["accuracy"] >= acc2]
    best = max(pts, key=lambda p: p["accuracy"])
    out = {"best_accuracy": best["accuracy"], "best_escalated": best["escalated"],
           "best_cost_fraction": best["cost_fraction"]}
    if match:
        m = min(match, key=lambda p: p["escalated"])
        out.update({"match_escalated": m["escalated"], "match_cost_fraction": m["cost_fraction"],
                    "match_tau": m["tau"]})
    for target in (0.95, 0.99):
        ok = [p for p in pts if p["retained"] is not None and p["retained"] >= target]
        if ok:
            m = min(ok, key=lambda p: p["escalated"])
            out[f"retain{int(target * 100)}_escalated"] = m["escalated"]
            out[f"retain{int(target * 100)}_cost_fraction"] = m["cost_fraction"]
    return out


def best_tau(conf, c1, c2):
    """Threshold maximizing cascade accuracy on the given decisions (ties: least escalation)."""
    taus = np.unique(np.r_[0.0, conf, 1.0 + 1e-9])
    accs = [np.where(conf < t, c2, c1).mean() for t in taus]
    best = max(accs)
    return float(min(t for t, a in zip(taus, accs) if a == best))


def heldout(f, s, cond, conf, c1, c2, k1, k2, keys_items):
    """Cascade scored with a threshold chosen on data the scored items never touch: the
    d1_calib slice for D1, five-fold cross-fitting disjoint by item otherwise."""
    if cond == "d1_neutral" and bench.available_reps(f, "d1_calib") and             bench.available_reps(s, "d1_calib"):
        cc, cc1, cc2 = aligned(f, s, "d1_calib")
        tau = best_tau(cc, cc1, cc2)
        esc = conf < tau
        taus = [tau]
    else:
        rng = np.random.default_rng(C.SEED)
        items = np.array(keys_items)
        uniq = np.unique(items)
        rng.shuffle(uniq)
        fold = {u: i % 5 for i, u in enumerate(uniq)}
        fo = np.array([fold[i] for i in items])
        esc = np.zeros(len(conf), bool)
        taus = []
        for k in range(5):
            tr, te = fo != k, fo == k
            t = best_tau(conf[tr], c1[tr], c2[tr])
            taus.append(t)
            esc[te] = conf[te] < t
    acc = float(np.where(esc, c2, c1).mean())
    cf = None if (k1 is None or k2 in (None, 0)) else float((k1 + esc.mean() * k2) / k2)
    return {"accuracy": acc, "escalated": float(esc.mean()), "cost_fraction": cf,
            "tau": taus, "gain": acc - max(c1.mean(), c2.mean())}


def main():
    p = os.path.join(C.RESULTS, "cost_latency.json")
    cl = json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {}
    firsts = [bench.JEV] + bench.MODELS_OPEN
    pairs = [(f, c) for c in COMPARATORS for f in firsts]
    pairs += [(f, bench.JEV) for f in bench.MODELS_OPEN]
    res = {}
    for f, s in pairs:
        for cond in CONDS:
            if not (bench.available_reps(f, cond) and bench.available_reps(s, cond)):
                continue
            conf, c1, c2, items = aligned(f, s, cond, with_items=True)
            if len(conf) < 50:
                continue
            k1, k2 = cost_per_decision(cl, f, cond), cost_per_decision(cl, s, cond)
            pts = curve(conf, c1, c2, k1, k2)
            res[f"{f}>{s}|{cond}"] = {"n": int(len(conf)), "acc_first": float(c1.mean()),
                                      "acc_second": float(c2.mean()),
                                      "summary": summary(pts, c2.mean()), "curve": pts,
                                      "heldout": heldout(f, s, cond, conf, c1, c2, k1, k2, items)}
            print(f"{f:14s} > {s:16s} {cond:20s} acc1={c1.mean():.3f} acc2={c2.mean():.3f} "
                  f"{res[f'{f}>{s}|{cond}']['summary']}", flush=True)
    C.dump(res, "e6_cascade.json")


if __name__ == "__main__":
    main()
