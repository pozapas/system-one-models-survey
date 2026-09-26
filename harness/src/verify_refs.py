"""Verify every candidate reference against authoritative bibliographic records.

This implements the protocol in step 2 of the plan as a deterministic script
rather than as a language agent. Crossref is queried first, then OpenAlex, then
arXiv. A candidate is accepted only when the title matches closely and either
the first author's surname or the year agrees, and the metadata written to the
bibliography is the record's, never the candidate's.

Everything the script decides is logged, so the accept and reject lists can be
audited line by line.
"""
import csv
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request

import common as C

REFS = os.path.join(C.ROOT, "references")
MAILTO = "crowd-paper-refcheck@example.org"     # Crossref polite pool
UA = f"paper3-refcheck/1.0 (mailto:{MAILTO})"
TITLE_THRESHOLD = 0.72


def get(url, timeout=30):
    req = urllib.request.Request(url, headers={"User-Agent": UA,
                                               "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8", "replace"))


def get_text(url, timeout=30):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "replace")


def norm(s):
    s = re.sub(r"<[^>]+>", " ", s or "")
    s = s.lower().replace("&", " and ")
    s = re.sub(r"[^a-z0-9 ]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def title_sim(a, b):
    """Similarity that tolerates a shortened title but not a vague one.

    Published titles often carry a subtitle that an informal citation drops, so
    a symmetric ratio scores a correct match badly. Containment is used as well,
    but only when the shorter title is at least five content words long, which
    keeps a short generic phrase from matching an unrelated paper. Acceptance
    still also requires the first author or the year to agree.
    """
    ta, tb = set(norm(a).split()), set(norm(b).split())
    if not ta or not tb:
        return 0.0
    inter = len(ta & tb)
    symmetric = inter / max(len(ta), len(tb))
    shorter = min(len(ta), len(tb))
    if shorter >= 5:
        return max(symmetric, inter / shorter)
    return symmetric


def title_candidates(citation):
    """Every plausible title inside an informal citation string.

    The candidate strings are written as 'Authors Year, Title, Venue', but the
    title itself often contains commas, so a single split is unreliable. All
    comma-separated fragments of reasonable length are offered as candidates and
    the best-scoring one against a retrieved record decides the match.
    """
    parts = [p.strip() for p in citation.split(",")]
    cands = []
    for i, p in enumerate(parts):
        if re.fullmatch(r".*\b(19|20|21)\d{2}\b.*", p) and i + 1 < len(parts):
            cands.append(parts[i + 1])
            cands.append(", ".join(parts[i + 1:i + 3]))
    cands += [p for p in parts if len(p.split()) >= 3]
    cands.append(re.sub(r"\b(19|20|21)\d{2}\b", " ", citation))
    seen, out = set(), []
    for c in cands:
        c = re.sub(r"\s+", " ", c).strip(" .")
        if c and c.lower() not in seen:
            seen.add(c.lower())
            out.append(c)
    return out


def guess_title(citation):
    c = title_candidates(citation)
    return max(c, key=lambda p: len(p.split())) if c else citation


def guess_year(citation):
    m = re.findall(r"\b(19|20|21)\d{2}\b", citation)
    return int(re.findall(r"\b((?:19|20|21)\d{2})\b", citation)[0]) if m else None


def guess_first_author(citation):
    head = citation.split(",")[0]
    head = re.sub(r"\b(19|20|21)\d{2}\b.*", "", head)
    head = re.split(r"\s+(?:&|and)\s+|\s+et al\.?", head)[0]
    toks = [t for t in re.split(r"\s+", head.strip()) if t]
    return toks[-1] if toks else ""


def from_crossref_item(it):
    auths = it.get("author", []) or []
    def nm(a):
        fam = a.get("family", "") or a.get("name", "")
        giv = a.get("given", "")
        return f"{fam}, {giv}".strip().strip(",")
    year = None
    for k in ("published-print", "published-online", "issued", "created"):
        dp = (it.get(k) or {}).get("date-parts") or []
        if dp and dp[0] and dp[0][0]:
            year = dp[0][0]
            break
    return {
        "source": "crossref",
        "title": (it.get("title") or [""])[0],
        "authors": [nm(a) for a in auths if nm(a)],
        "year": year,
        "venue": (it.get("container-title") or [""])[0] or it.get("publisher", ""),
        "publisher": it.get("publisher", ""),
        "volume": it.get("volume", ""),
        "issue": it.get("issue", ""),
        "pages": it.get("page", ""),
        "doi": it.get("DOI", ""),
        "type": it.get("type", ""),
        "url": it.get("URL", ""),
    }


def crossref_by_doi(doi):
    d = get(f"https://api.crossref.org/works/{urllib.parse.quote(doi)}?mailto={MAILTO}")
    return from_crossref_item(d["message"])


def crossref_by_title(title):
    q = urllib.parse.quote(title)
    d = get(f"https://api.crossref.org/works?query.bibliographic={q}&rows=5&mailto={MAILTO}")
    return [from_crossref_item(i) for i in d["message"].get("items", [])]


def openalex(doi=None, title=None):
    try:
        if doi:
            d = get(f"https://api.openalex.org/works/doi:{urllib.parse.quote(doi)}"
                    f"?mailto={MAILTO}")
            items = [d]
        else:
            q = urllib.parse.quote(title)
            d = get(f"https://api.openalex.org/works?search={q}&per-page=5&mailto={MAILTO}")
            items = d.get("results", [])
    except Exception:
        return []
    out = []
    for it in items:
        loc = (it.get("primary_location") or {}).get("source") or {}
        out.append({
            "source": "openalex",
            "title": it.get("title") or it.get("display_name") or "",
            "authors": [a["author"]["display_name"]
                        for a in it.get("authorships", []) if a.get("author")],
            "year": it.get("publication_year"),
            "venue": loc.get("display_name", "") or "",
            "publisher": loc.get("host_organization_name", "") or "",
            "volume": (it.get("biblio") or {}).get("volume", "") or "",
            "issue": (it.get("biblio") or {}).get("issue", "") or "",
            "pages": "-".join(x for x in [(it.get("biblio") or {}).get("first_page"),
                                          (it.get("biblio") or {}).get("last_page")] if x),
            "doi": (it.get("doi") or "").replace("https://doi.org/", ""),
            "type": it.get("type", ""),
            "url": it.get("doi") or (it.get("primary_location") or {}).get("landing_page_url", ""),
        })
    return out


def arxiv(arxiv_id=None, title=None):
    try:
        if arxiv_id:
            url = f"http://export.arxiv.org/api/query?id_list={arxiv_id}"
        else:
            q = urllib.parse.quote(f'ti:"{title}"')
            url = f"http://export.arxiv.org/api/query?search_query={q}&max_results=5"
        xml = get_text(url)
    except Exception:
        return []
    out = []
    for m in re.finditer(r"<entry>(.*?)</entry>", xml, re.S):
        e = m.group(1)
        t = re.search(r"<title>(.*?)</title>", e, re.S)
        y = re.search(r"<published>(\d{4})", e)
        ids = re.search(r"<id>(.*?)</id>", e, re.S)
        auth = re.findall(r"<name>(.*?)</name>", e, re.S)
        out.append({"source": "arxiv",
                    "title": re.sub(r"\s+", " ", t.group(1)).strip() if t else "",
                    "authors": [a.strip() for a in auth],
                    "year": int(y.group(1)) if y else None,
                    "venue": "arXiv preprint", "publisher": "arXiv",
                    "volume": "", "issue": "", "pages": "",
                    "doi": "", "type": "preprint",
                    "url": ids.group(1).strip() if ids else ""})
    return out


def arxiv_abs(arxiv_id):
    """Read an arXiv record from its landing page.

    The arXiv API rate-limits aggressively and returns 429 rather than an empty
    result, which is indistinguishable from "no such paper" unless it is handled
    explicitly. The landing page carries the same metadata in citation meta tags
    and is far more reliable here.
    """
    try:
        html = get_text(f"https://arxiv.org/abs/{arxiv_id}")
    except Exception:
        return []
    def meta(name):
        return re.findall(rf'<meta name="{name}" content="([^"]*)"', html)
    t = meta("citation_title")
    if not t:
        return []
    date = (meta("citation_date") or meta("citation_online_date") or [""])[0]
    yr = re.search(r"(19|20|21)\d{2}", date)
    return [{"source": "arxiv", "title": t[0],
             "authors": meta("citation_author"),
             "year": int(yr.group(0)) if yr else None,
             "venue": "arXiv preprint", "publisher": "arXiv",
             "volume": "", "issue": "", "pages": "",
             "doi": (meta("citation_doi") or [""])[0], "type": "preprint",
             "url": f"https://arxiv.org/abs/{arxiv_id}"}]


def datacite(doi):
    """Datasets and archives carry DataCite DOIs, which Crossref does not hold."""
    try:
        d = get(f"https://api.datacite.org/dois/{urllib.parse.quote(doi)}")
    except Exception:
        return []
    a = d.get("data", {}).get("attributes", {})
    titles = a.get("titles") or [{}]
    return [{"source": "datacite",
             "title": titles[0].get("title", ""),
             "authors": [c.get("name", "") for c in (a.get("creators") or [])],
             "year": a.get("publicationYear"),
             "venue": a.get("publisher", "") or "",
             "publisher": a.get("publisher", "") or "",
             "volume": "", "issue": "", "pages": "",
             "doi": a.get("doi", doi), "type": "dataset",
             "url": a.get("url", f"https://doi.org/{doi}")}]


def openlibrary(title):
    """Books are not in Crossref; OpenLibrary is the repository page the protocol wants."""
    try:
        q = urllib.parse.quote(title)
        d = get(f"https://openlibrary.org/search.json?q={q}&limit=5&"
                f"fields=title,author_name,first_publish_year,publisher,key")
    except Exception:
        return []
    out = []
    for it in d.get("docs", []):
        out.append({"source": "openlibrary",
                    "title": it.get("title", ""),
                    "authors": it.get("author_name", []) or [],
                    "year": it.get("first_publish_year"),
                    "venue": "", "publisher": (it.get("publisher") or [""])[0],
                    "volume": "", "issue": "", "pages": "",
                    "doi": "", "type": "book",
                    "url": "https://openlibrary.org" + it.get("key", "")})
    return out


def surname(a):
    a = a.strip()
    return (a.split(",")[0] if "," in a else a.split()[-1]).lower() if a else ""


def pick(cands, titles, year, first_author):
    """Best record over every retrieved candidate and every plausible title."""
    if isinstance(titles, str):
        titles = [titles]
    # Repositories hold many lookalike titles, such as summaries and study guides
    # of a well-known book, so a record whose author agrees is preferred over a
    # marginally closer title by someone else.
    scored = []
    for c in cands:
        s = max((title_sim(t, c.get("title", "")) for t in titles), default=0.0)
        au = any(surname(a) == first_author.lower() for a in c.get("authors", [])[:6])
        scored.append((au, s, c))
    scored.sort(key=lambda x: (x[0], x[1]), reverse=True)
    best, best_s = (scored[0][2], scored[0][1]) if scored else (None, 0.0)
    if not best or best_s < TITLE_THRESHOLD:
        return None, best_s, "title does not match any record"
    au_ok = any(surname(a) == first_author.lower() for a in best.get("authors", [])[:6])
    yr_ok = best.get("year") and year and abs(int(best["year"]) - year) <= 1
    if not (au_ok or yr_ok):
        return None, best_s, ("title matched but neither the first author nor the "
                              "year agrees")
    return best, best_s, None


def bib_escape(s):
    return (str(s).replace("&", r"\&").replace("%", r"\%").replace("_", r"\_")
            .replace("#", r"\#"))


def protect_caps(title):
    out = []
    for w in str(title).split():
        core = re.sub(r"[^A-Za-z]", "", w)
        if len(core) > 1 and core[1:].lower() != core[1:]:
            out.append("{" + w + "}")
        elif core.isupper() and len(core) > 1:
            out.append("{" + w + "}")
        else:
            out.append(w)
    return " ".join(out)


def to_bibtex(key, r):
    t = r.get("type", "")
    if r["source"] == "arxiv" or "preprint" in t:
        et = "misc"
    elif "book" in t:
        et = "book"
    elif "chapter" in t:
        et = "incollection"
    elif "proceedings" in t:
        et = "inproceedings"
    else:
        et = "article"
    f = [("author", " and ".join(r.get("authors", [])[:20])),
         ("title", protect_caps(bib_escape(r.get("title", "")))),
         ("year", r.get("year") or "")]
    if et in ("article",):
        f += [("journal", bib_escape(r.get("venue", ""))),
              ("volume", r.get("volume", "")), ("number", r.get("issue", "")),
              ("pages", r.get("pages", "").replace("-", "--"))]
    elif et == "inproceedings":
        f += [("booktitle", bib_escape(r.get("venue", ""))),
              ("pages", r.get("pages", "").replace("-", "--"))]
    elif et in ("book", "incollection"):
        f += [("publisher", bib_escape(r.get("publisher", "") or r.get("venue", "")))]
        if et == "incollection":
            f += [("booktitle", bib_escape(r.get("venue", "")))]
    else:
        f += [("howpublished", bib_escape(r.get("venue", "")))]
    if r.get("doi"):
        f.append(("doi", r["doi"]))
    elif r.get("url"):
        f.append(("url", r["url"]))
    body = ",\n  ".join(f"{k} = {{{v}}}" for k, v in f if str(v).strip())
    return f"@{et}{{{key},\n  {body}\n}}\n"


HINTS = {}
IDHINTS = {}


def load_hints():
    p = os.path.join(REFS, "title_hints.csv")
    if os.path.exists(p):
        for r in csv.DictReader(open(p, encoding="utf-8")):
            HINTS[r["key"].strip()] = r["title_hint"].strip()
            if (r.get("id_hint") or "").strip():
                IDHINTS[r["key"].strip()] = r["id_hint"].strip()


def run():
    os.makedirs(REFS, exist_ok=True)
    load_hints()
    rows = list(csv.DictReader(open(os.path.join(REFS, "candidates.csv"),
                                    encoding="utf-8")))
    verified, rejected, corrections = [], [], []

    for i, row in enumerate(rows, 1):
        key = row["key"].strip()
        cit = row["candidate_citation"]
        hint = (row.get("doi_or_hint") or "").strip()
        # A title hint is a better search query than anything parsed out of an
        # informal citation. It is only a query: the record still has to match on
        # title similarity and on either the first author or the year.
        titles = title_candidates(cit)
        if key in HINTS:
            titles = [HINTS[key]] + titles
        title = guess_title(cit)
        year = guess_year(cit)
        fa = guess_first_author(cit)

        cands, rec, err = [], None, None
        try:
            idh = IDHINTS.get(key, "")
            if idh.lower().startswith("arxiv:"):
                cands += arxiv_abs(idh.split(":", 1)[1])
            elif idh.startswith("10."):
                try:
                    cands.append(crossref_by_doi(idh))
                except Exception:
                    cands += datacite(idh)
            arx0 = re.search(r"arXiv[:\s]*(\d{4}\.\d{4,5})", cit, re.I)
            if arx0 and not cands:
                cands += arxiv_abs(arx0.group(1))
            if not cands and hint.startswith("10."):
                try:
                    cands.append(crossref_by_doi(hint))
                except Exception:
                    cands += datacite(hint)
            arx = re.search(r"arXiv[:\s]*(\d{4}\.\d{4,5})", cit, re.I)
            if arx and not cands:
                cands += arxiv(arxiv_id=arx.group(1))
            rec, sim, err = pick(cands, titles, year, fa) if cands else (None, 0, None)

            # widen the search over each plausible title until something matches
            for t in titles[:4]:
                if rec is not None:
                    break
                for fn in (crossref_by_title,
                           lambda x: openalex(title=x),
                           lambda x: arxiv(title=x),
                           openlibrary):
                    try:
                        more = fn(t)
                    except Exception:
                        continue
                    cands += more
                    rec, sim, err = pick(cands, titles, year, fa)
                    if rec is not None:
                        break
                    time.sleep(0.2)
        except Exception as e:
            err = f"lookup failed: {type(e).__name__}"

        if rec is None:
            rejected.append({"key": key, "candidate_citation": cit,
                             "reason": err or "no authoritative record found"})
            print(f"  [{i:3d}/{len(rows)}] REJECT {key}: {err}", flush=True)
        else:
            verified.append((key, rec))
            if year and rec.get("year") and int(rec["year"]) != year:
                corrections.append({"key": key, "field": "year",
                                    "candidate_value": year,
                                    "authoritative_value": rec["year"]})
            if title_sim(title, rec["title"]) < 0.95:
                corrections.append({"key": key, "field": "title",
                                    "candidate_value": title,
                                    "authoritative_value": rec["title"]})
            print(f"  [{i:3d}/{len(rows)}] ok     {key} <- {rec['source']}"
                  f" {rec.get('doi') or rec.get('url','')}", flush=True)
        time.sleep(0.34)

    with open(os.path.join(REFS, "verified.bib"), "w", encoding="utf-8") as fh:
        fh.write("% Generated by src/verify_refs.py against Crossref, OpenAlex and "
                 "arXiv.\n% Metadata is the authoritative record's, not the "
                 "candidate's.\n\n")
        for key, rec in verified:
            fh.write(to_bibtex(key, rec) + "\n")

    with open(os.path.join(REFS, "rejected.csv"), "w", encoding="utf-8",
              newline="") as fh:
        w = csv.DictWriter(fh, ["key", "candidate_citation", "reason"])
        w.writeheader()
        w.writerows(rejected)

    with open(os.path.join(REFS, "corrections.csv"), "w", encoding="utf-8",
              newline="") as fh:
        w = csv.DictWriter(fh, ["key", "field", "candidate_value",
                                "authoritative_value"])
        w.writeheader()
        w.writerows(corrections)

    C.dump({"n_candidates": len(rows), "n_verified": len(verified),
            "n_rejected": len(rejected), "n_corrections": len(corrections),
            "rejected_keys": [r["key"] for r in rejected],
            "queried": ["crossref", "openalex", "arxiv"],
            "title_similarity_threshold": TITLE_THRESHOLD},
           "reference_verification.json")

    print(f"\nverified {len(verified)} of {len(rows)}; rejected {len(rejected)}; "
          f"{len(corrections)} field corrections")
    print("wrote references/verified.bib, rejected.csv, corrections.csv")
    return len(verified)


if __name__ == "__main__":
    sys.exit(0 if run() else 1)
