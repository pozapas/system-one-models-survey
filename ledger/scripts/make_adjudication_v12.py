"""Build the adjudication workbook for the second rating of the version 1.2 sweep.

Reads the disagreements written by second_rating_agreement_v12.py, the first-rating reasons in rob.csv and the
recommended resolutions in notes/second_rating_v12/adjudication/ (rob_rec*.csv for risk of bias and
other_recommendations.csv for screening, heads and extraction). Every row shows both ratings, both reasons and a
recommended final rating, which is prefilled in the yellow "final" column for the author to accept or change.
apply_adjudication_v12.py reads the returned workbook.

Usage (needs openpyxl):  python make_adjudication_v12.py
"""
import csv
import json
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.worksheet.datavalidation import DataValidation

SURVEY = Path(__file__).resolve().parents[1]
LEDGER = SURVEY.parent / "shared" / "ledger"
RET = SURVEY / "notes" / "second_rating_v12" / "returned"
ADJ = SURVEY / "notes" / "second_rating_v12" / "adjudication"
YELLOW = PatternFill("solid", fgColor="FFF2CC")
GREY = PatternFill("solid", fgColor="EDEDED")
DOM = {"Reference-label independence": "domain1", "Sampling and reporting": "domain2",
       "Version pinning and run dates": "domain3", "Tuning-budget parity": "domain4", "Test-set exposure": "domain5"}

RULES = [
    ("G1", "Version pinning and run dates",
     "A release name without a revision hash or dated snapshot (Qwen3.5-0.8B, jev-1.13.0) is a version but not an "
     "exact revision, so the domain is unclear even with run dates. Low needs a revision or dated snapshot plus run "
     "dates. High only when some evaluated model has no identifier or only an alias. A minor version (Jev 1.13) is "
     "unclear. A name with a version or size token (GPT-5.6, gpt-4o-mini, Kev 4B) is a release name; a bare product or "
     "endpoint name (cloudflare/clef, Mercury Decide) is no identifier, and so is any name the paper itself calls a "
     "rolling alias."),
    ("G2", "Version pinning and run dates",
     "Every evaluated system whose results are compared counts, generative baselines and judges included, and the "
     "domain is rated by the weakest."),
    ("G3", "Test-set exposure",
     "A third-party public set released during 2026 is unclear. A set newly built by the study's authors, or a "
     "private set, is low."),
    ("G4", "Test-set exposure",
     "A public benchmark released before 2026 with a reported contamination or overlap check is unclear, even when "
     "the check is partial."),
    ("G5", "Reference-label independence",
     "A score from the outcome of the system's own actions in an environment, game or simulator (success, reward, "
     "tasks solved) is a task outcome, so low. A reference label precomputed by a program or simulator and compared "
     "with the model's answer is a synthetic procedure, so high."),
    ("C1", "Sampling and reporting",
     "Reading applied throughout. A standard deviation or standard error over seeds is not an interval; low needs an "
     "interval on the headline result or the headline contrast. Counts that do not add up make the domain high."),
    ("C2", "Tuning-budget parity",
     "Reading applied throughout. A setting chosen on the scored evaluation items is high even when disclosed or "
     "applied to every system. Training on a train or development split, unequal reasoning effort or imported "
     "published numbers are a disclosed asymmetry, so unclear."),
    ("C3", "Reference-label independence",
     "Reading applied throughout. When the paper never says how its benchmark labels were made, the domain is "
     "unclear; outside knowledge of the dataset is not used. Headline results that mix label types are unclear."),
    ("C4", "Test-set exposure",
     "Reading applied throughout. A study that adds its own new items next to public sets released before 2026 is "
     "unclear, as the anchor states, whatever the share of each."),
]
CORRECTIONS = [
    ("L3299", "huang2026consider", "model and version_pin named Qwen3-8B; the value 27 is the Qwen3.5-35B-A3B run "
     "(Sec. 6). Relabelled; value unchanged; row not used in the synthesis."),
    ("L4413 to L4422", "liu2026timesjev", "metric said mean of 13 datasets; the paper's Overall column is not the "
     "plain mean of the 13 cells (61.77 against 67.80). Relabelled as the printed Overall; values unchanged."),
    ("L1333", "nandakishore2026laya", "value_key had an empty detail part; now "
     "nandakishore2026laya.jevCardMaintainersAccuracy. Value unchanged."),
]


def table(wb, title, cols, rows, widths, final_col=None, options=None):
    ws = wb.create_sheet(title)
    ws.append(cols)
    for c in ws[1]:
        c.font = Font(bold=True)
    for r in rows:
        ws.append(r)
    for i, w in enumerate(widths, start=1):
        ws.column_dimensions[ws.cell(row=1, column=i).column_letter].width = w
    for row in ws.iter_rows(min_row=2):
        for c in row:
            c.alignment = Alignment(wrap_text=True, vertical="top")
    for name in (final_col, "author_note"):
        if name in cols:
            letter = ws.cell(row=1, column=cols.index(name) + 1).column_letter
            for j in range(2, len(rows) + 2):
                ws[f"{letter}{j}"].fill = YELLOW
    if final_col and options and rows:
        letter = ws.cell(row=1, column=cols.index(final_col) + 1).column_letter
        dv = DataValidation(type="list", formula1='"' + ",".join(options) + '"', allow_blank=False)
        dv.add(f"{letter}2:{letter}{len(rows) + 1}")
        ws.add_data_validation(dv)
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = ws.dimensions
    return ws


def main():
    rob = {r["study_key"]: r for r in csv.DictReader((LEDGER / "rob.csv").open(encoding="utf-8"))}
    dis = list(csv.DictReader((RET / "disagreements_v12.csv").open(encoding="utf-8")))
    rec = {}
    for p in sorted(ADJ.glob("rob_rec*.csv")):
        for r in csv.DictReader(p.open(encoding="utf-8-sig")):
            rec[r["id"].strip()] = r
    other = {(r["task"], r["item"]): r for r in csv.DictReader((ADJ / "other_recommendations.csv").open(encoding="utf-8"))}
    agree = json.loads((RET / "agreement_v12.json").read_text(encoding="utf-8"))

    rob_rows, missing = [], []
    for i, d in enumerate([d for d in dis if d["task"] == "rob"]):
        rid = f"RB{i + 1:03d}"
        r = rec.get(rid)
        if r is None:
            missing.append(rid)
            r = {"recommended": "", "rule": "", "reason": ""}
        rob_rows.append([rid, d["item"], d["detail"], d["first"], d["second"], r["recommended"].strip(),
                         r["rule"].strip(), r["reason"].strip(), rob[d["item"]][DOM[d["detail"]] + "_reason"],
                         d["second_note"], r["recommended"].strip(), ""])
    if missing:
        raise SystemExit(f"no recommendation for {len(missing)} rows, e.g. {missing[:5]}")

    def other_rows(task):
        out = []
        for d in dis:
            if d["task"] != task:
                continue
            key = d["item"] if task != "extraction" else d["item"]
            o = other[(task, key)]
            out.append([o["id"], key, d["first"], d["second"], o["recommended"], o["reason"], d["second_note"],
                        o["recommended"], ""])
        return out

    wb = Workbook()
    ins = wb.active
    ins.title = "Instructions"
    n_rob, n_other = len(rob_rows), sum(1 for d in dis if d["task"] != "rob")
    for line in [
        "Adjudication of the second rating, version 1.2 sweep",
        f"{n_rob + n_other} disagreements: {sum(d['task'] == 'inclusion' for d in dis)} screening, {n_rob} risk of bias, "
        f"{sum(d['task'] == 'heads' for d in dis)} decision heads, {sum(d['task'] == 'extraction' for d in dis)} extraction.",
        "Start with the Rules sheet. Each rule settles a case that the written anchors left open, and many risk-of-bias "
        "rows depend on one. Accept or reject each rule, then filter the RiskOfBias sheet by the rule column.",
        "On every other sheet the yellow 'final' column is prefilled with the recommended resolution. Keep it to accept, "
        "or change it. Use author_note for anything that should go into the adjudication log.",
        "The recommendation reads the full text, applies the anchors literally and cites a location. The first and "
        "second reasons are shown so that a row can be decided without opening the paper in most cases.",
        "Screening rows marked include add a study, which is then extracted and graded before the synthesis is rerun.",
        "Save the workbook under the same name when done.",
        "",
        f"Agreement before adjudication: screening {agree['inclusion']['agreement']} (kappa {agree['inclusion']['kappa']}), "
        f"risk of bias {agree['rob']['agreement']} (weighted kappa {agree['rob']['weightedKappa']}), extraction "
        f"{agree['extraction']['agreement']}, heads {agree['heads']['agreement']} (kappa {agree['heads']['kappa']}).",
    ]:
        ins.append([line])
    ins.column_dimensions["A"].width = 150
    for row in ins.iter_rows():
        row[0].alignment = Alignment(wrap_text=True)
    ins["A1"].font = Font(bold=True, size=13)

    counts = {g: sum(1 for r in rob_rows if r[6] == g) if g.startswith("G") else "many" for g, _, _ in RULES}
    table(wb, "Rules", ["rule", "domain", "proposed rule", "rows decided by it", "final", "author_note"],
          [[g, d, t, counts[g], "accept", ""] for g, d, t in RULES], [6, 26, 110, 12, 10, 40], "final",
          ["accept", "reject"])
    table(wb, "RiskOfBias",
          ["id", "study", "domain", "first", "second", "recommended", "rule", "recommendation reason", "first reason",
           "second reason", "final", "author_note"],
          rob_rows, [7, 24, 22, 8, 8, 11, 6, 60, 50, 50, 9, 30], "final", ["low", "unclear", "high"])
    cols = ["id", "item", "first", "second", "recommended", "recommendation reason", "second note", "final", "author_note"]
    table(wb, "Screening", cols, other_rows("inclusion"), [6, 14, 9, 9, 11, 70, 50, 9, 30], "final",
          ["include", "exclude"])
    table(wb, "Heads", cols, other_rows("heads"), [6, 36, 6, 6, 11, 70, 50, 9, 30], "final",
          ["a", "b", "c", "d", "e", "undisclosed"])
    table(wb, "Extraction", cols, other_rows("extraction"), [6, 26, 10, 16, 11, 70, 50, 12, 30], "final")
    ws = table(wb, "LedgerCorrections", ["rows", "study", "correction already applied"],
               [list(c) for c in CORRECTIONS], [16, 24, 120])
    for row in ws.iter_rows(min_row=2):
        for c in row:
            c.fill = GREY
    out = ADJ / "Adjudication_v12.xlsx"
    wb.save(out)
    print(out, "| rob rows", n_rob, "| other rows", n_other, "| rule counts", counts)


if __name__ == "__main__":
    main()
