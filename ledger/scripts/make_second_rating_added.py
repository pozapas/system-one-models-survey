"""Second-rating workbooks for the studies added at the adjudication of 2026-10-29.

Six papers excluded at screening were included at that adjudication and graded once under the adjudicated rules. This
script gives them the treatment every other graded study had: each is graded on the five domains and one of its
ledger values is read from its source, split over N raters, blind to the first rating. The studies are the graded
studies that appear in no earlier key (notes/second_rater_key, second_rating_v11rest_key, second_rating_v12_key). Every
arXiv source is linked with the exact version the ledger extracted (read from the study note), so that raters and
the first rating read the same text. The workbook layout, rules and key format are those of
make_second_rating_v11rest.py, so second_rating_agreement_v12.py scores the returned workbooks with --key and --orig.

Usage (needs openpyxl):  python make_second_rating_added.py [--raters 3] [--seed 20261031]
"""
import argparse
import csv
import json
import random
import re
from collections import defaultdict

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font

from make_second_rater import ANCHORS, DOMAINS
from make_second_rating_v11rest import RULES
from make_second_rating_v12 import HEAD_PANELS, LEDGER, MIN_PER, SURVEY, sheet, split

NOTES = SURVEY / "notes"
OUT = NOTES / "second_rating_added"
KEY = NOTES / "second_rating_added_key"
EARLIER = [NOTES / "second_rater_key" / "first_rater_key.json",
           NOTES / "second_rating_v11rest_key" / "first_rating_key.json",
           NOTES / "second_rating_v12_key" / "first_rating_key.json"]
G6 = ("Model names: a name with a version or size token but no dated snapshot or revision is an incomplete version, so "
      "unclear; it is an unresolved alias, so high, only when the study itself calls it an alias, latest, preview or a "
      "free-tier tag that it does not resolve. Outside knowledge about whether a provider name rolls is not used.")


def rated(path):
    d = json.loads(path.read_text(encoding="utf-8"))
    if "raters" not in d:
        return set(d["rob"])
    return set().union(*(r["rob"] for r in d["raters"].values()))


def versioned(url, study_key):
    m = re.search(r"arxiv\.org/abs/(\d{4}\.\d{4,5})$", url)
    if not m:
        return url
    note = (LEDGER / "studies" / f"{study_key}.md")
    v = re.search(re.escape(m.group(1)) + r"(v\d+)", note.read_text(encoding="utf-8")) if note.exists() else None
    return url + v.group(1) if v else url


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raters", type=int, default=3)
    ap.add_argument("--seed", type=int, default=20261031)
    a = ap.parse_args()
    rng = random.Random(a.seed)

    done = set().union(*(rated(p) for p in EARLIER))
    rob = {r["study_key"]: r for r in csv.DictReader((LEDGER / "rob.csv").open(encoding="utf-8-sig"))}
    studies = [r for k, r in sorted(rob.items()) if k not in done]
    rng.shuffle(studies)
    by_study, url = defaultdict(list), {}
    for r in csv.DictReader((LEDGER / "ledger.csv").open(encoding="utf-8-sig")):
        url.setdefault(r["study_key"], versioned(r["source_url"], r["study_key"]))
        if r["value"].strip() and r["location"].strip():
            by_study[r["study_key"]].append(r)

    key = {"seed": a.seed, "raters": {}}
    OUT.mkdir(parents=True, exist_ok=True)
    KEY.mkdir(parents=True, exist_ok=True)
    for i, share in enumerate(split(studies, a.raters)):
        rid = f"A{i + 1:02d}"
        ext = sorted((rng.choice(by_study[s["study_key"]]) for s in share if by_study[s["study_key"]]),
                     key=lambda r: (r["study_key"], r["row_id"]))
        minutes = len(share) * MIN_PER["rob"] + len(ext) * MIN_PER["extraction"]
        wb = Workbook()
        ins = wb.active
        ins.title = "Instructions"
        lines = [
            f"Second rating of the survey 'System One Decision Models', workbook {rid}.",
            f"Your share: {len(share)} studies to grade on five domains and {len(ext)} values to read from those same "
            f"studies. Expected time: about {minutes / 60:.1f} hours. The Inclusion and Heads sheets are empty.",
            "Read the guide (Second_rating_guide.docx) before you start; its RiskOfBias and Extraction sections apply. "
            "Work alone, do not discuss items with the other raters, and do not open the survey, its tables or its "
            "repository.",
            "Each source link names the exact paper version to read (for example v1). Read that version, not a later one.",
            "Fill only the yellow cells. Leave a cell empty if you cannot decide and explain why in the notes column.",
            "",
            "Rating anchors for the RiskOfBias sheet:",
        ] + [f"{name}: {ANCHORS[k]}" for k, name, _ in DOMAINS] + [
            "",
            "Rules for cases the anchors leave open:",
        ] + RULES + [G6, "", "Save the workbook under its own name and return it when done."]
        for line in lines:
            ins.append([line])
        ins.column_dimensions["A"].width = 150
        for row in ins.iter_rows():
            row[0].alignment = Alignment(wrap_text=True)
        ins["A1"].font = Font(bold=True, size=13)

        sheet(wb, "Inclusion", ["arxiv_id", "title", "abstract", "link", "decision", "notes"], [],
              {"decision", "notes"}, [14, 40, 90, 32, 12, 30])
        rob_rows = [[s["study_key"], url.get(s["study_key"], ""), name, "", ""] for s in share for k, name, _ in DOMAINS]
        sheet(wb, "RiskOfBias", ["study", "source", "domain", "rating", "justification"], rob_rows,
              {"rating", "justification"}, [26, 40, 28, 12, 70], ("rating", ["low", "unclear", "high"]))
        sheet(wb, "Extraction",
              ["item", "study", "source", "location", "model", "dataset", "metric", "detail", "value", "notes"],
              [[j + 1, r["study_key"], url.get(r["study_key"], r["source_url"]), r["location"], r["model"], r["dataset"],
                r["metric"], r["value_key"].split(".", 1)[-1], "", ""] for j, r in enumerate(ext)],
              {"value", "notes"}, [6, 24, 36, 26, 28, 30, 28, 30, 12, 30])
        sheet(wb, "Heads", ["item", "repository", "card", "head", "evidence", "notes"], [],
              {"head", "evidence", "notes"}, [6, 44, 52, 22, 60, 30], ("head", HEAD_PANELS))
        wb.save(OUT / f"second_rating_{rid}.xlsx")
        key["raters"][rid] = {
            "inclusion": {},
            "rob": {s["study_key"]: {name: s[f"{k}_rating"] for k, name, _ in DOMAINS} for s in share},
            "extraction": {str(j + 1): {"row_id": r["row_id"], "value": r["value"]} for j, r in enumerate(ext)},
            "heads": {},
        }
        print(f"{rid}: {len(share)} studies ({', '.join(s['study_key'] for s in share)}), {len(ext)} values, "
              f"~{minutes / 60:.1f} h")
    (KEY / "first_rating_key.json").write_text(json.dumps(key, indent=1), encoding="utf-8")
    print("studies:", len(studies), "| workbooks:", OUT, "| key:", KEY / "first_rating_key.json")


if __name__ == "__main__":
    main()
