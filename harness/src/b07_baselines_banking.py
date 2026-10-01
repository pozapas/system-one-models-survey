"""Conventional baselines on the Banking77 intent task d2_banking77 (fourth revision).

As for CLINC-150 (b01): a logistic regression on BAAI/bge-small-en-v1.5 embeddings trained on
the Banking77 training utterances (shared/data/banking77/train.jsonl, written by
s00f_freeze_banking77.py; test utterances removed after normalization), with C chosen on a
class-balanced 20 percent validation part and one temperature fitted there (b04 rules), under
tag baseline-bge-small-lr-banking; and the zero-shot entailment classifier of b01 on the same
items (condition d2_banking77 added to baseline-nli-deberta-v3-base), with one temperature
fitted on 616 training utterances (8 per intent). Answers use the record format of
b01.write_answers, with probabilities over each item's own option order.

Summary to results/baselines_banking.json. Usage: python b07_baselines_banking.py
"""
import json
import os
import time

import numpy as np

import bench
import common as C
import metrics as M
import b01_baselines as B1
import b04_baselines_d3 as B4
from b02_clinc_overlap import norm

COND = "d2_banking77"
TAG_LR = "baseline-bge-small-lr-banking"
TAG_NLI = "baseline-nli-deberta-v3-base"


def train_rows():
    return [json.loads(l) for l in
            open(os.path.join(C.DATA, "banking77", "train.jsonl"), encoding="utf-8")]


def test_items():
    out = []
    for r in bench.inputs(COND):
        g = r["gold"]["intent"]
        out.append((r["key"], "intent", r["state"], g["native_options"], g["options"],
                    g["native_options"][g["options"].index(g["label"])]))
    return out


def write(tag, probs, model_id, revision, T):
    d = os.path.join(C.ANSWERS, tag)
    os.makedirs(d, exist_ok=True)
    path = os.path.join(d, f"{COND}__rep1.jsonl")
    assert not os.path.exists(path), f"{path} exists"
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        for r in bench.inputs(COND):
            g = r["gold"]["intent"]
            p = probs[r["key"]]
            pd = {o: float(v) for o, v in zip(g["options"], p)}
            ans = {"intent": {"probs": pd, "raw": {
                "served_temperature": 1.0, "probs_t1": pd, "fitted_temperature": T,
                "probs_scaled": {o: float(v) for o, v in zip(g["options"], M.apply_T(p, T))}}}}
            fh.write(json.dumps({"key": r["key"], "condition": COND, "rep": 1, "model": tag,
                                 "revision": revision, "model_returned": model_id,
                                 "served_temperature": 1.0, "run_date": B1.RUN_DATE,
                                 "latency_s": None, "usage_in": None, "answers": ans},
                                ensure_ascii=False) + "\n")


def main():
    summary = {}
    test = test_items()
    labels = sorted({l for *_, l in test})
    assert len(labels) == 77
    rows = train_rows()
    tn = {norm(t) for _, _, t, *_ in test}
    n0 = len(rows)
    rows = [r for r in rows if norm(r["text"]) not in tn]
    items = [{"text": r["text"], "y": labels.index(r["label"]), "group": i}
             for i, r in enumerate(rows)]
    rng = np.random.default_rng(C.SEED)
    _sel, tr_i, _va, vab_i = B4.cap_and_split(items, 77, rng)
    tr = [items[i] for i in tr_i]; va = [items[i] for i in vab_i]
    Etr, _ = B1.embed([r["text"] for r in tr]); Eva, _ = B1.embed([r["text"] for r in va])
    Ete, _ = B1.embed([t for _, _, t, *_ in test])
    ytr = np.array([r["y"] for r in tr]); yva = np.array([r["y"] for r in va])
    (c, acc, nll, m), grid = B4.fit_select(Etr, ytr, Eva, yva, 77)
    T = M.fit_T(list(m.predict_proba(Eva)), list(yva))
    Pl = m.predict_proba(Ete)                      # columns in sorted label order
    probs = {}
    for (key, _q, _t, native, _opts, _g), p in zip(test, Pl):
        probs[key] = np.array([p[labels.index(n)] for n in native])
    write(TAG_LR, probs, B1.BGE, B1.hub_rev(B1.BGE), T)
    yte = np.array([native.index(g) for (_k, _q, _t, native, _o, g) in test])
    summary["bge_lr"] = {"n_pool": n0, "dropped": n0 - len(rows), "n_train": len(tr),
                         "n_val_balanced": len(va), "C": c, "val_acc": acc, "T": T,
                         "test_acc": float(np.mean([np.argmax(probs[k]) == y for (k, *_), y
                                                    in zip(test, yte)]))}
    print("bge-lr", summary["bge_lr"], flush=True)

    sc = B1.NLIScorer()
    dec = B1.nli_pairs(COND)
    flat = [pr for d in dec for pr in d[3]]
    t0 = time.time()
    s = sc.score(flat)
    nli, k = {}, 0
    for key, qid, opts, prs in dec:
        nli[key] = B1.softmax(s[k:k + len(prs)])
        k += len(prs)
    q = bench.inputs(COND)[0]["questions"]["intent"]
    pick = []
    for lab in labels:
        idx = [i for i, r in enumerate(rows) if r["label"] == lab]
        pick += list(rng.choice(idx, 8, replace=False))
    Pv, yv = [], []
    for i in pick:
        prem = f"{rows[i]['text']}\n{q['instructions']}"
        prs = [(prem, f"This text is about {l.replace('_', ' ')}.") for l in labels]
        Pv.append(B1.softmax(sc.score(prs)))
        yv.append(labels.index(rows[i]["label"]))
    Tn = M.fit_T(Pv, yv)
    write(TAG_NLI, nli, B1.NLI, B1.hub_rev(B1.NLI), Tn)
    summary["nli"] = {"T": Tn, "seconds": time.time() - t0,
                      "test_acc": float(np.mean([np.argmax(nli[k]) == y for (k, *_), y
                                                 in zip(test, yte)]))}
    print("nli", summary["nli"], flush=True)
    C.dump(summary, "baselines_banking.json")


if __name__ == "__main__":
    main()
