"""E3: cardinality sweep on CLINC-150.

The same 600 in-scope utterances are asked with 5, 20, 50 and 150 options. The option
sets are nested prefixes of one fixed permutation per item and always contain the
gold intent, so the number of options is the only thing that changes. The
hierarchical condition asks the domain (10 options) and then the intent within the
gold domain (15 options); a hierarchical answer is correct only when both stages are
correct, which is exact because a wrong domain can never lead to the right intent.

Output: results/e3_cardinality.json
"""
import numpy as np

import bench
import common as C
import metrics as M

KS = [5, 20, 50, 150]
MODELS = [bench.JEV] + bench.MODELS_OPEN + ["comparator-open"]


def by_item(model, cond, rep=1):
    return {r["item_id"]: r for r in bench.decisions(model, cond, rep)
            if r["y"] >= 0 and not np.isnan(r["p"]).any()}


def main():
    res = {}
    for m in MODELS:
        if not any(bench.available_reps(m, f"d2_k{k}") for k in KS):
            continue
        d = {}
        for k in KS:
            if not bench.available_reps(m, f"d2_k{k}"):
                continue
            it = by_item(m, f"d2_k{k}")
            if not it:
                # the model refused every request at this option count (Laya's English head
                # raises when the option text exceeds its token budget); recorded, not scored
                n_ref = sum(1 for _ in open(bench.os.path.join(bench.C.ANSWERS, m,
                                                             f"d2_k{k}__rep1.jsonl"),
                                            encoding="utf-8"))
                d[str(k)] = {"n": 0, "refused": n_ref, "accuracy": None, "ece": None,
                             "mean_confidence": None, "chance": 1.0 / k}
                continue
            conf = np.array([r["p"].max() for r in it.values()])
            cor = np.array([float(np.argmax(r["p"]) == r["y"]) for r in it.values()])
            groups = np.array([r["meta"]["intent"] for r in it.values()])
            d[str(k)] = {"n": len(it), "accuracy": float(cor.mean()),
                         "accuracy_ci": M.cluster_boot(lambda i: cor[i].mean(), groups),
                         "ece": M.ece(conf, cor), "mean_confidence": float(conf.mean()),
                         "chance": 1.0 / k, "aurc": M.aurc(conf, cor),
                         "coverage_at_5pct": M.coverage_at_risk(conf, cor, 0.05)[0]}
        if bench.available_reps(m, "d2_hier_dom") and bench.available_reps(m, "d2_hier_int"):
            dom = by_item(m, "d2_hier_dom")
            itn = by_item(m, "d2_hier_int")
            keys = sorted(set(dom) & set(itn))
            c_dom = np.array([np.argmax(dom[k]["p"]) == dom[k]["y"] for k in keys])
            c_int = np.array([np.argmax(itn[k]["p"]) == itn[k]["y"] for k in keys])
            both = c_dom & c_int
            d["hier"] = {"n": len(keys), "domain_accuracy": float(c_dom.mean()),
                         "intent_given_gold_domain_accuracy": float(c_int.mean()),
                         "accuracy": float(both.mean())}
            if "150" in d and d["150"]["accuracy"] is not None:
                flat = by_item(m, "d2_k150")
                kk = sorted(set(keys) & set(flat))
                cf = np.array([np.argmax(flat[k]["p"]) == flat[k]["y"] for k in kk])
                ch = np.array([both[keys.index(k)] for k in kk])
                d["hier"]["flat150_same_items_accuracy"] = float(cf.mean())
                d["hier"]["mcnemar_vs_flat150"] = M.mcnemar(ch, cf)
        if "5" in d and "150" in d and d["150"]["accuracy"] is not None:
            d["drop_5_to_150"] = d["5"]["accuracy"] - d["150"]["accuracy"]
        res[m] = d
        print(m, {k: (round(v["accuracy"], 3) if v.get("accuracy") is not None else "refused")
                  for k, v in d.items() if isinstance(v, dict)},
              flush=True)
    C.dump(res, "e3_cardinality.json")


if __name__ == "__main__":
    main()
