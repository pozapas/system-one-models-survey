"""Assemble the public release package.

Everything needed to reproduce the reported numbers is copied here, except the
crash narratives, which cannot be redistributed. The README states what is
present, what is absent and why, and how to obtain the absent part.
"""
import hashlib
import json
import os
import shutil

import common as C

REL = os.path.join(C.ROOT, "release")

COPY_TREES = [
    (os.path.join(C.ROOT, "src"), "code"),
    (os.path.join(C.ROOT, "results"), "results"),
    (os.path.join(C.ROOT, "figures"), "figures"),
    (os.path.join(C.ROOT, "tables"), "tables"),
    (os.path.join(C.ROOT, "references"), "references"),
]

COPY_FILES = [
    (C._p("ped", "pilot", "choice_test.py"), "code/pilot_choice_test.py"),
    (C._p("ped", "pilot", "pushing_test.py"), "code/pilot_pushing_test.py"),
    (C._p("crowd_nudging", "nudge_test.py"), "code/pilot_nudge_test.py"),
]

# Cached model answers, which are the raw evidence for every reported number.
ANSWER_FILES = (
    [(C._p("ped", "pilot", f"jev_answers_{t}.jsonl"), f"answers/jev_answers_{t}.jsonl")
     for t in C.LOCO_TAGS]
    + [(C._p("ped", "pilot", f"push_jev_{v}.jsonl"), f"answers/push_jev_{v}.jsonl")
       for v in ("nohist", "hist")]
)

EXCLUDE_NAMES = {"__pycache__", "_main_text.txt"}


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def copy_tree(src, dst):
    n = 0
    for root, dirs, files in os.walk(src):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_NAMES]
        for f in files:
            if f in EXCLUDE_NAMES or f.endswith(".pyc"):
                continue
            s = os.path.join(root, f)
            rel = os.path.relpath(s, src)
            d = os.path.join(dst, rel)
            os.makedirs(os.path.dirname(d), exist_ok=True)
            shutil.copy2(s, d)
            n += 1
    return n


def run():
    # The directory itself is kept, because a synchronizing file service can
    # hold a handle on it and refuse the removal. Only the contents are cleared.
    os.makedirs(REL, exist_ok=True)
    for name in os.listdir(REL):
        p = os.path.join(REL, name)
        if os.path.isdir(p):
            shutil.rmtree(p, ignore_errors=True)
        else:
            try:
                os.remove(p)
            except OSError:
                pass

    total = 0
    for src, sub in COPY_TREES:
        if os.path.exists(src):
            total += copy_tree(src, os.path.join(REL, sub))
    for src, rel in COPY_FILES + ANSWER_FILES:
        if os.path.exists(src):
            d = os.path.join(REL, rel)
            os.makedirs(os.path.dirname(d), exist_ok=True)
            shutil.copy2(src, d)
            total += 1

    # the pilot decision sets carry the encoded situations themselves
    for src, rel in [(C._p("ped", "pilot", f"decisions_{t}.pkl"),
                      f"encoded/decisions_{t}.pkl") for t in C.LOCO_TAGS] + \
                    [(C._p("ped", "pilot", "push_decisions.pkl"),
                      "encoded/push_decisions.pkl")]:
        if os.path.exists(src):
            d = os.path.join(REL, rel)
            os.makedirs(os.path.dirname(d), exist_ok=True)
            shutil.copy2(src, d)
            total += 1

    manifest = []
    for root, dirs, files in os.walk(REL):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_NAMES]
        for f in sorted(files):
            p = os.path.join(root, f)
            manifest.append({"path": os.path.relpath(p, REL).replace("\\", "/"),
                             "bytes": os.path.getsize(p),
                             "sha256": sha256(p)})
    with open(os.path.join(REL, "MANIFEST.json"), "w", encoding="utf-8") as fh:
        json.dump({"n_files": len(manifest), "files": manifest}, fh, indent=1)

    ds = json.load(open(os.path.join(C.RESULTS, "datasets.json"), encoding="utf-8"))
    nu = json.load(open(os.path.join(C.RESULTS, "nudging_archive_report.json"),
                        encoding="utf-8"))
    cl = json.load(open(os.path.join(C.RESULTS, "cost_latency.json"), encoding="utf-8"))

    lines = [
        "# Release package",
        "",
        "Everything needed to reproduce the numbers in the paper, apart from one",
        "dataset that cannot be redistributed. The model evaluated throughout is",
        f"`{C.MODEL}`, pinned explicitly on every call made for this paper, and the",
        "model identifier returned by the service is recorded in each answer record.",
        "",
        "## What is here",
        "",
        "`code/` holds every analysis, figure and table script, the shared protocol",
        "in `common.py`, the task registry in `tasks.py`, the encoders and question",
        "sets in `b01_ablations.py`, the reference verifier, the style linter and the",
        "numbers audit. `answers/` holds every cached model answer as append-only",
        "JSONL keyed by instance. `encoded/` holds the encoded situations that were",
        "sent, so an answer can be traced back to the exact text that produced it.",
        "`results/` holds every number the paper cites, including",
        "`numbers.json`, which maps each label used in the manuscript to a value and",
        "the file that produced it. `figures/` and `tables/` hold the generated",
        "output. `references/` holds the verified bibliography together with the",
        "rejected candidates and the field corrections found during verification.",
        "",
        "## The nudging archive",
        "",
        f"`results/nudging_archive.json` holds {nu['n_accepted']} experiments. Each",
        "entry carries a description with the result removed, the observed efficacy",
        "band and direction, a source, and a verbatim quotation of the sentence in",
        "the source that states the number. Descriptions are written so that a",
        "forecaster reads only what was knowable before the experiment ran, and a",
        "leak check over the descriptions is part of the build.",
        "`results/nudging_stimulus_codes.json` holds a blind coding of every stimulus,",
        "produced without sight of any outcome, which the a priori heuristics use.",
        "",
        "## Source datasets",
        "",
    ]
    for k, d in ds["datasets"].items():
        if d.get("resolved"):
            lines.append(f"- {d['title']} ({d['year']}), `{d['doi']}`, {d['publisher']}.")
    lines += [
        "",
        "Those records are openly available under the terms stated on their landing",
        "pages and are not duplicated here.",
        "",
        "## What is not here, and how to get it",
        "",
        "The police crash narratives used for the positive contrast are not included.",
        "They are held by the state agency that collects them and are available to",
        "researchers through that agency's data request process, which the companion",
        "methods paper documents. The human-coded labels, the model probabilities and",
        "every aggregate result derived from those narratives are included, so each",
        "reported number can be checked without access to the text itself.",
        "",
        "A human review of sixty coded crowd-incident descriptions was planned to",
        "support an accuracy claim on releasable incident text. Those verdicts were",
        "not available when this package was built, and no accuracy claim is made on",
        "that corpus.",
        "",
        "## Reproducing",
        "",
        "The analyses that use cached answers need no network access and no API key.",
        "Run `a01_core_results.py`, `a02_learning_curves.py`, `a03_information_gain.py`,",
        "`a04_cost_latency.py`, `c01_narrative_contrast.py` where the narratives are",
        "available, `d01_ablation_analysis.py` and `e03_nudge_analysis.py`, then",
        "`collect_numbers.py`. Scripts beginning with `b0` or `e02` issue new API calls",
        "and are only needed to regenerate the cached answers.",
        "",
        f"The full set of calls reported in the paper was {cl['total']['calls']:,}",
        f"requests costing {cl['total']['cost_usd']:.2f} US dollars.",
        "",
        "## Integrity",
        "",
        "`MANIFEST.json` lists every file with its size and SHA-256 digest.",
    ]
    with open(os.path.join(REL, "README.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")

    size = sum(m["bytes"] for m in manifest)
    print(f"release package: {len(manifest)} files, {size / 1e6:.1f} MB")
    print(f"  wrote {REL}")


if __name__ == "__main__":
    run()
