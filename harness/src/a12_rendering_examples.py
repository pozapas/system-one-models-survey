"""The exact text and token sequence each model family reads for the same frozen request.

Revision, reviewer point 2. Every model receives byte-identical wire requests (state plus
questions, colab/inputs/*.jsonl), but each model's own code turns that request into its own
token sequence. This script runs each project's own rendering code (no weights) at the pinned
revision on two example requests and records the decoded text, the token ids and the length:

    d1_neutral|security_incidents_000058   a D1 state with choice, noul and score questions
    d2_k5|accept_reservations_00         a D2 intent question with five options

Families and the rendering function used (all at the revision the answers record):
    jev-1.13.0      hosted; its internal rendering is not observable, the JSON body sent and
                    the input-token usage the service reported are recorded instead
    laya-en/-ml     laya.common.build_sequence, one sequence per question, checkpoint tokenizers
    kev             kev.api.to_record then kev.model.encode (kev-0.8b checkpoint metadata and
                    base tokenizer; kev-9b uses the same code path and Qwen3.5 tokenizer family)
    decider-2b      decider.systemone.render_question / plan_rows and decider.prompt.build,
                    one row per question and one isolated yes/no row per score level
    this-that-1.0   adapters.thisthat_render then thisthat.prompt.build, under the original
                    "key: description" rendering and the description-only alternative
    nimble-9b       adapters.nimble_schema then the repository's serving_schema.prepare_prompts,
                    one prompt per field
    comparator      adapters.comparator_prompt through the Qwen3-14B-AWQ chat template

Output: results/rendering_examples.json

Usage: python a12_rendering_examples.py   (HF_HOME defaults to D:/p4env/hf; downloads only
tokenizer and code files that are not cached yet)
"""
import json
import os
import sys
import traceback

os.environ.setdefault("HF_HOME", "D:/p4env/hf")
os.environ.setdefault("TORCHDYNAMO_DISABLE", "1")
os.environ.setdefault("TORCH_COMPILE_DISABLE", "1")
os.environ.setdefault("USE_TF", "0")

import common as C
import harness
import adapters as A

EXAMPLES = ["d1_neutral|security_incidents_000058", "d2_k5|accept_reservations_00"]
REV = {  # the revision every original answer line records
    "convaiinnovations/laya": "55cf4c4ebb4ebe31b2550e8bdf3bd21b99753851",
    "jaredpalmer/kev-0.8b": "9a45d25eb2ab761841196625383fa1dff0e56c1e",
    "jaredpalmer/kev-9b": "2629c06a5aeb0feb3b9783bafed17ed8f39ecf5c",
    "Mapika/decider-2b": "d61c1c16089572df5d180329b9fea4997a90090c",
    "flock-io/this-that-model-1.0": "3d927195c4f9845efe66c5715883a7a0f42b1239",
    "bespokelabs/Bespoke-Nimble-9B": "bd792f44ec8e265be861bfcdf4e05967ffe0e858",
    "Qwen/Qwen3-14B-AWQ": "31c69efc29464b6bb0aee1398b5a7b50a99340c3",
}


def snap(repo, patterns=None):
    import huggingface_hub as hh
    return hh.snapshot_download(repo, revision=REV[repo], allow_patterns=patterns)


def seq(tok, ids, **extra):
    return dict(extra, n_tokens=len(ids), text=tok.decode(ids), token_ids=list(map(int, ids)))


def get_record(key):
    cond = key.split("|")[0]
    return next(r for r in harness.load_inputs(cond) if r["key"] == key)


# ------------------------------------------------------------------ families

def fam_jev(rec):
    body = {"state": rec["state"], "questions": rec["questions"], "model": "jev-1.13.0"}
    cond = rec["condition"]
    use = None
    path = os.path.join(C.ANSWERS, "jev-1.13.0", f"{cond}__rep1.jsonl")
    for line in open(path, encoding="utf-8"):
        j = json.loads(line)
        if j["key"] == rec["key"]:
            use = j.get("usage_in")
            break
    return {"renderer": "POST /v1/systemone JSON body (server-side rendering not observable)",
            "revision": "jev-1.13.0", "request_body": body,
            "reported_input_tokens": use, "sequences": []}


def fam_laya(rec, sub):
    from transformers import AutoTokenizer
    from laya.common import build_sequence, render_options
    base = snap("convaiinnovations/laya", ["*config.json", "tokenizer/*",
                                            "multilingual/*config.json",
                                            "multilingual/tokenizer/*"])
    d = os.path.join(base, sub) if sub else base
    cfgf = [f for f in os.listdir(d) if f.startswith("rl_") and f.endswith("_config.json")][0]
    cfg = json.load(open(os.path.join(d, cfgf), encoding="utf-8"))
    tok = AutoTokenizer.from_pretrained(os.path.join(d, "tokenizer"))
    out = []
    for qid, q in rec["questions"].items():
        crit = q.get("criteria")
        if q["type"] == "noul" and isinstance(crit, dict):
            crit = {str(k).lower(): v for k, v in crit.items()}
        qi = {"t": q["type"], "ins": q["instructions"] if isinstance(q["instructions"], str)
              else json.dumps(q["instructions"], ensure_ascii=False), "crit": crit}
        ids, markers = build_sequence(tok, rec["state"], qi, cfg["max_len"], cfg["head_max_len"],
                                      truncate_left=isinstance(rec["state"], list))
        out.append(seq(tok, ids, question=qid, option_strings=render_options(qi),
                       option_marker_positions=markers))
    return {"renderer": "laya.common.build_sequence (laya 0.3.20)",
            "revision": REV["convaiinnovations/laya"], "encoder": cfg["encoder"],
            "head_max_len": cfg["head_max_len"], "max_len": cfg["max_len"], "sequences": out}


def fam_kev(rec):
    from kev.api import SystemOneRequest, to_record
    from kev.checkpoint import Checkpoint
    from kev.model import SERVE_MAX_BRANCH, SERVE_MAX_STATE, encode, load_tokenizer
    repo = "jaredpalmer/kev-0.8b"
    snap(repo, ["head.pt", "*.json"])
    ck = Checkpoint(f"{repo}@{REV[repo]}")
    meta = ck.meta
    tok = load_tokenizer(meta.base, revision=meta.base_revision)
    req = SystemOneRequest(state=rec["state"], questions=rec["questions"])
    internal, qmeta = to_record(req)
    enc = encode(tok, internal, max_state=SERVE_MAX_STATE, max_branch=SERVE_MAX_BRANCH,
                 option_isolation=meta.option_isolation)
    return {"renderer": "kev.api.to_record + kev.model.encode (kev at the pinned GitHub commit)",
            "revision": REV[repo], "base": meta.base, "base_revision": meta.base_revision,
            "option_strings": {m["id"]: q["options"] for m, q in zip(qmeta, internal["questions"])},
            "sequences": [seq(tok, enc["ids"], note="one packed sequence, state then one branch "
                                                     "per question")]}


def fam_decider(rec):
    from transformers import AutoTokenizer
    d = snap("Mapika/decider-2b", ["decider/*", "*.json", "*.jinja"])
    if d not in sys.path:
        sys.path.insert(0, d)
    from decider.infer import Example, Q
    from decider.prompt import MAX_OPTIONS, build
    from decider.systemone import plan_rows, render_question, render_state
    tok = AutoTokenizer.from_pretrained(d)

    class Keep:
        def shuffle(self, x):
            pass

        def sample(self, xs, k):
            return xs[:k]

    ctx = render_state(rec["state"])
    rqs = {k: render_question(v) for k, v in rec["questions"].items()}
    flat, index = plan_rows(rqs, True)
    out = []
    names = []
    for k, kind, s, n in index:
        names += [f"{k}" if kind == "list" else f"{k} level {j}" for j in range(n)]
    for name, r in zip(names, flat):
        it = build(Example(ctx, [Q(r["question"], list(r["options"]), 0)]), tok, Keep(),
                   max_options=MAX_OPTIONS, max_ctx_tokens=32768)
        out.append(seq(tok, it["ids"], row=name, option_strings=list(r["options"])))
    return {"renderer": "decider.systemone.render_question + plan_rows(isolated) + "
                        "decider.prompt.build, independent=True (one row per question)",
            "revision": REV["Mapika/decider-2b"], "sequences": out}


def fam_thisthat(rec):
    from transformers import AutoTokenizer
    from thisthat import Question
    from thisthat.prompt import build
    d = snap("flock-io/this-that-model-1.0", ["*.json", "*.jinja"])
    tok = AutoTokenizer.from_pretrained(d)
    res = {"renderer": "adapters.thisthat_render + thisthat.prompt.build (state_first)",
           "revision": REV["flock-io/this-that-model-1.0"], "renderings": {}}
    for mode in ("keydesc", "desc"):
        state_text, items = A.thisthat_render(rec, mode)
        qs = [Question(instr, opts) for _, instr, opts, _ in items]
        b = build(tok, state_text, qs)
        res["renderings"][mode] = {
            "option_strings": {qid: opts for qid, _, opts, _ in items},
            "sequences": [seq(tok, b["ids"], answer_slots=b["slots"])]}
    return res


def fam_nimble(rec):
    from transformers import AutoTokenizer
    d = snap("bespokelabs/Bespoke-Nimble-9B", ["*.py", "*.json", "*.jinja"])
    if d not in sys.path:
        sys.path.insert(0, d)
    import serving_schema
    contract = json.load(open(os.path.join(d, "schema_config.json"), encoding="utf-8"))
    tok = AutoTokenizer.from_pretrained(d)
    schema, score_fields = A.nimble_schema(rec["questions"])
    pp = serving_schema.prepare_prompts(tok, A._state_text(rec["state"]), schema,
                                        contract["max_length"])
    out = [seq(tok, ids, field=name) for name, ids in zip(pp.names, pp.full_ids)]
    return {"renderer": "adapters.nimble_schema + serving_schema.prepare_prompts "
                        "(one prompt per field)",
            "revision": REV["bespokelabs/Bespoke-Nimble-9B"], "schema": schema,
            "score_fields": score_fields, "sequences": out}


def fam_comparator(rec):
    from transformers import AutoTokenizer
    d = snap("Qwen/Qwen3-14B-AWQ", ["*.json", "*.txt", "*.jinja"])
    tok = AutoTokenizer.from_pretrained(d)
    out = []
    for qid, q in rec["questions"].items():
        prompt, keys, n_report = A.comparator_prompt(rec, qid, q)
        text = tok.apply_chat_template([{"role": "user", "content": prompt}], tokenize=False,
                                       add_generation_prompt=True, enable_thinking=False)
        ids = tok.encode(text, add_special_tokens=False)
        out.append(seq(tok, ids, question=qid, n_report=n_report))
    return {"renderer": "adapters.comparator_prompt + chat template, thinking off",
            "revision": REV["Qwen/Qwen3-14B-AWQ"], "sequences": out}


def recorded_usage(tag, rec):
    path = os.path.join(C.ANSWERS, tag, f"{rec['condition']}__rep1.jsonl")
    if not os.path.exists(path):
        return None
    for line in open(path, encoding="utf-8"):
        j = json.loads(line)
        if j["key"] == rec["key"]:
            return j.get("usage_in")
    return None


FAMILIES = [("jev-1.13.0", fam_jev), ("laya-en", lambda r: fam_laya(r, None)),
            ("laya-ml", lambda r: fam_laya(r, "multilingual")), ("kev", fam_kev),
            ("decider-2b", fam_decider), ("this-that-1.0", fam_thisthat),
            ("nimble-9b", fam_nimble), ("comparator-open", fam_comparator)]


def option_join_summary(fam, block):
    """How a choice option reaches the model: the key, the description, or both joined."""
    return {"jev-1.13.0": "not observable (server side)",
            "laya-en": "key: description (laya.common.render_options)",
            "laya-ml": "key: description (laya.common.render_options)",
            "kev": "key: description (kev.api.option_text)",
            "decider-2b": "key: description (decider.systemone.render_question)",
            "this-that-1.0": "key: description in the original runs (adapter), description "
                             "only under this-that-1.0-desc",
            "nimble-9b": "key as the enum value and description as a separate "
                         "choice_descriptions field, both inside one JSON schema",
            "comparator-open": "- key: description (adapter prompt)"}[fam]


def main():
    res = {"_doc": (
        "Exact rendered input each model family builds from the same frozen request, produced "
        "by each project's own rendering code at the pinned revision with tokenizers only. For "
        "each example request and family: renderer (the function used), revision, and "
        "sequences, each with the decoded text, token ids and token count. Laya builds one "
        "sequence per question, decider one row per question plus one isolated row per score "
        "level, Nimble and the comparator one prompt per question, Kev and this-that one "
        "sequence for all questions. this-that carries both the original key: description "
        "rendering and the description-only alternative. choice_option_join states how a "
        "choice option's key and description reach each model."),
        "examples": {}}
    for key in EXAMPLES:
        rec = get_record(key)
        ex = {"request": {"state": rec["state"], "questions": rec["questions"]}, "families": {}}
        for fam, fn in FAMILIES:
            try:
                block = fn(rec)
                block["choice_option_join"] = option_join_summary(fam, block)
                tag = {"kev": "kev-0.8b"}.get(fam, fam)
                if fam != "jev-1.13.0" and "sequences" in block:
                    got = recorded_usage(tag, rec)
                    if got is not None:
                        # Laya and Kev report the tokens of the sequences above (summed over
                        # Laya's per-question rows); decider counts the shared state once
                        block["usage_in_recorded_in_answers"] = got
                        block["tokens_rendered_here"] = sum(s["n_tokens"]
                                                            for s in block["sequences"])
            except Exception as e:     # noqa: BLE001, recorded rather than fatal
                block = {"error": repr(e), "traceback": traceback.format_exc()[-1500:]}
            ex["families"][fam] = block
            seqs = block.get("sequences") or [s for r in block.get("renderings", {}).values()
                                              for s in r["sequences"]]
            print(f"{key:40s} {fam:16s} "
                  + ("ERROR " + block["error"][:150] if "error" in block
                     else f"{len(seqs)} sequence(s), tokens {[s['n_tokens'] for s in seqs]}"),
                  flush=True)
        res["examples"][key] = ex
    C.dump(res, "rendering_examples.json")


if __name__ == "__main__":
    main()
