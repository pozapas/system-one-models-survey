"""Decision-head type of every T1 original implementation (first census and version 1.2).

Reads the hand codes in shared/census/head_check_H1.csv to H4.csv (under HEAD_CODING_BRIEF.md), adds each entry's
family (the naming rule of t_s5_census.py for the first census, the hand-assigned family for version 1.2), and
writes shared/census/census_heads.csv and shared/census/census_heads.json (macros \\cenval{heads.*}): for each
head type, the number of originals and of families. A family whose checkpoints carry different head types counts
once under each. Codes that disagree with the hand-placed cards of Figure 3 (f03_heads.CARD_PANELS) are listed.
"""
import csv
import glob
import json
import os
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as K
from t_s5_census import family_of

PANELS = ["a", "b", "c", "d", "e", "undisclosed"]
LABEL = {"a": "fixedSlots", "b": "optionMarkers", "c": "labelLogits", "d": "pairScoring", "e": "constrainedDecoding",
         "undisclosed": "undisclosed"}


def main():
    codes = {}
    for p in sorted(glob.glob(os.path.join(K.CENSUS, "head_check_H*.csv"))):
        for r in csv.DictReader(open(p, encoding="utf-8-sig")):
            codes[r["id"].strip()] = r
    fam = {}
    for r in csv.DictReader(open(os.path.join(K.CENSUS, "census_screened.csv"), encoding="utf-8")):
        if r["tier"] == "T1":
            fam[r["id"]] = family_of(r["id"])
    for r in csv.DictReader(open(os.path.join(K.CENSUS, "census_screened_v12_final.csv"), encoding="utf-8")):
        if r["tier"] == "T1":
            fam[r["id"]] = (r.get("family") or r["id"]).lower()
    missing = sorted(set(fam) - set(codes))
    out, n, fams = [], defaultdict(int), defaultdict(set)
    for i, f in sorted(fam.items(), key=lambda kv: kv[0].lower()):
        c = codes.get(i)
        if not c:
            continue
        panel = c["panel"].strip().lower()
        if panel not in PANELS:
            sys.exit(f"{i}: unknown panel {panel}")
        out.append(dict(id=i, family=f, panel=panel, quote=c.get("quote", ""), source=c.get("source", ""), note=c.get("note", "")))
        n[panel] += 1
        fams[panel].add(f)
    with open(os.path.join(K.CENSUS, "census_heads.csv"), "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0].keys()))
        w.writeheader()
        w.writerows(out)
    src = "shared/census/census_heads.json"
    V = {"heads": {"coded": {"text": str(len(out)), "source": src, "note": "T1 originals coded by decision head"}}}
    for p in PANELS:
        V["heads"][LABEL[p]] = {"text": str(n[p]), "source": src, "note": f"originals with head type {p}"}
        V["heads"][LABEL[p] + "Families"] = {"text": str(len(fams[p])), "source": src, "note": f"families with head type {p}"}
    json.dump({"values": V}, open(os.path.join(K.CENSUS, "census_heads.json"), "w", encoding="utf-8"), indent=1)
    print({p: (n[p], len(fams[p])) for p in PANELS}, "coded", len(out), "missing", missing[:10])
    try:
        from f03_heads import CARD_PANELS
    except Exception as e:  # yaml is needed by f03_heads
        print("could not compare with Figure 3:", e)
        return
    by_name = {os.path.basename(k).replace(".yaml", "").replace("__", "/"): v[0] for k, v in CARD_PANELS.items()}
    for k, panel in by_name.items():
        for i in out:
            if i["id"].lower() == k.lower() and i["panel"] != panel:
                print(f"  differs from Figure 3: {i['id']} coded {i['panel']}, figure {panel}")


if __name__ == "__main__":
    main()
