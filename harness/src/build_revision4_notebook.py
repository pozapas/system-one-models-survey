"""Build colab/run_revision4.ipynb and colab/revision4_upload.zip for the fourth revision runs.

Five parts, each runnable on its own runtime and all five at the same time (switches RUN_PART_A,
RUN_PART_B, RUN_PART_C1, RUN_PART_C2 and RUN_PART_C3 in the first code cell). Every job is rep 1
except the optional Jev latency sample (rep 6). Within each part the most important jobs run
first. All parts write to the same Drive folder; the status cell of whichever runtime finishes
last lists and archives every part's files.

  Part A, Colab L4:
    a. the open decision models laya-en, laya-ml, kev-0.8b, decider-2b, this-that-1.0, kev-9b and
       nimble-9b on d3_goemotions, then d2_banking77, with revision 1's per-family envs and pins
       (as revision 3 part 1a). laya-en's English head splits 192 - 16 tokens over the option
       labels and refused every 150-option question (1 token per label); at 77 options it has 2
       per label, which may pass or not, so its smoke test covers d3_goemotions only and
       d2_banking77 runs after d3_goemotions is answered.
    b. the four untuned Qwen3.5 backbones with key scoring (backbone-qwen35-*, revision 2 env
       and pins) on d3_goemotions and d2_banking77, after a smoke test with the self-check on.
    c. the Qwen3-14B-AWQ comparator, tag comparator-open, on d3_goemotions and d2_banking77.
       adapters.py registers no batch-1 tag for it, so it gets no batch-1 latency sample.
    e. optional: 40 Jev requests of d1_neutral (rep 6) from the cloud, with the API key from the
       Colab secret TYPESAFE_API_KEY, handed to the harness process through its environment
       only; skipped with a message when the secret is missing.
    d. the two 9B description-scoring backbones backbone-desc-qwen35-9b-base and
       backbone-desc-qwen35-9b on adapters.BACKBONE_DESC_CONDITIONS with P4_DESC_ROWS=4.
       Their third-revision smoke test ran out of memory in the self-check on d2_k150: the
       allocation of 2.40 GiB is the float64 log-softmax over the whole sequence in
       desc_logprobs_naive (1300 tokens x 248,320 vocabulary x 8 bytes), not the row loop that
       adapters.py now retries with fewer rows. The self-check therefore runs on d1_neutral and
       d3_emotion (where it passed before), and d2_k150 and d3_conv_go_awry (prompts up to 8,000
       tokens) get a 2-request smoke test with the check off, on the cached path of the full run.
  Part B, Colab L4: b05_strong_classifiers for baseline-deberta-large-clinc, -goemo, -banking,
    -d3 and -d1, in its own env, after a smoke test with the real pinned checkpoint on a few
    rows of every task.
  Part C1, Colab A100 80GB: Gemma-4-31B-it (comparator-gemma, comparator-gemma-ll).
  Part C2, Colab A100 80GB: Mistral-Small-24B-Instruct-2501 (comparator-mistral,
    comparator-mistral-ll).
    Gemma and Mistral run every condition Qwen3.6-27B covers: adapters.COMPARATOR_CONDITIONS,
    d3_goemotions, d2_banking77, d2_k150_oos and adapters.STRESS_CONDITIONS, after a smoke
    test of both modes. adapters.py registers no batch-1 tag for either, so neither gets a
    batch-1 latency sample.
  Part C3, Colab A100 80GB: comparator-open2-think (Qwen3.6-27B-FP8, thinking on, verbal
    readout) on d1_neutral, d1_calib, d2_k150, the four D3 tasks, d2_k150_oos, d3_goemotions and
    d2_banking77, after a 5-request smoke test of d1_neutral and d2_k150 that stops the tag
    when more than half the replies are error lines; then Qwen3.6-27B-FP8 (comparator-open2,
    comparator-open2-ll, revision 2 pins and profile) on d3_goemotions, d2_banking77 and
    adapters.STRESS_CONDITIONS without d2_k20, which both Qwen3.6 tags already answered in the
    second revision (unpacking the hand-back archive would otherwise overwrite those files).
  vLLM 0.30.0 in the env of revision 3 part 2 for every comparator.

A failed model or condition never stops the others; a condition counts as done only when every
request is answered. harness.py records a failing request as an error line and exits 0, so
every smoke test reads its own answer files.

The pins, package lists and install scripts come from build_revision_notebook.py and
build_revision2_notebook.py. The b05 training rows are frozen at build time by
b05_strong_classifiers.freeze_files (from the local b01/b04 caches) and written straight into
the zip, so no file is added under shared/.

Answers go to My Drive/Jev/paper4/colab/answers_revision4/<tag>/<cond>__rep1.jsonl, the layout of
shared/answers, so answers_revision4.zip unpacks straight into shared/answers. The build asserts
that no planned answer file exists there already.

Usage: python build_revision4_notebook.py [--check]
"""
import argparse
import ast
import builtins
import hashlib
import json
import os
import py_compile
import shlex
import symtable
import tempfile
import zipfile

import nbformat as nbf

import adapters as AD
import b05_strong_classifiers as B5
import build_revision_notebook as R1
import build_revision2_notebook as R2

HERE = os.path.dirname(os.path.abspath(__file__))
SHARED = os.path.dirname(HERE)
COLAB = os.path.join(SHARED, "colab")
INPUTS = os.path.join(COLAB, "inputs")
ANSWERS = os.path.join(SHARED, "answers")
OUT_NB = os.path.join(COLAB, "run_revision4.ipynb")
OUT_ZIP = os.path.join(COLAB, "revision4_upload.zip")

SRC_FILES = ["common.py", "harness.py", "adapters.py", "metrics.py", "b05_strong_classifiers.py"]
GOEMO = AD.GOEMOTIONS_COND
BANK = AD.BANKING77_COND
OOS = "d2_k150_oos"

# ---------------------------------------------------------------- part A
PLAN = list(R1.PLAN)                                  # revision 1 order, cheapest first
DECISION_TAGS = [p[0] for p in PLAN]
DECISION_CONDS = {t: [GOEMO, BANK] for t in DECISION_TAGS}
# laya-en may refuse 77 options (see the docstring): a refusal must not stop its d3_goemotions run
DECISION_SMOKE = {t: [GOEMO] if t == "laya-en" else [GOEMO, BANK] for t in DECISION_TAGS}
COMP_OPEN_CONDS = [GOEMO, BANK]
KEY_TAGS = ["backbone-qwen35-0.8b-base", "backbone-qwen35-2b-base", "backbone-qwen35-9b-base",
            "backbone-qwen35-9b"]                  # key scoring (BackboneOptScoreBackend)
KEY_CONDS = [GOEMO, BANK]
JEV_TAG, JEV_COND, JEV_REP, JEV_LIMIT = "jev-1.13.0", "d1_neutral", 6, 40
JEV_PKGS = ["typesafe-sdk==0.7.1", "python-dotenv", "httpx", "numpy"]   # the local SDK version
DESC_TAGS =["backbone-desc-qwen35-9b-base", "backbone-desc-qwen35-9b"]
DESC_CONDS = list(AD.BACKBONE_DESC_CONDITIONS)
DESC_CHECK_SMOKE = ["d1_neutral", "d3_emotion"]       # self-check on
DESC_PLAIN_SMOKE = ["d2_k150", "d3_conv_go_awry"]     # self-check off

# ---------------------------------------------------------------- part B
B5_TAG_CONDS = {}
for _task, (_g, _cond, _tag, *_rest) in B5.TASKS.items():
    B5_TAG_CONDS.setdefault(_tag, []).extend(B5.D1_CONDS if _task == "d1" else [_cond])
B5_GROUP_TAG = {B5.TASKS[t][0]: B5.TASKS[t][2] for t in B5.TASKS}
B5_TAGS = [B5_GROUP_TAG[g] for g in B5.GROUPS]
B5_PKGS = ["torch==2.8.0", "transformers==5.17.0", "sentencepiece==0.2.2", "protobuf",
           "huggingface_hub", "numpy"]
B5_FIELDS = sorted(["key", "condition", "rep", "model", "revision", "model_returned",
                    "served_temperature", "run_date", "latency_s", "usage_in", "answers"])

# ---------------------------------------------------------------- parts C1, C2, C3
GEMMA = ["comparator-gemma", "comparator-gemma-ll"]
MISTRAL = ["comparator-mistral", "comparator-mistral-ll"]
QWEN36 = ["comparator-open2", "comparator-open2-ll"]
THINK = "comparator-open2-think"
GEMMA_REV = "842da3794eaa0b77d5f08bae87a17459d91ff475"
MISTRAL_REV = "9527884be6e5616bdd54de542f9ae13384489724"  # 9527884be6, model_info 2026-09-29
# full parity with Qwen3.6-27B: its revision 2 conditions, the new tasks, then the stress set
FAMILY_CONDS = (list(AD.COMPARATOR_CONDITIONS) + [GOEMO, BANK, OOS]
                + [c for c in AD.STRESS_CONDITIONS if c not in AD.COMPARATOR_CONDITIONS])
C_SMOKE = ["d1_neutral", "d2_k150", "d3_conv_go_awry"]   # three question types, 150 options,
                                                           # the longest prompts
THINK_CONDS = (["d1_neutral", "d1_calib", "d2_k150", "d3_conv_go_awry", "d3_wiki_corpus",
                "d3_emotion", "d3_wiki_politeness", OOS, GOEMO, BANK])
THINK_SMOKE, THINK_SMOKE_N, THINK_MAX_ERR = ["d1_neutral", "d2_k150"], 5, 0.5
# batch-1 latency samples: the first 40 requests of d1_neutral per tag, as revision 2 did for
# Qwen3.6-27B (optional in the status: a failure never blocks ALL_DONE)
B1_COND, B1_LIMIT = "d1_neutral", 40
GEMMA_B1 = ["comparator-gemma-b1", "comparator-gemma-ll-b1"]
MISTRAL_B1 = ["comparator-mistral-b1", "comparator-mistral-ll-b1"]
OPEN_B1 = ["comparator-open-b1"]


def _exists(tag, cond, rep=1):
    return os.path.exists(os.path.join(ANSWERS, tag, f"{cond}__rep{rep}.jsonl"))


QWEN36_DROPPED = [c for c in AD.STRESS_CONDITIONS if any(_exists(t, c) for t in QWEN36)]
QWEN36_CONDS = [GOEMO, BANK] + [c for c in AD.STRESS_CONDITIONS if c not in QWEN36_DROPPED]

REVISIONS = dict(R1.REVISIONS)
for _repo, _sha in list(R2.REVISIONS.items()) + [(AD.COMPARATOR3_REPO, GEMMA_REV),
                                                 (AD.COMPARATOR4_REPO, MISTRAL_REV),
                                                 (B5.MODEL_ID, B5.MODEL_REV)]:
    assert REVISIONS.get(_repo, _sha) == _sha, _repo
    REVISIONS[_repo] = _sha
TAG_REPO = {t: R1.TAG_REPO[t] for t in DECISION_TAGS + ["comparator-open"]}
TAG_REPO.update({t: AD.BACKBONE_REPOS[AD.BACKBONE_DESC_OF[t]] for t in DESC_TAGS})
TAG_REPO.update({t: B5.MODEL_ID for t in B5_TAGS})
TAG_REPO.update({t: AD.COMPARATOR3_TAGS[t][1] for t in GEMMA})
TAG_REPO.update({t: AD.COMPARATOR4_TAGS[t][1] for t in MISTRAL})
TAG_REPO.update({t: AD.COMPARATOR2_TAGS[t][1] for t in QWEN36})
TAG_REPO.update({t: R2.TAG_REPO[t] for t in KEY_TAGS})
TAG_REPO[THINK] = AD.COMPARATOR2_REPO
TAG_REPO.update({t: AD.COMPARATOR_B1_TAGS[t][1] for t in GEMMA_B1 + MISTRAL_B1 + OPEN_B1})
TAG_REPO[JEV_TAG] = JEV_TAG          # the service pins the version; the record carries it

_MAN = json.load(open(os.path.join(INPUTS, "manifest.json"), encoding="utf-8"))


def _p(part, tag, conds, rep=1, n=None, optional=False):
    """Planned answer files: (part, tag, condition, rep, requests wanted, optional)."""
    return [(part, tag, c, rep, n or _MAN[c]["requests"], optional) for c in conds]


PLANNED = ([x for t in DECISION_TAGS for x in _p("A", t, DECISION_CONDS[t])]
           + [x for t in KEY_TAGS for x in _p("A", t, KEY_CONDS)]
           + _p("A", "comparator-open", COMP_OPEN_CONDS)
           + [x for t in OPEN_B1 for x in _p("A", t, [B1_COND], 1, B1_LIMIT, optional=True)]
           + [x for t in DESC_TAGS for x in _p("A", t, DESC_CONDS)]
           + _p("A", JEV_TAG, [JEV_COND], JEV_REP, JEV_LIMIT, optional=True)
           + [x for t in B5_TAGS for x in _p("B", t, B5_TAG_CONDS[t])]
           + [x for t in GEMMA for x in _p("C1", t, FAMILY_CONDS)]
           + [x for t in GEMMA_B1 for x in _p("C1", t, [B1_COND], 1, B1_LIMIT, optional=True)]
           + [x for t in MISTRAL for x in _p("C2", t, FAMILY_CONDS)]
           + [x for t in MISTRAL_B1 for x in _p("C2", t, [B1_COND], 1, B1_LIMIT, optional=True)]
           + _p("C3", THINK, THINK_CONDS)
           + [x for t in QWEN36 for x in _p("C3", t, QWEN36_CONDS)])
SHIP_INPUTS = sorted({x[2] for x in PLANNED} | set(DESC_CHECK_SMOKE + DESC_PLAIN_SMOKE
                                                   + C_SMOKE + THINK_SMOKE))

VLLM_INSTALL = ("set -e\nexport UV_CACHE_DIR=/content/uv-cache\n"
                "uv venv /content/envs/vllm_env --python 3.12 -q --allow-existing\n"
                "uv pip install --python /content/envs/vllm_env/bin/python -q "
                + " ".join(shlex.quote(p) for p in R2.VLLM_PKGS) + "\n")
NB_ROOT = "/content/p4"

# names of the earlier runs that must not survive in the generated notebook
STALE = ["revision3", "revision2", "RUN_PART1", "RUN_PART2", "revision_upload",
         "answers_revision/", "answers_revision.zip", "DONE_revision'", "DONE_revision\"",
         "ERROR_revision.txt", "run_log_revision.json", "COMPARATOR2_VARIANT"]

sha256 = R1.sha256
md = R1.md
code = R1.code


HELPERS = r'''
import subprocess, shutil, traceback, gc

def answer_counts(path):
    """(answered lines, error lines) of one answer file; (0, 0) when it does not exist."""
    ok = err = 0
    if os.path.exists(path):
        with open(path, encoding='utf-8') as fh:
            for l in fh:
                try:
                    j = json.loads(l)
                except json.JSONDecodeError:
                    continue
                if j.get('error'):
                    err += 1
                else:
                    ok += 1
    return ok, err

def n_ok(tag, cond):
    return answer_counts(f'{ANSWERS_DIR}/{tag}/{cond}__rep1.jsonl')[0]

def incomplete(tag, conds):
    return [c for c in conds if n_ok(tag, c) < EXPECTED[c]['requests']]

def unfinished(tag, conds):
    """Conditions with requests that have no line at all (answered or error), after a crash."""
    return [c for c in conds
            if sum(answer_counts(f'{ANSWERS_DIR}/{tag}/{c}__rep1.jsonl')) < EXPECTED[c]['requests']]

def smoke_counts(smoke_dir):
    """(answered lines, error lines, output tokens per answered question) of the smoke files."""
    ok = err = 0
    outs = []
    for root, _dirs, files in os.walk(smoke_dir):
        for fn in sorted(files):
            if not fn.endswith('.jsonl'):
                continue
            with open(os.path.join(root, fn), encoding='utf-8') as fh:
                for l in fh:
                    try:
                        j = json.loads(l)
                    except json.JSONDecodeError:
                        continue
                    if j.get('error'):
                        err += 1
                        continue
                    ok += 1
                    for a in (j.get('answers') or {}).values():
                        u = (a.get('raw') or {}).get('usage_out')
                        if u is not None:
                            outs.append(u)
    return ok, err, outs

def smoke_report(smoke_dir):
    """Error lines and the largest self-check difference over every smoke answer file.
    harness.py records a failed request, a failed self-check included, as an error line and
    exits 0, so the smoke gate reads the files instead of trusting the exit code."""
    errs, dmax = [], None
    for root, _dirs, files in os.walk(smoke_dir):
        for fn in sorted(files):
            if not fn.endswith('.jsonl'):
                continue
            with open(os.path.join(root, fn), encoding='utf-8') as fh:
                for l in fh:
                    try:
                        j = json.loads(l)
                    except json.JSONDecodeError:
                        continue
                    if j.get('error'):
                        errs.append(f"{fn}: {j['error'][:200]}")
                        continue
                    for a in (j.get('answers') or {}).values():
                        d = (a.get('raw') or {}).get('check_max_abs_dprob')
                        if d is not None:
                            dmax = d if dmax is None else max(dmax, d)
    return errs, dmax

def mark(tag, ok, detail=''):
    """DONE_revision4 or ERROR_revision4.txt in the tag folder; an earlier error marker of this
    notebook is kept as ERROR_revision4_earlier.txt."""
    d = f'{ANSWERS_DIR}/{tag}'
    os.makedirs(d, exist_ok=True)
    if os.path.exists(f'{d}/ERROR_revision4.txt'):
        os.replace(f'{d}/ERROR_revision4.txt', f'{d}/ERROR_revision4_earlier.txt')
    name = 'DONE_revision4' if ok else 'ERROR_revision4.txt'
    with open(f'{d}/{name}', 'w') as fh:
        fh.write(time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()) + '\n' + detail)
    print(f'=== {tag}: {"DONE" if ok else "ERROR"} {detail[:400]} ===', flush=True)

def is_done(tag):
    return os.path.exists(f'{ANSWERS_DIR}/{tag}/DONE_revision4')

def stream(cmd, log_path, env=None):
    """Run a command; every output line goes to the cell and to the log on Drive."""
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    with open(log_path, 'a', encoding='utf-8') as log:
        log.write(f'\n$ {" ".join(cmd)}\n'); log.flush()
        p = subprocess.Popen(cmd, cwd=SRC_DIR, env=env, stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT, text=True, bufsize=1)
        for line in p.stdout:
            print(line, end='', flush=True)
            log.write(line); log.flush()
        return p.wait()

def harness_env(env_name, answers_dir, extra=None):
    env = dict(os.environ)
    env['HF_HOME'] = '/content/hf'
    env['P4_INPUTS'] = INPUTS_DIR
    env['P4_ANSWERS'] = answers_dir
    env['P4_REVISIONS'] = json.dumps(REVISIONS)
    # ninja and any other console script of the env must be on PATH (FlashInfer JIT, Triton)
    env['PATH'] = f'/content/envs/{env_name}/bin:' + env.get('PATH', '')
    env.update(extra or {})
    return env

def harness(env_name, tag, conds, log_path, answers_dir=None, limit=None, extra=None):
    """Conditions in one process (the model loads once), rep 1."""
    cmd = [f'/content/envs/{env_name}/bin/python', f'{SRC_DIR}/harness.py', '--model', tag,
           '--cond', ','.join(conds), '--rep', '1']
    if limit:
        cmd += ['--limit', str(limit)]
    t0 = time.time()
    rc = stream(cmd, log_path, harness_env(env_name, answers_dir or ANSWERS_DIR, extra))
    return rc, time.time() - t0

def save_run_log():
    tmp = RUN_LOG_PATH + '.tmp'
    with open(tmp, 'w') as fh:
        json.dump(run_log, fh, indent=2)
    os.replace(tmp, RUN_LOG_PATH)

def free_gb():
    return shutil.disk_usage('/content').free / 1e9

def gpu_memory():
    subprocess.run(['nvidia-smi', '--query-gpu=memory.used', '--format=csv,noheader'])
'''


DECISION_RUNNER = r'''TAG = __TAG__
ENV_NAME = __ENV__
INSTALL = __INSTALL__
CONDS = __CONDS__   # rep 1 each, most important first
SMOKE_CONDS = __SMOKE__

if not (RUN_PART_A and RUN_DECISION_MODELS):
    print(f'{TAG}: skipped (RUN_PART_A = {RUN_PART_A}, RUN_DECISION_MODELS = {RUN_DECISION_MODELS})')
else:
    LOG = f'{ANSWERS_DIR}/{TAG}/run_log_{TAG}.txt'
    SMOKE_DIR = f'/content/smoke/{TAG}'
    # a fresh smoke folder on every run of the cell, so the smoke test and its timing are real
    shutil.rmtree(SMOKE_DIR, ignore_errors=True)
    try:
        print(f'=== {TAG}: building env {ENV_NAME} ===', flush=True)
        rc = stream(['bash', '-c', INSTALL], LOG)
        if rc:
            raise RuntimeError(f'env build failed (exit {rc}); see {LOG}')
        print(f'=== {TAG}: smoke test, 3 requests of each of {SMOKE_CONDS} ===', flush=True)
        rc, dt = harness(ENV_NAME, TAG, SMOKE_CONDS, LOG, answers_dir=SMOKE_DIR, limit=3)
        errs, _ = smoke_report(SMOKE_DIR)
        if rc or errs:
            raise RuntimeError(f'smoke test failed (exit {rc}, {len(errs)} error lines, first: '
                               f'{errs[:1]}); see {LOG}')
        n_req = sum(EXPECTED[c]['requests'] for c in CONDS)
        per = dt / (3 * len(SMOKE_CONDS))
        print(f'{TAG}: {per:.2f} s per request including the model load -> at most '
              f'{per * n_req / 60:.0f} min for {n_req} requests, '
              f'~{per * n_req / 3600 * UNITS_PER_HOUR["L4"]:.1f} compute units on an L4', flush=True)
        run_log.setdefault('models', {})[TAG] = {'smoke_s_per_request_incl_load': per,
                                                 'requests': n_req}
        for cond in CONDS:
            for attempt in (1, 2):
                rc, dt = harness(ENV_NAME, TAG, [cond], LOG)
                ok, err = answer_counts(f'{ANSWERS_DIR}/{TAG}/{cond}__rep1.jsonl')
                want = EXPECTED[cond]['requests']
                print(f'[{TAG}] {cond} attempt {attempt}: exit {rc}, {dt / 60:.1f} min, '
                      f'{ok}/{want} answered, {err} error lines', flush=True)
                run_log['models'][TAG][f'{cond}_min_attempt{attempt}'] = dt / 60
                if ok >= want:
                    break
        missing = incomplete(TAG, CONDS)
        mark(TAG, not missing, f'incomplete: {missing}' if missing else '')
    except Exception:
        mark(TAG, False, traceback.format_exc())
    finally:
        save_run_log()
        gc.collect()
        gpu_memory()
'''

BACKBONE_RUNNER = r'''TAG = __TAG__
ENV_NAME = 'backbone'
INSTALL = __INSTALL__
CONDS = __CONDS__                  # rep 1 each
CHECK_SMOKE = __CHECK_SMOKE__      # smoke with the self-check on
PLAIN_SMOKE = __PLAIN_SMOKE__      # smoke with the self-check off (may be empty)
EXTRA = __EXTRA__

if not (__SWITCH__):
    print(f'{TAG}: skipped (switch __SWITCH_TEXT__ is off)')
else:
    LOG = f'{ANSWERS_DIR}/{TAG}/run_log_{TAG}.txt'
    SMOKE_DIR = f'/content/smoke/{TAG}'
    shutil.rmtree(SMOKE_DIR, ignore_errors=True)
    try:
        print(f'=== {TAG}: building env {ENV_NAME} ===', flush=True)
        rc = stream(['bash', '-c', INSTALL], LOG)
        if rc:
            raise RuntimeError(f'env build failed (exit {rc}); see {LOG}')
        # For description scoring the full-sequence self-check takes a float64 log-softmax over
        # every prompt position, 2.4 GiB on a d2_k150 prompt, which does not fit next to 9B
        # weights on an L4. It runs on d1_neutral and d3_emotion there; d2_k150 and
        # d3_conv_go_awry are smoke-tested with the check off.
        print(f'=== {TAG}: smoke test with the self-check, 2 requests each of {CHECK_SMOKE} ===',
              flush=True)
        rc1, dt1 = harness(ENV_NAME, TAG, CHECK_SMOKE, LOG, answers_dir=SMOKE_DIR, limit=2,
                           extra=dict(EXTRA, P4_OPTSCORE_CHECK='100'))
        errs, dmax = smoke_report(SMOKE_DIR)
        rc2, dt2 = 0, 0.0
        if PLAIN_SMOKE:
            print(f'=== {TAG}: smoke test without the self-check, 2 requests of {PLAIN_SMOKE} ===',
                  flush=True)
            rc2, dt2 = harness(ENV_NAME, TAG, PLAIN_SMOKE, LOG, answers_dir=SMOKE_DIR, limit=2,
                               extra=dict(EXTRA, P4_OPTSCORE_CHECK='0'))
            errs, _ = smoke_report(SMOKE_DIR)
        print(f'{TAG}: smoke {dt1 + dt2:.0f} s including the model loads; largest self-check '
              f'difference {dmax}', flush=True)
        if rc1 or rc2 or errs:
            raise RuntimeError(f'smoke test failed (exit {rc1}/{rc2}, {len(errs)} error lines, '
                               f'first: {errs[:1]}); see {LOG}')
        if dmax is None:
            raise RuntimeError(f'the smoke answers carry no self-check value; see {LOG}')
        n_req = sum(EXPECTED[c]['requests'] for c in CONDS)
        run_log.setdefault('models', {})[TAG] = {'smoke_s_incl_loads': dt1 + dt2,
                                                 'requests': n_req,
                                                 'smoke_check_max_abs_dprob': dmax}
        print(f'=== {TAG}: full run, {len(CONDS)} conditions, {n_req} requests ===', flush=True)
        rc, dt = harness(ENV_NAME, TAG, CONDS, LOG, extra=dict(EXTRA, P4_OPTSCORE_CHECK='0'))
        print(f'[{TAG}] one-process run: exit {rc}, {dt / 60:.1f} min', flush=True)
        run_log['models'][TAG]['full_min'] = dt / 60
        save_run_log()
        # a condition left incomplete (a crash, a disconnect) is retried on its own
        for c in incomplete(TAG, CONDS):
            rc, dt = harness(ENV_NAME, TAG, [c], LOG, extra=dict(EXTRA, P4_OPTSCORE_CHECK='0'))
            print(f'[{TAG}] retry {c}: exit {rc}, {dt / 60:.1f} min', flush=True)
        missing = incomplete(TAG, CONDS)
        mark(TAG, not missing, f'incomplete: {missing}' if missing else '')
    except Exception:
        mark(TAG, False, traceback.format_exc())
    finally:
        save_run_log()
        gc.collect()
        gpu_memory()
'''

VLLM_RUNNER = r'''CELL = __CELL__
ENV_NAME = 'vllm_env'
INSTALL = __INSTALL__
PLAN_TAGS = __PLAN__          # [(tag, conditions)] in run order, rep 1
SMOKE_CONDS = __SMOKE__
SMOKE_N = __SMOKE_N__
# share of smoke replies that may be error lines before a tag is stopped (0: none may be)
MAX_ERR_SHARE = __MAX_ERR__
# retry conditions with error lines (True), or only conditions with requests that got no line
# at all (False: a sampled reply that fails to parse fails again under the fixed seed)
RETRY_ERRORS = __RETRY_ERRORS__
REPO = __REPO__
NEEDS_A100 = __A100__
FREE_AFTER = __FREE__          # this cell is the last one that needs REPO on this part
VLLM_EXTRA = {'VLLM_LOGGING_LEVEL': 'INFO',
              # greedy decoding does not need the FlashInfer sampler
              'VLLM_USE_FLASHINFER_SAMPLER': '0'}

def smoke_per_question(sd, tag):
    """Engine time per question from the smoke answers (batch share, no engine start)."""
    per_q = []
    for c in SMOKE_CONDS:
        p = f'{sd}/{tag}/{c}__rep1.jsonl'
        if not os.path.exists(p):
            continue
        with open(p, encoding='utf-8') as fh:
            for l in fh:
                j = json.loads(l)
                if j.get('error'):
                    continue
                for a in j['answers'].values():
                    r = a.get('raw') or {}
                    if r.get('batch_wall_s') is not None and r.get('n_requests'):
                        per_q.append(r['batch_wall_s'] / r['n_requests'])
    return sum(per_q) / len(per_q) if per_q else None

if not (__SWITCH__):
    print(f'{CELL}: skipped (switch __SWITCH_TEXT__ is off)')
elif NEEDS_A100 and not PART_C_GPU_OK:
    print(f'{CELL}: skipped, this part needs an A100 or H100 (this runtime: {gpu_info})')
else:
    first_log = f'{ANSWERS_DIR}/{PLAN_TAGS[0][0]}/run_log_{PLAN_TAGS[0][0]}.txt'
    print(f'{CELL}: free disk under /content {free_gb():.0f} GB', flush=True)
    rc = stream(['bash', '-c', INSTALL + f'/content/envs/{ENV_NAME}/bin/python -c "import vllm, torch; '
                 f'print(\'vllm\', vllm.__version__, \'torch\', torch.__version__)"'], first_log)
    if rc:
        for tag, _conds in PLAN_TAGS:
            mark(tag, False, f'vLLM env build failed (exit {rc}); see {first_log}')
    else:
        go = []
        for tag, conds in PLAN_TAGS:
            if not (SMOKE_CONDS and (__DO_SMOKE__)):
                go.append((tag, conds))
                continue
            sd = f'/content/smoke/{tag}'
            shutil.rmtree(sd, ignore_errors=True)
            log = f'{ANSWERS_DIR}/{tag}/run_log_{tag}.txt'
            print(f'=== {tag}: smoke test, {SMOKE_N} requests each of {SMOKE_CONDS} ===', flush=True)
            try:
                rc, dt = harness(ENV_NAME, tag, SMOKE_CONDS, log, answers_dir=sd, limit=SMOKE_N,
                                 extra=VLLM_EXTRA)
                errs, _ = smoke_report(sd)
                n_ok_s, n_err_s, outs = smoke_counts(sd)
            except Exception:
                rc, dt, errs, n_ok_s, n_err_s, outs = -1, 0.0, [traceback.format_exc()], 0, 1, []
            share = n_err_s / max(n_ok_s + n_err_s, 1)
            s = smoke_per_question(sd, tag)
            n_q = sum(EXPECTED[c]['decisions'] for c in conds)
            print(f'{tag}: smoke {dt:.0f} s including the engine start (exit {rc}, {n_ok_s} '
                  f'answered, {n_err_s} error lines)', flush=True)
            if errs:
                print(f'{tag}: first smoke error: {errs[0]}', flush=True)
            if outs:
                print(f'{tag}: mean output tokens per question in the smoke test '
                      f'{sum(outs) / len(outs):.0f} (max {max(outs)}) -> about '
                      f'{sum(outs) / len(outs) * n_q / 1e6:.1f} M output tokens for the {n_q} '
                      f'questions', flush=True)
            if s is not None:
                print(f'{tag}: {s:.2f} s per question in the smoke batches -> about '
                      f'{s * n_q / 60:.0f} min for the {n_q} questions; small smoke batches '
                      f'overstate batched time', flush=True)
            run_log.setdefault('models', {}).setdefault(tag, {}).update(
                {'smoke_s_incl_load': dt, 'smoke_s_per_question': s,
                 'smoke_answered': n_ok_s, 'smoke_error_lines': n_err_s,
                 'smoke_mean_output_tokens': sum(outs) / len(outs) if outs else None})
            if rc or n_ok_s == 0 or share > MAX_ERR_SHARE:
                mark(tag, False, f'smoke test failed (exit {rc}, {n_err_s} of '
                                 f'{n_ok_s + n_err_s} replies are error lines): {errs[:1]}')
            else:
                go.append((tag, conds))
        for tag, conds in go:
            log = f'{ANSWERS_DIR}/{tag}/run_log_{tag}.txt'
            print(f'=== {tag}: {len(conds)} conditions, '
                  f'{sum(EXPECTED[c]["requests"] for c in conds)} requests: {conds} ===', flush=True)
            try:
                rc, dt = harness(ENV_NAME, tag, conds, log, extra=VLLM_EXTRA)
                print(f'[{tag}] one-process run: exit {rc}, {dt / 60:.1f} min', flush=True)
                run_log.setdefault('models', {}).setdefault(tag, {})['full_min'] = dt / 60
                save_run_log()
                # a crash in the one-process run leaves later conditions incomplete; each is
                # retried in its own process, finished requests are skipped
                for c in (incomplete(tag, conds) if RETRY_ERRORS else unfinished(tag, conds)):
                    rc, dt = harness(ENV_NAME, tag, [c], log, extra=VLLM_EXTRA)
                    print(f'[{tag}] retry {c}: exit {rc}, {dt / 60:.1f} min', flush=True)
                missing = incomplete(tag, conds)
                detail = ', '.join(f'{c}: {n_ok(tag, c)}/{EXPECTED[c]["requests"]}' for c in missing)
                mark(tag, not missing, f'incomplete: {detail}' if missing else '')
            except Exception:
                mark(tag, False, traceback.format_exc())
            save_run_log()
        # the downloaded weights of this model only, once every tag of it is done
        if (NEEDS_A100 and FREE_AFTER and FREE_DISK_AFTER_DONE
                and all(is_done(t) for t, _c in PLAN_TAGS)):
            cache = '/content/hf/hub/models--' + REPO.replace('/', '--')
            shutil.rmtree(cache, ignore_errors=True)
            print(f'{CELL}: removed the downloaded weights in {cache}; free disk {free_gb():.0f} GB')
    save_run_log()
    gpu_memory()
'''

B05_RUNNER = r'''ENV_NAME = 'b05'
PYBIN = f'/content/envs/{ENV_NAME}/bin/python'
INSTALL = __INSTALL__
B05 = f'{SRC_DIR}/b05_strong_classifiers.py'
GROUP_TAG = __GROUP_TAG__      # group -> tag
TAG_CONDS = __TAG_CONDS__      # tag -> conditions
B05_MODEL, B05_REV = __MODEL__, __REV__
SMOKE_TEST_N = __SMOKE_N__     # answered items per condition in the smoke run
FIELDS = __FIELDS__            # the record fields of the earlier baseline answers

def b05_env():
    env = dict(os.environ)
    env['HF_HOME'] = '/content/hf'
    env['P4_INPUTS'] = INPUTS_DIR
    env['P4_B05_DATA'] = B05_DATA_DIR
    env['P4_ANSWERS'] = ANSWERS_DIR
    env['PATH'] = f'/content/envs/{ENV_NAME}/bin:' + env.get('PATH', '')
    return env

if not RUN_PART_B:
    print(f'part B skipped (RUN_PART_B = {RUN_PART_B})')
else:
    groups = [g for g in B05_GROUPS if g in GROUP_TAG]
    LOG = f'{ANSWERS_DIR}/run_log_b05.txt'
    SMOKE_DIR = '/content/smoke/b05'
    shutil.rmtree(SMOKE_DIR, ignore_errors=True)
    smoke_ok = False
    try:
        print(f'=== part B: building env {ENV_NAME} ===', flush=True)
        rc = stream(['bash', '-c', INSTALL], LOG)
        if rc:
            raise RuntimeError(f'env build failed (exit {rc}); see {LOG}')
        # the real pinned checkpoint on a few rows of every task, one epoch: tokenizer, bf16
        # training with 512-token micro-batches, answers and the fit file
        print(f'=== part B: smoke test with {B05_MODEL}@{B05_REV[:8]} on groups {groups} ===',
              flush=True)
        t0 = time.time()
        rc = stream([PYBIN, B05, 'run', '--smoke', '--model', B05_MODEL, '--revision', B05_REV,
                     '--groups', ','.join(groups), '--answers', SMOKE_DIR], LOG, env=b05_env())
        problems = []
        for g in groups:
            tag = GROUP_TAG[g]
            for c in TAG_CONDS[tag]:
                p = f'{SMOKE_DIR}/{tag}/{c}__rep1.jsonl'
                if not os.path.exists(p) or not os.path.exists(f'{SMOKE_DIR}/{tag}/{c}__fit.json'):
                    problems.append(f'{tag}/{c}: missing')
                    continue
                with open(p, encoding='utf-8') as fh:
                    recs = [json.loads(l) for l in fh if l.strip()]
                if len(recs) != SMOKE_TEST_N or any(r.get('error') for r in recs):
                    problems.append(f'{tag}/{c}: {len(recs)} lines')
                elif sorted(recs[0]) != FIELDS or recs[0]['revision'] != B05_REV:
                    problems.append(f'{tag}/{c}: fields {sorted(recs[0])}, revision {recs[0]["revision"]}')
        run_log.setdefault('models', {})['b05'] = {'smoke_min': (time.time() - t0) / 60}
        if rc or problems:
            raise RuntimeError(f'smoke test failed (exit {rc}): {problems}; see {LOG}')
        smoke_ok = True
    except Exception:
        tb = traceback.format_exc()
        for g in groups:
            mark(GROUP_TAG[g], False, tb)
    if smoke_ok:
        for g in groups:
            tag = GROUP_TAG[g]
            try:
                for attempt in (1, 2):
                    print(f'=== {tag}: group {g}, attempt {attempt} ===', flush=True)
                    t0 = time.time()
                    rc = stream([PYBIN, B05, 'run', '--groups', g], LOG, env=b05_env())
                    run_log['models'].setdefault(tag, {})[f'attempt{attempt}_min'] = (time.time() - t0) / 60
                    missing = incomplete(tag, TAG_CONDS[tag])
                    print(f'[{tag}] exit {rc}, {(time.time() - t0) / 60:.1f} min, incomplete: {missing}',
                          flush=True)
                    if not missing:
                        break
                mark(tag, not missing, f'incomplete: {missing}' if missing else '')
            except Exception:
                mark(tag, False, traceback.format_exc())
            save_run_log()
    save_run_log()
    gpu_memory()
'''

B1_RUNNER = r'''CELL = __CELL__
ENV_NAME = 'vllm_env'
INSTALL = __INSTALL__
B1_TAGS = __TAGS__             # each runs the first LIMIT requests of COND one request at a time
COND, LIMIT = __COND__, __LIMIT__
REPO = __REPO__
NEEDS_A100 = __A100__
MAIN_TAGS = __MAIN__           # the batched tags of this model on this part (for the disk cleanup)
B1_EXTRA = {'VLLM_LOGGING_LEVEL': 'INFO', 'VLLM_USE_FLASHINFER_SAMPLER': '0'}

if not (__SWITCH__):
    print(f'{CELL}: skipped (switch __SWITCH_TEXT__ is off)')
elif NEEDS_A100 and not PART_C_GPU_OK:
    print(f'{CELL}: skipped, this part needs an A100 or H100 (this runtime: {gpu_info})')
else:
    first_log = f'{ANSWERS_DIR}/{B1_TAGS[0]}/run_log_{B1_TAGS[0]}.txt'
    rc = stream(['bash', '-c', INSTALL], first_log)     # the env of the batched cell, reused
    for tag in B1_TAGS:
        log = f'{ANSWERS_DIR}/{tag}/run_log_{tag}.txt'
        path = f'{ANSWERS_DIR}/{tag}/{COND}__rep1.jsonl'
        if rc:
            mark(tag, False, f'vLLM env build failed (exit {rc}); see {first_log}')
            continue
        print(f'=== {tag}: batch-1 latency sample, the first {LIMIT} requests of {COND} ===',
              flush=True)
        try:
            rc_h, dt = harness(ENV_NAME, tag, [COND], log, limit=LIMIT, extra=B1_EXTRA)
            ok, err = answer_counts(path)
            lats = []
            if os.path.exists(path):
                with open(path, encoding='utf-8') as fh:
                    for l in fh:
                        j = json.loads(l)
                        if not j.get('error') and j.get('latency_s') is not None:
                            lats.append(j['latency_s'])
            med = sorted(lats)[len(lats) // 2] if lats else None
            print(f'[{tag}] exit {rc_h}, {ok}/{LIMIT} answered, {err} error lines, median latency '
                  f'{med} s per request, {dt / 60:.1f} min including the engine start', flush=True)
            run_log.setdefault('models', {})[tag] = {'answered': ok, 'error_lines': err,
                                                     'median_latency_s': med, 'min': dt / 60}
            mark(tag, ok >= LIMIT, '' if ok >= LIMIT else f'{ok}/{LIMIT} answered')
        except Exception:
            mark(tag, False, traceback.format_exc())
        save_run_log()
    # this is the last cell that needs the weights on this part
    if (NEEDS_A100 and FREE_DISK_AFTER_DONE
            and all(is_done(t) for t in MAIN_TAGS + B1_TAGS)):
        cache = '/content/hf/hub/models--' + REPO.replace('/', '--')
        shutil.rmtree(cache, ignore_errors=True)
        print(f'{CELL}: removed the downloaded weights in {cache}; free disk {free_gb():.0f} GB')
    save_run_log()
    gpu_memory()
'''

JEV_RUNNER = r'''TAG = __TAG__
ENV_NAME = 'jev'
INSTALL = __INSTALL__
COND, REP, LIMIT = __COND__, __REP__, __LIMIT__

if not (RUN_PART_A and RUN_JEV_LATENCY):
    print(f'Jev latency: skipped (RUN_PART_A = {RUN_PART_A}, RUN_JEV_LATENCY = {RUN_JEV_LATENCY})')
else:
    _key = None
    try:
        from google.colab import userdata
        _key = userdata.get('TYPESAFE_API_KEY')
    except Exception as _e:
        print('Jev latency: skipped. The Colab secret TYPESAFE_API_KEY is missing, or this '
              f'notebook has no access to it ({type(_e).__name__}). Add it under Secrets (the key '
              'icon on the left) and switch on notebook access to run this cell.')
    if _key is not None and not str(_key).strip():
        print('Jev latency: skipped. The Colab secret TYPESAFE_API_KEY is empty.')
        _key = None
    if _key:
        LOG = f'{ANSWERS_DIR}/{TAG}/run_log_{TAG}.txt'
        path = f'{ANSWERS_DIR}/{TAG}/{COND}__rep{REP}.jsonl'
        try:
            print(f'=== Jev latency: building env {ENV_NAME} ===', flush=True)
            rc = stream(['bash', '-c', INSTALL], LOG)
            if rc:
                raise RuntimeError(f'env build failed (exit {rc}); see {LOG}')
            # the key reaches the harness process through its environment only; it is never
            # printed, logged or written to a file
            cmd = [f'/content/envs/{ENV_NAME}/bin/python', f'{SRC_DIR}/harness.py', '--model',
                   'jev', '--cond', COND, '--rep', str(REP), '--limit', str(LIMIT)]
            t0 = time.time()
            rc = stream(cmd, LOG, harness_env(ENV_NAME, ANSWERS_DIR,
                                               {'TYPESAFE_API_KEY': str(_key).strip()}))
            ok, err = answer_counts(path)
            lats = []
            if os.path.exists(path):
                with open(path, encoding='utf-8') as fh:
                    for l in fh:
                        j = json.loads(l)
                        if not j.get('error') and j.get('latency_s') is not None:
                            lats.append(j['latency_s'])
            med = sorted(lats)[len(lats) // 2] if lats else None
            print(f'[{TAG}] {COND} rep {REP}: exit {rc}, {ok}/{LIMIT} answered, {err} error lines, '
                  f'median latency {med} s, {(time.time() - t0) / 60:.1f} min', flush=True)
            run_log.setdefault('models', {})[TAG] = {'answered': ok, 'error_lines': err,
                                                     'median_latency_s': med}
            mark(TAG, ok >= LIMIT, '' if ok >= LIMIT else f'{ok}/{LIMIT} answered')
        except Exception as _e:
            mark(TAG, False, f'{type(_e).__name__}: {_e}')
        finally:
            _key = None
            save_run_log()
'''

STATUS = r'''import datetime, glob, uuid, zipfile

PLANNED = __PLANNED__   # [(part, tag, condition, rep, requests wanted, optional)]

def scan(path):
    ok = err = 0
    revs, ntok, trunc, errs = set(), 0, 0, {}
    with open(path, encoding='utf-8') as fh:
        for line in fh:
            try:
                j = json.loads(line)
            except json.JSONDecodeError:
                continue
            if j.get('error'):
                err += 1
                e = j['error']
                if 'max_len' in e or 'max_model_len' in e or 'budget' in e:
                    trunc += 1
                errs[e[:80]] = errs.get(e[:80], 0) + 1
                continue
            ok += 1
            revs.add(j.get('revision'))
            for a in j['answers'].values():
                ntok = max(ntok, (a.get('raw') or {}).get('n_prompt_tokens') or 0)
    return ok, err, revs, ntok, trunc, errs

status, problems = {}, []
for part, tag, cond, rep, want, optional in PLANNED:
    path = f'{ANSWERS_DIR}/{tag}/{cond}__rep{rep}.jsonl'
    key = f'{tag}/{cond}__rep{rep}'
    if not os.path.exists(path):
        status[key] = f'MISSING (part {part}{", optional" if optional else ""})'
        if not optional:
            problems.append(key)
        continue
    ok, err, revs, ntok, trunc, errs = scan(path)
    rev_ok = revs == {REVISIONS.get(TAG_REPO[tag], TAG_REPO[tag])}
    note = (f'{ok}/{want} answered, {err} error lines ({trunc} over the length limit), '
            f'revision {"ok" if rev_ok else revs}')
    if ntok:
        note += f', longest prompt {ntok} tokens'
    complete = ok >= want and rev_ok
    status[key] = ('OK ' if complete else 'INCOMPLETE ') + note
    if errs:
        status[key] += f', errors: {errs}'
    if not complete and not optional:
        problems.append(key)

for k, v in status.items():
    print(f'{k:62s} {v}')
# every part's files are read from Drive, whichever runtime wrote them; files another runtime
# wrote in the last minutes may not be visible yet, so rerun this cell if one shows as MISSING
print()
for part in sorted({x[0] for x in PLANNED}):
    keys = [f'{x[1]}/{x[2]}__rep{x[3]}' for x in PLANNED if x[0] == part]
    n_ok_part = sum(status[k].startswith('OK') for k in keys)
    n_missing = sum(status[k].startswith('MISSING') for k in keys)
    print(f'part {part:3s}: {n_ok_part}/{len(keys)} files complete, {n_missing} missing')

# the logs of the runtimes, merged read-only into one file; each runtime writes only its own.
# Temporary names carry a random suffix: two runtimes can have the same process id.
merged = {'parts': {}, 'end': datetime.datetime.utcnow().isoformat() + 'Z', 'status': status,
          'revisions_pinned': REVISIONS}
for p in sorted(glob.glob(f'{ANSWERS_DIR}/run_log_revision4_part*.json')):
    try:
        merged['parts'][os.path.basename(p)] = json.load(open(p))
    except Exception as e:
        merged['parts'][os.path.basename(p)] = f'unreadable: {e}'
tmp = f'{ANSWERS_DIR}/run_log_revision4.json.{uuid.uuid4().hex}.tmp'
with open(tmp, 'w') as fh:
    json.dump(merged, fh, indent=2)
os.replace(tmp, f'{ANSWERS_DIR}/run_log_revision4.json')

if problems:
    print(f'\n{len(problems)} file(s) missing or incomplete. A part not run yet shows as MISSING; '
          'otherwise re-run the cell of that model: finished requests are skipped.')
else:
    with open(f'{ANSWERS_DIR}/ALL_DONE_revision4', 'w') as fh:
        fh.write(merged['end'] + '\n')
    print('\nEvery planned answer file is complete. ALL_DONE_revision4 written.')

# the hand-back archive next to the folder on Drive: answer files, fit files of the trained
# baselines, DONE markers and the run logs; console logs and tracebacks stay on Drive only.
# Written under a temporary name and then renamed, so two runtimes never leave a torn archive.
archive = f'{DRIVE_ROOT}/answers_revision4.zip'
tmp = f'{archive}.{uuid.uuid4().hex}.tmp'
n_files = 0
with zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as z:
    for root, _dirs, files in os.walk(ANSWERS_DIR):
        for fn in sorted(files):
            if (fn.endswith('.jsonl') or fn.endswith('__fit.json') or fn == 'DONE_revision4'
                    or fn == 'ALL_DONE_revision4'
                    or (fn.startswith('run_log_revision4') and fn.endswith('.json'))):
                full = os.path.join(root, fn)
                z.write(full, os.path.relpath(full, ANSWERS_DIR))
                n_files += 1
os.replace(tmp, archive)
print(f'hand-back archive: {archive} ({n_files} files)')
'''


def _consistency(man):
    """Build-time checks on the plan, before anything is written."""
    assert R2.VLLM_VERSION == "0.30.0" and "vllm==0.30.0" in R2.VLLM_PKGS
    assert DECISION_TAGS == ["laya-en", "laya-ml", "kev-0.8b", "decider-2b", "this-that-1.0",
                             "kev-9b", "nimble-9b"], DECISION_TAGS
    assert man[GOEMO]["requests"] == 492 and man[BANK]["requests"] == 616
    assert man[OOS]["requests"] == 800 and man[OOS]["derived_from"] == "d2_k150"
    assert set(DESC_TAGS) <= set(AD.BACKBONE_DESC_OF)
    for t in DESC_TAGS:
        assert TAG_REPO[t] == R2.TAG_REPO[AD.BACKBONE_DESC_OF[t]], t
    assert AD.COMPARATOR3_REPO == "google/gemma-4-31B-it"
    assert AD.COMPARATOR4_REPO == "mistralai/Mistral-Small-24B-Instruct-2501"
    for t in (DECISION_TAGS + DESC_TAGS + KEY_TAGS + GEMMA + MISTRAL + QWEN36
              + ["comparator-open", THINK, "jev"]):
        assert t in AD.harness.BACKENDS, t
    assert AD.THINK_MAX_TOKENS == 8192 and AD.THINK_MAX_MODEL_LEN == 24576
    for part, tag, cond, rep, n, optional in PLANNED:
        assert tag == JEV_TAG or TAG_REPO[tag] in REVISIONS, tag
        assert cond in man, cond
        # nothing planned may overwrite an existing answer file when the hand-back is unpacked
        assert not _exists(tag, cond, rep), f"{tag}/{cond}__rep{rep}.jsonl exists in shared/answers"
    keys = [(x[1], x[2], x[3]) for x in PLANNED]
    assert len(keys) == len(set(keys))
    for c in DESC_CHECK_SMOKE + DESC_PLAIN_SMOKE:
        assert c in DESC_CONDS, c
    assert QWEN36_DROPPED == ["d2_k20"], QWEN36_DROPPED
    # every comparator covers every condition Qwen3.6-27B covers (revision 2 and this run)
    qwen_all = set(AD.COMPARATOR_CONDITIONS) | {OOS} | set(QWEN36_CONDS) | set(QWEN36_DROPPED)
    assert set(FAMILY_CONDS) == qwen_all, sorted(qwen_all ^ set(FAMILY_CONDS))
    assert set(THINK_SMOKE) <= set(THINK_CONDS)
    for t in GEMMA_B1 + MISTRAL_B1 + OPEN_B1:
        assert t in AD.harness.BACKENDS and AD.COMPARATOR_B1_TAGS[t][2] is True, t
    assert [AD.COMPARATOR_B1_TAGS[t][1] for t in GEMMA_B1] == [AD.COMPARATOR3_REPO] * 2
    assert [AD.COMPARATOR_B1_TAGS[t][1] for t in MISTRAL_B1] == [AD.COMPARATOR4_REPO] * 2
    assert AD.COMPARATOR_B1_TAGS[OPEN_B1[0]][1] == TAG_REPO["comparator-open"]


def b1_cell(cell, tags, repo, a100, main, switch):
    return (B1_RUNNER.replace("__CELL__", repr(cell))
            .replace("__INSTALL__", repr(VLLM_INSTALL))
            .replace("__TAGS__", repr(tags))
            .replace("__COND__", repr(B1_COND)).replace("__LIMIT__", repr(B1_LIMIT))
            .replace("__REPO__", repr(repo)).replace("__A100__", repr(a100))
            .replace("__MAIN__", repr(main))
            .replace("__SWITCH_TEXT__", switch).replace("__SWITCH__", switch))


def build(check=False):
    man = json.load(open(os.path.join(INPUTS, "manifest.json"), encoding="utf-8"))
    _consistency(man)
    for c in SHIP_INPUTS:
        assert sha256(os.path.join(INPUTS, man[c]["file"])) == man[c]["sha256"], c
    expected = {c: {"file": man[c]["file"], "sha256": man[c]["sha256"],
                    "requests": man[c]["requests"], "decisions": man[c]["decisions"]}
                for c in SHIP_INPUTS}
    src_sha = {f: sha256(os.path.join(HERE, f)) for f in SRC_FILES}
    print("freezing the b05 training rows (b01/b04 caches) ...", flush=True)
    data = B5.freeze_files()
    data_sha = {fn: hashlib.sha256(b).hexdigest() for fn, b in data.items()}

    # ---------------------------------------------------------------- the upload zip
    with zipfile.ZipFile(OUT_ZIP, "w", zipfile.ZIP_DEFLATED) as z:
        for f in SRC_FILES:
            z.write(os.path.join(HERE, f), f"shared/src/{f}")
        for c in SHIP_INPUTS:
            z.write(os.path.join(INPUTS, man[c]["file"]), f"shared/colab/inputs/{man[c]['file']}")
        z.write(os.path.join(INPUTS, "manifest.json"), "shared/colab/inputs/manifest.json")
        for fn, b in sorted(data.items()):
            z.writestr(f"shared/data/b05/{fn}", b)
    zip_sha = sha256(OUT_ZIP)

    cells = []
    cells.append(md(
        "# Paper 4, fourth revision runs\n\n"
        "Five parts. Each runs in its own runtime, and all five can run at the same time; set "
        "the switches in the next cell.\n\n"
        "1. **Part A (L4).** (a) The open decision models on `d3_goemotions`, then on "
        "`d2_banking77` (`laya-en` is smoke-tested on `d3_goemotions` only: its English head "
        "refused every 150-option question and may refuse the 77 Banking77 intents, which then "
        "leaves its `d3_goemotions` answers intact). (b) The four untuned Qwen3.5 backbones, "
        "key scoring, on the same two conditions. (c) The Qwen3-14B comparator "
        "`comparator-open` on the same two conditions. (d) The two 9B description-scoring "
        "backbones on the six conditions of the third revision. (e) Optional: a Jev latency "
        "sample from the cloud, if the Colab secret `TYPESAFE_API_KEY` exists.\n"
        "2. **Part B (L4).** DeBERTa-v3-large fine-tuned per task: "
        "`baseline-deberta-large-clinc`, `-goemo`, `-banking`, `-d3` and `-d1`.\n"
        "3. **Part C1 (A100 80GB).** Gemma-4-31B-it as a verbalized-JSON and an "
        "option-key-likelihood comparator on every condition Qwen3.6-27B covers.\n"
        "4. **Part C2 (A100 80GB).** Mistral-Small-24B-Instruct-2501 in the same two modes on "
        "the same conditions.\n"
        "5. **Part C3 (A100 80GB).** Qwen3.6-27B with thinking on (`comparator-open2-think`), "
        "then the Qwen3.6-27B pair on `d3_goemotions`, `d2_banking77` and the stress "
        "conditions.\n\n"
        "All parts write to the same Drive folder. The last cell of whichever runtime finishes "
        "last lists and archives every part's files found there.\n\n"
        "Before Run all, upload `revision4_upload.zip` to `My Drive/Jev/paper4/colab/`. The "
        "notebook unpacks it and checks every file against its SHA-256. Answers are written to "
        "`My Drive/Jev/paper4/colab/answers_revision4/` (the trained baselines write each "
        "condition at once), so a disconnect loses little: run all again and finished requests "
        "are skipped. A failing condition or model never stops the others. The last cell lists "
        "every planned file and writes `answers_revision4.zip` next to the folder for hand-back."))

    cells.append(code(
        "import subprocess as _sp, sys as _sys\n"
        "_sp.run([_sys.executable, '-m', 'pip', 'install', '-q', 'uv'], check=False)\n"
        "from google.colab import drive\n"
        "drive.mount('/content/drive')\n\n"
        "import os, json, time, datetime\n\n"
        "# ---- switches: one part per runtime (A and B on L4 runtimes, C1, C2 and C3 on A100 80GB)\n"
        "RUN_PART_A = True\n"
        "RUN_PART_B = False\n"
        "RUN_PART_C1 = False          # Gemma-4-31B-it pair\n"
        "RUN_PART_C2 = False          # Mistral-Small-24B pair\n"
        "RUN_PART_C3 = False          # Qwen3.6-27B thinking, then the Qwen3.6-27B pair\n"
        "# part A\n"
        "RUN_DECISION_MODELS = True   # (a) seven open decision models\n"
        "RUN_BACKBONE_KEY = True      # (b) the four Qwen3.5 backbones, key scoring\n"
        "RUN_COMPARATOR_OPEN = True   # (c) comparator-open (Qwen3-14B-AWQ)\n"
        "RUN_BACKBONE_DESC = True     # (d) the two 9B description-scoring backbones\n"
        "RUN_JEV_LATENCY = True       # (e) 40 Jev requests; skipped without the TYPESAFE_API_KEY secret\n"
        "# part B\n"
        f"B05_GROUPS = {B5.GROUPS!r}   # run order\n"
        "# part C3\n"
        "RUN_THINK = True\n"
        "RUN_QWEN36 = True\n"
        "QWEN36_SMOKE = False         # the Qwen3.6 pair ran twice before with this env and pins\n"
        "FREE_DISK_AFTER_DONE = True  # remove a comparator's downloaded weights once both its tags are done\n"
        "HF_TOKEN_FROM_SECRETS = False  # True reads HF_TOKEN from the Colab secrets (faster downloads)\n"
        "# compute units per hour, as Colab shows them in the Resources panel (assumptions until checked)\n"
        "UNITS_PER_HOUR = {'L4': 4.8, 'A100': 11.8}\n\n"
        f"LOCAL_ROOT = {NB_ROOT!r}\n"
        "SHARED_LOCAL = f'{LOCAL_ROOT}/shared'\n"
        "SRC_DIR = f'{SHARED_LOCAL}/src'\n"
        "INPUTS_DIR = f'{SHARED_LOCAL}/colab/inputs'\n"
        "B05_DATA_DIR = f'{SHARED_LOCAL}/data/b05'\n"
        "os.environ['HF_HOME'] = '/content/hf'\n"
        "os.environ['USE_TF'] = '0'\n"
        "if HF_TOKEN_FROM_SECRETS:\n"
        "    from google.colab import userdata\n"
        "    os.environ['HF_TOKEN'] = userdata.get('HF_TOKEN')\n\n"
        "DRIVE_ROOT = '/content/drive/MyDrive/Jev/paper4/colab'\n"
        "UPLOAD_ZIP = f'{DRIVE_ROOT}/revision4_upload.zip'\n"
        "ANSWERS_DIR = f'{DRIVE_ROOT}/answers_revision4'\n"
        "os.makedirs(ANSWERS_DIR, exist_ok=True)\n"
        "# one run log per combination of parts, so two runtimes never write the same file;\n"
        "# the status cell merges them into run_log_revision4.json\n"
        "RUN_PART_C = RUN_PART_C1 or RUN_PART_C2 or RUN_PART_C3\n"
        "# (part C3 split over two runtimes: C3think and C3qwen)\n"
        "_c3 = 'C3' + ('' if RUN_THINK == RUN_QWEN36 else ('think' if RUN_THINK else 'qwen'))\n"
        "LABEL = '_'.join(p for p, on in (('A', RUN_PART_A), ('B', RUN_PART_B), ('C1', RUN_PART_C1),\n"
        "                                 ('C2', RUN_PART_C2), (_c3, RUN_PART_C3)) if on)\n"
        "RUN_LOG_PATH = f'{ANSWERS_DIR}/run_log_revision4_part{LABEL or \"none\"}.json'\n"
        "run_log = json.load(open(RUN_LOG_PATH)) if os.path.exists(RUN_LOG_PATH) else {}\n"
        "run_log.setdefault('runtimes', []).append({'start': datetime.datetime.utcnow().isoformat() + 'Z',\n"
        "                                           'parts': LABEL, 'b05_groups': B05_GROUPS,\n"
        "                                           'think': RUN_THINK, 'qwen36': RUN_QWEN36})\n"
        "run_log['units_per_hour_assumed'] = UNITS_PER_HOUR\n"
        "print('answers on Drive:', ANSWERS_DIR, '| parts:', LABEL or 'none (status only)')"))

    cells.append(code(
        "import subprocess, shutil\n"
        "gpu_info = subprocess.run(['nvidia-smi', '--query-gpu=name,driver_version,memory.total',\n"
        "                           '--format=csv,noheader'], capture_output=True, text=True).stdout.strip()\n"
        "run_log['runtimes'][-1]['gpu'] = gpu_info\n"
        "PART_C_GPU_OK = 'A100' in gpu_info or 'H100' in gpu_info\n"
        "print(gpu_info)\n"
        "print(f\"free disk under /content: {shutil.disk_usage('/content').free / 1e9:.0f} GB\")\n"
        "if RUN_PART_C and not PART_C_GPU_OK:\n"
        "    print('WARNING: parts C1, C2 and C3 need an A100 (80 GB planned); their cells will skip on this GPU.')\n"
        "elif RUN_PART_C and int(''.join(ch for ch in gpu_info.split(',')[-1] if ch.isdigit()) or 0) < 70000:\n"
        "    print('note: parts C1, C2 and C3 were planned for an 80 GB A100; on 40 GB less memory is left for the '\n"
        "          'prompt cache and the likelihood runs take longer.')\n"
        "if (RUN_PART_A or RUN_PART_B) and 'L4' not in gpu_info:\n"
        "    print('note: parts A and B were planned for an L4; latencies will not match the earlier runs.')"))

    cells.append(md("## Unpack the upload and verify every file"))
    cells.append(code(
        "import hashlib, zipfile\n\n"
        f"EXPECTED = {json.dumps(expected, indent=1, sort_keys=True)}\n"
        f"SRC_SHA256 = {json.dumps(src_sha, indent=1, sort_keys=True)}\n"
        f"B05_DATA_SHA256 = {json.dumps(data_sha, indent=1, sort_keys=True)}\n"
        f"ZIP_SHA256 = {zip_sha!r}\n\n"
        "def _sha256(path):\n"
        "    h = hashlib.sha256()\n"
        "    with open(path, 'rb') as fh:\n"
        "        for chunk in iter(lambda: fh.read(1 << 20), b''):\n"
        "            h.update(chunk)\n"
        "    return h.hexdigest()\n\n"
        "if not os.path.exists(UPLOAD_ZIP):\n"
        "    raise SystemExit(f'{UPLOAD_ZIP} not found: upload revision4_upload.zip to that Drive folder first.')\n"
        "got = _sha256(UPLOAD_ZIP)\n"
        "if got != ZIP_SHA256:\n"
        "    print(f'note: the zip differs from the one this notebook was built with ({got}); '\n"
        "          'the per-file check below decides')\n"
        "shutil.rmtree(LOCAL_ROOT, ignore_errors=True)\n"
        "with zipfile.ZipFile(UPLOAD_ZIP) as z:\n"
        "    z.extractall(LOCAL_ROOT)\n"
        "bad = []\n"
        "for cond, meta in EXPECTED.items():\n"
        "    p = f'{INPUTS_DIR}/' + meta['file']\n"
        "    if not os.path.exists(p) or _sha256(p) != meta['sha256']:\n"
        "        bad.append(cond)\n"
        "for f, h in SRC_SHA256.items():\n"
        "    if _sha256(f'{SRC_DIR}/{f}') != h:\n"
        "        bad.append(f)\n"
        "for f, h in B05_DATA_SHA256.items():\n"
        "    if _sha256(f'{B05_DATA_DIR}/{f}') != h:\n"
        "        bad.append(f)\n"
        "if bad:\n"
        "    raise SystemExit(f'these files do not match the build: {bad} -- stopping.')\n"
        "print(f'{len(EXPECTED)} input files, {len(SRC_SHA256)} source files and '\n"
        "      f'{len(B05_DATA_SHA256)} training data files verified.')"))

    cells.append(md(
        "## Revisions, plan and helpers\n\nEvery checkpoint is pinned through `P4_REVISIONS`, "
        "which `adapters.py` reads: the decision models and Qwen3-14B-AWQ to the commits of "
        "their original answers, the backbones and Qwen3.6-27B to the commits of the second "
        "revision run, Gemma-4-31B-it to `842da379`, Mistral-Small-24B-Instruct-2501 to "
        f"`{MISTRAL_REV[:10]}`. `b05_strong_classifiers.py` pins DeBERTa-v3-large to "
        f"`{B5.MODEL_REV[:8]}` itself."))
    cells.append(code(
        f"REVISIONS = {json.dumps(REVISIONS, indent=1, sort_keys=True)}\n"
        f"TAG_REPO = {json.dumps(TAG_REPO, indent=1)}\n"
        + HELPERS +
        "\nprint(json.dumps(REVISIONS, indent=1))"))

    cells.append(md(
        "## Part A (a): open decision models on d3_goemotions and d2_banking77\n\nEach cell "
        "builds (or reuses) its uv env, smoke-tests 3 requests of each condition (`laya-en`: of "
        "`d3_goemotions` only; any error line stops that model), prints a time estimate, then "
        "runs each condition and retries it "
        "once if it is incomplete. Output is streamed and appended to "
        "`answers_revision4/<tag>/run_log_<tag>.txt`. Look for `DONE_revision4` or "
        "`ERROR_revision4.txt` in each model folder."))
    for tag, env, pkgs, opt in PLAN:
        src = (DECISION_RUNNER.replace("__TAG__", repr(tag)).replace("__ENV__", repr(env))
               .replace("__INSTALL__", repr(R1.install_script(env, pkgs, opt)))
               .replace("__CONDS__", repr(DECISION_CONDS[tag]))
               .replace("__SMOKE__", repr(DECISION_SMOKE[tag])))
        cells.append(md(f"### {tag}"))
        cells.append(code(src))

    install = R2.install_script("backbone", R2.BACKBONE_PKGS, R2.BACKBONE_OPT)
    cells.append(md(
        "## Part A (b): the untuned backbones, key scoring, on d3_goemotions and d2_banking77\n\n"
        "The four `backbone-qwen35-*` tags of the second revision (`BackboneOptScoreBackend`), "
        "in its `backbone` env with its pins. Each cell smoke-tests 2 requests of each "
        "condition with the cached-versus-full-sequence self-check on (the key-scoring check "
        "passed on `d2_k150` for all four in the second revision), then runs both conditions in "
        "one process. Switch `RUN_BACKBONE_KEY`."))
    for tag in KEY_TAGS:
        cells.append(md(f"### {tag}\n\n{TAG_REPO[tag]}."))
        cells.append(code(
            BACKBONE_RUNNER.replace("__TAG__", repr(tag))
            .replace("__INSTALL__", repr(install))
            .replace("__CONDS__", repr(KEY_CONDS))
            .replace("__CHECK_SMOKE__", repr(KEY_CONDS))
            .replace("__PLAIN_SMOKE__", repr([]))
            .replace("__EXTRA__", repr({"PYTORCH_CUDA_ALLOC_CONF": "expandable_segments:True"}))
            .replace("__SWITCH_TEXT__", "RUN_PART_A and RUN_BACKBONE_KEY")
            .replace("__SWITCH__", "RUN_PART_A and RUN_BACKBONE_KEY")))

    cells.append(md(
        "## Part A (c): comparator-open on d3_goemotions and d2_banking77\n\nQwen3-14B-AWQ "
        "through vLLM 0.30.0 with the settings of its earlier runs (greedy, thinking off, "
        "verbalized JSON). No batch-1 latency sample: `adapters.py` registers no batch-1 tag "
        "for this model. Switch `RUN_COMPARATOR_OPEN`."))
    cells.append(code(
        VLLM_RUNNER.replace("__CELL__", repr("comparator-open"))
        .replace("__INSTALL__", repr(VLLM_INSTALL))
        .replace("__PLAN__", repr([("comparator-open", COMP_OPEN_CONDS)]))
        .replace("__SMOKE_N__", "3").replace("__SMOKE__", repr(COMP_OPEN_CONDS))
        .replace("__MAX_ERR__", "0.0").replace("__RETRY_ERRORS__", "True")
        .replace("__REPO__", repr(TAG_REPO["comparator-open"]))
        .replace("__A100__", "False").replace("__FREE__", "False")
        .replace("__SWITCH_TEXT__", "RUN_PART_A and RUN_COMPARATOR_OPEN")
        .replace("__SWITCH__", "RUN_PART_A and RUN_COMPARATOR_OPEN")
        .replace("__DO_SMOKE__", "True")))
    cells.append(md(
        "### comparator-open-b1: batch-1 latency\n\n"
        f"The first {B1_LIMIT} requests of `{B1_COND}`, one request at a time, in the same "
        "`vllm_env` env, as the second revision did for Qwen3.6-27B. Optional in the status: a "
        "failure never blocks `ALL_DONE_revision4`."))
    cells.append(code(b1_cell("comparator-open-b1", OPEN_B1, TAG_REPO["comparator-open"],
                              False, ["comparator-open"], "RUN_PART_A and RUN_COMPARATOR_OPEN")))

    cells.append(md(
        "## Part A (d): 9B backbones scored on option descriptions\n\n"
        "`P4_DESC_ROWS=4` rows per scoring pass. In the third revision both smoke tests ran out "
        "of memory in the self-check on `d2_k150`: the check recomputes each description with a "
        "full-sequence pass and a float64 log-softmax over every prompt position (2.4 GiB for a "
        "1300-token prompt), which does not fit next to 9B weights on an L4. The self-check "
        "therefore runs on `d1_neutral` and `d3_emotion`, where it passed before, and `d2_k150` "
        "and `d3_conv_go_awry` (prompts up to 8,000 tokens) get a 2-request smoke test with the "
        "check off, on the cached path the full run uses. "
        "Then all six conditions run in one process; a condition left incomplete is retried on "
        "its own. Switch `RUN_BACKBONE_DESC`."))
    notes = {"backbone-desc-qwen35-9b-base": "Qwen/Qwen3.5-9B-Base, the base of kev-9b.",
             "backbone-desc-qwen35-9b": "Qwen/Qwen3.5-9B (post-trained), the base of nimble-9b."}
    for tag in DESC_TAGS:
        cells.append(md(f"### {tag}\n\n{notes[tag]}"))
        cells.append(code(
            BACKBONE_RUNNER.replace("__TAG__", repr(tag))
            .replace("__INSTALL__", repr(install))
            .replace("__CONDS__", repr(DESC_CONDS))
            .replace("__CHECK_SMOKE__", repr(DESC_CHECK_SMOKE))
            .replace("__PLAIN_SMOKE__", repr(DESC_PLAIN_SMOKE))
            .replace("__EXTRA__", repr({"P4_DESC_ROWS": "4",
                                        "PYTORCH_CUDA_ALLOC_CONF": "expandable_segments:True"}))
            .replace("__SWITCH_TEXT__", "RUN_PART_A and RUN_BACKBONE_DESC")
            .replace("__SWITCH__", "RUN_PART_A and RUN_BACKBONE_DESC")))

    cells.append(md(
        "## Part A (e): optional Jev latency from the cloud\n\n"
        f"`harness.py --model jev --cond {JEV_COND} --rep {JEV_REP} --limit {JEV_LIMIT}` "
        "through `typesafe-sdk` 0.7.1, the SDK version of the local runs, with the model pinned to "
        "`jev-1.13.0`. Reps 1 to 5 exist locally, so this is rep 6. The API key is read from the "
        "Colab secret `TYPESAFE_API_KEY` and handed to the harness process through its "
        "environment only; it is never printed or written to a file. Without the secret the "
        "cell says so and skips. Switch `RUN_JEV_LATENCY`."))
    cells.append(code(
        JEV_RUNNER.replace("__TAG__", repr(JEV_TAG))
        .replace("__INSTALL__", repr(R2.install_script("jev", JEV_PKGS, index="")))
        .replace("__COND__", repr(JEV_COND)).replace("__REP__", repr(JEV_REP))
        .replace("__LIMIT__", repr(JEV_LIMIT))))

    cells.append(md(
        "## Part B: DeBERTa-v3-large fine-tuned per task\n\n"
        "Builds the `b05` env, runs `b05_strong_classifiers.py --smoke` with the real pinned "
        "checkpoint on a few rows of every task (one epoch, bf16, the 512-token micro-batches of "
        "the D3 tasks) and checks the smoke answers (line count, record fields, revision). Then "
        "one process per group in the order of `B05_GROUPS`, each retried once if a condition "
        "is incomplete. The smoke run prints the training throughput and an estimate per task. "
        "Each condition's answers are written at once, with `<cond>__fit.json` next to them. "
        "The `d1` group trains one cross-encoder on the typed-decisions training states against "
        "the teacher's soft labels and answers `d1_neutral` and `d1_calib`."))
    cells.append(code(
        B05_RUNNER.replace("__INSTALL__", repr(R2.install_script("b05", B5_PKGS)))
        .replace("__GROUP_TAG__", repr(B5_GROUP_TAG))
        .replace("__TAG_CONDS__", repr(B5_TAG_CONDS))
        .replace("__MODEL__", repr(B5.MODEL_ID)).replace("__REV__", repr(B5.MODEL_REV))
        .replace("__SMOKE_N__", repr(B5.SMOKE_TEST))
        .replace("__FIELDS__", repr(B5_FIELDS))))

    cells.append(md(
        "## Parts C1, C2 and C3: comparators from three model families (A100 80GB)\n\n"
        "Part C1 is the Gemma cell (switch `RUN_PART_C1`), Part C2 the Mistral cell "
        "(`RUN_PART_C2`), Part C3 the Qwen3.6-27B thinking cell and then the Qwen3.6-27B pair "
        "(`RUN_PART_C3`, with `RUN_THINK` and `RUN_QWEN36`). The three can run at the same time "
        "on three A100 runtimes. Each cell builds (or reuses) the `vllm_env` env (vLLM 0.30.0). "
        "Gemma and Mistral are quantized to FP8 weights on load, as `adapters.py` sets in their "
        "profiles, and run every condition Qwen3.6-27B covers. For each of them both modes are "
        "smoke-tested first (3 requests each of `d1_neutral`, `d2_k150` and "
        "`d3_conv_go_awry`); a mode whose smoke test fails is skipped and the other still runs. "
        "Each mode then runs all its conditions in one process, and a condition left incomplete "
        "is retried on its own. There are no batch-1 latency samples for Gemma or Mistral: "
        "`adapters.py` registers no batch-1 tag for them. With `FREE_DISK_AFTER_DONE`, a model's "
        "downloaded weights are removed from the runtime disk once all its tags on that part "
        "are done."))
    for cell, part, plan, sw, smoke, smoke_conds, smoke_n, max_err, retry, free in (
            # the batch-1 cell after these two frees the disk, so these keep the weights
            ("Gemma-4-31B-it", "C1", [(t, FAMILY_CONDS) for t in GEMMA], "RUN_PART_C1", "True",
             C_SMOKE, 3, 0.0, True, False),
            ("Mistral-Small-24B-Instruct-2501", "C2", [(t, FAMILY_CONDS) for t in MISTRAL],
             "RUN_PART_C2", "True", C_SMOKE, 3, 0.0, True, False),
            ("Qwen3.6-27B-FP8, thinking on", "C3", [(THINK, THINK_CONDS)],
             "RUN_PART_C3 and RUN_THINK", "True", THINK_SMOKE, THINK_SMOKE_N, THINK_MAX_ERR,
             False, False),
            ("Qwen3.6-27B-FP8", "C3", [(t, QWEN36_CONDS) for t in QWEN36],
             "RUN_PART_C3 and RUN_QWEN36", "QWEN36_SMOKE", C_SMOKE, 3, 0.0, True, True)):
        tags = [t for t, _c in plan]
        conds = plan[0][1]
        extra = ""
        if tags == [THINK]:
            extra = (
                "\n\nThinking on, verbal readout only (`Comparator2ThinkBackend`: up to "
                f"{AD.THINK_MAX_TOKENS} output tokens, a {AD.THINK_MAX_MODEL_LEN}-token context, "
                "the sampling of `THINK_SAMPLING` with a fixed seed, JSON parsed after the closing "
                f"think tag). Smoke test: {THINK_SMOKE_N} requests each of "
                + ", ".join(f"`{c}`" for c in THINK_SMOKE) + "; the tag stops if more than half "
                "the smoke replies are error lines, and the cell prints the mean output tokens "
                "per question and a time estimate. A reply that fails to parse is an error line; "
                "under the fixed seed it fails again, so only requests without any line are "
                "retried, and such a condition stays INCOMPLETE in the status with its count.")
        cells.append(md(f"### Part {part}: {cell}\n\nTags " + ", ".join(f"`{t}`" for t in tags)
                        + " on " + ", ".join(f"`{c}`" for c in conds) + "." + extra))
        cells.append(code(
            VLLM_RUNNER.replace("__CELL__", repr(cell))
            .replace("__INSTALL__", repr(VLLM_INSTALL))
            .replace("__PLAN__", repr(plan))
            .replace("__SMOKE_N__", repr(smoke_n)).replace("__SMOKE__", repr(smoke_conds))
            .replace("__MAX_ERR__", repr(max_err)).replace("__RETRY_ERRORS__", repr(retry))
            .replace("__REPO__", repr(TAG_REPO[tags[0]]))
            .replace("__A100__", "True").replace("__FREE__", repr(free))
            .replace("__SWITCH_TEXT__", sw)
            .replace("__SWITCH__", sw)
            .replace("__DO_SMOKE__", smoke)))
        b1 = {GEMMA[0]: GEMMA_B1, MISTRAL[0]: MISTRAL_B1}.get(tags[0])
        if b1:
            cells.append(md(
                f"### Part {part}: {cell}, batch-1 latency\n\nTags `{b1[0]}` and `{b1[1]}`: the "
                f"first {B1_LIMIT} requests of `{B1_COND}`, one request at a time, as the second "
                "revision did for Qwen3.6-27B. Optional in the status: a failure never blocks "
                "`ALL_DONE_revision4`. This cell removes the model's weights afterwards when "
                "`FREE_DISK_AFTER_DONE` is on and every tag of the model is done."))
            cells.append(code(b1_cell(f"{cell}, batch 1", b1, TAG_REPO[tags[0]], True, tags, sw)))

    cells.append(md(
        "## Status and hand-back\n\nReads the Drive folder, so it covers every part whichever "
        "runtime wrote it. Lists every planned answer file of all four parts with its count of "
        "answered requests, error lines, the longest prompt in tokens (backbones) and the "
        "recorded revision against the pin, then a summary per part. A part not run yet shows "
        "as MISSING. Then merges the run logs of all runtimes into `run_log_revision4.json` and "
        "writes `answers_revision4.zip` into `My Drive/Jev/paper4/colab/`. Run this cell last on "
        "the runtime that finishes last; files another runtime wrote in the last few minutes "
        "may take a moment to appear, so rerun it if a finished part shows as MISSING."))
    cells.append(code(STATUS.replace("__PLANNED__", repr([list(x) for x in PLANNED]))))

    nb = nbf.v4.new_notebook()
    nb["cells"] = cells
    nb["metadata"] = {"kernelspec": {"display_name": "Python 3", "language": "python",
                                     "name": "python3"},
                      "language_info": {"name": "python", "pygments_lexer": "ipython3"},
                      "accelerator": "GPU", "colab": {"provenance": [], "gpuType": "L4"}}
    nbf.validate(nb)
    with open(OUT_NB, "w", encoding="utf-8") as fh:
        nbf.write(nb, fh)

    print(f"wrote {OUT_NB} ({len(cells)} cells)")
    print(f"wrote {OUT_ZIP} ({os.path.getsize(OUT_ZIP) / 1e6:.1f} MB, sha256 {zip_sha})")
    print(f"dropped from the Qwen3.6 stress list (answered in the second revision): {QWEN36_DROPPED}")
    for part in ("A", "B", "C1", "C2", "C3"):
        rows = [x for x in PLANNED if x[0] == part]
        print(f"part {part}: {len(rows)} files, {sum(x[4] for x in rows)} requests, "
              f"{sum(man[x[2]]['decisions'] if x[4] == man[x[2]]['requests'] else x[4] for x in rows)}"
              f" decisions")
        by_tag = {}
        for x in rows:
            by_tag.setdefault(x[1], []).append(x)
        for t, xs in by_tag.items():
            print(f"   {t:34s} {sum(x[4] for x in xs):6d}  "
                  + ", ".join(x[2] + (f" rep {x[3]}" if x[3] != 1 else "")
                              + (" (optional)" if x[5] else "") for x in xs))
    if check:
        _check(nb, man, data_sha)


def _undefined_names(sources):
    """Names loaded somewhere in the notebook but never bound at module level (in cell order,
    all cells share one namespace) nor built in. py_compile does not see these."""
    src = "\n\n".join(sources)
    ast.parse(src)
    top = symtable.symtable(src, "notebook", "exec")
    bound = {s.get_name() for s in top.get_symbols()
             if s.is_assigned() or s.is_imported() or s.is_namespace()}
    known = bound | set(dir(builtins))
    missing = set()

    def walk(t):
        for s in t.get_symbols():
            if t is top:
                if s.is_referenced() and s.get_name() not in known:
                    missing.add(s.get_name())
            elif s.is_global() and s.is_referenced() and s.get_name() not in known:
                missing.add(s.get_name())
        for ch in t.get_children():
            walk(ch)
    walk(top)
    return sorted(missing)


def _check(nb, man, data_sha):
    """Compile every code cell and the shipped source files, look for names used but never
    defined, check the zip against the manifest and the build, and look for names of the
    earlier runs left in the notebook."""
    sources = []
    for cell in nb["cells"]:
        if cell["cell_type"] != "code":
            continue
        src = "\n".join(l for l in cell["source"].splitlines() if not l.startswith(("%", "!")))
        sources.append(src)
        with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8") as fh:
            fh.write(src)
            tmp = fh.name
        try:
            py_compile.compile(tmp, doraise=True)
        finally:
            os.unlink(tmp)
    for f in SRC_FILES + [os.path.basename(__file__)]:
        py_compile.compile(os.path.join(HERE, f), doraise=True)
    print(f"py_compile OK for {len(sources)} code cells and {len(SRC_FILES) + 1} source files")
    und = _undefined_names(sources)
    assert not und, f"names used but never defined in the notebook: {und}"
    print("every name the cells use is defined in an earlier or the same cell, or built in")

    with zipfile.ZipFile(OUT_ZIP) as z:
        names = set(z.namelist())
        want = ({f"shared/src/{f}" for f in SRC_FILES}
                | {f"shared/colab/inputs/{man[c]['file']}" for c in SHIP_INPUTS}
                | {"shared/colab/inputs/manifest.json"}
                | {f"shared/data/b05/{fn}" for fn in data_sha})
        assert names == want, sorted(names ^ want)
        for c in SHIP_INPUTS:
            got = hashlib.sha256(z.read(f"shared/colab/inputs/{man[c]['file']}")).hexdigest()
            assert got == man[c]["sha256"], c
        for f in SRC_FILES:
            got = hashlib.sha256(z.read(f"shared/src/{f}")).hexdigest()
            assert got == sha256(os.path.join(HERE, f)), f
        for fn, h in data_sha.items():
            assert hashlib.sha256(z.read(f"shared/data/b05/{fn}")).hexdigest() == h, fn
        meta = json.loads(z.read("shared/data/b05/b05_meta.json"))
        assert set(meta) == set(B5.TASKS), sorted(meta)
    print(f"zip OK: {len(SHIP_INPUTS)} inputs match the manifest SHA-256, {len(SRC_FILES)} "
          f"source files match the working copy, {len(data_sha)} training data files match the build")

    text = open(OUT_NB, encoding="utf-8").read()
    left = [s for s in STALE if s in text]
    assert not left, f"names of earlier runs left in the notebook: {left}"
    print("no names of the earlier runs left in the notebook")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    build(check=ap.parse_args().check)


if __name__ == "__main__":
    main()
