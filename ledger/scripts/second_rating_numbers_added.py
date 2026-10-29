"""Values of the second rating of the studies added at adjudication, for the macros \\synval{sr5.*}.

Reads the agreement computed by second_rating_agreement_v12.py for this round
(notes/second_rating_added/returned/agreement_added.json), the key, the adjudicated workbook and rob.csv, and writes
shared/ledger/second_rating_added.json. The total of studies with a second rating takes the union of every key
(version 1.1 sample, first-sweep round, version 1.2 round and this round), so a study graded once shows up in
studiesGradedOnce.

Usage (needs openpyxl):  python second_rating_numbers_added.py
"""
import csv
import json
import os
import sys

from openpyxl import load_workbook

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as K
from apply_adjudication_added import BOOK
from apply_adjudication_v12 import clean, sheet
from second_rating_numbers_v11rest import rated

SURVEY = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOTES = os.path.join(SURVEY, "notes")
OUT = os.path.join(K.LEDGER, "second_rating_added.json")
SRC = "shared/ledger/second_rating_added.json"


def main():
    a = json.load(open(os.path.join(NOTES, "second_rating_added", "returned", "agreement_added.json"), encoding="utf-8"))
    this_key = os.path.join(NOTES, "second_rating_added_key", "first_rating_key.json")
    key = json.load(open(this_key, encoding="utf-8"))
    v11 = set(json.load(open(os.path.join(NOTES, "second_rater_key", "first_rater_key.json"), encoding="utf-8"))["rob"])
    others = [os.path.join(NOTES, d, "first_rating_key.json")
              for d in ("second_rating_v11rest_key", "second_rating_v12_key", "second_rating_added_key")]
    both = v11.union(*(rated(p) for p in others))
    rob = sheet(load_workbook(BOOK, data_only=True), "RiskOfBias")
    cur = {r["study_key"] for r in csv.DictReader(open(os.path.join(K.LEDGER, "rob.csv"), encoding="utf-8-sig"))}
    v = {"raters": len(key["raters"]), "robStudies": len(rated(this_key)), "robN": a["rob"]["n"],
         "robAgreeN": a["rob"]["agree"], "robWeightedKappa": f"{a['rob']['weightedKappa']:.2f}",
         "extractionN": a["extraction"]["n"], "extractionAgreeN": a["extraction"]["agree"],
         "robDisagreeN": len(rob),
         "robChangedN": sum(1 for d in rob if clean(d["final"]).lower() != clean(d["first"]).lower()),
         "studiesSecondRated": len(both & cur), "studiesGradedOnce": len(cur - both)}
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump({"values": {f"sr5.{k}": {"text": str(x), "source": SRC} for k, x in v.items()}}, fh, indent=1)
        fh.write("\n")
    for k, x in v.items():
        print(f"sr5.{k} = {x}")


if __name__ == "__main__":
    main()
