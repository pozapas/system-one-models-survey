"""Version 1.2 literature sweep: every protocol query plus terms for models released after the first cutoff.

Runs each arXiv query through curl for submissions from 2026-09-14 to the new cutoff, pages through all results,
writes the raw feeds under shared/ledger/raw/v12/, appends one row per query to sweep_log.csv (tagged [v1.2]), and
writes shared/ledger/candidates_v12.csv with every record not already in candidates.csv.
"""
import csv
import datetime
import os
import re
import subprocess
import sys
import time
import urllib.parse
from html import unescape

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as K

CUTOFF_V12 = "2026-10-28"
WINDOW = " AND submittedDate:[202609140000 TO 202610282359]"
QUERIES = [
    'all:Jev',
    'all:"System One model"',
    'all:"System One models"',
    'all:"decision model" AND all:typed',
    'all:"typed decision"',
    'all:Laya AND all:calibrat*',
    'all:Kev AND all:decision',
    'all:Nimble AND all:decision',
    'all:TypeSafe',
    'all:"decision models" AND all:calibration',
    'abs:"typed probabilistic"',
    'all:"decision model" AND all:Jev',
    'all:"jev-1.13"',
    'all:RLCD',
    'all:"calibrated decisions"',
    'all:"System One" AND all:decision',
    'all:"decision models" AND all:LLM',
    # models and terms that appeared after the first cutoff
    'all:"jev-1.14"',
    'all:"Decision-1" AND all:Microsoft',
    'all:Clef AND all:decision',
    'all:"pplx-decider"',
    'all:"Trio-Spark"',
    'all:"System-1" AND all:"decision model"',
    'all:"decision models" AND all:typed',
]
RAW = os.path.join(K.LEDGER, "raw", "v12")
LOG = os.path.join(K.LEDGER, "sweep_log.csv")
OUT = os.path.join(K.LEDGER, "candidates_v12.csv")


def fetch(q, start):
    url = "https://export.arxiv.org/api/query?" + urllib.parse.urlencode(
        {"search_query": q + WINDOW, "start": start, "max_results": 200, "sortBy": "submittedDate", "sortOrder": "descending"})
    for attempt in range(5):
        p = subprocess.run(["curl", "-s", "-L", "-m", "90", "-A", "Mozilla/5.0", url], capture_output=True)
        text = p.stdout.decode("utf-8", "replace")
        if "<feed" in text:
            return text, attempt
        time.sleep(6 * (attempt + 1))
    return None, 5


def entries(text):
    out = []
    for e in text.split("<entry>")[1:]:
        g = lambda pat: (re.search(pat, e, re.S).group(1) if re.search(pat, e, re.S) else "")
        aid = g(r"<id>http://arxiv.org/abs/([\d.]+)v\d+</id>")
        if not aid:
            continue
        authors = re.findall(r"<name>(.*?)</name>", e)
        out.append({"arxiv_id": aid, "title": re.sub(r"\s+", " ", unescape(g(r"<title>(.*?)</title>"))).strip(),
                    "first_author": authors[0] if authors else "", "all_authors": "; ".join(authors),
                    "published": g(r"<published>(\d{4}-\d{2}-\d{2})"),
                    "primary_category": g(r'<arxiv:primary_category[^>]*term="([^"]+)"'),
                    "abstract": re.sub(r"\s+", " ", unescape(g(r"<summary>(.*?)</summary>"))).strip()})
    return out


def main():
    os.makedirs(RAW, exist_ok=True)
    known = {r["arxiv_id"].split("v")[0] for r in csv.DictReader(open(os.path.join(K.LEDGER, "candidates.csv"), encoding="utf-8"))}
    found, log_rows = {}, []
    for qi, q in enumerate(QUERIES):
        hits, retries, start = [], 0, 0
        while True:
            text, r = fetch(q, start)
            retries += r
            if text is None:
                break
            open(os.path.join(RAW, f"q{qi:02d}_{start}.xml"), "w", encoding="utf-8").write(text)
            page = entries(text)
            hits += page
            if len(page) < 200:
                break
            start += 200
            time.sleep(4)
        for h in hits:
            found.setdefault(h["arxiv_id"], dict(h, found_by=q))
        new = sum(1 for h in hits if h["arxiv_id"] not in known)
        note = "OK; {} not previously screened [v1.2]".format(new) if text is not None or hits else "No feed after retries [v1.2]"
        log_rows.append({"source": "arXiv", "query": q + " [v1.2]",
                         "run_timestamp_utc": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
                         "n_hits": len(hits), "retries": retries, "note": note})
        print(f"{len(hits):4d} hits, {new:4d} new  {q}", flush=True)
        time.sleep(4)
    with open(LOG, "a", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["source", "query", "run_timestamp_utc", "n_hits", "retries", "note"])
        w.writerows(log_rows)
    new_rows = [v for k, v in sorted(found.items()) if k not in known]
    cols = ["arxiv_id", "title", "first_author", "all_authors", "published", "primary_category", "abstract", "found_by",
            "screen_decision", "screen_reason"]
    with open(OUT, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        for r in new_rows:
            w.writerow(dict(r, screen_decision="", screen_reason=""))
    print(f"{len(found)} unique records in window, {len(new_rows)} new -> {OUT}")


if __name__ == "__main__":
    main()
