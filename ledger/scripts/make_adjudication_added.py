"""Build the adjudication workbook for the second rating of the studies added at adjudication (make_second_rating_added.py).

Reads the disagreements written by second_rating_agreement_v12.py (--key and --orig of this round), the first-rating
reasons in rob.csv and the recommended resolutions in notes/second_rating_added/adjudication/rob_rec.csv. Every rule
adopted on 2026-10-29 (PROTOCOL.md, final section, G6 included) applies, and every disputed cell is decided on the
saved v1 full text that the ledger extracted and the raters read.

Usage (needs openpyxl):  python make_adjudication_added.py
"""
import csv
import json

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font

from make_adjudication_v12 import DOM, LEDGER, SURVEY, table

NOTES = SURVEY / "notes" / "second_rating_added"
RET, ADJ = NOTES / "returned", NOTES / "adjudication"


def main():
    rob = {r["study_key"]: r for r in csv.DictReader((LEDGER / "rob.csv").open(encoding="utf-8-sig"))}
    dis = list(csv.DictReader((RET / "disagreements_added.csv").open(encoding="utf-8")))
    rec = {r["id"].strip(): r for r in csv.DictReader((ADJ / "rob_rec.csv").open(encoding="utf-8-sig"))}
    agree = json.loads((RET / "agreement_added.json").read_text(encoding="utf-8"))
    rob_rows = []
    for i, d in enumerate([d for d in dis if d["task"] == "rob"]):
        rid = f"RB{i + 1:03d}"
        r = rec[rid]
        rob_rows.append([rid, d["item"], d["detail"], d["first"], d["second"], r["recommended"].strip(), r["rule"].strip(),
                         r["reason"].strip(), rob[d["item"]][DOM[d["detail"]] + "_reason"], d["second_note"],
                         r["recommended"].strip(), ""])
    wb = Workbook()
    ins = wb.active
    ins.title = "Instructions"
    for line in [
        "Adjudication of the second rating of the studies added at adjudication",
        f"{len(rob_rows)} risk-of-bias disagreements from 3 raters on 6 studies. All 6 extracted values agreed.",
        "Every rule adopted on 2026-10-29 applies (PROTOCOL.md, final section), G6 included, and no new rule is proposed.",
        "Every cell is decided on the saved v1 full text, which is the version the ledger extracted and the raters read.",
        "The yellow 'final' column is prefilled with the recommended resolution. Keep it to accept, or change it, and use "
        "author_note for anything that should go into the adjudication log. Save the workbook under the same name.",
        "",
        f"Agreement before adjudication: risk of bias {agree['rob']['agreement']} (weighted kappa "
        f"{agree['rob']['weightedKappa']}), extraction {agree['extraction']['agreement']}.",
    ]:
        ins.append([line])
    ins.column_dimensions["A"].width = 150
    for row in ins.iter_rows():
        row[0].alignment = Alignment(wrap_text=True)
    ins["A1"].font = Font(bold=True, size=13)
    table(wb, "RiskOfBias",
          ["id", "study", "domain", "first", "second", "recommended", "rule", "recommendation reason", "first reason",
           "second reason", "final", "author_note"],
          rob_rows, [7, 24, 22, 8, 8, 11, 6, 60, 50, 50, 9, 30], "final", ["low", "unclear", "high"])
    out = ADJ / "Adjudication_added.xlsx"
    wb.save(out)
    print(out, "| rob rows", len(rob_rows))


if __name__ == "__main__":
    main()
