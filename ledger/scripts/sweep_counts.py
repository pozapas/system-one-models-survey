"""Count the literature sweep and screening outcomes for survey section 2 and Supplement S2.

Reads shared/ledger/candidates.csv, sweep_log.csv and the merged ledger, and
writes shared/ledger/sweep_counts.json, whose keys become \\synval{sweep.*}.
"""
import csv
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as K


def main():
    cands = list(csv.DictReader(open(os.path.join(K.LEDGER, "candidates.csv"), encoding="utf-8-sig")))
    log = list(csv.DictReader(open(os.path.join(K.LEDGER, "sweep_log.csv"), encoding="utf-8-sig")))
    inc = [c for c in cands if c["screen_decision"] == "include"]
    exc = [c for c in cands if c["screen_decision"] == "exclude"]
    arxiv_queries = [r for r in log if r.get("source", "").lower().startswith("arxiv") and "force" not in r.get("query", "").lower() and not r.get("query", "").startswith("RERUN")]
    V = {
        "sweep.arxivQueries": len(arxiv_queries),
        "sweep.uniqueArxiv": len(cands),
        "sweep.includedArxiv": len(inc),
        "sweep.excludedArxiv": len(exc),
    }
    studies_dir = os.path.join(K.LEDGER, "studies")
    notes = [f for f in os.listdir(studies_dir) if f.endswith(".md")]
    V["sweep.studiesTotal"] = len(notes)
    V["sweep.studiesGrey"] = len([f for f in notes if f.startswith("grey_")])
    led = os.path.join(K.LEDGER, "ledger.csv")
    if os.path.exists(led):
        rows = list(csv.DictReader(open(led, encoding="utf-8-sig")))
        V["sweep.ledgerRows"] = len(rows)
    out = {"values": {k: {"text": f"{v:,}", "source": "shared/ledger/sweep_counts.json"} for k, v in V.items()}}
    json.dump(out, open(os.path.join(K.LEDGER, "sweep_counts.json"), "w", encoding="utf-8"), indent=2)
    print(V)


if __name__ == "__main__":
    main()
