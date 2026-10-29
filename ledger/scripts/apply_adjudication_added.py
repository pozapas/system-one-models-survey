"""Apply the adjudicated second rating of the studies added at adjudication (make_second_rating_added.py).

Reads notes/second_rating_added/adjudication/Adjudication_added_returned.xlsx (made by make_adjudication_added.py
and filled by the author) and applies every final risk-of-bias value that differs from the first rating, with the
functions of apply_adjudication_v12.py: the domain rating is replaced, the adjudication reason is appended to the
domain reason, and overall is derived again. Every decision is written to adjudication_log_added.md. Running the
script twice changes nothing the second time.

Usage (needs openpyxl):  python apply_adjudication_v11rest.py
Then run merge_rob.py.
"""
import os

from openpyxl import load_workbook

import apply_adjudication_v12 as A

ADJ = os.path.join(os.path.dirname(A.ADJ), "..", "second_rating_added", "adjudication")
BOOK = os.path.join(ADJ, "Adjudication_added_returned.xlsx")
LOG = os.path.join(ADJ, "adjudication_log_added.md")


def main():
    A.TAG = "[Adjudicated 2026-10-29 after the second rating of the added studies:"
    wb = load_workbook(BOOK, data_only=True)
    rob = A.sheet(wb, "RiskOfBias")
    log = ["# Adjudication of the second rating of the studies added at adjudication", "",
           f"Source: {os.path.basename(BOOK)}. Every disagreement between the first rating and the second rating was "
           "decided by the author against the saved v1 full text that the ledger extracted and the raters read. Rows whose "
           "final value equals the first rating are not listed, and the author's note on every cell follows."]
    log += ["", "## Risk of bias", "", "| id | study | domain | first | second | final | reason |",
            "|---|---|---|---|---|---|---|"]
    n_files = A.apply_rob(rob, log)
    log += ["", "## Author's notes", "", "| id | study | domain | first | second | final | note |", "|---|---|---|---|---|---|---|"]
    log += [f"| {d['id']} | {d['study']} | {A.DOM[d['domain']]} | {d['first']} | {d['second']} | {d['final']} | {A.clean(d['author_note'])} |"
            for d in rob]
    with open(LOG, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(log) + "\n")
    changed = sum(1 for d in rob if A.clean(d["final"]).lower() != A.clean(d["first"]).lower())
    print(f"risk of bias: {changed} cells changed in {n_files} part files; log -> {os.path.normpath(LOG)}")


if __name__ == "__main__":
    main()
