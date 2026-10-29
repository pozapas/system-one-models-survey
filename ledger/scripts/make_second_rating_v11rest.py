"""Second-rating workbooks for the first-sweep studies that no second rater has graded.

The version 1.1 second rating graded 8 of the 27 studies of the first sweep (notes/second_rater_key); the version 1.2
second rating graded every study of the second sweep. This script gives the remaining first-sweep studies the same
treatment as the second sweep: each is graded on the five domains and one of its ledger values (not one already read
in version 1.1) is read from its source, split over N raters. The Inclusion and Heads sheets are present but empty,
so that second_rating_agreement_v12.py can score the returned workbooks with --key and --orig. The written anchors
and the rules added at adjudication on 2026-10-29 (PROTOCOL.md) are given to the raters. The first ratings go only
to the key file.

Usage (needs openpyxl):  python make_second_rating_v11rest.py [--raters 5] [--seed 20261030]
"""
import argparse
import csv
import json
import random
from collections import defaultdict
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font

from make_second_rater import ANCHORS, DOMAINS
from make_second_rating_v12 import HEAD_PANELS, LEDGER, MIN_PER, SURVEY, sheet, split

OUT = SURVEY / "notes" / "second_rating_v11rest"
KEY = SURVEY / "notes" / "second_rating_v11rest_key"
V11_KEY = SURVEY / "notes" / "second_rater_key" / "first_rater_key.json"
RULES = [
    "Version pinning: an exact model version or a revision, together with run dates, is enough for low; low requires "
    "this for every compared system that contributes to the results, including baselines and scoring judges, and the "
    "domain is rated by the weakest. An incomplete version, a minor version such as Jev 1.13, or missing run dates is "
    "unclear. A missing version identifier, or an alias the study does not resolve to a served version, is high.",
    "Test-set exposure: a third-party public set released during 2026 is unclear; new items built by the authors and "
    "private items are low; a public set released before 2026 with a reported overlap or contamination check is "
    "unclear, even when the check is partial; a mixture of new items and public pre-2026 sets is unclear.",
    "Reference labels: the observed outcome of the system's own actions in an environment, game or simulator is a task "
    "outcome, so low; a stored reference answer computed by a program or simulator is synthetic, so high; when the "
    "study does not say how its labels were made, unclear; headline results with different reference types, "
    "unclear; an endpoint that needs no external reference label is low.",
    "Sampling and reporting: a standard deviation or standard error over seeds is not an interval on a headline "
    "result; a confirmed count contradiction is high, but rounded percentages alone do not establish one.",
    "Tuning-budget parity: a setting selected with feedback from the scored evaluation items is high, even when "
    "disclosed or applied to every system; a disclosed and bounded difference in training, instructions or budget is "
    "unclear; a predeclared descriptive operating point does not by itself establish tuning.",
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raters", type=int, default=5)
    ap.add_argument("--seed", type=int, default=20261030)
    a = ap.parse_args()
    rng = random.Random(a.seed)

    v11 = json.loads(V11_KEY.read_text(encoding="utf-8"))
    rated, read = set(v11["rob"]), {e["row_id"] for e in v11["extraction"].values()}
    first = list(csv.DictReader((LEDGER / "parts" / "rob_v11.csv").open(encoding="utf-8-sig")))
    rob = {r["study_key"]: r for r in csv.DictReader((LEDGER / "rob.csv").open(encoding="utf-8-sig"))}
    studies = [rob[r["study_key"]] for r in first if r["study_key"] not in rated]
    rng.shuffle(studies)
    by_study, url = defaultdict(list), {}
    for r in csv.DictReader((LEDGER / "ledger.csv").open(encoding="utf-8-sig")):
        url.setdefault(r["study_key"], r["source_url"])
        if r["value"].strip() and r["location"].strip() and r["row_id"] not in read:
            by_study[r["study_key"]].append(r)

    key = {"seed": a.seed, "raters": {}}
    OUT.mkdir(parents=True, exist_ok=True)
    KEY.mkdir(parents=True, exist_ok=True)
    for i, share in enumerate(split(studies, a.raters)):
        rid = f"S{i + 1:02d}"
        ext = sorted((rng.choice(by_study[s["study_key"]]) for s in share if by_study[s["study_key"]]),
                     key=lambda r: (r["study_key"], r["row_id"]))
        minutes = len(share) * MIN_PER["rob"] + len(ext) * MIN_PER["extraction"]
        wb = Workbook()
        ins = wb.active
        ins.title = "Instructions"
        lines = [
            f"Second rating of the survey 'System One Decision Models', first-sweep workbook {rid}.",
            f"Your share: {len(share)} studies to grade on five domains and {len(ext)} values to read from those same "
            f"studies. Expected time: about {minutes / 60:.1f} hours. The Inclusion and Heads sheets are empty.",
            "Read the guide (Second_rating_guide.docx) before you start; its RiskOfBias and Extraction sections apply. "
            "Work alone, do not discuss items with the other raters, and do not open the survey, its tables or its "
            "repository.",
            "Fill only the yellow cells. Leave a cell empty if you cannot decide and explain why in the notes column.",
            "",
            "Rating anchors for the RiskOfBias sheet:",
        ] + [f"{name}: {ANCHORS[k]}" for k, name, _ in DOMAINS] + [
            "",
            "Rules for cases the anchors leave open:",
        ] + RULES + ["", "Save the workbook under its own name and return it when done."]
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
              [[j + 1, r["study_key"], r["source_url"], r["location"], r["model"], r["dataset"], r["metric"],
                r["value_key"].split(".", 1)[-1], "", ""] for j, r in enumerate(ext)],
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
        print(f"{rid}: {len(share)} studies, {len(ext)} values, ~{minutes / 60:.1f} h")
    (KEY / "first_rating_key.json").write_text(json.dumps(key, indent=1), encoding="utf-8")
    print("studies:", len(studies), "| workbooks:", OUT, "| key:", KEY / "first_rating_key.json")


if __name__ == "__main__":
    main()
