"""Build the adjudication workbook for the second rating of the first-sweep studies (make_second_rating_v11rest.py).

Reads the disagreements written by second_rating_agreement_v12.py (--key and --orig of this round), the first-rating
reasons in rob.csv and the recommended resolutions in notes/second_rating_v11rest/adjudication/rob_rec_*.csv. The
rules adopted on 2026-10-29 (PROTOCOL.md) apply; the Rules sheet asks only about the one case they leave open. Every
disputed cell is decided on the saved full text that the ledger extracted at the first cutoff.

Usage (needs openpyxl):  python make_adjudication_v11rest.py
"""
import csv
import json
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font

from make_adjudication_v12 import DOM, LEDGER, SURVEY, table

NOTES = SURVEY / "notes" / "second_rating_v11rest"
RET, ADJ = NOTES / "returned", NOTES / "adjudication"
RULES = [
    ("G6", "Version pinning and run dates",
     "A model name with a version or size token but no dated snapshot or revision (GPT-6 Astra, Qwen3.8-Max, GPT-4o, "
     "gemini-3-flash-preview) is an incomplete version, so unclear. It is an unresolved alias, so high, only when the "
     "study itself calls it an alias, latest, preview or a free-tier tag that it does not resolve. Outside knowledge "
     "about whether a provider name rolls is not used."),
]


def main():
    rob = {r["study_key"]: r for r in csv.DictReader((LEDGER / "rob.csv").open(encoding="utf-8-sig"))}
    dis = list(csv.DictReader((RET / "disagreements_v11rest.csv").open(encoding="utf-8")))
    rec = {r["id"].strip(): r for p in sorted(ADJ.glob("rob_rec_*.csv"))
           for r in csv.DictReader(p.open(encoding="utf-8-sig"))}
    agree = json.loads((RET / "agreement_v11rest.json").read_text(encoding="utf-8"))
    rob_rows = []
    for i, d in enumerate([d for d in dis if d["task"] == "rob"]):
        rid = f"RB{i + 1:03d}"
        r = rec[rid]
        rob_rows.append([rid, d["item"], d["detail"], d["first"], d["second"], r["recommended"].strip(), r["rule"].strip(),
                         r["reason"].strip(), rob[d["item"]][DOM[d["detail"]] + "_reason"], d["second_note"],
                         r["recommended"].strip(), ""])
    ext_rows = [[f"EX{i + 1:02d}", d["item"], d["first"], d["second"], d["first"],
                 "Same value in a different unit. Table 1 prints 0.95 in the Success column and Sec. 5.1 prints 95%; "
                 "the ledger metric success_rate is a proportion, so 0.95 stands.", d["second_note"], d["first"], ""]
                for i, d in enumerate(d for d in dis if d["task"] == "extraction")]

    wb = Workbook()
    ins = wb.active
    ins.title = "Instructions"
    for line in [
        "Adjudication of the second rating of the first-sweep studies",
        f"{len(dis)} disagreements: {len(rob_rows)} risk of bias and {len(ext_rows)} extraction, from 5 raters on 19 studies.",
        "The rules adopted on 2026-10-29 apply (PROTOCOL.md, final section). The Rules sheet asks about the one case "
        "they leave open, which the raters flagged. Cells decided by it carry G6 in the rule column.",
        "Every cell is decided on the saved full text that the ledger extracted at the first cutoff (normally v1). Some "
        "raters read a later arXiv version; the recommendation says so where that explains the disagreement.",
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
    n_g6 = sum(1 for r in rob_rows if r[6] == "G6")
    table(wb, "Rules", ["rule", "domain", "proposed rule", "rows decided by it", "final", "author_note"],
          [[g, d, t, n_g6, "accept", ""] for g, d, t in RULES], [6, 26, 110, 12, 10, 40], "final", ["accept", "reject"])
    table(wb, "RiskOfBias",
          ["id", "study", "domain", "first", "second", "recommended", "rule", "recommendation reason", "first reason",
           "second reason", "final", "author_note"],
          rob_rows, [7, 24, 22, 8, 8, 11, 6, 60, 50, 50, 9, 30], "final", ["low", "unclear", "high"])
    table(wb, "Extraction", ["id", "item", "first", "second", "recommended", "recommendation reason", "second note",
                             "final", "author_note"], ext_rows, [6, 26, 10, 10, 11, 70, 50, 12, 30], "final")
    out = ADJ / "Adjudication_v11rest.xlsx"
    wb.save(out)
    print(out, "| rob rows", len(rob_rows), "| G6 rows", n_g6)


if __name__ == "__main__":
    main()
