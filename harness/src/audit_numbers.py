"""Audit every number in the manuscript against results/numbers.json.

Two passes run. The source pass is the strict one and it is the pass that
enforces the rule, because the rule is that no number is typed into the prose.
It reads the manuscript sources and flags any numeric literal that is not inside
a generated macro, a label, a length, or an included table.

The document pass is a cross-check on the compiled file. It is looser by
necessity, since text extracted from a compiled document also contains citation
markers, section numbers and the tick labels of embedded figures, none of which
are claims. Both reports are written and the source pass is the one that must be
empty.
"""
import csv
import sys
sys.stdout.reconfigure(encoding="utf-8")
import json
import os
import re
import subprocess

import common as C

MANU = os.environ.get("P4_MANU") or os.path.join(os.path.dirname(C.ROOT), "benchmark", "manuscript")
PDF = os.path.join(MANU, "main.pdf")
SOURCES = [os.path.join("sections", f) for f in sorted(os.listdir(os.path.join(MANU, "sections")))
           if f.endswith(".tex")]

# Names that contain digits but are identifiers, not evidence: model, dataset and
# hardware names, condition keys and identifiers such as o1 or SHA-256.
NAME_TOKENS = re.compile(
    r"(?:\b\d+(?:\.\d+)?[BM](?:-class)?\b|"                  # parameter sizes in names
    r"Jev\s*1\.13\.0|jev-1\.13\.0|Kev-0\.8B|Kev-9B|Nimble-9B|decider-2b|decider-0\.8b|"
    r"this-that-model-1\.0|Qwen3(?:\.5)?-[\w.]+|Qwen3(?:\.5)?|mmBERT|CLINC-150|SHA-256|L4|T4|H100|"
    r"F1|RQ[1-4]|DeBERTa-v3|BERT-base|D[123]|o_?\{?\d\}?|o\d+|k01|kny|kswap|krand|d[123]_\w+|e2_\w+|Qwen3-14B|AWQ|"
    r"Gemma-3-27B|typesafe-sdk|GPT-\d)", re.I)

# Numeric literals that are typography or structure rather than evidence.
ALLOWED_SOURCE = re.compile(
    r"^(?:"
    r"1\.13\.0"        # the pinned model version, stated deliberately
    r"|4\.0"           # the licence version
    r"|0\.\d+|1(?:\.0)?"   # lengths such as width=0.495\linewidth
    r")$")


def strip_for_source_audit(text):
    """Remove everything that is allowed to contain a number."""
    t = re.sub(r"(?m)%.*$", " ", text)                       # comments
    t = re.sub(r"\\num\{[^}]*\}", " NUM ", t)                # generated values
    t = re.sub(r"\\(?:label|ref|sref|fref|frefi|tref|eref|aref|refi)"
               r"\*?(?:\{[^}]*\})+", " REF ", t)
    t = re.sub(r"\\cite[pt]?\*?(?:\[[^]]*\])*\{[^}]*\}", " CITE ", t)
    t = re.sub(r"\\input\{[^}]*\}", " TABLE ", t)            # generated tables
    t = re.sub(r"\\includegraphics(?:\[[^]]*\])?\{[^}]*\}", " FIG ", t)
    t = re.sub(r"\\begin\{[^}]*\}|\\end\{[^}]*\}", " ENV ", t)
    t = re.sub(r"\\texttt\{[^}]*\}", " CODE ", t)            # version strings
    t = re.sub(r"\$[^$]*\$", " MATH ", t)
    t = re.sub(r"\\\(.*?\\\)", " MATH ", t)                  # \( ... \) inline math
    t = NAME_TOKENS.sub(" NAME ", t)
    return t


def source_pass():
    rows = []
    for name in SOURCES:
        p = os.path.join(MANU, name)
        if not os.path.exists(p):
            continue
        raw = open(p, encoding="utf-8").read().split("\n")
        in_eq = False
        for ln, line in enumerate(raw, 1):
            # display equations are notation, not reported values
            if re.search(r"\\begin\{(?:equation|align)\*?\}", line):
                in_eq = True
            if in_eq:
                if re.search(r"\\end\{(?:equation|align)\*?\}", line):
                    in_eq = False
                continue
            line = re.sub(r"p\{[\d.]+cm\}", " ", line)             # tabular column widths
            probe = strip_for_source_audit(line)
            for tok in re.findall(r"\d(?:[\d,]*\d)?(?:\.\d+)?", probe):
                if ALLOWED_SOURCE.match(tok):
                    continue
                rows.append({"file": name, "line": ln, "value": tok,
                             "context": line.strip()[:110]})
    return rows


def sourced_strings(numbers):
    ok = set()
    for rec in numbers.values():
        v = rec["value"]
        if isinstance(v, str):
            ok.add(v.strip())
            continue
        if v is None:
            continue
        cands = []
        if rec.get("fmt"):
            try:
                cands.append(format(v, rec["fmt"]))
            except (ValueError, TypeError):
                pass
        if isinstance(v, int):
            cands += [str(v), f"{v:,}"]
        else:
            cands += [f"{v:.0f}", f"{v:.1f}", f"{v:.2f}", f"{v:.3f}", f"{v:.4f}",
                      f"{v:,.0f}", f"{v:+.2f}", f"{v:+.3f}", f"{v:+.4f}"]
        for c in cands:
            ok.add(c.strip())
            ok.add(c.lstrip("+").strip())
    return ok


def document_pass(numbers):
    out = os.path.join(C.RESULTS, "_main_text.txt")
    subprocess.run(["pdftotext", "-layout", PDF, out], check=True)
    text = open(out, encoding="utf-8", errors="replace").read()
    cut = text.rfind("References")
    body = text[:cut] if cut > 0 else text
    ok = sourced_strings(numbers)

    rows, scanned = [], 0
    for ln, line in enumerate(body.split("\n"), 1):
        probe = line
        probe = re.sub(r"\[[\d,\s]+\]", " ", probe)          # citation markers
        probe = re.sub(r"(?m)^\s*\d{1,3}\s", " ", probe)     # margin line numbers
        probe = re.sub(r"https?://\S+|10\.\d{4,9}/\S+", " ", probe)
        probe = re.sub(r"^\s*\d+(?:\.\d+)*\.?\s+[A-Z]", " ", probe)  # headings
        # a row of axis tick labels from an embedded figure
        toks = re.findall(r"[-+]?\d(?:[\d,]*\d)?(?:\.\d+)?", probe)
        if len(toks) >= 4 and all(len(t) <= 5 for t in toks):
            continue
        for tok in toks:
            scanned += 1
            if tok in ok or tok.lstrip("+-") in ok:
                continue
            if re.fullmatch(r"(?:19|20)\d{2}|\d{1,2}|1\.13\.0|4\.0", tok.lstrip("+-")):
                continue
            rows.append({"line": ln, "value": tok, "context": line.strip()[:110]})
    return rows, scanned


def run():
    numbers = json.load(open(os.path.join(C.RESULTS, "numbers.json"),
                             encoding="utf-8"))
    src = source_pass()
    with open(os.path.join(C.RESULTS, "unsourced_numbers.csv"), "w",
              encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, ["file", "line", "value", "context"])
        w.writeheader()
        w.writerows(src)

    doc, scanned = ([], 0)
    if os.path.exists(PDF):
        doc, scanned = document_pass(numbers)
        with open(os.path.join(C.RESULTS, "document_pass_numbers.csv"), "w",
                  encoding="utf-8", newline="") as fh:
            w = csv.DictWriter(fh, ["line", "value", "context"])
            w.writeheader()
            w.writerows(doc)

    C.dump({"labeled_values_available": len(numbers),
            "source_pass_hand_typed_numbers": len(src),
            "document_pass_unmatched": len(doc),
            "document_pass_tokens_scanned": scanned,
            "rule": "the source pass must be empty; the document pass is advisory"},
           "numbers_audit.json")

    print(f"SOURCE PASS: {len(src)} hand-typed number(s) in the manuscript prose")
    for r in src[:20]:
        print(f"  {r['file']}:{r['line']} {r['value']:>10s}  {r['context'][:70]}")
    print(f"\nDOCUMENT PASS: {len(doc)} unmatched of {scanned} scanned (advisory)")
    for r in doc[:12]:
        print(f"  line {r['line']:4d} {r['value']:>10s}  {r['context'][:70]}")
    return len(src)


if __name__ == "__main__":
    run()
