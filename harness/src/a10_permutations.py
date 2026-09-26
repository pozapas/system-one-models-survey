"""E3 robustness: three distractor sequences for the cardinality sweep, and this-that's option
rendering (revision, reviewer points 1 and 2).

Permutations. p1 is the original sweep (d2_k5, d2_k20, d2_k50, d2_k150); p2 and p3 are the
conditions d2_k{K}_p2 and d2_k{K}_p3 written by s00c_freeze_permutations.py, the same 600
in-scope items under two further independent permutations with the same nested-prefix rule.
For every model and K the script reports accuracy and top-label ECE (equal-mass, 10 bins,
metrics.ece, the estimator of a03_e3_cardinality.py) on the 600 in-scope items at rep 1 for
each permutation, their mean and range (max minus min over the three permutations, null until all three are present), the
number of answered items, refusals, and the share of items on which the chosen intent is the
same under all three permutations (order sensitivity at fixed K). p1 values equal the ones in
e3_cardinality.json by construction.

Rendering sensitivity. this-that-1.0 has no wire-format entry point, so its adapter renders a
choice option as "key: description" (and a score level as "i: description"). The tag
this-that-1.0-desc runs the same model with the description alone (adapters.thisthat_render,
render="desc") on d1_neutral and d2_k150. For each condition, and in d1_neutral for each
question type, the script reports accuracy and ECE under both renderings, the paired share of
decisions whose top option changes (flip rate), the mean absolute change in top probability,
and, as the floor for those flips, this-that's own test-retest flip rate on the d1_neutral
subset. noul questions are rendered ["no", "yes"] in both runs, so their flips measure only
the model's run-to-run noise.

Missing answers are reported, never guessed: a model or rendering whose files are not there
yet appears with null values and is listed under "_missing".

Output: results/e3_permutations.json
Usage:  python a10_permutations.py
"""
import json
import os

import numpy as np

import bench
import common as C
import metrics as M

KS = [5, 20, 50, 150]
PERMS = {"p1": "", "p2": "_p2", "p3": "_p3"}
MODELS = [bench.JEV] + bench.MODELS_OPEN + ["comparator-open"]
TT, TT_ALT = "this-that-1.0", "this-that-1.0-desc"

DOC = (
    "Per model, per K (option count): acc_p1, acc_p2, acc_p3 are top-1 accuracies on the 600 "
    "in-scope CLINC-150 items at rep 1 under the original permutation (p1, d2_k{K}) and two "
    "further independent permutations (p2, p3: d2_k{K}_p2, d2_k{K}_p3, seeds in manifest.json "
    "_d2_permutations); ece_p* is top-label ECE with 10 equal-mass bins; acc_mean, acc_range, "
    "ece_mean, ece_range are the mean and max-minus-min over p1, p2 and p3 (null until all three exist); n_p* is "
    "the number of answered in-scope items; refused_p* counts error lines (for example Laya's "
    "English head at K=150); same_choice_all3 is the share of items answered under all three "
    "permutations on which the chosen intent is identical. null means the answers are not there "
    "yet. render_sensitivity compares this-that-1.0 (options rendered 'key: description') with "
    "this-that-1.0-desc (description only) on d1_neutral (overall and by question type) and "
    "d2_k150 (in-scope items): accuracy, ECE, paired flip rate of the top option, mean absolute "
    "change of the top probability, and this-that's own d1_neutral test-retest flip rate as the "
    "noise floor.")


def load(model, cond, rep=1):
    """{item_id: row} of answered, gold-labelled decisions, and the count of error lines."""
    path = os.path.join(C.ANSWERS, model, f"{cond}__rep{rep}.jsonl")
    if not os.path.exists(path):
        return None, None
    errs = 0
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            try:
                errs += bool(json.loads(line).get("error"))
            except json.JSONDecodeError:
                pass
    rows = {r["item_id"]: r for r in bench.decisions(model, cond, rep)
            if r["y"] >= 0 and not np.isnan(r["p"]).any()}
    return rows, errs


def acc_ece(rows):
    if not rows:
        return None, None
    conf = np.array([r["p"].max() for r in rows])
    cor = np.array([float(np.argmax(r["p"]) == r["y"]) for r in rows])
    return float(cor.mean()), float(M.ece(conf, cor))


def spread(vals):
    """(mean, max - min) over the three permutations; null until all three are present, so a
    model with p1 only never shows a spread of zero it was not measured to have."""
    if any(x is None for x in vals):
        return None, None
    return float(np.mean(vals)), float(max(vals) - min(vals))


def permutations(res, missing):
    native = {}
    for p, suf in PERMS.items():
        for k in KS:
            cond = f"d2_k{k}{suf}"
            native[cond] = {r["item_id"]: r["gold"]["intent"]["native_options"]
                            for r in bench.inputs(cond)}
    for m in MODELS:
        mres = {}
        for k in KS:
            d = {}
            picks = {}
            for p, suf in PERMS.items():
                cond = f"d2_k{k}{suf}"
                rows, errs = load(m, cond)
                if rows is None:
                    missing.append(f"{m}/{cond}__rep1.jsonl")
                    d.update({f"acc_{p}": None, f"ece_{p}": None, f"n_{p}": 0,
                              f"refused_{p}": None})
                    continue
                a, e = acc_ece(list(rows.values()))
                d.update({f"acc_{p}": a, f"ece_{p}": e, f"n_{p}": len(rows),
                          f"refused_{p}": errs})
                picks[p] = {iid: native[cond][iid][int(np.argmax(r["p"]))]
                            for iid, r in rows.items()}
            d["acc_mean"], d["acc_range"] = spread([d[f"acc_{p}"] for p in PERMS])
            d["ece_mean"], d["ece_range"] = spread([d[f"ece_{p}"] for p in PERMS])
            d["permutations_present"] = [p for p in PERMS if d[f"acc_{p}"] is not None]
            if len(picks) == 3:
                common = set(picks["p1"]) & set(picks["p2"]) & set(picks["p3"])
                d["same_choice_all3"] = (float(np.mean([picks["p1"][i] == picks["p2"][i] ==
                                                        picks["p3"][i] for i in common]))
                                         if common else None)
                d["n_all3"] = len(common)
            else:
                d["same_choice_all3"], d["n_all3"] = None, 0
            mres[str(k)] = d
        if any(v["permutations_present"] for v in mres.values()):
            accs = {k: (v["acc_p1"], v["acc_p2"], v["acc_p3"]) for k, v in mres.items()}
            print(m, {k: tuple(None if x is None else round(x, 4) for x in a)
                      for k, a in accs.items()}, flush=True)
        res[m] = mres


def paired(a_rows, b_rows):
    keys = sorted(set(a_rows) & set(b_rows))
    if not keys:
        return None
    flip = np.mean([np.argmax(a_rows[k]["p"]) != np.argmax(b_rows[k]["p"]) for k in keys])
    dtop = np.mean([abs(a_rows[k]["p"].max() - b_rows[k]["p"].max()) for k in keys])
    return {"n_paired": len(keys), "flip_rate": float(flip), "mean_abs_dtop": float(dtop)}


def by_decision(model, cond, rep=1, qtype=None):
    path = os.path.join(C.ANSWERS, model, f"{cond}__rep{rep}.jsonl")
    if not os.path.exists(path):
        return None
    return {(r["item_id"], r["qid"]): r for r in bench.decisions(model, cond, rep)
            if not np.isnan(r["p"]).any() and (qtype is None or r["type"] == qtype)}


def render_sensitivity(missing):
    out = {"original": f"{TT} (choice option 'key: description', score level "
                       f"'i: description', noul ['no', 'yes'])",
           "alternative": f"{TT_ALT} (description only; noul unchanged)"}
    man = json.load(open(os.path.join(C.INPUTS, "manifest.json"), encoding="utf-8"))
    subset = set(man["_retest_subset"]["item_ids"])
    a1, a2 = by_decision(TT, "d1_neutral", 1), by_decision(TT, "d1_neutral", 2)
    if a1 and a2:
        a1s = {k: v for k, v in a1.items() if k[0] in subset}
        out["retest_floor_d1_neutral"] = paired(a1s, a2)
    for cond in ("d1_neutral", "d2_k150"):
        qtypes = [None, "choice", "score", "noul"] if cond == "d1_neutral" else [None]
        cres = {}
        for qt in qtypes:
            o = by_decision(TT, cond, 1, qt)
            n = by_decision(TT_ALT, cond, 1, qt)
            if n is None:
                if qt is None:
                    missing.append(f"{TT_ALT}/{cond}__rep1.jsonl")
            if o is None:
                if qt is None:
                    missing.append(f"{TT}/{cond}__rep1.jsonl")
            og = {k: v for k, v in (o or {}).items() if v["y"] >= 0}
            ng = {k: v for k, v in (n or {}).items() if v["y"] >= 0}
            acc_o, ece_o = acc_ece(list(og.values()))
            acc_n, ece_n = acc_ece(list(ng.values()))
            entry = {"n_original": len(og), "n_alternative": len(ng),
                     "acc_original": acc_o, "acc_alternative": acc_n,
                     "ece_original": ece_o, "ece_alternative": ece_n,
                     "acc_change": (None if acc_o is None or acc_n is None else acc_n - acc_o),
                     "ece_change": (None if ece_o is None or ece_n is None else ece_n - ece_o)}
            pr = paired(og, ng) if (o and n) else None
            entry.update(pr or {"n_paired": 0, "flip_rate": None, "mean_abs_dtop": None})
            cres["all" if qt is None else qt] = entry
        out[cond] = cres
    return out


def main():
    missing = []
    res = {"_doc": DOC}
    permutations(res, missing)
    res["render_sensitivity"] = render_sensitivity(missing)
    res["_missing"] = sorted(set(missing))
    # p1 must reproduce e3_cardinality.json
    e3p = os.path.join(C.RESULTS, "e3_cardinality.json")
    if os.path.exists(e3p):
        e3 = json.load(open(e3p, encoding="utf-8"))
        bad = []
        for m, v in e3.items():
            for k in map(str, KS):
                if k in v and v[k].get("accuracy") is not None and m in res:
                    if abs(v[k]["accuracy"] - res[m][k]["acc_p1"]) > 1e-12 or \
                            abs(v[k]["ece"] - res[m][k]["ece_p1"]) > 1e-12:
                        bad.append((m, k))
        res["_check_p1_equals_e3_cardinality"] = "ok" if not bad else bad
        print("p1 equals e3_cardinality.json:", "ok" if not bad else bad)
    print(f"{len(res['_missing'])} answer files missing (expected until the Colab answers "
          f"arrive)")
    C.dump(res, "e3_permutations.json")


if __name__ == "__main__":
    main()
