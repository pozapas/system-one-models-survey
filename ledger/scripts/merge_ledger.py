"""Merge the ledger parts into shared/ledger/ledger.csv and validate them.

Group A's per-study row files (written headerless by its sub-workers) are
gathered into parts/ledger_A.csv with row identifiers L001 upward, and the
seed checks into parts/seed_check_A.csv. The script then concatenates every
parts/ledger_*.csv in the SCHEMA.md column order, checks that row_id and
value_key are unique and well formed, and writes ledger.csv plus
seed_check.csv. Rerunning it rebuilds both files from the parts.
"""
import csv
import glob
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as K

PARTS = os.path.join(K.LEDGER, "parts")
SCRATCH_A = sys.argv[1] if len(sys.argv) > 1 else None
GROUP_A = ["ibrahim2026evaluating", "sun2026typesafe", "li2026jevasajudge",
           "rafe2026calibrated", "zhang2026same", "huang2026can"]


def schema_columns():
    text = open(os.path.join(K.LEDGER, "SCHEMA.md"), encoding="utf-8").read()
    cols = []
    for m in re.finditer(r"^\| ([a-z_ /]+) \|", text, re.M):
        name = m.group(1).strip()
        if name == "column":
            continue
        if "/" in name:
            cols += [c.strip() for c in name.split("/")]
        else:
            cols.append(name)
    return cols


def build_group_a(cols):
    rows, seeds = [], []
    n = 0
    for key in GROUP_A:
        p = os.path.join(SCRATCH_A, f"rows_{key}.csv")
        if not os.path.exists(p):
            print("missing group A rows:", key)
            continue
        for rec in csv.reader(open(p, encoding="utf-8-sig")):
            if not rec or rec[0] == "row_id":
                continue
            if len(rec) != len(cols):
                sys.exit(f"{p}: {len(rec)} fields, expected {len(cols)}")
            n += 1
            rec[0] = f"L{n:03d}"
            rows.append(rec)
        sp = os.path.join(SCRATCH_A, f"seed_{key}.csv")
        if os.path.exists(sp):
            for rec in csv.reader(open(sp, encoding="utf-8-sig")):
                if rec and rec[0] != "arxiv_id":
                    seeds.append(rec)
    with open(os.path.join(PARTS, "ledger_A.csv"), "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(cols)
        w.writerows(rows)
    with open(os.path.join(PARTS, "seed_check_A.csv"), "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["arxiv_id", "claim", "found_value", "verdict", "excerpt", "location"])
        w.writerows(seeds)
    print(f"group A: {len(rows)} rows, {len(seeds)} seed checks")


def main():
    cols = schema_columns()
    if SCRATCH_A:
        build_group_a(cols)
    allrows = []
    for p in sorted(glob.glob(os.path.join(PARTS, "ledger_*.csv"))):
        for r in csv.DictReader(open(p, encoding="utf-8-sig")):
            allrows.append({c: r.get(c, "") for c in cols})
    ids = [r["row_id"] for r in allrows]
    keys = [r["value_key"] for r in allrows if r["value_key"]]
    dup_ids = {i for i in ids if ids.count(i) > 1}
    dup_keys = {k for k in keys if keys.count(k) > 1}
    bad_keys = [k for k in keys if not re.fullmatch(r"[A-Za-z0-9.]+", k)]
    no_excerpt = [r["row_id"] for r in allrows if not r["excerpt"].strip()]
    with open(os.path.join(K.LEDGER, "ledger.csv"), "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        w.writerows(allrows)
    seeds = []
    for p in sorted(glob.glob(os.path.join(PARTS, "seed_check_*.csv"))):
        seeds += list(csv.reader(open(p, encoding="utf-8-sig")))[1:]
    with open(os.path.join(K.LEDGER, "seed_check.csv"), "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["arxiv_id", "claim", "found_value", "verdict", "excerpt", "location"])
        w.writerows(seeds)
    print(f"ledger.csv: {len(allrows)} rows from {len(set(r['study_key'] for r in allrows))} studies; "
          f"seed checks {len(seeds)}")
    print("duplicate row_ids:", sorted(dup_ids) or "none")
    print("duplicate value_keys:", sorted(dup_keys) or "none")
    print("malformed value_keys:", bad_keys or "none")
    print("rows without excerpt:", no_excerpt or "none")
    return 1 if (dup_ids or dup_keys or bad_keys or no_excerpt) else 0


if __name__ == "__main__":
    sys.exit(main())
