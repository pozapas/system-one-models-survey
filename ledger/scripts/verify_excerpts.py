"""Check that every ledger excerpt of a given version appears verbatim in the saved full text.

Reads shared/ledger/ledger.csv, keeps rows whose ledger_version matches the argument (default 1.2), and
looks for each excerpt in fulltext/<arxiv_id>.txt, falling back to the tag-stripped .html. Both sides
are normalized for whitespace, quotes, dashes, ligatures and math spacing before matching. A table
excerpt quoted as "caption; row; column" passes when every piece is found. A table excerpt whose structured
part (row and column labels, cells joined by // or |) is not a literal run of text passes as table_ok when its
caption is verbatim and the row's value appears in the full text. Writes
shared/ledger/excerpt_check_v<version>.csv and prints the rows that fail.
"""
import csv
import html
import os
import re
import sys
import unicodedata

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as K

VERSION = sys.argv[1] if len(sys.argv) > 1 else "1.2"
FULL = os.path.join(K.LEDGER, "fulltext")
SUBS = {"‘": "'", "’": "'", "“": '"', "”": '"', "–": "-", "—": "-",
        "−": "-", " ": " ", "ﬁ": "fi", "ﬂ": "fl", " ": " ", " ": " "}


def norm(s):
    s = unicodedata.normalize("NFKC", s)
    for a, b in SUBS.items():
        s = s.replace(a, b)
    s = re.sub(r"[^0-9A-Za-z.%+\-=<>]+", " ", s)
    return re.sub(r"\s+", " ", s).strip().lower()


_cache = {}


def text_for(aid):
    if aid in _cache:
        return _cache[aid]
    t = ""
    for ext in (".txt", ".html"):
        p = os.path.join(FULL, aid + ext)
        if os.path.exists(p):
            raw = open(p, encoding="utf-8", errors="replace").read()
            if ext == ".html":
                raw = html.unescape(re.sub(r"<[^>]+>", " ", re.sub(r"(?s)<(script|style).*?</\1>", " ", raw)))
            t += " " + raw
    _cache[aid] = norm(t)
    return _cache[aid]


def found(excerpt, body):
    pieces = [p for p in re.split(r"\s*(?:;|\||//|\[|\])\s*|\.\.\.|…", excerpt) if len(norm(p)) >= 3]
    return bool(pieces) and all(norm(p) in body for p in pieces)


def table_ok(excerpt, value, body):
    excerpt = re.sub(r"\\[A-Za-z]+", " ", excerpt)
    caption = re.split(r"\s*(?://|\[|\||;|, row )\s*", excerpt)[0]
    vals = [v for v in re.findall(r"-?\d+(?:\.\d+)?", value or "")]
    return (len(norm(caption)) >= 25 and norm(caption) in body and bool(vals)
            and all(re.search(r"(?<![\d.])" + re.escape(v.lstrip("-")) + r"(?![\d])", body) for v in vals))


def main():
    rows = [r for r in csv.DictReader(open(os.path.join(K.LEDGER, "ledger.csv"), encoding="utf-8"))
            if r["ledger_version"].strip() == VERSION]
    out, bad, missing = [], 0, set()
    for r in rows:
        aid = re.sub(r"v\d+$", "", r["arxiv_id"].strip())
        body = text_for(aid) if aid else ""
        if not body:
            status = "no_fulltext"
            missing.add(aid or r["study_key"])
        else:
            status = ("ok" if found(r["excerpt"], body)
                      else "table_ok" if table_ok(r["excerpt"], r["value"], body) else "not_found")
        bad += status not in ("ok", "table_ok")
        out.append({"row_id": r["row_id"], "study_key": r["study_key"], "arxiv_id": aid, "status": status,
                    "excerpt": r["excerpt"][:300]})
    path = os.path.join(K.LEDGER, f"excerpt_check_v{VERSION}.csv")
    with open(path, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0].keys()) if out else ["row_id"])
        w.writeheader()
        w.writerows(out)
    n_tab = sum(o["status"] == "table_ok" for o in out)
    print(f"{len(rows)} rows of version {VERSION}; {len(rows) - bad - n_tab} verbatim, {n_tab} table caption and value, "
          f"{bad} flagged -> {path}")
    if missing:
        print("no full text:", sorted(missing))
    for o in out:
        if o["status"] == "not_found":
            print(o["row_id"], o["study_key"], "|", o["excerpt"][:120])
    return 0


if __name__ == "__main__":
    sys.exit(main())
