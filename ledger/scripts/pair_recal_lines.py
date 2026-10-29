"""Join raw and recalibrated ECE that version 1.2 selection lines entered as two lines into one paired line.

Percent-scale ECE was read with expression a/100, which synthesis.py could not apply to the second number of a
pair before version 1.2, so the raw and the recalibrated value were entered as separate lines. Each pair
below gets b_row, b_field and b_pattern from its recalibrated line, which is kept with include=no and a
reason naming the line it was joined into. synthesis.py scales b by 1/100 whenever the expression is a/100.
"""
import csv
import glob
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as K

PAIRS = {  # raw record -> recalibrated record (same study, same model, same items)
    "linPact": "linPactRecal", "linNimbleRecipe": "linNimbleRecipeRecal", "secjev4b": "secjev4bScaled",
    "secjev9bRaw": "secjev9bScaled", "dekaPfrCeRaw": "dekaPfrCeScaled", "dekaPfrPgRaw": "dekaPfrPgScaled",
    "yanOpenEce": "yanOpenEceRecal",
}


def main():
    done = 0
    for p in sorted(glob.glob(os.path.join(K.LEDGER, "selection_parts", "sel_*.csv"))):
        rows = list(csv.DictReader(open(p, encoding="utf-8-sig")))
        if not rows:
            continue
        cols = list(rows[0].keys())
        by = {(r["analysis"], r["record"]): r for r in rows}
        changed = False
        for raw, rec in PAIRS.items():
            for an in ("r2OpenEce", "r2JevEce"):
                a, b = by.get((an, raw)), by.get((an, rec))
                if not a or not b or b["include"] != "yes":
                    continue
                a["b_row"] = b["row_id"]
                a["b_field"] = b["a_field"] or "value"
                a["b_pattern"] = b["a_pattern"]
                b["include"] = "no"
                b["reason"] = f"Joined into {raw} as its recalibrated value (pair_recal_lines.py). " + b["reason"]
                changed, done = True, done + 1
        if changed:
            with open(p, "w", encoding="utf-8", newline="") as fh:
                w = csv.DictWriter(fh, fieldnames=cols)
                w.writeheader()
                w.writerows(rows)
    print(f"joined {done} of {len(PAIRS)} pairs")


if __name__ == "__main__":
    main()
