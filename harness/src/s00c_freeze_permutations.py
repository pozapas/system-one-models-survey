"""Two further distractor sequences for the cardinality sweep (revision, reviewer point 1).

The original sweep (d2_k5, d2_k20, d2_k50, d2_k150, written by s00_freeze_inputs.d2_all) asks
the same 600 in-scope CLINC-150 items with option sets that are nested prefixes of ONE fixed
random permutation of the 150 intents per item, the gold intent always included. With one
permutation, the option count and the particular distractors that enter at each K are
confounded. This script adds two independent permutations under exactly the same rule:

    d2_k{K}_p2   permutation stream random.Random(f"{SEED}-d2perm-p2")
    d2_k{K}_p3   permutation stream random.Random(f"{SEED}-d2perm-p3")

for K in (5, 20, 50, 150), in-scope items only (600 requests per condition, including K=150,
whose original file also carries 200 out-of-scope items). p1 is the original sequence.

Construction rule, copied from d2_all without change:
  * item selection: 4 test utterances per intent drawn with random.Random(SEED), then 200
    out-of-scope utterances, exactly as in d2_all (the p2/p3 files reuse the same 600 items)
  * per item, perm = sorted intents, shuffled once with that condition family's stream, the
    items visited in the same order as d2_all (sorted intents, then sorted picks)
  * K=150 asks every intent in permutation order
  * K<150 keeps the gold intent plus the first K-1 non-gold intents of the permutation, listed
    in permutation order (nested prefixes, so the K=5 set is inside K=20 inside K=50)
  * option keys are neutral o1..oK in listed order, descriptions are the intent names with
    underscores replaced by spaces, the question text is unchanged

Proof of the rule. Before writing anything, the script replays the original random stream in
memory and checks that the regenerated d2_k5, d2_k20, d2_k50 and d2_k150 bytes have the SHA-256
recorded in manifest.json. It stops if any of them differs.

Writing. New files only. manifest.json gains one entry per new condition and a
"_d2_permutations" note with the seeds; every existing entry is asserted unchanged.

Usage: python s00c_freeze_permutations.py
"""
import hashlib
import json
import os
import random

import common as C

OUT = C.INPUTS
KS = (150, 50, 20, 5)
PERMS = {"p2": f"{C.SEED}-d2perm-p2", "p3": f"{C.SEED}-d2perm-p3"}
Q_INT = "Which intent does this request to a virtual assistant express?"


def neutral_keys(k):
    return [f"o{i + 1}" for i in range(k)]


def human(s):
    return s.replace("_", " ")


def choice_row(cond, iid, text, options, gold_name, instr, meta):
    """Byte-identical copy of the closure of the same name in s00_freeze_inputs.d2_all."""
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


def serialize(rows):
    return "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows).encode("utf-8")


def load_d2():
    d = json.load(open(os.path.join(C.DATA, "d2", "data_full.json"), encoding="utf-8"))
    domains = json.load(open(os.path.join(C.DATA, "d2", "domains.json"), encoding="utf-8"))
    dom_of = {i: dname for dname, ints in domains.items() for i in ints}
    intents = sorted(dom_of)
    assert len(intents) == 150
    return d, dom_of, intents


def original_items_and_orders():
    """Replay d2_all's random stream: item picks, out-of-scope picks, per-item shuffles."""
    d, dom_of, intents = load_d2()
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
    orders = {}
    for iid, text, lab in ins + oos:
        perm = intents[:]
        rng.shuffle(perm)
        orders[iid] = perm
    return ins, oos, orders, dom_of, intents


def rows_for(cond_of_k, items, orders, dom_of, oos=()):
    """{K: rows} under the nested-prefix rule. oos items are only used at K=150 (p1 replay)."""
    out = {}
    out[150] = [choice_row(cond_of_k(150), iid, text, orders[iid], lab, Q_INT,
                           {"in_scope": lab is not None, "intent": lab,
                            "domain": dom_of.get(lab)})
                for iid, text, lab in list(items) + list(oos)]
    for k in (50, 20, 5):
        rows = []
        for iid, text, lab in items:
            others = [o for o in orders[iid] if o != lab]
            keep = set(others[:k - 1]) | {lab}
            opts = [o for o in orders[iid] if o in keep]
            rows.append(choice_row(cond_of_k(k), iid, text, opts, lab, Q_INT,
                                   {"in_scope": True, "intent": lab, "domain": dom_of[lab]}))
        out[k] = rows
    return out


def main():
    man_path = os.path.join(OUT, "manifest.json")
    manifest = json.load(open(man_path, encoding="utf-8"))
    before = json.dumps(manifest, sort_keys=True)

    ins, oos, orders, dom_of, intents = original_items_and_orders()
    assert len(ins) == 600 and len(oos) == 200

    # 1. the replay must reproduce the four original files byte for byte
    p1 = rows_for(lambda k: f"d2_k{k}", ins, orders, dom_of, oos)
    for k in KS:
        h = hashlib.sha256(serialize(p1[k])).hexdigest()
        want = manifest[f"d2_k{k}"]["sha256"]
        on_disk = hashlib.sha256(open(os.path.join(OUT, f"d2_k{k}.jsonl"), "rb").read()).hexdigest()
        assert h == want == on_disk, f"replay of d2_k{k} does not reproduce the frozen file"
        print(f"replay d2_k{k:<4d} sha256 {h} matches manifest and file")

    # 2. two independent permutation streams over the same 600 in-scope items
    for tag, seed in PERMS.items():
        rng = random.Random(seed)
        orders_p = {}
        for iid, _text, _lab in ins:
            perm = intents[:]
            rng.shuffle(perm)
            orders_p[iid] = perm
        rows = rows_for(lambda k, t=tag: f"d2_k{k}_{t}", ins, orders_p, dom_of)
        for k in sorted(KS):
            cond = f"d2_k{k}_{tag}"
            path = os.path.join(OUT, f"{cond}.jsonl")
            data = serialize(rows[k])
            if os.path.exists(path):
                old = open(path, "rb").read()
                assert old == data, f"{path} exists with different content; refusing to overwrite"
            else:
                with open(path, "wb") as fh:
                    fh.write(data)
            h = hashlib.sha256(open(path, "rb").read()).hexdigest()
            nq = sum(len(r["questions"]) for r in rows[k])
            entry = {"file": f"{cond}.jsonl", "requests": len(rows[k]), "decisions": nq,
                     "sha256": h}
            if cond in manifest:
                assert manifest[cond] == entry, f"manifest entry {cond} differs"
            manifest[cond] = entry
            print(f"{cond:14s} {len(rows[k]):4d} requests  sha256 {h}")

    # 3. sanity: nesting, gold inclusion, the permutations really differ from p1
    for tag in PERMS:
        sets = {}
        for k in KS:
            for line in open(os.path.join(OUT, f"d2_k{k}_{tag}.jsonl"), encoding="utf-8"):
                r = json.loads(line)
                g = r["gold"]["intent"]
                opts = g["native_options"]
                assert len(opts) == k and r["meta"]["intent"] in opts
                assert opts[g["options"].index(g["label"])] == r["meta"]["intent"]
                sets.setdefault(r["item_id"], {})[k] = set(opts)
        for iid, s in sets.items():
            assert s[5] <= s[20] <= s[50] <= s[150], iid
        same5 = sum(1 for iid, _t, lab in ins
                    if sets[iid][5] == set(p1[5][[x[0] for x in ins].index(iid)]
                                           ["gold"]["intent"]["native_options"]))
        print(f"{tag}: nesting and gold inclusion hold for all 600 items; "
              f"{same5} of 600 K=5 option sets coincide with p1")

    manifest["_d2_permutations"] = {
        "p1": "the original d2_k5/k20/k50/k150 files, random.Random(_seed) stream of "
              "s00_freeze_inputs.d2_all",
        "p2": {"seed": PERMS["p2"], "conditions": [f"d2_k{k}_p2" for k in sorted(KS)]},
        "p3": {"seed": PERMS["p3"], "conditions": [f"d2_k{k}_p3" for k in sorted(KS)]},
        "rule": "same 600 in-scope items as d2_k5; per item one shuffle of the sorted 150 "
                "intents; K keeps the gold plus the first K-1 non-gold intents in permutation "
                "order; keys o1..oK; in-scope items only (no out-of-scope rows at K=150)",
        "script": "src/s00c_freeze_permutations.py",
    }
    after = json.loads(before)
    for k, v in after.items():
        assert manifest[k] == v, f"existing manifest entry {k} would change"
    with open(man_path, "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=1, sort_keys=True)
    print("manifest.json: added", sorted(set(manifest) - set(after)))


if __name__ == "__main__":
    main()
