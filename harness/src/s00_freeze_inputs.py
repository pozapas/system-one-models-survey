"""Freeze every request the benchmark sends, one JSONL file per condition.

Every model, hosted or open, reads exactly these files, so the state, question and
option text are byte-identical across models. A record is

    {"key", "dataset", "condition", "item_id", "state", "questions", "gold", "meta"}

where "state" and "questions" together are the body of a POST /v1/systemone request,
and "gold" maps each question id to {"type", "label", "options", "soft"} with option
keys as they appear in that condition.

Conditions
    d1_native      typed-decisions test split, questions exactly as published
    d1_neutral     the same, Choice option keys replaced by o1..oK (rubrics unchanged)
    d1_calib       300 training-split states in the neutral form, for temperature fits
    e2_d1_<name>   every noul question of d1 recast as a two-option Choice whose keys
                   are 0/1, no/yes, yes/no (polarity swapped against the rubric) or
                   random strings; rubrics and their order are held fixed
    d2_k150        CLINC-150 test, 600 in-scope (4 per intent) + 200 out-of-scope
    d2_k50/k20/k5  the same 600 in-scope items with nested option subsets that
                   always contain the gold intent
    d2_hier_dom    domain Choice (10 options) for the 600 in-scope items
    d2_hier_int    intent Choice within the gold domain (15 options)
    d3_<task>      human-labelled social-science tasks, neutral keys
    e2_d3_<name>   binary d3 tasks under the four naming conditions

Run once. Re-running reproduces the same files, and the manifest records SHA-256.
"""
import hashlib
import json
import os
import random
import re
import string

import common as C

OUT = C.INPUTS
D1_REPO = "LocalLLaMA/typed-decisions"
NAMINGS = ["k01", "kny", "kswap", "krand"]


def neutral_keys(k):
    return [f"o{i + 1}" for i in range(k)]


def write(cond, rows, manifest):
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, f"{cond}.jsonl")
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        for r in rows:
            # no sort_keys: insertion order of each criteria dict is the option order
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    h = hashlib.sha256(open(path, "rb").read()).hexdigest()
    nq = sum(len(r["questions"]) for r in rows)
    manifest[cond] = {"file": f"{cond}.jsonl", "requests": len(rows), "decisions": nq,
                      "sha256": h}
    print(f"{cond:18s} {len(rows):5d} requests {nq:6d} decisions")


# ------------------------------------------------------------------ D1

def d1_rows(split, neutral, cond, pick=None):
    from datasets import load_dataset
    ds = load_dataset(D1_REPO, "all", split=split)
    rows = []
    for r in ds:
        if pick is not None and r["id"] not in pick:
            continue
        qs = json.loads(r["questions"])
        gold = json.loads(r["gold"])
        state = json.loads(r["state"])
        out_q, out_g = {}, {}
        for qid, q in qs.items():
            g = gold[qid]
            if q["type"] == "choice":
                names = list(q["criteria"].keys())
                keys = neutral_keys(len(names)) if neutral else names
                ren = dict(zip(names, keys))
                out_q[qid] = {"type": "choice", "instructions": q["instructions"],
                              "criteria": {ren[n]: q["criteria"][n] for n in names}}
                out_g[qid] = {"type": "choice", "label": ren[g["label"]], "options": keys,
                              "soft": {ren[n]: g["probabilities"][n] for n in names},
                              "native_options": names}
            elif q["type"] == "noul":
                out_q[qid] = q
                out_g[qid] = {"type": "noul", "label": g["label"], "options": ["false", "true"],
                              "soft": {"false": g["probabilities"]["false"],
                                       "true": g["probabilities"]["true"]}}
            else:
                lv = [str(i) for i in range(len(q["criteria"]))]
                out_q[qid] = q
                out_g[qid] = {"type": "score", "label": g["label"], "options": lv,
                              "soft": {k: g["probabilities"][k] for k in lv}}
        rows.append({"key": f"{cond}|{r['id']}", "dataset": "d1", "condition": cond,
                     "item_id": r["id"], "state": state, "questions": out_q, "gold": out_g,
                     "meta": {"workflow": r["workflow"],
                              "label_agreement": json.loads(r["label_agreement"])}})
    return rows


def naming_pair(name, rng):
    """Keys for (negative rubric, positive rubric) under one naming condition."""
    if name == "k01":
        return "0", "1"
    if name == "kny":
        return "no", "yes"
    if name == "kswap":
        return "yes", "no"
    a = "".join(rng.choice(string.ascii_lowercase) for _ in range(5))
    b = a
    while b == a:
        b = "".join(rng.choice(string.ascii_lowercase) for _ in range(5))
    return a, b


def e2_from_binary(base_rows, name, cond, binary_fn):
    """Recast binary questions under a naming condition, rubric order held fixed.

    binary_fn(row, qid) returns (instructions, neg_rubric, pos_rubric, gold_is_pos,
    soft_pos) for a binary question, or None to skip it.
    """
    rng = random.Random(f"{C.SEED}-{cond}")
    rows = []
    for r in base_rows:
        out_q, out_g = {}, {}
        for qid in r["questions"]:
            b = binary_fn(r, qid)
            if b is None:
                continue
            instr, neg, pos, is_pos, soft_pos = b
            kn, kp = naming_pair(name, rng)
            out_q[qid] = {"type": "choice", "instructions": instr,
                          "criteria": {kn: neg, kp: pos}}
            out_g[qid] = {"type": "choice", "label": kp if is_pos else kn,
                          "options": [kn, kp], "positive": kp,
                          "soft": None if soft_pos is None else {kn: 1 - soft_pos, kp: soft_pos}}
        if out_q:
            rows.append({"key": f"{cond}|{r['item_id']}", "dataset": r["dataset"],
                         "condition": cond, "item_id": r["item_id"], "state": r["state"],
                         "questions": out_q, "gold": out_g,
                         "meta": dict(r["meta"], naming=name)})
    return rows


def d1_binary(r, qid):
    q, g = r["questions"][qid], r["gold"][qid]
    if q["type"] != "noul":
        return None
    crit = q.get("criteria") or {"false": "No.", "true": "Yes."}
    return (q["instructions"], crit["false"], crit["true"], g["label"] == "true",
            g["soft"]["true"])


# ------------------------------------------------------------------ D2

def human(s):
    return s.replace("_", " ")


def d2_all(manifest):
    d = json.load(open(os.path.join(C.DATA, "d2", "data_full.json"), encoding="utf-8"))
    domains = json.load(open(os.path.join(C.DATA, "d2", "domains.json"), encoding="utf-8"))
    dom_of = {i: dname for dname, ints in domains.items() for i in ints}
    intents = sorted(dom_of)
    assert len(intents) == 150
    rng = random.Random(C.SEED)
    by_int = {}
    for text, lab in d["test"]:
        by_int.setdefault(lab, []).append(text)
    ins = []
    for lab in intents:
        pick = rng.sample(range(len(by_int[lab])), 4)
        ins += [(f"{lab}_{i:02d}", by_int[lab][i], lab) for i in sorted(pick)]
    oos_texts = [t for t, _ in d["oos_test"]]
    oos_idx = sorted(rng.sample(range(len(oos_texts)), 200))
    oos = [(f"oos_{i:04d}", oos_texts[i], None) for i in oos_idx]

    q_int = "Which intent does this request to a virtual assistant express?"
    q_dom = "Which domain does this request to a virtual assistant belong to?"

    def choice_row(cond, iid, text, options, gold_name, instr, meta):
        keys = neutral_keys(len(options))
        ren = dict(zip(options, keys))
        return {"key": f"{cond}|{iid}", "dataset": "d2", "condition": cond, "item_id": iid,
                "state": text,
                "questions": {"intent": {"type": "choice", "instructions": instr,
                                         "criteria": {ren[o]: human(o) for o in options}}},
                "gold": {"intent": {"type": "choice",
                                    "label": ren[gold_name] if gold_name else None,
                                    "options": keys, "native_options": options,
                                    "soft": None}},
                "meta": meta}

    # one fixed permutation of the 150 intents per item, and nested subsets
    orders = {}
    for iid, text, lab in ins + oos:
        perm = intents[:]
        rng.shuffle(perm)
        orders[iid] = perm
    rows150 = [choice_row("d2_k150", iid, text, orders[iid], lab, q_int,
                          {"in_scope": lab is not None, "intent": lab,
                           "domain": dom_of.get(lab)})
               for iid, text, lab in ins + oos]
    write("d2_k150", rows150, manifest)
    for k in (50, 20, 5):
        rows = []
        for iid, text, lab in ins:
            others = [o for o in orders[iid] if o != lab]
            keep = set(others[:k - 1]) | {lab}          # nested: prefix of one permutation
            opts = [o for o in orders[iid] if o in keep]
            rows.append(choice_row(f"d2_k{k}", iid, text, opts, lab, q_int,
                                   {"in_scope": True, "intent": lab, "domain": dom_of[lab]}))
        write(f"d2_k{k}", rows, manifest)
    dnames = sorted(domains)
    rows_dom, rows_int = [], []
    for iid, text, lab in ins:
        dperm = dnames[:]
        rng.shuffle(dperm)
        r = choice_row("d2_hier_dom", iid, text, dperm, dom_of[lab], q_dom,
                       {"in_scope": True, "intent": lab, "domain": dom_of[lab]})
        r["questions"]["domain"] = r["questions"].pop("intent")
        r["gold"]["domain"] = r["gold"].pop("intent")
        rows_dom.append(r)
        iperm = [o for o in orders[iid] if dom_of[o] == dom_of[lab]]
        rows_int.append(choice_row("d2_hier_int", iid, text, iperm, lab, q_int,
                                   {"in_scope": True, "intent": lab, "domain": dom_of[lab]}))
    write("d2_hier_dom", rows_dom, manifest)
    write("d2_hier_int", rows_int, manifest)


# ------------------------------------------------------------------ D3

def d3_all(manifest):
    ddir = os.path.join(C.DATA, "d3")
    if not os.path.isdir(ddir):
        print("D3 not prepared yet; skipped")
        return
    for fn in sorted(os.listdir(ddir)):
        if not fn.endswith(".jsonl"):
            continue
        task = fn[:-6]
        items = [json.loads(l) for l in open(os.path.join(ddir, fn), encoding="utf-8")]
        cond = f"d3_{task}"
        rows = []
        for it in items:
            opts = it["options"]
            keys = neutral_keys(len(opts))
            ren = dict(zip(opts, keys))
            rows.append({"key": f"{cond}|{it['id']}", "dataset": "d3", "condition": cond,
                         "item_id": str(it["id"]), "state": it["text"],
                         "questions": {task: {"type": "choice",
                                              "instructions": it["question"],
                                              "criteria": {ren[o]: it["option_desc"][o]
                                                           for o in opts}}},
                         "gold": {task: {"type": "choice", "label": ren[it["gold"]],
                                         "options": keys, "native_options": opts,
                                         "soft": None}},
                         "meta": {"task": task, "binary": bool(it["binary"]),
                                  "positive": it.get("positive"),
                                  "native_gold": it["gold"]}})
        write(cond, rows, manifest)
        if items[0]["binary"]:
            def fn_bin(r, qid, _items={str(i["id"]): i for i in items}):
                it = _items[r["item_id"]]
                pos = it["positive"]
                neg = [o for o in it["options"] if o != pos][0]
                # the package's binary rubrics open with "True:" or "False:"; that
                # prefix would carry polarity independently of the option name, so the
                # naming conditions strip it and keep the rest of the rubric verbatim
                strip = lambda s: re.sub(r"^(True|False):\s*", "", s)
                return (it["question"], strip(it["option_desc"][neg]),
                        strip(it["option_desc"][pos]), it["gold"] == pos, None)
            for name in NAMINGS:
                write(f"e2_d3_{task}_{name}",
                      e2_from_binary(rows, name, f"e2_d3_{task}_{name}", fn_bin), manifest)


def main():
    os.environ.setdefault("HF_HOME", "D:/p4env/hf")
    manifest = {}
    native = d1_rows("test", False, "d1_native")
    write("d1_native", native, manifest)
    neutral = d1_rows("test", True, "d1_neutral")
    write("d1_neutral", neutral, manifest)
    from datasets import load_dataset
    tr = load_dataset(D1_REPO, "all", split="train")
    rng = random.Random(C.SEED)
    pick = set()
    for wf in sorted(set(tr["workflow"])):
        ids = sorted(r["id"] for r in tr if r["workflow"] == wf)
        pick |= set(rng.sample(ids, 75))
    write("d1_calib", d1_rows("train", True, "d1_calib", pick), manifest)
    for name in NAMINGS:
        write(f"e2_d1_{name}", e2_from_binary(native, name, f"e2_d1_{name}", d1_binary),
              manifest)
    d2_all(manifest)
    d3_all(manifest)
    # the test-retest subset: 10 states per workflow of d1_neutral, 200 decisions
    rng = random.Random(f"{C.SEED}-retest")
    sub = []
    for wf in sorted({r["meta"]["workflow"] for r in neutral}):
        ids = sorted(r["item_id"] for r in neutral if r["meta"]["workflow"] == wf)
        sub += rng.sample(ids, 10)
    manifest["_retest_subset"] = {"condition": "d1_neutral", "item_ids": sorted(sub)}
    manifest["_seed"] = C.SEED
    manifest["_sources"] = {
        "d1": f"https://huggingface.co/datasets/{D1_REPO} revision c76749ec58bd8c3d2ea706b31c333a9059c38f90",
        "d2": "https://github.com/clinc/oos-eval data/data_full.json and domains.json, commit "
              + open(os.path.join(C.DATA, "d2", "CLINC_COMMIT")).read().strip()}
    with open(os.path.join(OUT, "manifest.json"), "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=1, sort_keys=True)


if __name__ == "__main__":
    main()
