"""Rebuild shared/ledger/rob.csv from the risk-of-bias parts.

parts/rob_v11.csv holds the version 1.1 grades (adjudicated after the second rating); parts/rob_G*.csv hold
the version 1.2 grades, one file per grader. The script concatenates them in the rob.csv column order, checks
that every study is graded once, that every rating is low, high or unclear, that overall follows the written
rule, and that every graded study has ledger rows. On the first run it saves the existing rob.csv as
parts/rob_v11.csv.
"""
import csv
import glob
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as K

ROB = os.path.join(K.LEDGER, "rob.csv")
PARTS = os.path.join(K.LEDGER, "parts")
BASE = os.path.join(PARTS, "rob_v11.csv")
RATINGS = {"low", "high", "unclear"}


def overall(r):
    d = [r[f"domain{i}_rating"].strip() for i in range(1, 6)]
    if d[0] == "high" or d[4] == "high" or d.count("high") >= 2:
        return "high"
    if d.count("low") == 5 or (d.count("unclear") == 1 and d.count("high") == 0):
        return "low"
    return "some_concerns"


def main():
    if not os.path.exists(BASE):
        shutil.copyfile(ROB, BASE)
    cols = next(csv.reader(open(BASE, encoding="utf-8-sig")))
    rows, problems = [], []
    for p in [BASE] + sorted(glob.glob(os.path.join(PARTS, "rob_G*.csv"))):
        for r in csv.DictReader(open(p, encoding="utf-8-sig")):
            r = {c: (r.get(c) or "").strip() for c in cols}
            bad = [i for i in range(1, 6) if r[f"domain{i}_rating"] not in RATINGS]
            if bad:
                problems.append(f"{os.path.basename(p)} {r['study_key']}: rating not in {sorted(RATINGS)} on domains {bad}")
            if r["overall"] != overall(r):
                problems.append(f"{os.path.basename(p)} {r['study_key']}: overall {r['overall']} but the rule gives {overall(r)}")
            rows.append(r)
    keys = [r["study_key"] for r in rows]
    dups = sorted({k for k in keys if keys.count(k) > 1})
    ledger_keys = {r["study_key"] for r in csv.DictReader(open(os.path.join(K.LEDGER, "ledger.csv"), encoding="utf-8"))}
    orphans = sorted(set(keys) - ledger_keys)
    with open(ROB, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)
    from collections import Counter
    print(f"rob.csv: {len(rows)} studies; overall {dict(Counter(r['overall'] for r in rows))}")
    print("duplicate studies:", dups or "none")
    print("graded studies without ledger rows:", orphans or "none")
    print("ledger studies without a grade:", len(ledger_keys - set(keys)))
    for p in problems:
        print("  ", p)
    return 1 if (dups or problems) else 0


if __name__ == "__main__":
    sys.exit(main())
