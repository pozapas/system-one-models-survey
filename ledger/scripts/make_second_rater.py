"""Build a blind second-rater workbook for the survey and keep the first-rater answers in a separate key.

The workbook has four sheets:
  Instructions  what to do, in order, and the rating definitions;
  Inclusion     every arXiv candidate of the sweep, to be judged include or exclude against Definition 2.1;
  Extraction    a seeded sample of ledger rows, whose value the rater reads from the cited source;
  RiskOfBias    a seeded sample of studies, rated low, unclear or high on the five domains.
The first-rater decisions, values and ratings are written only to the key file, which the rater must not open.
Run second_rater_agreement.py on the filled workbook to compute the agreement statistics.

Usage (needs openpyxl):  python make_second_rater.py [--rows 40] [--studies 8] [--seed 20260926]
       version 1.2 sample:    python make_second_rater.py --v12 [--candidates 50] [--rows 40] [--studies 15]
With --v12 the sheets sample the second sweep only (candidates_v12.csv, ledger_version 1.2 rows, the studies graded
in parts/rob_G*.csv), and the workbook and key are written to second_rater_v12/ and second_rater_v12_key/.
"""
import argparse
import csv
import json
import random
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.worksheet.datavalidation import DataValidation

SURVEY = Path(__file__).resolve().parents[1]
LEDGER = SURVEY.parent / "shared" / "ledger"
OUT_DIR = SURVEY / "notes" / "second_rater"
KEY_DIR = SURVEY / "notes" / "second_rater_key"

ANCHORS = {
    "domain1": "low: human adjudicated or task outcome; unclear: human crowd, an administrative field, or headline results that mix label types; high: an LLM teacher, a model consensus, a synthetic procedure or a vendor label.",
    "domain2": "low: n stated, sampling design described and intervals on the headline results; unclear: some but not all of these; high: none of n, design or intervals, or counts that do not reconcile.",
    "domain3": "low: exact model version or revision and run dates; unclear: a version or a date but not both, or a minor version only; high: no version identifier for the evaluated models.",
    "domain4": "low: same instructions and budget for every compared system, or a single-system study; unclear: an asymmetry that is disclosed and bounded; high: one system tuned on test data or selected after seeing results.",
    "domain5": "low: new or private items; unclear: public items seen only through derived features, credentialed access, or partly public data; high: verbatim public benchmark items with answer keys released before 2026 and no contamination check.",
}
DOMAINS = [
    ("domain1", "Reference-label independence",
     "Are the reference labels independent of the models being evaluated (human adjudication, task outcome), or produced "
     "by a model, a teacher, a synthetic procedure or the vendor?"),
    ("domain2", "Sampling and reporting",
     "Is the sample size stated, the sampling design described, and uncertainty (intervals) reported?"),
    ("domain3", "Version pinning and run dates",
     "Are exact model versions or revisions and the run dates stated?"),
    ("domain4", "Tuning-budget parity",
     "Did the decision model and its comparators receive comparable tuning (prompts, training data, thresholds)?"),
    ("domain5", "Test-set exposure",
     "Could the test items have been seen in training (public benchmarks released before the models), and was this checked?"),
]
HEAD = Font(bold=True, color="FFFFFF")
FILL = PatternFill("solid", fgColor="1B6B5A")
RATER = PatternFill("solid", fgColor="FFF4D6")


def sheet(wb, title, cols, rows, rater_cols, widths, validation=None):
    ws = wb.create_sheet(title)
    ws.append(cols)
    for c in ws[1]:
        c.font, c.fill = HEAD, FILL
        c.alignment = Alignment(wrap_text=True, vertical="top")
    for r in rows:
        ws.append(r)
    for row in ws.iter_rows(min_row=2):
        for c in row:
            c.alignment = Alignment(wrap_text=True, vertical="top")
            if cols[c.column - 1] in rater_cols:
                c.fill = RATER
    for i, w in enumerate(widths, 1):
        ws.column_dimensions[ws.cell(1, i).column_letter].width = w
    if validation:
        col, options = validation
        dv = DataValidation(type="list", formula1='"' + ",".join(options) + '"', allow_blank=True)
        ws.add_data_validation(dv)
        letter = ws.cell(1, cols.index(col) + 1).column_letter
        dv.add(f"{letter}2:{letter}{len(rows) + 1}")
    ws.freeze_panes = "A2"
    return ws


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rows", type=int, default=40)
    ap.add_argument("--studies", type=int, default=8)
    ap.add_argument("--seed", type=int, default=20260926)
    ap.add_argument("--v12", action="store_true")
    ap.add_argument("--candidates", type=int, default=50)
    a = ap.parse_args()
    rng = random.Random(a.seed)
    global OUT_DIR, KEY_DIR

    cand = list(csv.DictReader((LEDGER / "candidates.csv").open(encoding="utf-8")))
    led = [r for r in csv.DictReader((LEDGER / "ledger.csv").open(encoding="utf-8"))
           if r["excerpt"].strip() and r["location"].strip() and r["value"].strip() and r["extractor"] != "synthesis"]
    rob = list(csv.DictReader((LEDGER / "rob.csv").open(encoding="utf-8")))
    if a.v12:
        OUT_DIR, KEY_DIR = SURVEY / "notes" / "second_rater_v12", SURVEY / "notes" / "second_rater_v12_key"
        cand = rng.sample(list(csv.DictReader((LEDGER / "candidates_v12.csv").open(encoding="utf-8"))), a.candidates)
        led = [r for r in led if r["ledger_version"].strip() == "1.2"]
        g = set()
        for p in sorted((LEDGER / "parts").glob("rob_G*.csv")):
            g |= {r["study_key"] for r in csv.DictReader(p.open(encoding="utf-8-sig"))}
        rob = [r for r in rob if r["study_key"] in g]

    sample_rows = rng.sample(led, a.rows)
    sample_studies = rng.sample(rob, a.studies)
    urls = {}
    for r in csv.DictReader((LEDGER / "ledger.csv").open(encoding="utf-8")):
        urls.setdefault(r["study_key"], r["source_url"])

    wb = Workbook()
    ins = wb.active
    ins.title = "Instructions"
    text = [
        "Second-rater workbook for the survey 'System One Decision Models'.",
        "Work alone and do not look at the paper's tables, the ledger or any key file while rating.",
        "Fill only the yellow columns. Leave a cell empty if you cannot decide, and explain in the notes column.",
        "",
        "Sheet Inclusion: read the title and abstract (open the arXiv link if needed) and decide include or exclude.",
        "Include a paper if it reports a measured quantity, a documented interface or a governing method for a typed "
        "probabilistic decision model: a model that maps a state and a question with a finite, declared answer space to a "
        "probability distribution over those answers in one forward pass, without generating free text.",
        "",
        "Sheet Extraction: open the source, go to the location given, and write the value of the named metric for the named "
        "model and dataset exactly as printed (keep the source's precision). The detail column names the exact condition "
        "or subset (for example a variable, a threshold or an error type). Do not compute anything.",
        "",
        "Sheet RiskOfBias: read the study and rate each domain low, unclear or high, with one line of justification that "
        "cites a section or table of the study. The domain definitions are listed below.",
        "",
    ] + [f"{name}: {desc} Anchors, {ANCHORS[key]}" for key, name, desc in DOMAINS] + [
        "",
        "Return the saved workbook to the corresponding author. Agreement is computed by survey/src/second_rater_agreement.py.",
    ]
    for line in text:
        ins.append([line])
    ins.column_dimensions["A"].width = 140
    for row in ins.iter_rows():
        row[0].alignment = Alignment(wrap_text=True)
    ins["A1"].font = Font(bold=True, size=13)

    sheet(wb, "Inclusion",
          ["arxiv_id", "title", "abstract", "link", "decision", "notes"],
          [[c["arxiv_id"], c["title"], c["abstract"], f"https://arxiv.org/abs/{c['arxiv_id']}", "", ""] for c in cand],
          {"decision", "notes"}, [14, 40, 80, 32, 12, 30], ("decision", ["include", "exclude"]))
    sheet(wb, "Extraction",
          ["item", "study", "source", "location", "model", "dataset", "metric", "detail", "value", "notes"],
          [[i + 1, r["study_key"], r["source_url"], r["location"], r["model"], r["dataset"], r["metric"],
            r["value_key"].split(".", 1)[-1], "", ""]
           for i, r in enumerate(sample_rows)],
          {"value", "notes"}, [6, 22, 36, 22, 26, 30, 26, 28, 12, 30])
    rob_rows = []
    for s in sample_studies:
        for key, name, _ in DOMAINS:
            rob_rows.append([s["study_key"], urls.get(s["study_key"], s.get("arxiv_id_or_url", "")), name, "", ""])
    sheet(wb, "RiskOfBias", ["study", "source", "domain", "rating", "justification"], rob_rows,
          {"rating", "justification"}, [24, 40, 28, 12, 60], ("rating", ["low", "unclear", "high"]))

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    KEY_DIR.mkdir(parents=True, exist_ok=True)
    wb.save(OUT_DIR / "second_rater_workbook.xlsx")
    key = {
        "seed": a.seed,
        "inclusion": {c["arxiv_id"]: c["screen_decision"] for c in cand},
        "extraction": {str(i + 1): {"row_id": r["row_id"], "value": r["value"]} for i, r in enumerate(sample_rows)},
        "rob": {s["study_key"]: {name: s[f"{key}_rating"] for key, name, _ in DOMAINS} for s in sample_studies},
    }
    (KEY_DIR / "first_rater_key.json").write_text(json.dumps(key, indent=1), encoding="utf-8")
    print(f"workbook: {OUT_DIR / 'second_rater_workbook.xlsx'}")
    print(f"key (do not share with the rater): {KEY_DIR / 'first_rater_key.json'}")
    print(f"{len(cand)} candidates, {len(sample_rows)} ledger rows, {len(sample_studies)} studies x 5 domains")


if __name__ == "__main__":
    main()
