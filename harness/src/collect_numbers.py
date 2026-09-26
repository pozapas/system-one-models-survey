"""Collect every number the manuscripts cite into one file, with its source.

Adapted from paper3/src/collect_numbers.py. A manuscript never types a number. It
writes \\num{label}, and the macro is defined from results/numbers.json, which this
script builds. A label that has no entry produces a visible error at compile time
rather than a wrong number in the text.

Labels are <experiment>.<model>.<dataset or condition>.<metric>, lower case, and are
frozen once shared/results/NUMBERS_PRELIM exists, because the survey
builds its own macros from the same file.

Run this after any analysis changes, then recompile.
"""
import json
import os

import numpy as np

import bench
import common as C
import metrics as M

N = {}

D3_CONDS = ["d3_conv_go_awry", "d3_wiki_corpus", "d3_emotion", "d3_wiki_politeness"]

SLUG = {"jev-1.13.0": "jev", "laya-en": "layaen", "laya-ml": "layaml",
        "kev-0.8b": "kevsmall", "kev-9b": "kevlarge", "decider-2b": "decider",
        "this-that-1.0": "thisthat", "nimble-9b": "nimble",
        "comparator-open": "compopen"}
CSLUG = {"d1_native": "donenative", "d1_neutral": "doneneutral", "d2_k150": "dtwo",
         "d3_conv_go_awry": "toxicity", "d3_wiki_corpus": "power",
         "d3_emotion": "emotion", "d3_wiki_politeness": "politeness"}


def add(label, value, source, note=None, fmt=None):
    if value is None:          # e.g. a model that refused every request of a condition
        return
    N[label] = {"value": value, "source": source, "note": note, "fmt": fmt}


def load(name):
    p = os.path.join(C.RESULTS, name)
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else None


def fmt_value(v, fmt):
    if isinstance(v, str):
        return v
    if fmt:
        return format(v, fmt)
    if isinstance(v, int):
        return f"{v:,}"
    if isinstance(v, float):
        return f"{v:.3f}" if abs(v) < 100 else f"{v:,.0f}"
    return str(v)


def tidy_decimal(v):
    """Display a ledger value at no more than three decimals and without a trailing
    zero after the point (0.5610 -> 0.561, 32.50 -> 32.5); the ledger keeps the
    value as extracted, and this changes only its printed precision."""
    import re
    if not re.fullmatch(r"-?\d+\.\d+", v):
        return v
    dec = len(v.split(".")[1])
    if dec > 3:
        v = f"{float(v):.3f}"
    if "." in v:
        v = v.rstrip("0")
        v = v + "0" if v.endswith(".") else v
    return v


def pool_d3(model, rep=1):
    """Pool shipped, raw and scaled probabilities across the four D3 tasks.

    Mirrors a01_e1_main.summarize() condition by condition (so the temperature
    used for the scaled arm is cross-fit within each task, never across tasks),
    then concatenates the four tasks' decisions into one pooled set. Used by
    t04's D3-pooled calibration row and by f07's pooled D3 risk-coverage panel,
    so the figure and the table cannot disagree. Returns None if the model has
    no D3 answers yet.
    """
    conf_l, corr_l = [], []
    conf_raw_l, corr_raw_l = [], []
    conf_s_l, corr_s_l = [], []
    for cond in D3_CONDS:
        if not bench.available_reps(model, cond):
            continue
        rows = bench.decisions(model, cond, rep)
        rs = [r for r in rows if r["y"] >= 0 and not np.isnan(r["p"]).any()]
        if not rs:
            continue
        raw_rows = {r["key"] + r["qid"]: r
                    for r in bench.decisions(model, cond, rep, raw=True)}
        P = [r["p"] for r in rs]
        y = np.array([r["y"] for r in rs])
        groups = np.array([r["item_id"] for r in rs])
        conf = np.array([p.max() for p in P])
        correct = np.array([float(np.argmax(p) == k) for p, k in zip(P, y)])
        Praw = [raw_rows[r["key"] + r["qid"]]["p"] for r in rs]
        conf_raw = np.array([p.max() for p in Praw])
        corr_raw = np.array([float(np.argmax(p) == k) for p, k in zip(Praw, y)])
        Ps, _Ts = M.crossfit_T(P, y, groups)
        conf_s = np.array([p.max() for p in Ps])
        corr_s = np.array([float(np.argmax(p) == k) for p, k in zip(Ps, y)])
        conf_l.append(conf); corr_l.append(correct)
        conf_raw_l.append(conf_raw); corr_raw_l.append(corr_raw)
        conf_s_l.append(conf_s); corr_s_l.append(corr_s)
    if not conf_l:
        return None
    return {"conf": np.concatenate(conf_l), "correct": np.concatenate(corr_l),
            "conf_raw": np.concatenate(conf_raw_l), "correct_raw": np.concatenate(corr_raw_l),
            "conf_scaled": np.concatenate(conf_s_l), "correct_scaled": np.concatenate(corr_s_l),
            "n": int(sum(len(c) for c in conf_l))}


def collect_e1(e1):
    src = "results/e1_main.json"
    for key, d in e1.items():
        m, cond = key.split("|")
        if m not in SLUG:
            continue
        ms = SLUG[m]
        if cond == "d2_oos":
            add(f"e1.{ms}.oos.auroc", d["auroc_in_vs_oos"], src, fmt=".3f")
            add(f"e1.{ms}.oos.confin", d["mean_conf_in"], src, fmt=".3f")
            add(f"e1.{ms}.oos.confoos", d["mean_conf_oos"], src, fmt=".3f")
            add(f"e1.{ms}.oos.highconf", d["share_oos_conf_ge_0_9"], src, fmt=".3f")
            continue
        p = f"e1.{ms}.{CSLUG[cond]}"
        add(f"{p}.n", d["n_scored"], src)
        add(f"{p}.acc", d["accuracy"], src, fmt=".3f")
        add(f"{p}.acclo", d["accuracy_ci"][0], src, fmt=".3f")
        add(f"{p}.acchi", d["accuracy_ci"][1], src, fmt=".3f")
        add(f"{p}.brier", d["brier"], src, fmt=".3f")
        add(f"{p}.nll", d["nll"], src, fmt=".3f")
        add(f"{p}.ece", d["ece_shipped"], src, fmt=".3f")
        add(f"{p}.ecelo", d["ece_shipped_ci"][0], src, fmt=".3f")
        add(f"{p}.ecehi", d["ece_shipped_ci"][1], src, fmt=".3f")
        add(f"{p}.eceraw", d["ece_raw"], src, fmt=".3f")
        add(f"{p}.ecescaled", d["ece_scaled"], src, fmt=".3f")
        add(f"{p}.aurc", d["aurc_shipped"], src, fmt=".3f")
        add(f"{p}.covone", d["coverage_at_1pct"], src, fmt=".2f")
        add(f"{p}.covfive", d["coverage_at_5pct"], src, fmt=".2f")
        add(f"{p}.covfivescaled", d["coverage_at_5pct_scaled"], src, fmt=".2f")
        add(f"{p}.reviewfive", d["review_budget_at_5pct"], src, fmt=".2f")
        add(f"{p}.meanconf", d["mean_confidence"], src, fmt=".3f")
        add(f"{p}.highconf", d["share_conf_ge_0_9"], src, fmt=".3f")
        if d.get("acc_when_conf_ge_0_9") is not None:
            add(f"{p}.acchighconf", d["acc_when_conf_ge_0_9"], src, fmt=".3f")
        add(f"{p}.reliability", d["murphy_shipped"]["reliability"], src, fmt=".4f")
        add(f"{p}.resolution", d["murphy_shipped"]["resolution"], src, fmt=".4f")
        add(f"{p}.distinct", d["distinct_prob_values"], src)
        if "macro_f1" in d:
            add(f"{p}.macrofone", 100 * d["macro_f1"], src, fmt=".1f")
        if "soft_accuracy" in d:
            add(f"{p}.softacc", d["soft_accuracy"], src, fmt=".3f")
            add(f"{p}.briersoft", d["brier_soft"], src, fmt=".3f")
            for t, v in d["by_type"].items():
                add(f"{p}.{t}.acc", v["accuracy"], src, fmt=".3f")
                add(f"{p}.{t}.ece", v["ece_shipped"], src, fmt=".3f")

    models = sorted({key.split("|")[0] for key in e1 if key.split("|")[0] in SLUG})
    for m in models:
        ms = SLUG[m]
        d3_keys = [f"{m}|{c}" for c in D3_CONDS if f"{m}|{c}" in e1]
        f1s = [e1[k]["macro_f1"] for k in d3_keys if "macro_f1" in e1[k]]
        if f1s:
            add(f"e1.{ms}.dthree.macrofone", 100 * float(np.mean(f1s)), src, fmt=".1f",
                note="mean of the four D3 tasks' macro-F1, not a pooled confusion matrix")
        pooled = pool_d3(m)
        if pooled is None:
            continue
        psrc = "answers/ pooled across the four D3 tasks by collect_numbers.pool_d3"
        add(f"e1.{ms}.dthree.n", pooled["n"], psrc)
        add(f"e1.{ms}.dthree.ece", M.ece(pooled["conf"], pooled["correct"]), psrc, fmt=".3f")
        add(f"e1.{ms}.dthree.eceraw", M.ece(pooled["conf_raw"], pooled["correct_raw"]), psrc,
            fmt=".3f")
        add(f"e1.{ms}.dthree.ecescaled",
            M.ece(pooled["conf_scaled"], pooled["correct_scaled"]), psrc, fmt=".3f")
        cov5, _thr = M.coverage_at_risk(pooled["conf"], pooled["correct"], 0.05)
        add(f"e1.{ms}.dthree.covfive", cov5, psrc, fmt=".2f")


def collect_e2(e2):
    src = "results/e2_names.json"
    dsl = {"d1": "done", "d3_conv_go_awry": "toxicity", "d3_wiki_corpus": "power",
           "d1_neutral": "done"}
    for m, d in e2.items():
        ms = SLUG[m]
        for ds, dd in d.items():
            if ds == "retest_floor":
                for v in dd.values():
                    add(f"e2.{ms}.floor", v["flips_per_100"], src, fmt=".1f")
                for rds, v in dd.items():
                    label = dsl.get(rds, rds.replace("_", ""))
                    add(f"e2.{ms}.{label}.floor", v["flips_per_100"], src, fmt=".1f")
                continue
            for n in ("k01", "kny", "kswap", "krand"):
                p = f"e2.{ms}.{dsl[ds]}.{n}"
                add(f"{p}.auc", dd[n]["auc"], src, fmt=".2f")
                add(f"{p}.flips", dd[n]["flips_per_100_vs_kny"], src, fmt=".1f")
                add(f"{p}.effect", dd[n]["name_effect_vs_kny"], src, fmt=".3f")
                add(f"{p}.acc", dd[n]["accuracy"], src, fmt=".3f")
                if n != "kny":
                    add(f"{p}.dauc", dd[n]["delta_auc_vs_kny"], src, fmt=".2f")
                    add(f"{p}.absdauc", abs(dd[n]["delta_auc_vs_kny"]), src, fmt=".2f")
            add(f"e2.{ms}.{dsl[ds]}.n", dd["n"], src)


def collect_e2_summary(e2):
    """Largest swap flip rate of the four decoder-based heads over the three binary sets."""
    src = "results/e2_names.json"
    heads = ["kev-9b", "nimble-9b", "decider-2b", "this-that-1.0"]
    vals = [e2[m][ds]["kswap"]["flips_per_100_vs_kny"] for m in heads if m in e2
            for ds in ("d1", "d3_conv_go_awry", "d3_wiki_corpus") if ds in e2[m]]
    if vals:
        add("e2.decoderheads.kswap.maxflips", max(vals), src, fmt=".1f")
    j = e2.get("jev-1.13.0", {})
    other = [j[ds][n]["flips_per_100_vs_kny"] for ds in ("d1", "d3_conv_go_awry", "d3_wiki_corpus")
             if ds in j for n in ("k01", "krand")]
    if other:
        add("e2.jev.neutralnames.maxflips", max(other), src, fmt=".1f")


def collect_e3(e3):
    src = "results/e3_cardinality.json"
    kname = {"5": "five", "20": "twenty", "50": "fifty", "150": "all"}
    for m, d in e3.items():
        ms = SLUG[m]
        for k, v in d.items():
            if k in kname:
                add(f"e3.{ms}.{kname[k]}.acc", v["accuracy"], src, fmt=".3f")
                add(f"e3.{ms}.{kname[k]}.ece", v["ece"], src, fmt=".3f")
                add(f"e3.{ms}.{kname[k]}.meanconf", v["mean_confidence"], src, fmt=".3f")
        if "drop_5_to_150" in d:
            add(f"e3.{ms}.drop", d["drop_5_to_150"], src, fmt=".3f")
        if "hier" in d:
            h = d["hier"]
            add(f"e3.{ms}.hier.acc", h["accuracy"], src, fmt=".3f")
            add(f"e3.{ms}.hier.domacc", h["domain_accuracy"], src, fmt=".3f")
            add(f"e3.{ms}.hier.intacc", h["intent_given_gold_domain_accuracy"], src, fmt=".3f")


def collect_e5(cl):
    src = "results/cost_latency.json"
    for m, d in cl.items():
        if m not in SLUG:
            continue
        ms = SLUG[m]
        for cond, v in d.items():
            cs = cond.replace("_", "")
            add(f"e5.{ms}.{cs}.pfifty", 1000 * v["p50_s"], src, fmt=".0f")
            add(f"e5.{ms}.{cs}.pninetyfive", 1000 * v["p95_s"], src, fmt=".0f")
            if v.get("usd_per_1000_decisions") is not None:
                add(f"e5.{ms}.{cs}.usd", v["usd_per_1000_decisions"], src, fmt=".4f")
            if v.get("input_tokens_per_decision"):
                add(f"e5.{ms}.{cs}.tokens", v["input_tokens_per_decision"], src, fmt=".0f")
    add("e5.jev.spend", cl["jev_total"]["usd"], src, fmt=".2f")
    add("e5.gpuhour", cl["assumptions"]["usd_per_gpu_hour"], src, fmt=".2f")


def collect_e6(e6):
    src = "results/e6_cascade.json"
    for key, d in e6.items():
        pair, cond = key.split("|")
        f, s = pair.split(">")
        p = f"e6.{SLUG[f]}.{SLUG[s]}.{CSLUG.get(cond, cond.replace('_', ''))}"
        add(f"{p}.accfirst", d["acc_first"], src, fmt=".3f")
        add(f"{p}.accsecond", d["acc_second"], src, fmt=".3f")
        sm = d["summary"]
        add(f"{p}.bestacc", sm["best_accuracy"], src, fmt=".3f")
        add(f"{p}.bestescalated", sm["best_escalated"], src, fmt=".2f")
        if sm.get("best_cost_fraction") is not None:
            add(f"{p}.bestcostfraction", float(sm["best_cost_fraction"]), src, fmt=".2f")
        add(f"{p}.gain", 100 * (sm["best_accuracy"] - max(d["acc_first"], d["acc_second"])),
            src, fmt=".1f")
        h = d.get("heldout")
        if h:
            add(f"{p}.hoacc", h["accuracy"], src, fmt=".3f")
            add(f"{p}.hoescalated", h["escalated"], src, fmt=".2f")
            if h.get("cost_fraction") is not None:
                add(f"{p}.hocostfraction", h["cost_fraction"], src, fmt=".2f")
            add(f"{p}.hogain", 100 * h["gain"], src, fmt=".1f")
        for k in ("match_escalated", "match_cost_fraction", "retain95_escalated",
                  "retain95_cost_fraction", "retain99_escalated", "retain99_cost_fraction"):
            if sm.get(k) is not None:
                add(f"{p}.{k.replace('_', '')}", sm[k], src, fmt=".2f")


# ------------------------------------------------------------------ revision labels
#
# Everything below adds labels only. radd refuses a label that already exists, so no
# earlier label can be overwritten by the revision block.

RV_TASK = dict(CSLUG, **{"d2_k5": "dtwokfive", "d2_k20": "dtwoktwenty",
                         "d2_k50": "dtwokfifty"})
RV_ALPHA = {"1pct": "one", "5pct": "five"}
RV_REP = {"1": "one", "2": "two", "3": "three", "4": "four", "5": "five"}
RV_Q = {"q1": "qone", "q2": "qtwo", "q3": "qthree", "q4": "qfour", "q5": "qfive"}
RV_K = {"5": "five", "20": "twenty", "50": "fifty", "150": "all"}
RV_SET = {"d1": "done", "d3_conv_go_awry": "toxicity", "d3_wiki_corpus": "power"}


def radd(label, value, source, note=None, fmt=None):
    if label in N:
        raise RuntimeError(f"revision label collides with an existing label: {label}")
    if isinstance(value, float) and np.isnan(value):
        return
    add(label, value, source, note, fmt)


def _ci(label, ci, source, fmt, scale=1.0):
    if ci:
        radd(label + "lo", scale * ci[0], source, fmt=fmt)
        radd(label + "hi", scale * ci[1], source, fmt=fmt)


def collect_params_revision():
    """Parameters read from the code that sets them: the comparator's reporting and
    budget constants and the temperature grid of metrics.fit_T."""
    import inspect
    import re
    import adapters
    radd("p.comp.fullk", int(adapters.COMPARATOR_FULL_COVERAGE_MAX_K),
         "src/adapters.py COMPARATOR_FULL_COVERAGE_MAX_K", fmt="d")
    radd("p.comp.topn", int(adapters.COMPARATOR_TOP_N), "src/adapters.py COMPARATOR_TOP_N",
         fmt="d")
    sig = inspect.signature(adapters.ComparatorOpenBackend.__init__).parameters
    radd("p.comp.maxlen", int(sig["max_model_len"].default),
         "src/adapters.py ComparatorOpenBackend(max_model_len)", fmt="d")
    radd("p.comp.maxtokens", int(sig["max_tokens"].default),
         "src/adapters.py ComparatorOpenBackend(max_tokens)", fmt="d")
    m = re.search(r"np\.linspace\(np\.log\(([0-9.]+)\),\s*np\.log\(([0-9.]+)\),\s*(\d+)\)",
                  inspect.getsource(M.fit_T))
    if m is None:
        raise RuntimeError("temperature grid not found in metrics.fit_T")
    lo, hi, n = float(m.group(1)), float(m.group(2)), int(m.group(3))
    src = "src/metrics.py fit_T grid (log-spaced)"
    radd("p.tgrid.lo", lo, src, fmt=".1f")
    radd("p.tgrid.hi", int(hi) if hi == int(hi) else hi, src,
         fmt="d" if hi == int(hi) else None)
    radd("p.tgrid.n", n, src, fmt="d")


def collect_revision():
    """Labels rv.* from results/revision_stats.json (src/a09_revision_stats.py), and
    bl.*, ov.*, e3p.* from files other scripts produce, when they exist."""
    rv = load("revision_stats.json")
    if rv:
        _collect_rv(rv)
    for name, prefix in (("baselines.json", "bl"), ("clinc_overlap.json", "ov"),
                         ("e3_permutations.json", "e3p")):
        d = load(name)
        if d:
            _collect_external(d, prefix, "results/" + name)
    lb = load("laya_budget.json")
    if lb:
        _collect_laya_budget(lb)
    rp = load("render_paired.json")
    if rp:
        # rp.<done|dtwo>.<comparison>.{diff,lo,hi,p}: src/a13_render_paired.py
        src = "results/render_paired.json"
        cw = {"d1_neutral": "done", "d2_k150": "dtwo"}
        for cond, comps in rp.items():
            for comp, v in comps.items():
                p = f"rp.{cw[cond]}.{comp.replace('_', '')}"
                radd(f"{p}.diff", v["diff_points"], src, fmt=".1f")
                radd(f"{p}.lo", v["lo"], src, fmt=".1f")
                radd(f"{p}.hi", v["hi"], src, fmt=".1f")
                radd(f"{p}.p", v["p"], src, fmt=".2g")
                radd(f"{p}.acc", v["acc_a"], src, fmt=".3f")


def _collect_laya_budget(lb):
    """Labels lb.<model>.<K>.* from results/laya_budget.json (src/a11_laya_budget.py):
    the replayed Laya option-token budget on the original D2 permutation."""
    src = "results/laya_budget.json"
    kword = {"d2_k5": "five", "d2_k20": "twenty", "d2_k50": "fifty", "d2_k150": "all"}
    for model, ms in (("laya-en", "layaen"), ("laya-ml", "layaml")):
        conds = lb.get(model, {}).get("conditions", {})
        for cond, kw in kword.items():
            c = conds.get(cond)
            if not c:
                continue
            p = f"lb.{ms}.{kw}"
            add(f"{p}.opttokens", int(c["option_tokens_after_cap_median"]), src)
            add(f"{p}.head", int(c["head_max_len"]), src)
            add(f"{p}.maxlen", int(c["max_len"]), src)
            add(f"{p}.exceeds", c["share_exceeding_head_budget"], src, fmt=".2f")
            add(f"{p}.desclost", c["options_whose_description_is_lost_mean"], src, fmt=".0f")
            add(f"{p}.dropped", c["options_dropped_at_max_len_mean"], src, fmt=".0f")
            add(f"{p}.distinct", c["distinct_option_texts_seen_mean"], src, fmt=".0f")
            if "state_tokens_kept_median" in c:
                add(f"{p}.statekept", c["state_tokens_kept_median"], src, fmt=".0f")


# Expected structure of results/baselines.json, results/clinc_overlap.json and
# results/e3_permutations.json (skipped silently while absent):
#
#   {"labels": {"<suffix>": {"value": <number or string>,
#                            "fmt": "<format spec such as .3f or d, or null>",
#                            "source": "<optional provenance>", "note": "<optional>"},
#               "<suffix>": <bare number or string>, ...},
#    ... any other keys are ignored when "labels" is present ...}
#
# Each entry becomes the label <prefix>.<suffix> with prefix bl, ov or e3p. Suffixes are
# lower case, dot separated, and spell numbers as words (kfive, not k5).
#
# Two files already exist in their own structure and are read by dedicated emitters:
#   e3_permutations.json  {model: {"5"|"20"|"50"|"150": {acc_p1.., ece_p1.., acc_mean,
#                         acc_range, ece_mean, ece_range, n_p1.., n_all3, refused_p1..,
#                         same_choice_all3}}, "render_sensitivity": {cond: {type: {...}}}}
#                         -> e3p.<model>.<five|twenty|fifty|all>.<metric>, e3p.render.*
#   clinc_overlap.json    {"counts": {"<variant>/<split>": {exact, normalized, near_dup_*,
#                         n_items, ...}}, "emotion": {"items", "counts": {...}},
#                         "sources": {...splits...}} -> ov.clinc.*, ov.emotion.*, ov.size.*
# Any other file without a "labels" mapping is flattened: every numeric or string leaf at
# the key path a -> b -> c becomes <prefix>.a.b.c, each segment lower-cased and reduced
# to letters and digits, with the default number format. Null values are skipped.
def _slug(s):
    import re
    return re.sub(r"[^a-z0-9]", "", str(s).lower())


E3P_METRIC = {"acc_mean": "accmean", "acc_range": "accrange", "ece_mean": "ecemean",
              "ece_range": "ecerange", "n_all3": "nallthree", "same_choice_all3": "samechoice"}
for _i, _w in (("1", "one"), ("2", "two"), ("3", "three")):
    for _m in ("acc", "ece", "n", "refused"):
        E3P_METRIC[f"{_m}_p{_i}"] = f"{_m}p{_w}"


def _collect_e3p(d, src):
    """results/e3_permutations.json (b-series permutation check): per model and K the
    top-1 accuracy and ECE under up to three option permutations, and the
    render-sensitivity comparison. Null entries (answers not there yet) are skipped."""
    if isinstance(d.get("_check_p1_equals_e3_cardinality"), str):
        radd("e3p.check", d["_check_p1_equals_e3_cardinality"], src)
    for m, byk in d.items():
        if m not in SLUG or not isinstance(byk, dict):
            continue
        for k, v in byk.items():
            if k not in RV_K or not isinstance(v, dict):
                continue
            for key, lab in E3P_METRIC.items():
                x = v.get(key)
                if isinstance(x, bool) or not isinstance(x, (int, float)):
                    continue
                fmt = ".3f" if key.startswith(("acc", "ece", "same")) else None
                radd(f"e3p.{SLUG[m]}.{RV_K[k]}.{lab}", x, src, fmt=fmt)
    rs = d.get("render_sensitivity")
    if isinstance(rs, dict):
        for cond, byt in rs.items():
            if cond not in RV_TASK or not isinstance(byt, dict):
                continue
            for t, v in byt.items():
                if not isinstance(v, dict):
                    continue
                for key, x in v.items():
                    if isinstance(x, bool) or not isinstance(x, (int, float)):
                        continue
                    fmt = None if key.startswith("n_") else ".3f"
                    radd(f"e3p.render.{RV_TASK[cond]}.{_slug(t)}.{_slug(key)}", x, src, fmt=fmt)


OV_SOURCE = {"data_full": "full", "data_imbalanced": "imbalanced", "data_oos_plus": "oosplus",
             "data_small": "small", "hf_plus": "hfplus",
             "decider_temperature_fit_rows": "deciderfit", "split": "", "unsplit": "unsplit"}


def _ov_path(key):
    parts = key.split("/")
    head = OV_SOURCE.get(parts[0], _slug(parts[0]))
    return ".".join(p for p in [head] + [_slug(x) for x in parts[1:]] if p)


def _collect_ov(d, src):
    """results/clinc_overlap.json (b02_clinc_overlap.py): counts of D2 test texts (and
    D3 emotion items) with a matching row in each public split, by match type."""
    def counts(block, prefix):
        for key, v in block.items():
            if not isinstance(v, dict):
                continue
            p = f"{prefix}.{_ov_path(key)}"
            for mk, x in v.items():
                if isinstance(x, bool) or not isinstance(x, (int, float)):
                    continue
                radd(f"{p}.{_slug(mk)}", x, src)
    if isinstance(d.get("counts"), dict):
        counts(d["counts"], "ov.clinc")
    em = d.get("emotion")
    if isinstance(em, dict):
        if isinstance(em.get("items"), int):
            radd("ov.emotion.items", em["items"], src)
        if isinstance(em.get("counts"), dict):
            counts(em["counts"], "ov.emotion")
    for name, blk in (d.get("sources") or {}).items():
        if isinstance(blk, dict) and isinstance(blk.get("splits"), dict):
            for sp, n in blk["splits"].items():
                if isinstance(n, int):
                    radd(f"ov.size.{_ov_path(name)}.{_slug(sp)}", n, src)
    esp = ((em or {}).get("sources") or {}).get("splits")
    if isinstance(esp, dict):
        for sp, n in esp.items():
            if isinstance(n, int):
                radd(f"ov.size.emotion.{_ov_path(sp)}", n, src)


def _external_fmt(prefix, path):
    """Printed precision for the baseline labels (bl.*), matching the decision-model
    labels of the same quantity; other prefixes keep the default."""
    if prefix != "bl":
        return None
    last = path[-1]
    if last in ("acc", "acclo", "acchi", "softacc", "aurocoos", "brier", "brierscaled",
                "nll", "nllscaled", "aurc", "aurcscaled") or last.startswith("ece"):
        return ".3f"
    if last.startswith("cov5"):
        return ".2f"
    if last.startswith("latency"):
        return ".0f" if "cpu" in last or "gpu" in last and "batched" not in last else ".1f"
    if last in ("macrof1",):
        return ".3f"
    return None


def _collect_external(d, prefix, src):
    import re
    if prefix == "e3p" and "labels" not in d:
        return _collect_e3p(d, src)
    if prefix == "ov" and "labels" not in d:
        return _collect_ov(d, src)
    if isinstance(d.get("labels"), dict):
        for suf, v in d["labels"].items():
            if isinstance(v, dict):
                radd(f"{prefix}.{suf}", v.get("value"), v.get("source") or src,
                     note=v.get("note"), fmt=v.get("fmt"))
            else:
                radd(f"{prefix}.{suf}", v, src)
        return

    def walk(node, path):
        # numbers only: free text (a _doc field, a percent sign) could break numbers.tex
        if isinstance(node, dict):
            for k, v in node.items():
                if str(k).startswith("_"):
                    continue
                seg = re.sub(r"[^a-z0-9]", "", str(k).lower())
                if seg:
                    walk(v, path + [seg])
        elif isinstance(node, (int, float)) and not isinstance(node, bool) and path:
            radd(".".join([prefix] + path), node, src, fmt=_external_fmt(prefix, path))
    walk(d, [])


def _collect_rv(rv):
    src = "results/revision_stats.json"
    meta = rv.get("meta", {})
    msrc = "src/a09_revision_stats.py"
    if meta:
        radd("p.boot.reps", int(meta["replicates_boot"]), msrc + " B_BOOT", fmt="d")
        radd("p.boot.refitreps", int(meta["replicates_refit"]), msrc + " B_REFIT", fmt="d")
        radd("p.boot.pairedreps", int(meta["replicates_paired"]), msrc + " B_PAIRED", fmt="d")
        radd("p.boot.level", int(meta["level"]), msrc + " LEVEL", fmt="d")

    # A. temperature scaling per task
    A = rv.get("A_temperature_scaling", {})
    for key, d in A.get("results", {}).items():
        m, cond = key.split("|")
        p = f"rv.ts.{SLUG[m]}.{RV_TASK[cond]}"
        radd(f"{p}.n", d["n"], src)
        radd(f"{p}.ece", d["ece_shipped"], src, fmt=".3f")
        _ci(f"{p}.ece", d["ece_shipped_ci"], src, ".3f")
        if d.get("ece_raw") is not None:
            radd(f"{p}.eceraw", d["ece_raw"], src, fmt=".3f")
        radd(f"{p}.ecescaled", d["ece_scaled"], src, fmt=".3f")
        _ci(f"{p}.ecescaled", d["ece_scaled_ci_refit"], src, ".3f")
        t = d["temperatures"]
        if "crossfit_folds" in t:
            radd(f"{p}.tmin", min(t["crossfit_folds"]), src, fmt=".2f")
            radd(f"{p}.tmax", max(t["crossfit_folds"]), src, fmt=".2f")
        for ty, T in t.get("per_type_from_d1_calib", {}).items():
            radd(f"{p}.t{ty}", T, src, fmt=".2f")
    for m, d in A.get("d3_pooled", {}).items():
        p = f"rv.ts.{SLUG[m]}.dthree"
        radd(f"{p}.ece", d["ece_shipped"], src, fmt=".3f")
        if d.get("ece_raw") is not None:
            radd(f"{p}.eceraw", d["ece_raw"], src, fmt=".3f")
        radd(f"{p}.ecescaled", d["ece_scaled"], src, fmt=".3f")
        radd(f"{p}.scaledmin", d["per_task_scaled_min"], src, fmt=".3f")
        radd(f"{p}.scaledmax", d["per_task_scaled_max"], src, fmt=".3f")

    # B. selective prediction
    Bs = rv.get("B_selective_prediction", {})
    for key, d in Bs.get("insample", {}).items():
        m, cond = key.split("|")
        p = f"rv.sel.{SLUG[m]}.{RV_TASK[cond]}"
        for a, w in RV_ALPHA.items():
            radd(f"{p}.cov{w}", d[f"coverage_at_{a}"], src, fmt=".2f")
            _ci(f"{p}.cov{w}", d[f"coverage_at_{a}_ci"], src, ".2f")
        radd(f"{p}.aurc", d["aurc"], src, fmt=".3f")
        _ci(f"{p}.aurc", d["aurc_ci"], src, ".3f")
        if "auroc_in_vs_oos" in d:
            q = f"rv.sel.{SLUG[m]}.oos"
            radd(f"{q}.auroc", d["auroc_in_vs_oos"], src, fmt=".3f")
            _ci(f"{q}.auroc", d["auroc_in_vs_oos_ci"], src, ".3f")
    for key, d in Bs.get("heldout", {}).items():
        m, cond = key.split("|")
        for a, w in RV_ALPHA.items():
            h = d[a]
            p = f"rv.ho.{SLUG[m]}.{RV_TASK[cond]}.{w}"
            radd(f"{p}.cov", h["coverage"], src, fmt=".2f")
            if h["risk"] is not None:
                radd(f"{p}.risk", h["risk"], src, fmt=".3f")
            if h["risk_upper_95_one_sided_cp"] is not None:
                radd(f"{p}.riskub", h["risk_upper_95_one_sided_cp"], src, fmt=".3f")
            radd(f"{p}.accepted", h["accepted"], src)
    for m, d in Bs.get("gate", {}).items():
        p = f"rv.gate.{SLUG[m]}"
        radd(f"{p}.cov", d["coverage_in"], src, fmt=".2f")
        _ci(f"{p}.cov", d["coverage_in_ci"], src, ".2f")
        radd(f"{p}.risk", d["risk_in"], src, fmt=".3f")
        _ci(f"{p}.risk", d["risk_in_ci"], src, ".3f")
        if d.get("risk_in_upper_95_one_sided_cp") is not None:
            radd(f"{p}.riskub", d["risk_in_upper_95_one_sided_cp"], src, fmt=".3f")
        radd(f"{p}.far", d["oos_false_acceptance"], src, fmt=".3f")
        _ci(f"{p}.far", d["oos_false_acceptance_ci"], src, ".3f")
        if d.get("deployable_threshold") is not None:
            radd(f"{p}.thr", d["deployable_threshold"], src, fmt=".2f")

    # C. raw arm availability
    for m, d in rv.get("C_raw_arm", {}).items():
        radd(f"rv.raw.{SLUG[m]}.available", "yes" if d["raw_available"] else "no", src,
             note=d["reason"])

    # D. cascades
    Dc = rv.get("D_cascades", {})

    def casc(p, d, esc_key):
        radd(f"{p}.n", d["n"], src)
        radd(f"{p}.acc", d["accuracy"], src, fmt=".3f")
        radd(f"{p}.gain", 100 * d["gain"], src, fmt=".1f")
        radd(f"{p}.gaindec", d["gain_decisions"], src, fmt="d")
        radd(f"{p}.gainp", d["p_gain_le_0"], src, fmt=".2g")
        radd(f"{p}.esc", d[esc_key], src, fmt=".2f")
        if d.get("escalated_decisions") is not None:
            radd(f"{p}.escdec", d["escalated_decisions"], src, fmt=".2f")
        if d.get("cost_fraction") is not None:
            radd(f"{p}.costfrac", d["cost_fraction"], src, fmt=".2f")
        ci = d.get("ci", {})
        _ci(f"{p}.acc", ci.get("accuracy"), src, ".3f")
        _ci(f"{p}.gain", ci.get("gain"), src, ".1f", scale=100)
        _ci(f"{p}.esc", ci.get(esc_key), src, ".2f")
        _ci(f"{p}.costfrac", ci.get("cost_fraction"), src, ".2f")
        if ci.get("gain_decisions"):
            radd(f"{p}.gaindeclo", int(round(ci["gain_decisions"][0])), src, fmt="d")
            radd(f"{p}.gaindechi", int(round(ci["gain_decisions"][1])), src, fmt="d")
        tau = d.get("deployable_tau", d.get("tau"))
        if tau is not None:
            radd(f"{p}.tau", tau, src, fmt=".2f")
        radd(f"{p}.pfifty", 1000 * d["latency"]["p50_s"], src, fmt=".0f")
        radd(f"{p}.pninetyfive", 1000 * d["latency"]["p95_s"], src, fmt=".0f")

    for key, d in Dc.get("pairs", {}).items():
        pair, cond = key.split("|")
        f, s = pair.split(">")
        p = f"rv.cas.{SLUG[f]}.{SLUG[s]}.{RV_TASK[cond]}"
        radd(f"{p}.kone", d["k1_usd_per_1000"], src, fmt=".4f")
        radd(f"{p}.ktwo", d["k2_usd_per_1000"], src, fmt=".4f")
        casc(p, d["decision_level"], "escalated")
        if "request_level_replace_all" in d:
            casc(f"rv.cas.{SLUG[f]}.{SLUG[s]}.donerequest", d["request_level_replace_all"],
                 "escalated_requests")
            casc(f"rv.cas.{SLUG[f]}.{SLUG[s]}.donerequestlow", d["request_level_replace_low"],
                 "escalated_requests")
    for key, d in Dc.get("cost_sensitivity", {}).items():
        m, cond = key.split("|")
        p = f"rv.cost.{SLUG[m]}.{RV_TASK[cond]}"
        if d.get("breakeven_usd_per_gpu_hour") is not None:
            radd(f"{p}.breakeven", d["breakeven_usd_per_gpu_hour"], src, fmt=".2f")
        u = d["usd_per_1000_at_utilization"]
        radd(f"{p}.usdquarter", u["0.25"], src, fmt=".4f")
        radd(f"{p}.usdhalf", u["0.5"], src, fmt=".4f")
        radd(f"{p}.usdfull", u["1.0"], src, fmt=".4f")

    # E. paired comparisons and service variability
    E = rv.get("E_paired", {})
    for cond, fam in E.get("families", {}).items():
        for m, d in fam.items():
            p = f"rv.pd.{SLUG[m]}.{RV_TASK[cond]}"
            radd(f"{p}.diff", 100 * d["diff"], src, fmt=".1f")
            _ci(f"{p}.diff", d["diff_ci"], src, ".1f", scale=100)
            radd(f"{p}.p", d["p_boot"], src, fmt=".2g")
            radd(f"{p}.holm", d["p_holm"], src, fmt=".2g")
            radd(f"{p}.mcnemar", d["mcnemar_p"], src, fmt=".2g",
                 note="ignores clustering" if d["mcnemar_ignores_clustering"] else None)
            radd(f"{p}.mcnemarholm", d["mcnemar_p_holm"], src, fmt=".2g")
    for cond, d in E.get("jev_reps", {}).items():
        p = f"rv.rep.jev.{RV_TASK[cond]}"
        for r, v in d["reps"].items():
            radd(f"{p}.{RV_REP[r]}.acc", v["accuracy"], src, fmt=".3f")
            radd(f"{p}.{RV_REP[r]}.ece", v["ece"], src, fmt=".3f")
        radd(f"{p}.accmin", d["accuracy_range"][0], src, fmt=".3f")
        radd(f"{p}.accmax", d["accuracy_range"][1], src, fmt=".3f")
        radd(f"{p}.accspread", 100 * d["accuracy_spread"], src, fmt=".1f")
        radd(f"{p}.ecemin", d["ece_range"][0], src, fmt=".3f")
        radd(f"{p}.ecemax", d["ece_range"][1], src, fmt=".3f")

    # F. option names
    for key, d in rv.get("F_option_names", {}).get("results", {}).items():
        m, ds = key.split("|")
        p = f"rv.nm.{SLUG[m]}.{RV_SET[ds]}"
        for n in ("k01", "krand", "kswap"):
            v = d[n]
            radd(f"{p}.{n}.flips", v["flips_per_100"], src, fmt=".1f")
            _ci(f"{p}.{n}.flips", v["flips_ci"], src, ".1f")
            radd(f"{p}.{n}.dauc", v["delta_auc"], src, fmt=".2f")
            _ci(f"{p}.{n}.dauc", v["delta_auc_ci"], src, ".2f")
        fl = d["floor"]
        radd(f"{p}.floormeasured", "yes" if fl["measured"] else "no", src)
        if fl["measured"] and fl.get("flips_per_100_rep1_vs_rep2") is not None:
            radd(f"{p}.floor", fl["flips_per_100_rep1_vs_rep2"], src, fmt=".1f")

    # G. failures
    G = rv.get("G_failures", {})
    tot = {"answered": 0, "errors": 0, "refusals": 0}
    for m, d in G.get("by_model", {}).items():
        p = f"rv.fail.{SLUG[m]}"
        for k in ("files", "answered", "errors", "refusals", "answered_questions"):
            radd(f"{p}.{k.replace('_', '')}", d.get(k, 0), src)
        for k in ("answered", "errors", "refusals"):
            tot[k] += d.get(k, 0)
        if m == "comparator-open":
            radd(f"{p}.truncated", d.get("truncated", 0), src)
            radd(f"{p}.renormalized", d.get("verbalized_not_summing_to_one", 0), src)
            radd(f"{p}.percentscale", d.get("verbalized_on_percent_scale", 0), src)
    for k, v in tot.items():
        radd(f"rv.fail.all.{k}", v, src)
    for key, d in G.get("files", {}).items():
        m, cond, rep = key.split("|")
        if d["errors"] and rep == "rep1" and cond in RV_TASK:
            radd(f"rv.fail.{SLUG[m]}.{RV_TASK[cond]}.errors", d["errors"], src)
            radd(f"rv.fail.{SLUG[m]}.{RV_TASK[cond]}.refusals", d["refusals"], src)
    radd("rv.fail.distinct", len(G.get("distinct_errors", {})), src)

    # H. cardinality diagnostics
    H = rv.get("H_cardinality", {})
    for key, d in H.get("accuracy_by_position", {}).items():
        m, cond = key.split("|")
        kw = RV_K[cond.split("_k")[1]]
        for q, w in RV_Q.items():
            if d.get(q) and d[q]["accuracy"] is not None:
                radd(f"rv.card.{SLUG[m]}.{kw}.{w}.acc", d[q]["accuracy"], src, fmt=".3f")
    for key, d in H.get("predicted_position", {}).items():
        m, cond = key.split("|")
        kw = RV_K[cond.split("_k")[1]]
        radd(f"rv.card.{SLUG[m]}.{kw}.predfirst", d["first_option"], src, fmt=".3f")
        if m.startswith("laya"):
            for q, w in RV_Q.items():
                radd(f"rv.card.{SLUG[m]}.{kw}.pred{w}", d[q], src, fmt=".3f")
    for k, d in H.get("chars", {}).items():
        p = f"rv.card.chars.{RV_K[k]}"
        radd(f"{p}.mean", d["rendered_mean"], src, fmt=".0f")
        radd(f"{p}.max", d["rendered_max"], src, fmt="d")
        radd(f"{p}.textmean", d["text_only_mean"], src, fmt=".0f")


def collect_params():
    """Protocol constants, each tied to the script that sets it, and dataset facts."""
    s00 = "src/s00_freeze_inputs.py"
    add("p.seed", C.SEED, "src/common.py SEED", fmt="d")
    add("p.bins", 10, "src/metrics.py ece(bins=10)")
    add("p.folds", 5, "src/metrics.py crossfit_T(folds=5)")
    add("p.bootreps", 1000, "src/metrics.py cluster_boot(reps=1000)", fmt="d")
    add("p.eceboot", 400, "src/a01_e1_main.py ECE interval reps", fmt="d")
    add("p.jevreps", 3, "harness runs, rep 1 to 3 for every Jev condition")
    add("p.jevretestreps", 5, "harness runs, rep 4 and 5 on the retest subset")
    add("p.jevconcurrency", 10, "src/harness.py JevBackend.concurrency")
    add("p.riskone", 1, "coverage at 1 percent risk (metrics.coverage_at_risk)")
    add("p.riskfive", 5, "coverage at 5 percent risk (metrics.coverage_at_risk)")
    add("p.kfive", 5, s00)
    add("p.ktwenty", 20, s00)
    add("p.kfifty", 50, s00)
    add("p.kall", 150, s00)
    add("p.perintent", 4, s00 + " (4 test utterances per intent)")
    add("p.oos", 200, s00 + " (out-of-scope test utterances)")
    add("p.domains", 10, "clinc/oos-eval domains.json")
    add("p.intentsperdomain", 15, "clinc/oos-eval domains.json")
    add("p.calibperworkflow", 75, s00 + " (training states per workflow)")
    add("p.workflows", 4, "typed-decisions card")
    add("p.questionsperstate", 5, "typed-decisions card")
    add("p.randlen", 5, s00 + " naming_pair (random five-letter strings)")
    add("p.d3tasks", 4, "shared/data/d3/README.md")
    add("p.price", C.PRICE_PER_MTOK, "docs.typesafe.ai pricing, accessed 2026-09-24", fmt=".3f")
    add("p.conf", 0.9, "high-confidence threshold used in a01", fmt=".1f")
    add("p.anchor.jev.acc", 0.727, "typed-decisions dataset card leaderboard, accessed 2026-09-24",
        fmt=".3f")
    add("p.anchor.jev.softacc", 0.580, "Laya model card typed-decisions table (published Jev)",
        fmt=".3f")
    add("p.anchor.jev.brier", 0.148, "typed-decisions dataset card leaderboard", fmt=".3f")
    add("p.anchor.ceiling", 0.735, "typed-decisions card, teacher self-agreement", fmt=".3f")
    add("p.pninetyfive", 95, "latency percentile reported in a04_e5_cost_latency.py")
    add("p.d1kmin", 2, "typed-decisions questions: noul has two options")
    add("p.d1kmax", 5, "typed-decisions questions: widest choice and score have five")
    add("p.anchor.prior", 0.470, "typed-decisions card leaderboard, prior that ignores the input", fmt=".3f")
    add("p.anchor.laya.acc", 0.362, "Laya model card, typed-decisions table, accessed 2026-09-24",
        fmt=".3f")
    add("p.anchor.package.tox", 0.572, "Ibrahim and Zaki package analysis/cell_metrics.csv, commit 311956c", fmt=".3f")
    add("p.anchor.package.pwr", 0.610, "Ibrahim and Zaki package analysis/cell_metrics.csv, commit 311956c", fmt=".3f")
    add("p.anchor.package.emo", 0.494, "Ibrahim and Zaki package analysis/cell_metrics.csv, commit 311956c", fmt=".3f")
    add("p.gpuhourcost", 4.8 * 9.99 / 100, "Colab Pro 100 units for 9.99 USD, L4 4.8 units per hour (assumption)", fmt=".2f")

    # Model facts (§4), label prefix m.<slug>.<fact>. Parameter counts and context
    # budgets are copied verbatim from each model's own card; served temperatures for
    # Kev and decider are the values the checkpoint itself carries and applies at
    # inference, not the harness's choice.
    add("m.laya.en.params", "421M", "convaiinnovations/laya card, Architecture section (421M total)")
    add("m.laya.ml.params", "322M",
        "convaiinnovations/laya-multilingual card, Architecture section (322M total)")
    add("m.laya.en.context", 512,
        "convaiinnovations/laya card (512 tokens per question, head_max_len=192)")
    add("m.laya.ml.context", 1024,
        "convaiinnovations/laya-multilingual card (1024 tokens per question)")
    add("m.laya.ml.contextmax", 8192,
        "convaiinnovations/laya-multilingual card (max_len=8192 for long documents)")
    add("m.laya.temp", 1.0,
        "src/adapters.py LayaBackend (no shipped temperature; the harness applies none)",
        fmt=".1f")
    add("m.kev.lorarank", 16, "jaredpalmer/kev-0.8b and kev-9b cards (LoRA adapter, r=16)")
    add("m.kev08b.temp", 2.35,
        "src/adapters.py KevBackend, read from head.pt on 2026-09-24 "
        "(the jaredpalmer/kev-0.8b card states 2.41)", fmt=".2f")
    add("m.kev9b.temp", 2.30, "jaredpalmer/kev-9b card (built-in temperature, head.pt)",
        fmt=".2f")
    add("m.decider.temp", 1.30, "Mapika/decider-2b card and decider_config.json", fmt=".2f")
    add("m.decider.baseparams", "1.9B",
        "Mapika/decider-2b card (base model Qwen/Qwen3.5-2B-Base, 1.9B parameters)")
    add("m.decider.context", 32,
        "Mapika/decider-2b card, Usage section (state and questions up to 32k tokens)")
    add("m.thisthat.params", "1.88B", "flock-io/this-that-model-1.0 card")
    add("m.thisthat.temp", 1.0,
        "src/adapters.py ThisThatBackend (decide()'s own default temperature is served as is)",
        fmt=".1f")
    add("m.nimble.temp", 1.0,
        "bespokelabs/Bespoke-Nimble-9B card, 2026-09-24 update (T=1.0, main branch)",
        fmt=".1f")
    add("m.nimble.context", 8192, "bespokelabs/Bespoke-Nimble-9B card (8,192-token context limit)")
    add("m.comparator.quantbits", 4,
        "gaunernst/gemma-3-27b-it-int4-awq (AWQ, group_size=32, 4-bit weights)")
    add("m.comparator.temp", 0.0,
        "src/adapters.py ComparatorOpenBackend (greedy decoding, served_temperature=0.0)",
        fmt=".1f")

    # Dataset facts (§5), label prefix d.<dataset>.<fact>.
    add("d.d1.license", "Apache-2.0", "LocalLLaMA/typed-decisions card")
    add("d.d2.license", "CC BY 3.0",
        "github.com/clinc/oos-eval LICENSE, accessed 2026-09-24")
    add("d.d3convgoawry.license", "unstated",
        "shared/data/d3/README.md (conv_go_awry; no corpus-level license statement found; "
        "underlying text is Wikipedia, CC BY-SA)")
    add("d.d3wikicorpus.license", "CC BY-SA 4.0", "shared/data/d3/README.md (wiki_corpus)")
    add("d.d3emotion.license", "research use only",
        "shared/data/d3/README.md (emotion; dair-ai/emotion card states "
        "\"for educational and research purposes only\")")
    add("d.d3wikipoliteness.license", "CC BY 4.0",
        "shared/data/d3/README.md (wiki_politeness)")
    add("d.d3convgoawry.k", 2, "shared/data/d3/README.md (conv_go_awry, binary)")
    add("d.d3wikicorpus.k", 2, "shared/data/d3/README.md (wiki_corpus, binary)")
    add("d.d3emotion.k", 6, "shared/data/d3/README.md (emotion, six-class)")
    add("d.d3wikipoliteness.k", 3, "shared/data/d3/README.md (wiki_politeness, three-class)")


def collect():
    man =json.load(open(os.path.join(C.INPUTS, "manifest.json"), encoding="utf-8"))
    src = "colab/inputs/manifest.json"
    for cond, v in man.items():
        if cond.startswith("_"):
            continue
        add(f"n.{cond.replace('_', '')}.decisions", v["decisions"], src)
        add(f"n.{cond.replace('_', '')}.requests", v["requests"], src)
    add("n.retest.states", len(man["_retest_subset"]["item_ids"]), src)
    collect_params()
    # prior-study numbers, from the graded ledger (shared/ledger/ledger.csv), each
    # with its row id and supporting excerpt as the source; values kept as extracted
    import csv
    lp = os.path.join(C.ROOT, "ledger", "ledger.csv")
    if os.path.exists(lp):
        for r in csv.DictReader(open(lp, encoding="utf-8")):
            k, v = r.get("value_key"), (r.get("value") or "").strip()
            if not k or not v:
                continue
            v = "0" + v if v.startswith(".") else v
            v = tidy_decimal(v)
            add(f"lit.{k}", v, f"ledger {r['row_id']}: {r['excerpt'][:200]}")
            cv = (r.get("comparator_value") or "").strip()
            try:
                float(cv)
                add(f"lit.{k}.cmp", tidy_decimal("0" + cv if cv.startswith(".") else cv),
                    f"ledger {r['row_id']} comparator value ({r.get('comparator', '')[:80]})")
            except ValueError:
                pass
    ex = load("exposure.json")
    if ex:
        src = "results/exposure.json"
        add("x.emotion.seen", ex["emotion_items_in_dair_train"], src)
        add("x.emotion.unseen", ex["emotion_items"] - ex["emotion_items_in_dair_train"], src)
        for m, v in ex["by_model"].items():
            if m in SLUG:
                add(f"x.{SLUG[m]}.emotion.accunseen", v["acc_unseen"], src, fmt=".3f")
        if "nimble_train_overlap" in ex:
            add("x.nimble.overlap", sum(ex["nimble_train_overlap"].values()), src)
    pr = load("paired.json")
    if pr:
        src = "results/paired.json"
        for key, v in pr.items():
            m, cond = key.split("|")
            cs = "dthree" if cond == "d3_pooled" else CSLUG[cond]
            p = f"pd.{SLUG[m]}.{cs}"
            add(f"{p}.diff", 100 * v["diff"], src, fmt=".1f")
            add(f"{p}.difflo", 100 * v["diff_ci"][0], src, fmt=".1f")
            add(f"{p}.diffhi", 100 * v["diff_ci"][1], src, fmt=".1f")
            add(f"{p}.absdiff", abs(100 * v["diff"]), src, fmt=".1f")
            add(f"{p}.p", v["mcnemar_p"], src, fmt=".2g")
    rt = load("retest.json")
    if rt:
        src = "results/retest.json"
        for m, v in rt.items():
            if m in SLUG and "_overall" in v:
                add(f"rt.{SLUG[m]}.medianflip", 100 * v["_overall"]["median_flip_rate"], src,
                    fmt=".1f")
                add(f"rt.{SLUG[m]}.maxflip", 100 * v["_overall"]["max_flip_rate"], src, fmt=".1f")
    for name, fn in (("e1_main.json", collect_e1), ("e2_names.json", collect_e2), ("e2_names.json", collect_e2_summary),
                     ("e3_cardinality.json", collect_e3), ("cost_latency.json", collect_e5),
                     ("e6_cascade.json", collect_e6)):
        d = load(name)
        if d:
            fn(d)
    add("model.version", C.MODEL, "pinned in every API call and recorded per record")
    add("cutoff.date", "24 September 2026", "shared/ledger/PROTOCOL.md")
    collect_params_revision()
    collect_revision()


def emit_tex():
    lines = [r"% Generated by shared/src/collect_numbers.py. Do not edit by hand.",
             r"\makeatletter",
             r"\newcommand{\num}[1]{%",
             r"  \expandafter\ifx\csname cdnum@#1\endcsname\relax",
             r"    \GenericError{}{MISSING NUMBER: #1}{}{}\textbf{??}%",
             r"  \else\csname cdnum@#1\endcsname\fi}",
             r"\makeatother"]
    for label, rec in sorted(N.items()):
        val = fmt_value(rec["value"], rec["fmt"])
        if val.startswith("-") and val[1:2].isdigit():
            val = r"\ensuremath{-}" + val[1:]          # a true minus sign in print
        lines.append(r"\expandafter\def\csname cdnum@%s\endcsname{%s}" % (label, val))
    path = os.path.join(os.path.dirname(C.ROOT), "benchmark", "manuscript", "numbers.tex")
    eaai = os.path.join(os.path.dirname(C.ROOT), "benchmark", "eaai", "manuscript", "numbers.tex")
    for p in (path, eaai):
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w", encoding="utf-8") as fh:
            fh.write("\n".join(lines) + "\n")
    return path


def run():
    collect()
    C.dump(N, "numbers.json")
    p = emit_tex()
    print(f"collected {len(N)} numbers")
    print(f"  wrote results/numbers.json and {p}")
    missing = [k for k, v in N.items() if v["value"] is None]
    if missing:
        print(f"  WARNING: {len(missing)} labels have a null value: {missing[:8]}")


if __name__ == "__main__":
    run()
