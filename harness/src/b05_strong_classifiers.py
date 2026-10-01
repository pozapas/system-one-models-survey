"""Fine-tuned DeBERTa-v3-large classifiers on exactly the frozen benchmark items (fourth revision).

A stronger trained baseline than bert-base-clinc and bge-small-lr-d3: microsoft/deberta-v3-large
(pinned below) fine-tuned as a sequence classifier, one model per task, written as answer files
in the format of b01.write_answers (answers/<tag>/<cond>__rep1.jsonl), so bench.py and the
analysis scripts read them like any other baseline.

  baseline-deberta-large-clinc    d2_k150        the bert-base-clinc recipe of b01: CLINC-150 train
                                                 + oos_train of data_oos_plus at 828f8093 (rows
                                                 matching a test text after normalization
                                                 removed), 151-way head, validation = val +
                                                 oos_val; the served distribution is the softmax
                                                 over the offered intents (the out-of-scope logit
                                                 is dropped), max 64 tokens
  baseline-deberta-large-d3       d3_conv_go_awry, d3_wiki_corpus, d3_emotion, d3_wiki_politeness
                                                 the training and validation rows of
                                                 bge-small-lr-d3 (b04.build_pool, the test
                                                 conversations removed as b04 removes them, then
                                                 b04.cap_and_split with a fresh
                                                 numpy.random.default_rng(common.SEED) per task),
                                                 class-weighted loss (the "balanced" weights of
                                                 b04's regression), max 512 tokens
  baseline-deberta-large-goemo    d3_goemotions  data/goemotions/train.jsonl (s00e), rows whose
                                                 normalized text equals a test text removed, then
                                                 b04.cap_and_split as for D3, class-weighted loss,
                                                 max 512 tokens
  baseline-deberta-large-banking  d2_banking77   data/banking77/train.jsonl (s00f), rows whose
                                                 normalized text equals a test text removed; no
                                                 validation split exists, so 20% of the rows of
                                                 every intent (seed common.SEED) are held out as
                                                 validation; unweighted loss as for CLINC, max
                                                 128 tokens
  baseline-deberta-large-d1       d1_neutral, d1_calib
                                                 one cross-encoder on the 900 typed-decisions
                                                 training states of bge-small-lr-d1 (outside
                                                 d1_calib and d1_neutral; b01.d1_train_states):
                                                 each (state text as b01.state_text, question
                                                 instructions + newline + option description)
                                                 pair gets one logit, a softmax runs over each
                                                 question's options, and the loss is the
                                                 cross-entropy against the teacher's soft
                                                 distribution (b01's target); 20% of the states
                                                 of every workflow held out for validation;
                                                 selection by validation soft cross-entropy
                                                 (b01's D1 rule), one temperature per question
                                                 type on the validation states; max 512 tokens,
                                                 8 questions per step (run_d1)

Training (the finetune_bert loop of b01): AdamW, weight decay 0.01, batch 32, linear warm-up over
10% of the steps then linear decay, gradient clipping at 1.0, fp32 master weights with bf16
autocast on a GPU that supports it (fp32 otherwise), dynamic padding. A batch of 32 is split into
length-sorted micro-batches under a padded-token budget (gradient accumulation), so the update is
the same as one batch of 32; on out-of-memory the budget is halved and the batch redone. Seeds are
common.SEED throughout.

Selection and calibration (the b01 and b04 rules): a grid of learning rates LRS by epochs 1 to
EPOCHS; after each epoch the validation accuracy is computed (ties by NLL) over the classes the
test offers (CLINC: in-scope rows, 150-way, as b01.val_T_150; D3 and GoEmotions: the
class-balanced validation part of b04.cap_and_split); the best (learning rate, epoch) is kept.
b01 used learning rates 3e-5 and 5e-5 for BERT-base; DeBERTa-v3-large often diverges at those
rates, so the grid is 1e-5 and 2e-5. One temperature (metrics.fit_T) is fitted on the same
validation rows with the selected model and stored with the answers (raw.fitted_temperature,
raw.probs_scaled); "probs" are the T = 1 outputs.

latency_s is the median batch-1 time on the GPU, text to probabilities, over up to 100 test
items, as b01 records it; <tag>/<cond>__fit.json holds the grid, the selection, the temperature,
row counts, truncation counts, the hardware, the training minutes and the test log-probabilities
over all classes.

Commands
    python b05_strong_classifiers.py freeze --out DIR
        Local only (needs the b01/b04 caches). Writes the frozen training, validation and test
        rows, one <task>.jsonl per task, and b05_meta.json. The D3 rows are checked against the
        train_src and val_src lists b04 cached; the CLINC counts against b01's.
    python b05_strong_classifiers.py run --groups clinc,goemo,banking,d3 [--data DIR]
            [--inputs DIR] [--answers DIR] [--smoke] [--model ID --revision SHA]
        Trains and writes the answers. A condition whose answer file already holds every key is
        skipped. --smoke trains on a few rows for one epoch at one learning rate and answers a
        few items (tiny test model by default), to test the pipeline; it needs --answers.
Defaults: --data $P4_B05_DATA or shared/data/b05, --inputs $P4_INPUTS or shared/colab/inputs,
--answers $P4_ANSWERS or shared/answers.
"""
import argparse
import json
import math
import os
import sys
import time

import numpy as np

import common as C
import metrics as M

MODEL_ID = "microsoft/deberta-v3-large"
MODEL_REV = "64a8c8eab3e352a784c658aef62be1662607476f"   # huggingface_hub.model_info, 2026-09-29
SMOKE_MODEL = "hf-internal-testing/tiny-random-DebertaV2ForSequenceClassification"
SMOKE_REV = "035f03d5411169990d9ac33970a084ad98c0769a"    # huggingface_hub.model_info, 2026-09-29
LRS = (1e-5, 2e-5)
EPOCHS = 4
BATCH = 32
WARMUP = 0.1
WEIGHT_DECAY = 0.01
TOKENS_PER_MICRO = int(os.environ.get("B05_TOKENS_PER_MICRO", "4096"))
VAL_SHARE = 0.2
SMOKE_TRAIN, SMOKE_VAL, SMOKE_TEST = 48, 24, 6
RUN_DATE = time.strftime("%Y-%m-%d")

# task -> group, condition, tag, max tokens, class-weighted loss, how test options map to classes
TASKS = {
    "clinc": ("clinc", "d2_k150", "baseline-deberta-large-clinc", 64, False, "native"),
    "goemotions": ("goemo", "d3_goemotions", "baseline-deberta-large-goemo", 512, True, "position"),
    "banking77": ("banking", "d2_banking77", "baseline-deberta-large-banking", 128, False, "native"),
    "emotion": ("d3", "d3_emotion", "baseline-deberta-large-d3", 512, True, "position"),
    "wiki_politeness": ("d3", "d3_wiki_politeness", "baseline-deberta-large-d3", 512, True,
                        "position"),
    "conv_go_awry": ("d3", "d3_conv_go_awry", "baseline-deberta-large-d3", 512, True, "position"),
    "wiki_corpus": ("d3", "d3_wiki_corpus", "baseline-deberta-large-d3", 512, True, "position"),
    # one cross-encoder answers both D1 conditions (D1_CONDS); see run_d1
    "d1": ("d1", "d1_neutral", "baseline-deberta-large-d1", 512, False, "d1"),
}
GROUPS = ["clinc", "goemo", "banking", "d3", "d1"]    # the order of a full run
D3_TASKS = ["conv_go_awry", "wiki_corpus", "emotion", "wiki_politeness"]
D1_CONDS = ["d1_neutral", "d1_calib"]
D1_BATCH_Q = 8                   # questions per optimizer step (about 27 option rows)
D1_SMOKE_TRAIN, D1_SMOKE_VAL = 16, 8     # states


def d1_option_text(q, i, name):
    """The description of option i (key `name`) of a D1 question: the criteria text when the
    question ships one (a dict keyed by option name, or a list for score questions), else a
    plain yes or no for a noul question without criteria. The same rule builds training and
    test rows. Pure function."""
    crit = q.get("criteria")
    if isinstance(crit, dict) and name in crit:
        v = crit[name]
    elif isinstance(crit, list):
        v = crit[i]
    elif q["type"] == "noul":
        v = "Yes." if name == "true" else "No."
    else:
        v = name.replace("_", " ")
    return v if isinstance(v, str) else json.dumps(v, ensure_ascii=False)


def d1_second(q, text):
    """Second segment of a D1 cross-encoder pair: the question's instructions, then the option."""
    return f"{q['instructions']}\n{text}"


# ====================================================================== freeze (local only)

def _dump_rows(rows):
    return "".join(json.dumps(r, ensure_ascii=False, sort_keys=True, default=C._jsonable) + "\n"
                   for r in rows).encode("utf-8")


def _row(split, text, y=None, key=None):
    r = {"split": split, "text": text}
    if y is not None:
        r["y"] = int(y)
    if key is not None:
        r["key"] = key
    return r


def freeze_files():
    """{file name: bytes} of the frozen rows. Imports b01 and b04 lazily: their data sources
    (the CLINC file, ConvoKit, dair-ai/emotion) live in local caches, never on the GPU host."""
    import b01_baselines as B1
    import b04_baselines_d3 as B4
    import bench
    from b02_clinc_overlap import norm

    files, meta = {}, {}

    # ---------------------------------------------------------------- CLINC (b01.clinc)
    Xtr, ytr, Xva, yva, intents, cls, info = B1.clinc()
    classes = list(intents) + ["oos"]
    assert all(cls[c] == i for i, c in enumerate(classes))
    ref = os.path.join(B1.CACHE, "d2_bert.json")
    if os.path.exists(ref):
        d = json.load(open(ref, encoding="utf-8"))["data"]
        for k in ("train_rows", "val_rows", "train_dropped_normalized_match_to_test",
                  "val_dropped_normalized_match_to_test"):
            assert d[k] == info[k], (k, d[k], info[k])
    test = bench.inputs("d2_k150")
    rows = ([_row("train", t, y) for t, y in zip(Xtr, ytr)]
            + [_row("val", t, y) for t, y in zip(Xva, yva)]
            + [_row("test", r["state"], key=r["key"]) for r in test])
    files["clinc.jsonl"] = _dump_rows(rows)
    meta["clinc"] = {"classes": classes, "served_classes": list(range(150)),
                     "info": {k: v for k, v in info.items() if k != "dropped_texts"},
                     "dropped_texts": info["dropped_texts"],
                     "source": f"clinc/oos-eval data_oos_plus.json at {B1.CLINC_COMMIT[:8]}, "
                               "train + oos_train, validation val + oos_val (b01.clinc)",
                     "checked_against": "b01 cache d2_bert.json row and drop counts"}

    # ---------------------------------------------------------------- D3 (b04 rows)
    for task in D3_TASKS:
        cond = "d3_" + task
        K = len(bench.inputs(cond)[0]["gold"][task]["options"])
        pool, test, info = B4.build_pool(task)
        rng = np.random.default_rng(C.SEED)
        sel, tr, va, vab = B4.cap_and_split(pool, K, rng)
        ref = os.path.join(B1.CACHE, f"d3_{task}.data.json")
        checked = False
        if os.path.exists(ref):
            d = json.load(open(ref, encoding="utf-8"))
            rt = lambda xs: json.loads(json.dumps(xs, default=C._jsonable))   # noqa: E731
            assert rt([pool[i]["src"] for i in tr]) == rt(d["train_src"]), task
            assert rt([pool[i]["src"] for i in vab]) == rt(d["val_src"]), task
            assert [t["key"] for t in test] == d["test_keys"], task
            checked = True
        rows = ([_row("train", pool[i]["text"], pool[i]["y"]) for i in tr]
                + [_row("val", pool[i]["text"], pool[i]["y"]) for i in vab]
                + [_row("test", t["text"], t["y"], t["key"]) for t in test])
        files[f"{task}.jsonl"] = _dump_rows(rows)
        cnt = lambda ix: {f"o{k + 1}": int(sum(pool[i]["y"] == k for i in ix))   # noqa: E731
                          for k in range(K)}
        info = {k: v for k, v in info.items() if k != "dropped_train_row_indices"}
        info.update({"rows_after_cap": len(sel), "train_rows": len(tr),
                     "val_rows_before_balancing": len(va), "val_rows": len(vab),
                     "train_class_counts": cnt(tr), "val_class_counts": cnt(vab)})
        meta[task] = {"classes": [f"o{k + 1}" for k in range(K)], "served_classes": list(range(K)),
                      "info": info, "source": "b04.build_pool and b04.cap_and_split (the rows "
                      "of bge-small-lr-d3)",
                      "checked_against": ("b04 cache d3_%s.data.json train_src, val_src and "
                                          "test_keys" % task) if checked else None}

    # ---------------------------------------------------------------- GoEmotions
    test = bench.inputs("d3_goemotions")
    qid = next(iter(test[0]["gold"]))
    native = test[0]["gold"][qid]["native_options"]
    assert all(r["gold"][qid]["native_options"] == native for r in test)
    tn = {norm(r["state"]) for r in test}
    src = [json.loads(l) for l in open(os.path.join(C.DATA, "goemotions", "train.jsonl"),
                                       encoding="utf-8")]
    pool = [{"group": r["id"], "src": r["id"], "text": r["text"], "y": native.index(r["label"])}
            for r in src]
    keep = [r for r in pool if norm(r["text"]) not in tn]
    info = {"rows_in_source": len(pool), "rows_dropped_normalized_text_match": len(pool) - len(keep)}
    K = len(native)
    rng = np.random.default_rng(C.SEED)
    sel, tr, va, vab = B4.cap_and_split(keep, K, rng)
    tt = {r["state"] for r in test}
    info["overlap_after_filter"] = {"exact": sum(keep[i]["text"] in tt for i in sel),
                                    "normalized": sum(norm(keep[i]["text"]) in tn for i in sel)}
    assert info["overlap_after_filter"] == {"exact": 0, "normalized": 0}
    cnt = lambda ix: {f"o{k + 1}": int(sum(keep[i]["y"] == k for i in ix))   # noqa: E731
                      for k in range(K)}
    info.update({"rows_available": len(keep), "rows_after_cap": len(sel), "train_rows": len(tr),
                 "val_rows_before_balancing": len(va), "val_rows": len(vab),
                 "train_class_counts": cnt(tr), "val_class_counts": cnt(vab)})
    opts = test[0]["gold"][qid]["options"]
    rows = ([_row("train", keep[i]["text"], keep[i]["y"]) for i in tr]
            + [_row("val", keep[i]["text"], keep[i]["y"]) for i in vab]
            + [_row("test", r["state"], opts.index(r["gold"][qid]["label"]), r["key"])
               for r in test])
    files["goemotions.jsonl"] = _dump_rows(rows)
    meta["goemotions"] = {"classes": list(opts), "native": list(native),
                          "served_classes": list(range(K)), "info": info,
                          "source": "data/goemotions/train.jsonl (s00e_freeze_goemotions.py, "
                                    "GoEmotions simplified train split, single-Ekman comments); "
                                    "b04.cap_and_split with numpy.random.default_rng(common.SEED)"}

    # ---------------------------------------------------------------- Banking77
    test = bench.inputs("d2_banking77")
    tn = {norm(r["state"]) for r in test}
    src = [json.loads(l) for l in open(os.path.join(C.DATA, "banking77", "train.jsonl"),
                                       encoding="utf-8")]
    classes = sorted({r["label"] for r in src})
    assert len(classes) == 77
    assert all(set(r["gold"]["intent"]["native_options"]) == set(classes) for r in test)
    keep = [r for r in src if norm(r["text"]) not in tn]
    info = {"rows_in_source": len(src), "rows_dropped_normalized_text_match": len(src) - len(keep)}
    rng = np.random.default_rng(C.SEED)
    tr, va = [], []
    for c in classes:
        ix = [i for i, r in enumerate(keep) if r["label"] == c]
        ix = [ix[j] for j in rng.permutation(len(ix))]
        n_val = int(round(VAL_SHARE * len(ix)))
        va += ix[:n_val]
        tr += ix[n_val:]
    tr, va = sorted(tr), sorted(va)
    tt = {r["state"] for r in test}
    info["overlap_after_filter"] = {"exact": sum(r["text"] in tt for r in keep),
                                    "normalized": sum(norm(r["text"]) in tn for r in keep)}
    assert info["overlap_after_filter"] == {"exact": 0, "normalized": 0}
    info.update({"train_rows": len(tr), "val_rows": len(va),
                 "train_rows_per_intent_min_max": [min(sum(keep[i]["label"] == c for i in tr)
                                                       for c in classes),
                                                   max(sum(keep[i]["label"] == c for i in tr)
                                                       for c in classes)]})
    cix = {c: i for i, c in enumerate(classes)}
    rows = ([_row("train", keep[i]["text"], cix[keep[i]["label"]]) for i in tr]
            + [_row("val", keep[i]["text"], cix[keep[i]["label"]]) for i in va]
            + [_row("test", r["state"], cix[r["meta"]["intent"]], r["key"]) for r in test])
    files["banking77.jsonl"] = _dump_rows(rows)
    meta["banking77"] = {"classes": classes, "served_classes": list(range(77)), "info": info,
                         "source": "data/banking77/train.jsonl (s00f_freeze_banking77.py, "
                                   "legacy-datasets/banking77 train split); validation = 20% of "
                                   "the rows of every intent, numpy.random.default_rng(common.SEED)"}

    # ---------------------------------------------------------------- D1 (b01's states)
    train = B1.d1_train_states()                    # soft teacher labels, b01's name order
    from datasets import load_dataset
    ds = load_dataset(B1.D1_REPO, "all", split="train", revision=B1.D1_REV)
    qs_of = {r["id"]: (json.loads(r["questions"]), json.loads(r["gold"])) for r in ds}
    calib = {r["item_id"] for r in bench.inputs("d1_calib")}
    test_ids = {r["item_id"] for r in bench.inputs("d1_neutral")}
    pool = [r for r in train if r["id"] not in calib and r["id"] not in test_ids]
    assert len(pool) == 900 and not ({r["id"] for r in train} & test_ids)
    rng = np.random.default_rng(C.SEED)
    val_ids = set()
    for wf in sorted({r["workflow"] for r in pool}):
        ids = sorted(r["id"] for r in pool if r["workflow"] == wf)
        ids = [ids[j] for j in rng.permutation(len(ids))]
        val_ids |= set(ids[:int(round(VAL_SHARE * len(ids)))])
    rows, train_texts = [], set()
    for r in pool:
        qs, gold = qs_of[r["id"]]
        questions = []
        for qid, q in qs.items():
            if q["type"] == "choice":
                names = list(q["criteria"].keys())
            elif q["type"] == "noul":
                names = ["false", "true"]
            else:
                names = [str(i) for i in range(len(q["criteria"]))]
            soft = r["soft"][qid]
            texts = [d1_second(q, d1_option_text(q, i, n)) for i, n in enumerate(names)]
            train_texts |= set(texts)
            questions.append({"qid": qid, "type": q["type"], "texts": texts,
                              "soft": [float(x) / float(sum(soft)) for x in soft],
                              "label": names.index(gold[qid]["label"])})
        rows.append({"split": "val" if r["id"] in val_ids else "train", "id": r["id"],
                     "workflow": r["workflow"], "text": B1.state_text(r["state"]),
                     "questions": questions})
    n_test_q, unseen = 0, 0
    for cond in D1_CONDS:
        for r in bench.inputs(cond):
            questions = []
            for qid, g in r["gold"].items():
                q = r["questions"][qid]
                texts = [d1_second(q, d1_option_text(q, i, o)) for i, o in enumerate(g["options"])]
                unseen += sum(t not in train_texts for t in texts)
                n_test_q += 1
                questions.append({"qid": qid, "type": g["type"], "texts": texts,
                                  "options": g["options"]})
            rows.append({"split": "test", "cond": cond, "key": r["key"],
                         "text": B1.state_text(r["state"]), "questions": questions})
    assert unseen == 0, f"{unseen} test option texts never occur in training"
    files["d1.jsonl"] = _dump_rows(rows)
    n_tr = sum(r["split"] == "train" for r in rows)
    n_va = sum(r["split"] == "val" for r in rows)
    meta["d1"] = {"classes": [], "served_classes": [], "conditions": D1_CONDS,
                  "info": {"train_rows": n_tr, "val_rows": n_va,
                           "train_questions": sum(len(r["questions"]) for r in rows
                                                  if r["split"] == "train"),
                           "val_questions": sum(len(r["questions"]) for r in rows
                                                if r["split"] == "val"),
                           "test_questions": n_test_q,
                           "excluded": "the 300 d1_calib states and all d1_neutral states"},
                  "source": f"{B1.D1_REPO} train split at {B1.D1_REV[:8]}, the 900 states of "
                            "bge-small-lr-d1 (b01.d1_train_states), soft teacher labels; 20% of "
                            "the states of every workflow held out for validation, "
                            "numpy.random.default_rng(common.SEED)",
                  "input": "pair (state text as b01.state_text, instructions + newline + option "
                           "description), one logit per option, softmax over the question's "
                           "options, loss = cross-entropy against the teacher distribution"}

    for task, (group, cond, tag, max_len, weighted, mapping) in TASKS.items():
        meta[task].update({"group": group, "condition": cond, "tag": tag, "max_len": max_len,
                           "class_weighted": weighted, "option_mapping": mapping})
    files["b05_meta.json"] = (json.dumps(meta, indent=1, sort_keys=True, ensure_ascii=False,
                                         default=C._jsonable) + "\n").encode("utf-8")
    return files


def cmd_freeze(out):
    os.makedirs(out, exist_ok=True)
    files = freeze_files()
    for fn, data in files.items():
        with open(os.path.join(out, fn), "wb") as fh:
            fh.write(data)
    meta = json.loads(files["b05_meta.json"])
    for task, m in meta.items():
        print(f"{task:16s} train {m['info'].get('train_rows')} val {m['info'].get('val_rows')} "
              f"classes {len(m['classes']) or 'per question'} checked: {m.get('checked_against')}")
    print(f"wrote {len(files)} files to {out}")


# ====================================================================== training

def softmax(z):
    z = np.asarray(z, dtype=np.float64)
    z = z - z.max(-1, keepdims=True)
    e = np.exp(z)
    return e / e.sum(-1, keepdims=True)


class Runner:
    def __init__(self, args):
        import torch
        self.torch = torch
        self.args = args
        self.device = args.device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.bf16 = self.device == "cuda" and torch.cuda.is_bf16_supported()
        self.model_id = args.model or (SMOKE_MODEL if args.smoke else MODEL_ID)
        self.revision = args.revision or {MODEL_ID: MODEL_REV, SMOKE_MODEL: SMOKE_REV}.get(
            self.model_id)
        self.budget = TOKENS_PER_MICRO
        from transformers import AutoTokenizer
        self.tok = AutoTokenizer.from_pretrained(self.model_id, revision=self.revision)
        self.pad_id = self.tok.pad_token_id if self.tok.pad_token_id is not None else 0
        self.hardware = {"device": self.device,
                         "gpu": torch.cuda.get_device_name(0) if self.device == "cuda" else None,
                         "dtype": ("bf16 autocast, fp32 master weights" if self.bf16
                                   else "fp32"),
                         "torch": torch.__version__,
                         "transformers": __import__("transformers").__version__}

    # ------------------------------------------------------------------ helpers
    def autocast(self):
        import contextlib
        if self.bf16:
            return self.torch.autocast("cuda", dtype=self.torch.bfloat16)
        return contextlib.nullcontext()

    def encode(self, texts, max_len):
        """Token ids truncated to max_len, and how many texts were longer."""
        full = self.tok(list(texts), truncation=False)["input_ids"]
        n_trunc = sum(len(x) > max_len for x in full)
        ids = self.tok(list(texts), truncation=True, max_length=max_len)["input_ids"]
        return ids, int(n_trunc), int(sum(len(x) for x in ids))

    def tensors(self, seqs):
        torch = self.torch
        L = max(len(s) for s in seqs)
        ids = torch.full((len(seqs), L), self.pad_id, dtype=torch.long)
        att = torch.zeros((len(seqs), L), dtype=torch.long)
        for i, s in enumerate(seqs):
            ids[i, :len(s)] = torch.tensor(s, dtype=torch.long)
            att[i, :len(s)] = 1
        return ids.to(self.device), att.to(self.device)

    @staticmethod
    def micro(idx, lens, budget):
        """Length-sorted micro-batches whose padded size stays under budget tokens."""
        out, cur, L = [], [], 0
        for i in sorted(idx, key=lambda j: lens[j]):
            if cur and max(L, lens[i]) * (len(cur) + 1) > budget:
                out.append(cur)
                cur, L = [], 0
            cur.append(i)
            L = max(L, lens[i])
        if cur:
            out.append(cur)
        return out

    def logp(self, model, seqs):
        """log-softmax over all classes, float64, in input order."""
        torch = self.torch
        lens = [len(s) for s in seqs]
        out = [None] * len(seqs)
        model.eval()
        with torch.no_grad():
            for mb in self.micro(range(len(seqs)), lens, 4 * self.budget):
                ids, att = self.tensors([seqs[i] for i in mb])
                with self.autocast():
                    z = model(input_ids=ids, attention_mask=att).logits
                lp = torch.log_softmax(z.float(), -1).double().cpu().numpy()
                for i, v in zip(mb, lp):
                    out[i] = v
        return np.stack(out)

    def load_model(self, K):
        from transformers import AutoModelForSequenceClassification
        m = AutoModelForSequenceClassification.from_pretrained(
            self.model_id, revision=self.revision, num_labels=K, dtype=self.torch.float32,
            use_safetensors=False, ignore_mismatched_sizes=True)
        return m.to(self.device)

    # ------------------------------------------------------------------ one task
    def fit(self, task, meta, tr, va):
        torch = self.torch
        F = torch.nn.functional
        from transformers import get_linear_schedule_with_warmup
        K = len(meta["classes"])
        served = meta["served_classes"]
        max_len = meta["max_len"]
        tr_ids, tr_trunc, tr_tok = self.encode([r["text"] for r in tr], max_len)
        va_ids, va_trunc, _ = self.encode([r["text"] for r in va], max_len)
        ytr = torch.tensor([r["y"] for r in tr], dtype=torch.long)
        yva = np.array([r["y"] for r in va])
        counts = np.bincount(ytr.numpy(), minlength=K)
        if meta["class_weighted"]:
            w = len(tr) / (K * np.maximum(counts, 1))
        else:
            w = np.ones(K)
        w_t = torch.tensor(w, dtype=torch.float32, device=self.device)
        tr_lens = [len(s) for s in tr_ids]
        ins = np.isin(yva, served)
        col = {c: j for j, c in enumerate(served)}
        y_ins = np.array([col[y] for y in yva[ins]])

        def val_scores(lp):
            P = softmax(lp[ins][:, served])
            acc = float(np.mean(P.argmax(1) == y_ins))
            nll = float(-np.mean(np.log(np.clip(P[np.arange(len(y_ins)), y_ins], 1e-12, None))))
            return acc, nll

        lrs = LRS[:1] if self.args.smoke else LRS
        epochs = 1 if self.args.smoke else EPOCHS
        grid, best, best_state, t0 = [], None, None, time.time()
        n_tok_trained, t_train = 0, 0.0
        model = None
        for lr in lrs:
            torch.manual_seed(C.SEED)
            model = self.load_model(K)
            opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=WEIGHT_DECAY)
            steps = epochs * math.ceil(len(tr) / BATCH)
            sch = get_linear_schedule_with_warmup(opt, int(WARMUP * steps), steps)
            g = torch.Generator().manual_seed(C.SEED)
            for ep in range(1, epochs + 1):
                model.train()
                perm = torch.randperm(len(tr), generator=g).tolist()
                te0 = time.time()
                for a in range(0, len(tr), BATCH):
                    batch = perm[a:a + BATCH]
                    while True:
                        try:
                            opt.zero_grad(set_to_none=True)
                            for mb in self.micro(batch, tr_lens, self.budget):
                                ids, att = self.tensors([tr_ids[i] for i in mb])
                                with self.autocast():
                                    z = model(input_ids=ids, attention_mask=att).logits
                                yb = ytr[mb].to(self.device)
                                ce = F.cross_entropy(z.float(), yb, reduction="none")
                                loss = (ce * w_t[yb]).sum() / len(batch)
                                loss.backward()
                                n_tok_trained += int(ids.numel())
                            break
                        except torch.cuda.OutOfMemoryError:
                            opt.zero_grad(set_to_none=True)
                            z = loss = ce = ids = att = None
                            torch.cuda.empty_cache()
                            if self.budget <= max_len:
                                raise
                            self.budget = max(max_len, self.budget // 2)
                            print(f"  out of memory, micro-batch budget now {self.budget} tokens",
                                  flush=True)
                    torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                    opt.step()
                    sch.step()
                if self.device == "cuda":
                    torch.cuda.synchronize()
                t_train += time.time() - te0
                lp_va = self.logp(model, va_ids)
                acc, nll = val_scores(lp_va)
                grid.append({"lr": lr, "epoch": ep, "val_acc": acc, "val_nll": nll})
                print(f"  {task} lr={lr} ep={ep} val acc {acc:.4f} nll {nll:.4f} "
                      f"({(time.time() - t0) / 60:.1f} min)", flush=True)
                if best is None or (acc, -nll) > (best["val_acc"], -best["val_nll"]):
                    best = dict(grid[-1])
                    best_state = {k: v.detach().to("cpu", copy=True)
                                  for k, v in model.state_dict().items()}
                    best_lp_va = lp_va
            if lr != lrs[-1]:
                del model, opt, sch
                model = None
                if self.device == "cuda":
                    torch.cuda.empty_cache()
        model.load_state_dict(best_state)
        P_va = [p for p in softmax(best_lp_va[ins][:, served])]
        T = M.fit_T(P_va, list(y_ins))
        stats = {"grid": grid, "selected": best, "T": T,
                 "train_minutes": (time.time() - t0) / 60,
                 "train_tokens_per_s": n_tok_trained / max(t_train, 1e-9),
                 "rows": {"train": len(tr), "val": len(va), "val_used": int(ins.sum())},
                 "truncated": {"train": tr_trunc, "val": va_trunc}, "max_len": max_len,
                 "class_weights": [float(x) for x in w] if meta["class_weighted"] else None,
                 "train_class_counts": [int(x) for x in counts],
                 "train_tokens_unpadded": tr_tok}
        return model, stats

    def latency(self, model, texts, max_len, n=100):
        """Median batch-1 seconds, text to probabilities."""
        torch = self.torch
        model.eval()

        def one(t):
            b = self.tok([t], truncation=True, max_length=max_len, return_tensors="pt")
            b = {k: v.to(self.device) for k, v in b.items() if k in ("input_ids", "attention_mask")}
            with torch.no_grad(), self.autocast():
                z = model(**b).logits
            p = torch.softmax(z.float(), -1).cpu().numpy()
            if self.device == "cuda":
                torch.cuda.synchronize()
            return p
        for t in texts[:3]:
            one(t)
        ts = []
        for t in texts[:n]:
            a = time.perf_counter()
            one(t)
            ts.append(time.perf_counter() - a)
        return float(np.median(ts)), len(ts)

    # ------------------------------------------------------------------ answers
    def run_task(self, task, meta, rows, inputs_dir, answers_dir):
        args = self.args
        cond, tag = meta["condition"], meta["tag"]
        recs = [json.loads(l) for l in open(os.path.join(inputs_dir, f"{cond}.jsonl"),
                                            encoding="utf-8") if l.strip()]
        out_dir = os.path.join(answers_dir, tag)
        path = os.path.join(out_dir, f"{cond}__rep1.jsonl")
        want = [r["key"] for r in recs]
        tr = [r for r in rows if r["split"] == "train"]
        va = [r for r in rows if r["split"] == "val"]
        te = {r["key"]: r for r in rows if r["split"] == "test"}
        assert set(te) == set(want), f"{task}: frozen test keys differ from {cond}.jsonl"
        if args.smoke:
            rng = np.random.default_rng(C.SEED)
            longest = sorted(range(len(tr)), key=lambda i: -len(tr[i]["text"]))[:4]
            rest = [i for i in rng.permutation(len(tr)) if i not in longest]
            tr = [tr[i] for i in longest + rest[:SMOKE_TRAIN - 4]]
            va = [va[i] for i in rng.permutation(len(va))[:SMOKE_VAL]]
            recs = recs[:SMOKE_TEST]
        elif os.path.exists(path):
            done = set()
            for l in open(path, encoding="utf-8"):
                try:
                    j = json.loads(l)
                except json.JSONDecodeError:
                    continue
                if not j.get("error"):
                    done.add(j["key"])
            if done >= set(want):
                print(f"[{tag}] {cond}: complete, skipped", flush=True)
                return
        print(f"[{tag}] {cond}: {len(tr)} train rows, {len(va)} validation rows, "
              f"{len(recs)} test items, {self.model_id}@{(self.revision or '')[:8]}", flush=True)
        t0 = time.time()
        model, stats = self.fit(task, meta, tr, va)
        te_texts = [te[r["key"]]["text"] for r in recs]
        te_ids, te_trunc, _ = self.encode(te_texts, meta["max_len"])
        lp_te = self.logp(model, te_ids)
        lat, n_lat = self.latency(model, te_texts, meta["max_len"])
        stats["truncated"]["test"] = te_trunc
        classes, served, T = meta["classes"], meta["served_classes"], stats["T"]
        lines, acc = [], []
        for r, lp in zip(recs, lp_te):
            ans = {}
            for qid, g in r["gold"].items():
                if meta["option_mapping"] == "native":
                    idx = [classes.index(o) for o in g["native_options"]]
                    p = softmax(lp[idx])
                else:
                    assert len(g["options"]) == len(classes)
                    p = softmax(lp)
                pd = {o: float(v) for o, v in zip(g["options"], p)}
                raw = {"served_temperature": 1.0, "probs_t1": pd, "fitted_temperature": T,
                       "probs_scaled": {o: float(v) for o, v in zip(g["options"],
                                                                     M.apply_T(p, T))}}
                ans[qid] = {"probs": pd, "raw": raw}
                if g.get("label") in g["options"]:
                    acc.append(float(g["options"][int(np.argmax(p))] == g["label"]))
            lines.append(json.dumps({"key": r["key"], "condition": cond, "rep": 1, "model": tag,
                                     "revision": self.revision, "model_returned": self.model_id,
                                     "served_temperature": 1.0, "run_date": RUN_DATE,
                                     "latency_s": lat, "usage_in": None, "answers": ans},
                                    ensure_ascii=False) + "\n")
        os.makedirs(out_dir, exist_ok=True)
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8", newline="\n") as fh:
            fh.writelines(lines)
        os.replace(tmp, path)
        stats.update({"task": task, "condition": cond, "tag": tag, "model_id": self.model_id,
                      "revision": self.revision, "run_date": RUN_DATE, "smoke": bool(args.smoke),
                      "hardware": self.hardware, "latency_s_batch1_p50": lat,
                      "latency_items": n_lat, "tokens_per_micro_batch_final": self.budget,
                      "lrs": list(LRS[:1] if args.smoke else LRS),
                      "epochs": 1 if args.smoke else EPOCHS, "batch": BATCH,
                      "weight_decay": WEIGHT_DECAY, "warmup": WARMUP, "seed": C.SEED,
                      "temperature_rule": "metrics.fit_T on the validation rows of the served "
                                          "classes, selected model",
                      "data": {k: meta.get(k) for k in ("source", "info", "checked_against")},
                      "test_acc_logged_only": float(np.mean(acc)) if acc else None,
                      "test_keys": [r["key"] for r in recs], "classes": classes,
                      "test_logp": [[round(float(x), 6) for x in v] for v in lp_te],
                      "total_minutes": (time.time() - t0) / 60})
        with open(os.path.join(out_dir, f"{cond}__fit.json"), "w", encoding="utf-8") as fh:
            json.dump(stats, fh, indent=1, default=C._jsonable)
        print(f"[{tag}] {cond}: wrote {len(lines)} answers; selected {stats['selected']}, "
              f"T={T:.3f}, latency {lat * 1000:.1f} ms, {stats['total_minutes']:.1f} min, "
              f"{stats['train_tokens_per_s']:.0f} padded training tokens per s", flush=True)
        if args.smoke:
            self.estimate(task, meta, rows, stats)
        del model
        if self.device == "cuda":
            self.torch.cuda.empty_cache()

    def estimate(self, task, meta, rows, stats):
        """Full-grid time from this smoke run's training throughput (padding not counted)."""
        tr = [r["text"] for r in rows if r["split"] == "train"]
        va = [r["text"] for r in rows if r["split"] == "val"]
        _, _, n_tr = self.encode(tr, meta["max_len"])
        _, _, n_va = self.encode(va, meta["max_len"])
        tps = stats["train_tokens_per_s"]
        s = len(LRS) * EPOCHS * (n_tr / tps + n_va / (3 * tps))
        print(f"  estimate for the full {task} grid ({len(LRS)} x {EPOCHS} epochs): about "
              f"{s / 60:.0f} min at {tps:.0f} tokens per s, before padding", flush=True)


class D1Runner(Runner):
    """The D1 cross-encoder: one logit per (state, instructions + option) pair, a softmax over
    each question's options, trained against the teacher distribution (b01's soft labels)."""

    def encode_pairs(self, state, seconds, max_len):
        full = self.tok([state] * len(seconds), list(seconds), truncation=False)["input_ids"]
        n_trunc = sum(len(x) > max_len for x in full)
        ids = self.tok([state] * len(seconds), list(seconds), truncation="only_first",
                       max_length=max_len)["input_ids"]
        return ids, int(n_trunc)

    def items(self, rows, max_len):
        """One item per question: (row index, question, token ids of its option rows)."""
        out, n_trunc = [], 0
        for ri, r in enumerate(rows):
            for q in r["questions"]:
                ids, t = self.encode_pairs(r["text"], q["texts"], max_len)
                n_trunc += t
                out.append((ri, q, ids))
        return out, n_trunc

    def question_logp(self, model, items):
        """log-softmax over each question's options, float64, in item order."""
        torch = self.torch
        seqs, owner = [], []
        for k, (_ri, _q, ids) in enumerate(items):
            for s in ids:
                seqs.append(s)
                owner.append(k)
        z = np.zeros(len(seqs))
        lens = [len(s) for s in seqs]
        model.eval()
        with torch.no_grad():
            for mb in self.micro(range(len(seqs)), lens, 4 * self.budget):
                ids, att = self.tensors([seqs[i] for i in mb])
                with self.autocast():
                    out = model(input_ids=ids, attention_mask=att).logits[:, 0]
                for i, v in zip(mb, out.float().cpu().numpy()):
                    z[i] = v
        res, a = [], 0
        for _ri, _q, ids in items:
            v = z[a:a + len(ids)]
            v = v - v.max()
            res.append(v - np.log(np.exp(v).sum()))
            a += len(ids)
        return res

    @staticmethod
    def d1_micro(batch, items, budget):
        """Questions grouped so each group's padded rows stay under budget (a question is
        never split, so its softmax is taken in one pass)."""
        out, cur, L, n = [], [], 0, 0
        for k in sorted(batch, key=lambda k: max(len(s) for s in items[k][2])):
            lk, nk = max(len(s) for s in items[k][2]), len(items[k][2])
            if cur and max(L, lk) * (n + nk) > budget:
                out.append(cur)
                cur, L, n = [], 0, 0
            cur.append(k)
            L, n = max(L, lk), n + nk
        if cur:
            out.append(cur)
        return out

    def fit_d1(self, meta, tr, va):
        torch = self.torch
        from transformers import get_linear_schedule_with_warmup
        max_len = meta["max_len"]
        tr_items, tr_trunc = self.items(tr, max_len)
        va_items, va_trunc = self.items(va, max_len)
        floor = max(len(ids) for _r, _q, ids in tr_items) * max_len

        def val_scores(lps):
            ce = float(np.mean([-np.dot(q["soft"], lp) for (_r, q, _i), lp in zip(va_items, lps)]))
            acc = float(np.mean([int(np.argmax(lp)) == q["label"]
                                 for (_r, q, _i), lp in zip(va_items, lps)]))
            return ce, acc

        lrs = LRS[:1] if self.args.smoke else LRS
        epochs = 1 if self.args.smoke else EPOCHS
        grid, best, best_state, t0 = [], None, None, time.time()
        n_tok, t_train, model = 0, 0.0, None
        for lr in lrs:
            torch.manual_seed(C.SEED)
            model = self.load_model(1)
            opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=WEIGHT_DECAY)
            steps = epochs * math.ceil(len(tr_items) / D1_BATCH_Q)
            sch = get_linear_schedule_with_warmup(opt, int(WARMUP * steps), steps)
            g = torch.Generator().manual_seed(C.SEED)
            for ep in range(1, epochs + 1):
                model.train()
                perm = torch.randperm(len(tr_items), generator=g).tolist()
                te0 = time.time()
                for a in range(0, len(tr_items), D1_BATCH_Q):
                    batch = perm[a:a + D1_BATCH_Q]
                    while True:
                        try:
                            opt.zero_grad(set_to_none=True)
                            for mb in self.d1_micro(batch, tr_items, max(self.budget, floor)):
                                seqs = [s for k in mb for s in tr_items[k][2]]
                                ids, att = self.tensors(seqs)
                                with self.autocast():
                                    z = model(input_ids=ids, attention_mask=att).logits[:, 0]
                                z = z.float()
                                loss, p = 0.0, 0
                                for k in mb:
                                    nk = len(tr_items[k][2])
                                    t = torch.tensor(tr_items[k][1]["soft"], device=self.device)
                                    loss = loss - (t * torch.log_softmax(z[p:p + nk], -1)).sum()
                                    p += nk
                                (loss / len(batch)).backward()
                                n_tok += int(ids.numel())
                            break
                        except torch.cuda.OutOfMemoryError:
                            opt.zero_grad(set_to_none=True)
                            z = loss = ids = att = None
                            torch.cuda.empty_cache()
                            if self.budget <= floor:
                                raise
                            self.budget = max(floor, self.budget // 2)
                            print(f"  out of memory, micro-batch budget now {self.budget} tokens",
                                  flush=True)
                    torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                    opt.step()
                    sch.step()
                if self.device == "cuda":
                    torch.cuda.synchronize()
                t_train += time.time() - te0
                lps = self.question_logp(model, va_items)
                ce, acc = val_scores(lps)
                grid.append({"lr": lr, "epoch": ep, "val_soft_ce": ce, "val_acc": acc})
                print(f"  d1 lr={lr} ep={ep} val soft CE {ce:.4f} acc {acc:.4f} "
                      f"({(time.time() - t0) / 60:.1f} min)", flush=True)
                # b01's D1 rule selects by soft cross-entropy against the teacher
                if best is None or (ce, -acc) < (best["val_soft_ce"], -best["val_acc"]):
                    best = dict(grid[-1])
                    best_state = {k: v.detach().to("cpu", copy=True)
                                  for k, v in model.state_dict().items()}
                    best_lps = lps
            if lr != lrs[-1]:
                del model, opt, sch
                model = None
                if self.device == "cuda":
                    torch.cuda.empty_cache()
        model.load_state_dict(best_state)
        T = {}
        for t in ("choice", "noul", "score"):
            sel = [(np.exp(lp), q["label"]) for (_r, q, _i), lp in zip(va_items, best_lps)
                   if q["type"] == t]
            T[t] = M.fit_T([p for p, _y in sel], [y for _p, y in sel]) if sel else 1.0
        stats = {"grid": grid, "selected": best, "T": T,
                 "train_minutes": (time.time() - t0) / 60,
                 "train_tokens_per_s": n_tok / max(t_train, 1e-9),
                 "rows": {"train_states": len(tr), "val_states": len(va),
                          "train_questions": len(tr_items), "val_questions": len(va_items),
                          "train_pairs": sum(len(i) for _r, _q, i in tr_items)},
                 "truncated_pairs": {"train": tr_trunc, "val": va_trunc}, "max_len": max_len,
                 "train_tokens_unpadded": sum(len(s) for _r, _q, i in tr_items for s in i)}
        return model, stats

    def run_d1(self, meta, rows, inputs_dir, answers_dir):
        args = self.args
        tag = meta["tag"]
        out_dir = os.path.join(answers_dir, tag)
        recs = {c: [json.loads(l) for l in open(os.path.join(inputs_dir, f"{c}.jsonl"),
                                                encoding="utf-8") if l.strip()]
                for c in D1_CONDS}
        tr = [r for r in rows if r["split"] == "train"]
        va = [r for r in rows if r["split"] == "val"]
        te = {(r["cond"], r["key"]): r for r in rows if r["split"] == "test"}
        for c in D1_CONDS:
            assert {k for cc, k in te if cc == c} == {r["key"] for r in recs[c]}, c
        if args.smoke:
            rng = np.random.default_rng(C.SEED)
            tr = [tr[i] for i in rng.permutation(len(tr))[:D1_SMOKE_TRAIN]]
            va = [va[i] for i in rng.permutation(len(va))[:D1_SMOKE_VAL]]
            recs = {c: v[:SMOKE_TEST] for c, v in recs.items()}
        else:
            complete = True
            for c in D1_CONDS:
                path = os.path.join(out_dir, f"{c}__rep1.jsonl")
                done = set()
                if os.path.exists(path):
                    for l in open(path, encoding="utf-8"):
                        try:
                            j = json.loads(l)
                        except json.JSONDecodeError:
                            continue
                        if not j.get("error"):
                            done.add(j["key"])
                complete &= done >= {r["key"] for r in recs[c]}
            if complete:
                print(f"[{tag}] {D1_CONDS}: complete, skipped", flush=True)
                return
        print(f"[{tag}] {D1_CONDS}: {len(tr)} train states, {len(va)} validation states, "
              f"{self.model_id}@{(self.revision or '')[:8]}", flush=True)
        t0 = time.time()
        model, stats = self.fit_d1(meta, tr, va)
        # batch-1 latency per state (all option rows of its questions in one pass), as b01
        # times bge-small-lr-d1 per state
        lat_rows = [te[("d1_neutral", r["key"])] for r in recs["d1_neutral"]][:100]
        torch = self.torch
        ts = []
        for k, r in enumerate(lat_rows):
            a = time.perf_counter()
            items, _ = self.items([r], meta["max_len"])
            self.question_logp(model, items)
            if self.device == "cuda":
                torch.cuda.synchronize()
            if k >= 3 or len(lat_rows) <= 3:
                ts.append(time.perf_counter() - a)
        lat = float(np.median(ts))
        T = stats["T"]
        os.makedirs(out_dir, exist_ok=True)
        for c in D1_CONDS:
            trows = [te[(c, r["key"])] for r in recs[c]]
            items, n_trunc = self.items(trows, meta["max_len"])
            lps = self.question_logp(model, items)
            by = {}
            for (ri, q, _ids), lp in zip(items, lps):
                by[(ri, q["qid"])] = (q, lp)
            lines = []
            for ri, r in enumerate(recs[c]):
                ans = {}
                for qid, g in r["gold"].items():
                    q, lp = by[(ri, qid)]
                    assert q["options"] == g["options"]
                    p = np.exp(lp)
                    pd = {o: float(v) for o, v in zip(g["options"], p)}
                    Tq = T.get(g["type"], 1.0)
                    ans[qid] = {"probs": pd, "raw": {
                        "served_temperature": 1.0, "probs_t1": pd, "fitted_temperature": Tq,
                        "probs_scaled": {o: float(v) for o, v in zip(g["options"],
                                                                     M.apply_T(p, Tq))}}}
                lines.append(json.dumps({"key": r["key"], "condition": c, "rep": 1, "model": tag,
                                         "revision": self.revision,
                                         "model_returned": self.model_id,
                                         "served_temperature": 1.0, "run_date": RUN_DATE,
                                         "latency_s": lat, "usage_in": None, "answers": ans},
                                        ensure_ascii=False) + "\n")
            path = os.path.join(out_dir, f"{c}__rep1.jsonl")
            with open(path + ".tmp", "w", encoding="utf-8", newline="\n") as fh:
                fh.writelines(lines)
            os.replace(path + ".tmp", path)
            st = dict(stats)
            st.update({"condition": c, "tag": tag, "model_id": self.model_id,
                       "revision": self.revision, "run_date": RUN_DATE,
                       "smoke": bool(args.smoke), "hardware": self.hardware,
                       "latency_s_batch1_p50": lat, "latency_unit": "state (all its questions)",
                       "latency_items": len(ts), "truncated_pairs_test": n_trunc,
                       "tokens_per_micro_batch_final": self.budget,
                       "lrs": list(LRS[:1] if args.smoke else LRS),
                       "epochs": 1 if args.smoke else EPOCHS, "batch_questions": D1_BATCH_Q,
                       "weight_decay": WEIGHT_DECAY, "warmup": WARMUP, "seed": C.SEED,
                       "selection_rule": "validation soft cross-entropy against the teacher "
                                         "(b01's D1 rule), ties by accuracy",
                       "temperature_rule": "metrics.fit_T per question type on the validation "
                                           "states, selected model (b01 fits per type on "
                                           "d1_calib)",
                       "data": {k: meta.get(k) for k in ("source", "info", "input")},
                       "test_keys": [r["key"] for r in recs[c]],
                       "test_logp": [[round(float(x), 6) for x in lp] for lp in lps],
                       "total_minutes": (time.time() - t0) / 60})
            with open(os.path.join(out_dir, f"{c}__fit.json"), "w", encoding="utf-8") as fh:
                json.dump(st, fh, indent=1, default=C._jsonable)
            print(f"[{tag}] {c}: wrote {len(lines)} answers", flush=True)
        print(f"[{tag}] selected {stats['selected']}, T={T}, latency {lat * 1000:.1f} ms per "
              f"state, {(time.time() - t0) / 60:.1f} min, {stats['train_tokens_per_s']:.0f} "
              f"padded training tokens per s", flush=True)
        if args.smoke:
            full_tr = [r for r in rows if r["split"] == "train"]
            tok = 0
            for r in full_tr:
                for q in r["questions"]:
                    ids, _ = self.encode_pairs(r["text"], q["texts"], meta["max_len"])
                    tok += sum(len(s) for s in ids)
            tps = stats["train_tokens_per_s"]
            s = len(LRS) * EPOCHS * tok / tps * 1.15
            print(f"  estimate for the full d1 grid ({len(LRS)} x {EPOCHS} epochs, "
                  f"{tok / 1e6:.2f} M training tokens per epoch): about {s / 60:.0f} min at "
                  f"{tps:.0f} tokens per s", flush=True)
        del model
        if self.device == "cuda":
            self.torch.cuda.empty_cache()


def cmd_run(args):
    data = args.data or os.environ.get("P4_B05_DATA") or os.path.join(C.DATA, "b05")
    inputs = args.inputs or os.environ.get("P4_INPUTS") or C.INPUTS
    answers = args.answers or os.environ.get("P4_ANSWERS") or C.ANSWERS
    if args.smoke and os.path.abspath(answers) == os.path.abspath(C.ANSWERS):
        sys.exit("--smoke needs --answers (or P4_ANSWERS) outside shared/answers")
    groups = [g for g in args.groups.split(",") if g]
    unknown = [g for g in groups if g not in GROUPS]
    if unknown:
        sys.exit(f"unknown groups {unknown}; choose from {GROUPS}")
    meta_all = json.load(open(os.path.join(data, "b05_meta.json"), encoding="utf-8"))
    runner = D1Runner(args)
    print(f"model {runner.model_id}@{runner.revision}, device {runner.device}, "
          f"{runner.hardware['dtype']}", flush=True)
    failed = []
    for g in groups:
        for task in (D3_TASKS_RUN if g == "d3" else [t for t, v in TASKS.items() if v[0] == g]):
            rows = [json.loads(l) for l in open(os.path.join(data, f"{task}.jsonl"),
                                                encoding="utf-8")]
            try:
                if task == "d1":
                    runner.run_d1(meta_all[task], rows, inputs, answers)
                else:
                    runner.run_task(task, meta_all[task], rows, inputs, answers)
            except Exception as e:     # one task failing never stops the others
                import traceback
                traceback.print_exc()
                failed.append(f"{task}: {type(e).__name__}: {e}")
    if failed:
        print("failed tasks:", failed, flush=True)
        sys.exit(1)


# D3 tasks in the order of a run, cheapest first (short texts, then the long conversations)
D3_TASKS_RUN = ["emotion", "wiki_politeness", "conv_go_awry", "wiki_corpus"]


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    f = sub.add_parser("freeze")
    f.add_argument("--out", required=True)
    r = sub.add_parser("run")
    r.add_argument("--groups", default=",".join(GROUPS))
    r.add_argument("--data")
    r.add_argument("--inputs")
    r.add_argument("--answers")
    r.add_argument("--smoke", action="store_true")
    r.add_argument("--model")
    r.add_argument("--revision")
    r.add_argument("--device")
    a = ap.parse_args()
    if a.cmd == "freeze":
        cmd_freeze(a.out)
    else:
        cmd_run(a)


if __name__ == "__main__":
    main()
