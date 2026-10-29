"""Apply the adjudicated second rating of the version 1.2 sweep.

Reads the returned workbook notes/second_rating_v12/adjudication/Adjudication_v12_returned.xlsx (made by
make_adjudication_v12.py and filled by the author) and applies every final value that differs from the first
rating. Risk of bias goes to the part file that holds the study (parts/rob_v11.csv or parts/rob_G*.csv): the
domain rating is replaced, the adjudication reason is appended to the domain reason, and overall is derived again
by merge_rob.overall. Head codes go to shared/census/head_check_H*.csv. Screening decisions that turn to include
go to candidates_v12.csv. Every change, and every rule decision, is written to adjudication_log_v12.md. Running the
script twice changes nothing the second time.

Usage (needs openpyxl):  python apply_adjudication_v12.py
Then run merge_rob.py and census_heads.py.
"""
import csv
import glob
import os
import sys

from openpyxl import load_workbook

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as K
from merge_rob import overall

SURVEY = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ADJ = os.path.join(SURVEY, "notes", "second_rating_v12", "adjudication")
BOOK = os.path.join(ADJ, "Adjudication_v12_returned.xlsx")
LOG = os.path.join(ADJ, "adjudication_log_v12.md")
PARTS = os.path.join(K.LEDGER, "parts")
DOM = {"Reference-label independence": 1, "Sampling and reporting": 2, "Version pinning and run dates": 3,
       "Tuning-budget parity": 4, "Test-set exposure": 5}
TAG = "[Adjudicated 2026-10-29 after the version 1.2 second rating:"


def sheet(wb, name):
    ws = wb[name]
    head = [c.value for c in ws[1]]
    return [dict(zip(head, r)) for r in ws.iter_rows(min_row=2, values_only=True) if r[0]]


def clean(s):
    return " ".join(str(s or "").split())


def read_csv(p):
    with open(p, encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.DictReader(fh))
    return rows, list(rows[0].keys()) if rows else []


def write_csv(p, rows, cols):
    with open(p, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, lineterminator="\r\n")
        w.writeheader()
        w.writerows(rows)


def apply_rob(items, log):
    files = [os.path.join(PARTS, "rob_v11.csv")] + sorted(glob.glob(os.path.join(PARTS, "rob_G*.csv")))
    data = {p: read_csv(p) for p in files}
    where = {r["study_key"]: (p, r) for p, (rows, _) in data.items() for r in rows}
    touched = set()
    for d in items:
        final, first = clean(d["final"]).lower(), clean(d["first"]).lower()
        if final == first:
            continue
        p, r = where[d["study"]]
        k = DOM[d["domain"]]
        why = clean(d["author_note"]) or clean(d["recommendation reason"])
        if r[f"domain{k}_rating"] != final or TAG not in r[f"domain{k}_reason"]:
            r[f"domain{k}_rating"] = final
            r[f"domain{k}_reason"] = f"{r[f'domain{k}_reason'].rstrip()} {TAG} {why}]"
            touched.add(p)
        log.append(f"| {d['id']} | {d['study']} | {k} | {first} | {clean(d['second'])} | {final} | {why} |")
    for p in files:
        rows, cols = data[p]
        for r in rows:
            r["overall"] = overall(r)
        if p in touched:
            write_csv(p, rows, cols)
    return len(touched)


def apply_heads(items, log):
    files = sorted(glob.glob(os.path.join(K.CENSUS, "head_check_H*.csv")))
    for d in items:
        final, first = clean(d["final"]), clean(d["first"])
        if final == first:
            continue
        why = clean(d["author_note"]) or clean(d["recommendation reason"])
        for p in files:
            rows, cols = read_csv(p)
            hit = [r for r in rows if r["id"].strip() == d["item"]]
            if hit:
                for r in hit:
                    if r["panel"] != final:
                        r["panel"] = final
                        r["note"] = f"{r['note'].rstrip()} {TAG} {why}]"
                write_csv(p, rows, cols)
        log.append(f"| {d['id']} | {d['item']} | {first} | {clean(d['second'])} | {final} | {why} |")


def apply_screening(items, log):
    p = os.path.join(K.LEDGER, "candidates_v12.csv")
    rows, cols = read_csv(p)
    by = {r["arxiv_id"]: r for r in rows}
    for d in items:
        final, first = clean(d["final"]).lower(), clean(d["first"]).lower()
        why = clean(d["author_note"]) or clean(d["recommendation reason"])
        # an exclusion of a title-and-abstract include matches the full-text exclusion already recorded in the
        # study note, so only a new include changes candidates_v12.csv
        if final == "include" and first == "exclude":
            r = by[d["item"]]
            if r["screen_decision"] != final:
                r["screen_decision"] = final
                r["screen_reason"] = f"{r['screen_reason'].rstrip()} {TAG} {why}]"
        log.append(f"| {d['id']} | {d['item']} | {first} | {clean(d['second'])} | {final} | {why} |")
    write_csv(p, rows, cols)


def main():
    wb = load_workbook(BOOK, data_only=True)
    rules = sheet(wb, "Rules")
    rob = sheet(wb, "RiskOfBias")
    log = ["# Adjudication of the version 1.2 second rating", "",
           f"Source: {os.path.basename(BOOK)}. Every disagreement between the first rating and the second rating was "
           "decided by the author against the full text. Rows whose final value equals the first rating are not "
           "listed.", "", "## Rules", "", "| rule | domain | decision | note |", "|---|---|---|---|"]
    log += [f"| {r['rule']} | {r['domain']} | {r['final']} | {clean(r['author_note'])} |" for r in rules]
    log += ["", "## Risk of bias", "", "| id | study | domain | first | second | final | reason |",
            "|---|---|---|---|---|---|---|"]
    n_files = apply_rob(rob, log)
    log += ["", "## Decision heads", "", "| id | model | first | second | final | reason |", "|---|---|---|---|---|---|"]
    apply_heads(sheet(wb, "Heads"), log)
    log += ["", "## Screening", "", "| id | arXiv | first | second | final | reason |", "|---|---|---|---|---|---|"]
    apply_screening(sheet(wb, "Screening"), log)
    log += ["", "## Extraction", "", "| id | item | first | second | final | reason |", "|---|---|---|---|---|---|"]
    log += [f"| {d['id']} | {d['item']} | {d['first']} | {d['second']} | {d['final']} | {clean(d['author_note'])} |"
            for d in sheet(wb, "Extraction")]
    log += ["", "## Ledger corrections made from the second raters' notes", "", "| rows | study | correction |",
            "|---|---|---|"]
    log += [f"| {r['rows']} | {r['study']} | {clean(r['correction already applied'])} |"
            for r in sheet(wb, "LedgerCorrections")]
    with open(LOG, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(log) + "\n")
    changed = sum(1 for d in rob if clean(d["final"]).lower() != clean(d["first"]).lower())
    print(f"risk of bias: {changed} cells changed in {n_files} part files; log -> {LOG}")


if __name__ == "__main__":
    main()
