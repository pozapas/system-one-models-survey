"""F-reliability: small-multiples reliability diagrams on D1, shipped vs scaled.

One cell per model, both curves computed on d1_neutral: the shipped top-label
probability and the same decisions after the per-primitive-type temperature
scaling already fitted by a01_e1_main.py (the "temperature" field it wrote into
e1_main.json), applied here with metrics.apply_T so the scaled curve matches the
paper's reported ece_scaled exactly. Ten equal-mass bins (metrics.reliability).
Each bin also carries a cluster bootstrap band (resample decisions by item_id,
200 reps, 2.5 to 97.5 percentiles) computed at the bin assignment fixed by the
full-sample rank split, not by resampled confidence value.

Presentation: full text width, a 3 x 3 grid of equal panels with shared axes, one
per model in the fixed model order and color; shipped is the solid line with
the model's marker filled, scaled the dashed line with the same marker hollow.

Output: figures/f08_reliability.pdf and .png
"""
import json
import math
import os

import numpy as np

import bench
import common as C
import metrics as M
import style

BINS = 10
REPS = 200
MODEL_ORDER = list(style.MODEL_COLORS)


def load_e1():
    p = os.path.join(C.RESULTS, "e1_main.json")
    return json.load(open(p, encoding="utf-8"))


def rows_d1(model):
    return [r for r in bench.decisions(model, "d1_neutral")
            if r["y"] >= 0 and not np.isnan(r["p"]).any()]


def scaled_probs(model, rows, T_used):
    if "crossfit_folds" in T_used:
        P = [r["p"] for r in rows]
        y = np.array([r["y"] for r in rows])
        groups = np.array([r["item_id"] for r in rows])
        Ps, _Ts = M.crossfit_T(P, y, groups)
        return Ps
    return [M.apply_T(r["p"], T_used.get(r["type"], 1.0)) for r in rows]


def bin_assign(conf, bins=BINS):
    n = len(conf)
    order = np.argsort(conf, kind="mergesort")
    edges = np.linspace(0, n, bins + 1).round().astype(int)
    bin_id = np.full(n, -1, dtype=int)
    for b, (a, bb) in enumerate(zip(edges[:-1], edges[1:])):
        bin_id[order[a:bb]] = b
    return bin_id


def band(conf, correct, groups, bins=BINS, reps=REPS, seed=C.SEED):
    point = M.reliability(conf, correct, bins)
    bin_id = bin_assign(conf, bins)
    rng = np.random.default_rng(seed)
    ug, inv = np.unique(groups, return_inverse=True)
    members = [np.where(inv == g)[0] for g in range(len(ug))]
    acc_by_bin = [[] for _ in range(bins)]
    for _ in range(reps):
        pick = rng.integers(0, len(ug), len(ug))
        idx = np.concatenate([members[g] for g in pick])
        bidx, cidx = bin_id[idx], correct[idx]
        for b in range(bins):
            m = bidx == b
            if m.sum() > 0:
                acc_by_bin[b].append(cidx[m].mean())
    lo = np.full(bins, np.nan)
    hi = np.full(bins, np.nan)
    for b in range(bins):
        if acc_by_bin[b]:
            lo[b], hi[b] = np.percentile(acc_by_bin[b], [2.5, 97.5])
    return point, lo, hi


def main():
    style.apply()
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    from matplotlib.patches import Patch

    e1 = load_e1()
    models = [m for m in MODEL_ORDER if f"{m}|d1_neutral" in e1
              and bench.available_reps(m, "d1_neutral")]
    if not models:
        print("f08_reliability: no model has d1_neutral results yet")

    n = max(len(models), 1)
    ncols = 3
    nrows = math.ceil(n / ncols)
    cell_h = 1.38
    top, bottom, hspace = 0.56, 0.44, 0.40
    H = top + bottom + nrows * cell_h + (nrows - 1) * hspace
    fig, axs = style.grid(style.FULL, H, nrows, ncols, left=0.50, right=0.06, top=top,
                          bottom=bottom, wspace=0.16, hspace=hspace, sharex=True, sharey=True)
    flat_axes = [a for row in axs for a in row]
    for ax in flat_axes[len(models):]:
        ax.set_visible(False)

    ticks = np.arange(0, 1.01, 0.2)
    ticklabels = ["0", "0.2", "0.4", "0.6", "0.8", "1"]
    for i, (ax, model) in enumerate(zip(flat_axes, models)):
        rows = rows_d1(model)
        conf = np.array([r["p"].max() for r in rows])
        correct = np.array([float(np.argmax(r["p"]) == r["y"]) for r in rows])
        groups = np.array([r["item_id"] for r in rows])
        T_used = e1[f"{model}|d1_neutral"]["temperature"]
        Ps = scaled_probs(model, rows, T_used)
        conf_s = np.array([p.max() for p in Ps])
        correct_s = np.array([float(np.argmax(p) == r["y"]) for p, r in zip(Ps, rows)])

        pt_ship, lo_ship, hi_ship = band(conf, correct, groups)
        pt_scal, lo_scal, hi_scal = band(conf_s, correct_s, groups)

        color = style.MODEL_COLORS[model]
        ax.plot([0, 1], [0, 1], color=style.INK_3, linewidth=0.7, linestyle=(0, (1, 1.6)),
                zorder=1)

        xs = np.array([b["conf"] for b in pt_ship])
        ys = np.array([b["acc"] for b in pt_ship])
        ax.fill_between(xs, lo_ship, hi_ship, color=color, alpha=0.18, linewidth=0, zorder=2)
        ax.plot(xs, ys, color=color, linewidth=1.2, zorder=5)
        ax.plot(xs, ys, **{**style.point_kw(model, base=3.6, fill="full"), "zorder": 6})

        xs2 = np.array([b["conf"] for b in pt_scal])
        ys2 = np.array([b["acc"] for b in pt_scal])
        ax.fill_between(xs2, lo_scal, hi_scal, color=color, alpha=0.08, linewidth=0, zorder=2)
        ax.plot(xs2, ys2, color=color, linewidth=1.0, linestyle=(0, (3, 1.6)), zorder=4)
        ax.plot(xs2, ys2, **{**style.point_kw(model, base=3.6, fill="none"), "zorder": 5})

        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.set_xticks(ticks)
        ax.set_yticks(ticks)
        ax.set_xticklabels(ticklabels)
        ax.set_yticklabels(ticklabels)
        style.guides(ax, "y")
        style.title(ax, "abcdefghijkl"[i], style.label(model))
        r, c = divmod(i, ncols)
        last_in_col = i + ncols >= len(models)
        ax.tick_params(labelleft=(c == 0), labelbottom=last_in_col)
        if c == 0:
            ax.set_ylabel("Observed accuracy")
        if last_in_col:
            ax.set_xlabel("Mean predicted confidence")

    ink = style.INK_2
    handles = [
        Line2D([], [], color=ink, linewidth=1.2, marker="o", markersize=3.2,
               markerfacecolor=ink, markeredgecolor="white", markeredgewidth=0.5,
               label="Shipped probabilities"),
        Line2D([], [], color=ink, linewidth=1.0, linestyle=(0, (3, 1.6)), marker="o",
               markersize=3.4, markerfacecolor="white", markeredgecolor=ink,
               markeredgewidth=0.7, label="Temperature scaled"),
        Patch(facecolor=ink, alpha=0.2, linewidth=0, label="Cluster bootstrap 95% band"),
        Line2D([], [], color=style.INK_3, linewidth=0.7, linestyle=(0, (1, 1.6)),
               label="Perfect calibration"),
    ]
    if models:
        style.legend_top(fig, flat_axes[0], flat_axes[ncols - 1], handles, ncol=4, gap=0.27)
    style.save(fig, "f08_reliability")


if __name__ == "__main__":
    main()
