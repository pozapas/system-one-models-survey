"""Paired comparisons of every decision model with the conventional classifiers.

For each benchmark (d1_neutral, in-scope d2_k150, the four D3 tasks) and each decision
model, the accuracy difference against the zero-shot entailment classifier and against
the classifier trained on the task's labels, with a paired cluster-bootstrap interval,
a two-sided bootstrap p-value and a Holm correction over the models of each benchmark
and baseline. Output: results/baseline_paired.json
"""
import numpy as np

import bench
import common as C

REPS = 10000
CONDS = ["d1_neutral", "d2_k150", "d3_conv_go_awry", "d3_wiki_corpus", "d3_emotion",
         "d3_wiki_politeness", "d3_goemotions", "d2_banking77"]
BASE = {"nli": {c: "baseline-nli-deberta-v3-base" for c in CONDS},
        # the stronger trained classifier of the fourth revision (b05), on every benchmark
        "trainedlarge": {"d1_neutral": "baseline-deberta-large-d1",
                         "d2_k150": "baseline-deberta-large-clinc",
                         "d3_conv_go_awry": "baseline-deberta-large-d3",
                         "d3_wiki_corpus": "baseline-deberta-large-d3",
                         "d3_emotion": "baseline-deberta-large-d3",
                         "d3_wiki_politeness": "baseline-deberta-large-d3",
                         "d3_goemotions": "baseline-deberta-large-goemo",
                         "d2_banking77": "baseline-deberta-large-banking"},
        "trained": {"d1_neutral": "baseline-bge-small-lr-d1",
                    "d2_k150": "baseline-bge-small-lr-clinc",
                    "d3_conv_go_awry": "baseline-bge-small-lr-d3",
                    "d3_wiki_corpus": "baseline-bge-small-lr-d3",
                    "d3_emotion": "baseline-bge-small-lr-d3",
                    "d3_wiki_politeness": "baseline-bge-small-lr-d3",
                    "d3_goemotions": "baseline-bge-small-lr-goemo",
                    "d2_banking77": "baseline-bge-small-lr-banking"}}
MODELS = [bench.JEV] + bench.MODELS_OPEN
# second revision comparators, when answered, are paired against the same baselines in a
# Holm family of their own (holm_family "comparators2"), so the Holm-adjusted values of
# MODELS stay exactly as they are
EXTRA = bench.present(bench.COMPARATORS_2)


def cmap(model, cond):
    return {r["key"] + "|" + r["qid"]: (float(np.argmax(r["p"]) == r["y"]), r["item_id"])
            for r in bench.decisions(model, cond)
            if r["y"] >= 0 and not np.isnan(r["p"]).any()}


def paired(A, B, seed):
    keys = sorted(set(A) & set(B))
    if len(keys) < 50:
        return None
    d = np.array([A[k][0] - B[k][0] for k in keys])
    items = np.array([A[k][1] for k in keys])
    ug, inv = np.unique(items, return_inverse=True)
    sums = np.bincount(inv, weights=d); cnt = np.bincount(inv)
    rng = np.random.default_rng(seed)
    pick = rng.integers(0, len(ug), (REPS, len(ug)))
    boots = sums[pick].sum(1) / cnt[pick].sum(1)
    lo, hi = np.percentile(boots, [2.5, 97.5])
    p = min(1.0, 2 * min((boots <= 0).mean(), (boots >= 0).mean()))
    return {"n": len(keys), "diff": float(100 * d.mean()), "lo": float(100 * lo),
            "hi": float(100 * hi), "p": float(max(p, 1 / REPS))}


def holm(ps):
    order = sorted(range(len(ps)), key=lambda i: ps[i])
    adj = [0.0] * len(ps); run = 0.0
    for r, i in enumerate(order):
        run = max(run, min(1.0, (len(ps) - r) * ps[i])); adj[i] = run
    return adj


def main():
    out = {}
    for cond in CONDS:
        for bname, bmap in BASE.items():
            B = cmap(bmap[cond], cond)
            # one Holm family per benchmark and baseline across every model compared with it
            res = {}
            for m in MODELS + EXTRA:
                if not bench.available_reps(m, cond):
                    continue
                r = paired(cmap(m, cond), B, C.SEED)
                if r:
                    res[m] = r
            for (m, v), a in zip(res.items(), holm([v["p"] for v in res.values()])):
                v["holm"] = a
            out[f"{cond}|{bname}"] = res
            sig_pos = [m for m, v in res.items() if v["holm"] < 0.05 and v["diff"] > 0]
            sig_neg = [m for m, v in res.items() if v["holm"] < 0.05 and v["diff"] < 0]
            print(f"{cond:20s} vs {bname:8s} above: {sig_pos} below: {sig_neg}")
    C.dump(out, "baseline_paired.json")


if __name__ == "__main__":
    main()
