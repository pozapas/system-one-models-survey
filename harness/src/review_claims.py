"""List every generated number in the manuscript beside the sentence that uses it.

The numbers audit proves that no value was typed by hand. It cannot prove that a
label denotes what the surrounding sentence says it denotes, which is a
different and more dangerous error. This script prints each macro with its
value, its source file and its context, so that correspondence can be read.
"""
import json
import sys
sys.stdout.reconfigure(encoding="utf-8")
import os
import re

import common as C

MANU = os.path.join(os.environ.get("P4_MANU") or os.path.join(os.path.dirname(C.ROOT), "benchmark", "manuscript"), "sections")
SOURCES = sorted(f for f in os.listdir(MANU) if f.endswith(".tex"))


def fmt(rec):
    v, f = rec["value"], rec.get("fmt")
    if isinstance(v, str):
        return v
    if f:
        try:
            return format(v, f)
        except (ValueError, TypeError):
            pass
    return f"{v:,}" if isinstance(v, int) else f"{v:.3f}"


def run():
    N = json.load(open(os.path.join(C.RESULTS, "numbers.json"), encoding="utf-8"))
    missing, total = [], 0
    for name in SOURCES:
        p = os.path.join(MANU, name)
        if not os.path.exists(p):
            continue
        flat = re.sub(r"\s+", " ", open(p, encoding="utf-8").read())
        print(f"===== {name}")
        for m in re.finditer(r"\\num\{([^}]+)\}", flat):
            lab = m.group(1)
            total += 1
            lo, hi = max(0, m.start() - 100), min(len(flat), m.end() + 50)
            ctx = flat[lo:hi].replace("\\num{" + lab + "}", " <<VALUE>> ")
            if lab not in N:
                missing.append(lab)
                print(f"  MISSING  {lab}\n           ...{ctx}...")
                continue
            print(f"  {fmt(N[lab]):>10s}  {lab}")
            print(f"             ...{ctx}...")
    print(f"\n{total} number macros, {len(missing)} missing labels")
    if missing:
        print("  missing:", missing)
    return len(missing)


if __name__ == "__main__":
    run()
