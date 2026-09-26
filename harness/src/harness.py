"""One harness for every decision model in the benchmark.

A backend answers one frozen request, which is the body of a POST /v1/systemone call
({"state", "questions"}), and returns a dict of normalized answers

    {qid: {"probs": {option_key: p, ...}, "raw": <the model's own answer object>}}

where option keys are those of the request ("false"/"true" for noul, "0".."L-1" for
score). The runner writes one append-only JSONL line per request, keyed by the
record key, with the model identifier, the revision, the repeat index, the run date,
the wall-clock latency and the input-token usage when the backend reports it. An
interrupted run resumes without repeating work.

Backends
    jev        TypeSafe API through typesafe-sdk, model pinned to jev-1.13.0
    systemone  any server that implements the same wire format (laya-serve,
               kev.serve, decider.serve), through plain HTTP
    others     in-process adapters for the open models live in adapters.py and
               register themselves through register()

Usage
    python harness.py --model jev --cond d1_neutral --rep 1 [--limit 10]
    python harness.py --model jev --cond all --rep 1 --stage estimate
"""
import argparse
import asyncio
import datetime as dt
import hashlib
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
SHARED = os.path.dirname(HERE)
INPUTS = os.environ.get("P4_INPUTS", os.path.join(SHARED, "colab", "inputs"))
ANSWERS = os.environ.get("P4_ANSWERS", os.path.join(SHARED, "answers"))
PRICE_PER_MTOK = 0.042          # USD per million input tokens for Jev, accessed 2026-09-24
SPEND_TRIPWIRE = float(os.environ.get("P4_SPEND_TRIPWIRE", "20.0"))

BACKENDS = {}


def register(name, factory):
    BACKENDS[name] = factory


# ------------------------------------------------------------------ io

def load_inputs(cond):
    path = os.path.join(INPUTS, f"{cond}.jsonl")
    with open(path, encoding="utf-8") as fh:
        return [json.loads(l) for l in fh if l.strip()]


def all_conditions():
    man = json.load(open(os.path.join(INPUTS, "manifest.json"), encoding="utf-8"))
    return [c for c in man if not c.startswith("_")]


def out_path(model_tag, cond, rep):
    d = os.path.join(ANSWERS, model_tag)
    os.makedirs(d, exist_ok=True)
    return os.path.join(d, f"{cond}__rep{rep}.jsonl")


def done_keys(path):
    keys = set()
    if os.path.exists(path):
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                try:
                    j = json.loads(line)
                    if not j.get("error"):
                        keys.add(j["key"])
                except (json.JSONDecodeError, KeyError):
                    continue
    return keys


def request_hash(rec):
    body = json.dumps({"state": rec["state"], "questions": rec["questions"]},
                      ensure_ascii=False)
    return hashlib.sha256(body.encode("utf-8")).hexdigest()[:16]


# ------------------------------------------------------------------ normalization

def normalize_answer(q, a):
    """Map one answer object in the System One response shape to option probabilities."""
    t = q["type"]
    if t == "noul":
        p = a.get("noul")
        if p is None and "probabilities" in a:
            pr = a["probabilities"]
            p = pr.get("true", pr.get("yes"))
        p = float(p)
        return {"false": 1.0 - p, "true": p}
    if t == "score":
        pr = a["probabilities"]
        return {str(k): float(v) for k, v in pr.items()}
    pr = a["probabilities"]
    return {str(k): float(v) for k, v in pr.items()}


def normalize_response(questions, answers):
    out = {}
    for qid, q in questions.items():
        a = answers.get(qid)
        if a is None:
            out[qid] = {"probs": None, "raw": None}
            continue
        out[qid] = {"probs": normalize_answer(q, a), "raw": a}
    return out


# ------------------------------------------------------------------ backends

class JevBackend:
    """TypeSafe API. The alias jev-latest moves, so the version is always pinned."""
    tag = "jev-1.13.0"
    revision = "jev-1.13.0"
    served_temperature = None
    concurrency = 10

    def __init__(self, model="jev-1.13.0"):
        from dotenv import load_dotenv
        load_dotenv(os.path.join(os.path.dirname(os.path.dirname(SHARED)), ".env"))
        self.model = model
        self.tag = model
        self.revision = model

    async def __aenter__(self):
        from typesafe_sdk import AsyncTypeSafeClient
        self.client = AsyncTypeSafeClient(timeout=90)
        await self.client.__aenter__()
        return self

    async def __aexit__(self, *a):
        await self.client.__aexit__(*a)

    async def answer(self, rec):
        r = await self.client.system_one(state=rec["state"], questions=rec["questions"],
                                         model=self.model)
        d = r.model_dump() if hasattr(r, "model_dump") else dict(r)
        answers = d["answers"]
        answers = {k: (v if isinstance(v, dict) else dict(v)) for k, v in answers.items()}
        return {"model_returned": d.get("model"),
                "usage_in": d["usage"]["input_tokens"] if d.get("usage") else None,
                "answers": normalize_response(rec["questions"], answers)}


class SystemOneHTTP:
    """Any local server that implements POST /v1/systemone (laya-serve, kev.serve,
    decider.serve). The caller supplies the tag, revision and served temperature."""
    concurrency = 1

    def __init__(self, base_url, tag, revision, served_temperature=None, model=None,
                 concurrency=1):
        self.base_url = base_url.rstrip("/")
        self.tag, self.revision = tag, revision
        self.served_temperature = served_temperature
        self.model = model
        self.concurrency = concurrency

    async def __aenter__(self):
        import httpx
        self.client = httpx.AsyncClient(timeout=300)
        return self

    async def __aexit__(self, *a):
        await self.client.aclose()

    async def answer(self, rec):
        body = {"state": rec["state"], "questions": rec["questions"]}
        if self.model:
            body["model"] = self.model
        r = await self.client.post(f"{self.base_url}/v1/systemone", json=body)
        r.raise_for_status()
        d = r.json()
        return {"model_returned": d.get("model"),
                "usage_in": (d.get("usage") or {}).get("input_tokens"),
                "answers": normalize_response(rec["questions"], d["answers"])}


register("jev", lambda **kw: JevBackend(**kw))


# ------------------------------------------------------------------ runner

async def run(backend, cond, rep, limit=None, only_keys=None):
    recs = load_inputs(cond)
    if only_keys is not None:
        recs = [r for r in recs if r["item_id"] in only_keys]
    if limit:
        recs = recs[:limit]
    path = out_path(backend.tag, cond, rep)
    have = done_keys(path)
    todo = [r for r in recs if r["key"] not in have]
    print(f"[{backend.tag} {cond} rep{rep}] {len(todo)} to run, {len(have)} cached",
          flush=True)
    if not todo:
        return path
    sem = asyncio.Semaphore(getattr(backend, "concurrency", 1))
    lock = asyncio.Lock()
    stats = {"n": 0, "err": 0, "tok": 0}
    t0 = time.time()
    run_date = dt.date.today().isoformat()
    fh = open(path, "a", encoding="utf-8")

    async def one(rec):
        async with sem:
            last = None
            for attempt in range(7):
                try:
                    st = time.perf_counter()
                    out = await backend.answer(rec)
                    lat = time.perf_counter() - st
                    line = {"key": rec["key"], "condition": cond, "rep": rep,
                            "model": backend.tag, "revision": backend.revision,
                            "model_returned": out.get("model_returned"),
                            "served_temperature": backend.served_temperature,
                            "run_date": run_date, "latency_s": round(lat, 4),
                            "usage_in": out.get("usage_in"),
                            "request_hash": request_hash(rec),
                            "answers": out["answers"]}
                    async with lock:
                        fh.write(json.dumps(line, ensure_ascii=False) + "\n")
                        # HOOK (adapters.py, documented in its module docstring): flush every
                        # line, not every 200. The Colab notebook writes answers straight to a
                        # mounted Drive folder so a disconnect costs nothing; that only holds if
                        # each line is actually on disk before the next request starts.
                        fh.flush()
                        stats["n"] += 1
                        stats["tok"] += out.get("usage_in") or 0
                        if stats["n"] % 200 == 0:
                            cost = stats["tok"] * PRICE_PER_MTOK / 1e6
                            print(f"  {stats['n']}/{len(todo)} {time.time() - t0:.0f}s "
                                  f"tokens {stats['tok']} ${cost:.3f}", flush=True)
                    return
                except Exception as e:          # noqa: BLE001, retried or recorded
                    last = repr(e)
                    if any(t in last for t in ("429", "529", "502", "503", "Timeout",
                                               "Connect", "RemoteProtocol")):
                        await asyncio.sleep(min(2 ** attempt, 30))
                        continue
                    break
            async with lock:
                stats["err"] += 1
                fh.write(json.dumps({"key": rec["key"], "condition": cond, "rep": rep,
                                     "model": backend.tag, "error": last[:500]}) + "\n")
                fh.flush()   # HOOK (adapters.py): same every-line-flush reasoning as the ok path
                if stats["err"] <= 3:
                    print(f"  ERR {rec['key']}: {last[:200]}", flush=True)

    async with backend:
        # chunks keep the spend tripwire effective within one condition
        for i in range(0, len(todo), 500):
            chunk = todo[i:i + 500]
            # HOOK (adapters.py, documented in its module docstring): a backend that wants to
            # batch a whole chunk through one call (comparator-open's vLLM offline LLM.generate)
            # may define an async prefetch(records) that fills its own cache; answer(rec) then
            # just looks the result up. Backends without prefetch are unaffected.
            prefetch = getattr(backend, "prefetch", None)
            if prefetch is not None:
                await prefetch(chunk)
            await asyncio.gather(*(one(r) for r in chunk))
            spent = spend_so_far()
            if spent > SPEND_TRIPWIRE:
                print(f"SPEND TRIPWIRE: ${spent:.2f} > ${SPEND_TRIPWIRE}", flush=True)
                break
    fh.close()
    cost = stats["tok"] * PRICE_PER_MTOK / 1e6
    print(f"[{backend.tag} {cond} rep{rep}] done {stats['n']} ok, {stats['err']} errors, "
          f"{time.time() - t0:.0f}s, tokens {stats['tok']} (${cost:.3f} at Jev price)",
          flush=True)
    return path


def spend_so_far():
    """Jev spend across every Jev answer file, from recorded usage."""
    tok = 0
    d = os.path.join(ANSWERS)
    if not os.path.isdir(d):
        return 0.0
    for tag in os.listdir(d):
        if not tag.startswith("jev"):
            continue
        for fn in os.listdir(os.path.join(d, tag)):
            with open(os.path.join(d, tag, fn), encoding="utf-8") as fh:
                for line in fh:
                    try:
                        tok += json.loads(line).get("usage_in") or 0
                    except json.JSONDecodeError:
                        pass
    return tok * PRICE_PER_MTOK / 1e6


def estimate(conds, reps):
    """Rough Jev cost before anything is sent: characters / 3.5 as tokens."""
    tot_tok = 0
    for c in conds:
        for r in load_inputs(c):
            body = json.dumps({"state": r["state"], "questions": r["questions"]})
            tot_tok += len(body) / 3.5
    print(f"{len(conds)} conditions x {reps} repeats ~ {tot_tok * reps / 1e6:.2f} M tokens"
          f" ~ ${tot_tok * reps * PRICE_PER_MTOK / 1e6:.2f} at the Jev price")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--cond", required=True, help="condition name, comma list, or all")
    ap.add_argument("--rep", type=int, default=1)
    ap.add_argument("--limit", type=int)
    ap.add_argument("--retest", action="store_true",
                    help="only the 40-state test-retest subset of d1_neutral")
    ap.add_argument("--stage", default="run", choices=["run", "estimate"])
    a = ap.parse_args()
    conds = all_conditions() if a.cond == "all" else a.cond.split(",")
    if a.stage == "estimate":
        estimate(conds, a.rep)
        return
    only = None
    if a.retest:
        man = json.load(open(os.path.join(INPUTS, "manifest.json"), encoding="utf-8"))
        only = set(man["_retest_subset"]["item_ids"])
    try:
        import adapters  # noqa: F401  registers the open-model backends
    except ImportError:
        pass
    backend = BACKENDS[a.model]()
    for c in conds:
        asyncio.run(run(backend, c, a.rep, a.limit, only))


if __name__ == "__main__":
    sys.exit(main())
