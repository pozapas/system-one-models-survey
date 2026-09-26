"""F-riskcov: risk-coverage curves for D1, D2 and D3 pooled.

One panel per main dataset (D1 = d1_neutral, D2 = d2_k150 restricted to in-scope
items, D3 = the four D3 tasks pooled), one curve per model present, computed from
shipped probabilities with metrics.risk_coverage. The D3 pool uses the same
shipped decisions as t04's D3-pooled calibration row (collect_numbers.pool_d3),
so the figure and the table agree.

Presentation: full text width, three panels with one shared risk axis on a
square-root scale, so the low-risk operating region (the 1% and 5% guides, which
are also y ticks) and the full 0 to 1 range are readable in the same frame.

Output: figures/f07_riskcov.pdf and .png
"""
import numpy as np
from matplotlib.ticker import NullLocator

import bench
import collect_numbers as CN
import common as C
import metrics as M
import style

MODEL_ORDER = list(style.MODEL_COLORS)


def d1_curve(model):
    rows = [r for r in bench.decisions(model, "d1_neutral")
            if r["y"] >= 0 and not np.isnan(r["p"]).any()]
    if not rows:
        return None
    conf = np.array([r["p"].max() for r in rows])
    correct = np.array([float(np.argmax(r["p"]) == r["y"]) for r in rows])
    return M.risk_coverage(conf, correct)


def d2_curve(model):
    rows = [r for r in bench.decisions(model, "d2_k150")
            if r["y"] >= 0 and not np.isnan(r["p"]).any() and r["meta"]["in_scope"]]
    if not rows:
        return None
    conf = np.array([r["p"].max() for r in rows])
    correct = np.array([float(np.argmax(r["p"]) == r["y"]) for r in rows])
    return M.risk_coverage(conf, correct)


def d3_curve(model):
    pooled = CN.pool_d3(model)
    if pooled is None:
        return None
    return M.risk_coverage(pooled["conf"], pooled["correct"])


PANELS = [("D1, neutral phrasing", d1_curve, "d1_neutral"),
          ("D2, in-scope items", d2_curve, "d2_k150"),
          ("D3, four tasks pooled", d3_curve, "d3_conv_go_awry")]

RISK_TICKS = [0, 0.01, 0.05, 0.1, 0.2, 0.4, 0.6, 0.8, 1.0]


def sqrt_scale(ax):
    ax.set_yscale("function", functions=(lambda v: np.sqrt(np.clip(v, 0, None)),
                                         lambda v: np.square(v)))
    ax.set_ylim(0, 1.0)
    ax.set_yticks(RISK_TICKS)
    ax.set_yticklabels([f"{t:g}" for t in RISK_TICKS])
    ax.yaxis.set_minor_locator(NullLocator())


def main():
    style.apply()
    W, H = style.FULL, 2.85
    fig, axs = style.grid(W, H, 1, 3, left=0.50, right=0.06, top=0.66, bottom=0.44,
                          wspace=0.20, hspace=0, sharey=True)
    axes = axs[0]
    present = []
    for k, (ax, letter, (tag, fn, probe)) in enumerate(zip(axes, "abc", PANELS)):
        sqrt_scale(ax)
        for lvl in (0.01, 0.05):
            ax.axhline(lvl, color=style.INK_3, linewidth=0.6, linestyle=(0, (3, 2)), zorder=1)
        for i, model in enumerate(MODEL_ORDER):
            if not bench.available_reps(model, probe):
                continue
            out = fn(model)
            if out is None:
                continue
            cov, risk, _thr = out
            kw = style.line_kw(model, base=3.8)
            # markers at fixed coverages, staggered per model so they do not stack
            targets = np.arange(0.08 + 0.022 * i, 1.0, 0.2)
            kw["markevery"] = sorted(set(np.clip(np.searchsorted(cov, targets), 0,
                                                 len(cov) - 1).tolist()))
            ax.plot(cov, risk, **kw)
            if model not in present:
                present.append(model)
        ax.set_xlim(0, 1)
        ax.set_xticks(np.arange(0, 1.01, 0.2))
        ax.set_xticklabels(["0", "0.2", "0.4", "0.6", "0.8", "1"])
        ax.set_xlabel("Coverage")
        style.title(ax, letter, tag)
        if k:
            ax.tick_params(axis="y", labelleft=False)
    axes[0].set_ylabel("Risk of accepted decisions (square-root scale)")

    if not present:
        print("f07_riskcov: no model has usable decisions yet, wrote empty panels")
    hs, ls, ncol = style.model_legend(present)
    style.legend_top(fig, axes[0], axes[-1], hs, ls, ncol=ncol, gap=0.27)
    style.save(fig, "f07_riskcov")


if __name__ == "__main__":
    main()
