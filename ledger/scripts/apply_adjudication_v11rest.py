"""Apply the adjudicated second rating of the first-sweep studies (make_second_rating_v11rest.py).

Reads notes/second_rating_v11rest/adjudication/Adjudication_v11rest_returned.xlsx (made by make_adjudication_v11rest.py
and filled by the author) and applies every final risk-of-bias value that differs from the first rating, with the
functions of apply_adjudication_v12.py: the domain rating is replaced, the adjudication reason is appended to the
domain reason, and overall is derived again. Every decision is written to adjudication_log_v11rest.md. Running the
script twice changes nothing the second time.

Usage (needs openpyxl):  python apply_adjudication_v11rest.py
Then run merge_rob.py.
"""
import os

from openpyxl import load_workbook

import apply_adjudication_v12 as A

ADJ = os.path.join(os.path.dirname(A.ADJ), "..", "second_rating_v11rest", "adjudication")
BOOK = os.path.join(ADJ, "Adjudication_v11rest_returned.xlsx")
LOG = os.path.join(ADJ, "adjudication_log_v11rest.md")


def main():
    A.TAG = "[Adjudicated 2026-10-29 after the second rating of the first sweep:"
    wb = load_workbook(BOOK, data_only=True)
    rules = A.sheet(wb, "Rules")
    rob = A.sheet(wb, "RiskOfBias")
    log = ["# Adjudication of the second rating of the first-sweep studies", "",
           f"Source: {os.path.basename(BOOK)}. Every disagreement between the first rating and the second rating was "
           "decided by the author against the saved full text that the ledger extracted at the first cutoff. Rows whose "
           "final value equals the first rating are not listed.", "", "## Rules", "",
           "| rule | domain | decision | note |", "|---|---|---|---|"]
    log += [f"| {r['rule']} | {r['domain']} | {r['final']} | {A.clean(r['author_note'])} |" for r in rules]
    log += ["", "## Risk of bias", "", "| id | study | domain | first | second | final | reason |",
            "|---|---|---|---|---|---|---|"]
    n_files = A.apply_rob(rob, log)
    log += ["", "## Extraction", "", "| id | item | first | second | final | reason |", "|---|---|---|---|---|---|"]
    log += [f"| {d['id']} | {d['item']} | {d['first']} | {d['second']} | {d['final']} | {A.clean(d['author_note'])} |"
            for d in A.sheet(wb, "Extraction")]
    with open(LOG, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(log) + "\n")
    changed = sum(1 for d in rob if A.clean(d["final"]).lower() != A.clean(d["first"]).lower())
    print(f"risk of bias: {changed} cells changed in {n_files} part files; log -> {os.path.normpath(LOG)}")


if __name__ == "__main__":
    main()
