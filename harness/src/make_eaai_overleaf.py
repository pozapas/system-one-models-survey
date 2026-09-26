"""Build a clean Overleaf package of the EAAI manuscript.

Copies only the files the manuscript needs from benchmark/eaai/manuscript into
benchmark/eaai/overleaf/, inserts the progress note for Dr. Das as the first page of
main.tex (between clearly marked REMOVE BEFORE SUBMISSION comments), and writes
benchmark/eaai/overleaf.zip for upload (Overleaf, New Project, Upload Project).
"""
import os
import shutil
import zipfile

import common as C

BASE = os.path.join(os.path.dirname(C.ROOT), "benchmark", "eaai")
MANU = os.path.join(BASE, "manuscript")
OUT = os.path.join(BASE, "overleaf")
ZIP = os.path.join(BASE, "overleaf.zip")

FILES = ["cas-sc.cls", "cas-common.sty", "cas-model2-names.bst", "paper4a_tables.sty",
         "numbers.tex", "refs.bib", "title_page.tex"]
DIRS = ["sections", "tables", "figures", "thumbnails"]

NOTE = r"""%% ======================= REMOVE BEFORE SUBMISSION =======================
%% Progress note for Dr. Das. Delete everything from this line down to the
%% matching END line (or set \shownotefalse) before submitting.
\newif\ifshownote
\shownotetrue
\ifshownote
\begingroup
\thispagestyle{empty}
\setlength{\parindent}{0pt}
\definecolor{notegreen}{HTML}{2E7D32}
\vspace*{3cm}
\textcolor{notegreen}{\rule{\linewidth}{1.2pt}}\par
\vspace{1.2cm}
{\LARGE Dear Dr.\ Das,\par}
\vspace{0.9cm}
{\Large
This is not the final version of the manuscript. I am sharing it with you so that you can see the progress so far.\par
\vspace{0.9cm}
The remaining work is to\par
\vspace{0.3cm}
\begin{itemize}\setlength{\itemsep}{0.35cm}
  \item finalize some of the tables,
  \item refine the framing of some sections, and
  \item reread the whole manuscript in the role of a reviewer.
\end{itemize}
\vspace{0.9cm}
Best regards,\\[0.2cm]
Amir\par}
\vspace{1.2cm}
\textcolor{notegreen}{\rule{\linewidth}{1.2pt}}\par
\clearpage
\endgroup
\setcounter{page}{1}
\fi
%% ===================== END REMOVE BEFORE SUBMISSION =====================
"""

README = """EAAI manuscript, Overleaf package

Upload overleaf.zip with New Project > Upload Project. Compiler: pdfLaTeX (the
default), main document main.tex. Overleaf runs BibTeX with refs.bib and
cas-model2-names.bst automatically.

- main.tex        anonymized manuscript. Its first page is a progress note for
                  Dr. Das between the REMOVE BEFORE SUBMISSION markers; delete
                  that block (or change \\shownotetrue to \\shownotefalse) before
                  submitting.
- title_page.tex  separate title page with authors, declarations and CRediT
                  (compile it by setting it as the main document in the menu).
- numbers.tex     every number in the text, generated from the analysis; edit
                  the prose, not this file.
- sections/       one file per section; tables/ and figures/ hold the floats.
- cas-sc.cls, cas-common.sty   Elsevier CAS single-column class, unmodified.
- paper4a_tables.sty           table style (green header band, group rows).
- The Code and data availability statement cites the GitHub repository by its
  real address; replace it with the anonymous link before submission.
"""


def run():
    # Remove only what this script writes (never other files the owner keeps here,
    # such as review outputs); OneDrive can lock folders, so files only.
    if os.path.isdir(OUT):
        managed = [os.path.join(OUT, f) for f in FILES + ["main.tex", "README.txt"]]
        for d in DIRS:
            dd = os.path.join(OUT, d)
            if os.path.isdir(dd):
                managed += [os.path.join(dd, f) for f in os.listdir(dd)
                            if os.path.isfile(os.path.join(dd, f))]
        for p in managed:
            if os.path.isfile(p):
                os.remove(p)
    os.makedirs(OUT, exist_ok=True)
    for f in FILES:
        shutil.copy(os.path.join(MANU, f), os.path.join(OUT, f))
    for d in DIRS:
        for f in os.listdir(os.path.join(MANU, d)):
            os.makedirs(os.path.join(OUT, d), exist_ok=True)
            shutil.copy(os.path.join(MANU, d, f), os.path.join(OUT, d, f))

    main = open(os.path.join(MANU, "main.tex"), encoding="utf-8").read()
    anchor = "\\begin{document}\n"
    assert main.count(anchor) == 1
    main = main.replace(anchor, anchor + NOTE, 1)
    with open(os.path.join(OUT, "main.tex"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(main)
    with open(os.path.join(OUT, "README.txt"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(README)

    if os.path.exists(ZIP):
        os.remove(ZIP)
    n = 0
    with zipfile.ZipFile(ZIP, "w", zipfile.ZIP_DEFLATED) as z:
        for root, _, files in os.walk(OUT):
            rel_root = os.path.relpath(root, OUT).replace("\\", "/")
            if rel_root != "." and rel_root.split("/")[0] not in DIRS:
                continue                      # only the package, never other folders here
            for f in files:
                if rel_root == "." and f not in FILES + ["main.tex", "README.txt"]:
                    continue
                p = os.path.join(root, f)
                z.write(p, os.path.relpath(p, OUT).replace("\\", "/"))
                n += 1
    print(f"wrote {OUT} and {ZIP} ({n} files)")


if __name__ == "__main__":
    run()
