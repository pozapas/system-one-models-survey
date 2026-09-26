"""Assemble the arXiv package of Paper 4A.

Copies the compiled sources (main.tex, sections, tables, figures as PDF, numbers.tex,
acl.sty, acl_natbib.bst and the generated main.bbl) into benchmark/release/arxiv/,
test-compiles the copy with pdflatex without BibTeX (as arXiv does when a .bbl is
present), writes the plain-text metadata file, and zips the package with a SHA-256
manifest.
"""
import hashlib
import os
import re
import shutil
import subprocess
import zipfile

P4 = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MAN = os.path.join(P4, "benchmark", "manuscript")
OUT = os.path.join(P4, "benchmark", "release", "arxiv")
SRC = os.path.join(OUT, "src")


def main():
    # OneDrive can hold a lock on the folders, so stale files are removed one by one
    # and the folders are reused rather than deleted
    if os.path.isdir(OUT):
        for root, _, files in os.walk(OUT):
            for f in files:
                os.remove(os.path.join(root, f))
    os.makedirs(SRC, exist_ok=True)
    for f in ("main.tex", "numbers.tex", "acl.sty", "acl_natbib.bst", "main.bbl"):
        shutil.copy2(os.path.join(MAN, f), os.path.join(SRC, f))
    for d in ("sections", "tables"):
        shutil.copytree(os.path.join(MAN, d), os.path.join(SRC, d), dirs_exist_ok=True)
    used = set(re.findall(r"figures/(f\d+_[a-z]+)",
                          " ".join(open(os.path.join(MAN, "sections", f), encoding="utf-8").read()
                                   for f in os.listdir(os.path.join(MAN, "sections")))))
    os.makedirs(os.path.join(SRC, "figures"), exist_ok=True)
    for f in sorted(used):
        shutil.copy2(os.path.join(MAN, "figures", f + ".pdf"), os.path.join(SRC, "figures", f + ".pdf"))

    # arXiv compiles with the .bbl; test that path in the copy
    for _ in range(2):
        subprocess.run(["pdflatex", "-interaction=nonstopmode", "main.tex"], cwd=SRC,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    log = open(os.path.join(SRC, "main.log"), encoding="latin-1").read()
    bad = [l for l in log.splitlines() if l.startswith("!") or "undefined" in l.lower()]
    shutil.copy2(os.path.join(SRC, "main.pdf"), os.path.join(OUT, "Rafe_Das_2026_six_decision_models.pdf"))
    for f in os.listdir(SRC):
        if f.split(".")[-1] in ("aux", "log", "out", "pdf", "fls", "fdb_latexmk"):
            os.remove(os.path.join(SRC, f))

    # metadata: the abstract as plain text for the arXiv form
    ab = open(os.path.join(MAN, "sections", "abstract.tex"), encoding="utf-8").read()
    nums = {}
    for m in re.finditer(r"\\csname cdnum@([^\\]+)\\endcsname\{(.*)\}$",
                         open(os.path.join(MAN, "numbers.tex"), encoding="utf-8").read(), re.M):
        nums[m.group(1)] = m.group(2).replace(r"\ensuremath{-}", "-")
    ab = re.sub(r"\\num\{([^}]+)\}", lambda m: nums[m.group(1)], ab)
    ab = re.sub(r"\\(begin|end)\{abstract\}", "", ab)
    ab = " ".join(ab.split())
    meta = (
        "Title: Six Decision Models, One Harness: Benchmarking System One Models on Accuracy, "
        "Calibration, Cardinality and Option Naming\n"
        "Authors: Amir Rafe, Subasish Das\n"
        "Primary category: cs.CL\nCross-list: cs.LG\n"
        "Comments: 8 pages of content plus references and appendices; code, frozen inputs and "
        "every model answer at https://github.com/pozapas/system-one-models-survey "
        "(to be made public on release)\n"
        "License: to be chosen by the authors at submission\n\n"
        f"Abstract ({len(ab)} characters, arXiv limit 1920):\n{ab}\n")
    open(os.path.join(OUT, "arxiv_metadata.txt"), "w", encoding="utf-8").write(meta)

    zpath = os.path.join(OUT, "arxiv_source_4A.zip")
    man = []
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for root, _, files in os.walk(SRC):
            for f in sorted(files):
                full = os.path.join(root, f)
                rel = os.path.relpath(full, SRC).replace(os.sep, "/")
                z.write(full, rel)
                man.append((hashlib.sha256(open(full, "rb").read()).hexdigest(), rel))
    with open(os.path.join(OUT, "SHA256SUMS.txt"), "w", encoding="utf-8", newline="\n") as fh:
        for h, rel in man:
            fh.write(f"{h}  {rel}\n")
    print(f"package: {zpath}, {len(man)} files; test compile problems: {len(bad)}")
    for l in bad[:10]:
        print("  ", l)
    print(f"abstract {len(ab)} chars")


if __name__ == "__main__":
    main()
