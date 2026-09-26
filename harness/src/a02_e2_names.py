"""E2: option-name polarity swap with every rubric held fixed.

Each binary question (the noul questions of D1 and the two binary D3 tasks) is asked
as a two-option Choice under four naming conditions: keys 0/1, no/yes aligned with
the rubric, yes/no swapped against the rubric, and random five-letter strings. The
rubric text and its order are identical across conditions, so any change in the
answer is caused by the names alone.

For each model this reports, per dataset and condition,
    flips per hundred    decisions whose chosen rubric differs from the aligned
                         no/yes condition
    AUC                  of the probability on the positive rubric against the gold
    delta AUC            against the aligned condition, with a paired bootstrap
                         interval over items
    name effect          mean change in the positive-rubric probability against
                         the aligned condition
and the test-retest floor, which is the flip rate between two repeats of one
condition (Jev) or of d1_neutral (open models, expected zero if deterministic).

Output: results/e2_names.json
"""
import numpy as np

import bench
import common as C
import metrics as M

NAMINGS = ["k01", "kny", "kswap", "krand"]
SETS = {"d1": ["e2_d1_{}"],
        "d3_conv_go_awry": ["e2_d3_conv_go_awry_{}"],
        "d3_wiki_corpus": ["e2_d3_wiki_corpus_{}"]}
MODELS = [bench.JEV] + bench.MODELS_OPEN


def pos_prob(model, cond, rep=1):
    """{(item_id, qid): (p_pos, gold_is_pos)} for one naming condition."""
    out = {}
    for r in bench.decisions(model, cond, rep):
        if np.isnan(r["p"]).any():
            continue
        k = r["options"].index(r["positive"])
        out[(r["item_id"], r["qid"])] = (float(r["p"][k]), r["y"] == k)
    return out


def flips(a, b):
    keys = sorted(set(a) & set(b))
    if not keys:
        return np.nan, 0
    f = [(a[k][0] >= 0.5) != (b[k][0] >= 0.5) for k in keys]
    return 100.0 * float(np.mean(f)), len(keys)


def auc_of(d, keys):
    return M.auroc([d[k][0] for k in keys], [d[k][1] for k in keys])


def delta_auc_ci(a, b, reps=1000):
    keys = sorted(set(a) & set(b))
    items = np.array([k[0] for k in keys])
    ua = np.unique(items)
    idx_of = {u: np.where(items == u)[0] for u in ua}
    rng = np.random.default_rng(C.SEED)
    sa = np.array([a[k][0] for k in keys])
    sb = np.array([b[k][0] for k in keys])
    y = np.array([a[k][1] for k in keys])
    vals = []
    for _ in range(reps):
        pick = rng.choice(ua, len(ua))
        i = np.concatenate([idx_of[u] for u in pick])
        if y[i].all() or (~y[i]).all():
            continue
        vals.append(M.auroc(sb[i], y[i]) - M.auroc(sa[i], y[i]))
    return [float(v) for v in np.percentile(vals, [2.5, 97.5])]


def retest_floor(model):
    """Flip rate per hundred between repeat 1 and repeat 2 of the same condition."""
    out = {}
    for ds, pats in SETS.items():
        cond = pats[0].format("kny")
        if len(bench.available_reps(model, cond)) >= 2:
            f, n = flips(pos_prob(model, cond, 1), pos_prob(model, cond, 2))
            out[ds] = {"flips_per_100": f, "n": n, "source": f"{cond} rep1 vs rep2"}
    if not out and len(bench.available_reps(model, "d1_neutral")) >= 2:
        a = {(r["item_id"], r["qid"]): int(np.argmax(r["p"]))
             for r in bench.decisions(model, "d1_neutral", 1) if not np.isnan(r["p"]).any()}
        b = {(r["item_id"], r["qid"]): int(np.argmax(r["p"]))
             for r in bench.decisions(model, "d1_neutral", 2) if not np.isnan(r["p"]).any()}
        keys = sorted(set(a) & set(b))
        out["d1_neutral"] = {"flips_per_100": 100.0 * float(np.mean([a[k] != b[k] for k in keys])),
                             "n": len(keys), "source": "d1_neutral retest subset rep1 vs rep2"}
    return out


def main():
    res = {}
    for m in MODELS:
        mres = {}
        for ds, pats in SETS.items():
            conds = {n: pats[0].format(n) for n in NAMINGS}
            if not all(bench.available_reps(m, c) for c in conds.values()):
                continue
            pp = {n: pos_prob(m, c) for n, c in conds.items()}
            ref = pp["kny"]
            keys = sorted(set.intersection(*[set(v) for v in pp.values()]))
            d = {"n": len(keys)}
            for n in NAMINGS:
                f, _ = flips(ref, pp[n])
                d[n] = {"auc": auc_of(pp[n], keys),
                        "flips_per_100_vs_kny": f,
                        "mean_p_pos": float(np.mean([pp[n][k][0] for k in keys])),
                        "name_effect_vs_kny": float(np.mean([pp[n][k][0] - ref[k][0]
                                                             for k in keys])),
                        "accuracy": float(np.mean([(pp[n][k][0] >= 0.5) == pp[n][k][1]
                                                   for k in keys]))}
            for n in NAMINGS:
                if n != "kny":
                    d[n]["delta_auc_vs_kny"] = d[n]["auc"] - d["kny"]["auc"]
                    d[n]["delta_auc_ci"] = delta_auc_ci(ref, pp[n])
            mres[ds] = d
            print(f"{m:16s} {ds:18s} n={len(keys)} " + " ".join(
                f"{n}:auc={d[n]['auc']:.3f},flip={d[n]['flips_per_100_vs_kny']:.1f}"
                for n in NAMINGS), flush=True)
        if mres:
            mres["retest_floor"] = retest_floor(m)
            res[m] = mres
    C.dump(res, "e2_names.json")


if __name__ == "__main__":
    main()
