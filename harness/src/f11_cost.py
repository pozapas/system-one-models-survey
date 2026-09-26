"""F-cost: USD per 1,000 decisions against p50 latency, p95 as a whisker.

One point per model, taken from the d1_neutral condition (the condition every
other main figure uses as its D1 canonical set). One column wide, log-log, each
point labeled directly with its model name instead of a legend, since nine
entries would take more room than the plot. The hardware is stated in the plot:
the hosted model is measured at the client through its API; every open model and
the comparator ran on the Colab GPU named in cost_latency.json (assumptions.gpu,
or the L4 implied by assumptions.l4_units_per_hour). A model whose latency_mode is
batched_amortized has p50 equal to p95 by construction and is labeled "batched"
so the missing whisker is not read as zero spread.

Output: figures/f11_cost.pdf and .png
"""
import json
import os

import numpy as np
from matplotlib.ticker import NullLocator

import common as C
import style

MODEL_ORDER = list(style.MODEL_COLORS)
COND = "d1_neutral"
API_MODELS = {"jev-1.13.0"}

# direct-label placement: (dx pt, dy pt, ha)
PLACE = {"laya-ml": (6, -1, "left"), "laya-en": (-6, 1, "right"),
         "this-that-1.0": (6, -3, "left"), "kev-0.8b": (-6, 4, "right"),
         "jev-1.13.0": (7, -2, "left"), "decider-2b": (-7, 0, "right"),
         "kev-9b": (7, -3, "left"), "comparator-open": (-7, 0, "right"),
         "nimble-9b": (-7, 0, "right")}


def load():
    p = os.path.join(C.RESULTS, "cost_latency.json")
    return json.load(open(p, encoding="utf-8"))


def gpu_name(cl):
    a = cl.get("assumptions", {})
    if a.get("gpu"):
        return f"Colab {a['gpu']} GPU"
    if "l4_units_per_hour" in a:
        return "Colab L4 GPU"
    return "Colab GPU"


def main():
    style.apply()
    cl = load()
    gpu = gpu_name(cl)
    models = [m for m in MODEL_ORDER if m in cl and COND in cl.get(m, {})
              and cl[m][COND].get("usd_per_1000_decisions") is not None]
    if not models:
        print("f11_cost: no model has a priced d1_neutral run yet")

    W, H = style.COLUMN, 2.75
    fig, axs = style.grid(W, H, 1, 1, left=0.50, right=0.08, top=0.10, bottom=0.44,
                          wspace=0, hspace=0)
    ax = axs[0][0]
    ax.set_xscale("log")
    ax.set_yscale("log")

    for m in models:
        v = cl[m][COND]
        x = v["usd_per_1000_decisions"]
        y50 = v["p50_s"] * 1000
        y95 = v["p95_s"] * 1000
        color = style.MODEL_COLORS[m]
        if y95 > y50:
            ax.plot([x, x], [y50, y95], color=color, linewidth=0.9, zorder=3)
            ax.plot([x], [y95], marker="_", markersize=5, markeredgewidth=0.9, color=color,
                    zorder=3)
        ax.plot([x], [y50], **style.point_kw(m, base=5.0))
        name = style.label(m)
        if m in API_MODELS:
            name += ", hosted API"
        elif v.get("latency_mode") == "batched_amortized":
            name += ", batched"
        dx, dy, ha = PLACE.get(m, (6, 0, "left"))
        ax.annotate(name, (x, y50), xytext=(dx, dy), textcoords="offset points", ha=ha,
                    va="center", fontsize=style.FS_NOTE, color=style.INK)

    ax.set_xlim(4e-4, 1.5e-1)
    ax.set_ylim(20, 6000)
    ax.set_xticks([1e-3, 1e-2, 1e-1])
    ax.set_xticklabels(["0.001", "0.01", "0.1"])
    ax.set_yticks([20, 50, 100, 200, 500, 1000, 2000, 5000])
    ax.set_yticklabels(["20", "50", "100", "200", "500", "1000", "2000", "5000"])
    ax.yaxis.set_minor_locator(NullLocator())
    ax.set_xlabel("USD per 1,000 decisions (log scale)")
    ax.set_ylabel("Median latency per request, ms (log scale)")
    style.guides(ax, "y")
    ax.text(0.03, 0.98, f"Open models and comparator\non one {gpu}\n"
            "Whiskers reach the 95th percentile",
            transform=ax.transAxes, ha="left", va="top", fontsize=style.FS_NOTE,
            color=style.INK_2, linespacing=1.3)
    style.save(fig, "f11_cost")


if __name__ == "__main__":
    main()
