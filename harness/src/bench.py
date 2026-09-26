"""Loading answers into aligned probability matrices, shared by every analysis script.

A decision is one (request, question) pair. For each condition and model the loader
returns one row per decision with the option keys in request order, the gold label,
the soft gold where the dataset has one, and the model's probability vector aligned
to those options. Missing or failed answers are kept as NaN rows and counted, never
silently dropped.
"""
import json
import os

import numpy as np

import common as C

MODELS_OPEN = ["laya-en", "laya-ml", "kev-0.8b", "decider-2b", "this-that-1.0",
               "kev-9b", "nimble-9b"]
JEV = "jev-1.13.0"


def inputs(cond):
    with open(os.path.join(C.INPUTS, f"{cond}.jsonl"), encoding="utf-8") as fh:
        return [json.loads(l) for l in fh if l.strip()]


def answers(model, cond, rep=1):
    path = os.path.join(C.ANSWERS, model, f"{cond}__rep{rep}.jsonl")
    out = {}
    if not os.path.exists(path):
        return out
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            try:
                j = json.loads(line)
            except json.JSONDecodeError:
                continue
            if j.get("error"):
                continue
            out[j["key"]] = j
    return out


def available_reps(model, cond):
    d = os.path.join(C.ANSWERS, model)
    if not os.path.isdir(d):
        return []
    reps = []
    for fn in os.listdir(d):
        if fn.startswith(cond + "__rep") and fn.endswith(".jsonl"):
            reps.append(int(fn[len(cond) + 5:-6]))
    return sorted(reps)


def t1_probs(p, T):
    """Undo a served temperature: softmax(z/T) raised to T and renormalized is softmax(z)."""
    if T is None or T == 1:
        return p
    q = np.clip(p, 1e-12, None) ** T
    return q / q.sum()


def decisions(model, cond, rep=1, raw=False):
    """One dict per decision; raw=True returns the T=1 probabilities where the model
    serves temperature-scaled ones."""
    recs = inputs(cond)
    ans = answers(model, cond, rep)
    rows = []
    for r in recs:
        a = ans.get(r["key"])
        for qid, g in r["gold"].items():
            opts = g["options"]
            p = np.full(len(opts), np.nan)
            lat = None
            if a is not None and a["answers"].get(qid) and a["answers"][qid]["probs"]:
                pr = a["answers"][qid]["probs"]
                p = np.array([float(pr.get(o, 0.0)) for o in opts])
                s = p.sum()
                p = p / s if s > 0 else np.full(len(opts), 1 / len(opts))
                if raw:
                    aq = a["answers"][qid]
                    rq = aq.get("raw") if isinstance(aq.get("raw"), dict) else {}
                    T = rq.get("served_temperature", a.get("served_temperature"))
                    # adapters store the exact T=1 distribution in raw.probs_t1 (Laya's
                    # per-bucket temperatures cannot be undone with one scalar)
                    rawp = aq.get("probs_t1") or rq.get("probs_t1")
                    if rawp:
                        p = np.array([float(rawp.get(o, 0.0)) for o in opts])
                        p = p / p.sum()
                    else:
                        p = t1_probs(p, T)
                lat = a.get("latency_s")
            y = opts.index(g["label"]) if g.get("label") in opts else -1
            soft = None
            if g.get("soft"):
                soft = np.array([g["soft"][o] for o in opts], dtype=float)
                soft = soft / soft.sum()
            rows.append({"key": r["key"], "item_id": r["item_id"], "qid": qid,
                         "type": g["type"], "options": opts, "y": y, "soft": soft,
                         "p": p, "meta": r["meta"], "latency_s": lat,
                         "usage_in": a.get("usage_in") if a else None,
                         "positive": g.get("positive")})
    return rows


def coverage(rows):
    n = len(rows)
    ok = sum(1 for r in rows if not np.isnan(r["p"]).any())
    return ok, n


def top(rows):
    """Arrays for top-label analyses over rows with a gold label and an answer."""
    rs = [r for r in rows if r["y"] >= 0 and not np.isnan(r["p"]).any()]
    conf = np.array([r["p"].max() for r in rs])
    correct = np.array([float(np.argmax(r["p"]) == r["y"]) for r in rs])
    K = np.array([len(r["options"]) for r in rs])
    return rs, conf, correct, K
