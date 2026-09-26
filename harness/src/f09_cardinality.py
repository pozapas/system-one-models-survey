"""F-cardinality: accuracy and ECE against option count on D2 (CLINC-150).

Full text width. Panel (a) is accuracy over K in (5, 20, 50, 150) on a log x-axis
with the chance curve 1/K, and a narrow strip to its right that holds the exact
accuracy of the two-stage (domain-then-intent) condition as hollow markers, dodged
horizontally so near-equal values stay visible. Panel (b) is top-label expected
calibration error over the same K. Every value is read from
results/e3_cardinality.json; a refused condition (accuracy None) is left out.

Output: figures/f09_cardinality.pdf and .png
"""
import json
import os

import numpy as np
from matplotlib.lines import Line2D
from matplotlib.ticker import FixedLocator, NullLocator, FuncFormatter

import common as C
import style

KS = [5, 20, 50, 150]
MODEL_ORDER = list(style.MODEL_COLORS)


def load():
    p = os.path.join(C.RESULTS, "e3_cardinality.json")
    return json.load(open(p, encoding="utf-8"))


def series(d, field):
    ks, vs = [], []
    for k in KS:
        v = d.get(str(k), {})
        if isinstance(v, dict) and v.get(field) is not None:
            ks.append(k)
            vs.append(v[field])
    return ks, vs


def log_x(ax):
    ax.set_xscale("log")
    ax.set_xlim(4.2, 180)
    ax.xaxis.set_major_locator(FixedLocator(KS))
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:g}"))
    ax.xaxis.set_minor_locator(NullLocator())


def main():
    style.apply()
    e3 = load()
    models = [m for m in MODEL_ORDER if m in e3]

    W, H = style.FULL, 2.80
    # columns: (a) main | two-stage strip | (b) main ; (a) and (b) have equal boxes
    strip, gap_strip, gap_ab = 0.40, 0.07, 0.62
    left, right = 0.50, 0.06
    main_w = (W - left - right - strip - gap_strip - gap_ab) / 2
    fig, axs = style.grid(W, H, 1, 3, left=left, right=right, top=0.64, bottom=0.44,
                          wspace=[gap_strip, gap_ab], hspace=0,
                          col_widths=[main_w, strip, main_w])
    ax1, axh, ax2 = axs[0]

    # chance curve
    ks_fine = np.geomspace(KS[0], KS[-1], 60)
    ax1.plot(ks_fine, 1.0 / ks_fine, color=style.INK_3, linewidth=0.8, linestyle=(0, (1, 1.6)),
             zorder=1)
    ax1.text(6.6, 1 / 6.6 + 0.02, "Chance", color=style.INK_2, fontsize=style.FS_NOTE,
             ha="left", va="bottom")

    n = len(models)
    for i, m in enumerate(models):
        d = e3[m]
        ks, acc = series(d, "accuracy")
        if ks:
            ax1.plot(ks, acc, **style.line_kw(m))
        ks, ece = series(d, "ece")
        if ks:
            ax2.plot(ks, ece, **style.line_kw(m))
        if isinstance(d.get("hier"), dict) and d["hier"].get("accuracy") is not None:
            dx = (i - (n - 1) / 2) * 0.115
            axh.plot([dx], [d["hier"]["accuracy"]], **style.point_kw(m, fill="none",
                                                                      base=style.MARKER_SIZE * 1.1))

    # panel (a)
    log_x(ax1)
    ax1.set_ylim(0, 1.02)
    ax1.set_yticks(np.arange(0, 1.01, 0.2))
    ax1.set_xlabel("Number of options (log scale)")
    ax1.set_ylabel("Accuracy")
    style.title(ax1, "a", "Accuracy by number of options")

    # two-stage strip shares the accuracy scale
    axh.set_ylim(ax1.get_ylim())
    axh.set_yticks(ax1.get_yticks())
    axh.tick_params(axis="y", length=0, labelleft=False)
    axh.set_xlim(-0.66, 0.66)
    axh.set_xticks([0])
    axh.set_xticklabels(["Two-\nstage"], linespacing=0.95)
    axh.tick_params(axis="x", length=0)
    axh.spines["left"].set_visible(True)
    axh.spines["left"].set_color("#BFBFBF")
    axh.spines["left"].set_linestyle((0, (2, 2)))

    # panel (b)
    log_x(ax2)
    ax2.set_ylim(0, 0.40)
    ax2.set_yticks(np.arange(0, 0.401, 0.1))
    ax2.set_xlabel("Number of options (log scale)")
    ax2.set_ylabel("Expected calibration error")
    style.title(ax2, "b", "Calibration error by number of options")

    hs, ls, ncol = style.model_legend(models)
    style.legend_top(fig, ax1, ax2, hs, ls, ncol=ncol, gap=0.27)
    style.save(fig, "f09_cardinality")


if __name__ == "__main__":
    main()
