"""Async Jev runner shared by every new experiment in this paper.

Differences from the pilot runners, both deliberate. The model is pinned
explicitly rather than left to the `jev-latest` alias, and the model identifier
returned by the service is written into every record, so the manuscript can state
which version produced which number instead of asserting it.

Every output file is append-only JSONL keyed by a caller-supplied key, so an
interrupted run resumes without repeating work or spending twice.
"""
import asyncio
import json
import os
import time

from dotenv import load_dotenv

import common as C

load_dotenv(os.path.join(C.BASE, ".env"))

RAW = os.path.join(C.RESULTS, "raw")


def done_keys(path):
    keys = set()
    if os.path.exists(path):
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    keys.add(json.loads(line)["key"])
                except (json.JSONDecodeError, KeyError):
                    continue
    return keys


async def run_batch(items, questions, out_name, extract, concurrency=10,
                    model=C.MODEL, label=None):
    """items: list of (key, state_dict). extract: (response) -> dict of answers.

    Returns the path written. Rows already present in the file are skipped.
    """
    from typesafe_sdk import AsyncTypeSafeClient

    os.makedirs(RAW, exist_ok=True)
    path = os.path.join(RAW, out_name)
    have = done_keys(path)
    todo = [(k, s) for k, s in items if k not in have]
    label = label or out_name
    print(f"[{label}] {len(todo)} to run, {len(have)} cached, model={model}", flush=True)
    if not todo:
        return path

    sem = asyncio.Semaphore(concurrency)
    lock = asyncio.Lock()
    fh = open(path, "a", encoding="utf-8")
    n, errs, toks = 0, 0, []
    t0 = time.time()

    async with AsyncTypeSafeClient(timeout=60) as client:
        async def one(key, state):
            nonlocal n, errs
            async with sem:
                for attempt in range(6):
                    try:
                        st = time.time()
                        r = await client.system_one(state=state, questions=questions,
                                                    model=model)
                        rec = {"key": key, "model": getattr(r, "model", None),
                               "latency_s": round(time.time() - st, 3),
                               "usage": r.usage.input_tokens}
                        rec.update(extract(r))
                        async with lock:
                            fh.write(json.dumps(rec) + "\n")
                            n += 1
                            toks.append(r.usage.input_tokens)
                            if n % 500 == 0:
                                fh.flush()
                                print(f"  [{label}] {n}/{len(todo)} "
                                      f"{time.time() - t0:.0f}s", flush=True)
                        return
                    except Exception as e:
                        msg = repr(e)
                        if any(t in msg for t in ("429", "529", "Timeout", "Connection")):
                            await asyncio.sleep(min(2 ** attempt, 30))
                            continue
                        async with lock:
                            errs += 1
                            if errs <= 3:
                                print(f"  [{label}] ERR {msg[:180]}", flush=True)
                        return
                async with lock:
                    errs += 1

        await asyncio.gather(*(one(k, s) for k, s in todo))

    fh.close()
    cost = sum(toks) * C.PRICE_PER_MTOK / 1e6
    print(f"[{label}] done {n} ok, {errs} errors, {time.time() - t0:.0f}s, "
          f"${cost:.3f}", flush=True)
    return path


def load_jsonl(name):
    path = os.path.join(RAW, name)
    out = {}
    if not os.path.exists(path):
        return out
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            j = json.loads(line)
            out[j["key"]] = j
    return out
