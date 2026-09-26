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
