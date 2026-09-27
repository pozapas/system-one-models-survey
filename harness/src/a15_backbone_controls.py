"""Untuned backbone controls: each open decision model against the base checkpoint it adapts.

The backbones (adapters.BackboneOptScoreBackend) read the same request content as the
decision models, as a plain text prompt ending in an answer cue, and their option
distribution is the softmax of each option key's sequence log-likelihood (with a boundary term
for keys that are token prefixes of longer keys), at temperature one. The pairs follow the
decision models' own cards (bench.BACKBONE_OF):

    kev-9b        vs backbone-qwen35-9b-base    Qwen/Qwen3.5-9B-Base
    nimble-9b     vs backbone-qwen35-9b         Qwen/Qwen3.5-9B (post-trained)
    decider-2b    vs backbone-qwen35-2b-base    Qwen/Qwen3.5-2B-Base
    this-that-1.0 vs backbone-qwen35-2b-base    (adapted from decider-2b)
    kev-0.8b      vs backbone-qwen35-0.8b-base  Qwen/Qwen3.5-0.8B-Base

Laya (ModernBERT encoder) has no language-model head over option keys and no control.

Per model and condition, with the definitions of a01, a02 and metrics:
    accuracy        argmax against the gold option over decisions with a gold label and an
                    answer (bench.top), cluster bootstrap interval over item_id (a01)
    ece_shipped     top-label ECE, 10 equal-mass bins (metrics.ece) on the shipped
                    probabilities
    auroc_oos       d2_k150: AUROC of the top probability for in-scope against out-of-scope
                    utterances over every answered utterance (a01.d2_oos)
    flips           option-name sets: flips per hundred against the aligned no/yes naming
                    (a02.pos_prob and a02.flips), with AUC and accuracy per naming

Paired differences, decision model minus its backbone, on the decisions both answered, as
cluster bootstraps over item_id (states on D1): accuracy and flip rates with B = 10000
vectorized replicates (as a14 and a09 E), ECE and AUROC with B = 1000 sort-based replicates
(as a09 B); percentile 95 percent intervals; two-sided bootstrap p = min(1, 2 min(1 + #{d* <=
0}, 1 + #{d* >= 0}) / (B + 1)) (a09.boot_p_two); Holm over the five pairs within each
condition and metric. Differences in accuracy, ECE and flips are in points (x 100).

Output: results/backbone_controls.json (only written when at least one backbone has answers)
"""
import json
import os

import common as C  # noqa: I100  (thread limits before numpy)

import numpy as np

import a02_e2_names as A2
import bench
import metrics as M

OUT = "backbone_controls.json"
MAIN = ["d1_neutral", "d2_k150", "d3_conv_go_awry", "d3_wiki_corpus", "d3_emotion",
        "d3_wiki_politeness"]
PAIRS = [(d, b) for d, b in bench.BACKBONE_OF.items()]
B_PAIRED = 10000
B_SORT = 1000
if os.environ.get("A15_QUICK"):          # smoke test only
    B_PAIRED, B_SORT, OUT = 500, 100, "backbone_controls.quick.json"


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


def pct(vals):
    vals = np.asarray([v for v in vals if v is not None and not np.isnan(v)], float)
    if len(vals) == 0:
        return None
    lo, hi = np.percentile(vals, [2.5, 97.5])
    return [float(lo), float(hi)]


class Clusters:
    """Resampling of item_id clusters with duplicates kept (a09.Clusters)."""

    def __init__(self, groups):
        groups = np.asarray(groups)
        self.ug, inv = np.unique(groups, return_inverse=True)
        self.order = np.argsort(inv, kind="mergesort")
        self.len = np.bincount(inv, minlength=len(self.ug))
        self.start = np.r_[0, np.cumsum(self.len)[:-1]]
        self.inv = inv
        self.G = len(self.ug)

    def draw(self, rng):
        pick = rng.integers(0, self.G, self.G)
        lens = self.len[pick]
        offs = np.repeat(self.start[pick] - np.r_[0, np.cumsum(lens)[:-1]], lens)
        return self.order[np.arange(int(lens.sum())) + offs]


# ------------------------------------------------------------------ per model

def scored(model, cond):
    """{key|qid: (conf, correct, item_id)} over decisions with a gold label and an answer."""
    rs, conf, correct, _K = bench.top(bench.decisions(model, cond))
    return {r["key"] + "|" + r["qid"]: (float(c), float(k), r["item_id"])
            for r, c, k in zip(rs, conf, correct)}


def oos(model):
    """{key|qid: (top probability, in scope, item_id)} on d2_k150 (a01.d2_oos)."""
    return {r["key"] + "|" + r["qid"]: (float(r["p"].max()), bool(r["meta"]["in_scope"]),
                                        r["item_id"])
            for r in bench.decisions(model, "d2_k150") if not np.isnan(r["p"]).any()}


def summarize(model):
    out = {}
    for cond in MAIN:
        if not bench.available_reps(model, cond):
            continue
        S = scored(model, cond)
        if not S:
            continue
        conf = np.array([v[0] for v in S.values()])
        cor = np.array([v[1] for v in S.values()])
        groups = np.array([v[2] for v in S.values()])
        n_dec = len(bench.decisions(model, cond))
        out[cond] = {"n_decisions": n_dec, "n_scored": len(S), "accuracy": float(cor.mean()),
                     "accuracy_ci": M.cluster_boot(lambda i: cor[i].mean(), groups),
                     "ece_shipped": M.ece(conf, cor), "mean_confidence": float(conf.mean())}
    if bench.available_reps(model, "d2_k150"):
        O = oos(model)
        if O:
            s = np.array([v[0] for v in O.values()])
            ins = np.array([v[1] for v in O.values()])
            out["d2_oos"] = {"auroc_in_vs_oos": M.auroc(s, ins), "n_in": int(ins.sum()),
                             "n_oos": int((~ins).sum()),
                             "mean_conf_in": float(s[ins].mean()),
                             "mean_conf_oos": float(s[~ins].mean())}
    names = {}
    for ds, pats in A2.SETS.items():
        conds = {n: pats[0].format(n) for n in A2.NAMINGS}
        if not all(bench.available_reps(model, c) for c in conds.values()):
            continue
        pp = {n: A2.pos_prob(model, c) for n, c in conds.items()}
        keys = sorted(set.intersection(*[set(v) for v in pp.values()]))
        d = {"n": len(keys)}
        for n in A2.NAMINGS:
            f, _ = A2.flips(pp["kny"], pp[n])
            d[n] = {"auc": A2.auc_of(pp[n], keys), "flips_per_100_vs_kny": f,
                    "accuracy": float(np.mean([(pp[n][k][0] >= 0.5) == pp[n][k][1]
                                               for k in keys])),
                    "mean_p_pos": float(np.mean([pp[n][k][0] for k in keys]))}
        names[ds] = d
    if names:
        out["names"] = names
    return out


def truncation(model):
    """Longest prompt in tokens and length errors per answer file (backbones record
    raw.n_prompt_tokens; nothing is truncated, an over-length prompt is an error line)."""
    d = os.path.join(C.ANSWERS, model)
    out = {}
    for fn in sorted(os.listdir(d)):
        if not fn.endswith(".jsonl"):
            continue
        mx = err = length = ok = 0
        joint_bad = 0
        for line in open(os.path.join(d, fn), encoding="utf-8"):
            try:
                j = json.loads(line)
            except json.JSONDecodeError:
                continue
            if j.get("error"):
                err += 1
                length += "max_len" in j["error"]
                continue
            ok += 1
            for a in j["answers"].values():
                raw = a.get("raw") or {}
                mx = max(mx, raw.get("n_prompt_tokens") or 0)
                joint_bad += raw.get("joint_tokenization_ok") is False
        out[fn[:-6]] = {"answered": ok, "errors": err, "over_length": length,
                        "max_prompt_tokens": mx, "joint_tokenization_mismatch": joint_bad}
    return out


# ------------------------------------------------------------------ paired

def paired_mean(A, B, seed=C.SEED):
    """Mean of A - B over shared keys, clustered by item: {key: (value, item)} each."""
    keys = sorted(set(A) & set(B))
    if len(keys) < 30:
        return None
    d = np.array([A[k][0] - B[k][0] for k in keys])
    ug, inv = np.unique(np.array([A[k][1] for k in keys]), return_inverse=True)
    s = np.bincount(inv, weights=d)
    nn = np.bincount(inv).astype(float)
    rng = np.random.default_rng(seed)
    pick = rng.integers(0, len(ug), (B_PAIRED, len(ug)))
    bd = s[pick].sum(1) / nn[pick].sum(1)
    return {"n": len(keys), "n_clusters": int(len(ug)), "a": float(np.mean([A[k][0] for k in keys])),
            "b": float(np.mean([B[k][0] for k in keys])), "diff": float(d.mean()),
            "ci": pct(bd), "p": boot_p_two(bd), "replicates": B_PAIRED}


def paired_stat(A, B, stat, seed=C.SEED):
    """stat(A rows) - stat(B rows) over shared keys, cluster bootstrap of B_SORT replicates.
    A and B map key -> (x, y, item); stat takes arrays x, y."""
    keys = sorted(set(A) & set(B))
    if len(keys) < 30:
        return None
    xa = np.array([A[k][0] for k in keys]); ya = np.array([A[k][1] for k in keys])
    xb = np.array([B[k][0] for k in keys]); yb = np.array([B[k][1] for k in keys])
    cl = Clusters(np.array([A[k][2] for k in keys]))
    rng = np.random.default_rng(seed)
    vals = []
    for _ in range(B_SORT):
        ii = cl.draw(rng)
        vals.append(stat(xa[ii], ya[ii]) - stat(xb[ii], yb[ii]))
    a, b = stat(xa, ya), stat(xb, yb)
    return {"n": len(keys), "n_clusters": int(cl.G), "a": float(a), "b": float(b),
            "diff": float(a - b), "ci": pct(vals), "p": boot_p_two(vals), "replicates": B_SORT}


def flip_map(model, ds, naming):
    """{(item, qid) as key: (flip indicator vs kny, item)} (a02 definition)."""
    pats = A2.SETS[ds]
    ref = A2.pos_prob(model, pats[0].format("kny"))
    alt = A2.pos_prob(model, pats[0].format(naming))
    return {f"{k[0]}|{k[1]}": (float((ref[k][0] >= 0.5) != (alt[k][0] >= 0.5)), k[0])
            for k in sorted(set(ref) & set(alt))}


def scale(r, f=100.0):
    if r is None:
        return None
    r = dict(r)
    for k in ("a", "b", "diff"):
        r[k] = f * r[k]
    r["ci"] = [f * v for v in r["ci"]] if r["ci"] else None
    return r


def main():
    have = bench.present(bench.BACKBONES)
    if not have:
        print("no backbone answers under answers/ yet; nothing written")
        return
    res = {"definitions": {
        "pairs": dict(bench.BACKBONE_OF),
        "backbone_scoring": ("adapters.BackboneOptScoreBackend: plain prompt (state, question, "
                             "'- key: description' options, instruction, 'Answer:'), option "
                             "probability = softmax over keys of the summed key-token "
                             "log-probabilities plus a boundary term for keys that are token "
                             "prefixes of longer keys, temperature 1, no length normalization"),
        "accuracy": "a01: argmax against gold over answered decisions with a gold label",
        "ece_shipped": "metrics.ece, top label, 10 equal-mass bins",
        "auroc_oos": "a01.d2_oos: top probability, in scope against out of scope, d2_k150",
        "flips": "a02: flips per hundred against the aligned no/yes naming, positive rubric >= 0.5",
        "paired": ("decision model minus backbone on shared decisions, cluster bootstrap over "
                   "item_id; accuracy and flips vectorized with B_PAIRED replicates, ECE and "
                   "AUROC with B_SORT; percentile 95 percent; two-sided bootstrap p; Holm over "
                   "the five pairs within each condition and metric; accuracy, ECE and flip "
                   "differences in points"),
        "replicates": {"paired": B_PAIRED, "sort_based": B_SORT}},
        "models": {}, "paired": {}, "truncation": {}}
    for m in sorted(set(bench.BACKBONE_OF) | set(have)):
        s = summarize(m)
        if s:
            res["models"][m] = s
            print(m, {c: round(v["accuracy"], 3) for c, v in s.items()
                      if isinstance(v, dict) and "accuracy" in v}, flush=True)
    for b in have:
        res["truncation"][b] = truncation(b)

    fams = {}
    for dm, bb in PAIRS:
        if bb not in have:
            continue
        pk = f"{dm}>{bb}"
        for cond in MAIN:
            if not (bench.available_reps(dm, cond) and bench.available_reps(bb, cond)):
                continue
            SA, SB = scored(dm, cond), scored(bb, cond)
            acc = scale(paired_mean({k: (v[1], v[2]) for k, v in SA.items()},
                                    {k: (v[1], v[2]) for k, v in SB.items()}))
            ece = scale(paired_stat(SA, SB, lambda x, y: M.ece(x, y)))
            for metric, r in (("accuracy", acc), ("ece_shipped", ece)):
                if r is not None:
                    res["paired"][f"{pk}|{cond}|{metric}"] = r
                    fams.setdefault((cond, metric), []).append(f"{pk}|{cond}|{metric}")
        if bench.available_reps(dm, "d2_k150") and bench.available_reps(bb, "d2_k150"):
            OA, OB = oos(dm), oos(bb)
            r = paired_stat({k: (v[0], v[1], v[2]) for k, v in OA.items()},
                            {k: (v[0], v[1], v[2]) for k, v in OB.items()},
                            lambda x, y: M.auroc(x, y))
            if r is not None:
                res["paired"][f"{pk}|d2_oos|auroc"] = r
                fams.setdefault(("d2_oos", "auroc"), []).append(f"{pk}|d2_oos|auroc")
        for ds, pats in A2.SETS.items():
            conds = [pats[0].format(n) for n in A2.NAMINGS]
            if not all(bench.available_reps(x, c) for x in (dm, bb) for c in conds):
                continue
            for n in ("k01", "kswap", "krand"):
                r = scale(paired_mean(flip_map(dm, ds, n), flip_map(bb, ds, n)))
                if r is not None:
                    key = f"{pk}|names_{ds}_{n}|flips"
                    res["paired"][key] = r
                    fams.setdefault((f"names_{ds}_{n}", "flips"), []).append(key)
    for (cond, metric), keys in fams.items():
        for k, a in zip(keys, holm([res["paired"][k]["p"] for k in keys])):
            res["paired"][k]["holm"] = float(a)
            res["paired"][k]["holm_family"] = f"{cond}|{metric} over {len(keys)} pairs"
    for k, v in res["paired"].items():
        print(f"{k:70s} diff={v['diff']:+.3f} ci={[round(x, 3) for x in v['ci']] if v['ci'] else None} "
              f"holm={v['holm']:.3g}", flush=True)
    C.dump(res, OUT)
    print("wrote results/" + OUT)


if __name__ == "__main__":
    main()
