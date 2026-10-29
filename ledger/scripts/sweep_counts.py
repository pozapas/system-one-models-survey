"""Count the literature sweep and screening outcomes for survey section 2 and Supplement S2.

Reads shared/ledger/candidates.csv (the first sweep), candidates_v12.csv (the version 1.2 sweep of the
window 2026-09-14 to 2026-10-28, new records only), sweep_log.csv, rob.csv and the merged ledger, and writes shared/ledger/sweep_counts.json, whose keys become \\synval{sweep.*}.
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
    p12 = os.path.join(K.LEDGER, "candidates_v12.csv")
    cands12 = list(csv.DictReader(open(p12, encoding="utf-8-sig"))) if os.path.exists(p12) else []
    allc = cands + cands12
    inc = [c for c in allc if c["screen_decision"] == "include"]
    exc = [c for c in allc if c["screen_decision"] == "exclude"]
    is_arxiv = lambda r: (r.get("source", "").lower().startswith("arxiv") and "force" not in r.get("query", "").lower()
                          and not r.get("query", "").startswith("RERUN"))
    first = [r for r in log if is_arxiv(r) and "[v1.2]" not in r.get("query", "")]
    second = [r for r in log if is_arxiv(r) and "[v1.2]" in r.get("query", "")]
    rows = list(csv.DictReader(open(os.path.join(K.LEDGER, "ledger.csv"), encoding="utf-8-sig")))
    with_rows = {r["arxiv_id"].split("v")[0] for r in rows}
    V = {
        "sweep.arxivQueries": len(first),
        "sweep.arxivQueriesV12": len(second),
        "sweep.uniqueArxiv": len(allc),
        "sweep.uniqueArxivV12": len(cands12),
        "sweep.includedArxiv": len(inc),
        "sweep.excludedArxiv": len(exc),
        "sweep.includedNoRows": len([c for c in inc if c["arxiv_id"].split("v")[0] not in with_rows]),
    }
    rob = list(csv.DictReader(open(os.path.join(K.LEDGER, "rob.csv"), encoding="utf-8-sig")))
    V["sweep.studiesTotal"] = len(rob)
    V["sweep.studiesGrey"] = len([r for r in rob if r["study_key"].startswith("grey_")])
    V["sweep.ledgerRows"] = len(rows)
    out = {"values": {k: {"text": f"{v:,}", "source": "shared/ledger/sweep_counts.json"} for k, v in V.items()}}
    json.dump(out, open(os.path.join(K.LEDGER, "sweep_counts.json"), "w", encoding="utf-8"), indent=2)
    print(V)


if __name__ == "__main__":
    main()
