"""F-names: option-name swap, flips per hundred and AUC by condition, as a dot matrix.

Models are rows, grouped by decision-head type (hosted, encoder option-marker
scorers, decoder-based heads), in the fixed model color and marker. Panel (a) is
flips per hundred against the aligned no/yes condition on a symmetric log axis,
one column block per binary dataset (D1, conversation derailment, power). Each row
carries three naming conditions as fill states of the model's own marker (0/1
hollow, random strings half filled, swapped filled), a thin bar over their range,
and a black tick at the model's test-retest floor where one was measured. Panel
(b) is the AUC of the positive-rubric probability for the same conditions, with
the aligned no/yes AUC as the black reference tick and chance at 0.5.

Every value comes from results/e2_names.json. The floor mapping is unchanged from
the previous version: the dataset's own floor when present, else the d1_neutral
retest floor for D1, else no floor is drawn.

Output: figures/f10_names.pdf and .png
"""
import json
import os

from matplotlib.lines import Line2D
from matplotlib.ticker import FixedLocator, NullLocator

import common as C
import style

DATASETS = [("d1", "D1"), ("d3_conv_go_awry", "Derailment"), ("d3_wiki_corpus", "Power")]
CONDS = [("k01", "none"), ("krand", "left"), ("kswap", "full")]      # (key, marker fill)
GROUPS = [("Hosted", ["jev-1.13.0"]),
          ("Encoder scorers", ["laya-en", "laya-ml"]),
          ("Decoder-based heads", ["kev-0.8b", "kev-9b", "decider-2b", "this-that-1.0",
                                   "nimble-9b"])]
HEADER_GAP = 0.95
GROUP_GAP = 0.45


def load():
    p = os.path.join(C.RESULTS, "e2_names.json")
    return json.load(open(p, encoding="utf-8"))


def layout(models):
    """y position of every model row and of every group header (top to bottom)."""
    ys, heads = {}, []
    y = 0.0
    for gi, (name, members) in enumerate(GROUPS):
        members = [m for m in members if m in models]
        if not members:
            continue
        if gi:
            y += GROUP_GAP
        heads.append((name, y))
        y += HEADER_GAP
        for m in members:
            ys[m] = y
            y += 1.0
    return ys, heads, y - 0.4


def floor_of(d, ds_key):
    floor = d.get("retest_floor", {})
    fkey = ds_key if ds_key in floor else ("d1_neutral" if ds_key == "d1" else None)
    if fkey is None or fkey not in floor:
        return None
    return floor[fkey]["flips_per_100"]


def draw_row(ax, m, y, vals, ref):
    color = style.MODEL_COLORS[m]
    span = [v for v in vals.values()] + ([ref] if ref is not None else [])
    ax.plot([min(span), max(span)], [y, y], color=color, linewidth=1.3 if m == style.HOSTED
            else 0.9, alpha=0.55, solid_capstyle="butt", zorder=2)
    if ref is not None:
        ax.plot([ref], [y], linestyle="none", marker="|", markersize=7.5,
                markeredgewidth=1.2, color=style.INK, zorder=3)
    for c_key, fill in CONDS:
        if c_key in vals:
            ax.plot([vals[c_key]], [y], **style.point_kw(m, fill=fill, base=4.4))


def main():
    style.apply()
    e2 = load()
    models = [m for m in style.MODEL_COLORS if m in e2]
    if not models:
        print("f10_names: no model has e2_names results yet")
    ys, heads, ymax = layout(models)

    W, H = style.FULL, 2.95
    left, right = 1.16, 0.06
    sub_gap, block_gap = 0.09, 0.30
    fig, axs = style.grid(W, H, 1, 6, left=left, right=right, top=0.74, bottom=0.44,
                          wspace=[sub_gap, sub_gap, block_gap, sub_gap, sub_gap], hspace=0)
    axes = axs[0]
    flip_axes, auc_axes = axes[:3], axes[3:]

    for j, (ds_key, ds_lab) in enumerate(DATASETS):
        axf, axa = flip_axes[j], auc_axes[j]
        axa.axvline(0.5, color=style.INK_3, linewidth=0.7, linestyle=(0, (1, 1.6)), zorder=1)
        for m in models:
            d = e2[m].get(ds_key)
            if not d:
                continue
            y = ys[m]
            flips = {c: d[c]["flips_per_100_vs_kny"] for c, _ in CONDS if c in d}
            draw_row(axf, m, y, flips, floor_of(e2[m], ds_key))
            aucs = {c: d[c]["auc"] for c, _ in CONDS if c in d}
            draw_row(axa, m, y, aucs, d["kny"]["auc"] if "kny" in d else None)

        axf.set_xscale("symlog", linthresh=1.0, linscale=0.6)
        axf.set_xlim(-0.7, 160)
        axf.xaxis.set_major_locator(FixedLocator([0, 1, 10, 100]))
        axf.set_xticklabels(["0", "1", "10", "100"])
        axf.xaxis.set_minor_locator(NullLocator())
        axa.set_xlim(0.26, 0.96)
        axa.set_xticks([0.4, 0.6, 0.8])
        axa.set_xticklabels(["0.4", "0.6", "0.8"])
        for ax in (axf, axa):
            ax.set_ylim(ymax, -0.35)
            ax.grid(False)
            for y in ys.values():
                ax.axhline(y, color="#F4F4F4", linewidth=0.5, zorder=0)
            ax.set_title(ds_lab, loc="left", fontsize=style.FS_LABEL, pad=3.0,
                         color=style.INK_2)
            ax.set_yticks([ys[m] for m in models])
            if ax is axes[0]:
                ax.set_yticklabels([style.label(m) for m in models])
                ax.tick_params(axis="y", length=0, pad=4)
            else:
                ax.tick_params(axis="y", length=0, labelleft=False)
                ax.spines["left"].set_color("#BFBFBF")

    # group headers, left-aligned at the figure margin, in the header rows
    ax0 = axes[0]
    x_head = -(left - 0.06) / (ax0.get_position().width * W)
    for name, y in heads:
        ax0.text(x_head, y + 0.15, name, transform=ax0.get_yaxis_transform(), ha="left",
                 va="center", fontsize=style.FS_TICK, style="italic", color=style.INK_2)

    # panel titles sit above the dataset headers, left-aligned to each block
    for ax, letter, text in ((flip_axes[0], "a", "Flips per hundred against aligned names"),
                             (auc_axes[0], "b", "AUC of the positive-rubric probability")):
        ax.text(0, 1 + 0.20 / (ax.get_position().height * H), f"({letter}) {text}",
                transform=ax.transAxes, ha="left", va="bottom", fontsize=style.FS_TITLE)
    flip_axes[1].set_xlabel("Flips per hundred (symmetric log scale)")
    auc_axes[1].set_xlabel("Area under the ROC curve")

    ink = style.INK_2
    glyph = dict(linestyle="none", marker="o", markersize=4.6, color=ink, markeredgewidth=0.7,
                 markeredgecolor=ink)
    handles = [
        Line2D([], [], markerfacecolor="white", label="0/1 names", **glyph),
        Line2D([], [], fillstyle="left", markerfacecolor=ink, markerfacecoloralt="white",
               label="Random strings", **glyph),
        Line2D([], [], markerfacecolor=ink, label="Swapped", **glyph),
        Line2D([], [], linestyle="none", marker="|", markersize=7.5, markeredgewidth=1.2,
               color=style.INK, label="Retest floor (a) or aligned names (b)"),
        Line2D([], [], color=style.INK_3, linewidth=0.7, linestyle=(0, (1, 1.6)),
               label="Chance"),
    ]
    style.legend_top(fig, axes[0], axes[-1], handles, ncol=5, gap=0.45)
    style.save(fig, "f10_names")


if __name__ == "__main__":
    main()
