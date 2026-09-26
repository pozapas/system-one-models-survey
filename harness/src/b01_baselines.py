"""Conventional classifier baselines on exactly the frozen benchmark items.

Four baselines, each written as answer files in the harness format so bench.py and a01 read
them like any model (answers/baseline-<tag>/<cond>__rep1.jsonl), and summarized in
results/baselines.json.

bert-base-clinc      bert-base-uncased fine-tuned (fp32, local GPU) on the CLINC-150 train split
                     of data_oos_plus at commit 828f8093 (15,000 in-scope + 250 out-of-scope
                     rows, the rows decider-2b trains on), 151-way head; learning rate and epoch
                     count selected on the CLINC validation split. The harness never offers the
                     out-of-scope class, so the served distribution is the softmax over the
                     offered intents (the out-of-scope logit is dropped).
bge-small-lr-clinc   BAAI/bge-small-en-v1.5 sentence embeddings (CLS pooling, L2-normalized, as
                     its model card specifies) + multinomial logistic regression on the same rows,
                     C selected on the validation split.
bge-small-lr-d1      D1: one logistic regression per workflow x question on bge-small embeddings
                     of the JSON state concatenated with TF-IDF word uni- and bigrams, fitted to
                     the teacher's soft labels (each state enters once per option, weighted by the
                     teacher probability) on the 900 training-split states outside d1_calib; C by
                     5-fold cross-validation on those states.
nli-deberta-v3-base  zero-shot entailment, MoritzLaurer/deberta-v3-base-zeroshot-v2.0, no task
                     training. Premise = the state text the harness sends (JSON for D1) followed
                     by a newline and the question's instructions; hypothesis = the option's
                     rubric, with a leading "True:" / "False:" removed, used verbatim when it has
                     five or more words or ends in a period, else inserted into the model's
                     default template "This text is about {}."; a noul question without rubrics
                     uses the instructions (true) and "It is not the case that <instructions>"
                     (false). Each option gets its entailment log-odds (entailment minus
                     not_entailment logit); the softmax over the offered options is the answer.
                     Premises are truncated to fit 512 tokens (only_first) and counted.

Calibration. Shipped probabilities are the T = 1 outputs (written as "probs" and raw.probs_t1).
ece_scaled uses one temperature fitted with metrics.fit_T (NLL, same grid) on data disjoint from
the test items: the CLINC validation split for D2 (in-scope rows, 150-way distribution; for the
entailment model 600 validation rows, four per intent), d1_calib per question type for D1 (the
same slice and rule a01 uses for every model), and five-fold cross-fitting by item for D3,
where no validation split exists (the a01 rule). ece_scaled_crossfit applies the a01 rule to
every condition, for comparison with the paper's tables.

Exposure. Training and validation texts whose normalized form (lower case, punctuation
removed, whitespace collapsed) equals one of our 800 D2 test texts are removed before training;
the counts are recorded. D1 training states exclude d1_calib and every d1_neutral state.

Stages (default all): d2bge, d2bert (the two CLINC models), d1, nli, latency, eval.
    python b01_baselines.py [stage ...]
Intermediate arrays and checkpoints go to D:/p4env/b01cache, outside the synced folder.
"""
import json
import os
import sys
import time

import numpy as np

import common as C

os.environ.setdefault("HF_HOME", "D:/p4env/hf")
import bench                      # noqa: E402
import metrics as M               # noqa: E402

CACHE = "D:/p4env/b01cache"
CLINC_FILE = "D:/p4env/cache/clinc_828f8093/data_oos_plus.json"
CLINC_COMMIT = "828f8093932c8fe6ca7936c3d2e52903b1c523de"
D1_REPO, D1_REV = "LocalLLaMA/typed-decisions", "c76749ec58bd8c3d2ea706b31c333a9059c38f90"
BERT = "bert-base-uncased"
BGE = "BAAI/bge-small-en-v1.5"
NLI = "MoritzLaurer/deberta-v3-base-zeroshot-v2.0"
D2_CONDS = ["d2_k150", "d2_k50", "d2_k20", "d2_k5"]
D3_CONDS = ["d3_conv_go_awry", "d3_wiki_corpus", "d3_emotion", "d3_wiki_politeness"]
D1_CONDS = ["d1_neutral", "d1_native", "d1_calib"]
TAGS = {"bert-base-clinc": "baseline-bert-base-clinc",
        "bge-small-lr-clinc": "baseline-bge-small-lr-clinc",
        "bge-small-lr-d1": "baseline-bge-small-lr-d1",
        "nli-deberta-v3-base": "baseline-nli-deberta-v3-base"}
RUN_DATE = time.strftime("%Y-%m-%d")


def dev():
    import torch
    return "cuda" if torch.cuda.is_available() else "cpu"


def cpath(name):
    os.makedirs(CACHE, exist_ok=True)
    return os.path.join(CACHE, name)


def hub_rev(repo):
    from huggingface_hub import HfApi
    try:
        return HfApi().model_info(repo).sha
    except Exception:
        return None


def softmax(z, axis=-1):
    z = z - z.max(axis, keepdims=True)
    e = np.exp(z)
    return e / e.sum(axis, keepdims=True)


# ------------------------------------------------------------------ CLINC data

def clinc():
    from b02_clinc_overlap import norm, fetch_variant
    if not os.path.exists(CLINC_FILE):
        fetch_variant("data_oos_plus")
    d = json.load(open(CLINC_FILE, encoding="utf-8"))
    domains = json.load(open(os.path.join(C.DATA, "d2", "domains.json"), encoding="utf-8"))
    intents = sorted(i for ints in domains.values() for i in ints)
    assert len(intents) == 150
    cls = {n: i for i, n in enumerate(intents)}
    cls["oos"] = 150
    test_rows = bench.inputs("d2_k150")
    test_norm = {norm(r["state"]) for r in test_rows}

    def part(names):
        X, y, dropped = [], [], []
        for nm in names:
            for t, lab in d[nm]:
                if norm(t) in test_norm:
                    dropped.append(t)
                    continue
                X.append(t)
                y.append(cls[lab])
        return X, np.array(y), dropped

    tr = part(["train", "oos_train"])
    va = part(["val", "oos_val"])
    exact = sum(t in {r["state"] for r in test_rows} for t in tr[0] + va[0])
    normed = sum(norm(t) in test_norm for t in tr[0] + va[0])
    assert exact == 0 and normed == 0
    info = {"train_rows": len(tr[0]), "val_rows": len(va[0]),
            "train_dropped_normalized_match_to_test": len(tr[2]),
            "val_dropped_normalized_match_to_test": len(va[2]),
            "dropped_texts": tr[2] + va[2],
            "overlap_after_filter": {"exact": exact, "normalized": normed}}
    return tr[0], tr[1], va[0], va[1], intents, cls, info


def d2_option_probs(logp151, rows, cls):
    """Per input row: distribution over its offered options from class log-probabilities
    (softmax restricted to those classes, which drops the out-of-scope class)."""
    out = []
    for r, lp in zip(rows, logp151):
        idx = [cls[o] for o in r["gold"]["intent"]["native_options"]]
        out.append(softmax(lp[idx]))
    return out


def val_T_150(logp_val, y_val):
    """One temperature on the in-scope validation rows, 150-way distribution."""
    m = y_val < 150
    P = [softmax(lp[:150]) for lp in logp_val[m]]
    return M.fit_T(P, list(y_val[m]))


# ------------------------------------------------------------------ encoders

def embed(texts, model_id=BGE, bs=128, max_len=512, device=None):
    """CLS-pooled, L2-normalized embeddings (fp32). Returns (E, n_truncated)."""
    import torch
    from transformers import AutoModel, AutoTokenizer
    device = device or dev()
    tok = AutoTokenizer.from_pretrained(model_id)
    mdl = AutoModel.from_pretrained(model_id).to(device).eval()
    n_trunc = sum(len(tok(t)["input_ids"]) > max_len for t in texts)
    order = np.argsort([len(t) for t in texts])
    E = np.zeros((len(texts), mdl.config.hidden_size), dtype=np.float32)
    with torch.no_grad():
        for a in range(0, len(texts), bs):
            idx = order[a:a + bs]
            b = tok([texts[i] for i in idx], padding=True, truncation=True, max_length=max_len,
                    return_tensors="pt").to(device)
            h = mdl(**b).last_hidden_state[:, 0].float()
            h = torch.nn.functional.normalize(h, dim=-1)
            E[idx] = h.cpu().numpy()
    return E, int(n_trunc)


def fit_lr_select(Xtr, ytr, Xva, yva, grid=(1.0, 10.0, 100.0, 1000.0, 10000.0)):
    from sklearn.linear_model import LogisticRegression
    best = None
    for c in grid:
        m = LogisticRegression(C=c, max_iter=3000)
        m.fit(Xtr, ytr)
        lp = np.log(np.clip(m.predict_proba(Xva), 1e-12, None))
        ins = yva < 150
        P = softmax(lp[ins][:, :150])
        acc = float(np.mean(P.argmax(1) == yva[ins]))
        nll = float(-np.mean(np.log(np.clip(P[np.arange(ins.sum()), yva[ins]], 1e-12, None))))
        print(f"  LR C={c}: val acc {acc:.4f} nll {nll:.4f}", flush=True)
        if best is None or (acc, -nll) > (best[1], -best[2]):
            best = (c, acc, nll, m)
    return best


# ------------------------------------------------------------------ stage d2

def stage_d2bge():
    Xtr, ytr, Xva, yva, intents, cls, info = clinc()
    print("CLINC rows", info["train_rows"], info["val_rows"], "dropped",
          info["train_dropped_normalized_match_to_test"], info["val_dropped_normalized_match_to_test"])
    test_rows = bench.inputs("d2_k150")
    Xte = [r["state"] for r in test_rows]
    # bge + LR
    Etr, _ = embed(Xtr)
    Eva, _ = embed(Xva)
    Ete, _ = embed(Xte)
    c, acc, nll, lr = fit_lr_select(Etr, ytr, Eva, yva)
    lp_va = np.log(np.clip(lr.predict_proba(Eva), 1e-12, None))
    lp_te = np.log(np.clip(lr.predict_proba(Ete), 1e-12, None))
    T = val_T_150(lp_va, yva)
    np.savez(cpath("d2_bge.npz"), lp_te=lp_te, lp_va=lp_va, yva=yva)
    import pickle
    pickle.dump(lr, open(cpath("d2_bge_lr.pkl"), "wb"))
    json.dump({"C": c, "val_acc": acc, "val_nll": nll, "T": T, "data": info},
              open(cpath("d2_bge.json"), "w"), indent=1)
    print("bge-lr C", c, "val acc", acc, "T", T, flush=True)


def stage_d2bert():
    Xtr, ytr, Xva, yva, intents, cls, info = clinc()
    Xte = [r["state"] for r in bench.inputs("d2_k150")]
    res = finetune_bert(Xtr, ytr, Xva, yva, Xte)
    T = val_T_150(res["lp_va"], yva)
    np.savez(cpath("d2_bert.npz"), lp_te=res["lp_te"], lp_va=res["lp_va"], yva=yva)
    json.dump({"selected": res["selected"], "grid": res["grid"], "T": T, "data": info,
               "train_minutes": res["minutes"]}, open(cpath("d2_bert.json"), "w"), indent=1)
    print("bert selected", res["selected"], "T", T, flush=True)


def finetune_bert(Xtr, ytr, Xva, yva, Xte, lrs=(3e-5, 5e-5), epochs=4, bs=32, max_len=64):
    import torch
    from transformers import (AutoModelForSequenceClassification, AutoTokenizer,
                              get_linear_schedule_with_warmup)
    device = dev()
    tok = AutoTokenizer.from_pretrained(BERT)

    # dynamic padding: CLINC queries average 10 word pieces, so padding each batch to its
    # longest member is several times faster than a fixed length
    def enc(texts):
        return tok(texts, padding=True, truncation=True, max_length=max_len, return_tensors="pt")

    ytr_t = torch.tensor(ytr)

    def logits_of(mdl, texts):
        out = []
        mdl.eval()
        with torch.no_grad():
            for a in range(0, len(texts), 256):
                b = enc(texts[a:a + 256]).to(device)
                out.append(mdl(**b).logits.float().cpu())
        return torch.log_softmax(torch.cat(out), -1).numpy()

    grid, best, t0 = [], None, time.time()
    for lr in lrs:
        torch.manual_seed(C.SEED)
        mdl = AutoModelForSequenceClassification.from_pretrained(BERT, num_labels=151).to(device)
        opt = torch.optim.AdamW(mdl.parameters(), lr=lr, weight_decay=0.01)
        steps = epochs * ((len(Xtr) + bs - 1) // bs)
        sch = get_linear_schedule_with_warmup(opt, int(0.1 * steps), steps)
        g = torch.Generator().manual_seed(C.SEED)
        for ep in range(1, epochs + 1):
            mdl.train()
            perm = torch.randperm(len(Xtr), generator=g)
            for a in range(0, len(Xtr), bs):
                idx = perm[a:a + bs]
                b = enc([Xtr[i] for i in idx.tolist()]).to(device)
                loss = torch.nn.functional.cross_entropy(mdl(**b).logits, ytr_t[idx].to(device))
                opt.zero_grad(set_to_none=True)
                loss.backward()
                torch.nn.utils.clip_grad_norm_(mdl.parameters(), 1.0)
                opt.step()
                sch.step()
            lp = logits_of(mdl, Xva)
            ins = yva < 150
            P = softmax(lp[ins][:, :150])
            acc = float(np.mean(P.argmax(1) == yva[ins]))
            nll = float(-np.mean(np.log(np.clip(P[np.arange(ins.sum()), yva[ins]], 1e-12, None))))
            grid.append({"lr": lr, "epoch": ep, "val_acc": acc, "val_nll": nll})
            print(f"  bert lr={lr} ep={ep} val acc {acc:.4f} nll {nll:.4f} "
                  f"({(time.time() - t0) / 60:.1f} min)", flush=True)
            if best is None or (acc, -nll) > (best["val_acc"], -best["val_nll"]):
                best = dict(grid[-1])
                torch.save(mdl.state_dict(), cpath("bert_best.pt"))
        del mdl, opt
        torch.cuda.empty_cache()
    mdl = AutoModelForSequenceClassification.from_pretrained(BERT, num_labels=151).to(device)
    mdl.load_state_dict(torch.load(cpath("bert_best.pt")))
    return {"lp_va": logits_of(mdl, Xva), "lp_te": logits_of(mdl, Xte), "grid": grid,
            "selected": best, "minutes": (time.time() - t0) / 60}


# ------------------------------------------------------------------ stage d1

def d1_train_states():
    from datasets import load_dataset
    ds = load_dataset(D1_REPO, "all", split="train", revision=D1_REV)
    out = []
    for r in ds:
        qs, gold = json.loads(r["questions"]), json.loads(r["gold"])
        lab = {}
        for qid, q in qs.items():
            g = gold[qid]
            if q["type"] == "choice":
                names = list(q["criteria"].keys())
            elif q["type"] == "noul":
                names = ["false", "true"]
            else:
                names = [str(i) for i in range(len(q["criteria"]))]
            lab[qid] = np.array([g["probabilities"][n] for n in names], dtype=float)
        out.append({"id": r["id"], "workflow": r["workflow"], "state": json.loads(r["state"]),
                    "soft": lab})
    return out


def state_text(s):
    return s if isinstance(s, str) else json.dumps(s, ensure_ascii=False)


def soft_lr(X, Y, c):
    """Multinomial logistic regression on soft labels by row expansion with weights."""
    from sklearn.linear_model import LogisticRegression
    import scipy.sparse as sp
    n, K = Y.shape
    rows, ys, ws = [], [], []
    for k in range(K):
        keep = np.where(Y[:, k] > 1e-6)[0]
        rows.append(keep)
        ys.append(np.full(len(keep), k))
        ws.append(Y[keep, k])
    idx = np.concatenate(rows)
    m = LogisticRegression(C=c, max_iter=5000)
    m.fit(X[idx] if not sp.issparse(X) else X[idx], np.concatenate(ys),
          sample_weight=np.concatenate(ws))
    return m


def lr_proba(m, X, K):
    P = np.full((X.shape[0], K), 1e-4)
    P[:, m.classes_] += m.predict_proba(X)
    return P / P.sum(1, keepdims=True)


def stage_d1():
    import scipy.sparse as sp
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.model_selection import KFold
    train = d1_train_states()
    calib = {r["item_id"] for r in bench.inputs("d1_calib")}
    test = {r["item_id"] for r in bench.inputs("d1_neutral")}
    pool = [r for r in train if r["id"] not in calib and r["id"] not in test]
    assert not ({r["id"] for r in train} & test)
    eval_rows = {c: bench.inputs(c) for c in D1_CONDS}
    eval_states = {}
    for c in D1_CONDS:
        for r in eval_rows[c]:
            eval_states[r["item_id"]] = (r["meta"]["workflow"], state_text(r["state"]))
    texts_pool = [state_text(r["state"]) for r in pool]
    ev_ids = sorted(eval_states)
    texts_ev = [eval_states[i][1] for i in ev_ids]
    E_pool, tr_pool = embed(texts_pool)
    E_ev, tr_ev = embed(texts_ev)
    tf = TfidfVectorizer(ngram_range=(1, 2), token_pattern=r"[A-Za-z_]+|\d+(?:\.\d+)?",
                         sublinear_tf=True, min_df=2, max_features=20000)
    tf.fit(texts_pool)
    X_pool = sp.hstack([sp.csr_matrix(E_pool), tf.transform(texts_pool)]).tocsr()
    X_ev = sp.hstack([sp.csr_matrix(E_ev), tf.transform(texts_ev)]).tocsr()
    ev_pos = {i: k for k, i in enumerate(ev_ids)}
    preds, chosen, models = {}, {}, {}
    grid = (0.3, 1.0, 3.0, 10.0, 30.0, 100.0, 300.0, 1000.0, 3000.0, 10000.0)
    for wf in sorted({r["workflow"] for r in pool}):
        ix = [k for k, r in enumerate(pool) if r["workflow"] == wf]
        for qid in pool[ix[0]]["soft"]:
            Y = np.stack([pool[k]["soft"][qid] for k in ix])
            Y = Y / Y.sum(1, keepdims=True)
            X = X_pool[ix]
            K = Y.shape[1]
            cv = {}
            for c in grid:
                loss = []
                for a, b in KFold(5, shuffle=True, random_state=C.SEED).split(ix):
                    m = soft_lr(X[a], Y[a], c)
                    P = lr_proba(m, X[b], K)
                    loss.append(-np.mean(np.sum(Y[b] * np.log(P), 1)))
                cv[c] = float(np.mean(loss))
            c = min(cv, key=cv.get)
            m = soft_lr(X, Y, c)
            models[(wf, qid)] = (m, K)
            ids = [i for i in ev_ids if eval_states[i][0] == wf]
            P = lr_proba(m, X_ev[[ev_pos[i] for i in ids]], K)
            for i, p in zip(ids, P):
                preds[(i, qid)] = p
            chosen[f"{wf}|{qid}"] = {"C": c, "cv_soft_ce": cv, "n_train_states": len(ix)}
            print(f"  {wf} {qid} C={c} cv {cv[c]:.3f}", flush=True)
    import pickle
    pickle.dump({"preds": preds, "chosen": chosen, "n_pool": len(pool), "models": models, "tfidf": tf,
                 "truncated_train": tr_pool, "truncated_eval": tr_ev},
                open(cpath("d1_bge.pkl"), "wb"))


# ------------------------------------------------------------------ stage nli

def hypothesis(q, opt_index, opt_key):
    import re
    crit = q.get("criteria")
    if q["type"] == "noul" and not crit:
        ins = q["instructions"].strip()
        if opt_key == "true":
            return ins
        return "It is not the case that " + ins[0].lower() + ins[1:]
    if isinstance(crit, dict):
        rub = crit.get(opt_key)
    elif isinstance(crit, list):
        rub = crit[opt_index]
    else:
        rub = None
    if rub is None:
        rub = opt_key.replace("_", " ")
    if not isinstance(rub, str):
        rub = json.dumps(rub, ensure_ascii=False)
    rub = re.sub(r"^(True|False):\s*", "", rub.strip())
    if len(rub.split()) >= 5 or rub.endswith("."):
        return rub[0].upper() + rub[1:]
    return f"This text is about {rub}."


def nli_pairs(cond):
    """(key, qid, options, [(premise, hypothesis)]) per decision of a condition."""
    out = []
    for r in bench.inputs(cond):
        st = state_text(r["state"])
        for qid, g in r["gold"].items():
            q = r["questions"][qid]
            prem = f"{st}\n{q['instructions']}"
            hyps = [hypothesis(q, i, o) for i, o in enumerate(g["options"])]
            out.append((r["key"], qid, g["options"], [(prem, h) for h in hyps]))
    return out


class NLIScorer:
    def __init__(self, device=None, fp16=False):
        import torch
        from transformers import AutoModelForSequenceClassification, AutoTokenizer
        self.device = device or dev()
        self.tok = AutoTokenizer.from_pretrained(NLI)
        self.mdl = AutoModelForSequenceClassification.from_pretrained(NLI).to(self.device).eval()
        if self.device == "cuda" and fp16:
            self.mdl = self.mdl.half()
        lab = {v.lower(): k for k, v in self.mdl.config.id2label.items()}
        self.ie, self.ine = lab["entailment"], lab["not_entailment"]
        self.cache = {}
        self.truncated = set()

    def _run(self, pairs):
        import torch
        b = self.tok([p for p, _ in pairs], [h for _, h in pairs], padding=True,
                     truncation="only_first", max_length=512, return_tensors="pt").to(self.device)
        with torch.no_grad():
            z = self.mdl(**b).logits.float()
        return (z[:, self.ie] - z[:, self.ine]).cpu().numpy()

    def score(self, pairs, bs=128, tokens_per_batch=24000):
        todo = sorted({p for p in pairs if p not in self.cache}, key=lambda x: len(x[0]) + len(x[1]))
        if todo:
            lens = [len(self.tok(p, h)["input_ids"]) for p, h in todo]
            for (p, h), n in zip(todo, lens):
                if n > 512:
                    self.truncated.add(p)
            a = 0
            while a < len(todo):
                width = min(512, lens[min(a + bs, len(todo)) - 1])
                step = max(1, min(bs, tokens_per_batch // max(width, 1)))
                chunk = todo[a:a + step]
                for pr, v in zip(chunk, self._run(chunk)):
                    self.cache[pr] = float(v)
                a += step
        return np.array([self.cache[p] for p in pairs])


def stage_nli():
    import pickle
    sc = NLIScorer()
    out, timing = {}, {}
    conds = ["d2_k150"] + D3_CONDS + ["d1_neutral", "d1_calib", "d1_native"]
    for cond in conds:
        dec = nli_pairs(cond)
        flat = [pr for d in dec for pr in d[3]]
        t0 = time.time()
        s = sc.score(flat)
        timing[cond] = {"seconds": time.time() - t0, "decisions": len(dec), "pairs": len(flat)}
        k = 0
        for key, qid, opts, prs in dec:
            out[(cond, key, qid)] = s[k:k + len(prs)]
            k += len(prs)
        print(f"  nli {cond}: {len(dec)} decisions {len(flat)} pairs "
              f"{timing[cond]['seconds']:.0f}s, truncated premises so far {len(sc.truncated)}",
              flush=True)
    # k-subsets: the same (premise, hypothesis) pairs as d2_k150, so every score is cached
    for cond in ["d2_k50", "d2_k20", "d2_k5"]:
        for key, qid, opts, prs in nli_pairs(cond):
            out[(cond, key, qid)] = sc.score(prs)
    # temperature for D2: 600 in-scope validation rows, four per intent
    Xtr, ytr, Xva, yva, intents, cls, info = clinc()
    rng = np.random.default_rng(C.SEED)
    pick = np.concatenate([rng.choice(np.where(yva == c)[0], 4, replace=False) for c in range(150)])
    q_int = bench.inputs("d2_k150")[0]["questions"]["intent"]
    val_scores = []
    for i in pick:
        prs = [(f"{Xva[i]}\n{q_int['instructions']}", f"This text is about {n.replace('_', ' ')}.")
               for n in intents]
        val_scores.append(sc.score(prs))
    Pv = [softmax(v) for v in val_scores]
    T_val = M.fit_T(Pv, list(yva[pick]))
    trunc = {}
    for cond in conds:
        prem = {p for d in nli_pairs(cond) for p, _ in d[3]}
        trunc[cond] = {"premises": len(prem), "truncated": len(prem & sc.truncated)}
    pickle.dump({"scores": out, "timing": timing, "T_val_d2": T_val,
                 "val_acc_d2": float(np.mean([p.argmax() == y for p, y in zip(Pv, yva[pick])])),
                 "truncation": trunc}, open(cpath("nli.pkl"), "wb"))
    print("nli T_val", T_val, flush=True)


# ------------------------------------------------------------------ answers

def write_answers(tag, cond, probs, latency_s, model_id, revision, T=None):
    """probs: {(key, qid): np.array over that decision's options}."""
    d = os.path.join(C.ANSWERS, TAGS[tag])
    os.makedirs(d, exist_ok=True)
    path = os.path.join(d, f"{cond}__rep1.jsonl")
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        for r in bench.inputs(cond):
            ans = {}
            for qid, g in r["gold"].items():
                p = probs[(r["key"], qid)]
                pd = {o: float(v) for o, v in zip(g["options"], p)}
                raw = {"served_temperature": 1.0, "probs_t1": pd}
                if T is not None:
                    Tq = T.get(g["type"], 1.0) if isinstance(T, dict) else T
                    raw["fitted_temperature"] = Tq
                    raw["probs_scaled"] = {o: float(v) for o, v in
                                           zip(g["options"], M.apply_T(p, Tq))}
                ans[qid] = {"probs": pd, "raw": raw}
            fh.write(json.dumps({"key": r["key"], "condition": cond, "rep": 1,
                                 "model": TAGS[tag], "revision": revision,
                                 "model_returned": model_id, "served_temperature": 1.0,
                                 "run_date": RUN_DATE, "latency_s": latency_s,
                                 "usage_in": None, "answers": ans}, ensure_ascii=False) + "\n")


def build_answers():
    import pickle
    lat = json.load(open(cpath("latency.json"))) if os.path.exists(cpath("latency.json")) else {}

    def l_of(tag, cond):
        v = lat.get(tag, {}).get(cond, {}).get("gpu_batch1_ms_p50")
        return None if v is None else v / 1000
    _, _, _, _, intents, cls, _ = clinc()
    rows150 = bench.inputs("d2_k150")
    by_key = {r["item_id"]: i for i, r in enumerate(rows150)}
    for tag, f, mid in (("bge-small-lr-clinc", "d2_bge", BGE), ("bert-base-clinc", "d2_bert", BERT)):
        if not os.path.exists(cpath(f + ".npz")):
            continue
        z = np.load(cpath(f + ".npz"))
        T = json.load(open(cpath(f + ".json")))["T"]
        for cond in D2_CONDS:
            rows = bench.inputs(cond)
            lp = z["lp_te"][[by_key[r["item_id"]] for r in rows]]
            P = d2_option_probs(lp, rows, cls)
            write_answers(tag, cond, {(r["key"], "intent"): p for r, p in zip(rows, P)},
                          l_of(tag, cond), mid, hub_rev(mid), T)
    if os.path.exists(cpath("d1_bge.pkl")):
        d = pickle.load(open(cpath("d1_bge.pkl"), "rb"))
        for cond in D1_CONDS:
            probs = {(r["key"], q): d["preds"][(r["item_id"], q)]
                     for r in bench.inputs(cond) for q in r["gold"]}
            write_answers("bge-small-lr-d1", cond, probs, l_of("bge-small-lr-d1", cond), BGE,
                          hub_rev(BGE))
    if os.path.exists(cpath("nli.pkl")):
        d = pickle.load(open(cpath("nli.pkl"), "rb"))
        for cond in D2_CONDS + D3_CONDS + D1_CONDS:
            probs = {(k, q): softmax(v) for (c, k, q), v in d["scores"].items() if c == cond}
            write_answers("nli-deberta-v3-base", cond, probs, l_of("nli-deberta-v3-base", cond),
                          NLI, hub_rev(NLI), d["T_val_d2"] if cond.startswith("d2") else None)


# ------------------------------------------------------------------ latency

def _p50(xs):
    return float(np.median(xs)) * 1000


def stage_latency_d1():
    """Re-time only bge-small-lr-d1 and merge into latency.json."""
    keep = json.load(open(cpath("latency.json")))
    import shutil
    shutil.copy(cpath("latency.json"), cpath("latency_full.json"))
    stage_latency(only=("bge-small-lr-d1",))
    new = json.load(open(cpath("latency.json")))
    keep["bge-small-lr-d1"] = new["bge-small-lr-d1"]
    json.dump(keep, open(cpath("latency.json"), "w"), indent=1)


def stage_latency(only=None):
    import pickle
    import torch
    from transformers import AutoModel, AutoModelForSequenceClassification, AutoTokenizer
    res = {}
    torch.set_num_threads(os.cpu_count() or 4)
    d2_texts = [r["state"] for r in bench.inputs("d2_k150")]
    d1_texts = [state_text(r["state"]) for r in bench.inputs("d1_neutral")]

    def time_encoder(fn_batch, texts, n1=200, ncpu=100, bs=64):
        out = {}
        for device in ("cuda", "cpu"):
            fn = fn_batch(device)
            fn(texts[:4])
            if device == "cuda":
                torch.cuda.synchronize()
            ts = []
            for t in texts[:(n1 if device == "cuda" else ncpu)]:
                a = time.perf_counter()
                fn([t])
                if device == "cuda":
                    torch.cuda.synchronize()
                ts.append(time.perf_counter() - a)
            out[f"{'gpu' if device == 'cuda' else 'cpu'}_batch1_ms_p50"] = _p50(ts)
            if device == "cuda":
                per = []
                for a0 in range(0, len(texts) - bs + 1, bs):
                    a = time.perf_counter()
                    fn(texts[a0:a0 + bs])
                    torch.cuda.synchronize()
                    per.append((time.perf_counter() - a) / bs)
                out["gpu_batched_ms_per_item_p50"] = _p50(per)
                out["gpu_batch_size"] = bs
        return out

    # bert-base classifier
    if os.path.exists(cpath("bert_best.pt")) and (only is None or "bert-base-clinc" in only):
        tok = AutoTokenizer.from_pretrained(BERT)
        sd = torch.load(cpath("bert_best.pt"), map_location="cpu")

        def mk_bert(device):
            m = AutoModelForSequenceClassification.from_pretrained(BERT, num_labels=151)
            m.load_state_dict(sd)
            m = m.to(device).eval()

            def f(ts):
                with torch.no_grad():
                    b = tok(ts, padding=True, truncation=True, max_length=64,
                            return_tensors="pt").to(device)
                    return torch.softmax(m(**b).logits.float()[:, :150], -1).cpu().numpy()
            return f
        r = time_encoder(mk_bert, d2_texts)
        res["bert-base-clinc"] = {c: r for c in D2_CONDS}
        print("latency bert", r, flush=True)
    # bge + LR
    btok = AutoTokenizer.from_pretrained(BGE)

    def mk_bge(lr_fn, max_len):
        def mk(device):
            m = AutoModel.from_pretrained(BGE).to(device).eval()

            def f(ts):
                with torch.no_grad():
                    b = btok(ts, padding=True, truncation=True, max_length=max_len,
                             return_tensors="pt").to(device)
                    h = torch.nn.functional.normalize(m(**b).last_hidden_state[:, 0].float(), dim=-1)
                    return lr_fn(h.cpu().numpy(), ts)
            return f
        return mk
    if os.path.exists(cpath("d2_bge_lr.pkl")) and (only is None or "bge-small-lr-clinc" in only):
        lr = pickle.load(open(cpath("d2_bge_lr.pkl"), "rb"))
        r = time_encoder(mk_bge(lambda E, ts: lr.predict_proba(E), 64), d2_texts)
        res["bge-small-lr-clinc"] = {c: r for c in D2_CONDS}
        print("latency bge-lr clinc", r, flush=True)
    if os.path.exists(cpath("d1_bge.pkl")) and (only is None or "bge-small-lr-d1" in only):
        import scipy.sparse as sp
        d1 = pickle.load(open(cpath("d1_bge.pkl"), "rb"))
        wf_of = {state_text(r["state"]): r["meta"]["workflow"] for r in bench.inputs("d1_neutral")}

        def d1_head(E, ts):
            X = sp.hstack([sp.csr_matrix(E), d1["tfidf"].transform(ts)]).tocsr()
            wfs = np.array([wf_of.get(t) for t in ts])
            out = []
            for (wf, q), (m, K) in d1["models"].items():
                rows = np.where(wfs == wf)[0]
                if len(rows):
                    out.append(lr_proba(m, X[rows], K))
            return out
        r = time_encoder(mk_bge(d1_head, 512), d1_texts, n1=100, ncpu=50)
        res["bge-small-lr-d1"] = {c: {**r, "per": "state (5 decisions)"} for c in D1_CONDS}
        print("latency bge-lr d1", r, flush=True)
    # entailment model: one decision = one batch of K (premise, hypothesis) pairs
    if os.path.exists(cpath("nli.pkl")) and (only is None or "nli-deberta-v3-base" in only):
        timing = pickle.load(open(cpath("nli.pkl"), "rb"))["timing"]
        res["nli-deberta-v3-base"] = {}
        for device in ("cuda", "cpu"):
            sc = NLIScorer(device=device)
            for cond in D2_CONDS + D3_CONDS + ["d1_neutral"]:
                dec = nli_pairs(cond)
                n = 60 if device == "cuda" else (8 if cond == "d2_k150" else 20)
                rng = np.random.default_rng(C.SEED)
                pick = rng.choice(len(dec), min(n, len(dec)), replace=False)
                sc._run(dec[pick[0]][3])
                ts = []
                for i in pick:
                    a = time.perf_counter()
                    sc._run(dec[i][3])
                    if device == "cuda":
                        torch.cuda.synchronize()
                    ts.append(time.perf_counter() - a)
                e = res["nli-deberta-v3-base"].setdefault(cond, {"per": "decision (K pairs)"})
                e[f"{'gpu' if device == 'cuda' else 'cpu'}_batch1_ms_p50"] = _p50(ts)
                if device == "cuda" and cond in timing:
                    t = timing[cond]
                    e["gpu_batched_ms_per_item_p50"] = 1000 * t["seconds"] / t["decisions"]
                    e["gpu_batched_note"] = "mean over the scoring run, pairs batched by length"
                print("latency nli", device, cond, e, flush=True)
            del sc
            torch.cuda.empty_cache()
        for c in ("d1_native", "d1_calib"):
            res["nli-deberta-v3-base"][c] = res["nli-deberta-v3-base"]["d1_neutral"]
    res["_hardware"] = {"gpu": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
                        "cpu_threads": torch.get_num_threads(), "gpu_dtype": "fp32",
                        "cpu_dtype": "fp32",
                        "note": "fp32 on the GPU: on this Turing TU117 card without tensor cores "
                                "fp16 inference and mixed-precision training measured 3 to 4 "
                                "times slower than fp32"}
    json.dump(res, open(cpath("latency.json"), "w"), indent=1)


# ------------------------------------------------------------------ evaluation

def evaluate(tag, cond, T_rule):
    """Metrics through bench.decisions, so key alignment is exactly the harness's."""
    model = TAGS[tag]
    rows = bench.decisions(model, cond)
    ok, n_all = bench.coverage(rows)
    assert ok == n_all, (tag, cond, ok, n_all)
    rs = [r for r in rows if r["y"] >= 0]
    P = [r["p"] for r in rs]
    y = np.array([r["y"] for r in rs])
    groups = np.array([r["item_id"] for r in rs])
    conf = np.array([p.max() for p in P])
    correct = np.array([float(np.argmax(p) == k) for p, k in zip(P, y)])
    if T_rule[0] == "fixed":
        T = T_rule[1]
        Ps = [M.apply_T(p, T.get(r["type"], 1.0) if isinstance(T, dict) else T)
              for p, r in zip(P, rs)]
        T_desc = T
    else:
        Ps, Ts = M.crossfit_T(P, y, groups)
        T_desc = {"crossfit_folds": Ts}
    Pc, Tc = M.crossfit_T(P, y, groups)
    conf_s = np.array([p.max() for p in Ps])
    corr_s = np.array([float(np.argmax(p) == k) for p, k in zip(Ps, y)])
    conf_c = np.array([p.max() for p in Pc])
    corr_c = np.array([float(np.argmax(p) == k) for p, k in zip(Pc, y)])
    out = {"n": len(rs), "acc": float(correct.mean()),
           "acc_ci": list(M.cluster_boot(lambda i: correct[i].mean(), groups)),
           "ece_shipped": M.ece(conf, correct), "ece_scaled": M.ece(conf_s, corr_s),
           "ece_scaled_crossfit": M.ece(conf_c, corr_c),
           "temperature": T_desc, "temperature_rule": T_rule[2],
           "brier": M.brier_multi(P, y), "brier_scaled": M.brier_multi(Ps, y),
           "nll": M.nll(P, y), "nll_scaled": M.nll(Ps, y),
           "cov5": M.coverage_at_risk(conf, correct, 0.05)[0],
           "cov5_scaled": M.coverage_at_risk(conf_s, corr_s, 0.05)[0],
           "aurc": M.aurc(conf, correct), "aurc_scaled": M.aurc(conf_s, corr_s),
           "auroc_oos": None, "softacc": None, "macro_f1": None}
    if cond == "d2_k150":
        allr = [r for r in rows]
        c_all = np.array([r["p"].max() for r in allr])
        ins = np.array([r["meta"]["in_scope"] for r in allr])
        out["auroc_oos"] = M.auroc(c_all, ins)
        out["n_oos"] = int((~ins).sum())
    if cond.startswith("d1"):
        out["softacc"] = float(np.mean([r["soft"][np.argmax(r["p"])] for r in rs]))
        out["by_type"] = {t: {"n": int(sum(r["type"] == t for r in rs)),
                              "acc": float(np.mean([c for c, r in zip(correct, rs) if r["type"] == t]))}
                          for t in ("choice", "noul", "score")}
    if cond.startswith("d3"):
        out["macro_f1"] = M.macro_f1([int(np.argmax(p)) for p in P], y, len(rs[0]["options"]))
    return out


def fit_types_from_answers(tag):
    rows = [r for r in bench.decisions(TAGS[tag], "d1_calib") if r["y"] >= 0]
    return {t: M.fit_T([r["p"] for r in rows if r["type"] == t],
                       [r["y"] for r in rows if r["type"] == t]) for t in ("choice", "noul", "score")}


def n_params(model_id, num_labels=None):
    import torch
    from transformers import AutoModel, AutoModelForSequenceClassification
    m = (AutoModelForSequenceClassification.from_pretrained(model_id, num_labels=num_labels)
         if num_labels else AutoModel.from_pretrained(model_id))
    n = sum(p.numel() for p in m.parameters())
    return int(n)


def stage_eval():
    import pickle
    build_answers()
    lat = json.load(open(cpath("latency.json"))) if os.path.exists(cpath("latency.json")) else {}
    out = {"_doc": DOC}
    bge_d2 = json.load(open(cpath("d2_bge.json")))
    bert = json.load(open(cpath("d2_bert.json")))
    d1 = pickle.load(open(cpath("d1_bge.pkl"), "rb"))
    nli = pickle.load(open(cpath("nli.pkl"), "rb"))
    lr = pickle.load(open(cpath("d2_bge_lr.pkl"), "rb"))
    n_bge = n_params(BGE)
    exposure = {k: v for k, v in bge_d2["data"].items()}
    specs = {
        "bert-base-clinc": {
            "description": "bert-base-uncased fine-tuned as a 151-way CLINC classifier (150 intents "
                           "+ out-of-scope), fp32 AdamW (weight decay 0.01), batch 32, dynamic "
                           "padding, max 64 tokens, linear warm-up 10%; served distribution = softmax over the offered intents",
            "model_id": BERT, "revision": hub_rev(BERT),
            "params": n_params(BERT, 151),
            "size_mb_fp32": round(n_params(BERT, 151) * 4 / 2 ** 20, 1),
            "training_data": {"source": f"clinc/oos-eval data_oos_plus.json at {CLINC_COMMIT[:8]}, "
                                        "train + oos_train (the rows of clinc/clinc_oos plus train, "
                                        "which decider-2b trains on)", **exposure},
            "hyperparameter_selection": {"grid": bert["grid"], "selected": bert["selected"],
                                         "criterion": "CLINC validation in-scope accuracy, ties "
                                                      "by NLL", "train_minutes": bert["train_minutes"]},
            "calibration": {"method": "one temperature by NLL (metrics.fit_T grid) on the 3000 "
                                      "in-scope CLINC validation rows, 150-way distribution",
                            "T": bert["T"]},
            "T_rule": ("fixed", bert["T"], "CLINC validation split"), "conds": D2_CONDS},
        "bge-small-lr-clinc": {
            "description": "BAAI/bge-small-en-v1.5 CLS embeddings (L2-normalized, fp32) + "
                           "multinomial logistic regression over 151 classes (fp32 encoder)",
            "model_id": BGE, "revision": hub_rev(BGE),
            "params": n_bge + int(lr.coef_.size + lr.intercept_.size),
            "size_mb_fp32": round((n_bge + lr.coef_.size + lr.intercept_.size) * 4 / 2 ** 20, 1),
            "training_data": {"source": "as bert-base-clinc", **exposure},
            "hyperparameter_selection": {"C": bge_d2["C"], "val_acc": bge_d2["val_acc"],
                                         "grid": [1.0, 10.0, 100.0, 1000.0, 10000.0],
                                         "criterion": "CLINC validation in-scope accuracy"},
            "calibration": {"method": "as bert-base-clinc", "T": bge_d2["T"]},
            "T_rule": ("fixed", bge_d2["T"], "CLINC validation split"), "conds": D2_CONDS},
        "bge-small-lr-d1": {
            "description": "one soft-label logistic regression per workflow x question (20 "
                           "models) on [bge-small-en-v1.5 CLS embedding of the JSON state, TF-IDF "
                           "word uni- and bigrams]",
            "model_id": BGE, "revision": hub_rev(BGE), "params": n_bge,
            "params_note": "encoder parameters; the 20 regressions add about "
                           "20 x 5 x (384 + TF-IDF vocabulary) weights",
            "size_mb_fp32": round(n_bge * 4 / 2 ** 20, 1),
            "training_data": {"source": f"{D1_REPO} train split at {D1_REV[:8]}, soft teacher "
                                        "labels", "n_states": d1["n_pool"],
                              "excluded": "the 300 d1_calib states and all d1_neutral states",
                              "states_truncated_at_512_tokens": {"train": d1["truncated_train"],
                                                                 "eval": d1["truncated_eval"]},
                              "C_by_question": {k: v["C"] for k, v in d1["chosen"].items()}},
            "calibration": {"method": "one temperature per question type fitted on d1_calib "
                                      "(metrics.fit_T), the a01 rule"},
            "T_rule": None, "conds": D1_CONDS},
        "nli-deberta-v3-base": {
            "description": "zero-shot entailment classifier, no task training; premise = state "
                           "text + newline + instructions, hypothesis = option rubric (template "
                           "'This text is about {}.' for rubrics under five words without a "
                           "final period), softmax over options of entailment log-odds",
            "model_id": NLI, "revision": hub_rev(NLI), "params": n_params(NLI),
            "size_mb_fp32": round(n_params(NLI) * 4 / 2 ** 20, 1),
            "training_data": "none for these tasks (public NLI and zero-shot training mixture of "
                             "the checkpoint)",
            "truncation": nli["truncation"],
            "calibration": {"d2": "one temperature on 600 CLINC validation in-scope rows (four "
                                  "per intent), 150-way", "T_d2": nli["T_val_d2"],
                            "val_acc_d2": nli["val_acc_d2"],
                            "d1": "per question type on d1_calib (a01 rule)",
                            "d3": "five-fold cross-fitting by item (a01 rule)"},
            "T_rule": ("fixed", nli["T_val_d2"], "CLINC validation rows"),
            "conds": D2_CONDS + D3_CONDS + D1_CONDS},
    }
    for tag, s in specs.items():
        conds = s.pop("conds")
        rule = s.pop("T_rule")
        entry = dict(s)
        entry["answers_dir"] = f"shared/answers/{TAGS[tag]}"
        if tag in ("bge-small-lr-d1", "nli-deberta-v3-base"):
            Td1 = fit_types_from_answers(tag)
        for cond in conds:
            if cond.startswith("d1"):
                r = ("fixed", Td1, "d1_calib, one temperature per question type")
            elif cond.startswith("d3"):
                r = ("crossfit", None, "five-fold cross-fitting by item on the condition itself")
            else:
                r = rule
            m = evaluate(tag, cond, r)
            L = lat.get(tag, {}).get(cond, {})
            m["latency_ms_p50_gpu"] = L.get("gpu_batch1_ms_p50")
            m["latency_ms_per_item_gpu_batched"] = L.get("gpu_batched_ms_per_item_p50")
            m["latency_ms_p50_cpu"] = L.get("cpu_batch1_ms_p50")
            m["latency_unit"] = L.get("per", "item")
            entry[cond] = m
            print(f"{tag:22s} {cond:20s} n={m['n']:4d} acc={m['acc']:.3f} "
                  f"ece={m['ece_shipped']:.3f}->{m['ece_scaled']:.3f} cov5={m['cov5']:.2f} "
                  f"auroc={m['auroc_oos']}", flush=True)
        out[tag] = entry
    out["_hardware"] = lat.get("_hardware")
    C.dump(out, "baselines.json")


DOC = ("Conventional baselines written by shared/src/b01_baselines.py. Top-level keys are model "
       "tags; each holds description, model_id, revision, params, size_mb_fp32, training_data, "
       "calibration and one entry per condition. A condition entry has n (scored decisions; for "
       "d2_k150 the 600 in-scope items), acc and acc_ci (95% percentile interval, 1000 cluster "
       "bootstrap resamples of items, metrics.cluster_boot), ece_shipped (T = 1 output, 10 "
       "equal-mass bins, metrics.ece), ece_scaled (after the temperature named in "
       "temperature_rule: CLINC validation split for D2, d1_calib per question type for D1, "
       "five-fold cross-fitting by item for D3), ece_scaled_crossfit (the a01 cross-fitting "
       "rule on every condition, comparable with e1_main.json), brier (multi-class, shipped), "
       "nll, cov5 (largest coverage with at most 5% risk, shipped confidence; cov5_scaled after "
       "scaling), aurc, auroc_oos (d2_k150 only: in-scope versus the 200 out-of-scope items by top "
       "probability), softacc (D1: teacher probability of the chosen option, as in a01), "
       "macro_f1 (D3), latency_ms_p50_gpu (batch 1, fp32, NVIDIA T1000), "
       "latency_ms_per_item_gpu_batched, latency_ms_p50_cpu (batch 1, fp32) and latency_unit "
       "(item, state, or decision of K entailment pairs). Unused keys are null. Answer files in "
       "the harness format are in answers_dir; probs are the T = 1 outputs and raw.probs_scaled "
       "holds the scaled ones where one temperature applies.")


def main():
    stages = sys.argv[1:] or ["d2bge", "d2bert", "d1", "nli", "latency", "eval"]
    for s in stages:
        t0 = time.time()
        {"d2bge": stage_d2bge, "d2bert": stage_d2bert, "d1": stage_d1, "nli": stage_nli, "latency": stage_latency, "latency_d1": stage_latency_d1,
         "eval": stage_eval, "answers": build_answers}[s]()
        print(f"stage {s} done in {(time.time() - t0) / 60:.1f} min", flush=True)


if __name__ == "__main__":
    main()
