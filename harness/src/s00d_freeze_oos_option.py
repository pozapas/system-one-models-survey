"""The intent benchmark with an explicit out-of-scope option (third revision, reviewer M5).

d2_k150 asks the 600 in-scope and 200 out-of-scope CLINC-150 items with the 150 intents as
options, so a decision model has no answer that says the request fits none of them, while the
trained classifiers saw out-of-scope examples in training. d2_k150_oos asks the same 800
requests with the same question text and the same 150 options in the same order, plus one
further option appended last:

    o151   "out of scope"   (native label oos, the CLINC-150 name of the class)

The reference label of every out-of-scope item becomes o151; every in-scope item keeps its
intent. Nothing else changes, and no random stream is involved, so the file follows from the
frozen d2_k150 file alone. The script checks that d2_k150 on disk has the SHA-256 recorded in
manifest.json before deriving anything, writes d2_k150_oos.jsonl as a new file only, and adds
one manifest entry (every existing entry is asserted unchanged).

Usage: python s00d_freeze_oos_option.py
"""
import copy
import hashlib
import json
import os

import common as C

SRC, DST = "d2_k150", "d2_k150_oos"
OOS_KEY, OOS_DESC, OOS_NATIVE = "o151", "out of scope", "oos"


def main():
    man_path = os.path.join(C.INPUTS, "manifest.json")
    manifest = json.load(open(man_path, encoding="utf-8"))
    before = json.dumps(manifest, sort_keys=True)
    src_path = os.path.join(C.INPUTS, f"{SRC}.jsonl")
    raw = open(src_path, "rb").read()
    assert hashlib.sha256(raw).hexdigest() == manifest[SRC]["sha256"], "d2_k150 changed"
    dst_path = os.path.join(C.INPUTS, f"{DST}.jsonl")
    assert not os.path.exists(dst_path), f"{dst_path} exists; this script writes new files only"

    rows, n_in, n_oos = [], 0, 0
    for line in raw.decode("utf-8").splitlines():
        r = json.loads(line)
        q = r["questions"]["intent"]
        g = r["gold"]["intent"]
        assert len(q["criteria"]) == 150 and OOS_KEY not in q["criteria"]
        new = copy.deepcopy(r)
        new["key"] = f"{DST}|{r['item_id']}"
        new["condition"] = DST
        new["questions"]["intent"]["criteria"][OOS_KEY] = OOS_DESC
        new["gold"]["intent"]["options"] = g["options"] + [OOS_KEY]
        new["gold"]["intent"]["native_options"] = g["native_options"] + [OOS_NATIVE]
        if r["meta"]["in_scope"]:
            assert g["label"] is not None
            n_in += 1
        else:
            assert g["label"] is None
            new["gold"]["intent"]["label"] = OOS_KEY
            n_oos += 1
        rows.append(new)
    assert (n_in, n_oos) == (600, 200)
    data = "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows).encode("utf-8")
    with open(dst_path, "wb") as fh:
        fh.write(data)

    entry = dict(manifest[SRC])
    entry.update({"file": f"{DST}.jsonl", "sha256": hashlib.sha256(data).hexdigest(), "requests": len(rows),
                  "decisions": len(rows), "derived_from": SRC,
                  "rule": "d2_k150 with option o151 'out of scope' appended; out-of-scope "
                          "items take o151 as their reference label",
                  "script": "src/s00d_freeze_oos_option.py"})
    for k in ("bytes", "size"):
        if k in entry:
            entry[k] = len(data)
    manifest[DST] = entry
    after = json.loads(json.dumps(manifest, sort_keys=True))
    old = json.loads(before)
    assert all(after[k] == v for k, v in old.items()), "an existing manifest entry changed"
    with open(man_path, "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2, sort_keys=True)
        fh.write("\n")
    print(f"wrote {dst_path}: {len(rows)} requests ({n_in} in scope, {n_oos} out of scope), "
          f"sha256 {entry['sha256']}")


if __name__ == "__main__":
    main()
