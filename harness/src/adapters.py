"""In-process (and one subprocess-free, one HTTP-served) backends for the open decision models.

Registers with harness.register() so `python harness.py --model <tag> --cond ...` works exactly
like the Jev backend. Import this module lazily (harness.main() does `import adapters` inside a
try/except ImportError) -- so THIS FILE MUST NOT IMPORT TORCH, TRANSFORMERS, LAYA, KEV, DECIDER,
THISTHAT OR VLLM AT MODULE SCOPE. Every backend below defers those imports to __aenter__ (or to a
worker thread/process invoked from __aenter__), so `import adapters` succeeds in any uv env
regardless of which of these packages that env actually has installed; only asking harness.py to
run a *specific* --model requires that model's dependency to be present.

Documented hooks this module relies on in harness.py (see harness.py's run(); both are backward
compatible -- a backend that does not use them behaves exactly as it did before this file existed):

  1. Every JSONL line is flushed to disk immediately, not every 200. The Colab notebook writes
     answers straight into a mounted Drive folder specifically so a disconnect costs nothing; that
     guarantee only holds if a line is actually on disk before the next request starts.
  2. Before each up-to-500-record chunk, run() calls `await backend.prefetch(chunk)` if the
     backend defines `prefetch`. comparator-open's backend uses this to run one vLLM
     `LLM.generate()` call over the whole chunk (`--stage`/batched inference) instead of one
     `generate()` per request; `answer()` then just looks its record up in the cache prefetch
     filled. Backends without `prefetch` (everything except comparator-open) are unaffected.

Precision convention. Every backend returns, per question id,

    {"probs": {option_key: p, ...}, "raw": {...}}

"probs" is always the model's *as-served* distribution -- the temperature it ships with, applied
the way its own code applies it -- at full float precision. Several of these projects round their
own wire-format probabilities to 4 decimal places before returning them (Laya's `agent.predict`,
decider's `system_one`, Kev's `kev.api.to_answers` / `kev.serve` all do this, `kev/api.py`'s
`round_prob` says so explicitly: "4 decimals keeps the sum ... within TypeSafe's tolerance"). This
module routes around that rounding case by case (documented in each backend below) rather than
serializing through the model's own wire format, because the task requires full float precision
with no rounding.

"raw" always carries "served_temperature" and "probs_t1" (the T=1, i.e. un-tempered, distribution)
at the same full precision, plus whatever native fields the model's own answer object provides.
Where a second forward pass is not needed to get both distributions, this module does not run one:
softmax is scale invariant to an additive shift, so if p_T = softmax(z / T) is known at full
precision for one T, the distribution at any other temperature T' is recoverable exactly (not
approximately) as

    p_T' = normalize(p_T ** (T / T'))

(derivation: p_T,i = exp(z_i/T) / sum_j exp(z_j/T); write exp(z_i) = p_1,i * S with S = sum_j
exp(z_j) constant over i; then exp(z_i/T) = p_1,i^(1/T) * S^(1/T), and S^(1/T) cancels in the
softmax's normalization, giving p_T ∝ p_1^(1/T), i.e. p_1 = normalize(p_T ** T); the general form
follows by applying this twice). `_pow_normalize` below implements this. It is used for Laya
(recovering pre-bucket-temperature probabilities), Kev (recovering the served, at-T probabilities
from a single T=1 forward pass) and decider (recovering T=1 choice/noul probabilities, and, per
isolated Score level, the T=1 "does this level fit" probability before recombining levels).

Idempotent loading. harness.main() builds one backend instance per --model invocation, but
harness.run() is called once per --cond entry (once per condition; `--cond all` means once per
condition in manifest.json, i.e. ~24 times) and every call does `async with backend:`. A naive
__aenter__ would therefore reload a checkpoint once per condition. Every backend below loads once
(a `self._loaded` guard) and __aexit__ is a no-op; the process exits (or the notebook cell moves
to the next model, in its own subprocess/uv env) to free the GPU.
"""
import asyncio
import json
import math
import os
import sys

# harness.py's own CLI runs it as __main__ and does `import adapters` from inside main(). A plain
# `import harness` here would then import harness.py a SECOND time under the module name
# "harness", re-executing its top level and creating an independent BACKENDS = {} dict that our
# register() calls below would fill -- while main() keeps reading its own __main__-scoped
# BACKENDS, which would then only ever contain "jev". (Verified: running `python harness.py
# --model laya-en ...` raised KeyError('laya-en') from BACKENDS[a.model] for exactly this reason.)
# Reusing whichever module object is already the running harness.py -- sys.modules["harness"] if
# it was imported normally, sys.modules["__main__"] if harness.py itself is the running script --
# avoids the double import and its split-BACKENDS bug without changing harness.py. The __main__
# check requires BACKENDS/register to already be defined there (true once main() reaches its
# `import adapters` line, since that is after harness.py's whole module body has run) so that
# importing adapters.py from an unrelated script (test_adapters.py, a notebook cell) still falls
# through to a plain, correct `import harness` instead of mistaking that script's own __main__ for
# harness.py.
_main = sys.modules.get("__main__")
if "harness" in sys.modules:
    harness = sys.modules["harness"]
elif _main is not None and hasattr(_main, "BACKENDS") and hasattr(_main, "register"):
    harness = _main
else:
    import harness

# ---------------------------------------------------------------------- shared helpers


def _txt(v):
    """Render an option/instructions value that may be a string or any JSON value, the same
    convention every one of these wire formats uses (decider's systemone._txt, kev's api.render)."""
    return v if isinstance(v, str) else json.dumps(v, ensure_ascii=False)


def _state_text(state):
    """A JSON state rendered compactly; a string state passed through unchanged (this-that and
    Nimble need a single context string; Laya, Kev and decider accept the raw JSON state)."""
    return state if isinstance(state, str) else json.dumps(state, ensure_ascii=False)


def _pow_normalize(p, exponent):
    """{key: p ** exponent}, renormalized -- see the module docstring for the exact identity this
    implements. `p` values are cast to float first; a genuine 0 stays 0 for any positive
    exponent."""
    ex = {k: (float(v) ** exponent if v > 0 else 0.0) for k, v in p.items()}
    s = sum(ex.values())
    if s <= 0:
        n = len(ex) or 1
        return {k: 1.0 / n for k in ex}
    return {k: v / s for k, v in ex.items()}


def wire_keys(qtype, criteria):
    """The option keys a question's probabilities are reported under, in option order: the
    criteria names (choice), ["false", "true"] (noul), the level indices as strings (score). Pure
    function (no model import) so test_adapters.py can check it directly; mirrors kev/api.py's
    `question_keys` and decider/systemone.py's `render_question` name lists, which every adapter
    below must agree with since the freeze files define option order by dict/list insertion order.
    """
    if qtype == "choice":
        return list(criteria)
    if qtype == "noul":
        return ["false", "true"]
    if qtype == "score":
        return [str(i) for i in range(len(criteria))]
    raise ValueError(f"unknown question type {qtype!r}")


def noul_criteria(q):
    """{"false": ..., "true": ...}, defaulting to plain "No."/"Yes." the way harness.py's
    JevBackend and every one of these model cards do when a noul question ships no criteria."""
    c = q.get("criteria") or {}
    return {"false": c.get("false", "No."), "true": c.get("true", "Yes.")}


async def _run_sync(fn, *a, **kw):
    """Run a blocking (CPU/GPU) call off the event loop. Every backend's forward pass is
    synchronous torch code; concurrency=1 on all of them (one loaded model, one GPU) so this just
    keeps the loop responsive between requests, not real parallelism."""
    loop = asyncio.get_event_loop()
    if kw:
        import functools
        fn = functools.partial(fn, **kw)
    return await loop.run_in_executor(None, fn, *a)


def _pinned_revisions():
    """{repo: commit sha} from the P4_REVISIONS environment variable (a JSON object), or {}.
    The revision runs set it so every open model loads the exact commit the original answers
    record in their "revision" field; without it the current head is resolved, as before."""
    raw = os.environ.get("P4_REVISIONS")
    return json.loads(raw) if raw else {}


def _model_sha(repo, revision=None):
    pinned = _pinned_revisions().get(repo)
    if pinned and revision is None:
        return pinned
    import huggingface_hub as hh
    return hh.model_info(repo, revision=revision).sha


# ---------------------------------------------------------------------- Laya (english / multilingual)

LAYA_REPO = "convaiinnovations/laya"


class LayaBackend:
    """convaiinnovations/laya, root checkpoint (English) or subfolder="multilingual".

    laya.load()/laya.agent.Agent() take no `revision` kwarg (verified against laya 0.3.20's
    source: Agent.__init__ calls `snapshot_download(model_id_or_path, **kw)` with no revision in
    `kw`). To pin the checkpoint anyway (the task requires it, and "not the Router" -- we use
    laya.load()'s single-checkpoint path, never laya.Router), we pre-resolve the pinned commit's
    snapshot ourselves with huggingface_hub.snapshot_download(repo, revision=sha, ...) and hand
    Agent() the resulting local directory; Agent() only downloads when its first argument is not
    an existing path, so a local directory is used exactly as given (agent.py's `if subfolder:
    model_dir = os.path.join(model_dir, subfolder)` still runs, so subfolder selection works the
    same as with a hub id).

    Precision: laya/agent.py's `_decode_answers` rounds every probability, score and confidence to
    4 decimal places with a bare `round(...)` call (agent.py lines ~675-703) before returning it.
    That name resolves at call time against the *module's* globals (LEGB), so assigning
    `laya.agent.round = <identity>` once, before the first predict(), makes every later call in
    that module skip rounding -- the temperature-bucket lookup, masking and softmax it wraps are
    completely untouched, only the final `round(x, 4)` becomes `x`. This is verified in the smoke
    test: the unrounded probabilities agree with `agent.predict()`'s normal (rounded) output to
    within 5e-5 on the same input.

    Laya ships one temperature per (question type, option-count) bucket rather than one scalar
    (`agent.temperature_by_options`, falling back to `agent.temperature[qtype]`; see
    laya/common.py's `temp_bucket`). `served_temperature` on the backend is therefore the
    sentinel 1.0 the task allows ("the temperature the model applies by default, or 1.0"); the
    exact bucket temperature actually used for each question is in that answer's
    raw["served_temperature_bucket"], and the whole map is in raw["temperature_buckets"].
    `head_max_len` and `max_len` (the option/state token budget the model card calls out as the
    source of high-K truncation) are recorded in raw on every answer, as the task asks.
    """

    concurrency = 1

    def __init__(self, subfolder=None, tag=None):
        self.subfolder = subfolder
        self.tag = tag or ("laya-ml" if subfolder else "laya-en")
        self._loaded = False

    async def __aenter__(self):
        if not self._loaded:
            await _run_sync(self._load)
            self._loaded = True
        return self

    async def __aexit__(self, *a):
        return None

    def _load(self):
        os.environ.setdefault("USE_TF", "0")
        import huggingface_hub as hh

        self.revision = _model_sha(LAYA_REPO)   # head, or the P4_REVISIONS pin when set
        prefix = f"{self.subfolder}/" if self.subfolder else ""
        local_dir = hh.snapshot_download(
            LAYA_REPO, revision=self.revision,
            allow_patterns=[prefix + p for p in
                            ("rl_agent_config.json", "model.safetensors", "tokenizer/*", "encoder/*")])

        import laya
        import laya.agent as _agent_mod
        if not getattr(_agent_mod, "_p4_unrounded", False):
            _agent_mod.round = lambda x, ndigits=None: x   # see class docstring
            _agent_mod._p4_unrounded = True
        from laya.common import QTYPES, temp_bucket
        self._QTYPES, self._temp_bucket = QTYPES, temp_bucket

        self.agent = laya.load(local_dir, subfolder=self.subfolder)
        self.served_temperature = 1.0
        self._temp_map = {"by_option_count": dict(self.agent.temperature_by_options),
                          "by_type": list(self.agent.temperature)}
        self._cfg = {"head_max_len": self.agent.cfg.get("head_max_len"),
                    "max_len": self.agent.cfg.get("max_len")}

    def _t_scale(self, qtype, k):
        bucket = self._temp_bucket(self._QTYPES[qtype], k)
        return self._temp_map["by_option_count"].get(bucket, self._temp_map["by_type"][self._QTYPES[qtype]])

    async def answer(self, rec):
        result = await _run_sync(self.agent.predict, rec["state"], rec["questions"])
        answers = harness.normalize_response(rec["questions"], result["answers"])
        out = {}
        for qid, a in answers.items():
            q = rec["questions"][qid]
            k = len(q["criteria"]) if q["type"] != "noul" else 2
            t = self._t_scale(q["type"], k)
            native = result["answers"][qid]
            raw = {"served_temperature_bucket": t, "temperature_buckets": self._temp_map,
                  "head_max_len": self._cfg["head_max_len"], "max_len": self._cfg["max_len"],
                  "native": native}
            probs = a["probs"] if a["probs"] is not None else None
            raw["probs_t1"] = _pow_normalize(probs, t) if probs is not None else None
            out[qid] = {"probs": probs, "raw": raw}
        return {"model_returned": result.get("model"),
               "usage_in": (result.get("usage") or {}).get("input_tokens"),
               "answers": out}


harness.register("laya-en", lambda **kw: LayaBackend(subfolder=None, tag="laya-en", **kw))
harness.register("laya-ml", lambda **kw: LayaBackend(subfolder="multilingual", tag="laya-ml", **kw))


# ---------------------------------------------------------------------- Kev (0.8b / 9b)

KEV_REPOS = {"kev-0.8b": "jaredpalmer/kev-0.8b", "kev-9b": "jaredpalmer/kev-9b"}
KEV_GITHUB_COMMIT = "73504e51f6ce2ade19c7819d4a5f2d84363cd40f"   # jaredpalmer/kev@main, resolved 2026-09-24


class KevBackend:
    """jaredpalmer/kev-0.8b or -9b: a LoRA + pointer head on Qwen3.5, served at a built-in
    temperature read from the checkpoint itself (kev.checkpoint.Meta.temperature, head.pt), never
    hard-coded here: the model card's published figures (T=2.41 for 0.8B, 2.30 for 9B) are a
    snapshot, and the actual served value can move with the checkpoint -- confirmed on this
    laptop, where the current kev-0.8b weights read T=2.3510958125672174, not the card's 2.41.
    `self.served_temperature = float(self.model.head.temperature)` below is always the live value.

    Uses kev's in-process loader (kev.checkpoint.Checkpoint, per the task: "use its in-process
    loader if one exists") rather than starting `python -m kev.serve` as a subprocess: kev.serve's
    /v1/systemone response goes through kev.api.to_answers -> round_prob, which rounds every
    probability to 4 decimals (kev/api.py: "Serialization precision ... 4 decimals keeps the sum
    ... within TypeSafe's tolerance"), so the HTTP path cannot give full precision no matter what
    temperature it is asked to serve at.

    Precision and both temperatures from one forward pass. `PointerHead.forward`/`.many` (kev/model.py)
    skip the temperature division entirely when `self.temperature == 1.0`: `z if ... or
    self.temperature == 1.0 else z / self.temperature`. So temporarily setting
    `model.head.temperature = 1.0` and calling `model.probs(enc)` returns `softmax(z)` -- the
    model's own T=1 distribution, at full float32 precision, with no rounding anywhere in the
    path (we never call kev.api.to_answers). The as-served distribution at the checkpoint's own
    temperature T is then recovered exactly (not approximately) from that single T=1 result via
    the power-transform identity in the module docstring: p_T = normalize(p_1 ** (1/T)). This
    means one forward pass gives both distributions at full precision, which both satisfies "do
    not run the whole benchmark twice" and improves on running the served endpoint once and a
    KEV_TEMPERATURE=1.0 server a second time (that alternative would still round both).

    CUDA graphs and the fused Qwen3.5 kernels are both declined (LoadOptions(cuda_graphs=False,
    fused=False)): kev.serve turns both on by default for throughput, but a captured CUDA graph
    bakes in whatever `model.head.temperature` was at *capture* time -- toggling the Python
    attribute between calls would silently stop affecting a replayed graph. Eager mode is exact
    and this backend is not batching (concurrency=1, one request at a time), so the throughput
    cost is the right trade for correctness.
    """

    concurrency = 1

    def __init__(self, tag):
        self.tag = tag
        self.repo = KEV_REPOS[tag]
        self._loaded = False

    async def __aenter__(self):
        if not self._loaded:
            await _run_sync(self._load)
            self._loaded = True
        return self

    async def __aexit__(self, *a):
        return None

    def _load(self):
        import torch
        from kev.checkpoint import Checkpoint, LoadOptions

        self.revision = _model_sha(self.repo)
        ck = Checkpoint(f"{self.repo}@{self.revision}")
        device = "cuda" if torch.cuda.is_available() else "cpu"
        dtype = torch.bfloat16 if device == "cuda" else torch.float32
        opts = LoadOptions(dtype=dtype, cuda_graphs=False, fused=False)
        self.tok, self.model = ck.load(device, opts)
        self.device = device
        self.served_temperature = float(self.model.head.temperature)

    async def answer(self, rec):
        from kev.api import SystemOneRequest, to_record
        from kev.model import SERVE_MAX_BRANCH, SERVE_MAX_STATE

        req = SystemOneRequest(state=rec["state"], questions=rec["questions"])
        internal_rec, meta = to_record(req)

        def _score():
            enc = self.model.encode(self.tok, internal_rec, max_state=SERVE_MAX_STATE,
                                    max_branch=SERVE_MAX_BRANCH)
            orig_T = self.model.head.temperature
            self.model.head.temperature = 1.0
            try:
                rows = self.model.probs(enc)
            finally:
                self.model.head.temperature = orig_T
            return rows, len(enc["ids"])

        rows, n_tok = await _run_sync(_score)
        T = self.served_temperature
        out = {}
        for row, m in zip(rows, meta):
            p1 = {k: float(v) for k, v in zip(m["keys"], row.tolist())}
            p_served = p1 if T == 1.0 else _pow_normalize(p1, 1.0 / T)
            raw = {"served_temperature": T, "probs_t1": p1,
                  "temperature_source": "kev.checkpoint.Meta.temperature (head.pt)"}
            if m["type"] == "score":
                raw["legend"] = m.get("legend")
            out[m["id"]] = {"probs": p_served, "raw": raw}
        return {"model_returned": self.tag, "usage_in": n_tok, "answers": out}


harness.register("kev-0.8b", lambda **kw: KevBackend("kev-0.8b", **kw))
harness.register("kev-9b", lambda **kw: KevBackend("kev-9b", **kw))


# ---------------------------------------------------------------------- decider-2b

DECIDER_REPO = "Mapika/decider-2b"


def isolated_score_t1(fit_served, T):
    """Given decider's per-level "fits" (P(this level fits), each an isolated yes/no row
    softmaxed at the served temperature T) and that same T, return the per-level fits a T=1
    forward pass would have produced. Each row is its own 2-option {no, yes} softmax, so the
    module's power-transform identity applies row by row: p_1(yes) = normalize(p_T ** T)[yes].
    Pure function (no decider import) so test_adapters.py can check it against hand-picked
    numbers; the caller still has to recombine the result with decider's own combine_isolated so
    the two code paths agree on everything except the fit values themselves."""
    return {k: _pow_normalize({"no": 1.0 - v, "yes": v}, T)["yes"] for k, v in fit_served.items()}


class DeciderBackend:
    """Mapika/decider-2b (v10), served at T=1.3 (decider_config.json's "temperature"), 
    "independent=True" (the default, and what we pass explicitly per the task).

    The bundled `decider/` package ships inside the model repo itself (see the model card's own
    usage snippet: "decider/ is included in this repo"), not on PyPI, so it is loaded by
    downloading a pinned snapshot and inserting that local directory onto sys.path -- this is also
    how the revision gets pinned, since decider.infer.Decider(path) takes a local path or an
    unpinned hub id, no revision kwarg.

    Precision. decider/systemone.py's `assemble()` calls `format_answer(rqs[k], probs[s])`, and
    `format_answer(rq, p, nd=4)` rounds every probability (and, for isolated Score levels, every
    per-level `level_fit`) to 4 decimals by default. `assemble` looks `format_answer` up as a bare
    module-global at call time, so reassigning `decider.systemone.format_answer` to
    `functools.partial(format_answer, nd=17)` (round to 17 decimals is a no-op for a float64/32
    value; there is no "don't round at all" switch) takes effect on every later `system_one()`
    call. `combine_isolated` and the certainty/confidence math are untouched.

    T=1 recovery. decider_config.json sets `isolated_levels: true`: a Score question's levels are
    each scored as an isolated yes/no row (its own softmax at T), and `combine_isolated` just
    ratio-normalizes those per-level "fit" values across levels -- that combination step is *not*
    itself a softmax, so the module's plain power-transform on the final Score distribution would
    not recover the correct T=1 Score distribution. `isolated_score_t1` above applies the
    power-transform to each isolated row first (which *is* exact, since each row is its own
    2-option softmax), then this backend recombines with decider's own `combine_isolated` so both
    the served and the T=1 Score distributions were produced by the identical combination logic.
    Choice and noul questions are plain softmaxes over their options, so the direct power-transform
    applies.
    """

    tag = "decider-2b"
    concurrency = 1

    def __init__(self):
        self._loaded = False

    async def __aenter__(self):
        if not self._loaded:
            await _run_sync(self._load)
            self._loaded = True
        return self

    async def __aexit__(self, *a):
        return None

    def _load(self):
        # decider/engine.py's Engine defaults to compile=True and decider/schema_engine.py
        # compiles per-schema graphs; both are skipped on CPU by passing use_graphs=False below,
        # but something else in the decider/transformers forward path still reaches
        # torch.compile's Inductor backend on a CPU-only machine with no Triton (observed:
        # "InductorError: AssertionError: Invalid device id"). These two env vars force
        # dynamo/inductor off process-wide. They must be set before `import torch` -- the very
        # first torch import in this process, since nothing before this point in harness.py or
        # adapters.py touches torch -- not merely before `import decider`: setting them after
        # `import torch` but before `import decider` was verified NOT to prevent the error, only
        # setting them before `import torch` itself did. They are set unconditionally, then
        # removed again if this turns out to be a CUDA machine (Colab), where decider's own
        # compile=True optimisations should run normally; on CUDA the corresponding branch below
        # never imports decider.* until after they are removed.
        _had = {v: v in os.environ for v in ("TORCHDYNAMO_DISABLE", "TORCH_COMPILE_DISABLE")}
        os.environ.setdefault("TORCHDYNAMO_DISABLE", "1")
        os.environ.setdefault("TORCH_COMPILE_DISABLE", "1")

        import sys
        import huggingface_hub as hh
        import torch

        # torch.compile and CUDA graphs stay off on every device (decision of the
        # coordinator): eager mode is slower but has no compile-time failure modes on an
        # unattended Colab run, and latency is reported with this setting stated.

        self.revision = _model_sha(DECIDER_REPO)
        local_dir = hh.snapshot_download(DECIDER_REPO, revision=self.revision)
        if local_dir not in sys.path:
            sys.path.insert(0, local_dir)

        import decider.systemone as _so
        if not getattr(_so, "_p4_unrounded", False):
            import functools
            _so.format_answer = functools.partial(_so.format_answer, nd=17)
            _so._p4_unrounded = True
        self._combine_isolated = _so.combine_isolated

        from decider.infer import Decider
        device = "cuda" if torch.cuda.is_available() else "cpu"
        dtype = torch.bfloat16 if device == "cuda" else torch.float32
        self.decider = Decider(local_dir, device=device, dtype=dtype, use_graphs=False)
        self.served_temperature = float(self.decider.T)

    async def answer(self, rec):
        def _score():
            return self.decider.system_one(rec["state"], rec["questions"], independent=True)

        result = await _run_sync(_score)
        answers, T = result["answers"], self.served_temperature
        out = {}
        for qid, q in rec["questions"].items():
            a = answers[qid]
            if q["type"] == "score" and "level_fit" in a:
                fit_served = {k: float(v) for k, v in a["level_fit"].items()}
                fit_t1 = isolated_score_t1(fit_served, T)
                order = sorted(fit_t1, key=int)
                p1_list, _mass = self._combine_isolated([fit_t1[k] for k in order])
                p1 = dict(zip(order, p1_list))
                probs_served = {k: float(v) for k, v in a["probabilities"].items()}
            elif q["type"] == "noul":
                probs_served = {"false": 1.0 - float(a["noul"]), "true": float(a["noul"])}
                p1 = _pow_normalize(probs_served, T)
            else:
                probs_served = {k: float(v) for k, v in a["probabilities"].items()}
                p1 = _pow_normalize(probs_served, T)
            out[qid] = {"probs": probs_served,
                       "raw": {"served_temperature": T, "probs_t1": p1, "native": a}}
        return {"model_returned": result.get("model"),
               "usage_in": (result.get("usage") or {}).get("input_tokens"),
               "answers": out}


harness.register("decider-2b", lambda **kw: DeciderBackend(**kw))


# ---------------------------------------------------------------------- this-that-1.0

THISTHAT_REPO = "flock-io/this-that-model-1.0"
THISTHAT_GITHUB_COMMIT = "542d445efa5f68b14bfbd1f8ed25aacd8379d839"   # FLock-io/this-that-model@main, resolved 2026-09-24


THISTHAT_RENDERS = ("keydesc", "desc", "key")


def thisthat_render(rec, render="keydesc"):
    """(state_text, [(qid, instructions, option_strings, option_keys), ...]) under the fixed
    rendering the task specifies for this model (it has no wire-format entry point -- see the
    backend's docstring). Pure function; test_adapters.py exercises it without importing thisthat.

    render selects how a choice option or a score level becomes the option string:
      "keydesc"  f"{key}: {description}"  (the original runs; the default, unchanged)
      "desc"     the description alone     (rendering-sensitivity condition)
      "key"      the key alone             (only informative where keys carry meaning, d1_native)
    noul questions are always ["no", "yes"], so a rendering change never touches them.
    """
    if render not in THISTHAT_RENDERS:
        raise ValueError(f"unknown this-that rendering {render!r}")

    def join(k, d):
        return {"keydesc": f"{k}: {d}", "desc": d, "key": str(k)}[render]

    state_text = _state_text(rec["state"])
    items = []
    for qid, q in rec["questions"].items():
        t = q["type"]
        if t == "choice":
            keys = list(q["criteria"])
            opts = [join(k, _txt(q["criteria"][k])) for k in keys]
        elif t == "noul":
            keys, opts = ["false", "true"], ["no", "yes"]
        elif t == "score":
            crit = q["criteria"]
            keys = [str(i) for i in range(len(crit))]
            opts = [join(i, _txt(c)) for i, c in enumerate(crit)]
        else:
            raise ValueError(f"unknown question type {t!r}")
        items.append((qid, q["instructions"], opts, keys))
    return state_text, items


class ThisThatBackend:
    """flock-io/this-that-model-1.0.

    TypedDecider exposes no system_one / wire-format entry point: checked against
    thisthat/server.py at the pinned GitHub commit (THISTHAT_GITHUB_COMMIT above) -- it serves an
    OpenAI-style /v1/chat/completions with the option set given as a response_format enum, not
    TypeSafe's {state, questions} shape, and thisthat/model.py's TypedDecider only has
    decide()/decide_batch(). So this backend uses the task's prescribed fallback rendering:
      - choice option string: f"{key}: {description}"
      - noul: options ["no", "yes"], answers mapped back to keys "false"/"true"
      - score option string: f"{i}: {level description}"
      - state: as-is if already a string, else json.dumps(state, ensure_ascii=False)

    No calibration file ships in the repo (its listing has no temperature_config.json, unlike
    Nimble's), and decide()'s own default is temperature=1.0, so that default *is* the served
    temperature; served and T=1 are identical here. thisthat/model.py never rounds
    Decision.probabilities (built as `tuple(x / total for x in p)` from a float32 softmax, no
    round() call in the module), so no precision hook is needed.
    """

    tag = "this-that-1.0"
    concurrency = 1

    def __init__(self, render="keydesc", tag="this-that-1.0"):
        # render: see thisthat_render. The tag carries the rendering, so answers under an
        # alternative rendering land in their own answers/<tag>/ folder (this-that-1.0-desc,
        # this-that-1.0-key) and never mix with the original this-that-1.0 files.
        self.render = render
        self.tag = tag
        self._loaded = False

    async def __aenter__(self):
        if not self._loaded:
            await _run_sync(self._load)
            self._loaded = True
        return self

    async def __aexit__(self, *a):
        return None

    def _load(self):
        import huggingface_hub as hh
        self.revision = _model_sha(THISTHAT_REPO)
        local_dir = hh.snapshot_download(THISTHAT_REPO, revision=self.revision)
        from thisthat import TypedDecider
        self.decider = TypedDecider.from_pretrained(local_dir)
        self.served_temperature = 1.0

    async def answer(self, rec):
        from thisthat import Question

        state_text, items = thisthat_render(rec, self.render)
        questions = [Question(instr, opts) for _, instr, opts, _ in items]

        def _score():
            # a list in, a list out (TypedDecider.decide only unwraps to a single Decision when
            # given a bare Question, never when given a list -- see thisthat/model.py:decide()),
            # so `decisions` is already aligned with `items` regardless of how many questions.
            return self.decider.decide(state_text, questions, temperature=1.0)

        decisions = await _run_sync(_score)
        out = {}
        for (qid, _instr, _opts, keys), d in zip(items, decisions):
            probs = {k: float(p) for k, p in zip(keys, d.probabilities)}
            out[qid] = {"probs": probs,
                       "raw": {"served_temperature": 1.0, "probs_t1": probs,
                               "choice": d.choice, "index": d.index,
                               **({"render": self.render} if self.render != "keydesc" else {})}}
        return {"model_returned": self.tag, "usage_in": None, "answers": out}


harness.register("this-that-1.0", lambda **kw: ThisThatBackend(**kw))
harness.register("this-that-1.0-desc",
                 lambda **kw: ThisThatBackend(render="desc", tag="this-that-1.0-desc", **kw))
harness.register("this-that-1.0-key",
                 lambda **kw: ThisThatBackend(render="key", tag="this-that-1.0-key", **kw))


# ---------------------------------------------------------------------- nimble-9b

NIMBLE_REPO = "bespokelabs/Bespoke-Nimble-9B"


def nimble_schema(questions):
    """(schema, score_fields) for inference.ParallelScorer.score(), per the task's mapping:
      noul   -> {"type": "boolean", "description": instructions}
      choice -> {"type": "enum", "choices": [keys], "description": instructions,
                 "choice_descriptions": {key: desc}}
      score  -> an integer-string enum ["0", ...] with level descriptions; the field name is
                listed in score_fields

    Field names checked against extended_schema.validate_schema (bespokelabs/Bespoke-Nimble-9B's
    own serving_schema.py, fetched at the pinned revision): "type" is "enum" or "boolean";
    "choices" is a list of distinct nonempty strings for "enum" (omitted for "boolean", which
    always means [False, True]); "choice_descriptions" is keyed by choice_key(value) -- "false"/
    "true" for a boolean field, the literal string for an enum field. Pure function, no
    torch/transformers import, so test_adapters.py exercises it directly.

    The question id is shown to the model as the schema's field name here (Nimble's
    prepare_prompts serialises {"name": name, "description": ..., "choices": [...]} verbatim into
    the prompt) -- unlike every other adapter in this module, where the qid never reaches the
    model. That is inherent to Nimble's one-JSON-object-keyed-by-field-name schema, so the freeze
    files' plain qids ("action", "risk", "intent", ...) are what this model reads; documented here
    since it is the one place that differs.
    """
    schema, score_fields = {}, []
    for qid, q in questions.items():
        t = q["type"]
        if t == "noul":
            schema[qid] = {"type": "boolean", "description": _txt(q["instructions"])}
        elif t == "choice":
            keys = list(q["criteria"])
            schema[qid] = {"type": "enum", "choices": keys, "description": _txt(q["instructions"]),
                           "choice_descriptions": {k: _txt(q["criteria"][k]) for k in keys}}
        elif t == "score":
            crit = q["criteria"]
            keys = [str(i) for i in range(len(crit))]
            schema[qid] = {"type": "enum", "choices": keys, "description": _txt(q["instructions"]),
                           "choice_descriptions": {str(i): _txt(c) for i, c in enumerate(crit)}}
            score_fields.append(qid)
        else:
            raise ValueError(f"unknown question type {t!r}")
    return schema, score_fields


class NimbleBackend:
    """bespokelabs/Bespoke-Nimble-9B, main branch: updated 2026-09-24 to a T=1.0 checkpoint (the
    task's "pin the main commit SHA as of today"). The pre-update checkpoint stays available at
    revision="original-2676" and is not used. LoRA adapter on Qwen/Qwen3.5-9B; the base repo and
    revision come from schema_config.json's own "model"/"revision" fields, which
    inference.ParallelScorer reads and loads itself -- parallel_schema.MODEL_ID
    ("Qwen/Qwen3.5-4B") is a stale constant left over from an earlier prompt-contract version and
    is NOT what actually gets loaded; schema_config.json says Qwen/Qwen3.5-9B @
    c202236235762e1c871ad0ccb60c8ee5ba337b9a, which matches the model card.

    Requires a CUDA GPU with bf16 support: inference.py hard-fails otherwise ("if not
    torch.cuda.is_available() or not torch.cuda.is_bf16_supported(): raise RuntimeError(...)"),
    with no fallback path. The project laptop's T1000 is Turing (no bf16), so this backend can
    only be import-tested there; the code is written to run unmodified on the Colab L4.

    Precision: inference.py's decision_result() never rounds -- probabilities and logits are
    plain `.tolist()` of a float64 tensor (`logits.double()`). Temperature is fixed at 1.0 for
    this checkpoint (ParallelScorer's default argument, and the model card's September 24 update
    says so explicitly; temperature_config.json in the repo is the *previous* checkpoint's 2.179
    and is not read by this code path), so served and T=1 are identical and no precision hook is
    needed.
    """

    tag = "nimble-9b"
    concurrency = 1

    def __init__(self):
        self._loaded = False

    async def __aenter__(self):
        if not self._loaded:
            await _run_sync(self._load)
            self._loaded = True
        return self

    async def __aexit__(self, *a):
        return None

    def _load(self):
        import sys
        import huggingface_hub as hh
        self.revision = _model_sha(NIMBLE_REPO)
        local_dir = hh.snapshot_download(NIMBLE_REPO, revision=self.revision)
        if local_dir not in sys.path:
            sys.path.insert(0, local_dir)
        from inference import NimbleModel   # = ParallelScorer; hard-requires CUDA + bf16
        self.model = NimbleModel(local_dir, temperature=1.0)
        self.served_temperature = 1.0

    async def answer(self, rec):
        schema, score_fields = nimble_schema(rec["questions"])
        context = _state_text(rec["state"])

        def _score():
            return self.model.score(context, schema, score_fields=score_fields)

        result = await _run_sync(_score)
        fields = result["fields"]
        out = {}
        for qid in rec["questions"]:
            f = fields[qid]
            probs = {k: float(v) for k, v in f["probabilities"].items()}
            out[qid] = {"probs": probs,
                       "raw": {"served_temperature": 1.0, "probs_t1": probs,
                               "logits": f.get("logits"), "native": f}}
        return {"model_returned": self.tag, "usage_in": None, "answers": out}


harness.register("nimble-9b", lambda **kw: NimbleBackend(**kw))


# ---------------------------------------------------------------------- comparator-open (vLLM)

# Qwen3-14B, official AWQ 4-bit release. The first Colab run used gemma-3-27b-it-int4-awq with
# max_model_len 16384 and failed at start-up on the L4 (2026-09-24); a 27B model leaves too little
# KV cache on 24 GB for batched generation. The 14B official AWQ checkpoint is natively supported
# by vLLM, leaves ample KV cache, and is run in non-thinking mode through its chat template.
COMPARATOR_REPO = "Qwen/Qwen3-14B-AWQ"
COMPARATOR_FULL_COVERAGE_MAX_K = 20   # every option reported at K <= this, else the top 5
COMPARATOR_TOP_N = 5


def comparator_option_list(q):
    """(keys, descriptions) in option order, using the same key convention as every other
    adapter in this module (wire_keys)."""
    t = q["type"]
    if t == "choice":
        keys = list(q["criteria"])
        descs = [_txt(q["criteria"][k]) for k in keys]
    elif t == "noul":
        c = noul_criteria(q)
        keys, descs = ["false", "true"], [_txt(c["false"]), _txt(c["true"])]
    else:
        crit = q["criteria"]
        keys = [str(i) for i in range(len(crit))]
        descs = [_txt(c) for c in crit]
    return keys, descs


def comparator_prompt(rec, qid, q):
    """(prompt_text, keys, n_report). n_report is how many {key, p} pairs the model must supply:
    every option at K <= 20, the 5 it considers most likely otherwise (the task's own rule)."""
    keys, descs = comparator_option_list(q)
    k = len(keys)
    n_report = k if k <= COMPARATOR_FULL_COVERAGE_MAX_K else COMPARATOR_TOP_N
    lines = "\n".join(f"- {key}: {desc}" for key, desc in zip(keys, descs))
    coverage = ("every option listed above" if k <= COMPARATOR_FULL_COVERAGE_MAX_K
               else f"the {COMPARATOR_TOP_N} options you judge most likely")
    prompt = (
        "You are answering a typed decision question about the state below. Reply with a single "
        "JSON object and nothing else.\n\n"
        f"State:\n{_state_text(rec['state'])}\n\n"
        f"Question: {_txt(q['instructions'])}\n\nOptions:\n{lines}\n\n"
        "Return JSON of the form "
        '{"answer": <the single best option\'s key, exactly as written above>, '
        '"probabilities": [{"key": <an option key>, "p": <your probability for it>}, ...]}, '
        f"covering {coverage}. Report your genuine calibrated belief for each; the probabilities "
        "need not sum to exactly 1, they will be renormalized."
    )
    return prompt, keys, n_report


def comparator_json_schema(n_report):
    """A guided-decoding JSON schema using an array of {key, p} pairs rather than an object keyed
    by the option strings themselves. An object whose property names are drawn from a dynamic,
    per-request enum is weakly supported by structured-output backends at K > ~20 and awkward to
    validate reliably at any K; the array form is uniform for every question regardless of option
    count and is converted back into the {"answer", "probabilities": {key: p}} shape the task
    describes by comparator_parse below."""
    return {
        "type": "object",
        "properties": {
            "answer": {"type": "string"},
            "probabilities": {
                "type": "array", "minItems": n_report, "maxItems": n_report,
                "items": {"type": "object",
                         "properties": {"key": {"type": "string"}, "p": {"type": "number"}},
                         "required": ["key", "p"]},
            },
        },
        "required": ["answer", "probabilities"],
    }


def comparator_parse(text, keys):
    """Parse the model's JSON reply into a full distribution over `keys`: missing options get 0,
    then the whole thing is renormalized (the task's own rule). Raises ValueError on a genuine
    parse failure, which the caller turns into an error line (the task: "parse failures as
    errors"). Pure function; test_adapters.py feeds it hand-written model output."""
    try:
        obj = json.loads(text)
        got = {}
        for item in obj["probabilities"]:
            k, p = str(item["key"]), float(item["p"])
            got[k] = max(0.0, p)
    except (json.JSONDecodeError, KeyError, TypeError, ValueError) as e:
        raise ValueError(f"comparator: could not parse the requested JSON: {e!r}") from e
    probs = {k: got.get(k, 0.0) for k in keys}
    s = sum(probs.values())
    if s <= 0:
        probs = {k: 1.0 / len(keys) for k in keys}   # every reported key missed the real option
                                                       # set: uniform, not an undefined 0/0 split
    else:
        probs = {k: v / s for k, v in probs.items()}
    return probs, obj.get("answer")


class ComparatorOpenBackend:
    """An open generative instruction model, served with vLLM offline batch inference on Colab:
    the "reads and reasons in text, then reports a number" comparator against the typed decision
    models. See COMPARATOR_REPO's comment above for which checkpoint and why.

    Batched through harness.py's documented prefetch() hook (this module's docstring): one vLLM
    LLM.generate() call per up-to-500-record chunk covers every question of every record in that
    chunk, each with its own per-question guided JSON schema. answer() then just looks its
    record's precomputed answers up in a cache prefetch() filled, so harness.py's own latency_s
    (timed around a single answer() call) reads near 0 for a prefetched record; the true cost is
    in raw instead: latency_mode="batched", batch_wall_s (that chunk's whole generate() wall time)
    and n_requests (per-question calls in that chunk) -- the task's own naming.

    A prompt that would not fit in max_model_len together with max_tokens of headroom is not sent
    to generate() at all (one over-length prompt would otherwise fail the whole batched call); it
    is recorded as a parse-failure-shaped error instead, same as a genuine JSON parse failure.

    Temperature 0 (greedy decoding -- distinct from the softmax "temperature" the other backends
    discuss): there is no output-token distribution to read a calibrated probability from, since
    the model reports its own numeric belief in text, so served_temperature is reported as 0.0 and
    there is no separate T=1 to recover (probs_t1 == probs).
    """

    tag = "comparator-open"
    repo = COMPARATOR_REPO
    served_temperature = 0.0
    concurrency = 500   # matches run()'s chunk size; prefetch() does the real batching

    def __init__(self, max_model_len=12288, max_tokens=768, gpu_memory_utilization=0.90):
        self.max_model_len = max_model_len
        self.max_tokens = max_tokens
        self.gpu_memory_utilization = gpu_memory_utilization
        self._loaded = False
        self._cache = {}

    async def __aenter__(self):
        if not self._loaded:
            await _run_sync(self._load)
            self._loaded = True
        return self

    async def __aexit__(self, *a):
        return None

    def _load(self):
        self.revision = _model_sha(self.repo)
        from vllm import LLM
        # quantization and dtype are read from the checkpoint's config (awq_marlin on an L4)
        self.llm = LLM(model=self.repo, revision=self.revision,
                       max_model_len=self.max_model_len,
                       gpu_memory_utilization=self.gpu_memory_utilization)
        self.tokenizer = self.llm.get_tokenizer()

    def _chat(self, prompt):
        """The instruct model's own chat template, with Qwen3's thinking mode switched off so
        the reply is the JSON object alone."""
        msgs = [{"role": "user", "content": prompt}]
        try:
            return self.tokenizer.apply_chat_template(msgs, tokenize=False,
                                                      add_generation_prompt=True,
                                                      enable_thinking=False)
        except TypeError:
            return self.tokenizer.apply_chat_template(msgs, tokenize=False,
                                                      add_generation_prompt=True)

    def _requests(self, rec):
        return [(rec["key"], qid) + comparator_prompt(rec, qid, q)
               for qid, q in rec["questions"].items()]

    async def prefetch(self, chunk):
        await _run_sync(self._prefetch_sync, chunk)

    def _prefetch_sync(self, chunk):
        import time
        from vllm import SamplingParams
        # structured output moved from guided_decoding=GuidedDecodingParams to
        # structured_outputs=StructuredOutputsParams in newer vLLM releases; support both
        try:
            from vllm.sampling_params import StructuredOutputsParams
        except ImportError:
            StructuredOutputsParams = None
        try:
            from vllm.sampling_params import GuidedDecodingParams
        except ImportError:
            GuidedDecodingParams = None

        all_reqs = [r for rec in chunk for r in self._requests(rec)]
        budget = self.max_model_len - self.max_tokens
        reqs, prompts, sampling = [], [], []
        for key, qid, prompt, keys, n_report in all_reqs:
            prompt = self._chat(prompt)
            n_prompt_tok = len(self.tokenizer.encode(prompt, add_special_tokens=False))
            if n_prompt_tok > budget:
                self._cache[(key, qid)] = {
                    "probs": None, "answer": None,
                    "error": f"comparator: prompt is {n_prompt_tok} tokens, budget is {budget}",
                    "raw_text": None, "usage_in": n_prompt_tok, "usage_out": None,
                    "latency_mode": "batched", "batch_wall_s": 0.0, "n_requests": len(all_reqs)}
                continue
            schema = comparator_json_schema(n_report)
            if StructuredOutputsParams is not None:
                sp = SamplingParams(temperature=0, max_tokens=self.max_tokens,
                                    structured_outputs=StructuredOutputsParams(json=schema))
            elif GuidedDecodingParams is not None:
                sp = SamplingParams(temperature=0, max_tokens=self.max_tokens,
                                    guided_decoding=GuidedDecodingParams(json=schema))
            else:   # older vLLM releases: guided_json lives directly on SamplingParams
                sp = SamplingParams(temperature=0, max_tokens=self.max_tokens, guided_json=schema)
            reqs.append((key, qid, keys))
            prompts.append(prompt)
            sampling.append(sp)

        if not prompts:
            return
        t0 = time.time()
        outputs = self.llm.generate(prompts, sampling)
        wall = time.time() - t0
        for (key, qid, keys), out in zip(reqs, outputs):
            text = out.outputs[0].text
            usage_in = len(out.prompt_token_ids) if out.prompt_token_ids is not None else None
            usage_out = len(out.outputs[0].token_ids) if out.outputs[0].token_ids is not None else None
            try:
                probs, answer = comparator_parse(text, keys)
                err = None
            except ValueError as e:
                probs, answer, err = None, None, str(e)
            self._cache[(key, qid)] = {
                "probs": probs, "answer": answer, "error": err, "raw_text": text,
                "usage_in": usage_in, "usage_out": usage_out,
                "latency_mode": "batched", "batch_wall_s": wall, "n_requests": len(reqs)}

    async def answer(self, rec):
        out, usage_in_total = {}, 0
        for qid in rec["questions"]:
            key = (rec["key"], qid)
            if key not in self._cache:
                await self.prefetch([rec])   # e.g. a direct unit test that never called prefetch
            cached = self._cache.pop(key)
            if cached["error"] is not None:
                raise RuntimeError(cached["error"])
            usage_in_total += cached["usage_in"] or 0
            out[qid] = {"probs": cached["probs"],
                       "raw": {"served_temperature": 0.0, "probs_t1": cached["probs"],
                               "answer": cached["answer"], "raw_text": cached["raw_text"],
                               "usage_out": cached["usage_out"], "latency_mode": cached["latency_mode"],
                               "batch_wall_s": cached["batch_wall_s"], "n_requests": cached["n_requests"]}}
        return {"model_returned": self.repo, "usage_in": usage_in_total, "answers": out}


harness.register("comparator-open", lambda **kw: ComparatorOpenBackend(**kw))

# Conditions the comparator answers, per the task and the coordinator's 2026-09-24 update (the
# refrozen manifest's D3 task list): d1_neutral, d1_calib, d2_k150, d2_k20, and every d3_<task> ,
# not the e2_ files.
COMPARATOR_CONDITIONS = ["d1_neutral", "d1_calib", "d2_k150", "d2_k20",
                        "d3_conv_go_awry", "d3_wiki_corpus", "d3_emotion", "d3_wiki_politeness"]


# ====================================================================== second revision
#
# Everything below was appended for the second revision and only ADDS backends and helpers:
# no line above this block changed, so every earlier tag behaves exactly as before. Two new
# families, both registered at the end of this block:
#
#   backbone-*        the untuned Qwen3.5 backbones of the decision models, asked the same
#                     question as a plain text prompt and scored by the likelihood of each
#                     option key (BackboneOptScoreBackend, transformers, one request at a time)
#   comparator-open2* Qwen3.6-27B through vLLM, in two modes: the verbalized-JSON protocol of
#                     comparator-open unchanged (Comparator2Backend), and the model's own
#                     likelihood of each option key after the same chat prompt
#                     (Comparator2LLBackend); each also has a batch-1 variant for latency


OPTSCORE_INSTRUCTION = "Reply with the key of the single best option, exactly as written above."
OPTSCORE_CUE = "Answer:"


def optscore_prompt(rec, q):
    """(prompt_text, keys, continuations) for one question under option-key scoring.

    The content is what every decision model receives: the state, the question's instruction
    and the options as "- key: description" lines in request order, with the keys of the
    frozen condition itself (o1..oK on the neutral files, 0/1, no/yes, yes/no or random strings
    on the option-name files, false/true for noul, 0..L-1 for score; comparator_option_list).
    One instruction line and the answer cue "Answer:" follow. The cue ends without a trailing
    space and each continuation is " " + key, so the prompt and each key are tokenized apart
    at a word boundary (optscore_encode checks that this equals the joint tokenization). No
    chat template is applied, for any backbone, so that the weights are the only variable
    across the four backbones. Pure function, no model import."""
    keys, descs = comparator_option_list(q)
    lines = "\n".join(f"- {key}: {desc}" for key, desc in zip(keys, descs))
    text = (f"State:\n{_state_text(rec['state'])}\n\n"
            f"Question: {_txt(q['instructions'])}\n\nOptions:\n{lines}\n\n"
            f"{OPTSCORE_INSTRUCTION}\n{OPTSCORE_CUE}")
    return text, keys, [" " + k for k in keys]


def key_nodes(key_ids):
    """The token paths after the prompt at which a next-token distribution is needed, shortest
    first: the empty path (the prompt itself) and every proper prefix of every key's token
    sequence. A key whose tokens are a proper prefix of a longer key (o1 of o10..o19 and
    o100..o150 under digit-wise tokenization) is such a path too, which is where its boundary
    term is read (combine_key_logprobs). Pure function."""
    seqs = [tuple(s) for s in key_ids]
    if any(len(s) == 0 for s in seqs):
        raise ValueError("an option key tokenized to nothing")
    if len(set(seqs)) != len(seqs):
        raise ValueError("two option keys tokenized to the same token sequence")
    nodes = {s[:j] for s in seqs for j in range(len(s))}
    return sorted(nodes, key=lambda n: (len(n), n))


def key_children(key_ids):
    """{path: set of next tokens that continue some declared key}. Pure function."""
    ch = {}
    for s in key_ids:
        s = tuple(s)
        for j in range(len(s)):
            ch.setdefault(s[:j], set()).add(s[j])
    return ch


def combine_key_logprobs(keys, key_ids, node_lp, node_floor=None):
    """Option probabilities from next-token log-probabilities at the key_nodes paths.

    For option k with tokens t_1..t_m after the prompt:
        log s_k = sum_j log p(t_j | prompt, t_<j)                  (sequence log-likelihood)
                + log(1 - sum_{c in E_k} p(c | prompt, t_1..t_m))  (boundary term)
    where E_k is the set of next tokens that continue k's tokens into a LONGER declared key.
    The first term alone is the plain sum of token log-probabilities; it is not divided by the
    number of tokens or normalized in any other way. The boundary term is zero unless k is a
    token prefix of another key: it removes from k the probability that the model goes on to
    write a longer declared key, so s_k is the probability of the event "the continuation is
    exactly key k among the declared keys" and o1 does not absorb the mass of o10..o19. The
    distribution is softmax(log s) over the options, i.e. temperature 1.

    node_lp maps each path to {token id: log-probability}. When a needed token is absent from a
    path's map (vLLM returns only the top-N), node_floor[path] (the smallest log-probability
    that was returned, an upper bound) is used and counted in n_missing; with no floor the
    absence is an error. Returns (probs, logp_key, log_boundary, n_missing). Pure function."""
    seqs = [tuple(s) for s in key_ids]
    ch = key_children(seqs)
    missing = [0]

    def lp(path, tok):
        d = node_lp[path]
        if tok in d:
            return float(d[tok])
        if node_floor is None or path not in node_floor:
            raise KeyError(f"no log-probability for token {tok} after path {path}")
        missing[0] += 1
        return float(node_floor[path])

    logp, logb = {}, {}
    for k, s in zip(keys, seqs):
        logp[k] = sum(lp(s[:j], s[j]) for j in range(len(s)))
        ext = ch.get(s)
        if ext:
            mass = sum(math.exp(lp(s, c)) for c in ext)
            logb[k] = math.log1p(-min(mass, 1.0 - 1e-15))
        else:
            logb[k] = 0.0
    tot = {k: logp[k] + logb[k] for k in keys}
    top = max(tot.values())
    ex = {k: math.exp(v - top) for k, v in tot.items()}
    z = sum(ex.values())
    return {k: v / z for k, v in ex.items()}, logp, logb, missing[0]


def _replicate_cache(cache, n, device):
    """n independent copies (batch rows) of a batch-1 transformers cache, leaving the source
    untouched: the layer objects are shallow-copied, the per-state dicts of the linear-attention
    (Gated DeltaNet) layers are copied, then reorder_cache(zeros(n)) index_selects every KV,
    conv and recurrent tensor into new tensors. This is kev/model.py's _rows_hidden replica
    (jaredpalmer/kev at KEV_GITHUB_COMMIT), which kev uses to continue question rows from a
    cached Qwen3.5 state."""
    import copy
    import torch
    from transformers.cache_utils import LinearAttentionCacheLayerMixin
    replica = copy.copy(cache)
    replica.layers = [copy.copy(layer) for layer in cache.layers]
    for src, tgt in zip(cache.layers, replica.layers):
        if isinstance(src, LinearAttentionCacheLayerMixin):
            tgt.conv_states = src.conv_states.copy()
            tgt.recurrent_states = src.recurrent_states.copy()
            tgt.is_conv_states_initialized = src.is_conv_states_initialized.copy()
            tgt.is_recurrent_states_initialized = src.is_recurrent_states_initialized.copy()
            tgt.has_previous_state = src.has_previous_state.copy()
            tgt.conv_kernel_size = src.conv_kernel_size.copy()
    replica.reorder_cache(torch.zeros(n, dtype=torch.long, device=device))
    return replica


# ---------------------------------------------------------------------- untuned backbones

# The base each decision model adapts, per its own card (shared/colab/cards):
#   kev-9b      LoRA + pointer head on Qwen/Qwen3.5-9B-Base (card: revision 68c46c4b)
#   nimble-9b   LoRA on the post-trained Qwen/Qwen3.5-9B (card and schema_config.json:
#               c202236235762e1c871ad0ccb60c8ee5ba337b9a), NOT the Base checkpoint
#   decider-2b  Qwen/Qwen3.5-2B-Base (decider_config.json "base"; no revision stated)
#   this-that   adapted from decider-2b, so the same 2B base
#   kev-0.8b    Qwen/Qwen3.5-0.8B-Base (card: revision dc7cdfe2)
# Laya is a ModernBERT encoder with no language-model head over its option keys, so it has
# no backbone control here. Revisions are pinned through P4_REVISIONS by the notebook.
BACKBONE_REPOS = {
    "backbone-qwen35-9b-base": "Qwen/Qwen3.5-9B-Base",
    "backbone-qwen35-9b": "Qwen/Qwen3.5-9B",
    "backbone-qwen35-2b-base": "Qwen/Qwen3.5-2B-Base",
    "backbone-qwen35-0.8b-base": "Qwen/Qwen3.5-0.8B-Base",
}
# the decision model(s) each backbone is the control for
BACKBONE_OF = {"kev-9b": "backbone-qwen35-9b-base", "nimble-9b": "backbone-qwen35-9b",
               "decider-2b": "backbone-qwen35-2b-base", "this-that-1.0": "backbone-qwen35-2b-base",
               "kev-0.8b": "backbone-qwen35-0.8b-base"}
BACKBONE_CONDITIONS = (["d1_neutral", "d2_k150", "d3_conv_go_awry", "d3_wiki_corpus",
                        "d3_emotion", "d3_wiki_politeness"]
                       + [f"e2_d1_{n}" for n in ("k01", "kny", "kswap", "krand")]
                       + [f"e2_d3_{t}_{n}" for t in ("conv_go_awry", "wiki_corpus")
                          for n in ("k01", "kny", "kswap", "krand")])


class BackboneOptScoreBackend:
    """An untuned causal LM scored on the option keys (optscore_prompt, combine_key_logprobs).

    One forward pass over the prompt with the cache on gives the next-token distribution at the
    answer cue. Every deeper path the keys need (key_nodes; one path " o" for o1..o9, sixteen
    for o1..o150, a few for random five-letter keys) then runs as one right-padded batch of rows
    that continue independent replicas of that cache (_replicate_cache), rows_per_pass rows at
    a time, so a question costs one prompt pass plus one short batched pass whatever its option
    count. Padding sits after each row's real tokens, so causal attention and the recurrent
    layers never let it reach a real position; each row is read at its own last real token.
    Log-softmax is taken in float64 from the model's logits (bfloat16 weights on CUDA, float32
    on CPU). Deterministic, so served and T=1 distributions coincide (probs_t1 == probs).

    Self-check. With P4_OPTSCORE_CHECK=n the first n requests of the process also recompute
    every path by a plain full-sequence forward pass without any cache and compare the
    resulting option distributions. The largest absolute difference is printed per request.
    It raises, failing the notebook's smoke test before the full run starts, when a difference
    exceeds P4_OPTSCORE_CHECK_TOL (default 0.15) or when the two argmax options disagree on
    more than one checked question. On CPU in float32 the two agree to about 1e-6 in
    probability and 3e-5 in log-probability (Qwen3.5-0.8B-Base on d2_k150, d1_neutral and the
    random-key files), which is the exactness test; in bfloat16 the cached rows and the
    full-sequence pass round differently (up to about 0.02 in probability on the laptop's
    emulated bfloat16), so on the GPU the check only guards against gross breakage.

    Truncation: none is applied. A prompt longer than max_len tokens (32768 by default; the
    longest frozen prompt is about 8k tokens, Qwen3.5 reads 262,144) is recorded as an error
    line, and the notebook's status cell reports the maximum prompt length per condition.
    """

    concurrency = 1
    served_temperature = 1.0

    def __init__(self, tag, max_len=32768, rows_per_pass=32):
        self.tag = tag
        self.repo = BACKBONE_REPOS[tag]
        self.max_len = max_len
        self.rows_per_pass = rows_per_pass
        self.check_n = int(os.environ.get("P4_OPTSCORE_CHECK", "0"))
        self.check_tol = float(os.environ.get("P4_OPTSCORE_CHECK_TOL", "0.15"))
        self._argmax_disagree = 0
        self._n_seen = 0
        self._loaded = False

    async def __aenter__(self):
        if not self._loaded:
            await _run_sync(self._load)
            self._loaded = True
        return self

    async def __aexit__(self, *a):
        return None

    def _load(self):
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer
        self.revision = _model_sha(self.repo)
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        dtype = torch.bfloat16 if self.device == "cuda" else torch.float32
        self.tok = AutoTokenizer.from_pretrained(self.repo, revision=self.revision)
        self.model = AutoModelForCausalLM.from_pretrained(
            self.repo, revision=self.revision, dtype=dtype).to(self.device).eval()
        self.dtype_name = str(dtype).replace("torch.", "")

    def encode(self, rec, q):
        """(prompt ids, keys, key ids, joint tokenization equal) for one question."""
        text, keys, conts = optscore_prompt(rec, q)
        enc = lambda s: self.tok.encode(s, add_special_tokens=False)   # noqa: E731
        p_ids = enc(text)
        k_ids = [enc(c) for c in conts]
        joint_ok = all(enc(text + c) == p_ids + ids for c, ids in zip(conts, k_ids))
        return p_ids, keys, k_ids, joint_ok

    def _needed(self, nodes, children):
        return {n: sorted(children.get(n, ())) for n in nodes}

    def node_logprobs(self, p_ids, nodes, children):
        """{path: {token: log-probability}} for the tokens each path needs, cached and batched."""
        import torch
        F = torch.nn.functional
        need = self._needed(nodes, children)
        out = {}
        with torch.no_grad():
            ids = torch.tensor([p_ids], device=self.device)
            res = self.model(input_ids=ids, use_cache=True, logits_to_keep=1)
            cache = res.past_key_values
            lp = F.log_softmax(res.logits[0, -1].double(), -1)
            out[()] = dict(zip(need[()], lp[need[()]].tolist()))
            rest = [n for n in nodes if n]
            for start in range(0, len(rest), self.rows_per_pass):
                part = rest[start:start + self.rows_per_pass]
                L = max(len(n) for n in part)
                x = torch.tensor([list(n) + [n[-1]] * (L - len(n)) for n in part],
                                 device=self.device)
                att = torch.tensor([[1] * (len(p_ids) + len(n)) + [0] * (L - len(n))
                                    for n in part], device=self.device)
                replica = _replicate_cache(cache, len(part), self.device)
                o = self.model(input_ids=x, attention_mask=att, past_key_values=replica,
                               use_cache=True)
                for i, n in enumerate(part):
                    row = F.log_softmax(o.logits[i, len(n) - 1].double(), -1)
                    out[n] = dict(zip(need[n], row[need[n]].tolist()))
                del replica, o
        return out

    def node_logprobs_naive(self, p_ids, nodes, children):
        """The same quantities by one full forward pass per path, no cache (the self-check)."""
        import torch
        F = torch.nn.functional
        need = self._needed(nodes, children)
        out = {}
        with torch.no_grad():
            for n in nodes:
                ids = torch.tensor([p_ids + list(n)], device=self.device)
                res = self.model(input_ids=ids, use_cache=False, logits_to_keep=1)
                row = F.log_softmax(res.logits[0, -1].double(), -1)
                out[n] = dict(zip(need[n], row[need[n]].tolist()))
        return out

    def score_question(self, rec, q, check=False):
        p_ids, keys, k_ids, joint_ok = self.encode(rec, q)
        n_tok = len(p_ids) + max(len(s) for s in k_ids)
        if n_tok > self.max_len:
            raise ValueError(f"optscore: prompt is {n_tok} tokens, max_len is {self.max_len}")
        nodes = key_nodes(k_ids)
        children = key_children(k_ids)
        node_lp = self.node_logprobs(p_ids, nodes, children)
        probs, logp, logb, _ = combine_key_logprobs(keys, k_ids, node_lp)
        raw = {"served_temperature": 1.0, "probs_t1": probs, "logp_key": logp,
               "log_boundary": {k: v for k, v in logb.items() if v != 0.0},
               "n_prompt_tokens": len(p_ids), "n_paths": len(nodes),
               "joint_tokenization_ok": joint_ok, "dtype": self.dtype_name,
               "scoring": "optscore: sum of key-token log-probs + boundary term, softmax, T=1"}
        if check:
            naive = self.node_logprobs_naive(p_ids, nodes, children)
            p_naive, _, _, _ = combine_key_logprobs(keys, k_ids, naive)
            d_prob = max(abs(probs[k] - p_naive[k]) for k in keys)
            d_lp = max(abs(node_lp[n][t] - naive[n][t]) for n in nodes for t in node_lp[n])
            raw["check_max_abs_dprob"], raw["check_max_abs_dlogp"] = d_prob, d_lp
            if max(probs, key=probs.get) != max(p_naive, key=p_naive.get):
                self._argmax_disagree += 1
            print(f"  optscore self-check: max |dprob| {d_prob:.3g}, max |dlogp| {d_lp:.3g}, "
                  f"argmax disagreements so far {self._argmax_disagree}", flush=True)
            if d_prob > self.check_tol or self._argmax_disagree > 1:
                raise RuntimeError(f"optscore self-check failed: cached and full-sequence "
                                   f"distributions differ by {d_prob:.4g} (tolerance "
                                   f"{self.check_tol}), {self._argmax_disagree} argmax "
                                   f"disagreements")
        return probs, raw, len(p_ids)

    async def answer(self, rec):
        check = self._n_seen < self.check_n
        self._n_seen += 1

        def _score():
            out, usage = {}, 0
            for qid, q in rec["questions"].items():
                probs, raw, n = self.score_question(rec, q, check=check)
                out[qid] = {"probs": probs, "raw": raw}
                usage += n
            return out, usage

        out, usage = await _run_sync(_score)
        return {"model_returned": self.repo, "usage_in": usage, "answers": out}


for _tag in BACKBONE_REPOS:
    harness.register(_tag, lambda _t=_tag, **kw: BackboneOptScoreBackend(_t, **kw))


# ---------------------------------------------------------------------- comparator-open2 (vLLM)

# Qwen3.6-27B, the official FP8 release (fine-grained FP8, block 128), on an A100 40 GB: its
# card puts it ahead of Gemma-4-31B and Qwen3.6-35B-A3B on MMLU-Pro (86.2), GPQA Diamond
# (87.8) and SuperGPQA (66.0). vLLM runs block FP8 on Ampere through the FP8 Marlin kernel
# (weight-only, W8A16). The L4 fallback is the same model as a community 4-bit AWQ release
# (compressed-tensors, group size 32), under its own tags so the two never mix.
COMPARATOR2_REPO = "Qwen/Qwen3.6-27B-FP8"
COMPARATOR2_AWQ_REPO = "cyankiwi/Qwen3.6-27B-AWQ-INT4"
COMPARATOR2_LL_CUE = '{"answer": "'
COMPARATOR2_TOPN = 64      # next-token log-probabilities returned per scoring path
COMPARATOR2_PROFILES = {   # engine settings per checkpoint (and the GPU it is meant for)
    COMPARATOR2_REPO: {"max_model_len": 16384, "gpu_memory_utilization": 0.92,
                       "max_num_seqs": 32, "enforce_eager": False},
    COMPARATOR2_AWQ_REPO: {"max_model_len": 12288, "gpu_memory_utilization": 0.95,
                           "max_num_seqs": 8, "enforce_eager": True},
}


class Comparator2Backend(ComparatorOpenBackend):
    """comparator-open's verbalized-JSON protocol, unchanged (comparator_prompt,
    comparator_json_schema, comparator_parse, greedy decoding, thinking off, prefetch
    batching), on a stronger checkpoint. Only the engine construction differs: the vision tower
    is not loaded (language_model_only), the tokenizer revision is pinned with the weights, and
    the engine settings come from COMPARATOR2_PROFILES. The prompt budget is the profile's
    max_model_len minus max_tokens (16384 - 768 on the A100 profile, so the longest D3 prompts
    that exceeded comparator-open's 12288 budget are answered)."""

    served_temperature = 0.0

    def __init__(self, tag, repo, batch1=False, max_tokens=768):
        prof = COMPARATOR2_PROFILES[repo]
        super().__init__(max_model_len=prof["max_model_len"], max_tokens=max_tokens,
                         gpu_memory_utilization=prof["gpu_memory_utilization"])
        self.tag, self.repo, self.batch1 = tag, repo, batch1
        self.max_num_seqs = prof["max_num_seqs"]
        self.enforce_eager = prof["enforce_eager"]
        if batch1:
            # harness.run() skips a backend whose prefetch is None, so nothing is batched: each
            # question is its own generate() call inside answer() and latency_s is batch-1 time
            self.prefetch = None
            self.concurrency = 1

    def _load(self):
        self.revision = _model_sha(self.repo)
        from vllm import LLM
        self.llm = LLM(model=self.repo, revision=self.revision, tokenizer_revision=self.revision,
                       max_model_len=self.max_model_len,
                       gpu_memory_utilization=self.gpu_memory_utilization,
                       max_num_seqs=self.max_num_seqs, enforce_eager=self.enforce_eager,
                       max_logprobs=COMPARATOR2_TOPN, enable_prefix_caching=True,
                       language_model_only=True)
        self.tokenizer = self.llm.get_tokenizer()

    def _one_question(self, rec, qid):
        return {"key": rec["key"], "state": rec["state"],
                "questions": {qid: rec["questions"][qid]}}

    async def answer(self, rec):
        if not self.batch1:
            return await super().answer(rec)
        out, usage_in_total = {}, 0
        for qid in rec["questions"]:
            await _run_sync(self._prefetch_sync, [self._one_question(rec, qid)])
            cached = self._cache.pop((rec["key"], qid))
            if cached["error"] is not None:
                raise RuntimeError(cached["error"])
            usage_in_total += cached["usage_in"] or 0
            out[qid] = {"probs": cached["probs"],
                       "raw": {"served_temperature": 0.0, "probs_t1": cached["probs"],
                               "answer": cached["answer"], "raw_text": cached["raw_text"],
                               "usage_out": cached["usage_out"], "latency_mode": "batch1",
                               "batch_wall_s": cached["batch_wall_s"], "n_requests": 1}}
        return {"model_returned": self.repo, "usage_in": usage_in_total, "answers": out}


class Comparator2LLBackend(Comparator2Backend):
    """The same checkpoint and the same chat prompt as Comparator2Backend, read as a
    likelihood instead of a verbalized number.

    The prompt is comparator_prompt unchanged, through the chat template with thinking off,
    followed by the assistant's opening characters of the JSON reply it was asked for,
    COMPARATOR2_LL_CUE = '{"answer": "'. What the model would write next is the key of its
    answer, so the option probabilities are combine_key_logprobs over the key tokens after that
    cue (the same sequence log-likelihood plus boundary term as the backbones, temperature 1,
    no generation). Each needed path is one vLLM request with max_tokens=1 that returns the
    top COMPARATOR2_TOPN next-token log-probabilities (vLLM's default logprobs_mode is the raw
    model distribution). Requests are sent as token ids, so nothing is re-tokenized. A needed
    token outside the returned top-N gets the smallest returned log-probability as an upper
    bound, counted per question in raw["n_missing"].

    Batching: the questions of a prefetch chunk go in groups of max_num_seqs. For each group,
    phase 1 sends every question's prompt (the root path), which fills vLLM's prefix cache,
    and phase 2 sends every deeper path, which continues a cached prompt (for this hybrid
    model vLLM caches at block granularity, "align" mode, so up to one block is recomputed per
    path). Grouping keeps a group's prompt blocks in the cache until its paths have run; with
    the whole chunk in phase 1, the blocks of early prompts would be evicted first.
    batch_wall_s is the summed wall time of all groups of the chunk and n_requests the number
    of questions in the chunk, so batch_wall_s / n_requests is a question's share, as for
    comparator-open. The batch-1 variant runs both phases for one question at a time."""

    served_temperature = 1.0

    def ll_encode(self, rec, qid, q):
        prompt, keys, _n_report = comparator_prompt(rec, qid, q)
        text = self._chat(prompt) + COMPARATOR2_LL_CUE
        enc = lambda s: self.tokenizer.encode(s, add_special_tokens=False)   # noqa: E731
        p_ids = enc(text)
        k_ids = [enc(k) for k in keys]
        joint_ok = all(enc(text + k + '"')[:len(p_ids) + len(ids)] == p_ids + ids
                       for k, ids in zip(keys, k_ids))
        return p_ids, keys, k_ids, joint_ok

    @staticmethod
    def _lp_dict(logprobs_at_pos):
        return {int(t): float(getattr(v, "logprob", v)) for t, v in logprobs_at_pos.items()}

    def _prefetch_sync(self, chunk):
        import time
        from vllm import SamplingParams
        sp = SamplingParams(temperature=0, max_tokens=1, logprobs=COMPARATOR2_TOPN)
        items = []
        for rec in chunk:
            for qid, q in rec["questions"].items():
                p_ids, keys, k_ids, joint_ok = self.ll_encode(rec, qid, q)
                n_tok = len(p_ids) + max(len(s) for s in k_ids)
                if n_tok > self.max_model_len - 1:
                    self._cache[(rec["key"], qid)] = {
                        "error": f"comparator-ll: prompt is {n_tok} tokens, "
                                 f"max_model_len is {self.max_model_len}"}
                    continue
                items.append({"key": rec["key"], "qid": qid, "p_ids": p_ids, "keys": keys,
                              "k_ids": k_ids, "joint_ok": joint_ok, "nodes": key_nodes(k_ids)})
        if not items:
            return
        node_lp = [{} for _ in items]
        wall = phase1 = 0.0
        n_paths_total = 0
        group = max(1, int(self.max_num_seqs))
        for g0 in range(0, len(items), group):
            idx = list(range(g0, min(g0 + group, len(items))))
            t0 = time.time()
            roots = self.llm.generate([{"prompt_token_ids": items[i]["p_ids"]} for i in idx],
                                      sp, use_tqdm=False)
            t1 = time.time()
            deeper = [(i, n) for i in idx for n in items[i]["nodes"] if n]
            outs = (self.llm.generate([{"prompt_token_ids": items[i]["p_ids"] + list(n)}
                                       for i, n in deeper], sp, use_tqdm=False)
                    if deeper else [])
            wall += time.time() - t0
            phase1 += t1 - t0
            n_paths_total += len(idx) + len(deeper)
            for i, o in zip(idx, roots):
                node_lp[i][()] = self._lp_dict(o.outputs[0].logprobs[0])
            for (i, n), o in zip(deeper, outs):
                node_lp[i][n] = self._lp_dict(o.outputs[0].logprobs[0])
        for i, it in enumerate(items):
            floor = {n: min(d.values()) for n, d in node_lp[i].items()}
            probs, logp, logb, n_missing = combine_key_logprobs(it["keys"], it["k_ids"],
                                                                node_lp[i], floor)
            self._cache[(it["key"], it["qid"])] = {
                "error": None, "probs": probs, "answer": max(probs, key=probs.get),
                "logp_key": logp, "log_boundary": {k: v for k, v in logb.items() if v != 0.0},
                "n_missing": n_missing, "n_paths": len(it["nodes"]),
                "joint_ok": it["joint_ok"], "usage_in": len(it["p_ids"]),
                "batch_wall_s": wall, "phase1_wall_s": phase1, "n_requests": len(items),
                "n_path_requests": n_paths_total}

    async def answer(self, rec):
        out, usage_in_total = {}, 0
        for qid in rec["questions"]:
            key = (rec["key"], qid)
            if self.batch1:
                await _run_sync(self._prefetch_sync, [self._one_question(rec, qid)])
            elif key not in self._cache:
                await _run_sync(self._prefetch_sync, [rec])
            c = self._cache.pop(key)
            if c["error"] is not None:
                raise RuntimeError(c["error"])
            usage_in_total += c["usage_in"] or 0
            out[qid] = {"probs": c["probs"],
                       "raw": {"served_temperature": 1.0, "probs_t1": c["probs"],
                               "answer": c["answer"], "logp_key": c["logp_key"],
                               "log_boundary": c["log_boundary"], "n_missing": c["n_missing"],
                               "n_paths": c["n_paths"], "joint_tokenization_ok": c["joint_ok"],
                               "latency_mode": "batch1" if self.batch1 else "batched",
                               "batch_wall_s": c["batch_wall_s"],
                               "phase1_wall_s": c["phase1_wall_s"],
                               "n_requests": 1 if self.batch1 else c["n_requests"],
                               "n_path_requests": c["n_path_requests"],
                               "cue": COMPARATOR2_LL_CUE}}
        return {"model_returned": self.repo, "usage_in": usage_in_total, "answers": out}


# tag -> (class, checkpoint, batch-1)
COMPARATOR2_TAGS = {
    "comparator-open2": (Comparator2Backend, COMPARATOR2_REPO, False),
    "comparator-open2-ll": (Comparator2LLBackend, COMPARATOR2_REPO, False),
    "comparator-open2-b1": (Comparator2Backend, COMPARATOR2_REPO, True),
    "comparator-open2-ll-b1": (Comparator2LLBackend, COMPARATOR2_REPO, True),
    "comparator-open2-awq": (Comparator2Backend, COMPARATOR2_AWQ_REPO, False),
    "comparator-open2-awq-ll": (Comparator2LLBackend, COMPARATOR2_AWQ_REPO, False),
    "comparator-open2-awq-b1": (Comparator2Backend, COMPARATOR2_AWQ_REPO, True),
    "comparator-open2-awq-ll-b1": (Comparator2LLBackend, COMPARATOR2_AWQ_REPO, True),
}
for _tag, (_cls, _repo, _b1) in COMPARATOR2_TAGS.items():
    harness.register(_tag, lambda _t=_tag, _c=_cls, _r=_repo, _b=_b1, **kw: _c(_t, _r, _b, **kw))



# ====================================================================== third revision
#
# Appended for the third revision; no line above changed. One backend family:
#
#   backbone-desc-*   the same untuned Qwen3.5 backbones, asked the same content, but scored on
#                     each option's DESCRIPTION instead of its key (BackboneDescScoreBackend)
#
# Key scoring asks an untuned base model to produce a neutral identifier such as o17, which
# may understate what the backbone knows about the options. Description scoring is the
# classic zero-shot readout of a language model: the probability of writing the option's own
# text after the answer cue.

DESCSCORE_INSTRUCTION = "Reply with the description of the single best option, exactly as written above."


def descscore_prompt(rec, q):
    """(prompt_text, keys, continuations) for one question under description scoring. The
    content equals optscore_prompt's (state, instruction, "- key: description" lines in
    request order) with the instruction line asking for the description; each continuation
    is " " + description. No chat template. Pure function, no model import."""
    keys, descs = comparator_option_list(q)
    lines = "\n".join(f"- {key}: {desc}" for key, desc in zip(keys, descs))
    text = (f"State:\n{_state_text(rec['state'])}\n\n"
            f"Question: {_txt(q['instructions'])}\n\nOptions:\n{lines}\n\n"
            f"{DESCSCORE_INSTRUCTION}\n{OPTSCORE_CUE}")
    return text, keys, [" " + d for d in descs]


def combine_desc_logprobs(keys, logp_sum, n_tok):
    """softmax over options of the MEAN log-probability per token of each description (length
    normalized, temperature one). Returns (probs, mean). Pure function."""
    mean = {k: logp_sum[k] / max(n_tok[k], 1) for k in keys}
    top = max(mean.values())
    ex = {k: math.exp(v - top) for k, v in mean.items()}
    z = sum(ex.values())
    return {k: v / z for k, v in ex.items()}, mean


class BackboneDescScoreBackend(BackboneOptScoreBackend):
    """The untuned backbone scored on option descriptions (descscore_prompt,
    combine_desc_logprobs). One cached forward pass over the prompt gives the log-probability
    of each description's first token; every description then continues a replica of that
    cache as one right-padded row, rows_per_pass rows per pass, and its remaining tokens are
    read at the row's own positions. The self-check (P4_OPTSCORE_CHECK) recomputes every
    description by a full-sequence forward pass without a cache."""

    def __init__(self, tag, max_len=32768, rows_per_pass=16):
        super().__init__(BACKBONE_DESC_OF[tag], max_len=max_len, rows_per_pass=rows_per_pass)
        self.tag = tag

    def encode_desc(self, rec, q):
        text, keys, conts = descscore_prompt(rec, q)
        enc = lambda s: self.tok.encode(s, add_special_tokens=False)   # noqa: E731
        p_ids = enc(text)
        c_ids = [enc(c) for c in conts]
        if any(len(c) == 0 for c in c_ids):
            raise ValueError("a description tokenized to nothing")
        joint_ok = all(enc(text + c) == p_ids + ids for c, ids in zip(conts, c_ids))
        return p_ids, keys, c_ids, joint_ok

    def desc_logprobs(self, p_ids, c_ids):
        """Summed log-probability of each description. Memory: the log-softmax is taken one
        vocabulary vector at a time, and a pass that runs out of GPU memory is retried with
        half as many rows (down to one), so the result does not depend on the batch size."""
        import torch
        F = torch.nn.functional
        rows = int(os.environ.get("P4_DESC_ROWS", self.rows_per_pass))
        sums = []
        with torch.no_grad():
            ids = torch.tensor([p_ids], device=self.device)
            res = self.model(input_ids=ids, use_cache=True, logits_to_keep=1)
            cache = res.past_key_values
            lp0 = F.log_softmax(res.logits[0, -1].double(), -1)
            del res
            start = 0
            while start < len(c_ids):
                part = c_ids[start:start + rows]
                L = max(len(c) for c in part)
                try:
                    x = torch.tensor([c + [c[-1]] * (L - len(c)) for c in part],
                                     device=self.device)
                    att = torch.tensor([[1] * (len(p_ids) + len(c)) + [0] * (L - len(c))
                                        for c in part], device=self.device)
                    replica = _replicate_cache(cache, len(part), self.device)
                    o = self.model(input_ids=x, attention_mask=att, past_key_values=replica,
                                   use_cache=True)
                    got = []
                    for i, c in enumerate(part):
                        tot = float(lp0[c[0]])
                        for j in range(1, len(c)):
                            tot += float(F.log_softmax(o.logits[i, j - 1].double(), -1)[c[j]])
                        got.append(tot)
                    del replica, o
                except torch.cuda.OutOfMemoryError:
                    replica = o = None
                    torch.cuda.empty_cache()
                    if rows == 1:
                        raise
                    rows = max(1, rows // 2)
                    print(f"  descscore: out of memory, retrying with {rows} rows per pass",
                          flush=True)
                    continue
                sums += got
                start += len(part)
                if self.device == "cuda":
                    torch.cuda.empty_cache()
        return sums

    def desc_logprobs_naive(self, p_ids, c_ids):
        import torch
        F = torch.nn.functional
        sums = []
        with torch.no_grad():
            for c in c_ids:
                ids = torch.tensor([p_ids + c], device=self.device)
                lps = F.log_softmax(self.model(input_ids=ids, use_cache=False).logits[0].double(), -1)
                sums.append(float(sum(lps[len(p_ids) - 1 + j, c[j]] for j in range(len(c)))))
        return sums

    def score_question(self, rec, q, check=False):
        p_ids, keys, c_ids, joint_ok = self.encode_desc(rec, q)
        n_tok = len(p_ids) + max(len(c) for c in c_ids)
        if n_tok > self.max_len:
            raise ValueError(f"descscore: prompt is {n_tok} tokens, max_len is {self.max_len}")
        sums = self.desc_logprobs(p_ids, c_ids)
        logp_sum = dict(zip(keys, sums))
        n_toks = {k: len(c) for k, c in zip(keys, c_ids)}
        probs, mean = combine_desc_logprobs(keys, logp_sum, n_toks)
        raw = {"served_temperature": 1.0, "probs_t1": probs, "logp_desc_sum": logp_sum,
               "desc_tokens": n_toks, "n_prompt_tokens": len(p_ids),
               "joint_tokenization_ok": joint_ok, "dtype": self.dtype_name,
               "scoring": "descscore: mean log-prob per description token, softmax, T=1"}
        if check:
            naive = self.desc_logprobs_naive(p_ids, c_ids)
            p_naive, _ = combine_desc_logprobs(keys, dict(zip(keys, naive)), n_toks)
            d_prob = max(abs(probs[k] - p_naive[k]) for k in keys)
            raw["check_max_abs_dprob"] = d_prob
            # a near tie can swap the argmax under bfloat16 rounding, so only a clear
            # disagreement (top two options more than 0.05 apart) counts against the check
            top2 = sorted(p_naive.values(), reverse=True)[:2]
            if (max(probs, key=probs.get) != max(p_naive, key=p_naive.get)
                    and top2[0] - top2[-1] > 0.05):
                self._argmax_disagree += 1
            print(f"  descscore self-check: max |dprob| {d_prob:.3g}, argmax disagreements "
                  f"so far {self._argmax_disagree}", flush=True)
            if d_prob > self.check_tol or self._argmax_disagree > 1:
                raise RuntimeError(f"descscore self-check failed: {d_prob:.4g} "
                                   f"(tolerance {self.check_tol}), {self._argmax_disagree} "
                                   f"argmax disagreements")
        return probs, raw, len(p_ids)


BACKBONE_DESC_OF = {"backbone-desc-qwen35-9b-base": "backbone-qwen35-9b-base",
                    "backbone-desc-qwen35-9b": "backbone-qwen35-9b",
                    "backbone-desc-qwen35-2b-base": "backbone-qwen35-2b-base",
                    "backbone-desc-qwen35-0.8b-base": "backbone-qwen35-0.8b-base"}
BACKBONE_DESC_CONDITIONS = ["d1_neutral", "d2_k150", "d3_conv_go_awry", "d3_wiki_corpus",
                            "d3_emotion", "d3_wiki_politeness"]
for _tag in BACKBONE_DESC_OF:
    harness.register(_tag, lambda _t=_tag, **kw: BackboneDescScoreBackend(_t, **kw))



# ====================================================================== fourth revision
#
# Appended for the fourth revision; no line above changed. A comparator from a second model
# family, Gemma-4-31B-it, read in the same two ways as Qwen3.6-27B (the verbalized-JSON
# protocol of comparator-open, and the likelihood of each option key after the same chat
# prompt), so that the comparator results do not rest on one model family.
#
# The bf16 checkpoint is quantized to FP8 weights when vLLM loads it (weight-only FP8 through
# the Marlin kernel on an A100), which is the same numeric format as the Qwen3.6-27B FP8
# release. The chat template is the model's own; Gemma has no thinking switch, so _chat's
# enable_thinking argument is ignored by its template.

COMPARATOR3_REPO = "google/gemma-4-31B-it"
COMPARATOR2_PROFILES[COMPARATOR3_REPO] = {"max_model_len": 16384, "gpu_memory_utilization": 0.92,
                                          "max_num_seqs": 32, "enforce_eager": False,
                                          "quantization": "fp8"}


class _Comparator3Load:
    """_load of Comparator2Backend with the profile's on-the-fly quantization; the
    language_model_only switch is passed only where the engine accepts it."""

    def _load(self):
        self.revision = _model_sha(self.repo)
        from vllm import LLM
        prof = COMPARATOR2_PROFILES[self.repo]
        kw = dict(model=self.repo, revision=self.revision, tokenizer_revision=self.revision,
                  max_model_len=self.max_model_len,
                  gpu_memory_utilization=self.gpu_memory_utilization,
                  max_num_seqs=self.max_num_seqs, enforce_eager=self.enforce_eager,
                  max_logprobs=COMPARATOR2_TOPN, enable_prefix_caching=True)
        if prof.get("quantization"):
            kw["quantization"] = prof["quantization"]
        try:
            self.llm = LLM(language_model_only=True, **kw)
        except (TypeError, ValueError) as e:
            print(f"  engine does not take language_model_only here ({e}); loading without it",
                  flush=True)
            self.llm = LLM(**kw)
        self.tokenizer = self.llm.get_tokenizer()


class Comparator3Backend(_Comparator3Load, Comparator2Backend):
    pass


class Comparator3LLBackend(_Comparator3Load, Comparator2LLBackend):
    pass


COMPARATOR3_TAGS = {
    "comparator-gemma": (Comparator3Backend, COMPARATOR3_REPO, False),
    "comparator-gemma-ll": (Comparator3LLBackend, COMPARATOR3_REPO, False),
}
for _tag, (_cls, _repo, _b1) in COMPARATOR3_TAGS.items():
    harness.register(_tag, lambda _t=_tag, _c=_cls, _r=_repo, _b=_b1, **kw: _c(_t, _r, _b, **kw))

# conditions of the fourth revision
GOEMOTIONS_COND = "d3_goemotions"
STRESS_CONDITIONS = ([f"d2_k{k}" for k in (5, 20, 50)]
                     + [f"e2_d1_{n}" for n in ("k01", "kny", "kswap", "krand")]
                     + [f"e2_d3_{t}_{n}" for t in ("conv_go_awry", "wiki_corpus")
                        for n in ("k01", "kny", "kswap", "krand")])


# A third comparator family, Mistral-Small-24B-Instruct-2501 (text only, standard tokenizer
# files), read in the same two ways; with Qwen and Gemma the comparators then span model
# families from three developers. Weights are quantized to FP8 on load, as for Gemma.
COMPARATOR4_REPO = "mistralai/Mistral-Small-24B-Instruct-2501"
COMPARATOR2_PROFILES[COMPARATOR4_REPO] = {"max_model_len": 16384, "gpu_memory_utilization": 0.92,
                                          "max_num_seqs": 32, "enforce_eager": False,
                                          "quantization": "fp8"}
COMPARATOR4_TAGS = {
    "comparator-mistral": (Comparator3Backend, COMPARATOR4_REPO, False),
    "comparator-mistral-ll": (Comparator3LLBackend, COMPARATOR4_REPO, False),
}
for _tag, (_cls, _repo, _b1) in COMPARATOR4_TAGS.items():
    harness.register(_tag, lambda _t=_tag, _c=_cls, _r=_repo, _b=_b1, **kw: _c(_t, _r, _b, **kw))
BANKING77_COND = "d2_banking77"


# A deliberating comparator: the same Qwen3.6-27B checkpoint with its thinking mode switched
# on, asked the verbalized-JSON question of comparator-open. It contrasts a model that reasons
# in text before it answers with the same weights answering at once (comparator-open2), so any
# difference is due to deliberation alone. Thinking cannot run under a JSON grammar, so the
# reply is generated freely with the sampling settings the model card recommends for thinking
# mode (temperature 0.6, top-p 0.95, top-k 20, fixed seed), and the JSON object after the
# closing think tag is parsed by comparator_parse unchanged. A reply without a parsable object
# is recorded as an error line. The context is widened so a long prompt still leaves the full
# thinking budget.

THINK_MAX_TOKENS = 8192
THINK_MAX_MODEL_LEN = 24576
THINK_SAMPLING = {"temperature": 0.6, "top_p": 0.95, "top_k": 20, "seed": 20260924}


def think_final_json(text):
    """The JSON object a thinking reply ends with: the text after the last closing think tag,
    from its first opening brace to its last closing brace. Pure function."""
    tail = text.rsplit("</think>", 1)[-1]
    a, b = tail.find("{"), tail.rfind("}")
    if a < 0 or b <= a:
        raise ValueError("comparator-think: no JSON object after the reasoning")
    return tail[a:b + 1]


class Comparator2ThinkBackend(Comparator2Backend):
    def __init__(self, tag, repo, batch1=False, max_tokens=THINK_MAX_TOKENS):
        super().__init__(tag, repo, batch1=batch1, max_tokens=max_tokens)
        self.max_model_len = THINK_MAX_MODEL_LEN

    def _chat(self, prompt):
        msgs = [{"role": "user", "content": prompt}]
        return self.tokenizer.apply_chat_template(msgs, tokenize=False,
                                                  add_generation_prompt=True,
                                                  enable_thinking=True)

    def _prefetch_sync(self, chunk):
        import time
        from vllm import SamplingParams
        all_reqs = [r for rec in chunk for r in self._requests(rec)]
        budget = self.max_model_len - self.max_tokens
        reqs, prompts = [], []
        for key, qid, prompt, keys, n_report in all_reqs:
            prompt = self._chat(prompt)
            n_prompt_tok = len(self.tokenizer.encode(prompt, add_special_tokens=False))
            if n_prompt_tok > budget:
                self._cache[(key, qid)] = {
                    "probs": None, "answer": None,
                    "error": f"comparator: prompt is {n_prompt_tok} tokens, budget is {budget}",
                    "raw_text": None, "usage_in": n_prompt_tok, "usage_out": None,
                    "latency_mode": "batched", "batch_wall_s": 0.0, "n_requests": len(all_reqs)}
                continue
            reqs.append((key, qid, keys))
            prompts.append(prompt)
        if not prompts:
            return
        sp = SamplingParams(max_tokens=self.max_tokens, **THINK_SAMPLING)
        t0 = time.time()
        outputs = self.llm.generate(prompts, [sp] * len(prompts))
        wall = time.time() - t0
        for (key, qid, keys), out in zip(reqs, outputs):
            text = out.outputs[0].text
            usage_in = len(out.prompt_token_ids) if out.prompt_token_ids is not None else None
            usage_out = len(out.outputs[0].token_ids) if out.outputs[0].token_ids is not None else None
            try:
                probs, answer = comparator_parse(think_final_json(text), keys)
                err = None
            except ValueError as e:
                probs, answer, err = None, None, str(e)
            self._cache[(key, qid)] = {
                "probs": probs, "answer": answer, "error": err, "raw_text": text,
                "usage_in": usage_in, "usage_out": usage_out,
                "latency_mode": "batched", "batch_wall_s": wall, "n_requests": len(reqs)}


harness.register("comparator-open2-think",
                 lambda **kw: Comparator2ThinkBackend("comparator-open2-think", COMPARATOR2_REPO,
                                                      False, **kw))


# Batch-1 latency samples of every comparator, so that latency is compared one request at a
# time for all of them (Comparator2Backend.answer handles batch1). Qwen3-14B-AWQ gets an
# engine profile with its first run's context limit so the same batch-1 code path serves it.
COMPARATOR2_PROFILES.setdefault(COMPARATOR_REPO, {"max_model_len": 12288,
                                                  "gpu_memory_utilization": 0.90,
                                                  "max_num_seqs": 32, "enforce_eager": False})
COMPARATOR_B1_TAGS = {
    "comparator-gemma-b1": (Comparator3Backend, COMPARATOR3_REPO, True),
    "comparator-gemma-ll-b1": (Comparator3LLBackend, COMPARATOR3_REPO, True),
    "comparator-mistral-b1": (Comparator3Backend, COMPARATOR4_REPO, True),
    "comparator-mistral-ll-b1": (Comparator3LLBackend, COMPARATOR4_REPO, True),
    "comparator-open-b1": (Comparator3Backend, COMPARATOR_REPO, True),
}
for _tag, (_cls, _repo, _b1) in COMPARATOR_B1_TAGS.items():
    harness.register(_tag, lambda _t=_tag, _c=_cls, _r=_repo, _b=_b1, **kw: _c(_t, _r, _b, **kw))


# Gemma-4-31B and Mistral-Small-24B quantized to FP8 on load fail inside vLLM 0.30's torch.compile
# pass (InductorError "auto_functionalized was not removed" during the engine's profile run, an
# inductor bug with online FP8 quantization). Both run in eager mode instead, which skips the
# compile and CUDA-graph capture and keeps the FP8 weights; the numerics are the same, only the
# throughput is lower. The Qwen3.6-27B FP8 release is pre-quantized and keeps its compiled profile.
for _repo in (COMPARATOR3_REPO, COMPARATOR4_REPO):
    COMPARATOR2_PROFILES[_repo]["enforce_eager"] = True


# FP8 quantization on load does not run on the A100 either: in eager mode vLLM 0.30 selects the
# CUTLASS w8a8 kernel for online FP8, which fails on this GPU (RuntimeError
# cutlass_scaled_mm_sm80_epilogue during the profile run). Gemma-4-31B and Mistral-Small-24B
# therefore run in their native bfloat16 weights, which fit an 80 GB A100 (about 58 and 47 GB),
# still in eager mode. The Qwen3.6-27B FP8 release keeps its pre-quantized weights.
for _repo in (COMPARATOR3_REPO, COMPARATOR4_REPO):
    COMPARATOR2_PROFILES[_repo].pop("quantization", None)
    COMPARATOR2_PROFILES[_repo]["gpu_memory_utilization"] = 0.94
    COMPARATOR2_PROFILES[_repo]["enforce_eager"] = True
