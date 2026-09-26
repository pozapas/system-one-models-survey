"""F-cascade: held-out cascade accuracy against cost fraction for the informative pairs.

Reads results/e6_cascade.json (schema in a06_e6_cascade.py) for the in-sample threshold
sweep and results/revision_stats.json, section D (a09_revision_stats.py), for the costs
and the held-out cascade. One panel per pair, full text width, 2 x 3. The top row
escalates an open decision model to the hosted model, the bottom row escalates to the
generative comparator. Every cost fraction in every panel uses the itemwise costs of
section D for that pair and task: each decision carries its own first- and second-stage
cost from the answer records (a09.aligned_full), whose means are the k1/k2 of section D
(rv.cas.*.kone/ktwo), so the D2 panels no longer borrow the typed-decisions costs that
e6's own cost fractions use. In every panel:

  * the held-out cascade, revision_stats D pairs[...]["decision_level"] (cost_fraction,
    accuracy), is the emphasized mark (a black ring); its threshold was chosen on data
    the scored items never touch (d1_calib for D1, item-disjoint cross-fitting
    elsewhere), and it is the rv.cas point of the tables;
  * the in-sample threshold sweep is a faint line in the first-stage model's color, for
    context only: e6's thresholds and accuracies, with the cost fraction recomputed
    itemwise at each threshold, (sum k1 + sum of k2 over escalated decisions) / sum k2;
    the accuracy and escalated share at every threshold are checked against e6;
  * the first stage alone is the sweep's zero-escalation point, and the second
    stage alone is drawn at cost fraction 1 (its own cost by definition of the
    cost fraction) and acc_second, each in its model's marker;
  * a dashed line marks the better of the two single stages.

Informative pairs are the ones the results section reads (this-that-model-1.0
and decider-2b to the hosted model on D2, the hosted model to the comparator on D1
and on politeness, Laya (English) to the comparator on D1), plus Kev-9B to the
hosted model on D1, the closest open model on D1, whose sweep shows the full
trade-off. Pairs with no cost fraction (cost unknown) are skipped.

Output: figures/f12_cascade.pdf and .png, and the PDF copied to the figures folders of
the ACL and EAAI manuscripts, which both include this file.
"""
import json
import os
import shutil

import numpy as np
from matplotlib.lines import Line2D
from matplotlib.ticker import FormatStrFormatter, MaxNLocator

import common as C
import style

PAIRS = [("this-that-1.0", "jev-1.13.0", "d2_k150"),
         ("decider-2b", "jev-1.13.0", "d2_k150"),
         ("kev-9b", "jev-1.13.0", "d1_neutral"),
         ("jev-1.13.0", "comparator-open", "d1_neutral"),
         ("jev-1.13.0", "comparator-open", "d3_wiki_politeness"),
         ("laya-en", "comparator-open", "d1_neutral")]
# direct-label offsets (dx pt, dy pt, ha, va) for the first-stage and second-stage points
R, L, B, A = (6, 0, "left", "center"), (-6, 0, "right", "center"),     (0, -7, "center", "top"), (0, 7, "center", "bottom")
LABEL_AT = {0: (R, B), 1: (R, B), 2: (B, A), 3: ((0, -9, "center", "top"), B),
            4: ((-5, -6, "right", "top"), B),
            5: (R, (-6, -6, "right", "top"))}
COND_LABEL = {"d1_neutral": "D1", "d2_k150": "D2", "d3_wiki_politeness": "politeness",
              "d3_conv_go_awry": "derailment", "d3_wiki_corpus": "power",
              "d3_emotion": "emotion"}
SECOND_LABEL = {"jev-1.13.0": "Jev 1.13.0 alone", "comparator-open": "Comparator alone"}


MANUSCRIPT_FIGURES = [os.path.join(os.path.dirname(C.ROOT), "benchmark", "manuscript", "figures"),
                      os.path.join(os.path.dirname(C.ROOT), "benchmark", "eaai", "manuscript",
                                   "figures")]


def load(name):
    p = os.path.join(C.RESULTS, name)
    if not os.path.exists(p):
        return None
    d = json.load(open(p, encoding="utf-8"))
    return d if d else None


def pair_data(e6, rv, first, second, cond):
    """Sweep and single stages with itemwise costs, and the held-out cascade of section D."""
    import a09_revision_stats as A9
    key = f"{first}>{second}|{cond}"
    if key not in e6 or key not in rv:
        return None
    v, r = e6[key], rv[key]
    ho = r["decision_level"]
    if ho.get("cost_fraction") is None:
        return None
    D = A9.aligned_full(first, second, cond)
    conf, c1, c2, k1, k2 = D["conf"], D["c1"], D["c2"], D["k1"], D["k2"]
    # the costs are those of section D (rv.cas.*.kone / ktwo are their means per thousand)
    assert np.isclose(k1.mean() * 1000, r["k1_usd_per_1000"], rtol=0, atol=1e-12), key
    assert np.isclose(k2.mean() * 1000, r["k2_usd_per_1000"], rtol=0, atol=1e-12), key
    assert len(conf) == v["n"] == r["n"], key
    pts = []
    for p in v["curve"]:
        esc = conf < p["tau"]
        acc = np.where(esc, c2, c1).mean()
        # e6 and section D score the same aligned decisions at the same thresholds
        assert abs(acc - p["accuracy"]) < 1e-12 and abs(esc.mean() - p["escalated"]) < 1e-12, key
        pts.append({"escalated": float(esc.mean()), "accuracy": float(acc),
                    "cost_fraction": float((k1.sum() + k2[esc].sum()) / k2.sum())})
    pts = sorted(pts, key=lambda p: (p["escalated"], p["cost_fraction"]))
    assert abs(ho["acc_first"] - v["acc_first"]) < 1e-12, key
    assert abs(ho["acc_second"] - v["acc_second"]) < 1e-12, key
    return {"x": np.array([p["cost_fraction"] for p in pts]),
            "y": np.array([p["accuracy"] for p in pts]),
            "first": pts[0], "acc1": v["acc_first"], "acc2": v["acc_second"], "ho": ho}


def main():
    e6 = load("e6_cascade.json")
    rv = load("revision_stats.json")
    if e6 is None or rv is None or "D_cascades" not in rv:
        print("f12_cascade: results/e6_cascade.json or revision_stats.json (section D) is"
              " missing, skipping this figure")
        return
    rv = rv["D_cascades"]["pairs"]
    style.apply()

    panels = [(f, s, c, pair_data(e6, rv, f, s, c)) for f, s, c in PAIRS]
    panels = [p for p in panels if p[3] is not None]
    if not panels:
        print("f12_cascade: none of the informative pairs is in e6_cascade.json, skipping")
        return

    ncols = 3
    nrows = int(np.ceil(len(panels) / ncols))
    cell_h, top, bottom, hspace = 1.55, 0.50, 0.44, 0.52
    H = top + bottom + nrows * cell_h + (nrows - 1) * hspace
    fig, axs = style.grid(style.FULL, H, nrows, ncols, left=0.50, right=0.08, top=top,
                          bottom=bottom, wspace=0.42, hspace=hspace)
    flat = [a for row in axs for a in row]
    for ax in flat[len(panels):]:
        ax.set_visible(False)

    for i, (ax, (f, s, cond, d)) in enumerate(zip(flat, panels)):
        cf = style.MODEL_COLORS[f]
        best = max(d["acc1"], d["acc2"])
        ax.axhline(best, color=style.INK_3, linewidth=0.7, linestyle=(0, (3, 2)), zorder=1)
        ax.plot(d["x"], d["y"], color=cf, linewidth=0.9, alpha=0.55, zorder=2,
                drawstyle="default")
        # single stages
        x1, y1 = d["first"]["cost_fraction"], d["first"]["accuracy"]
        ax.plot([x1], [y1], **style.point_kw(f, base=5.0))
        ax.plot([1.0], [d["acc2"]], **style.point_kw(s, base=5.0))
        # held-out cascade
        hx, hy = d["ho"]["cost_fraction"], d["ho"]["accuracy"]
        ax.plot([hx], [hy], linestyle="none", marker="o", markersize=8.5,
                markerfacecolor="none", markeredgecolor=style.INK, markeredgewidth=1.2,
                zorder=8)
        ax.plot([hx], [hy], linestyle="none", marker="o", markersize=2.2, color=style.INK,
                zorder=8)

        xs_all = np.r_[d["x"], 1.0, hx]
        ys_all = np.r_[d["y"], d["acc2"], hy]
        xmax = max(1.1, xs_all.max() * 1.04)
        ax.set_xlim(0, xmax)
        lo, hi = ys_all.min(), ys_all.max()
        pad = max(0.012, (hi - lo) * 0.14)
        ax.set_ylim(lo - pad * 1.6, hi + pad * 1.6)
        style.guides(ax, "y")

        # ticks: one format for every panel
        step = 0.5 if xmax > 1.6 else 0.25
        xt = np.arange(0, xmax + 1e-9, step)
        ax.set_xticks(xt)
        ax.set_xticklabels([f"{t:g}" for t in xt])
        ax.yaxis.set_major_formatter(FormatStrFormatter("%.2f"))
        ax.yaxis.set_major_locator(MaxNLocator(nbins=6, steps=[1, 2, 5, 10]))

        # direct labels for the single stages
        pos1, pos2 = LABEL_AT.get(i, (A, B))
        for (x, y, text), (dx, dy, ha, va) in (
                ((x1, y1, "First stage alone"), pos1),
                ((1.0, d["acc2"], SECOND_LABEL.get(s, style.label(s) + " alone")), pos2)):
            ax.annotate(text, (x, y), xytext=(dx, dy), textcoords="offset points", ha=ha,
                        va=va, fontsize=style.FS_NOTE, color=style.INK_2, zorder=9)

        style.title(ax, "abcdefghi"[i], f"{style.label(f)}, {COND_LABEL.get(cond, cond)}")
        r, c = divmod(i, ncols)
        if c == 0:
            ax.set_ylabel("Accuracy")
        if i + ncols >= len(panels):
            ax.set_xlabel("Cost relative to the second stage")

    ink = style.INK_2
    handles = [
        Line2D([], [], linestyle="none", marker="o", markersize=8.5, markerfacecolor="none",
               markeredgecolor=style.INK, markeredgewidth=1.2, label="Held-out cascade"),
        Line2D([], [], color=ink, linewidth=0.9, alpha=0.55, label="In-sample threshold sweep"),
        Line2D([], [], color=style.INK_3, linewidth=0.7, linestyle=(0, (3, 2)),
               label="Better single stage"),
        Line2D([], [], linestyle="none", marker="s", markersize=4.6, color=ink,
               markeredgecolor="white", label="Single stage alone (model marker)"),
    ]
    style.legend_top(fig, flat[0], flat[ncols - 1], handles, ncol=4, gap=0.27)
    pdf = style.save(fig, "f12_cascade")
    for d in MANUSCRIPT_FIGURES:
        if os.path.isdir(d):
            shutil.copyfile(pdf, os.path.join(d, "f12_cascade.pdf"))
            print(f"  copied to {d}")


if __name__ == "__main__":
    main()
