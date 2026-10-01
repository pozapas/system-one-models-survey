"""A second intent benchmark with the exposure reversed (fourth revision): Banking77.

CLINC-150 is in the training data of decider-2b (and so of this-that-model-1.0, adapted from
it), while the Kev cards list Banking77 (Casanueva et al., 2020) among their training sets.
Asking both benchmarks separates what exposure buys from what a model does on an unseen label
set. Banking77 has 77 human-assigned intents of online-banking queries.

Source: huggingface.co/datasets/legacy-datasets/banking77 at revision
f54121560de48f2852f90be299010d1d6dc612ec (CC-BY-4.0), data/{train,test}.parquet.

Construction follows d2_k150 (s00_freeze_inputs.d2_all): PER_INTENT test utterances per intent
drawn with random.Random(f"{SEED}-banking77"), every item asked with all 77 intents as options
in one random permutation per item (same stream), neutral keys o1..o77 in listed order,
descriptions are the intent names with underscores replaced by spaces.

Writes colab/inputs/d2_banking77.jsonl, data/banking77/train.jsonl (text, label) for the
trained classifiers, and one manifest.json entry (existing entries asserted unchanged).

Usage: python s00f_freeze_banking77.py
"""
import hashlib
import json
import os
import random

import pandas as pd
from huggingface_hub import hf_hub_download

import common as C

REPO = "legacy-datasets/banking77"
REV = "f54121560de48f2852f90be299010d1d6dc612ec"
COND = "d2_banking77"
PER_INTENT = 8
QUESTION = "Which intent does this request to a banking assistant express?"


def load(split):
    p = hf_hub_download(REPO, f"data/{split}-00000-of-00001.parquet", repo_type="dataset",
                        revision=REV)
    return pd.read_parquet(p)


def main():
    man_path = os.path.join(C.INPUTS, "manifest.json")
    manifest = json.load(open(man_path, encoding="utf-8"))
    before = json.loads(json.dumps(manifest))
    dst = os.path.join(C.INPUTS, f"{COND}.jsonl")
    assert not os.path.exists(dst), f"{dst} exists; this script writes new files only"

    test, train = load("test"), load("train")
    names = None
    try:
        import datasets  # noqa: F401
    except Exception:
        pass
    # label names from the dataset card's ClassLabel order (dataset_infos is not shipped with the
    # parquet export), read from the README front matter
    readme = hf_hub_download(REPO, "README.md", repo_type="dataset", revision=REV)
    lines = open(readme, encoding="utf-8").read().split("\n")
    names = {}
    for l in lines:
        s = l.strip()
        head = s.split(":")[0].strip().strip("'\"")
        if ": " in s and head.isdigit():
            k, v = s.split(":", 1)
            names[int(k.strip().strip("'\""))] = v.strip().strip("'\"")
    assert len(names) == 77, len(names)
    intents = [names[i] for i in range(77)]

    rng = random.Random(f"{C.SEED}-banking77")
    by = {}
    for i, r in test.iterrows():
        by.setdefault(int(r["label"]), []).append((i, r["text"]))
    rows = []
    keys = [f"o{i + 1}" for i in range(77)]
    for lab in range(77):
        pool = sorted(by[lab])
        for i, text in sorted(rng.sample(pool, PER_INTENT)):
            perm = intents[:]
            rng.shuffle(perm)
            ren = dict(zip(perm, keys))
            gold = intents[lab]
            rows.append({"key": f"{COND}|b77_{i:05d}", "dataset": "d2", "condition": COND,
                         "item_id": f"b77_{i:05d}", "state": text,
                         "questions": {"intent": {"type": "choice", "instructions": QUESTION,
                                                  "criteria": {ren[o]: o.replace("_", " ")
                                                               for o in perm}}},
                         "gold": {"intent": {"type": "choice", "label": ren[gold],
                                             "options": keys, "native_options": perm,
                                             "soft": None}},
                         "meta": {"in_scope": True, "intent": gold, "domain": "banking"}})
    data = "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows).encode("utf-8")
    with open(dst, "wb") as fh:
        fh.write(data)

    tdir = os.path.join(C.DATA, "banking77")
    os.makedirs(tdir, exist_ok=True)
    with open(os.path.join(tdir, "train.jsonl"), "w", encoding="utf-8") as fh:
        for _, r in train.iterrows():
            fh.write(json.dumps({"text": r["text"], "label": intents[int(r["label"])]},
                                ensure_ascii=False) + "\n")

    manifest[COND] = {"file": f"{COND}.jsonl", "sha256": hashlib.sha256(data).hexdigest(),
                      "requests": len(rows), "decisions": len(rows),
                      "source": f"{REPO}@{REV} test", "per_intent": PER_INTENT,
                      "rule": "8 test utterances per intent, all 77 intents as options in one "
                              "random permutation per item, keys o1..o77",
                      "script": "src/s00f_freeze_banking77.py"}
    assert all(manifest[k] == v for k, v in before.items()), "an existing entry changed"
    with open(man_path, "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2, sort_keys=True)
        fh.write("\n")
    print(f"wrote {dst}: {len(rows)} items, 77 options; train {len(train)} utterances")


if __name__ == "__main__":
    main()
