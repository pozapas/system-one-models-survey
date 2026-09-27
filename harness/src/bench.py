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

# Second revision runs (build_revision2_notebook.py). None of these is part of MODELS_OPEN:
# the analyses add them as extra models only when their answer folders exist, after the
# original models, so every earlier result stays as it was.
COMPARATORS_2 = ["comparator-open2", "comparator-open2-ll",
                 "comparator-open2-awq", "comparator-open2-awq-ll"]
COMPARATORS_2_B1 = ["comparator-open2-b1", "comparator-open2-ll-b1",
                    "comparator-open2-awq-b1", "comparator-open2-awq-ll-b1"]
BATCHED = ("comparator-open",) + tuple(COMPARATORS_2)     # latency amortized over a batch
BACKBONES = ["backbone-qwen35-0.8b-base", "backbone-qwen35-2b-base",
             "backbone-qwen35-9b-base", "backbone-qwen35-9b"]
# decision model -> the untuned backbone it adapts (adapters.BACKBONE_OF)
BACKBONE_OF = {"kev-9b": "backbone-qwen35-9b-base", "nimble-9b": "backbone-qwen35-9b",
               "decider-2b": "backbone-qwen35-2b-base",
               "this-that-1.0": "backbone-qwen35-2b-base",
               "kev-0.8b": "backbone-qwen35-0.8b-base"}
USD_PER_UNIT = 9.99 / 100          # Colab Pro: 100 compute units for 9.99 USD (a04)


def present(models):
    """The models of the list that have an answer folder."""
    return [m for m in models if os.path.isdir(os.path.join(C.ANSWERS, m))]


def usd_per_gpu_hour(model, default):
    """GPU price per hour for a model of the second revision run: the compute units per hour
    that answers/run_log_revision2.json records as assumed for the GPU of that model's part
    (part 1 backbones, part 2 comparators), times USD_PER_UNIT. Without the log, the planned
    GPU's rate is used (A100 11.8 units per hour for the FP8 comparator, L4 4.8 otherwise).
    Every other model gets `default` (a04's L4 rate), unchanged."""
    if model not in COMPARATORS_2 + COMPARATORS_2_B1 + BACKBONES:
        return default
    units = {"L4": 4.8, "A100": 11.8}
    gpu = "L4" if (model in BACKBONES or "-awq" in model) else "A100"
    p = os.path.join(C.ANSWERS, "run_log_revision2.json")
    if os.path.exists(p):
        log = json.load(open(p, encoding="utf-8"))
        units.update(log.get("units_per_hour_assumed") or {})
        name = log.get("part1_gpu" if model in BACKBONES else "part2_gpu") or ""
        for g in ("A100", "H100", "L4", "T4"):
            if g in name:
                gpu = g
                break
    return float(units.get(gpu, 4.8)) * USD_PER_UNIT


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
