"""Values of the version 1.2 second rating and its adjudication, for the manuscript macros \\synval{sr3.*}.

Reads the agreement computed by second_rating_agreement_v12.py (notes/second_rating_v12/returned/agreement_v12.json),
the adjudicated workbook Adjudication_v12_returned.xlsx and the merged rob.csv, and writes
shared/ledger/second_rating_v12.json. Overall grades before adjudication are rebuilt from rob.csv by putting the
first rating back into every adjudicated cell.

Usage (needs openpyxl):  python second_rating_numbers_v12.py
"""
import csv
import glob
import json
import os
import sys
from collections import defaultdict

from openpyxl import load_workbook

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as K
from apply_adjudication_v12 import BOOK, DOM, clean, sheet
from merge_rob import overall

SURVEY = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AGREE = os.path.join(SURVEY, "notes", "second_rating_v12", "returned", "agreement_v12.json")
KEY = os.path.join(SURVEY, "notes", "second_rating_v12_key", "first_rating_key.json")
OUT = os.path.join(K.LEDGER, "second_rating_v12.json")
SRC = "shared/ledger/second_rating_v12.json"


def main():
    a = json.load(open(AGREE, encoding="utf-8"))
    key = json.load(open(KEY, encoding="utf-8"))["raters"]
    wb = load_workbook(BOOK, data_only=True)
    rob = sheet(wb, "RiskOfBias")
    rules = sheet(wb, "Rules")
    cur = {r["study_key"]: r for r in csv.DictReader(open(os.path.join(K.LEDGER, "rob.csv"), encoding="utf-8-sig"))}
    before = {k: dict(r) for k, r in cur.items()}
    changed = [d for d in rob if clean(d["final"]).lower() != clean(d["first"]).lower()]
    for d in changed:
        before[d["study"]][f"domain{DOM[d['domain']]}_rating"] = clean(d["first"]).lower()
    moved = [k for k in {d["study"] for d in changed} if overall(before[k]) != cur[k]["overall"]]
    to_first = sum(1 for d in rob if clean(d["final"]).lower() == clean(d["first"]).lower())
    to_second = sum(1 for d in changed if clean(d["final"]).lower() == clean(d["second"]).lower())
    inc = [d for d in sheet(wb, "Screening") if clean(d["final"]).lower() == "include" != clean(d["first"]).lower()]
    heads = [d for d in sheet(wb, "Heads") if clean(d["final"]) != clean(d["first"])]
    ext = [d for d in sheet(wb, "Extraction") if clean(d["final"]) != clean(d["first"])]
    dom = {1: "Labels", 2: "Reporting", 3: "Versions", 4: "Tuning", 5: "Exposure"}
    v = {
        "raters": "10",
        "inclusionN": a["inclusion"]["n"], "inclusionAgreeN": a["inclusion"]["agree"],
        "inclusionAgreement": round(100 * a["inclusion"]["agreement"]), "inclusionKappa": f"{a['inclusion']['kappa']:.2f}",
        "robN": a["rob"]["n"], "robAgreeN": a["rob"]["agree"], "robAgreement": round(100 * a["rob"]["agreement"]),
        "robKappa": f"{a['rob']['kappa']:.2f}", "robWeightedKappa": f"{a['rob']['weightedKappa']:.2f}",
        "robStudies": sum(len(r["rob"]) for r in key.values()),
        "extractionN": a["extraction"]["n"], "extractionAgreeN": a["extraction"]["agree"],
        "extractionAgreement": f"{100 * a['extraction']['agreement']:.1f}",
        "headsN": a["heads"]["n"], "headsAgreeN": a["heads"]["agree"], "headsKappa": f"{a['heads']['kappa']:.2f}",
        "disagreeN": len(rob) + len(sheet(wb, "Screening")) + len(sheet(wb, "Heads")) + len(sheet(wb, "Extraction")),
        "robDisagreeN": len(rob), "robKeptFirstN": to_first, "robToSecondN": to_second,
        "robOtherN": len(changed) - to_second, "robChangedN": len(changed), "overallChangedN": len(moved),
        "inclusionAddedN": len(inc), "headsChangedN": len(heads), "extractionChangedN": len(ext),
        "headsRecodedN": sum(1 for f in glob.glob(os.path.join(K.CENSUS, "head_check_H*.csv"))
                             for r in csv.DictReader(open(f, encoding="utf-8-sig")) if "[Recoded 2026-10-29" in r["note"]),
        "rulesAcceptedN": sum(1 for r in rules if clean(r["final"]) == "accept"),
        "rulesRejectedN": sum(1 for r in rules if clean(r["final"]) == "reject"),
    }
    for k, name in dom.items():
        s = a["robByDomain"][[n for n, i in DOM.items() if i == k][0]]
        v[f"robKappa{name}"] = f"{s['weightedKappa']:.2f}"
    out = {"values": {f"sr3.{k}": {"text": str(x), "source": SRC} for k, x in v.items()}}
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1)
        fh.write("\n")
    for k, x in v.items():
        print(f"sr3.{k} = {x}")


if __name__ == "__main__":
    main()
