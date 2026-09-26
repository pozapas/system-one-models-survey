"""Exposure audit of the D2 (CLINC-150) and D3 emotion test items against every public
split they could have been trained or temperature-fitted on.

For each of our 800 D2 texts (600 in-scope from d2_k150, 200 out-of-scope) and each source
split, an item counts as matched when at least one row of the split is

    exact         the identical string
    normalized    identical after lower-casing, removing punctuation, collapsing whitespace
    near_dup_char Jaccard similarity of character 5-gram sets (normalized text) >= 0.8
    near_dup_tok  Jaccard similarity of word sets (normalized text) >= 0.9

Every near-duplicate count includes the exact and normalized matches. Splits that contain
our items by construction (the CLINC test splits) are reported twice: with the item's own
row, which is trivially 800 or its in-scope/out-of-scope share, and "_other_rows", which
drops rows whose raw text equals the item and so counts only other rows of the split.

Sources
    CLINC oos-eval at commit 828f8093 (github.com/clinc/oos-eval): data_full, data_small,
    data_imbalanced, data_oos_plus, splits train/val/test and oos_train/oos_val/oos_test.
    clinc/clinc_oos on the Hugging Face hub, config "plus", revision cached locally: the
    exact dataset decider-2b loads for training (train) and evaluation (test).
    decider-2b's temperature-fitting rows: Mapika/decider decider/data/core.py builds the
    CLINC evaluation rows as clinc_oos/plus test, shuffle(seed=0), first 1500 rows
    (EVAL_CAP = 1500, SEED = 0), and the card and docs/HISTORY.md state that the single
    temperature is fitted by NLL on the in-task evaluation sets. This script rebuilds that
    subsample with the datasets library and counts our items inside it.

The emotion part does the same for d3_emotion against dair-ai/emotion (config split:
train/validation/test; config unsplit) and against decider-2b's emotion evaluation rows
(split test, shuffle(seed=0), first 1500), extending results/exposure.json, which counted
only verbatim overlap with the split train set.

Output: results/clinc_overlap.json
"""
import json
import os
import re
import string

import numpy as np

import common as C

os.environ.setdefault("HF_HOME", "D:/p4env/hf")
CLINC_COMMIT = "828f8093932c8fe6ca7936c3d2e52903b1c523de"
CACHE = "D:/p4env/cache/clinc_" + CLINC_COMMIT[:8]
VARIANTS = ["data_full", "data_small", "data_imbalanced", "data_oos_plus"]
DECIDER_REPO_SHA = "a5120cce45b9ff70964fac54ea6e8c1ac5b08c7f"   # Mapika/decider main, read 2026-09-25
EVAL_CAP, SEED = 1500, 0

_punct = re.compile("[" + re.escape(string.punctuation) + "]")


def norm(s):
    return re.sub(r"\s+", " ", _punct.sub(" ", s.lower())).strip()


def fetch_variant(name):
    os.makedirs(CACHE, exist_ok=True)
    path = os.path.join(CACHE, name + ".json")
    if name == "data_full" and not os.path.exists(path):
        path = os.path.join(C.DATA, "d2", "data_full.json")
    if not os.path.exists(path):
        import requests
        url = f"https://raw.githubusercontent.com/clinc/oos-eval/{CLINC_COMMIT}/data/{name}.json"
        r = requests.get(url, timeout=120)
        r.raise_for_status()
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(r.text)
    return json.load(open(path, encoding="utf-8"))


class Matcher:
    """Exact, normalized and near-duplicate matching of query texts against one pool."""

    def __init__(self, queries):
        from sklearn.feature_extraction.text import CountVectorizer
        self.q = list(queries)
        self.qn = [norm(t) for t in self.q]
        self.cv_c = CountVectorizer(analyzer="char", ngram_range=(5, 5), binary=True,
                                    lowercase=False)
        self.cv_t = CountVectorizer(analyzer=lambda s: set(s.split()), binary=True)
        self.cv_c.fit(self.qn)
        self.cv_t.fit(self.qn)
        self.Qc = self.cv_c.transform(self.qn)
        self.Qt = self.cv_t.transform(self.qn)

    @staticmethod
    def _jac(Q, P, qn_sizes, p_sizes):
        inter = (Q @ P.T).toarray().astype(float)
        union = qn_sizes[:, None] + p_sizes[None, :] - inter
        with np.errstate(divide="ignore", invalid="ignore"):
            return np.where(union > 0, inter / union, 0.0)

    def match(self, pool, exclude_self=False):
        """Per query: best char and token Jaccard, and the matching flags.
        exclude_self drops pool rows whose raw text equals the query."""
        pool = list(pool)
        pn = [norm(t) for t in pool]
        # n-grams absent from every query cannot add to an intersection; they still count
        # in the pool row's own set size, which is computed separately
        from sklearn.feature_extraction.text import CountVectorizer
        full_c = CountVectorizer(analyzer="char", ngram_range=(5, 5), binary=True,
                                 lowercase=False)
        full_t = CountVectorizer(analyzer=lambda s: set(s.split()), binary=True)
        pc_sizes = np.asarray(full_c.fit_transform(pn).sum(1)).ravel().astype(float)
        pt_sizes = np.asarray(full_t.fit_transform(pn).sum(1)).ravel().astype(float)
        Pc = self.cv_c.transform(pn)
        Pt = self.cv_t.transform(pn)
        qc_sizes = np.asarray(self.Qc.sum(1)).ravel().astype(float)
        qt_sizes = np.asarray(self.Qt.sum(1)).ravel().astype(float)
        out = []
        raw_index = {}
        for j, t in enumerate(pool):
            raw_index.setdefault(t, []).append(j)
        norm_index = {}
        for j, t in enumerate(pn):
            norm_index.setdefault(t, []).append(j)
        step = max(10, min(200, int(1e7 / max(1, len(pool)))))
        for a in range(0, len(self.q), step):
            b = min(a + step, len(self.q))
            Jc = self._jac(self.Qc[a:b], Pc, qc_sizes[a:b], pc_sizes)
            Jt = self._jac(self.Qt[a:b], Pt, qt_sizes[a:b], pt_sizes)
            for i in range(a, b):
                jc, jt = Jc[i - a].copy(), Jt[i - a].copy()
                selfrows = raw_index.get(self.q[i], []) if exclude_self else []
                if exclude_self:
                    # drop exactly one row with the item's own raw text; a second copy of
                    # the same string elsewhere in the split is a real duplicate
                    drop = selfrows[:1]
                    jc[drop] = -1
                    jt[drop] = -1
                    n_exact = max(0, len(raw_index.get(self.q[i], [])) - 1)
                    n_norm = max(0, len(norm_index.get(self.qn[i], [])) - 1)
                else:
                    n_exact = len(raw_index.get(self.q[i], []))
                    n_norm = len(norm_index.get(self.qn[i], []))
                kc = int(np.argmax(jc)) if len(jc) else -1
                kt = int(np.argmax(jt)) if len(jt) else -1
                out.append({"exact": n_exact > 0, "normalized": n_norm > 0,
                            "best_char": float(jc[kc]) if kc >= 0 else 0.0,
                            "best_char_text": pool[kc] if kc >= 0 else None,
                            "best_tok": float(jt[kt]) if kt >= 0 else 0.0,
                            "best_tok_text": pool[kt] if kt >= 0 else None,
                            "near_dup_char": bool(kc >= 0 and jc[kc] >= 0.8) or n_norm > 0,
                            "near_dup_tok": bool(kt >= 0 and jt[kt] >= 0.9) or n_norm > 0})
        return out


def summarize(res, items, n_examples=5):
    cnt = {k: int(sum(r[k] for r in res)) for k in
           ("exact", "normalized", "near_dup_char", "near_dup_tok")}
    ins = np.array([it["in_scope"] for it in items])
    for k in list(cnt):
        cnt[k + "_in_scope"] = int(sum(r[k] for r, s in zip(res, ins) if s))
        cnt[k + "_oos"] = int(sum(r[k] for r, s in zip(res, ins) if not s))
    ex = []
    for r, it in zip(res, items):
        if (r["near_dup_char"] or r["near_dup_tok"]) and len(ex) < n_examples:
            ex.append({"item_id": it["item_id"], "text": it["text"],
                       "closest_char5": r["best_char_text"],
                       "char5_jaccard": round(r["best_char"], 3),
                       "closest_token": r["best_tok_text"],
                       "token_jaccard": round(r["best_tok"], 3), "exact": r["exact"],
                       "normalized": r["normalized"]})
    cnt["n_items"] = len(res)
    cnt["examples"] = ex
    return cnt


def decider_subsample(ds):
    """Rows decider/data/core.py keeps for evaluation: _sub(ds, EVAL_CAP, seed=0)."""
    if len(ds) <= EVAL_CAP:
        return ds
    return ds.shuffle(seed=SEED).select(range(EVAL_CAP))


def clinc_audit():
    import datasets
    from datasets import load_dataset
    rows = [json.loads(l) for l in open(os.path.join(C.INPUTS, "d2_k150.jsonl"), encoding="utf-8")]
    items = [{"item_id": r["item_id"], "text": r["state"], "in_scope": r["meta"]["in_scope"],
              "intent": r["meta"]["intent"]} for r in rows]
    M = Matcher([it["text"] for it in items])
    counts, sources = {}, {}
    for v in VARIANTS:
        d = fetch_variant(v)
        sources[v] = {"url": f"https://github.com/clinc/oos-eval/blob/{CLINC_COMMIT}/data/{v}.json",
                      "splits": {k: len(x) for k, x in d.items()}}
        for sp, data in d.items():
            texts = [t for t, _ in data]
            is_test = sp in ("test", "oos_test")
            key = f"{v}/{sp}"
            counts[key] = summarize(M.match(texts), items)
            if is_test:
                counts[key + "_other_rows"] = summarize(M.match(texts, exclude_self=True), items)
            print(key, {k: counts[key][k] for k in ("exact", "normalized", "near_dup_char",
                                                    "near_dup_tok")}, flush=True)
    # the Hugging Face copy decider-2b loads
    snap = os.listdir(os.path.join(os.environ["HF_HOME"], "hub", "datasets--clinc--clinc_oos",
                                   "snapshots"))
    hf = {sp: load_dataset("clinc/clinc_oos", "plus", split=sp) for sp in
          ("train", "validation", "test")}
    sources["hf_clinc_oos_plus"] = {"repo": "clinc/clinc_oos", "config": "plus",
                                    "revision": snap[0], "splits": {k: len(x) for k, x in hf.items()}}
    for sp, ds in hf.items():
        key = f"hf_plus/{sp}"
        counts[key] = summarize(M.match(ds["text"]), items)
        if sp == "test":
            counts[key + "_other_rows"] = summarize(M.match(ds["text"], exclude_self=True), items)
        print(key, {k: counts[key][k] for k in ("exact", "normalized")}, flush=True)
    # decider-2b's CLINC evaluation rows, which its temperature was fitted on
    sub = decider_subsample(hf["test"])
    oos_id = hf["test"].features["intent"].names.index("oos")
    subtexts = set(sub["text"])
    inside = [it for it in items if it["text"] in subtexts]
    names = hf["test"].features["intent"].names
    lab_of = {}
    for t, y in zip(sub["text"], sub["intent"]):
        lab_of.setdefault(t, set()).add(names[y])
    agree = sum(1 for it in inside if (it["intent"] or "oos") in lab_of[it["text"]])
    counts["decider_temperature_fit_rows"] = summarize(M.match(sub["text"]), items)
    counts["decider_temperature_fit_rows"].update({
        "n_rows": len(sub), "n_rows_oos": int(np.sum(np.array(sub["intent"]) == oos_id)),
        "items_inside": len(inside),
        "items_inside_in_scope": sum(it["in_scope"] for it in inside),
        "items_inside_oos": sum(not it["in_scope"] for it in inside),
        "items_inside_label_agrees": agree,
        "expected_if_independent": round(800 * len(sub) / len(hf["test"]), 1)})
    sources["decider_temperature_fit_rows"] = {
        "rule": "clinc/clinc_oos plus test, Dataset.shuffle(seed=0).select(range(1500)), as in "
                "Mapika/decider decider/data/core.py (_split_pair, _both, _sub; EVAL_CAP=1500, SEED=0)",
        "decider_repo_sha_read": DECIDER_REPO_SHA,
        "core_py_history": "three commits (81e154e3b5 2026-09-17, e3d97e5be0 2026-09-18, "
                           "751934af6f 2026-09-19); EVAL_CAP, SEED, _sub and the CLINC loader "
                           "are identical in all three",
        "datasets_version_used_here": datasets.__version__,
        "shuffle": "Dataset.shuffle(seed) draws np.random.default_rng(seed).permutation, which "
                   "is deterministic for a given row count",
        "corroboration": "eval_results.json in the Mapika/decider-2b snapshot d61c1c16 "
                         "reports clinc_oos n = 1500, heldout = false"}
    print("decider temperature-fit rows: items inside", len(inside), flush=True)
    return items, counts, sources


def emotion_audit():
    from datasets import load_dataset
    emo = [json.loads(l) for l in open(os.path.join(C.DATA, "d3", "emotion.jsonl"), encoding="utf-8")]
    items = [{"item_id": str(e["id"]), "text": e["text"], "in_scope": True, "intent": e["gold"]}
             for e in emo]
    M = Matcher([it["text"] for it in items])
    split = {sp: load_dataset("dair-ai/emotion", "split", split=sp)
             for sp in ("train", "validation", "test")}
    uns = load_dataset("dair-ai/emotion", "unsplit", split="train")
    snap = os.listdir(os.path.join(os.environ["HF_HOME"], "hub", "datasets--dair-ai--emotion",
                                   "snapshots"))
    # are the Ziems et al. ids row indices of the unsplit config?
    id_hits = sum(1 for e in emo if int(e["id"]) < len(uns) and uns[int(e["id"])]["text"] == e["text"])
    out = {"sources": {"repo": "dair-ai/emotion", "revision": snap[0],
                       "splits": {**{f"split/{k}": len(v) for k, v in split.items()},
                                  "unsplit/train": len(uns)}},
           "items": len(items),
           "ids_are_unsplit_row_indices": f"{id_hits} of {len(emo)} item ids index a row of "
                                          "dair-ai/emotion unsplit whose text equals the item text",
           "counts": {}}
    for sp, ds in split.items():
        out["counts"][f"split/{sp}"] = summarize(M.match(ds["text"]), items)
        print("emotion", sp, {k: out["counts"][f"split/{sp}"][k] for k in
                              ("exact", "normalized", "near_dup_char", "near_dup_tok")}, flush=True)
    out["counts"]["unsplit/train_other_rows"] = summarize(M.match(uns["text"], exclude_self=True),
                                                          items)
    sub = decider_subsample(split["test"])
    out["counts"]["decider_temperature_fit_rows"] = summarize(M.match(sub["text"]), items)
    out["counts"]["decider_temperature_fit_rows"]["n_rows"] = len(sub)
    for c in out["counts"].values():
        for k in list(c):
            if k.endswith("_in_scope") or k.endswith("_oos"):
                c.pop(k)
    print("emotion unsplit other rows", {k: out["counts"]["unsplit/train_other_rows"][k] for k in
                                         ("exact", "normalized", "near_dup_char")}, flush=True)
    return out


def hub_checks(items):
    """What the hub publishes about the two models' training data, and whether the cached
    dataset revisions are the heads that a 2026 loader would have read."""
    from huggingface_hub import HfApi, hf_hub_download
    api = HfApi()
    out = {"mapika_hub_datasets": [d.id for d in api.list_datasets(author="Mapika")],
           "flock_io_hub_datasets": [d.id for d in api.list_datasets(author="flock-io")]}
    p = hf_hub_download("limberc/this-that-spatial-bench", "test.jsonl", repo_type="dataset")
    t = norm(open(p, encoding="utf-8").read())
    emo = [json.loads(l)["text"] for l in open(os.path.join(C.DATA, "d3", "emotion.jsonl"),
                                                  encoding="utf-8")]
    out["spatial_bench_revision"] = api.dataset_info("limberc/this-that-spatial-bench").sha
    out["spatial_bench_d2_matches"] = sum(norm(it["text"]) in t for it in items
                                          if len(norm(it["text"])) > 15)
    out["spatial_bench_emotion_matches"] = sum(norm(x) in t for x in emo if len(norm(x)) > 15)
    out["spatial_bench_note"] = ("normalized substring search of every D2 and emotion text "
                                 "longer than 15 characters in test.jsonl, the only data file")
    for repo in ("clinc/clinc_oos", "dair-ai/emotion"):
        cs = api.list_repo_commits(repo, repo_type="dataset")
        out[f"{repo}_head"] = {"commit": cs[0].commit_id, "date": cs[0].created_at.isoformat(),
                               "title": cs[0].title}
    ans = os.path.join(C.ANSWERS, "this-that-1.0", "d2_k150__rep1.jsonl")
    j = json.loads(open(ans, encoding="utf-8").readline())
    out["this_that_served_temperature"] = j.get("served_temperature")
    out["this_that_revision"] = j.get("revision")
    out["revision_note"] = ("the cached clinc_oos (155b9c71) and dair-ai/emotion (cab853a1) "
                            "revisions are the heads of both repositories and date from 2024, "
                            "before decider's code (2026-09-17), so a 2026 loader read the same "
                            "row order that the rebuilt subsample uses")
    return out


CARD_QUOTES = [
    {"source": "Mapika/decider-2b model card (README.md at d61c1c16)", "quote":
     "\"In-task\" means the test splits of the training datasets; \"held-out\" means datasets "
     "never seen in training"},
    {"source": "Mapika/decider-2b model card (README.md at d61c1c16)", "quote":
     "Large label sets sub-sampled to 10 options; one temperature fitted on in-task data and "
     "stored in `decider_config.json`."},
    {"source": "Mapika/decider-2b model card (README.md at d61c1c16)", "quote":
     "fine-tune it with cross-entropy, a proper scoring rule, on a mixture of about 95 public "
     "decision datasets"},
    {"source": "Mapika/decider-2b model card (README.md at d61c1c16)", "quote":
     "One epoch on a mixture of public decision datasets (intent detection, ticket routing, "
     "topic classification, sentiment, emotion, moderation, NLI, ..."},
    {"source": "Mapika/decider-2b model card (README.md at d61c1c16)", "quote":
     "Full label sets cost accuracy against 10 sampled options: CLINC 151-way 0.88 against 0.98"},
    {"source": "Mapika/decider-2b decider_config.json (d61c1c16)", "quote": "\"temperature\": 1.3"},
    {"source": "Mapika/decider decider/data/core.py (main, a5120cc)", "quote":
     "tr, ev = _split_pair(\"clinc/clinc_oos\", \"plus\", \"train\", \"test\")"},
    {"source": "Mapika/decider decider/data/core.py (main, a5120cc)", "quote":
     "tr, ev = _split_pair(\"dair-ai/emotion\", \"split\", \"train\", \"test\")"},
    {"source": "Mapika/decider decider/data/core.py (main, a5120cc)", "quote":
     "TRAIN_CAP = 20000     # per task / EVAL_CAP = 1500       # per task / SEED = 0; "
     "_sub(ds, n): ds.shuffle(seed=seed).select(range(n))"},
    {"source": "Mapika/decider docs/HISTORY.md (main, a5120cc)", "quote":
     "Post-hoc temperature is fitted on in-task data and tested on held-out tasks."},
    {"source": "Mapika/decider decider/report.py (main, a5120cc)", "quote":
     "# temperature scaling: fit on in-task eval sets, report held-out"},
    {"source": "Mapika/decider decider/data/mixture.py (main, a5120cc)", "quote":
     "wide        full native label sets (CLINC 151, Banking 77, ...)",
     "note": "formats() builds this component from the training examples only (by_task is "
             "filled from `train`)"},
    {"source": "flock-io/this-that-model-1.0 model card", "quote":
     "Adapted from `decider-2b` (Apache-2.0) against a strictly proper scoring rule"},
    {"source": "flock-io/this-that-model-1.0 model card (YAML)", "quote":
     "base_model: decider-2b", "note": "the card's datasets field names only "
     "limberc/this-that-spatial-bench; no other training or temperature-fitting data is named "
     "and the decider-2b version adapted is not stated"},
    {"source": "flock-io/this-that-model-1.0 model card", "quote":
     "The whole adaptation is a single scalar λ applied as θ(λ) = θ₀ + λΔ"},
    {"source": "note", "quote": None, "note":
     "Neither card uses the words 'evaluation half'; the decider-2b card says the temperature "
     "was fitted on in-task data, which it defines as the test splits of the training datasets."},
]


def main():
    items, counts, sources = clinc_audit()
    emo = emotion_audit()
    hub = hub_checks(items)
    t = counts["decider_temperature_fit_rows"]
    tr = counts["hf_plus/train"]
    conclusion = (
        f"Training exposure: decider-2b trains on clinc/clinc_oos plus train and dair-ai/emotion "
        f"split train. Of our 800 D2 test texts, {tr['exact']} occur verbatim, {tr['normalized']} "
        f"after normalization, {tr['near_dup_char']} as character 5-gram near-duplicates "
        f"(Jaccard >= 0.8) and {tr['near_dup_tok']} as token near-duplicates (Jaccard >= 0.9) in "
        f"that training split. Temperature-fitting exposure: decider-2b's card defines in-task "
        f"data as the test splits of its training datasets and fits one temperature on it; the "
        f"published loader keeps 1500 rows of clinc_oos plus test (shuffle seed 0). Rebuilding "
        f"that subsample puts {t['items_inside']} of our 800 items inside it "
        f"({t['items_inside_in_scope']} in-scope, {t['items_inside_oos']} out-of-scope; "
        f"{t['expected_if_independent']} expected by chance). This is established for the "
        f"public loader code as released (core.py unchanged across its three commits) and the "
        f"cached clinc_oos revision, and the label of every item inside agrees with its CLINC "
        f"label. It cannot be established from public material that the released v10 "
        f"temperature (1.3 in decider_config.json) was fitted with this exact code state and dataset "
        f"revision, because the fitting run and its row list are not published. The fit pooled "
        f"the in-task evaluation sets of all tasks (67 in the rebuilt regression set, at most "
        f"1500 rows each) with label sets sub-sampled to 10 options, so our items would enter "
        f"one scalar temperature as a small share of the pool. The exposure concerns the "
        f"stored temperature only: D2 accuracy does not depend on it, and the benchmark's "
        f"scaled ECE for D2 refits T by five-fold cross-fitting on our items. "
        f"this-that-model-1.0 is adapted from decider-2b and inherits the training exposure of "
        f"the parent version it started from; its card names no other data, and it serves "
        f"temperature {hub['this_that_served_temperature']} (no stored temperature), so "
        f"decider-2b's temperature-fitting exposure does not carry over to its served "
        f"probabilities. Neither training mixture is published on the hub (Mapika publishes only "
        f"{', '.join(hub['mapika_hub_datasets'])}); the one dataset this-that names, "
        f"limberc/this-that-spatial-bench, is a grid and game-state benchmark with "
        f"{hub['spatial_bench_d2_matches']} D2 and {hub['spatial_bench_emotion_matches']} emotion "
        f"text matches. Emotion: "
        f"{emo['counts']['split/train']['exact']} of 498 d3_emotion items are verbatim in "
        f"dair-ai/emotion split train (decider-2b training data), "
        f"{emo['counts']['split/train']['near_dup_char']} counting character near-duplicates; "
        f"{emo['counts']['decider_temperature_fit_rows']['exact']} of 498 are in decider-2b's "
        f"emotion temperature-fitting rows. All 498 item ids are row indices of dair-ai/emotion "
        f"unsplit, the source of Ziems et al.'s test file, which is why a few items also fall "
        f"in the split train, validation and test sets.")
    out = {"_doc": ("CLINC-150 (D2) and emotion (D3) exposure audit written by "
                    "shared/src/b02_clinc_overlap.py. counts[split] gives, for our 800 D2 test "
                    "texts, the number of items with at least one matching row in that split: "
                    "exact string, normalized (lower-case, punctuation removed, whitespace "
                    "collapsed), near_dup_char (character 5-gram Jaccard >= 0.8 on normalized "
                    "text) and near_dup_tok (word-set Jaccard >= 0.9); near-duplicate counts "
                    "include exact and normalized matches, and *_in_scope / *_oos split them by "
                    "our 600 in-scope and 200 out-of-scope items. Split keys are <variant>/<split> "
                    "for the four oos-eval JSON files at commit 828f8093, hf_plus/<split> for "
                    "clinc/clinc_oos config plus on the hub, and decider_temperature_fit_rows for "
                    "the rebuilt 1500-row CLINC evaluation subsample decider-2b's temperature was "
                    "fitted on. Test splits contain our items by construction, so they also have "
                    "a *_other_rows entry that excludes the item's own row. emotion holds the same "
                    "structure for the 498 d3_emotion items. card_quotes hold verbatim excerpts (quote) and our "
                    "reading (note); hub_checks records what the Hugging Face hub publishes."),
           "sources": sources, "counts": counts, "emotion": emo,
           "card_quotes": CARD_QUOTES, "hub_checks": hub, "conclusion": conclusion}
    C.dump(out, "clinc_overlap.json")
    print(conclusion)


if __name__ == "__main__":
    main()
