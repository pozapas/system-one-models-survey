"""Counts for the reviews of the class that appeared after the launch (Section 2, Table 2).

Reads the saved full text of Tang and Zheng (arXiv 2609.32160), takes the arXiv identifiers listed from its
Appendix A onward as its corpus, and counts how many of them have rows in shared/ledger/ledger.csv. Writes
shared/ledger/prior_reviews.json (macros \\synval{prior.*}).
"""
import csv
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as K

TANG = "2609.32160"


def main():
    text = open(os.path.join(K.LEDGER, "fulltext", TANG + ".txt"), encoding="utf-8", errors="replace").read()
    start = text.find("Appendix A")
    corpus = sorted(set(re.findall(r"26(?:09|10)\.\d{5}", text[start:] if start > 0 else text)) - {TANG})
    ledger = {re.sub(r"v\d+$", "", r["arxiv_id"].strip())
              for r in csv.DictReader(open(os.path.join(K.LEDGER, "ledger.csv"), encoding="utf-8"))}
    shared = [a for a in corpus if a in ledger]
    src = "shared/ledger/prior_reviews.json"
    out = {"values": {"prior": {
        "tangCorpus": {"text": str(len(corpus)), "source": src,
                       "note": "papers in Tang and Zheng's corpus (arXiv identifiers listed from its Appendix A)"},
        "tangInLedger": {"text": str(len(shared)), "source": src,
                         "note": "of those, papers with rows in ledger.csv; not in the ledger: " +
                                 ", ".join(a for a in corpus if a not in ledger)}}}}
    json.dump(out, open(os.path.join(K.LEDGER, "prior_reviews.json"), "w", encoding="utf-8"), indent=1)
    print(f"Tang corpus {len(corpus)}, in ledger {len(shared)}")


if __name__ == "__main__":
    main()
