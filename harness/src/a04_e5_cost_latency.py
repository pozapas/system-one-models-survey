"""E5: latency and cost per thousand decisions, with the hardware or provider stated.

Latency is wall-clock time per request as recorded by the harness: for the hosted
model it is the client-side time of one API call (concurrency 10 in flight, so it
includes network and any server queueing); for the open models it is one request
at a time on the Colab GPU named in run_log.json. The two are reported side by side
and never ratioed, because the hardware and the network path differ.

Cost per thousand decisions:
    hosted model       recorded input tokens x the published price per token
                       (output tokens are free), divided by decisions
    open models        GPU time per decision x an hourly price for that GPU, stated
                       as an assumption (Colab compute units), batch size one
    open comparator    same as open models, with batched generation

Output: results/cost_latency.json
"""
import json
import os

import numpy as np

import bench
import common as C

CONDS = ["d1_neutral", "d2_k150", "d2_k5", "d2_k20", "d3_conv_go_awry", "d3_wiki_corpus",
         "d3_emotion", "d3_wiki_politeness"]
MODELS = [bench.JEV] + bench.MODELS_OPEN + ["comparator-open"]
# Assumptions, stated in the manuscript. Colab Pro sells 100 compute units for
# 9.99 USD; the L4 runtime draws the rate recorded in run_log.json, else 4.8 units/h.
USD_PER_UNIT = 9.99 / 100
UNITS_PER_HOUR_DEFAULT = 4.8


def run_log():
    p = os.path.join(C.ANSWERS, "run_log.json")
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {}


def main():
    log = run_log()
    units = log.get("units_per_hour", UNITS_PER_HOUR_DEFAULT)
    usd_per_hour = units * USD_PER_UNIT
    res = {"assumptions": {"usd_per_compute_unit": USD_PER_UNIT,
                           "l4_units_per_hour": units, "usd_per_gpu_hour": usd_per_hour,
                           "jev_usd_per_mtok_input": C.PRICE_PER_MTOK,
                           "gpu": log.get("gpu_name")}}
    for m in MODELS:
        mres = {}
        for cond in CONDS:
            if not bench.available_reps(m, cond):
                continue
            ans = bench.answers(m, cond, 1)
            if not ans:
                continue
            batched = m == "comparator-open"
            if batched:
                # vLLM generates a whole chunk at once; each request's share of the chunk's
                # wall time is batch_wall_s / n_requests, summed over its questions
                lat = np.array([sum(q["raw"]["batch_wall_s"] / q["raw"]["n_requests"]
                                    for q in a["answers"].values()) for a in ans.values()])
            else:
                lat = np.array([a["latency_s"] for a in ans.values() if a.get("latency_s")])
            n_dec = sum(len(a["answers"]) for a in ans.values())
            tok = [a.get("usage_in") for a in ans.values() if a.get("usage_in")]
            d = {"requests": len(ans), "decisions": n_dec,
                 "p50_s": float(np.percentile(lat, 50)), "p95_s": float(np.percentile(lat, 95)),
                 "mean_s": float(lat.mean())}
            if tok:
                d["input_tokens_per_decision"] = float(np.sum(tok) / n_dec)
            if m == bench.JEV:
                d["usd_per_1000_decisions"] = float(np.sum(tok) * C.PRICE_PER_MTOK / 1e6
                                                    / n_dec * 1000)
                d["basis"] = "recorded input tokens x 0.042 USD per million"
            else:
                gpu_s = float(lat.sum())
                d["usd_per_1000_decisions"] = gpu_s / 3600 * usd_per_hour / n_dec * 1000
                d["basis"] = (f"GPU seconds x {usd_per_hour:.3f} USD per hour "
                              "(Colab compute units), "
                              + ("batched generation, time amortized per request" if batched
                                 else "one request at a time"))
                d["latency_mode"] = "batched_amortized" if batched else "single_request"
            mres[cond] = d
        if mres:
            res[m] = mres
            print(m, {c: (round(v["p50_s"], 3), round(v.get("usd_per_1000_decisions", -1), 5))
                      for c, v in mres.items()}, flush=True)
    # total Jev spend across every answer file
    tok = 0
    d = os.path.join(C.ANSWERS, bench.JEV)
    for fn in os.listdir(d):
        with open(os.path.join(d, fn), encoding="utf-8") as fh:
            for line in fh:
                j = json.loads(line)
                tok += j.get("usage_in") or 0
    res["jev_total"] = {"input_tokens": tok, "usd": tok * C.PRICE_PER_MTOK / 1e6}
    print("Jev total", res["jev_total"])
    C.dump(res, "cost_latency.json")


if __name__ == "__main__":
    main()
