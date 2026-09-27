"""Paired comparisons of the second generative comparator with the hosted model.

Qwen3.6-27B read out as stated probabilities (comparator-open2) and as option
likelihoods (comparator-open2-ll) against Jev on each benchmark, with the paired
cluster bootstrap of a14 and a Holm correction over the two readouts per benchmark.
Output: results/comparator_paired.json
"""
import bench
import common as C
from a14_baseline_paired import CONDS, cmap, holm, paired

MODELS = ["comparator-open2", "comparator-open2-ll"]


def main():
    out = {}
    for cond in CONDS:
        J = cmap(bench.JEV, cond)
        res = {}
        for m in MODELS:
            if bench.available_reps(m, cond):
                r = paired(cmap(m, cond), J, C.SEED)
                if r:
                    res[m] = r
        for (m, v), a in zip(res.items(), holm([v["p"] for v in res.values()])):
            v["holm"] = a
        out[cond] = res
        print(cond, {m: (round(v["diff"], 1), round(v["lo"], 1), round(v["hi"], 1),
                         round(v["holm"], 3)) for m, v in res.items()})
    C.dump(out, "comparator_paired.json")


if __name__ == "__main__":
    main()
