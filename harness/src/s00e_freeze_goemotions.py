"""A human-rated emotion task (fourth revision): GoEmotions mapped to Ekman's six emotions.

The emotion task of D3 carries distant labels taken from hashtags. GoEmotions (Demszky et
al., 2020) labels Reddit comments with 27 emotions by three to five raters each, and its
"simplified" configuration keeps a label only when at least two raters chose it. The dataset
authors map the 27 emotions onto Ekman's six basic emotions (EKMAN below, from the GoEmotions
repository's ekman_mapping.json). This script keeps the comments whose retained labels all map
to one Ekman emotion (neutral excluded), so every item has a single rater-agreed label, and
asks the question of the D3 emotion task with the six Ekman emotions as options.

Source: huggingface.co/datasets/google-research-datasets/go_emotions at revision
add492243ff905527e67aeb8b80c082af02207c3 (Apache-2.0), files simplified/{train,test}.parquet.

Writes
  colab/inputs/d3_goemotions.jsonl      test items, stratified: up to PER_CLASS per emotion,
                                        drawn with random.Random(f"{SEED}-goemotions")
  data/goemotions/train.jsonl           single-Ekman training comments (text, label) for the
                                        trained classifiers; never shipped as a model input
and one manifest.json entry (every existing entry is asserted unchanged).

Usage: python s00e_freeze_goemotions.py
"""
import hashlib
import json
import os
import random

import pandas as pd
from huggingface_hub import hf_hub_download

import common as C

REPO = "google-research-datasets/go_emotions"
REV = "add492243ff905527e67aeb8b80c082af02207c3"
COND = "d3_goemotions"
PER_CLASS = 84
GOEMO = ["admiration", "amusement", "anger", "annoyance", "approval", "caring", "confusion",
         "curiosity", "desire", "disappointment", "disapproval", "disgust", "embarrassment",
         "excitement", "fear", "gratitude", "grief", "joy", "love", "nervousness", "optimism",
         "pride", "realization", "relief", "remorse", "sadness", "surprise", "neutral"]
EKMAN = {"anger": ["anger", "annoyance", "disapproval"],
         "disgust": ["disgust"],
         "fear": ["fear", "nervousness"],
         "joy": ["joy", "amusement", "approval", "excitement", "gratitude", "love", "optimism",
                 "relief", "pride", "admiration", "desire", "caring"],
         "sadness": ["sadness", "disappointment", "embarrassment", "grief", "remorse"],
         "surprise": ["surprise", "realization", "confusion", "curiosity"]}
OPTIONS = ["Anger", "Disgust", "Fear", "Joy", "Sadness", "Surprise"]
QUESTION = ("If a mental health professional saw the above text, what emotion would they "
            "categorize it to be (using the following six basic emotions according to Paul "
            "Ekman)?")
TO_EKMAN = {g: e for e, gs in EKMAN.items() for g in gs}


def single_ekman(labels):
    names = [GOEMO[i] for i in labels]
    if "neutral" in names:
        return None
    ek = {TO_EKMAN[n] for n in names}
    return ek.pop() if len(ek) == 1 else None


def load(split):
    p = hf_hub_download(REPO, f"simplified/{split}-00000-of-00001.parquet",
                        repo_type="dataset", revision=REV)
    df = pd.read_parquet(p)
    rows = []
    for _, r in df.iterrows():
        e = single_ekman(list(r["labels"]))
        if e:
            rows.append({"id": r["id"], "text": r["text"], "ekman": e})
    return rows


def main():
    man_path = os.path.join(C.INPUTS, "manifest.json")
    manifest = json.load(open(man_path, encoding="utf-8"))
    before = json.loads(json.dumps(manifest))
    dst = os.path.join(C.INPUTS, f"{COND}.jsonl")
    assert not os.path.exists(dst), f"{dst} exists; this script writes new files only"

    test = load("test")
    rng = random.Random(f"{C.SEED}-goemotions")
    picked = []
    for e in sorted(EKMAN):
        pool = sorted([r for r in test if r["ekman"] == e], key=lambda r: r["id"])
        picked += rng.sample(pool, min(PER_CLASS, len(pool)))
    keys = [f"o{i + 1}" for i in range(len(OPTIONS))]
    crit = dict(zip(keys, OPTIONS))
    out = []
    for r in picked:
        gold = keys[OPTIONS.index(r["ekman"].capitalize())]
        out.append({"key": f"{COND}|{r['id']}", "dataset": "d3", "condition": COND,
                    "item_id": r["id"], "state": r["text"],
                    "questions": {"emotion": {"type": "choice", "instructions": QUESTION,
                                              "criteria": crit}},
                    "gold": {"emotion": {"type": "choice", "label": gold, "options": keys,
                                         "native_options": [o.lower() for o in OPTIONS],
                                         "soft": None}},
                    "meta": {"task": "goemotions", "binary": False, "positive": None,
                             "native_gold": r["ekman"]}})
    data = "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in out).encode("utf-8")
    with open(dst, "wb") as fh:
        fh.write(data)

    train = load("train")
    tdir = os.path.join(C.DATA, "goemotions")
    os.makedirs(tdir, exist_ok=True)
    with open(os.path.join(tdir, "train.jsonl"), "w", encoding="utf-8") as fh:
        for r in train:
            fh.write(json.dumps({"id": r["id"], "text": r["text"], "label": r["ekman"]},
                                ensure_ascii=False) + "\n")

    counts = {e: sum(r["ekman"] == e for r in picked) for e in sorted(EKMAN)}
    manifest[COND] = {"file": f"{COND}.jsonl", "sha256": hashlib.sha256(data).hexdigest(),
                      "requests": len(out), "decisions": len(out),
                      "source": f"{REPO}@{REV} simplified/test", "per_class": counts,
                      "rule": "comments whose rater-agreed labels map to one Ekman emotion, "
                              "neutral excluded; up to 84 per emotion",
                      "script": "src/s00e_freeze_goemotions.py"}
    assert all(manifest[k] == v for k, v in before.items()), "an existing entry changed"
    with open(man_path, "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2, sort_keys=True)
        fh.write("\n")
    print(f"wrote {dst}: {len(out)} items {counts}; train {len(train)} single-Ekman comments")


if __name__ == "__main__":
    main()
