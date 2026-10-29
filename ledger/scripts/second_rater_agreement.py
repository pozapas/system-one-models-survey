"""Compute first-versus-second rater agreement from the filled workbook and the key.

Inclusion and risk-of-bias ratings: raw agreement and Cohen's kappa (unweighted; the risk-of-bias ratings also get a
linearly weighted kappa on the order low < unclear < high). Extraction: share of values that match the first rater
after normalizing number formatting, with a relative tolerance of 0.5 percent for rounding differences.
Writes shared/ledger/second_rater.json, whose values can be cited in Section S3 through \\synval{...} once the
collector reads that file, and prints a draft sentence for S3.

Usage (needs openpyxl):  python second_rater_agreement.py [filled_workbook.xlsx] [output.json] [key prefix, e.g. sr1]
"""
import json
import re
import sys
from collections import Counter
from pathlib import Path

from openpyxl import load_workbook

SURVEY = Path(__file__).resolve().parents[1]
KEY = SURVEY / "notes" / "second_rater_key" / "first_rater_key.json"
OUT = SURVEY.parent / "shared" / "ledger" / "second_rater.json"
ORDER = {"low": 0, "unclear": 1, "some_concerns": 1, "high": 2}


def kappa(a, b, weights=None):
    cats = sorted(set(a) | set(b))
    n = len(a)
    if n == 0:
        return None
    w = (lambda x, y: 1.0 if x == y else 0.0) if weights is None else \
        (lambda x, y: 1 - abs(weights[x] - weights[y]) / (max(weights.values()) or 1))
    po = sum(w(x, y) for x, y in zip(a, b)) / n
    pa, pb = Counter(a), Counter(b)
    pe = sum(w(x, y) * pa[x] * pb[y] for x in cats for y in cats) / n ** 2
    return None if pe == 1 else (po - pe) / (1 - pe)


def num(s):
    s = str(s).strip().replace("−", "-").replace(",", "")
    m = re.search(r"-?\d+(?:\.\d+)?", s)
    return float(m.group()) if m else None


def decimals(s):
    m = re.search(r"\.(\d+)", str(s))
    return len(m.group(1)) if m else 0


def same_value(first, second):
    """Equal as printed: identical text, the same number at the coarser of the two precisions, or a fraction
    that equals a percentage (83/84 against 98.8)."""
    a_txt, b_txt = str(first).strip().lower(), str(second).strip().lower()
    if a_txt == b_txt:
        return True
    frac = re.fullmatch(r"(\d+)\s*/\s*(\d+)", b_txt)
    a = num(first)
    if frac and a is not None:
        b = 100 * int(frac.group(1)) / int(frac.group(2))
        return round(b, decimals(first)) == a
    b = num(second)
    if a is None or b is None:
        nums_a, nums_b = re.findall(r"\d+/\d+", a_txt), re.findall(r"\d+/\d+", b_txt)
        return bool(nums_a) and sorted(set(nums_a)) == sorted(set(nums_b))
    d = min(decimals(first), decimals(second))
    return round(a, d) == round(b, d)


def rows(ws):
    it = ws.iter_rows(values_only=True)
    head = next(it)
    return [dict(zip(head, r)) for r in it if any(v not in (None, "") for v in r)]


def main():
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else SURVEY / "notes" / "second_rater" / "second_rater_workbook.xlsx"
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else OUT
    key = json.loads(KEY.read_text(encoding="utf-8"))
    wb = load_workbook(path)

    inc = [(key["inclusion"][r["arxiv_id"]], str(r["decision"]).strip().lower())
           for r in rows(wb["Inclusion"]) if r.get("decision")]
    ext = []
    for r in rows(wb["Extraction"]):
        if r.get("value") in (None, ""):
            continue
        ext.append(same_value(key["extraction"][str(r["item"])]["value"], r["value"]))
    rob = []
    for r in rows(wb["RiskOfBias"]):
        if r.get("rating"):
            first = key["rob"][r["study"]][r["domain"]]
            rob.append((first if first != "some_concerns" else "unclear", str(r["rating"]).strip().lower()))

    pre = sys.argv[3] if len(sys.argv) > 3 else "sr"
    res = {
        "sr.inclusionAgreeN": sum(x == y for x, y in inc),
        "sr.extractionMatchN": sum(ext),
        "sr.robAgreeN": sum(x == y for x, y in rob),
        "sr.inclusionN": len(inc),
        "sr.inclusionAgreement": round(sum(x == y for x, y in inc) / len(inc), 3) if inc else None,
        "sr.inclusionKappa": round(kappa(*zip(*inc)), 2) if inc and kappa(*zip(*inc)) is not None else None,
        "sr.extractionN": len(ext),
        "sr.extractionMatch": round(sum(ext) / len(ext), 3) if ext else None,
        "sr.robN": len(rob),
        "sr.robAgreement": round(sum(x == y for x, y in rob) / len(rob), 3) if rob else None,
        "sr.robKappa": round(kappa(*zip(*rob)), 2) if rob else None,
        "sr.robWeightedKappa": round(kappa(*zip(*rob), weights=ORDER), 2) if rob else None,
    }
    res = {pre + k[2:]: v for k, v in res.items()}
    doc = json.loads(out.read_text(encoding="utf-8")) if out.exists() else {"values": {}}
    doc["values"].update({k: {"text": str(v), "source": str(path.name)} for k, v in res.items()})
    out.write_text(json.dumps(doc, indent=2), encoding="utf-8")
    res = {"sr" + k[len(pre):]: v for k, v in res.items()}
    print(json.dumps(res, indent=1))
    print("\nDraft sentence for Section S3:")
    print(f"A second rater independently repeated the screening of all {res['sr.inclusionN']} arXiv candidates "
          f"(agreement {res['sr.inclusionAgreement']}, kappa {res['sr.inclusionKappa']}), the extraction of "
          f"{res['sr.extractionN']} sampled ledger values ({res['sr.extractionMatch']} matching) and the risk-of-bias "
          f"ratings of {res['sr.robN'] // 5 if res['sr.robN'] else 0} studies (weighted kappa {res['sr.robWeightedKappa']}).")


if __name__ == "__main__":
    main()
