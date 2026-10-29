"""Agreement between the two codings of the comparator class (comparator_class_first.csv and comparator_class_blind.csv).

Prints Cohen's kappa and the share of agreement per analysis, writes comparator_class_disagreements.csv for
adjudication, and writes shared/ledger/comparator_agreement.json (macros \\synval{cmpAgree.*}).
"""
import csv
import json
import os
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as K


def load(name):
    return {(r["analysis"], r["record"]): r for r in csv.DictReader(open(os.path.join(K.LEDGER, name), encoding="utf-8-sig"))}


def kappa(pairs):
    n = len(pairs)
    po = sum(a == b for a, b in pairs) / n
    ca, cb = Counter(a for a, _ in pairs), Counter(b for _, b in pairs)
    pe = sum(ca[k] * cb[k] for k in set(ca) | set(cb)) / n ** 2
    return po, (po - pe) / (1 - pe) if pe < 1 else 1.0


def main():
    first, blind = load("comparator_class_first.csv"), load("comparator_class_blind.csv")
    src = "shared/ledger/comparator_agreement.json"
    out, dis = {}, []
    for an, lab in (("r1Gap", "r1"), ("gapJevBest", "gap")):
        keys = sorted(k for k in first if k[0] == an and k in blind)
        pairs = [(first[k]["class"], blind[k]["class"]) for k in keys]
        po, k = kappa(pairs)
        out[lab + "Lines"] = {"text": str(len(pairs)), "source": src}
        out[lab + "Agreement"] = {"text": f"{100 * po:.0f}", "source": src, "note": "percent of lines coded alike"}
        out[lab + "Kappa"] = {"text": f"{k:.2f}", "source": src, "note": "Cohen's kappa"}
        out[lab + "Disagree"] = {"text": str(sum(a != b for a, b in pairs)), "source": src}
        print(f"{an}: {len(pairs)} lines, agreement {po:.2f}, kappa {k:.2f}")
        for kk in keys:
            if first[kk]["class"] != blind[kk]["class"]:
                dis.append(dict(analysis=an, record=kk[1], study=first[kk]["study"], first=first[kk]["class"],
                                blind=blind[kk]["class"], first_reason=first[kk]["reason"], blind_reason=blind[kk]["reason"]))
    json.dump({"values": {"cmpAgree": out}}, open(os.path.join(K.LEDGER, "comparator_agreement.json"), "w", encoding="utf-8"), indent=1)
    with open(os.path.join(K.LEDGER, "comparator_class_disagreements.csv"), "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(dis[0].keys()) if dis else ["analysis"])
        w.writeheader()
        w.writerows(dis)
    print(len(dis), "disagreements -> comparator_class_disagreements.csv")


if __name__ == "__main__":
    main()
