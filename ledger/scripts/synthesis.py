"""Evidence synthesis for the survey (section 7): regularities R1 to R3, accuracy gap, cost and speed ratios, vendor claims.

Deterministic. Reads
    shared/ledger/ledger.csv                 every number
    shared/ledger/synthesis_selection.csv    which rows enter which analysis, in which role, and how the
                                             number is read from the row (hand curated, one reason per row)
    shared/ledger/rob.csv                    risk-of-bias grades
    shared/references/web/vendor_facts.json  vendor claim values (f06 and t05 only, never synthesis.json)
    shared/references/web/ts_launch_blog.md  Pareto-frontier claim wording
and writes
    shared/ledger/synthesis.json
    shared/ledger/synthesis_tables/{f04_calibration,f05_cascade,f06_claims,t05_claims}.csv

No number is typed here. Each value comes from a ledger row, read from the column named in the selection
file (value, comparator_value, cost_or_latency, excerpt, n), optionally through a regular expression that must
match exactly once, and combined with a second number by one of a fixed set of expressions.

Statistics. Rows are first reduced to one value per independent study cluster (the median of that cluster's
estimate rows). li2026fast and li2026replacing come from the same group and testbed and form one cluster.
Each analysis reports the number of clusters and rows, the median, minimum and maximum over clusters, and,
where there are at least three clusters and the estimand is poolable, a percentile bootstrap interval of the
median over clusters (10,000 resamples, Python random.Random seed 11, a fresh generator per interval, percentiles by linear interpolation).
Calibration error is never pooled across binning schemes or estimands: R2 reports ranges by binning scheme.
"""
import csv
import json
import math
import os
import re
import sys
from collections import OrderedDict, defaultdict

import random
import statistics

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as K

SEL = os.path.join(K.LEDGER, "synthesis_selection.csv")
LEDGER_CSV = os.path.join(K.LEDGER, "ledger.csv")
ROB = os.path.join(K.LEDGER, "rob.csv")
VENDOR = os.path.join(K.REFS, "web", "vendor_facts.json")
LAUNCH = os.path.join(K.REFS, "web", "ts_launch_blog.md")
OUT_JSON = os.path.join(K.LEDGER, "synthesis.json")
OUT_TAB = os.path.join(K.LEDGER, "synthesis_tables")
SRC = "shared/ledger/synthesis.json"

N_BOOT = 10000
SEED = 11
CLUSTER = {"li2026fast": "li2026fast+li2026replacing", "li2026replacing": "li2026fast+li2026replacing"}
ACC_GROUPS = ("accuracy", "macroF1", "F1", "score")      # points on a 0-100 accuracy-type scale

EXPR = {
    "a": lambda a, b: a, "-a": lambda a, b: -a, "a-b": lambda a, b: a - b, "b-a": lambda a, b: b - a,
    "a/b": lambda a, b: a / b, "b/a": lambda a, b: b / a, "a/100": lambda a, b: a / 100,
    "1-a/100": lambda a, b: 1 - a / 100, "-100*a": lambda a, b: -100 * a,
    "100*(a-b)": lambda a, b: 100 * (a - b), "100*(b-a)": lambda a, b: 100 * (b - a),
    "1/(1-a/100)": lambda a, b: 1 / (1 - a / 100),
}
NUM = re.compile(r"^\s*([+-]?\d*\.?\d+)\s*$")
FRAC = re.compile(r"^\s*(\d+)\s*/\s*(\d+)\s*$")


# ---------------------------------------------------------------- reading
def load_csv(path):
    with open(path, encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


LED = {r["row_id"]: r for r in load_csv(LEDGER_CSV)}
ROBD = {r["study_key"]: r for r in load_csv(ROB)}


def num(text, pattern, where):
    text = text or ""
    if pattern:
        hits = re.findall(pattern, text)
        if len(hits) != 1:
            sys.exit(f"{where}: pattern {pattern!r} matched {len(hits)} times in {text!r}")
        return float(hits[0])
    m = NUM.match(text)
    if m:
        return float(m.group(1))
    m = FRAC.match(text)
    if m:
        return 100.0 * int(m.group(1)) / int(m.group(2))
    sys.exit(f"{where}: cannot read a number from {text!r} without a pattern")


def cluster_of(study):
    return CLUSTER.get(study, study)


def read_selection():
    recs = []
    for i, s in enumerate(load_csv(SEL), start=2):
        if s["include"].strip().lower() != "yes":
            recs.append(dict(s, included=False))
            continue
        where = f"selection line {i} ({s['analysis']} {s['row_id']})"
        row = LED.get(s["row_id"])
        if row is None:
            sys.exit(f"{where}: row not in ledger")
        a_field = s["a_field"] or "value"
        a = num(row[a_field], s["a_pattern"], where)
        b = None
        brow = LED[s["b_row"]] if s["b_row"] else row
        if s["b_field"]:
            b = num(brow[s["b_field"]], s["b_pattern"], where)
        expr = s["expr"] or "a"
        if expr not in EXPR:
            sys.exit(f"{where}: unknown expression {expr}")
        val = EXPR[expr](a, b)
        model = row["comparator"] if a_field == "comparator_value" else row["model"]
        study = row["study_key"]
        rob = ROBD.get(study, {})
        rows_used = [s["row_id"]] + ([s["b_row"]] if s["b_row"] and s["b_row"] != s["row_id"] else [])
        recs.append(dict(
            s, included=True, a=a, b=b, val=val, study=study, cluster=cluster_of(study), model=model,
            task_family=row["task_family"], n=row["n"], metric=row["metric"],
            ref=s["ref_override"] or row["reference_label_type"],
            value_key=row["value_key"], b_value_key=brow["value_key"] if s["b_row"] else "",
            rob=rob.get("overall", ""), d4=rob.get("domain4_rating", ""), role_ev=rob.get("evidence_role", ""),
            post_hoc_a=row["post_hoc_calibration"], post_hoc_b=brow["post_hoc_calibration"],
            rows_used=";".join(rows_used),
            cmp_name=row["model"] if "jev" not in row["model"].lower() else row["comparator"],
            rob_cost=cost_latency_grade(rob)))
    return recs


def cost_latency_grade(rob):
    """rob_summary.md exempts cost and latency estimates from D5, and D1 (reference labels) does not apply to
    them; the mechanical overall rule is re-applied to D2 to D4 only."""
    if not rob:
        return ""
    d = [rob[f"domain{i}_rating"] for i in (2, 3, 4)]
    if d.count("high") >= 2:
        return "high"
    if "high" not in d and d.count("unclear") <= 1:
        return "low"
    return "some_concerns"


# ---------------------------------------------------------------- statistics
def median(xs):
    return float(statistics.median(xs))


def percentile(sorted_xs, q):
    """Linear interpolation between order statistics (the numpy default)."""
    pos = (len(sorted_xs) - 1) * q / 100.0
    lo = int(math.floor(pos))
    hi = min(lo + 1, len(sorted_xs) - 1)
    return sorted_xs[lo] + (sorted_xs[hi] - sorted_xs[lo]) * (pos - lo)


def boot_ci(values):
    """Percentile bootstrap of the median over clusters; a fresh random.Random(SEED) per call."""
    vals = [float(v) for v in values]
    rng = random.Random(SEED)
    k = len(vals)
    meds = sorted(median([vals[rng.randrange(k)] for _ in range(k)]) for _ in range(N_BOOT))
    return percentile(meds, 2.5), percentile(meds, 97.5)


def by_cluster(recs):
    d = defaultdict(list)
    for r in recs:
        d[r["cluster"]].append(r["val"])
    return OrderedDict((c, median(v)) for c, v in sorted(d.items()))


def summarize(recs, poolable=True):
    cl = by_cluster(recs)
    vals = list(cl.values())
    out = dict(n_studies=len(cl), n_rows=len(recs), clusters=cl)
    if not vals:
        return out
    lo_c = min(cl, key=cl.get)
    hi_c = max(cl, key=cl.get)
    out.update(min=min(vals), max=max(vals), min_study=lo_c, max_study=hi_c, median=median(vals))
    if poolable and len(vals) >= 3:
        out["ci"] = boot_ci(vals)
    return out


# ---------------------------------------------------------------- formatting
def sig2(x):
    if x == 0:
        return "0"
    d = 2 - int(math.floor(math.log10(abs(x)))) - 1
    r = round(x, d)
    if d <= 0:
        return f"{int(round(r)):,}"
    return f"{r:.{d}f}"


FMT = {
    "ece": lambda x: f"{x:.3f}",
    "pp": lambda x: f"{x:.1f}",
    "ratio": sig2,
    "tau": lambda x: f"{x:.3f}",
    "int": lambda x: f"{int(round(x))}",
}

VALUES = OrderedDict()


def put(key, text, note):
    if not re.fullmatch(r"[A-Za-z0-9]+", key):
        sys.exit(f"bad synthesis key {key}")
    k = "syn." + key
    if k in VALUES:
        sys.exit(f"duplicate synthesis key {k}")
    VALUES[k] = {"text": text, "source": SRC, "note": note}


def put_summary(prefix, summ, kind, note, unit_note=""):
    f = FMT[kind]
    put(prefix + "NStudies", str(summ["n_studies"]), f"{note}: independent study clusters")
    put(prefix + "NRows", str(summ["n_rows"]), f"{note}: ledger rows (selection estimate rows)")
    if "median" not in summ:
        return
    put(prefix + "Min", f(summ["min"]), f"{note}: minimum over clusters ({summ['min_study']}){unit_note}")
    put(prefix + "Max", f(summ["max"]), f"{note}: maximum over clusters ({summ['max_study']}){unit_note}")
    put(prefix + "MinStudy", summ["min_study"], f"{note}: cluster with the minimum")
    put(prefix + "MaxStudy", summ["max_study"], f"{note}: cluster with the maximum")
    if "ci" in summ:
        put(prefix + "Median", f(summ["median"]), f"{note}: median over clusters{unit_note}")
        lo, hi = summ["ci"]
        extra = " With exactly 3 clusters the percentile interval is close to the minimum-maximum range." \
            if summ["n_studies"] == 3 else ""
        put(prefix + "CiLo", f(lo), f"{note}: 2.5th percentile of the bootstrap median over clusters "
                                    f"({N_BOOT} resamples, seed {SEED}).{extra}")
        put(prefix + "CiHi", f(hi), f"{note}: 97.5th percentile of the bootstrap median over clusters "
                                    f"({N_BOOT} resamples, seed {SEED}).{extra}")


def camel(s):
    return s[0].upper() + s[1:]


# ---------------------------------------------------------------- analyses
def sel(recs, analysis, role=None, subset=None, groups=None):
    out = [r for r in recs if r["included"] and r["analysis"] == analysis]
    if role:
        out = [r for r in out if r["role"] in (role if isinstance(role, tuple) else (role,))]
    if subset is not None:
        out = [r for r in out if r["subset"] in (subset if isinstance(subset, tuple) else (subset,))]
    if groups:
        out = [r for r in out if r["group"] in groups]
    return out


def rec(recs, analysis, record):
    hits = [r for r in recs if r["included"] and r["analysis"] == analysis and r["record"] == record]
    if len(hits) != 1:
        sys.exit(f"expected one record {analysis}/{record}, found {len(hits)}")
    return hits[0]


def r1(recs):
    est = sel(recs, "r1Gap", "estimate", groups=ACC_GROUPS)
    s = summarize(est)
    put_summary("r1Gap", s, "pp", "R1 best open model minus Jev on the same items, accuracy-type points "
                                 "(accuracy, macro-F1, leaderboard score), study value = median of its rows",
                " (points; positive means the open model is ahead)")
    absv = {c: abs(v) for c, v in s["clusters"].items()}
    sa = dict(n_studies=len(absv), n_rows=len(est), clusters=absv, median=median(list(absv.values())),
              min=min(absv.values()), max=max(absv.values()), min_study=min(absv, key=absv.get),
              max_study=max(absv, key=absv.get), ci=boot_ci(list(absv.values())))
    put("r1AbsGapMedian", FMT["pp"](sa["median"]), "R1 median over clusters of the absolute best-open-minus-Jev gap (points)")
    put("r1AbsGapCiLo", FMT["pp"](sa["ci"][0]), "R1 absolute gap, bootstrap 2.5th percentile over clusters")
    put("r1AbsGapCiHi", FMT["pp"](sa["ci"][1]), "R1 absolute gap, bootstrap 97.5th percentile over clusters")
    ahead = [c for c, v in s["clusters"].items() if v > 0]
    put("r1OpenAheadCount", str(len(ahead)), "R1 clusters where the best open model is ahead of Jev (" + ", ".join(ahead) + ")")
    put("r1OpenBehindCount", str(len(s["clusters"]) - len(ahead)), "R1 clusters where Jev is ahead or tied")
    # tuning parity (RoB D4) strata
    for lab, want in (("Parity", ("low",)), ("SelfReport", ("high", "unclear"))):
        sub = [r for r in est if r["d4"] in want]
        ss = summarize(sub, poolable=False)
        put(f"r1Gap{lab}NStudies", str(ss["n_studies"]), f"R1 clusters with RoB D4 {'/'.join(want)}")
        if "median" in ss:
            put(f"r1Gap{lab}Min", FMT["pp"](ss["min"]), f"R1 D4 {'/'.join(want)} minimum gap ({ss['min_study']})")
            put(f"r1Gap{lab}Max", FMT["pp"](ss["max"]), f"R1 D4 {'/'.join(want)} maximum gap ({ss['max_study']})")
    # reference-label strata (study values)
    for lab, test in (("HumanRef", lambda r: r["ref"].startswith("human")),
                      ("TaskOutcomeRef", lambda r: r["ref"] == "task_outcome"),
                      ("ModelOrSyntheticRef", lambda r: not r["ref"].startswith("human") and r["ref"] != "task_outcome")):
        sub = [r for r in est if test(r)]
        ss = summarize(sub, poolable=False)
        put(f"r1Gap{lab}NStudies", str(ss["n_studies"]), f"R1 clusters with {lab} rows")
        if "median" in ss:
            put(f"r1Gap{lab}Min", FMT["pp"](ss["min"]), f"R1 {lab} minimum study gap ({ss['min_study']})")
            put(f"r1Gap{lab}Max", FMT["pp"](ss["max"]), f"R1 {lab} maximum study gap ({ss['max_study']})")
    for r in sel(recs, "r1Gap") + sel(recs, "r1Readout"):
        kind = "pp"
        put(("r1Gap" if r["analysis"] == "r1Gap" else "r1Readout") + camel(r["record"]), FMT[kind](r["val"]),
            f"{r['study']} {r['model']} ({r['group']} points; ref {r['ref']}; RoB {r['rob']}; role {r['role']}); "
            f"ledger {r['rows_used']}")
    return s


def r2(recs):
    jev = sel(recs, "r2JevEce", "estimate")
    s = summarize(jev, poolable=False)
    put_summary("r2JevEce", s, "ece", "R2 Jev raw ECE, one value per study cluster across binning schemes "
                                      "(range only; not pooled because binning and estimands differ)")
    for g in sorted({r["group"] for r in jev}):
        sub = [r for r in jev if r["group"] == g]
        gs = summarize(sub, poolable=False)
        key = "r2JevEceBin" + "".join(w.capitalize() for w in re.findall(r"[A-Za-z0-9]+", g))
        put(key + "NStudies", str(gs["n_studies"]), f"R2 Jev raw ECE clusters with binning '{g}'")
        put(key + "Min", FMT["ece"](gs["min"]), f"R2 Jev raw ECE, binning '{g}', minimum ({gs['min_study']})")
        put(key + "Max", FMT["ece"](gs["max"]), f"R2 Jev raw ECE, binning '{g}', maximum ({gs['max_study']})")
    allj = [r for r in sel(recs, "r2JevEce") if r["a_stage"] == "raw" and r["subset"] != "sensitivity"]
    lo = min(allj, key=lambda r: r["val"])
    hi = max(allj, key=lambda r: r["val"])
    put("r2JevEceRecordMin", FMT["ece"](lo["val"]), f"R2 lowest Jev raw ECE of any record ({lo['study']}, {lo['record']}, ledger {lo['rows_used']})")
    put("r2JevEceRecordMax", FMT["ece"](hi["val"]), f"R2 highest Jev raw ECE of any record ({hi['study']}, {hi['record']}, ledger {hi['rows_used']})")
    put("r2JevEceRecordMaxStudy", hi["study"], "R2 study of the highest Jev raw ECE record")
    put("r2JevEceRecordMinStudy", lo["study"], "R2 study of the lowest Jev raw ECE record")
    # binning sensitivity inside one study against the spread between studies
    bins = [r for r in sel(recs, "r2JevEce") if r["study"] == "ibrahim2026evaluating"
            and r["record"] in ("ibrJev", "ibrJevBin10", "ibrJevBin20", "ibrJevMass15")]
    span_bin = max(r["val"] for r in bins) - min(r["val"] for r in bins)
    span_study = s["max"] - s["min"]
    put("r2BinningSpan", FMT["ece"](span_bin), "R2 spread of Jev median ECE across 10, 15, 20 equal-width and 15 "
                                             "equal-mass bins within Ibrahim & Zaki (ledger L006, L901, L902, L903)")
    put("r2JevEceMaxOverMin", sig2(s["max"] / s["min"]), "R2 highest over lowest study-level Jev raw ECE (different binning; descriptive ratio, not pooled)")
    guo = {r["record"]: r["val"] for r in sel(recs, "r2JevEce") if r["study"] == "guo2026just"}
    if {"guoJevMedianPerBenchmark", "guoJevPooled", "guoJevNull"} <= set(guo):
        put("r2GuoEstimandGap", FMT["ece"](guo["guoJevMedianPerBenchmark"] - guo["guoJevPooled"]),
            "R2 within-study contrast in Guo et al.: median per-benchmark ECE minus pooled ECE on the same decisions (ledger L608, L607)")
        put("r2GuoExcessOverNull", FMT["ece"](guo["guoJevMedianPerBenchmark"] - guo["guoJevNull"]),
            "R2 Guo et al. median per-benchmark ECE minus its perfect-calibration simulation null (ledger L608)")
    put("r2StudySpan", FMT["ece"](span_study), "R2 spread of Jev raw ECE between study clusters (maximum minus minimum)")
    put("r2StudySpanOverBinningSpan", sig2(span_study / span_bin), "R2 between-study spread divided by the within-study binning spread")
    for r in sel(recs, "r2JevEce"):
        put("r2Jev" + camel(r["record"]), FMT["ece"](r["val"]),
            f"{r['study']} Jev {r['a_stage']} ECE ({r['group']}; ref {r['ref']}; role {r['role']}); ledger {r['rows_used']}")
    for r in sel(recs, "r2OpenEce"):
        put("r2Open" + camel(r["record"]), FMT["ece"](r["val"]),
            f"{r['study']} {r['model']} {r['a_stage']} ECE ({r['group']}); ledger {r['rows_used']}")
    # recalibration: records with raw and recalibrated values
    pairs = [r for r in sel(recs, "r2JevEce") + sel(recs, "r2OpenEce")
             if r["b"] is not None and r["a_stage"] == "raw" and r["role"] == "estimate"]
    for r in pairs:
        r["recal_ratio"] = r["b"] / r["val"]
    rs = [dict(r, val=r["recal_ratio"]) for r in pairs]
    ss = summarize(rs, poolable=False)
    put_summary("r2RecalRatio", ss, "ratio", "R2 recalibrated over raw ECE, all decision models with both values "
                                             "(range only; methods and fit sets differ)")
    put("r2RecalRatioRecordMin", sig2(min(x["val"] for x in rs)), "R2 recal/raw ECE ratio, lowest record (" + min(rs, key=lambda x: x["val"])["record"] + ")")
    put("r2RecalRatioRecordMax", sig2(max(x["val"] for x in rs)), "R2 recal/raw ECE ratio, highest record (" + max(rs, key=lambda x: x["val"])["record"] + ")")
    for lab, test in (("InDomain", lambda r: r["fit"].startswith("in-domain")),
                      ("Transferred", lambda r: r["fit"].startswith("transferred"))):
        sub = [x for x in rs if test(x)]
        if sub:
            put(f"r2RecalRatio{lab}Min", sig2(min(x["val"] for x in sub)), f"R2 recal/raw ECE ratio, {lab} fits, minimum")
            put(f"r2RecalRatio{lab}Max", sig2(max(x["val"] for x in sub)), f"R2 recal/raw ECE ratio, {lab} fits, maximum")
            put(f"r2RecalRatio{lab}NRecords", str(len(sub)), f"R2 records with {lab} fits")
    for r in pairs:
        put("r2Recal" + camel(r["analysis"][2:]) + camel(r["record"]), sig2(r["recal_ratio"]),
            f"{r['study']} {r['model']}: recalibrated ECE {r['b']} over raw {r['val']} ({r['post_hoc_b']}; fit {r['fit']})")
        put("r2RecalDelta" + camel(r["analysis"][2:]) + camel(r["record"]), FMT["ece"](r["b"] - r["val"]),
            f"{r['study']} {r['model']}: recalibrated minus raw ECE")
    # the same pilot-task temperature applied to 19 LLMs (Ibrahim & Zaki Table 10)
    jv = rec(recs, "r2LlmTemp", "jev")
    llms = sel(recs, "r2LlmTemp", "comparator")
    before = sum(1 for r in llms if r["val"] < jv["val"])
    after = sum(1 for r in llms if r["b"] < jv["b"])
    put("r2LlmBelowJevBefore", str(before), "R2 Ibrahim & Zaki LLM baselines with lower median ECE than Jev before scaling")
    put("r2LlmBelowJevAfter", str(after), "R2 Ibrahim & Zaki LLM baselines with lower median ECE than Jev after the same "
                                          "pilot-task temperature fit (ledger L900, L914 to L932)")
    put("r2LlmCount", str(len(llms)), "R2 LLM baselines in Ibrahim & Zaki Table 10")
    best = min(llms, key=lambda r: r["b"])
    put("r2LlmBestScaled", FMT["ece"](best["b"]), f"R2 lowest scaled LLM ECE in Ibrahim & Zaki ({best['model']}, raw {best['val']})")
    put("r2LlmBestScaledModel", best["model"].replace(" before scaling (verbalized confidence)", ""), "R2 model with the lowest scaled ECE")
    # confident-but-wrong regions
    for r in sel(recs, "r2Cbw"):
        kind = "ece" if r["group"] in ("ECE", "AUROC", "accuracy", "confidence", "accuracy minus base rate") else "pp"
        put("r2Cbw" + camel(r["record"][3:]), FMT[kind](r["val"]),
            f"{r['study']} {r['model']}: {r['reason']}; ledger {r['rows_used']} ({r['value_key']})")
    return s, pairs


def r3(recs):
    out = {}
    for an, kind, note in (("r3Retained", "ratio", "R3 cascade quality over strong-model-alone quality (accuracy or success ratio)"),
                           ("r3FeeFrac", "ratio", "R3 cascade fee or cost as a fraction of the strong model alone"),
                           ("r3StrongFrac", "ratio", "R3 share of decisions escalated to the strong model")):
        est = sel(recs, an, "estimate")
        s = summarize(est, poolable=True)
        put_summary(an, s, kind, note)
        for r in sel(recs, an):
            put(an + camel(r["record"]), sig2(r["val"]), f"{r['study']}: {r['reason']} (role {r['role']}); ledger {r['rows_used']}")
        out[an] = s
    for r in sel(recs, "r3Context"):
        put("r3Context" + camel(r["record"]), sig2(r["val"]), f"{r['study']}: {r['reason']}; ledger {r['rows_used']}")
    b3 = rec(recs, "r3FeeFrac", "b3Tau")["val"]
    rx = rec(recs, "r3FeeFrac", "reflexTau")["val"]
    put("r3B3CostOverReflex", sig2(b3 / rx), "R3 B3 cheap generative cascade cost over REFLEX cost on tau^2-bench (ledger L432, L911)")
    n_casc = len({r["cluster"] for an in ("r3Retained", "r3FeeFrac", "r3StrongFrac") for r in sel(recs, an)})
    put("r3NStudiesAny", str(n_casc), "R3 study clusters reporting any escalation or cascade record")
    return out


def simple(recs, an, prefix, kind, note, poolable=True):
    est = sel(recs, an, "estimate", subset="primary")
    s = summarize(est, poolable=poolable)
    put_summary(prefix, s, kind, note)
    rows_all = [r for r in sel(recs, an) if r["role"] == "estimate"]
    lo = min(rows_all, key=lambda r: r["val"])
    hi = max(rows_all, key=lambda r: r["val"])
    put(prefix + "RowMin", FMT[kind](lo["val"]), f"{note}: lowest single row ({lo['study']}, {lo['record']}, ledger {lo['rows_used']})")
    put(prefix + "RowMinStudy", lo["study"], f"{note}: study of the lowest single row")
    put(prefix + "RowMax", FMT[kind](hi["val"]), f"{note}: highest single row ({hi['study']}, {hi['record']}, ledger {hi['rows_used']})")
    for r in sel(recs, an):
        f = FMT[kind] if r["group"] in ACC_GROUPS or kind != "pp" else (FMT["tau"])
        put(prefix + camel(r["record"]), f(r["val"]),
            f"{r['study']}: {r['reason']} ({r['group']}; ref {r['ref']}; RoB {r['rob']}; role {r['role']}); ledger {r['rows_used']}")
    return s


def gap(recs):
    est = sel(recs, "gapJevBest", "estimate", subset="primary", groups=ACC_GROUPS)
    s = summarize(est)
    put_summary("gapJevBest", s, "pp", "Jev minus best comparator on human-labelled or objectively scored items, "
                                       "accuracy-type points (macro-F1, accuracy, F1), frontier comparators only",
                " (points; negative means Jev behind)")
    sens = est + sel(recs, "gapJevBest", subset="sensitivity", groups=ACC_GROUPS)
    ss = summarize(sens)
    put_summary("gapJevBestSens", ss, "pp", "Sensitivity: accuracy gap including non-frontier comparators (li cluster, DeepSeek flash)")
    for r in sel(recs, "gapJevBest"):
        f = FMT["pp"] if r["group"] in ACC_GROUPS else FMT["tau"]
        put("gapJevBest" + camel(r["record"]), f(r["val"]),
            f"{r['study']}: {r['reason']} ({r['group']}; ref {r['ref']}; RoB {r['rob']}; role {r['role']}); ledger {r['rows_used']}")
    neg = sum(1 for v in s["clusters"].values() if v < 0)
    put("gapJevBestNegCount", str(neg), "Accuracy-gap clusters where Jev is behind its best frontier comparator")
    return s


def cost_speed(recs):
    c = simple(recs, "costRatio", "costRatio", "ratio", "Cost ratio, comparator cost over Jev cost on the same work")
    li = [r for r in sel(recs, "costRatio", "estimate") if r["cluster"] == "li2026fast+li2026replacing"]
    put("costRatioLiClusterMin", sig2(min(r["val"] for r in li)), "Cost ratio, li cluster lowest row (li2026fast, DeepSeek cheaper)")
    put("costRatioLiClusterMax", sig2(max(r["val"] for r in li)), "Cost ratio, li cluster highest row (li2026replacing)")
    below1 = sum(1 for r in sel(recs, "costRatio", "estimate") if r["val"] < 1)
    put("costRatioRowsBelowOne", str(below1), "Cost-ratio estimate rows where the comparator was cheaper than Jev")
    sp = simple(recs, "speedRatio", "speedRatio", "ratio", "Latency ratio, comparator median latency over Jev median latency")
    return c, sp


# ---------------------------------------------------------------- vendor claims
def vendor():
    facts = {f["fact_key"]: f for f in json.load(open(VENDOR, encoding="utf-8"))}
    launch = open(LAUNCH, encoding="utf-8").read()

    def rx(text, pat, key):
        hits = re.findall(pat, text)
        if len(hits) != 1:
            sys.exit(f"vendor value {key}: pattern {pat!r} matched {len(hits)} times")
        return hits[0]

    speed = facts["launch_speed_claim"]["verbatim_excerpt"]
    cost = facts["launch_cost_claim"]["verbatim_excerpt"]
    lo, hi = rx(speed, r"range from (\d+)x-(\d+)x faster", "speed")
    home_speed = rx(speed, r"([\d.]+)x Faster", "homeSpeed")
    home_cost = rx(cost, r"Faster, ([\d.]+)x Cheaper", "homeCost")
    pareto = rx(launch, r"\"([^\"]*Pareto frontier[^\"]*)\"", "pareto")
    return dict(
        speed=dict(text=f"{lo}x-{hi}x faster (launch blog); {home_speed}x faster (homepage)", lower=float(lo),
                   source="vendor_facts.json: launch_speed_claim (ts_launch_blog, ts_homepage)"),
        cost=dict(text=f"{home_cost}x cheaper (homepage)", lower=float(home_cost),
                  source="vendor_facts.json: launch_cost_claim (ts_homepage)"),
        types=dict(text=rx(facts["type_error_claim"]["verbatim_excerpt"], r"(The model never makes type errors)", "types"),
                   source="vendor_facts.json: type_error_claim (ts_launch_blog)"),
        halluc=dict(text=rx(facts["hallucination_claim"]["verbatim_excerpt"], r"(can.t hallucinate)", "halluc")
                    + "; " + rx(facts["hallucination_claim"]["verbatim_excerpt"], r"(Our number is not empirical)", "halluc2"),
                    source="vendor_facts.json: hallucination_claim (ts_launch_blog)"),
        calib=dict(text=rx(facts["type_error_claim"]["verbatim_excerpt"],
                           r"(All answers are accompanied with calibrated probabilities and confidence scores)", "calib"),
                   source="vendor_facts.json: type_error_claim excerpt (ts_launch_blog); RLCD per rlcd_description"),
        pareto=dict(text=pareto, source="shared/references/web/ts_launch_blog.md"),
    )


def claims(recs, v):
    rows = []

    def add(cid, claim, vend, r, meas, key, independent, direction, rule):
        rows.append(OrderedDict(
            claim_id=cid, claim=claim, vendor_value=vend["text"], vendor_source=vend["source"],
            study=r["study"] if r else "", cluster=r["cluster"] if r else "", measurement=meas, measurement_key=key,
            independent=independent, direction=direction, rule=rule,
            rob_overall=(r["rob"] if r else ""),
            rob_for_claim=((r.get("rob_cost") if cid in ("speed", "cost") else r["rob"]) if r else ""),
            evidence_role=(r["role_ev"] if r else ""),
            ledger_rows=(r["rows_used"] if r else "")))

    # speed
    rule = f"supported if ratio >= {v['speed']['lower']:g} (vendor lower bound); mixed if 1 < ratio < {v['speed']['lower']:g}; contradicted if <= 1"
    for r in sel(recs, "speedRatio", "estimate"):
        d = "supported" if r["val"] >= v["speed"]["lower"] else ("mixed" if r["val"] > 1 else "contradicted")
        add("speed", "Faster than frontier LLMs", v["speed"], r, f"{sig2(r['val'])}x ({r['cmp_name']} vs Jev)",
            "syn.speedRatio" + camel(r["record"]), "yes", d, rule)
    vr = LED["L511"]
    add("speed", "Faster than frontier LLMs", v["speed"], dict(study=vr["study_key"], cluster=vr["study_key"],
        rob=ROBD[vr["study_key"]]["overall"], rob_cost=cost_latency_grade(ROBD[vr["study_key"]]),
        role_ev=ROBD[vr["study_key"]]["evidence_role"], rows_used="L511"),
        f"{vr['value']}x p95 (X posts, no protocol)", vr["value_key"] or "L511", "no", "not counted",
        "practitioner report without protocol (contradicted_claims 4 and 12)")
    # cost
    rule = f"supported if ratio >= {v['cost']['lower']:g}; mixed if 1 < ratio < {v['cost']['lower']:g}; contradicted if <= 1"
    for r in sel(recs, "costRatio", "estimate"):
        d = "supported" if r["val"] >= v["cost"]["lower"] else ("mixed" if r["val"] > 1 else "contradicted")
        add("cost", "Cheaper than frontier LLMs", v["cost"], r, f"{sig2(r['val'])}x ({r['cmp_name']} vs Jev)",
            "syn.costRatio" + camel(r["record"]), "yes", d, rule)
    r = rec(recs, "costRatio", "vendorEvalsCost")
    add("cost", "Cheaper than frontier LLMs", v["cost"], r, f"{sig2(r['val'])}x (vendor's own evals, Claude Sonnet 5)",
        "syn.costRatioVendorEvalsCost", "no", "supported" if r["val"] >= v["cost"]["lower"] else "mixed", rule)
    # type errors
    for r in sel(recs, "typeErrors", "estimate"):
        add("types", "No type errors", v["types"], r, f"{int(r['val'])} ({r['metric']})", r["value_key"], "yes",
            "supported" if r["val"] == 0 else "contradicted", "supported if zero type errors or invalid answers")
    # hallucination (definitional)
    rule = "vendor states the figure is non-empirical; contradicted as ordinarily read if wrong answers occur at high confidence"
    r = rec(recs, "r2Cbw", "cbwKevJevConfErr")
    add("halluc", "Cannot hallucinate", v["halluc"], r, f"{r['val']:g}% of out-of-domain decisions at p>=0.9 are wrong",
        "syn.r2CbwKevJevConfErr", "yes", "contradicted" if r["val"] > 0 else "supported", rule)
    r = rec(recs, "r2Cbw", "cbwEmpathy")
    add("halluc", "Cannot hallucinate", v["halluc"], r, f"accuracy {r['a']:g} at confidence >= 0.9 vs base rate {r['b']:g} (empathy)",
        r["value_key"], "yes", "contradicted" if r["a"] < 1 else "supported", rule)
    # calibration, relative to comparators in the same study
    rule = "supported if Jev ECE is below every reported comparator in the study; contradicted if above all; mixed otherwise"
    ib = LED["L006"]["comparator_value"]
    m = re.findall(r"(\d+) of (\d+) have higher ECE than Jev; (\d+)", ib)
    if len(m) != 1:
        sys.exit("cannot read the Ibrahim ECE comparator counts from L006")
    higher, total, lower = map(int, m[0])
    r = rec(recs, "r2JevEce", "ibrJev")
    add("calib", "Calibrated probabilities", v["calib"], r, f"ECE {r['val']:.3f}; {higher} of {total} LLMs higher, {lower} lower",
        r["value_key"], "yes", "mixed" if 0 < lower < total else ("supported" if lower == 0 else "contradicted"), rule)
    jv = rec(recs, "r2LlmTemp", "jev")
    llms = sel(recs, "r2LlmTemp", "comparator")
    after = sum(1 for x in llms if x["b"] < jv["b"])
    add("calib", "Calibrated probabilities", v["calib"], jv, f"after the same temperature fit, {after} of {len(llms)} LLMs below Jev",
        "syn.r2LlmBelowJevAfter", "yes", "mixed" if 0 < after < len(llms) else ("supported" if after == 0 else "contradicted"), rule)
    # (Jev record, [(ledger row, field, pattern, label), ...]) : every comparator ECE the study reports in the ledger
    calib_cmp = (("rafeJevPlatt", [("L079", "comparator_value", None, "Claude Fable 5.1")]),
                 ("localllamaJev", [("L515", "comparator_value", None, "meraGPT Decider 1"),
                                    ("L933", "value", None, "Prior (knows nothing)")]),
                 ("kevJevOod", [("L477", "value", None, "Kev-9B served"),
                                ("L477", "excerpt", r"out-of-domain ECE \| [\d.]+ \| [\d.]+ \| ([\d.]+) \|", "Kev-9B raw")]),
                 ("kevJevScienthoon", [("L485", "value", r"^([\d.]+)", "Kev-9B")]),
                 ("nimbleJevBoolq", [("L463", "value", r"^([\d.]+)", "Nimble-9B")]))
    for recname, cmps in calib_cmp:
        r = rec(recs, "r2JevEce", recname)
        cvs = [(num(LED[row][fld], pat, recname), lab) for row, fld, pat, lab in cmps]
        below = sum(1 for cv, _ in cvs if r["val"] < cv)
        d = "supported" if below == len(cvs) else ("contradicted" if below == 0 else "mixed")
        add("calib", "Calibrated probabilities", v["calib"], r,
            f"Jev ECE {r['val']:.3f} vs " + ", ".join(f"{lab} {cv:.3f}" for cv, lab in cvs),
            r["value_key"] or "", "yes", d, rule)
    r = rec(recs, "r2JevEce", "ibrJevEmpathy")
    add("calib", "Calibrated probabilities", v["calib"], r, f"ECE {r['val']:.3f} on one task (empathy)", r["value_key"], "yes",
        "contradicted", "per-task record: confidence uninformative (accuracy at >=0.9 near the base rate, ledger L008)")
    # Pareto frontier: is Jev dominated on (quality, cost, latency) by the comparator in the same study?
    rule = ("contradicted if a comparator is at least as accurate, no more expensive and no slower (one strictly); "
            "mixed if not dominated but less accurate; supported if not dominated and at least as accurate; "
            "quality, cost and latency taken from the same workload of each study (li2026fast: cloud block)")
    pareto = (("li2026jevasajudge", ("gapJevBest", ("liJudgeRewardBench", "liJudgeJudgeBench", "liJudgeHaluEval")), 1,
               ("costRatio", "liJudgeCost"), ("speedRatio", "liJudgeSpeed")),
              ("zhang2026same", ("gapJevBest", ("zhangGap",)), 1, ("costRatio", "zhangCost"), ("speedRatio", "zhangSpeed")),
              ("deng2026jev", ("gapJevBest", ("dengGap",)), 1, ("costRatio", "dengCost"), ("speedRatio", "dengSpeed")),
              ("li2026fast+li2026replacing", ("gapJevBest", ("liFastCloud",)), 1, ("costRatio", "liFastCost"), ("speedRatio", "liFastSpeed")),
              ("grey_robbalian_rev", ("r1Gap", ("rev4b",)), -1, ("costRatio", "revCost"), ("speedRatio", "revSpeed")),
              ("ibrahim2026evaluating", ("gapJevBest", ("ibrGap",)), 1, ("costRatio", "ibrCost"), None))
    for label, (gan, grecs), sign, (can, crec), spd in pareto:
        g = median([rec(recs, gan, x)["val"] for x in grecs]) * sign   # Jev minus comparator
        cr = rec(recs, can, crec)["val"]                                          # comparator cost / Jev cost
        sr = rec(recs, spd[0], spd[1])["val"] if spd else None                   # comparator latency / Jev latency
        dominated = g <= 0 and cr <= 1 and (sr is None or sr <= 1) and (g < 0 or cr < 1 or (sr is not None and sr < 1))
        if spd is None:
            dominated = False if cr > 1 else dominated
        d = "contradicted" if dominated else ("mixed" if g < 0 else "supported")
        r0 = rec(recs, can, crec)
        add("pareto", "Owns the Pareto frontier of quality, cost and time", v["pareto"], r0,
            f"Jev minus comparator {g:.1f} pts; cost ratio {sig2(cr)}; latency ratio {sig2(sr) if sr else 'n/a'}",
            f"syn.{can}{camel(crec)}", "yes" if r0["role_ev"] != "vendor_evaluation" else "no (developer self-report)", d, rule)
    return rows


def t05(rows, v):
    out = []
    order = {"low": 0, "some_concerns": 1, "high": 2, "": 3}
    role_order = {"independent_evaluation": 0, "method_paper_with_evaluation": 1, "reverse_engineering": 2,
                  "vendor_evaluation": 3, "dataset_card": 4, "practitioner_report": 5, "": 6}
    for cid in ("speed", "cost", "types", "halluc", "calib", "pareto"):
        rs = [r for r in rows if r["claim_id"] == cid]
        ind = [r for r in rs if r["independent"] == "yes"]
        dirs = [r["direction"] for r in ind]
        if cid == "halluc":
            status = "Definitional (schema guarantee); contradicted as ordinarily read" if all(d == "contradicted" for d in dirs) else "Definitional; mixed"
        elif dirs and all(d == "supported" for d in dirs):
            status = "Supported"
        elif dirs and all(d == "contradicted" for d in dirs):
            status = "Contradicted"
        elif dirs and all(d == "mixed" for d in dirs):
            status = "Direction supported; magnitude below the claim"
        else:
            status = "Mixed"
        counts = {k: dirs.count(k) for k in ("supported", "mixed", "contradicted")}
        ranked = sorted(ind, key=lambda r: (role_order.get(r["evidence_role"], 6), order.get(r["rob_for_claim"], 3)))
        best, seen = [], set()
        for r in ranked:
            if r["cluster"] not in seen:
                best.append(r)
                seen.add(r["cluster"])
        best = best[:3]
        ev = "; ".join(f"{r['study']} ({r['rob_for_claim']}): {r['measurement']} [{r['measurement_key']}]" for r in best)
        other = "; ".join(f"{r['study']}: {r['measurement']} ({r['direction']}) [{r['measurement_key']}]"
                          for r in rs if r["independent"] != "yes")
        out.append(OrderedDict(claim=rs[0]["claim"], vendor_value=rs[0]["vendor_value"], vendor_source=rs[0]["vendor_source"],
                               status=status, n_independent=len(ind),
                               supported=counts["supported"], mixed=counts["mixed"], contradicted=counts["contradicted"],
                               best_independent_evidence=ev, not_counted_or_developer_evidence=other))
    return out


# ---------------------------------------------------------------- tables
def write_csv(name, rows, cols=None):
    os.makedirs(OUT_TAB, exist_ok=True)
    cols = cols or list(rows[0].keys())
    with open(os.path.join(OUT_TAB, name), "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)


def f04(recs):
    rows = []
    for r in sel(recs, "r2JevEce") + sel(recs, "r2OpenEce"):
        model = "Jev (hosted)" if r["analysis"] == "r2JevEce" else re.sub(r",? (pre-temperature-scaling|before scaling)$", "", r["model"].split(" vs ")[0])
        raw = r["val"] if r["a_stage"] != "recal" else ""   # stage column marks raw, bound (Rafe floor) or null (Guo simulation)
        recal = r["b"] if r["b"] is not None else (r["val"] if r["a_stage"] == "recal" else "")
        method = r["post_hoc_b"] if r["b"] is not None else (r["post_hoc_a"] if r["a_stage"] == "recal" else "none")
        rows.append(OrderedDict(
            record=r["record"], study=r["study"], cluster=r["cluster"], model=model, task_family=r["task_family"],
            raw_ece=f"{raw:.4f}" if raw != "" else "", recal_ece=f"{recal:.4f}" if recal != "" else "",
            stage=r["a_stage"], method=method, fit=r["fit"], binning=r["group"], n=r["n"], reference_type=r["ref"],
            role=r["role"], subset=r["subset"], ledger_rows=r["rows_used"],
            value_keys=";".join(k for k in (r["value_key"], r["b_value_key"]) if k),
            rob_overall=r["rob"], reason=r["reason"]))
    write_csv("f04_calibration.csv", rows)


AXIS = {"accuracy ratio": "cascade accuracy / strong model alone accuracy (same items)",
        "success ratio": "cascade task success / strong-only success (same tasks)",
        "error ratio": "strong model alone MAE / hybrid MAE (above 1 means the hybrid is better)",
        "fee fraction": "cascade fee or cost / strong model alone fee or cost (same work)",
        "escalated share": "share of decisions sent to the strong model (strong calls / strong-only calls)",
        "anchor share": "share of application states given a flagship anchor call (fixed, not confidence-gated)"}


def f05(recs):
    by = OrderedDict()
    for an in ("r3Retained", "r3FeeFrac", "r3StrongFrac"):
        for r in sel(recs, an):
            d = by.setdefault(r["record"], OrderedDict(
                record=r["record"], study=r["study"], cluster=r["cluster"], role=r["role"], setting=r["reason"],
                retained_quality="", retained_definition="", cost_fraction="", cost_definition="",
                strong_call_fraction="", strong_call_definition="", rob_overall=r["rob"], ledger_rows=""))
            if r["role"] == "estimate":
                d["role"] = "estimate"
            col = {"r3Retained": ("retained_quality", "retained_definition"),
                   "r3FeeFrac": ("cost_fraction", "cost_definition"),
                   "r3StrongFrac": ("strong_call_fraction", "strong_call_definition")}[an]
            d[col[0]] = f"{r['val']:.4f}"
            d[col[1]] = AXIS[r["group"]]
            ids = [x for x in (d["ledger_rows"] + ";" + r["rows_used"]).split(";") if x]
            d["ledger_rows"] = ";".join(dict.fromkeys(ids))
    for r in sel(recs, "r3Context"):
        by[r["record"]] = OrderedDict(record=r["record"], study=r["study"], cluster=r["cluster"], role="context",
                                      setting=r["reason"], retained_quality="", retained_definition="",
                                      cost_fraction="", cost_definition="", strong_call_fraction="", strong_call_definition="",
                                      rob_overall=r["rob"], ledger_rows=r["rows_used"])
        by[r["record"]]["setting"] += f" (value {r['val']:.4g}: {r['group']})"
    write_csv("f05_cascade.csv", list(by.values()))


def main():
    recs = read_selection()
    put("ledgerRows", str(len(LED)), "rows in ledger.csv at synthesis time")
    studies = {r["study_key"] for r in LED.values()}
    put("ledgerStudies", str(len(studies)), "studies in ledger.csv")
    put("ledgerClusters", str(len({cluster_of(s) for s in studies})), "independent study clusters (li2026fast and li2026replacing merged)")
    inc = [r for r in recs if r["included"]]
    put("selectionRowsIncluded", str(len(inc)), "selection rows included (all analyses and roles)")
    put("selectionRowsExcluded", str(len(recs) - len(inc)), "selection rows marked include=no")
    r1(recs)
    r2(recs)
    r3(recs)
    gap(recs)
    cost_speed(recs)
    v = vendor()
    crow = claims(recs, v)
    write_csv("f06_claims.csv", crow)
    write_csv("t05_claims.csv", t05(crow, v))
    f04(recs)
    f05(recs)
    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump({"values": VALUES}, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    print(f"synthesis: {len(VALUES)} values; {len(inc)} selection rows used; tables in {OUT_TAB}")


if __name__ == "__main__":
    main()
