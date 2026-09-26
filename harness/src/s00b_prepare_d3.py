"""Rebuild shared/data/d3/*.jsonl and manifest.json from public sources.

Self-contained: fetches the two source repositories at pinned commits over
HTTP (raw.githubusercontent.com, no auth needed, both repos are public) and
writes the four D3 task files plus manifest.json. No local state is read;
everything needed is either a literal in this file or fetched over the
network. Intended to run unmodified on a fresh machine (e.g. Google Colab
on Linux) as well as on the original Windows workstation.

Sources
-------
- Question/option wording and label mapping: hazemibrahim97/decision-models-css
  commit 311956c2d1096cabc0f09a1f248e7dc0e1c0c41e, file pilot_jev.py
  (https://github.com/hazemibrahim97/decision-models-css). The relevant
  functions (`parse_prompt`, `task_criteria`, `OPTION_TO_GOLD`,
  `BINARY_CRITERIA`) are reproduced here by hand rather than imported,
  because importing pilot_jev.py reads an OpenRouter API key from disk at
  module load time, which this script must not do.
- Task text and gold labels: SALT-NLP/LLMs_for_CSS commit
  55183a64d7faaf6d5fc23eddf2bfc48ece4cacad, files
  css_data/<task>/test.json (https://github.com/SALT-NLP/LLMs_for_CSS).

Usage
-----
    python s00b_prepare_d3.py [--out DIR]

Writes <DIR>/<task>.jsonl for task in {conv_go_awry, wiki_corpus, emotion,
wiki_politeness} and <DIR>/manifest.json, with sha256 + n per file. Default
DIR is ../data/d3 relative to this file (i.e. shared/data/d3).

Dependencies: requests only (pandas/datasets/huggingface_hub are permitted
per the project's environment but are not needed for this script, since the
source data is plain JSON over HTTP, not a Hugging Face dataset).
"""

import argparse
import hashlib
import json
import random
import re
import pathlib

import requests

SEED = 20260924

SALT_REPO = "SALT-NLP/LLMs_for_CSS"
SALT_COMMIT = "55183a64d7faaf6d5fc23eddf2bfc48ece4cacad"
IBRAHIM_ZAKI_REPO = "hazemibrahim97/decision-models-css"
IBRAHIM_ZAKI_COMMIT = "311956c2d1096cabc0f09a1f248e7dc0e1c0c41e"  # provenance only; not fetched, logic is reproduced below

RAW_BASE = "https://raw.githubusercontent.com/{repo}/{commit}/{path}"

ALL_TASKS = ["conv_go_awry", "wiki_corpus", "emotion", "wiki_politeness"]
BINARY_TASKS = {"conv_go_awry", "wiki_corpus"}

# ---------------------------------------------------------------------
# Reproduced by hand from pilot_jev.py at IBRAHIM_ZAKI_COMMIT (see module
# docstring). Word for word except for the subset of OPTION_TO_GOLD /
# BINARY_CRITERIA entries this script needs.
# ---------------------------------------------------------------------

def parse_prompt(prompt):
    lines = prompt.strip().split("\n")
    instr, opts, cur = [], {}, None
    for line in lines:
        m = re.match(r"^([A-Z]+): (.*)$", line)
        if m:
            cur = m.group(1)
            opts[cur] = m.group(2)
        elif line.startswith("Constraint:"):
            cur = None
        elif cur:
            opts[cur] += " " + line.strip()
        else:
            instr.append(line)
    return " ".join(instr).strip(), opts


OPTION_TO_GOLD = {
    "emotion": {"A": "A", "B": "B", "C": "C", "D": "D", "E": "E", "F": "F"},
    "wiki_politeness": {"A": 1, "B": 0, "C": -1},
}

BINARY_CRITERIA = {
    "conv_go_awry": {
        "True": "True: the previous conversation eventually derails into a personal attack.",
        "False": "False: the previous conversation does not eventually derail into a personal attack.",
    },
    "wiki_corpus": {
        "True": "True: the named user is in a position of power in the conversation.",
        "False": "False: the named user is not in a position of power in the conversation.",
    },
}

# The marked/positive class per binary task: the outcome the task's own
# instruction text asserts. Both binary tasks here use the package's own
# "True" label for that marked outcome; "False" is the negation. See
# shared/data/d3/README.md for the full rationale.
POSITIVE_CLASS = {
    "conv_go_awry": "True",
    "wiki_corpus": "True",
}


def task_criteria(task, opts):
    if task in BINARY_CRITERIA:
        return BINARY_CRITERIA[task]
    criteria = {}
    for letter, gold in OPTION_TO_GOLD[task].items():
        text = opts.get(letter)
        criteria[str(gold)] = text.strip() if text else text
    return criteria


def coerce_gold(task, raw):
    if task in BINARY_TASKS:
        return str(raw)  # Python bool True/False -> "True"/"False"
    if task == "wiki_politeness":
        return str(raw)
    return raw  # emotion: already a letter string


# ---------------------------------------------------------------------
# Fetch
# ---------------------------------------------------------------------

def fetch_test_json(task):
    path = f"css_data/{task}/test.json"
    url = RAW_BASE.format(repo=SALT_REPO, commit=SALT_COMMIT, path=path)
    resp = requests.get(url, timeout=60)
    resp.raise_for_status()
    return json.loads(resp.text)


# ---------------------------------------------------------------------
# Build (identical logic to shared/src's scratch build used to produce the
# checked-in files; see shared/data/d3/README.md for the sampling note)
# ---------------------------------------------------------------------

def build_task(task):
    j = fetch_test_json(task)
    ids = sorted(j["labels"].keys())

    if task in BINARY_TASKS:
        options = ["True", "False"]
        criteria = task_criteria(task, {})
        per_item_instr = {}
        for pid in ids:
            instr, _opts = parse_prompt(j["prompts"][pid])
            per_item_instr[pid] = instr
    else:
        prompts = set(j["prompts"].values())
        assert len(prompts) == 1, (task, "prompt not fixed across items", len(prompts))
        prompt = next(iter(prompts))
        instr, opts = parse_prompt(prompt)
        criteria = task_criteria(task, opts)
        options = [str(g) for g in OPTION_TO_GOLD[task].values()]
        per_item_instr = {pid: instr for pid in ids}

    assert set(criteria.keys()) == set(options), (task, criteria.keys(), options)

    # Seed 20260924. Every task here has n <= 500 (Ziems et al.'s released
    # test.json is already a class-stratified sample of at most 500 items),
    # so this seeded draw selects every item; the seed fixes only a
    # deterministic per-label shuffle-then-concatenate write order.
    rnd = random.Random(SEED)
    by_label = {}
    for pid in ids:
        lbl = coerce_gold(task, j["labels"][pid])
        by_label.setdefault(lbl, []).append(pid)
    ordered = []
    for lbl in sorted(by_label.keys(), key=str):
        bucket = by_label[lbl][:]
        rnd.shuffle(bucket)
        ordered.extend(bucket[:500])
    rnd.shuffle(ordered)
    ordered = ordered[:500]

    rows = []
    for pid in ordered:
        text = j["context"][pid]
        gold = coerce_gold(task, j["labels"][pid])
        assert gold in criteria, (task, pid, gold, list(criteria.keys()))
        rows.append({
            "id": pid,
            "task": task,
            "text": text,
            "gold": gold,
            "options": options,
            "option_desc": criteria,
            "question": per_item_instr[pid],
            "binary": task in BINARY_TASKS,
            "positive": POSITIVE_CLASS.get(task) if task in BINARY_TASKS else None,
        })
    return rows


def write_jsonl(path, rows):
    with path.open("w", encoding="utf-8", newline="\n") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def sha256_of(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=None, help="output directory (default: shared/data/d3 relative to this file)")
    args = ap.parse_args()

    out_dir = pathlib.Path(args.out) if args.out else (pathlib.Path(__file__).resolve().parent.parent / "data" / "d3")
    out_dir.mkdir(parents=True, exist_ok=True)

    manifest = {}
    for task in ALL_TASKS:
        rows = build_task(task)
        path = out_dir / f"{task}.jsonl"
        write_jsonl(path, rows)
        digest = sha256_of(path)
        manifest[f"{task}.jsonl"] = {"sha256": digest, "n": len(rows)}
        print(task, "n=", len(rows), "sha256=", digest)

    manifest_path = out_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print("wrote", manifest_path)


if __name__ == "__main__":
    main()
