"""Build the EAAI submission package from benchmark/eaai/manuscript.

Writes benchmark/eaai/submission/ with the anonymized manuscript PDF, the title page
PDF, the highlights and a plain-text abstract (every num-macro resolved from
numbers.tex), each figure as a separate file, a LaTeX source zip that compiles on its
own, and SHA256SUMS.txt. Run after compiling main.tex and title_page.tex.
"""
import hashlib
import os
import re
import shutil
import zipfile

import common as C

BASE = os.path.join(os.path.dirname(C.ROOT), "benchmark", "eaai")
MANU = os.path.join(BASE, "manuscript")
OUT = os.path.join(BASE, "submission")

HIGHLIGHTS = [
    "Eight decision-model checkpoints, a generator and baselines under one harness",
    "Classifiers trained on the task's data beat all decision models on intents",
    "A stored temperature fitted on few options inflates error with 150 options",
    "Swapping yes/no flips half of hosted workflow answers, under 10% for 4 of 5 decoders",
    "An intent-trained first stage matches hosted accuracy at under half its cost",
]


def macros():
    tex = open(os.path.join(MANU, "numbers.tex"), encoding="utf-8").read()
    d = dict(re.findall(r"\\csname cdnum@(.+?)\\endcsname\{(.*)\}$", tex, flags=re.M))
    return {k: v.replace(r"\ensuremath{-}", "-") for k, v in d.items()}


def plain_abstract(M):
    s = open(os.path.join(MANU, "sections", "abstract.tex"), encoding="utf-8").read()
    s = re.sub(r"\\(begin|end)\{abstract\}", "", s)
    s = re.sub(r"\\num\{([^}]*)\}", lambda m: M[m.group(1)], s)
    assert "\\" not in s, "unresolved LaTeX in abstract"
    return " ".join(s.split())


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def run():
    for f in os.listdir(OUT) if os.path.isdir(OUT) else []:
        p = os.path.join(OUT, f)
        if os.path.isfile(p):
            os.remove(p)                  # OneDrive can lock folders, so files only
    os.makedirs(OUT, exist_ok=True)
    M = macros()

    for h in HIGHLIGHTS:
        assert len(h) <= 85, (len(h), h)
    with open(os.path.join(OUT, "highlights.txt"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(HIGHLIGHTS) + "\n")

    ab = plain_abstract(M)
    words = len(ab.split())
    assert words <= 250, words
    with open(os.path.join(OUT, "abstract.txt"), "w", encoding="utf-8") as fh:
        fh.write(ab + "\n")

    shutil.copy(os.path.join(MANU, "main.pdf"), os.path.join(OUT, "manuscript_anonymized.pdf"))
    shutil.copy(os.path.join(MANU, "title_page.pdf"), os.path.join(OUT, "title_page.pdf"))
    shutil.copy(os.path.join(MANU, "title_page.tex"), os.path.join(OUT, "title_page.tex"))

    used = sorted(set(re.findall(r"figures/(f\d\d_\w+)",
                  " ".join(open(os.path.join(MANU, "sections", f), encoding="utf-8").read()
                           for f in os.listdir(os.path.join(MANU, "sections"))))))
    for i, name in enumerate(used, 1):
        shutil.copy(os.path.join(MANU, "figures", name + ".pdf"),
                    os.path.join(OUT, f"figure_{name}.pdf"))

    src = os.path.join(OUT, "latex_source_anonymized.zip")
    keep_ext = (".tex", ".bib", ".bbl", ".cls", ".sty", ".bst", ".pdf")
    with zipfile.ZipFile(src, "w", zipfile.ZIP_DEFLATED) as z:
        for root, _, files in os.walk(MANU):
            rel_root = os.path.relpath(root, MANU)
            if rel_root.startswith("thumbnails"):
                continue
            for f in files:
                rel = os.path.normpath(os.path.join(rel_root, f)).replace("\\", "/")
                if rel in ("main.pdf", "title_page.pdf", "title_page.tex", "title_page.bbl"):
                    continue          # the title page names the authors; it travels separately
                if rel_root == "." and f.endswith(".pdf"):
                    continue
                if f.endswith(keep_ext):
                    z.write(os.path.join(root, f), rel)
        names = z.namelist()
    # The code and data statement cites the repository by its real address until the
    # owner swaps in an anonymized mirror, so the repository name is not checked here.
    for bad in ("Rafe", "Subasish", "txstate"):
        with zipfile.ZipFile(src) as z:
            for n in z.namelist():
                if n.endswith((".tex", ".bbl")):
                    t = z.read(n).decode("utf-8", "ignore")
                    assert bad not in t, (bad, n)

    with open(os.path.join(OUT, "SHA256SUMS.txt"), "w", encoding="utf-8") as fh:
        for f in sorted(os.listdir(OUT)):
            if f != "SHA256SUMS.txt":
                fh.write(f"{sha(os.path.join(OUT, f))}  {f}\n")
    print(f"abstract {words} words; highlights {[len(h) for h in HIGHLIGHTS]}")
    print(f"source zip {len(names)} files; figures {used}")
    print("wrote", OUT)


if __name__ == "__main__":
    run()
