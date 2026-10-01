"""Conventional baselines on the human-rated emotion task d3_goemotions (fourth revision).

Two baselines, built exactly like their counterparts on the D3 tasks:
  baseline-bge-small-lr-goemo   logistic regression on BAAI/bge-small-en-v1.5 embeddings (b01
                                encoder), trained on the single-Ekman GoEmotions training comments
                                (shared/data/goemotions/train.jsonl, written by
                                s00e_freeze_goemotions.py, disjoint from the test split). The pool
                                is capped and split 80/20, C is chosen on the class-balanced
                                validation part and one temperature is fitted there (b04 rules:
                                cap_and_split, fit_select, metrics.fit_T).
  baseline-nli-deberta-v3-base  (condition d3_goemotions added to the existing tag) the zero-shot
                                entailment classifier of b01 (NLIScorer, hypothesis, nli_pairs),
                                with one temperature fitted on 600 training comments.

Answers are written in the record format of b01.write_answers. Summary to
results/baselines_goemo.json.

Usage: python b06_baselines_goemo.py
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

COND = "d3_goemotions"
LABELS = ["anger", "disgust", "fear", "joy", "sadness", "surprise"]
TAG_LR = "baseline-bge-small-lr-goemo"
TAG_NLI = "baseline-nli-deberta-v3-base"


def train_rows():
    p = os.path.join(C.DATA, "goemotions", "train.jsonl")
    return [json.loads(l) for l in open(p, encoding="utf-8")]


def write(tag, probs, model_id, revision, T):
    d = os.path.join(C.ANSWERS, tag)
    os.makedirs(d, exist_ok=True)
    path = os.path.join(d, f"{COND}__rep1.jsonl")
    assert not os.path.exists(path), f"{path} exists"
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        for r in bench.inputs(COND):
            ans = {}
            for qid, g in r["gold"].items():
                p = probs[(r["key"], qid)]
                pd = {o: float(v) for o, v in zip(g["options"], p)}
                ans[qid] = {"probs": pd,
                            "raw": {"served_temperature": 1.0, "probs_t1": pd,
                                    "fitted_temperature": T,
                                    "probs_scaled": {o: float(v) for o, v in
                                                     zip(g["options"], M.apply_T(p, T))}}}
            fh.write(json.dumps({"key": r["key"], "condition": COND, "rep": 1, "model": tag,
                                 "revision": revision, "model_returned": model_id,
                                 "served_temperature": 1.0, "run_date": B1.RUN_DATE,
                                 "latency_s": None, "usage_in": None, "answers": ans},
                                ensure_ascii=False) + "\n")


def test_texts():
    out = []
    for r in bench.inputs(COND):
        for qid, g in r["gold"].items():
            out.append((r["key"], qid, r["state"], g["options"].index(g["label"])))
    return out


def run_lr(summary):
    rows = train_rows()
    test = test_texts()
    test_norm = {norm(t) for _, _, t, _ in test}
    n_before = len(rows)
    rows = [r for r in rows if norm(r["text"]) not in test_norm]
    y = np.array([LABELS.index(r["label"]) for r in rows])
    rng = np.random.default_rng(C.SEED)
    items = [{"text": r["text"], "y": int(v), "group": r["id"]} for r, v in zip(rows, y)]
    _sel, tr_i, _va_i, vab_i = B4.cap_and_split(items, len(LABELS), rng)
    tr = [items[i] for i in tr_i]
    va = [items[i] for i in vab_i]      # class-balanced validation part, as in b04
    Etr, _ = B1.embed([r["text"] for r in tr])
    Eva, _ = B1.embed([r["text"] for r in va])
    Ete, n_trunc = B1.embed([t for _, _, t, _ in test])
    ytr = np.array([r["y"] for r in tr]); yva = np.array([r["y"] for r in va])
    (c, acc, nll, m), grid = B4.fit_select(Etr, ytr, Eva, yva, len(LABELS))
    T = M.fit_T(list(m.predict_proba(Eva)), list(yva))
    P = m.predict_proba(Ete)
    probs = {(k, q): p for (k, q, _, _), p in zip(test, P)}
    write(TAG_LR, probs, B1.BGE, B1.hub_rev(B1.BGE), T)
    yte = np.array([g for *_, g in test])
    summary["bge_lr"] = {"n_pool": n_before, "n_dropped_as_test_text": n_before - len(rows),
                         "n_train": len(tr), "n_val_balanced": len(va), "C": c,
                         "val_acc": acc, "T": T,
                         "test_acc": float(np.mean(P.argmax(1) == yte))}
    print("bge-lr", summary["bge_lr"], flush=True)


def run_nli(summary):
    sc = B1.NLIScorer()
    dec = B1.nli_pairs(COND)
    flat = [pr for d in dec for pr in d[3]]
    t0 = time.time()
    s = sc.score(flat)
    secs = time.time() - t0
    probs, k = {}, 0
    for key, qid, opts, prs in dec:
        probs[(key, qid)] = B1.softmax(s[k:k + len(prs)])
        k += len(prs)
    # temperature on 600 training comments (100 per emotion), same premise and hypotheses
    q = bench.inputs(COND)[0]["questions"]["emotion"]
    opts = bench.inputs(COND)[0]["gold"]["emotion"]["options"]
    rows = train_rows()
    rng = np.random.default_rng(C.SEED)
    pick = []
    for lab in LABELS:
        idx = [i for i, r in enumerate(rows) if r["label"] == lab]
        pick += list(rng.choice(idx, 100, replace=False))
    Pv, yv = [], []
    for i in pick:
        prem = f"{B1.state_text(rows[i]['text'])}\n{q['instructions']}"
        prs = [(prem, B1.hypothesis(q, j, o)) for j, o in enumerate(opts)]
        Pv.append(B1.softmax(sc.score(prs)))
        yv.append(LABELS.index(rows[i]["label"]))
    T = M.fit_T(Pv, yv)
    write(TAG_NLI, probs, B1.NLI, B1.hub_rev(B1.NLI), T)
    yte = {(r["key"], qid): g["options"].index(g["label"])
           for r in bench.inputs(COND) for qid, g in r["gold"].items()}
    acc = float(np.mean([np.argmax(p) == yte[k] for k, p in probs.items()]))
    summary["nli"] = {"T": T, "seconds": secs, "test_acc": acc,
                      "truncated": len(sc.truncated)}
    print("nli", summary["nli"], flush=True)


def main():
    summary = {}
    run_lr(summary)
    run_nli(summary)
    C.dump(summary, "baselines_goemo.json")


if __name__ == "__main__":
    main()
