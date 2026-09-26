"""Test-set exposure: which benchmark items or label sources appear in a model's training data.

Documented training sources (from each model's card or repository, accessed 2026-09-24):
    decider-2b      trains on dair-ai/emotion (train split) and clinc/clinc_oos (train split),
                    among about 95 public tasks (Mapika/decider, decider/data/core.py)
    this-that-1.0   adapted from decider-2b, so it inherits that exposure
    kev-*           ten public sources (banking77, boolq, ag_news, multi_nli, sst5, yelp, trec,
                    dbpedia_14, amazon_reviews_multi_en, imdb); none of D1 to D3
    nimble-9b       released training file bespokelabsai/nimble data/train.jsonl, checked below
    laya-*, jev     training data not released

For the emotion task the script counts D3 items whose text appears verbatim in the dair-ai
emotion training split and reports each model's emotion accuracy with those items removed, so a
difference between models can be read as more than item memorization. It also counts verbatim
overlaps between every benchmark state and Nimble's released training file.

Output: results/exposure.json
"""
import json
import os
import re

import numpy as np

import bench
import common as C

norm = lambda s: re.sub(r"\s+", " ", s.strip().lower())


def main():
    from datasets import load_dataset
    import requests
    tr = load_dataset("dair-ai/emotion", "split", split="train")
    trset = set(norm(t) for t in tr["text"])
    emo = [json.loads(l) for l in open(os.path.join(C.DATA, "d3", "emotion.jsonl"), encoding="utf-8")]
    seen = {str(e["id"]) for e in emo if norm(e["text"]) in trset}
    res = {"emotion_items_in_dair_train": len(seen), "emotion_items": len(emo),
           "by_model": {}}
    for m in [bench.JEV] + bench.MODELS_OPEN + ["comparator-open"]:
        if not bench.available_reps(m, "d3_emotion"):
            continue
        rows = [r for r in bench.decisions(m, "d3_emotion") if r["y"] >= 0
                and not np.isnan(r["p"]).any()]
        cor = np.array([np.argmax(r["p"]) == r["y"] for r in rows])
        unseen = np.array([r["item_id"] not in seen for r in rows])
        res["by_model"][m] = {"acc_all": float(cor.mean()),
                              "acc_unseen": float(cor[unseen].mean()),
                              "n_unseen": int(unseen.sum())}
        print(m, res["by_model"][m])
    g = requests.get("https://raw.githubusercontent.com/bespokelabsai/nimble/main/data/train.jsonl",
                     timeout=120)
    if g.ok:
        txt = norm(g.text)
        hits = {}
        for cond in ["d1_neutral", "d2_k150", "d3_conv_go_awry", "d3_wiki_corpus", "d3_emotion",
                     "d3_wiki_politeness"]:
            n = 0
            for r in bench.inputs(cond):
                s = r["state"] if isinstance(r["state"], str) else json.dumps(r["state"])
                s = norm(s)
                probe = s if len(s) < 120 else s[:120]
                n += probe in txt
            hits[cond] = n
        res["nimble_train_overlap"] = hits
        print("nimble overlap", hits)
    res["documented_sources"] = __doc__.split("Documented training sources")[1].split("For the")[0]
    C.dump(res, "exposure.json")


if __name__ == "__main__":
    main()
