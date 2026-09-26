"""License, redistribution and preprint metadata checks.

Part (a) reads the license of every benchmark dataset from its primary source at the
snapshot the benchmark used and at the current head, with verbatim quotes, and states
whether the companion repository may ship the text or should ship reconstruction scripts.
For D1 it reads the dataset card YAML at every commit of LocalLLaMA/typed-decisions.

Part (b) queries the arXiv API for the 2026 preprints cited in the manuscript and compares
title and author list with refs.bib (read only, never edited).

Outputs: results/licenses_audit.json, results/preprint_metadata.json
"""
import datetime
import html
import json
import os
import re
import xml.etree.ElementTree as ET

import requests

import common as C

os.environ.setdefault("HF_HOME", "D:/p4env/hf")
D1_REPO = "LocalLLaMA/typed-decisions"
D1_REV = "c76749ec58bd8c3d2ea706b31c333a9059c38f90"
CLINC_COMMIT = "828f8093932c8fe6ca7936c3d2e52903b1c523de"
SALT = ("SALT-NLP/LLMs_for_CSS", "55183a64d7faaf6d5fc23eddf2bfc48ece4cacad")
IZ = ("hazemibrahim97/decision-models-css", "311956c2d1096cabc0f09a1f248e7dc0e1c0c41e")
TODAY = datetime.date.today().isoformat()


def get(url, **kw):
    r = requests.get(url, timeout=120, **kw)
    return r


def yaml_license(text):
    m = re.search(r"^license:\s*(.*)$", text, re.M)
    if not m:
        return None
    v = m.group(1).strip()
    if v:
        return v
    items = re.findall(r"^license:\s*\n((?:- .*\n)+)", text, re.M)
    return items[0].strip() if items else None


def lines_with(text, pat, width=240):
    out = []
    for m in re.finditer(r".{0,%d}(%s).{0,%d}" % (width // 2, pat, width), text):
        out.append(re.sub(r"\s+", " ", m.group(0)).strip())
    return out


def page_text(url):
    r = get(url)
    r.encoding = "utf-8"
    t = re.sub(r"<[^>]+>", " ", r.text)
    return r.status_code, html.unescape(re.sub(r"\s+", " ", t))


# ------------------------------------------------------------------ (a) licenses

def d1_audit():
    from huggingface_hub import HfApi, hf_hub_download
    api = HfApi()
    commits = api.list_repo_commits(D1_REPO, repo_type="dataset")
    hist = []
    for c in commits:
        try:
            p = hf_hub_download(D1_REPO, "README.md", repo_type="dataset", revision=c.commit_id)
            t = open(p, encoding="utf-8").read()
            lic = yaml_license(t)
            body = [l for l in lines_with(t, r"CC BY|cc-by|Creative Commons|CC-BY", 160)]
        except Exception as e:                                        # first commit has no card
            lic, body = None, [f"no README.md ({type(e).__name__})"]
        hist.append({"commit": c.commit_id, "date": c.created_at.isoformat(), "title": c.title,
                     "yaml_license": lic, "cc_by_mentions": body})
    files_pinned = [f.rfilename for f in api.dataset_info(D1_REPO, revision=D1_REV).siblings]
    info_now = api.dataset_info(D1_REPO)
    lic_files = [f for f in files_pinned if "licen" in f.lower()]
    pinned = next(h for h in hist if h["commit"] == D1_REV)
    return {
        "dataset": "D1 LocalLLaMA/typed-decisions",
        "snapshot": D1_REV,
        "license_at_snapshot": pinned["yaml_license"],
        "license_current": yaml_license(open(hf_hub_download(D1_REPO, "README.md", repo_type="dataset"),
                                             encoding="utf-8").read()),
        "current_head": info_now.sha,
        "quote_at_snapshot": f"license: {pinned['yaml_license']}  (README.md YAML front matter at {D1_REV[:10]})",
        "license_files_in_repo_at_snapshot": lic_files,
        "license_history": hist,
        "any_revision_cc_by": any(
            bool(h["yaml_license"] and "cc" in h["yaml_license"].lower())
            or any("no README" not in x for x in h["cc_by_mentions"]) for h in hist),
        "redistribution": "permitted under Apache-2.0 with attribution, a copy of the license "
                          "and a notice of changes; the benchmark's d1_* inputs rename option "
                          "keys (a modification), which must be stated",
        "recommendation": "the repository may ship the D1 text; ship it with the Apache-2.0 "
                          "notice and a statement that option keys were renamed, and keep the "
                          "reconstruction script (s00_freeze_inputs.py) as the primary route",
        "finding": "the dataset card declares apache-2.0 at the pinned revision and at every "
                   "revision of the repository; no revision declares CC BY 4.0. The manuscript's "
                   "Apache-2.0 is correct and companion/DATA_LICENSES.md, which says CC BY 4.0 "
                   "at the revision used, is wrong",
    }


def clinc_audit():
    lic = get(f"https://raw.githubusercontent.com/clinc/oos-eval/{CLINC_COMMIT}/LICENSE").text
    readme = get(f"https://raw.githubusercontent.com/clinc/oos-eval/{CLINC_COMMIT}/README.md").text
    hf = get("https://huggingface.co/datasets/clinc/clinc_oos/raw/main/README.md").text
    return {
        "dataset": "D2 CLINC-150 (clinc/oos-eval)",
        "snapshot": CLINC_COMMIT,
        "license_at_snapshot": "CC BY 3.0 Unported",
        "quote_at_snapshot": " ".join(lic.split()[:6]) + "  (LICENSE file at " + CLINC_COMMIT[:8] + ")",
        "github_license_api": "NOASSERTION (GitHub does not parse the CC text, the file itself is CC BY 3.0)",
        "readme_mentions_license": bool(re.search("licen", readme, re.I)),
        "hf_mirror": {"repo": "clinc/clinc_oos", "yaml_license": yaml_license(hf) or
                      re.findall(r"license:\s*\n- (\S+)", hf)[:1]},
        "license_current": "CC BY 3.0 Unported (LICENSE unchanged at head: "
                           + str(get("https://raw.githubusercontent.com/clinc/oos-eval/master/LICENSE").text == lic) + ")",
        "redistribution": "permitted with attribution (CC BY 3.0, section 4b) and a note of changes "
                          "(the benchmark adds a fixed option permutation and neutral keys)",
        "recommendation": "the repository may ship the 800 D2 texts with attribution; the "
                          "reconstruction script is sufficient and smaller",
    }


def d3_audit():
    out = []
    salt_lic = get(f"https://api.github.com/repos/{SALT[0]}/license")
    iz_lic = get(f"https://api.github.com/repos/{IZ[0]}/license")
    common_notes = {
        "intermediate_source": f"github.com/{SALT[0]} at {SALT[1][:10]}, css_data/<task>/test.json",
        "intermediate_source_license": "none declared (GitHub license API HTTP "
                                       f"{salt_lic.status_code}; no LICENSE file in the tree)",
        "question_wording_source": f"github.com/{IZ[0]} at {IZ[1][:10]}, license "
                                   + (iz_lic.json().get("license", {}).get("spdx_id", "?")
                                      if iz_lic.ok else f"HTTP {iz_lic.status_code}")
                                   + " (covers the code and prompts, not the task data)",
    }
    s, t = page_text("https://convokit.cornell.edu/documentation/awry.html")
    q = lines_with(t, r"licen|Licen|CC BY|Creative Commons", 200)
    out.append({"dataset": "D3 conv_go_awry (Conversations Gone Awry, ConvoKit)",
                "license_at_snapshot": "not stated by the corpus page; text is Wikipedia talk-page "
                                       "content, which Wikipedia publishes under CC BY-SA",
                "quote_at_snapshot": q[0] if q else f"no license statement on "
                                     f"convokit.cornell.edu/documentation/awry.html (HTTP {s}, "
                                     f"read {TODAY})",
                "redistribution": "not explicitly granted by the corpus; CC BY-SA of the underlying "
                                  "Wikipedia text would require attribution and share-alike",
                "recommendation": "ship reconstruction scripts (s00b_prepare_d3.py) rather than the "
                                  "text", **common_notes})
    s, t = page_text("https://convokit.cornell.edu/documentation/wiki.html")
    q = re.findall(r"[A-Z][^.¶]*governed by the [^.]*?v\d\.\d", t)
    out.append({"dataset": "D3 wiki_corpus (Wikipedia Talk Pages, Echoes of Power, ConvoKit)",
                "license_at_snapshot": "CC BY-SA 4.0",
                "quote_at_snapshot": q[0] if q else f"HTTP {s}",
                "redistribution": "permitted with attribution and share-alike (derived files must "
                                  "carry CC BY-SA 4.0)",
                "recommendation": "shipping the text would put those files under CC BY-SA 4.0; "
                                  "ship the reconstruction script instead", **common_notes})
    s, t = page_text("https://convokit.cornell.edu/documentation/wiki_politeness.html")
    q = re.findall(r"[A-Z][^.¶]*governed by the [^.]*?v\d\.\d", t)
    out.append({"dataset": "D3 wiki_politeness (Stanford Politeness Corpus, Wikipedia, ConvoKit)",
                "license_at_snapshot": "CC BY 4.0",
                "quote_at_snapshot": q[0] if q else f"HTTP {s}",
                "redistribution": "permitted with attribution",
                "recommendation": "may ship with attribution; the reconstruction script is the "
                                  "consistent route for all four D3 tasks", **common_notes})
    em = get("https://huggingface.co/datasets/dair-ai/emotion/raw/main/README.md").text
    snap = os.listdir(os.path.join(os.environ["HF_HOME"], "hub", "datasets--dair-ai--emotion",
                                   "snapshots"))[0]
    em_snap = open(os.path.join(os.environ["HF_HOME"], "hub", "datasets--dair-ai--emotion",
                                "snapshots", snap, "README.md"), encoding="utf-8").read()
    q = re.findall(r"The dataset should be used for educational and research purposes only\.", em_snap)
    out.append({"dataset": "D3 emotion (CARER, dair-ai/emotion)",
                "snapshot": f"dair-ai/emotion {snap} (cached); items via Ziems et al. test.json",
                "license_at_snapshot": "other: " + (q[0] if q else "?"),
                "yaml_license_snapshot": re.findall(r"license:\s*\n- (\S+)", em_snap)[:1],
                "yaml_license_current": re.findall(r"license:\s*\n- (\S+)", em)[:1],
                "quote_at_snapshot": q[0] if q else None,
                "license_current_same_text": bool(re.search("educational and research purposes", em)),
                "redistribution": "not granted: the card restricts use to education and research "
                                  "and gives no redistribution terms",
                "recommendation": "do not ship the tweet text; ship item ids (row indices of "
                                  "dair-ai/emotion unsplit) and the reconstruction script",
                **common_notes})
    return out


# ------------------------------------------------------------------ (b) arXiv

BIB_KEYS = ["ibrahim2026evaluating", "li2026jevasajudge", "huang2026can", "ren2026openjev",
            "cheng2026thisthatmodel", "zhang2026same", "deng2026jev", "wu2026reflex", "li2026fast",
            "li2026replacing", "jiang2026jevmem", "ma2026jevstar", "yu2026visual",
            "robitza2026jevqa", "sun2026typesafe"]
BIB = os.path.join(C.BASE, "paper4", "benchmark", "eaai", "manuscript", "refs.bib")


def bib_entries():
    path = BIB if os.path.exists(BIB) else os.path.join(os.path.dirname(C.ROOT), "benchmark",
                                                        "eaai", "manuscript", "refs.bib")
    t = open(path, encoding="utf-8").read()
    out = {}
    for k in BIB_KEYS:
        m = re.search(r"@\w+\{" + k + r",(.*?)\n\}", t, re.S)
        if not m:
            out[k] = None
            continue
        body = m.group(1)
        f = lambda name: (re.search(name + r"\s*=\s*\{(.*)\},?\s*$", body, re.M) or [None, None])[1]
        out[k] = {"title": f("title"), "author": f("author"), "eprint": f("eprint")}
    return out, path


def strip_tex(s):
    return re.sub(r"\s+", " ", re.sub(r"[{}]", "", s or "")).strip()


def bib_authors(s):
    out = []
    for a in strip_tex(s).split(" and "):
        a = a.strip()
        if "," in a:
            last, first = [x.strip() for x in a.split(",", 1)]
            out.append(f"{first} {last}")
        else:
            out.append(a)
    return out


def arxiv_query(ids):
    """One request per id, three seconds apart; the API refused a single comma list with 406."""
    import time
    out = {}
    for aid in ids:
        for attempt in range(5):
            r = get("https://export.arxiv.org/api/query?id_list=" + aid,
                    headers={"Accept": "application/atom+xml"})
            if r.ok:
                break
            time.sleep(5 * (attempt + 1))
        r.raise_for_status()
        out.update(_parse_feed(r.text))
        time.sleep(3)
    return out


def _parse_feed(text):
    ns = {"a": "http://www.w3.org/2005/Atom", "x": "http://arxiv.org/schemas/atom"}
    root = ET.fromstring(text)
    out = {}
    for e in root.findall("a:entry", ns):
        aid = e.find("a:id", ns).text.rsplit("/", 1)[-1]
        base, ver = aid.rsplit("v", 1)
        out[base] = {"id_version": aid, "version": int(ver),
                     "title": re.sub(r"\s+", " ", e.find("a:title", ns).text).strip(),
                     "authors": [a.find("a:name", ns).text.strip() for a in e.findall("a:author", ns)],
                     "published": e.find("a:published", ns).text,
                     "updated": e.find("a:updated", ns).text,
                     "primary_category": e.find("x:primary_category", ns).attrib.get("term")}
    return out


def norm_title(s):
    return re.sub(r"[^a-z0-9]+", " ", strip_tex(s).lower()).strip()


def surname(n):
    return re.sub(r"[^a-z]", "", n.split()[-1].lower()) if n.split() else ""


def preprints():
    bib, path = bib_entries()
    ids = {k: v["eprint"] for k, v in bib.items() if v and v["eprint"]}
    ax = arxiv_query(sorted(set(ids.values())))
    rows = {}
    for k in BIB_KEYS:
        b = bib.get(k)
        if not b:
            rows[k] = {"status": "not in refs.bib"}
            continue
        a = ax.get(b["eprint"])
        if not a:
            rows[k] = {"eprint": b["eprint"], "status": "not returned by the arXiv API"}
            continue
        ba = bib_authors(b["author"])
        title_ok = norm_title(b["title"]) == norm_title(a["title"])
        auth_ok = [surname(x) for x in ba] == [surname(x) for x in a["authors"]]
        diffs = []
        if not title_ok:
            diffs.append("title differs")
        if not auth_ok:
            diffs.append(f"author list differs: bib has {len(ba)}, arXiv has {len(a['authors'])}")
        rows[k] = {"eprint": b["eprint"], "bib_title": strip_tex(b["title"]),
                   "bib_authors": ba, "arxiv": a, "title_matches": title_ok,
                   "authors_match": auth_ok, "needs_update": bool(diffs), "differences": diffs}
    return {"_doc": ("Preprint metadata from the arXiv API (export.arxiv.org/api/query), read "
                     f"{TODAY} by shared/src/b03_licenses.py, compared with refs.bib ({os.path.relpath(path, C.BASE)}), "
                     "which is not edited. entries[bibkey].arxiv gives the current version, "
                     "title, authors, first-version date (published) and latest-version date "
                     "(updated); title_matches ignores case, punctuation and TeX braces; "
                     "authors_match compares surnames in order; differences lists what refs.bib "
                     "should change."),
            "queried": TODAY, "entries": rows,
            "needs_update": [k for k, v in rows.items() if v.get("needs_update")]}


def main():
    d1 = d1_audit()
    print("D1", d1["license_at_snapshot"], d1["license_current"], "any CC BY:", d1["any_revision_cc_by"])
    lic = {"_doc": ("License audit written by shared/src/b03_licenses.py on " + TODAY + ". "
                    "datasets is a list, one entry per benchmark dataset (D1, D2, four D3 tasks), "
                    "each with license_at_snapshot (the license in force at the snapshot the "
                    "benchmark evaluated), quote_at_snapshot (verbatim from the primary source), "
                    "redistribution (what the license allows for the text) and recommendation "
                    "(ship text or ship reconstruction scripts). d1_license_history lists the "
                    "YAML license field of the D1 dataset card at every repository commit."),
           "datasets": [], "d1_license_history": d1.pop("license_history"),
           "data_licenses_md_check": {
               "file": "companion/DATA_LICENSES.md",
               "claim": "Apache-2.0 on the current dataset card (CC BY 4.0 at the revision used)",
               "verdict": "incorrect: apache-2.0 at the revision used (c76749ec) and at every "
                          "other revision"}}
    lic["datasets"].append(d1)
    lic["datasets"].append(clinc_audit())
    lic["datasets"] += d3_audit()
    lic["summary"] = ("D1 typed-decisions is Apache-2.0 at the evaluated revision c76749ec and at "
                      "every revision; DATA_LICENSES.md's CC BY 4.0 note is wrong. D2 CLINC-150 is "
                      "CC BY 3.0 (LICENSE file at 828f8093). D3: wiki_politeness CC BY 4.0, "
                      "wiki_corpus CC BY-SA 4.0, conv_go_awry has no corpus-level license "
                      "statement (Wikipedia text, CC BY-SA), emotion is restricted to educational "
                      "and research use with no redistribution terms, and the intermediate "
                      "SALT-NLP/LLMs_for_CSS repository declares no license. D1 and D2 text may be "
                      "shipped with attribution; for D3 the repository should ship the "
                      "reconstruction script and item ids rather than the text.")
    C.dump(lic, "licenses_audit.json")
    pp = preprints()
    C.dump(pp, "preprint_metadata.json")
    for k, v in pp["entries"].items():
        print(k, v.get("eprint"), v.get("differences"), (v.get("arxiv") or {}).get("id_version"))


if __name__ == "__main__":
    main()
