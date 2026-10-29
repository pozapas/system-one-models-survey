"""Values of the second rating of the first-sweep studies and its adjudication, for the macros \\synval{sr4.*}.

Reads the agreement computed by second_rating_agreement_v12.py for this round
(notes/second_rating_v11rest/returned/agreement_v11rest.json), the key, the adjudicated workbook
Adjudication_v11rest_returned.xlsx and the merged rob.csv, and writes shared/ledger/second_rating_v11rest.json.
Overall grades before adjudication are rebuilt by putting the first rating back into every adjudicated cell. The
total of studies with a second rating adds the version 1.1 sample, this round and the version 1.2 round.

Usage (needs openpyxl):  python second_rating_numbers_v11rest.py
"""
import csv
import json
import os
import sys

from openpyxl import load_workbook

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as K
from apply_adjudication_v12 import DOM, clean, sheet
from apply_adjudication_v11rest import BOOK
from merge_rob import overall

SURVEY = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOTES = os.path.join(SURVEY, "notes")
OUT = os.path.join(K.LEDGER, "second_rating_v11rest.json")
SRC = "shared/ledger/second_rating_v11rest.json"


def rated(path):
    return set().union(*(r["rob"] for r in json.load(open(path, encoding="utf-8"))["raters"].values()))


def main():
    a = json.load(open(os.path.join(NOTES, "second_rating_v11rest", "returned", "agreement_v11rest.json"), encoding="utf-8"))
    key = json.load(open(os.path.join(NOTES, "second_rating_v11rest_key", "first_rating_key.json"), encoding="utf-8"))
    v11 = set(json.load(open(os.path.join(NOTES, "second_rater_key", "first_rater_key.json"), encoding="utf-8"))["rob"])
    this = rated(os.path.join(NOTES, "second_rating_v11rest_key", "first_rating_key.json"))
    v12 = rated(os.path.join(NOTES, "second_rating_v12_key", "first_rating_key.json"))
    rob = sheet(load_workbook(BOOK, data_only=True), "RiskOfBias")
    cur = {r["study_key"]: r for r in csv.DictReader(open(os.path.join(K.LEDGER, "rob.csv"), encoding="utf-8-sig"))}
    before = {k: dict(r) for k, r in cur.items()}
    changed = [d for d in rob if clean(d["final"]).lower() != clean(d["first"]).lower()]
    for d in changed:
        before[d["study"]][f"domain{DOM[d['domain']]}_rating"] = clean(d["first"]).lower()
    moved = [k for k in {d["study"] for d in changed} if overall(before[k]) != cur[k]["overall"]]
    both = (v11 | this | v12) & set(cur)
    v = {"raters": len(key["raters"]), "robStudies": len(this), "robN": a["rob"]["n"], "robAgreeN": a["rob"]["agree"],
         "robAgreement": round(100 * a["rob"]["agreement"]), "robWeightedKappa": f"{a['rob']['weightedKappa']:.2f}",
         "extractionN": a["extraction"]["n"], "extractionAgreeN": a["extraction"]["agree"],
         "robDisagreeN": len(rob), "robChangedN": len(changed), "overallChangedN": len(moved),
         "firstSweepStudies": len(v11 | this), "studiesSecondRated": len(both),
         "studiesGradedOnce": len(set(cur) - both)}
    out = {"values": {f"sr4.{k}": {"text": str(x), "source": SRC} for k, x in v.items()}}
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1)
        fh.write("\n")
    for k, x in v.items():
        print(f"sr4.{k} = {x}")
    print("graded once:", sorted(set(cur) - both))


if __name__ == "__main__":
    main()
