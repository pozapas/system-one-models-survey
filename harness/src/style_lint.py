"""Mechanical enforcement of the manuscript writing rules in section 7 of the outline.

The linter reads the body files of the manuscript, strips LaTeX constructs where a
rule does not apply, and reports every violation with a line number. It exits
non-zero when anything is flagged, so the build can depend on it.

Adapted for Paper 4 (ACL template). Figures are referenced as Figure~\\ref{...} and
the word figure may appear in no other sense. Banned words and run-in paragraph
labels are also flagged.
"""
import os
import re
import sys

BRITISH = {
    "behaviour": "behavior", "behavioural": "behavioral", "colour": "color",
    "colours": "colors", "coloured": "colored", "modelling": "modeling",
    "modelled": "modeled", "centre": "center", "centres": "centers",
    "analyse": "analyze", "analysed": "analyzed", "analysing": "analyzing",
    "normalise": "normalize", "normalised": "normalized",
    "recognise": "recognize", "recognised": "recognized",
    "generalise": "generalize", "generalised": "generalized",
    "labelled": "labeled", "labelling": "labeling", "travelled": "traveled",
    "favour": "favor", "favourable": "favorable", "neighbour": "neighbor",
    "neighbours": "neighbors", "neighbouring": "neighboring",
    "metre": "meter", "metres": "meters", "litre": "liter",
    "defence": "defense", "licence": "license", "practise": "practice",
    "organisation": "organization", "organisations": "organizations",
    "emphasise": "emphasize", "emphasised": "emphasized",
    "summarise": "summarize", "summarised": "summarized",
    "utilise": "utilize", "utilised": "utilized", "programme": "program",
    "judgement": "judgment", "acknowledgement": "acknowledgment",
}

BANNED = ["honest", "honestly", "honesty", "frankly", "candidly", "truthfully"]

MAX_WORDS = 45
MIN_OPENING_WORDS = 8
LINES_PER_PAGE = 46


def strip_latex(line):
    """Remove constructs to which the prose rules do not apply."""
    s = line
    s = re.sub(r"%.*$", "", s)                       # comments
    s = re.sub(r"\$[^$]*\$", " MATH ", s)            # inline math
    s = re.sub(r"\\\(.*?\\\)", " MATH ", s)        # inline math \( \)
    s = re.sub(r"\\\[.*?\\\]", " MATH ", s)        # display math \[ \]
    s = re.sub(r"\\(?:url|href)\{[^}]*\}", " URL ", s)
    s = re.sub(r"\\(?:label|ref|eqref|sref|fref|frefi|tref|eref|aref|refi|cite|citep|citet)"
               r"\*?(?:\{[^}]*\})+", " REF ", s)
    s = re.sub(r"\\(?:input|include|includegraphics)(?:\[[^]]*\])?\{[^}]*\}", " ", s)
    s = re.sub(r"\\texttt\{[^}]*\}", " CODE ", s)
    s = re.sub(r"\\[a-zA-Z@]+\*?", " ", s)           # remaining commands
    s = re.sub(r"[{}]", " ", s)
    return s


def sentences(text):
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return []
    # A caption panel marker such as "(a)" begins a new sentence even though it
    # does not begin with a capital letter.
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z\\]|\([a-z]\)\s)", text)
    return [p.strip() for p in parts if p.strip()]


def lint_file(path):
    issues = []
    raw = open(path, encoding="utf-8").read().split("\n")

    in_verbatim = False
    in_table = False
    paragraph, para_start = [], None
    para_in_float = False
    however_lines = []

    def flush_paragraph():
        nonlocal para_in_float
        if not paragraph:
            return
        text = strip_latex(" ".join(paragraph))
        ss = sentences(text)
        # The opening-sentence rule is about body paragraphs. A caption is one
        # block of prose, so a wrapped line inside a float is not an opening.
        if ss and not para_in_float:
            first = ss[0]
            n = len(first.split())
            if n < MIN_OPENING_WORDS and not first.startswith("REF"):
                issues.append((para_start, "paragraph opens with a sentence of "
                                           f"{n} words, minimum is {MIN_OPENING_WORDS}",
                               first[:70]))
        for s in ss:
            if para_in_float:
                continue   # a table's cells are data, not sentence-structured prose;
                           # the colon rule already exempts them on the same grounds
            if len(s.split()) > MAX_WORDS:
                issues.append((para_start, f"sentence of {len(s.split())} words, "
                                           f"maximum is {MAX_WORDS}", s[:70]))
            if s.rstrip().endswith("?"):
                issues.append((para_start, "sentence ends with a question mark",
                               s[:70]))

    for i, line in enumerate(raw, start=1):
        if re.search(r"\\begin\{(verbatim|lstlisting|minted)\}", line):
            in_verbatim = True
        if re.search(r"\\end\{(verbatim|lstlisting|minted)\}", line):
            in_verbatim = False
            continue
        if in_verbatim:
            continue
        if re.search(r"\\begin\{(table|tabular|figure)\*?\}", line):
            in_table = True
        if re.search(r"\\end\{(table|tabular|figure)\*?\}", line):
            in_table = False
            continue

        if "—" in line or "–" in line or "---" in line:
            issues.append((i, "em dash or en dash", line.strip()[:70]))

        if re.search(r"\\begin\{(itemize|enumerate|description)\}", line) and not in_table:
            issues.append((i, "list environment in the body", line.strip()[:70]))

        clean = strip_latex(line)

        # The environment names "figure" and "table" are LaTeX, not prose, and
        # the rule is about the word appearing in a sentence.
        if re.search(r"\\(?:begin|end)\{(?:figure|table|longtable)\*?\}", line):
            clean = re.sub(r"[Ff]igure", " ", clean)

        # Paper 4 uses plain LaTeX, so a figure is referenced as Figure~\ref{...}
        # (Figures~\ref{a} and~\ref{b}); any other use of the word is flagged.
        for m in re.finditer(r"[Ff]igures?|[Ff]ig\.", clean):
            ok = re.match(r"Figures?[~\s]+REF", clean[m.start():])
            if not ok:
                issues.append((i, "the word figure appears other than as Figure~ref",
                               line.strip()[:70]))
                break

        for w in BANNED:
            if re.search(rf"\b{w}\b", clean, flags=re.I):
                issues.append((i, f"banned word {w!r}", line.strip()[:70]))

        if re.search(r"\\(?:sub)*paragraph\*?\{", line):
            issues.append((i, "run-in label (paragraph)", line.strip()[:70]))

        if not in_table:
            probe = re.sub(r"\d:\d", "", clean)           # times
            probe = re.sub(r"\d\s*:\s*\d", "", probe)     # ratios
            if ":" in probe:
                issues.append((i, "colon in a sentence", line.strip()[:70]))

        low = clean.lower()
        for b, a in BRITISH.items():
            if re.search(rf"\b{b}\b", low):
                issues.append((i, f"British spelling '{b}', use '{a}'",
                               line.strip()[:70]))

        if re.match(r"\s*(However|Moreover)\b", line):
            however_lines.append(i)

        if line.strip() == "":
            flush_paragraph()
            paragraph, para_start = [], None
        elif not line.lstrip().startswith("\\") or re.match(
                r"\s*\\(?:emph|textit|textbf|texttt|cite|ref|num|sref|fref|tref)", line):
            if para_start is None:
                para_start = i
                para_in_float = in_table
            paragraph.append(line)
        else:
            flush_paragraph()
            paragraph, para_start = [], None

    flush_paragraph()

    pages = {}
    for i in however_lines:
        pages.setdefault(i // LINES_PER_PAGE, []).append(i)
    for p, ls in pages.items():
        if len(ls) > 1:
            issues.append((ls[1], f"'however' or 'moreover' opens {len(ls)} sentences "
                                  f"within about one page (lines {ls})", ""))

    return sorted(issues)


def run(paths):
    total = 0
    report = []
    for p in paths:
        if not os.path.exists(p):
            continue
        issues = lint_file(p)
        total += len(issues)
        report.append(f"=== {os.path.basename(p)}: {len(issues)} issue(s)")
        for line, what, ctx in issues:
            report.append(f"  line {line:4d}  {what}")
            if ctx:
                report.append(f"             | {ctx}")
    text = "\n".join(report) if report else "no files found"
    print(text)
    print(f"\nTOTAL {total} issue(s)")
    out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       "manuscript", "style_lint_report.txt")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(text + f"\n\nTOTAL {total} issue(s)\n")
    return total


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    man = os.path.join(os.path.dirname(here), "manuscript")
    args = sys.argv[1:] or [os.path.join(man, "body.tex")]
    sys.exit(1 if run(args) else 0)
