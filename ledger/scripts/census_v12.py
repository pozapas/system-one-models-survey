"""Version 1.2 census counts: the Hugging Face entries created from 2026-09-15 to 2026-10-28.

Reads shared/census/census_screened_v12.csv (tiers from pattern rules) and the hand checks of every rule-tiered
T1 card in t1_check_C1.csv to t1_check_C3.csv, applies the checked verdicts, drops repositories that duplicate
another (identical creation time and weights), and writes census_screened_v12_final.csv and
census_numbers_v12.json (macros \\cenval{hf12.*}). T1 families are the hand-assigned family labels, plus one
family each for the named vendor releases that were checked separately. T2 and D tiers are the pattern-rule
tiers, corrected only where a T1 check moved a card into them.
"""
import csv
import glob
import json
import os
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as K

NAMED_FAMILY = {"perplexity-ai/": "pplx-decider (Perplexity)", "Cloudflare/": "Clef (Cloudflare)",
                "MachineFi/": "Trio-Spark (MachineFi)"}
DUPLICATES = {"ZichenAI/layazh-zh"}   # same createdAt and weights as NovaAI6868/layazh-zh (t1_check_C3)


def main():
    rows = list(csv.DictReader(open(os.path.join(K.CENSUS, "census_screened_v12.csv"), encoding="utf-8")))
    checks = {}
    for p in sorted(glob.glob(os.path.join(K.CENSUS, "t1_check_C*.csv"))):
        for r in csv.DictReader(open(p, encoding="utf-8-sig")):
            checks[r["id"]] = r
    out, fams = [], set()
    for r in rows:
        if r["id"] in DUPLICATES:
            continue
        r = dict(r, family="", checked="")
        c = checks.get(r["id"])
        if c:
            r["tier"], r["checked"] = c["verdict"].strip(), "hand"
            r["relation"], r["parent"] = c.get("relation", ""), c.get("parent", "")
            r["family"] = c.get("family", "").strip()
        elif r["tier"] == "T1":
            r["checked"] = "hand (named release)"
            r["family"] = next((f for pre, f in NAMED_FAMILY.items() if r["id"].startswith(pre)), r["id"])
        if r["tier"] == "T1":
            fams.add(r["family"].lower())
        out.append(r)
    cols = list(out[0].keys())
    with open(os.path.join(K.CENSUS, "census_screened_v12_final.csv"), "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        w.writerows(out)
    tiers = Counter(r["tier"] for r in out)
    t2 = Counter(r["relation"] or "other" for r in out if r["tier"] == "T2")
    unchecked_t1 = [r["id"] for r in out if r["tier"] == "T1" and not r["checked"]]
    src = "shared/census/census_numbers_v12.json"
    val = lambda v, note: {"text": f"{v:,}" if isinstance(v, int) else v, "source": src, "note": note}
    V = {"hf12": {
        "entries": val(len(out), "Hugging Face entries created 2026-09-15 to 2026-10-28 not in the first census"),
        "t1Count": val(tiers["T1"], "original implementations, every card checked by hand"),
        "t1Families": val(len(fams), "recipe families among them (author, backbone and recipe)"),
        "t1Rejected": val(sum(1 for c in checks.values() if c["verdict"].strip() != "T1"),
                          "rule-tiered T1 cards that the hand check moved to T2 or X"),
        "t2Count": val(tiers["T2"], "derivatives (pattern-rule tiers)"),
        "t2FormatConversion": val(t2["format_conversion"], "T2 format conversions"),
        "t2FinetuneDomain": val(t2["finetune_domain"], "T2 domain fine-tunes"),
        "dCount": val(tiers["D"], "datasets"),
        "xCount": val(tiers["X"], "screened out"),
    }}
    gh = list(csv.DictReader(open(os.path.join(K.CENSUS, "census_github_screened_v12.csv"), encoding="utf-8")))
    cat = Counter(r.get("category", "") for r in gh)
    V["gh12"] = {
        "countTotal": val(len(gh), "GitHub repositories created 2026-09-15 to 2026-10-28 that pass the relevance screen"),
        "countEvaluation": val(cat["evaluation"], "evaluation packages (category from rules and a classifier)"),
        "countLocalServer": val(cat["local_server"], "local servers"),
        "countTraining": val(cat["open_model_training"], "open-model training code"),
    }
    json.dump({"values": V}, open(os.path.join(K.CENSUS, "census_numbers_v12.json"), "w", encoding="utf-8"), indent=1)
    print({k: v["text"] for k, v in V["hf12"].items()})
    if unchecked_t1:
        print("T1 rows with no check:", unchecked_t1[:10])


if __name__ == "__main__":
    main()
