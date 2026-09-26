"""One visual system for every figure of Paper 4A (ACL two-column template).

The ACL column width is 219.08pt (3.03 in) and the text width 455.24pt (6.30 in),
from acl.sty. Every figure is drawn at exactly one of those widths and saved
without a tight bounding box, so the page of the PDF is the printed size and the
type inside it prints at the sizes below, in Times to match the template.

Layout is explicit. `grid()` places axes from margins given in inches, so equal
panels have identical boxes, panel titles (`title()`) sit left-aligned to the
axes edge at one height, and the shared legend (`legend_top()`) spans exactly the
axes grid above the titles.

Color. One fixed color and marker per model, used identically in every figure.
The hosted model is the anchor (vermillion, heavier line, larger marker, drawn on
top). Model families share a hue at two lightness steps: Laya English (light) and
multilingual (dark) in blue, Kev-0.8B (light) and Kev-9B (dark) in green, and the
square/diamond and down/up triangle markers pair them too. The generative
comparator is neutral grey with a dashed line. The eight chromatic colors pass
the dataviz validator (validate_palette.js, light mode, white surface) on ALL
pairs: worst CVD delta E 8.4, worst normal-vision delta E 15.7. The grey cannot
clear the CVD gate against every hue at any lightness, so the comparator always
carries its dash and hexagon as secondary encoding. Three colors are below 3:1
on white (#55A6E2, #40B98B, #BE960A), so their markers get a darker edge of the
same hue.
"""
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

PT_PER_INCH = 72.27
COLUMN = 219.08 / PT_PER_INCH             # 3.03 in, one ACL column
FULL = 455.24 / PT_PER_INCH               # 6.30 in, full ACL text width
HALF = COLUMN

# Type scale at printed size (pt)
FS_TICK = 7.5
FS_LABEL = 8.5
FS_TITLE = 9.0
FS_LEGEND = 7.5
FS_NOTE = 7.0          # direct labels inside a plot
LABELPAD = 4.0         # axis-title padding, identical everywhere
TITLEPAD = 5.0         # panel-title padding above the axes

# Ink
INK = "#1A1A1A"
INK_2 = "#4D4D4D"      # secondary text
INK_3 = "#8A8A8A"      # reference lines
GUIDE = "#EBEBEB"      # faint horizontal guides
SPINE = "#333333"

# Model identity (keys and order are also read by t01_tables.py, keep them)
MODEL_COLORS = {
    "jev-1.13.0": "#D54707",
    "laya-en": "#55A6E2",
    "laya-ml": "#0F5992",
    "kev-0.8b": "#40B98B",
    "kev-9b": "#057B5B",
    "decider-2b": "#7F4FC4",
    "this-that-1.0": "#CC5AA6",
    "nimble-9b": "#BE960A",
    "comparator-open": "#808080",
}

MODEL_LABELS = {
    "jev-1.13.0": "Jev 1.13.0",
    "laya-en": "Laya (English)",
    "laya-ml": "Laya (multilingual)",
    "kev-0.8b": "Kev-0.8B",
    "kev-9b": "Kev-9B",
    "decider-2b": "decider-2b",
    "this-that-1.0": "this-that-model-1.0",
    "nimble-9b": "Nimble-9B",
    "comparator-open": "Generative comparator",
}

MODEL_MARKERS = {
    "jev-1.13.0": "o", "laya-en": "s", "laya-ml": "D", "kev-0.8b": "v", "kev-9b": "^",
    "decider-2b": "P", "this-that-1.0": "X", "nimble-9b": "*", "comparator-open": "h",
}

# darker same-hue edge for the three colors under 3:1 on white, and for the thin
# plus and cross glyphs, which a white edge would erode
_EDGE = {"laya-en": "#2F78B0", "kev-0.8b": "#23865F", "nimble-9b": "#8A6A00",
         "decider-2b": "#5E35A0", "this-that-1.0": "#A8407F"}
# markers that read small at the same nominal size
_MSCALE = {"jev-1.13.0": 1.2, "kev-9b": 1.12, "nimble-9b": 1.45, "laya-ml": 0.9, "decider-2b": 1.1,
           "this-that-1.0": 1.05}

HOSTED = "jev-1.13.0"
COMPARATORS = ("comparator-open",)
MARKER_SIZE = 4.2
LW = 1.0
LW_HOSTED = 1.7


def label(model):
    """Figure label. Product names keep their own case (decider-2b,
    this-that-model-1.0); the one descriptive label is capitalized."""
    s = MODEL_LABELS[model]
    return "Generative comparator" if s == "generative comparator" else s


def edge(model):
    return _EDGE.get(model, "white")


def msize(model, base=MARKER_SIZE):
    return base * _MSCALE.get(model, 1.0)


def line_kw(model, markers=True, base=MARKER_SIZE):
    """Keyword arguments for ax.plot of one model's series."""
    hosted = model == HOSTED
    kw = dict(color=MODEL_COLORS[model], linewidth=LW_HOSTED if hosted else LW,
              linestyle=(0, (4, 1.6)) if model in COMPARATORS else "-",
              zorder=6 if hosted else 3, solid_capstyle="round", label=label(model))
    if markers:
        kw.update(marker=MODEL_MARKERS[model], markersize=msize(model, base),
                  markerfacecolor=MODEL_COLORS[model], markeredgecolor=edge(model),
                  markeredgewidth=0.6)
    return kw


def point_kw(model, base=MARKER_SIZE, fill="full"):
    """Keyword arguments for a standalone marker of one model (no line)."""
    c = MODEL_COLORS[model]
    kw = dict(linestyle="none", marker=MODEL_MARKERS[model], markersize=msize(model, base),
              color=c, markeredgewidth=0.7, zorder=7 if model == HOSTED else 4)
    if fill == "full":
        kw.update(markerfacecolor=c, markeredgecolor=edge(model))
    elif fill == "none":
        kw.update(markerfacecolor="white", markeredgecolor=c)
    else:                                   # "left" half filled
        kw.update(fillstyle="left", markerfacecolor=c, markerfacecoloralt="white",
                  markeredgecolor=c)
    return kw


# legend grid, one list per column: families stacked in one column
LEGEND_COLUMNS = [["jev-1.13.0", "comparator-open"], ["laya-en", "laya-ml"],
                  ["kev-0.8b", "kev-9b"], ["decider-2b", "this-that-1.0"], ["nimble-9b"]]


def model_legend(models, markers=True, extra=()):
    """Handles and labels for the shared legend, laid out column by column so each
    family shares a column (matplotlib fills legends column-major). Missing models
    leave an empty slot; `extra` handles are appended as further columns."""
    rows = max(len(c) for c in LEGEND_COLUMNS)
    hs, ls = [], []
    blank = Line2D([], [], linestyle="none", marker=None)
    for col in LEGEND_COLUMNS:
        if not any(m in models for m in col):
            continue
        for r in range(rows):
            m = col[r] if r < len(col) else None
            if m in models:
                h = handle(m, markers=markers)
                hs.append(h)
                ls.append(h.get_label())
            else:
                hs.append(blank)
                ls.append("")
    extra = list(extra)
    while extra:
        for r in range(rows):
            if extra:
                h = extra.pop(0)
                hs.append(h)
                ls.append(h.get_label())
            else:
                hs.append(blank)
                ls.append("")
    ncol = len(hs) // rows
    return hs, ls, ncol


def handle(model, markers=True):
    return Line2D([], [], **line_kw(model, markers=markers))


def apply():
    plt.rcParams.update({
        "figure.dpi": 150,
        "savefig.dpi": 300,
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "savefig.facecolor": "white",
        "savefig.edgecolor": "white",
        "savefig.bbox": None,
        "savefig.pad_inches": 0.0,
        "font.family": "serif",
        "font.serif": ["Times New Roman", "Times", "Nimbus Roman", "STIXGeneral"],
        "mathtext.fontset": "stix",
        "font.size": FS_LABEL,
        "text.color": INK,
        "axes.titlesize": FS_TITLE,
        "axes.titleweight": "normal",
        "axes.titlelocation": "left",
        "axes.titlepad": TITLEPAD,
        "axes.titlecolor": INK,
        "axes.labelsize": FS_LABEL,
        "axes.labelpad": LABELPAD,
        "axes.labelcolor": INK,
        "axes.edgecolor": SPINE,
        "axes.linewidth": 0.6,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "axes.grid.axis": "y",
        "axes.axisbelow": True,
        "grid.color": GUIDE,
        "grid.linewidth": 0.5,
        "grid.linestyle": "-",
        "xtick.labelsize": FS_TICK,
        "ytick.labelsize": FS_TICK,
        "xtick.color": SPINE,
        "ytick.color": SPINE,
        "xtick.labelcolor": INK,
        "ytick.labelcolor": INK,
        "xtick.direction": "out",
        "ytick.direction": "out",
        "xtick.major.size": 3.0,
        "ytick.major.size": 3.0,
        "xtick.minor.size": 1.6,
        "ytick.minor.size": 1.6,
        "xtick.major.width": 0.6,
        "ytick.major.width": 0.6,
        "xtick.minor.width": 0.45,
        "ytick.minor.width": 0.45,
        "xtick.major.pad": 2.5,
        "ytick.major.pad": 2.5,
        "legend.fontsize": FS_LEGEND,
        "legend.frameon": False,
        "legend.handlelength": 1.7,
        "legend.handletextpad": 0.45,
        "legend.columnspacing": 1.0,
        "legend.borderaxespad": 0.0,
        "legend.borderpad": 0.0,
        "lines.linewidth": LW,
        "lines.markeredgewidth": 0.6,
        "lines.solid_capstyle": "round",
        "patch.linewidth": 0.5,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
    })


def grid(width, height, nrows, ncols, left, right, top, bottom, wspace, hspace,
         col_widths=None, row_heights=None, sharex=False, sharey=False):
    """Axes on an explicit grid, every margin and gap in inches.

    wspace / hspace may be one gap or a list with one gap per boundary.
    col_widths / row_heights are relative weights; by default all cells are equal,
    so equal panels have identical boxes. Returns (fig, axes[nrows][ncols])."""
    fig = plt.figure(figsize=(width, height))
    cw = col_widths or [1.0] * ncols
    rh = row_heights or [1.0] * nrows
    wsp = list(wspace) if isinstance(wspace, (list, tuple)) else [wspace] * (ncols - 1)
    hsp = list(hspace) if isinstance(hspace, (list, tuple)) else [hspace] * (nrows - 1)
    avail_w = width - left - right - sum(wsp)
    avail_h = height - top - bottom - sum(hsp)
    ws = [avail_w * c / sum(cw) for c in cw]
    hs = [avail_h * r / sum(rh) for r in rh]
    axes = [[None] * ncols for _ in range(nrows)]
    y = height - top
    for i in range(nrows):
        y -= hs[i]
        x = left
        for j in range(ncols):
            kw = {}
            if sharex and (i or j):
                kw["sharex"] = axes[0][0]
            if sharey and (i or j):
                kw["sharey"] = axes[0][0]
            axes[i][j] = fig.add_axes([x / width, y / height, ws[j] / width, hs[i] / height], **kw)
            x += ws[j] + (wsp[j] if j < ncols - 1 else 0)
        y -= hsp[i] if i < nrows - 1 else 0
    return fig, axes


def title(ax, letter, text):
    """Panel title '(a) Text', left-aligned to the axes' left edge."""
    ax.set_title(f"({letter}) {text}", loc="left", pad=TITLEPAD, fontsize=FS_TITLE)


def legend_top(fig, ax_left, ax_right, handles, labels=None, ncol=5, gap=0.30):
    """One shared legend above the axes grid, its left edge on ax_left's left edge
    and its bottom `gap` inches above the top of ax_left (clear of the panel
    titles). Columns take their natural widths; ncol is reduced until the legend
    fits inside the grid width (ax_left.x0 to ax_right.x1)."""
    W, H = fig.get_size_inches()
    b0 = ax_left.get_position()
    b1 = ax_right.get_position()
    x0, x1 = b0.x0, b1.x1
    y0 = b0.y1 + gap / H
    if labels is None:
        labels = [h.get_label() for h in handles]
    renderer = fig.canvas.get_renderer()
    for nc in range(ncol, 0, -1):
        if nc < ncol and "" in labels:
            break                               # a fixed grid must not reflow
        leg = fig.legend(handles, labels, loc="lower left", bbox_to_anchor=(x0, y0),
                         ncol=nc, frameon=False, borderaxespad=0.0, borderpad=0.0,
                         labelspacing=0.35)
        bb = leg.get_window_extent(renderer).transformed(fig.transFigure.inverted())
        if bb.x1 <= x1 + 1e-6:
            return leg
        leg.remove()
    return fig.legend(handles, labels, loc="lower left", bbox_to_anchor=(x0, y0), ncol=1)


def legend_height(fig, leg):
    """Height of a placed legend in inches."""
    bb = leg.get_window_extent(fig.canvas.get_renderer())
    return bb.height / fig.dpi


def guides(ax, axis="y"):
    ax.grid(False)
    ax.grid(True, axis=axis, color=GUIDE, linewidth=0.5)


def save(fig, name, figdir=None):
    from common import FIGURES
    figdir = figdir or FIGURES
    os.makedirs(figdir, exist_ok=True)
    path = os.path.join(figdir, name + ".pdf")
    fig.savefig(path, bbox_inches=None, pad_inches=0.0, facecolor="white")
    png = os.path.join(figdir, name + ".png")
    fig.savefig(png, dpi=300, bbox_inches=None, pad_inches=0.0, facecolor="white")
    w, h = fig.get_size_inches()
    plt.close(fig)
    print(f"  wrote {path}  ({w:.2f} x {h:.2f} in)")
    return path


def panel_label(ax, letter, dx=-0.22, dy=1.22):
    """Kept for backward compatibility; figures now use title()."""
    ax.text(dx, dy, f"({letter})", transform=ax.transAxes,
            fontsize=FS_TITLE, va="top", ha="left")
