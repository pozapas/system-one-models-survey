"""Two sensitivity checks on the generative comparators and the probability grid.

Reply format. The verbal protocol (comparator_parse) matches a reported key only when it
equals an option key exactly. Some replies write the key followed by ": description", the
rendering the prompt itself uses, and fall back to a uniform distribution. This re-parses
every verbal reply accepting a reported key whose text before the first colon is an option
key, with everything else unchanged (negatives clipped, renormalized over matched options,
uniform when none match), and reports how many replies it recovers and the accuracy on
the scored decisions (in-scope on D2, as e1 reports it).

Probability grid. The hosted model returns probabilities on a two-decimal grid, which ties
confidences and can lower its in-sample coverage at a fixed risk. This rounds the
distributions of every other model to the same grid, renormalizes, and recomputes the
in-sample coverage at five percent risk on D1 and D2.

Output: results/parse_rounding.json
"""
import json
import os

import numpy as np

import bench
import common as C
import metrics as M

VERBAL = ["comparator-open", "comparator-open2"]
CONDS = ["d1_neutral", "d2_k150", "d3_conv_go_awry", "d3_wiki_corpus", "d3_emotion",
         "d3_wiki_politeness"]
ROUND_MODELS = [bench.JEV] + bench.MODELS_OPEN + ["comparator-open"] + \
    bench.present(bench.COMPARATORS_2)
RISK = 0.05


def raw_texts(model, cond):
    f = os.path.join(C.ANSWERS, model, f"{cond}__rep1.jsonl")
    out = {}
    if not os.path.exists(f):
        return out
    for line in open(f, encoding="utf-8"):
        if line.startswith("{"):
            r = json.loads(line)
            for qid, a in (r.get("answers") or {}).items():
                out[(r["key"], qid)] = (a.get("raw") or {}).get("raw_text") or ""
    return out


def lenient(txt, opts):
    try:
        items = json.loads(txt).get("probabilities") or []
    except Exception:
        items = []
    q = np.zeros(len(opts))
    for it in items:
        if not isinstance(it, dict):
            continue
        v = it.get("p", it.get("probability"))
        if not isinstance(v, (int, float)):
            continue
        k = str(it.get("key", "")).strip()
        k0 = k.split(":")[0].strip()
        if k in opts:
            q[opts.index(k)] += max(v, 0.0)
        elif k0 in opts:
            q[opts.index(k0)] += max(v, 0.0)
    return q / q.sum() if q.sum() > 0 else np.full(len(opts), 1.0 / len(opts))


def scored(d):
    return d["y"] >= 0 and bool((d.get("meta") or {}).get("in_scope", True))


def reparse():
    out = {}
    for m in VERBAL:
        for cond in CONDS:
            if not bench.available_reps(m, cond):
                continue
            raw = raw_texts(m, cond)
            n = rec = cs = cl = 0
            for d in bench.decisions(m, cond, 1):
                if np.isnan(d["p"]).any() or not scored(d):
                    continue
                p = np.asarray(d["p"], float)
                q = lenient(raw.get((d["key"], d["qid"]), ""), d["options"])
                n += 1
                rec += int(np.allclose(p, p[0]) and not np.allclose(q, q[0]))
                cs += int(np.argmax(p) == d["y"])
                cl += int(np.argmax(q) == d["y"])
            out[f"{m}|{cond}"] = {"n": n, "recovered": rec, "acc_strict": cs / n,
                                  "acc_lenient": cl / n}
            print("reparse", m, cond, out[f"{m}|{cond}"], flush=True)
    return out


def rounding():
    out = {}
    for m in ROUND_MODELS:
        for cond in ["d1_neutral", "d2_k150"]:
            if not bench.available_reps(m, cond):
                continue
            rows = [d for d in bench.decisions(m, cond, 1)
                    if not np.isnan(d["p"]).any() and scored(d)]
            if not rows:
                continue
            P = [np.asarray(d["p"], float) for d in rows]
            y = np.array([d["y"] for d in rows])
            conf = np.array([p.max() for p in P])
            corr = np.array([float(np.argmax(p) == t) for p, t in zip(P, y)])
            R = [np.round(p, 2) for p in P]
            R = [r / r.sum() if r.sum() > 0 else np.full(len(r), 1.0 / len(r)) for r in R]
            conf_r = np.array([r.max() for r in R])
            corr_r = np.array([float(np.argmax(r) == t) for r, t in zip(R, y)])
            cov, _ = M.coverage_at_risk(conf, corr, RISK)
            cov_r, _ = M.coverage_at_risk(conf_r, corr_r, RISK)
            out[f"{m}|{cond}"] = {"n": len(rows), "cov": float(cov), "cov_rounded": float(cov_r)}
            print("round", m, cond, out[f"{m}|{cond}"], flush=True)
    return out


def main():
    C.dump({"reparse": reparse(), "rounding": rounding(), "risk": RISK}, "parse_rounding.json")


if __name__ == "__main__":
    main()
