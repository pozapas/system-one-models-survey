"""Laya's option token budget on the cardinality conditions (revision, reviewer point 3).

Laya builds one encoder sequence per question,

    [CLS] "<type> question: <instructions>" [SEP] [MASK] opt_1 [MASK] opt_2 ... [SEP] state [SEP]

(laya.common.build_sequence, laya 0.3.20, the version the answers were produced with). Each
option is rendered "<key>: <description>" (laya.common.render_options), tokenized with a
leading space and capped at 48 tokens. When the option tokens, one [MASK] each included, leave
fewer than 16 of the head_max_len budget, every option is cut to
per = max(4, (head_max_len - 16) // K) tokens including its [MASK], the instructions are cut to
max(8, remaining budget) tokens, and the whole sequence is cut at max_len. An option whose
[MASK] falls beyond max_len is dropped, and Laya then refuses the question
("options exceed head_max_len").

This script replays that construction with Laya's own functions and the pinned checkpoint's
own tokenizers (English: ModernBERT-large tokenizer, head_max_len 192, max_len 512;
multilingual: mmBERT-base tokenizer, head_max_len 256, max_len 1024; both read from the
checkpoint's rl config), for every request of every d2 cardinality condition (p1 = d2_k*,
p2, p3). No weights are loaded. The replay is checked against what the benchmark observed:
the per-request sequence length must equal the input-token usage Laya reported in its answer
files, and the replayed refusals must be exactly the requests Laya refused.

Output: results/laya_budget.json with, per model and condition, the share of requests whose
option text exceeds the head budget, the excess in tokens, how many option tokens survive, how
many options lose their description entirely, how many options are dropped at max_len, and
where the gold option sits relative to the budget; plus a compact per-request table.

Usage: python a11_laya_budget.py
"""
import json
import os
import statistics as st

import common as C

LAYA_REV = "55cf4c4ebb4ebe31b2550e8bdf3bd21b99753851"
HF = os.environ.get("HF_HOME", "D:/p4env/hf")
SNAP = os.path.join(HF, "hub", "models--convaiinnovations--laya", "snapshots", LAYA_REV)
MODELS = {"laya-en": SNAP, "laya-ml": os.path.join(SNAP, "multilingual")}
KS = [5, 20, 50, 150]
PERMS = {"p1": "", "p2": "_p2", "p3": "_p3"}
OPT_CAP = 48          # laya.common.build_sequence caps every option at 48 tokens

COLUMNS = ["item_id", "K", "opt_tokens_uncut", "opt_tokens_after_cap", "exceeds_head",
           "excess_over_head", "per_option_tokens", "options_desc_lost",
           "options_dropped", "instr_tokens_kept", "state_tokens_kept", "state_tokens",
           "seq_len", "gold_pos", "gold_marker_pos", "gold_tokens_uncut",
           "gold_tokens_kept", "gold_desc_intact", "gold_desc_lost", "gold_dropped",
           "refused", "distinct_option_texts_seen"]


def load_tok(model_dir):
    from transformers import AutoTokenizer
    return AutoTokenizer.from_pretrained(os.path.join(model_dir, "tokenizer"))


def replay(tok, cfg, rec, build_sequence, render_options):
    """One request's budget facts, and the sequence Laya itself would build."""
    hml, ml = cfg["head_max_len"], cfg["max_len"]
    q = rec["questions"]["intent"]
    qi = {"t": "choice", "ins": q["instructions"], "crit": q["criteria"]}
    mask = tok.mask_token
    opts = render_options(qi)
    K = len(opts)
    keys = list(q["criteria"])
    enc = lambda s: tok(s, add_special_tokens=False)["input_ids"]
    uncut = [len(enc(" " + o.replace(mask, " "))) for o in opts]
    # tokens of " <key>:" alone; an option whose kept tokens do not exceed this has lost
    # every token of its description
    key_len = [len(enc(" " + k + ":")) for k in keys]
    capped = [min(OPT_CAP, n) for n in uncut]
    with_mask = [1 + n for n in capped]
    total = sum(with_mask)
    exceeds = hml - total < 16
    if exceeds:
        per = max(4, (hml - 16) // max(1, K))
        kept = [min(n, per) for n in with_mask]
    else:
        per = None
        kept = with_mask
    budget = hml - sum(kept)
    head = enc("%s question: %s" % ("choice", str(q["instructions"]).replace(mask, " ")))
    head_kept = min(len(head), max(8, budget))
    # marker positions, as build_sequence lays them out
    pos, markers = 1 + head_kept + 1, []
    for n in kept:
        markers.append(pos)
        pos += n
    pre_state = pos + 1
    state_ids = enc(C_state(rec["state"]).replace(mask, " "))
    room = max(0, ml - pre_state - 1)
    st_kept = min(len(state_ids), room)
    seq_len = min(ml, pre_state + st_kept + 1)
    n_markers = sum(1 for m in markers if m < ml)

    seq, mk = build_sequence(tok, rec["state"], qi, ml, hml, truncate_left=False,
                             state_ids=state_ids)
    assert len(seq) == seq_len and mk == [m for m in markers if m < ml], rec["key"]

    # the option texts the encoder actually sees after every cut; when only " oNN:" survives,
    # keys can collide after the cut (mmBERT's " o12" for both o12 and o120)
    spans = [tuple(seq[a + 1:a + n]) for a, n in zip(mk, kept)]
    distinct = len(set(spans))
    content_kept = [n - 1 for n in kept]
    desc_lost = sum(1 for c, kl in zip(content_kept, key_len) if c <= kl)
    g = rec["gold"]["intent"]["options"].index(rec["gold"]["intent"]["label"])
    return [rec["item_id"], K, sum(uncut) + K, total, bool(exceeds),
            max(0, total - (hml - 16)), per, desc_lost, K - n_markers, head_kept, st_kept,
            len(state_ids), seq_len, g + 1, markers[g], uncut[g], content_kept[g],
            bool(content_kept[g] >= uncut[g]), bool(content_kept[g] <= key_len[g]),
            bool(markers[g] >= ml),
            bool(n_markers != K), distinct]


def C_state(state):
    return state if isinstance(state, str) else json.dumps(state, ensure_ascii=False)


def observed(model, cond):
    """{key: usage_in} for answered requests and the set of refused keys, from rep 1."""
    path = os.path.join(C.ANSWERS, model, f"{cond}__rep1.jsonl")
    if not os.path.exists(path):
        return None, None
    use, refused = {}, set()
    for line in open(path, encoding="utf-8"):
        j = json.loads(line)
        if j.get("error"):
            refused.add(j["key"])
        else:
            use[j["key"]] = j.get("usage_in")
    return use, refused


def summarize(rows, K, cfg):
    col = {c: i for i, c in enumerate(COLUMNS)}
    v = lambda c: [r[col[c]] for r in rows]
    n = len(rows)
    mean = lambda xs: float(sum(xs) / len(xs)) if xs else None
    return {
        "n_requests": n, "K": K,
        "head_max_len": cfg["head_max_len"], "max_len": cfg["max_len"],
        "option_tokens_after_cap_median": st.median(v("opt_tokens_after_cap")),
        "option_tokens_after_cap_max": max(v("opt_tokens_after_cap")),
        "option_tokens_over_head_ratio_median":
            st.median(v("opt_tokens_after_cap")) / cfg["head_max_len"],
        "share_exceeding_head_budget": mean([float(x) for x in v("exceeds_head")]),
        "excess_over_head_median_tokens": st.median(v("excess_over_head")),
        "excess_over_head_max_tokens": max(v("excess_over_head")),
        "per_option_token_cap_when_cut": (sorted(set(x for x in v("per_option_tokens") if x))
                                          or None),
        "options_whose_description_is_lost_mean": mean(v("options_desc_lost")),
        "share_of_options_description_lost": mean(v("options_desc_lost")) / K,
        "options_dropped_at_max_len_mean": mean(v("options_dropped")),
        "share_requests_refused": mean([float(x) for x in v("refused")]),
        "distinct_option_texts_seen_mean": mean(v("distinct_option_texts_seen")),
        "instruction_tokens_kept_median": st.median(v("instr_tokens_kept")),
        "state_tokens_kept_share": (sum(v("state_tokens_kept")) / sum(v("state_tokens"))),
        "sequence_length_median": st.median(v("seq_len")),
        "sequence_length_max": max(v("seq_len")),
        "share_sequence_at_max_len": mean([float(x >= cfg["max_len"]) for x in v("seq_len")]),
        "gold_position_mean": mean(v("gold_pos")),
        "gold_marker_position_median": st.median(v("gold_marker_pos")),
        "share_gold_description_intact": mean([float(x) for x in v("gold_desc_intact")]),
        "share_gold_description_lost": mean([float(x) for x in v("gold_desc_lost")]),
        "share_gold_dropped": mean([float(x) for x in v("gold_dropped")]),
    }


def main():
    from laya.common import build_sequence, render_options
    import laya
    res = {"_doc": (
        "Laya option token budget on the D2 cardinality conditions, replayed with laya "
        + getattr(laya, "__version__", "0.3.20") + "'s own build_sequence and the pinned "
        "checkpoint's tokenizers (revision " + LAYA_REV + "). Per model and condition: "
        "option_tokens_after_cap counts every option's tokens after the 48-token per-option cap "
        "plus one [MASK] per option; exceeding the head budget means head_max_len minus that "
        "count is below 16, which cuts every option to per_option_token_cap_when_cut tokens "
        "including its [MASK]; excess_over_head is that count minus (head_max_len - 16); an "
        "option's description is lost when its surviving tokens do not go past ' <key>:'; "
        "options are dropped when their [MASK] falls at or beyond max_len, and any drop makes "
        "Laya refuse the question; distinct_option_texts_seen counts the different option token "
        "strings that survive every cut (below K when truncated keys collide, as mmBERT's ' o12' "
        "for o12 and o120). gold_position is the 1-based position of the gold option in "
        "the listed order. 'check' compares the replay with the answer files: the sequence "
        "length must equal the reported usage_in and the replayed refusals must equal the "
        "error lines. per_request lists one row per request with the columns in "
        "per_request_columns."),
        "per_request_columns": COLUMNS}
    for model, mdir in MODELS.items():
        cfg_file = [f for f in os.listdir(mdir) if f.startswith("rl_") and f.endswith("_config.json")]
        cfg_all = json.load(open(os.path.join(mdir, cfg_file[0]), encoding="utf-8"))
        cfg = {"head_max_len": cfg_all["head_max_len"], "max_len": cfg_all["max_len"],
               "encoder": cfg_all["encoder"]}
        tok = load_tok(mdir)
        mres = {"config": cfg, "conditions": {}, "per_request": {}}
        for p, suf in PERMS.items():
            for K in KS:
                cond = f"d2_k{K}{suf}"
                path = os.path.join(C.INPUTS, f"{cond}.jsonl")
                recs = [json.loads(l) for l in open(path, encoding="utf-8")]
                recs = [r for r in recs if r["gold"]["intent"]["label"] is not None]
                rows = [replay(tok, cfg, r, build_sequence, render_options) for r in recs]
                s = summarize(rows, K, cfg)
                s["permutation"] = p
                use, refused = observed(model, cond)
                if use is not None:
                    col = {c: i for i, c in enumerate(COLUMNS)}
                    keyed = {f"{cond}|{r[0]}": r for r in rows}
                    n_cmp = sum(1 for k in use if k in keyed and use[k] is not None)
                    n_eq = sum(1 for k, u in use.items()
                               if k in keyed and u == keyed[k][col["seq_len"]])
                    pred_ref = {k for k, r in keyed.items() if r[col["refused"]]}
                    obs_ref = {k for k in refused if k in keyed}
                    s["check"] = {"answered_compared": n_cmp,
                                  "seq_len_equals_reported_usage": n_eq,
                                  "refused_observed": len(obs_ref),
                                  "refused_replayed": len(pred_ref),
                                  "refusals_match": pred_ref == obs_ref}
                else:
                    s["check"] = "no answers yet for this condition"
                mres["conditions"][cond] = s
                mres["per_request"][cond] = rows
                print(f"{model} {cond:11s} exceeds={s['share_exceeding_head_budget']:.2f} "
                      f"opt_tok_med={s['option_tokens_after_cap_median']} "
                      f"excess_med={s['excess_over_head_median_tokens']} "
                      f"desc_lost={s['share_of_options_description_lost']:.2f} "
                      f"refused={s['share_requests_refused']:.2f} "
                      f"distinct={s['distinct_option_texts_seen_mean']:.0f} "
                      f"gold_intact={s['share_gold_description_intact']:.2f} "
                      f"check={s['check']}", flush=True)
        res[model] = mres
    C.dump(res, "laya_budget.json")


if __name__ == "__main__":
    main()
