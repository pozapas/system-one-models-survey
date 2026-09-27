"""Build colab/run_revision3.ipynb and colab/revision3_upload.zip for the third revision runs.

Two parts, each runnable on its own runtime (switches RUN_PART1 and RUN_PART2 in the first
code cell). Every job is rep 1.

  Part 1, Colab L4, cheapest and most important jobs first:
    a. the open decision models laya-ml, kev-0.8b, decider-2b, this-that-1.0, kev-9b and
       nimble-9b on d2_k150_oos (d2_k150 with option o151 "out of scope" appended; frozen by
       s00d_freeze_oos_option.py), with revision 1's per-family envs, pins and runner
       conventions and a 5-request smoke test per model. laya-en is left out: its English head
       refuses every 150-option question, as it did in the first run.
    b. the Qwen3-14B-AWQ generative comparator, tag comparator-open, on d2_k150_oos with
       revision 1's comparator settings (switch RUN_COMPARATOR, default True).
    c. the four description-scoring backbones backbone-desc-qwen35-{0.8b-base,2b-base,9b-base,9b}
       (adapters.BackboneDescScoreBackend) on adapters.BACKBONE_DESC_CONDITIONS, with revision
       2's backbone env, pins and runner, and a smoke test with the cached-versus-full-sequence
       self-check on over 2 requests each of d2_k150, d1_neutral and d3_emotion (switch
       RUN_BACKBONE_DESC, default True).
  Part 2, Colab A100: Qwen3.6-27B-FP8 through vLLM, tags comparator-open2 (verbalized JSON) and
  comparator-open2-ll (option-key likelihood), on d2_k150_oos only, with revision 2's env,
  pins and engine profile, and a 5-request smoke test of each mode. No batch-1 sample.
  COMPARATOR2_VARIANT = 'awq' switches to the L4 fallback as in revision 2.

The pins, package lists and install scripts are imported from build_revision_notebook.py and
build_revision2_notebook.py, so they are the same objects the earlier notebooks were built
from. Two decisions differ from a literal copy. First, comparator-open installs vLLM 0.30.0,
the version its first run logged, instead of revision 1's unpinned vllm; the Part 2 env pins
the same version and both use /content/envs/vllm_env, so the two cannot disagree. Second,
harness.py records a failing request (including a failed self-check) as an error line and
still exits 0, so every smoke test here also reads its own answer files and stops the model
on any error line; a condition counts as done only when every request is answered.

Answers go to My Drive/Jev/paper4/colab/answers_revision3/<tag>/<cond>__rep1.jsonl, the same
layout as shared/answers, so answers_revision3.zip unpacks straight into shared/answers.

Usage: python build_revision3_notebook.py [--check]
"""
import argparse
import hashlib
import json
import os
import py_compile
import shlex
import tempfile
import zipfile

import nbformat as nbf

import adapters as AD
import build_revision_notebook as R1
import build_revision2_notebook as R2

HERE = os.path.dirname(os.path.abspath(__file__))
SHARED = os.path.dirname(HERE)
COLAB = os.path.join(SHARED, "colab")
INPUTS = os.path.join(COLAB, "inputs")
OUT_NB = os.path.join(COLAB, "run_revision3.ipynb")
OUT_ZIP = os.path.join(COLAB, "revision3_upload.zip")

SRC_FILES = ["common.py", "harness.py", "adapters.py"]
OOS = "d2_k150_oos"
DECISION_TAGS = ["laya-ml", "kev-0.8b", "decider-2b", "this-that-1.0", "kev-9b", "nimble-9b"]
DESC_TAGS = ["backbone-desc-qwen35-0.8b-base", "backbone-desc-qwen35-2b-base",
             "backbone-desc-qwen35-9b-base", "backbone-desc-qwen35-9b"]
DESC_CONDS = list(AD.BACKBONE_DESC_CONDITIONS)
DESC_SMOKE = ["d2_k150", "d1_neutral", "d3_emotion"]
PART2_CONDS = [OOS]
SHIP_INPUTS = sorted(set([OOS] + DESC_CONDS + DESC_SMOKE))
COMP_TAGS = {v: {"verbal": t["verbal"], "ll": t["ll"]} for v, t in R2.COMP_TAGS.items()}

# revision 1 plan without laya-en, in revision 1's order (already cheapest first)
PLAN = [p for p in R1.PLAN if p[0] in DECISION_TAGS]

REVISIONS = dict(R1.REVISIONS)
for _repo, _sha in R2.REVISIONS.items():
    assert REVISIONS.get(_repo, _sha) == _sha, _repo
    REVISIONS[_repo] = _sha
TAG_REPO = {t: R1.TAG_REPO[t] for t in DECISION_TAGS + ["comparator-open"]}
TAG_REPO.update({t: AD.BACKBONE_REPOS[AD.BACKBONE_DESC_OF[t]] for t in DESC_TAGS})
TAG_REPO.update({t: r for v in COMP_TAGS.values() for t in v.values()
                 for r in [AD.COMPARATOR2_TAGS[t][1]]})

# vLLM 0.30.0 for both comparators (see the module docstring), install form of revision 2
VLLM_INSTALL = ("set -e\nexport UV_CACHE_DIR=/content/uv-cache\n"
                "uv venv /content/envs/vllm_env --python 3.12 -q --allow-existing\n"
                "uv pip install --python /content/envs/vllm_env/bin/python -q "
                + " ".join(shlex.quote(p) for p in R2.VLLM_PKGS) + "\n")
NB_ROOT = "/content/p4"

# names of the earlier runs that must not survive in the generated notebook
STALE = ["revision2", "revision_upload", "answers_revision/", "answers_revision.zip",
         "DONE_revision'", "DONE_revision\"", "ERROR_revision.txt", "run_log_revision.json",
         "ALL_DONE_revision'", "ALL_DONE_revision\""]

sha256 = R1.sha256
md = R1.md
code = R1.code


HELPERS = r'''
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
'''


DECISION_RUNNER = r'''import subprocess, time, json, os, traceback, shutil

TAG = __TAG__
ENV_NAME = __ENV__
PYBIN = f'/content/envs/{ENV_NAME}/bin/python'
INSTALL = __INSTALL__
JOBS = __JOBS__   # [(run tag, condition, rep), ...]

def harness_env(answers_dir):
    env = dict(os.environ)
    env['HF_HOME'] = '/content/hf'
    env['P4_INPUTS'] = INPUTS_DIR
    env['P4_ANSWERS'] = answers_dir
    env['P4_REVISIONS'] = json.dumps(REVISIONS)
    # ninja and any other console script of the env must be on PATH (FlashInfer JIT, Triton)
    env['PATH'] = f'/content/envs/{ENV_NAME}/bin:' + env.get('PATH', '')
    return env

def run_harness(run_tag, cond, rep, log_path, limit=None, answers_dir=None):
    """One condition in its own process; every output line goes to the cell and the Drive log."""
    cmd = [PYBIN, f'{SRC_DIR}/harness.py', '--model', run_tag, '--cond', cond, '--rep', str(rep)]
    if limit: cmd += ['--limit', str(limit)]
    t0 = time.time()
    with open(log_path, 'a', encoding='utf-8') as log:
        log.write(f'\n$ {" ".join(cmd)}\n'); log.flush()
        p = subprocess.Popen(cmd, cwd=SRC_DIR, env=harness_env(answers_dir or ANSWERS_DIR),
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
        for line in p.stdout:
            log.write(line); log.flush()
            print(line, end='', flush=True)
        rc = p.wait()
    return rc, time.time() - t0

if not (RUN_PART1 and globals().get('RUN_DECISION_MODELS', True)):
    print(f'{TAG}: skipped (RUN_PART1 = {RUN_PART1}, RUN_DECISION_MODELS = '
          f'{globals().get("RUN_DECISION_MODELS", True)})')
else:
    TAG_DIR = f'{ANSWERS_DIR}/{TAG}'
    os.makedirs(TAG_DIR, exist_ok=True)
    LOG = f'{TAG_DIR}/run_log_{TAG}.txt'
    SMOKE_DIR = f'/content/smoke/{TAG}'
    # a fresh smoke folder on every run of the cell, so the smoke test and its timing are real
    shutil.rmtree(SMOKE_DIR, ignore_errors=True)
    os.makedirs(SMOKE_DIR, exist_ok=True)
    try:
        print(f'=== {TAG}: building env {ENV_NAME} ===', flush=True)
        subprocess.run(['bash', '-c', INSTALL], check=True)

        print(f'=== {TAG}: smoke test (5 requests of {JOBS[0][1]}) ===', flush=True)
        rc, dt = run_harness(JOBS[0][0], JOBS[0][1], 1, LOG, limit=5, answers_dir=SMOKE_DIR)
        if rc:
            raise RuntimeError(f'{TAG}: smoke test failed (exit {rc}); see {LOG}')
        errs, _ = smoke_report(SMOKE_DIR)
        if errs:
            raise RuntimeError(f'{TAG}: {len(errs)} smoke request(s) returned an error line, '
                               f'first: {errs[0]}')
        n_req = sum(EXPECTED[c]['requests'] for _t, c, _r in JOBS)
        rate = UNITS_PER_HOUR['L4']
        print(f'{TAG}: {dt / 5:.2f} s per request including the model load -> at most '
              f'{dt / 5 * n_req / 60:.0f} min for {n_req} requests, '
              f'~{dt / 5 * n_req / 3600 * rate:.1f} compute units at {rate}/h on an L4', flush=True)
        run_log.setdefault('models', {})[TAG] = {'smoke_s_per_request_incl_load': dt / 5,
                                                 'requests': n_req}

        failed = []
        for run_tag, cond, rep in JOBS:
            rc, dt = run_harness(run_tag, cond, rep, LOG)
            ok, err = answer_counts(f'{ANSWERS_DIR}/{run_tag}/{cond}__rep{rep}.jsonl')
            want = EXPECTED[cond]['requests']
            print(f'[{run_tag}] {cond} rep{rep}: exit {rc}, {dt / 60:.1f} min, {ok}/{want} '
                  f'answered, {err} error lines', flush=True)
            run_log['models'][TAG][f'{run_tag}/{cond}_min'] = dt / 60
            if rc or ok < want:
                failed.append(f'{run_tag}/{cond}__rep{rep}')
        if failed:
            raise RuntimeError(f'{TAG}: conditions incomplete: {failed}')
        with open(f'{TAG_DIR}/DONE_revision3', 'w') as fh:
            fh.write(time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()) + '\n')
        print(f'=== {TAG}: DONE ===')
    except Exception:
        tb = traceback.format_exc()
        with open(f'{TAG_DIR}/ERROR_revision3.txt', 'w') as fh:
            fh.write(tb)
        print(f'=== {TAG}: ERROR, continuing with the next model (see {TAG_DIR}/ERROR_revision3.txt) ===')
        print(tb)
    finally:
        import gc
        gc.collect()
        subprocess.run(['nvidia-smi', '--query-gpu=memory.used', '--format=csv,noheader'])
'''

COMPARATOR_RUNNER = r'''import subprocess, time, json, os, traceback, shutil

TAG = 'comparator-open'
ENV_NAME = 'vllm_env'
PYBIN = f'/content/envs/{ENV_NAME}/bin/python'
INSTALL = __INSTALL__
CONDS = __CONDS__

def stream(cmd, log_path, env=None):
    with open(log_path, 'a', encoding='utf-8') as log:
        log.write(f'\n$ {" ".join(cmd)}\n'); log.flush()
        p = subprocess.Popen(cmd, cwd=SRC_DIR, env=env, stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT, text=True, bufsize=1)
        for line in p.stdout:
            print(line, end='', flush=True)
            log.write(line); log.flush()
        return p.wait()

def harness_env(answers_dir):
    env = dict(os.environ)
    env['HF_HOME'] = '/content/hf'
    env['P4_INPUTS'] = INPUTS_DIR
    env['P4_ANSWERS'] = answers_dir
    env['P4_REVISIONS'] = json.dumps(REVISIONS)
    env['VLLM_LOGGING_LEVEL'] = 'INFO'
    # FlashInfer JIT-compiles kernels with ninja, which lives in the env's bin folder;
    # greedy decoding does not need the FlashInfer sampler, so it is switched off as well
    env['PATH'] = f'/content/envs/{ENV_NAME}/bin:' + env.get('PATH', '')
    env['VLLM_USE_FLASHINFER_SAMPLER'] = '0'
    return env

if not (RUN_PART1 and RUN_COMPARATOR):
    print(f'{TAG}: skipped (RUN_PART1 = {RUN_PART1}, RUN_COMPARATOR = {RUN_COMPARATOR})')
else:
    TAG_DIR = f'{ANSWERS_DIR}/{TAG}'
    os.makedirs(TAG_DIR, exist_ok=True)
    LOG = f'{TAG_DIR}/run_log_{TAG}.txt'
    SMOKE_DIR = f'/content/smoke/{TAG}'
    shutil.rmtree(SMOKE_DIR, ignore_errors=True)
    try:
        print(f'=== {TAG}: building env {ENV_NAME} ===', flush=True)
        rc = stream(['bash', '-c', INSTALL + f'{PYBIN} -c "import vllm, torch; print(\'vllm\', vllm.__version__, \'torch\', torch.__version__)"'], LOG)
        if rc:
            raise RuntimeError(f'env build failed (exit {rc})')
        print(f'=== {TAG}: smoke test, 5 requests of {CONDS[0]} ===', flush=True)
        t0 = time.time()
        rc = stream([PYBIN, f'{SRC_DIR}/harness.py', '--model', TAG, '--cond', CONDS[0],
                     '--rep', '1', '--limit', '5'], LOG, env=harness_env(SMOKE_DIR))
        run_log.setdefault('models', {})[TAG] = {'smoke_s_incl_load': time.time() - t0}
        if rc:
            raise RuntimeError(f'smoke test failed (exit {rc}); see {LOG}')
        errs, _ = smoke_report(SMOKE_DIR)
        if errs:
            raise RuntimeError(f'{len(errs)} smoke request(s) returned an error line, first: {errs[0]}')
        print(f'=== {TAG}: full run (one process, model loaded once) ===', flush=True)
        t0 = time.time()
        rc = stream([PYBIN, f'{SRC_DIR}/harness.py', '--model', TAG, '--cond', ','.join(CONDS),
                     '--rep', '1'], LOG, env=harness_env(ANSWERS_DIR))
        run_log['models'][TAG]['full_min'] = (time.time() - t0) / 60
        print(f'full run exit {rc}, {(time.time() - t0) / 60:.1f} min', flush=True)
        missing = [c for c in CONDS
                   if answer_counts(f'{TAG_DIR}/{c}__rep1.jsonl')[0] < EXPECTED[c]['requests']]
        if rc or missing:
            raise RuntimeError(f'full run exit {rc}, incomplete: {missing}; see {LOG}')
        with open(f'{TAG_DIR}/DONE_revision3', 'w') as fh:
            fh.write(time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()) + '\n')
        print(f'=== {TAG}: DONE ===')
    except Exception:
        tb = traceback.format_exc()
        with open(f'{TAG_DIR}/ERROR_revision3.txt', 'w') as fh:
            fh.write(tb)
        print(f'=== {TAG}: ERROR, continuing; the full log is in {LOG} ===')
        print(tb)
    finally:
        subprocess.run(['nvidia-smi', '--query-gpu=memory.used', '--format=csv,noheader'])
'''

BACKBONE_DESC_RUNNER = r'''import subprocess, time, json, os, traceback, shutil

TAG = __TAG__
ENV_NAME = 'backbone'
PYBIN = f'/content/envs/{ENV_NAME}/bin/python'
INSTALL = __INSTALL__
CONDS = __CONDS__   # rep 1 each
SMOKE_CONDS = __SMOKE__

def harness_env(answers_dir, check=0):
    env = dict(os.environ)
    env['HF_HOME'] = '/content/hf'
    env['P4_INPUTS'] = INPUTS_DIR
    env['P4_ANSWERS'] = answers_dir
    env['P4_REVISIONS'] = json.dumps(REVISIONS)
    env['P4_OPTSCORE_CHECK'] = str(check)
    # rows per scoring pass; the 9B checkpoints leave little room on an L4 (adapters retries
    # with fewer rows on out-of-memory in any case)
    env['P4_DESC_ROWS'] = '4' if '9b' in TAG else '16'
    # ninja and any other console script of the env must be on PATH (Triton, fla kernels)
    env['PATH'] = f'/content/envs/{ENV_NAME}/bin:' + env.get('PATH', '')
    return env

def run_harness(conds, log_path, limit=None, answers_dir=None, check=0):
    """Conditions in one process (the model loads once); output goes to the cell and the log."""
    cmd = [PYBIN, f'{SRC_DIR}/harness.py', '--model', TAG, '--cond', ','.join(conds), '--rep', '1']
    if limit: cmd += ['--limit', str(limit)]
    t0 = time.time()
    with open(log_path, 'a', encoding='utf-8') as log:
        log.write(f'\n$ {" ".join(cmd)}\n'); log.flush()
        p = subprocess.Popen(cmd, cwd=SRC_DIR, env=harness_env(answers_dir or ANSWERS_DIR, check),
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
        for line in p.stdout:
            log.write(line); log.flush()
            print(line, end='', flush=True)
        rc = p.wait()
    return rc, time.time() - t0

def n_ok(cond):
    return answer_counts(f'{ANSWERS_DIR}/{TAG}/{cond}__rep1.jsonl')[0]

if not (RUN_PART1 and RUN_BACKBONE_DESC
        and (globals().get('DESC_ONLY') is None or TAG in DESC_ONLY)):
    print(f'{TAG}: skipped (RUN_PART1 = {RUN_PART1}, RUN_BACKBONE_DESC = {RUN_BACKBONE_DESC}, '
          f'DESC_ONLY = {globals().get("DESC_ONLY")})')
else:
    TAG_DIR = f'{ANSWERS_DIR}/{TAG}'
    os.makedirs(TAG_DIR, exist_ok=True)
    # a rerun replaces the marker of an earlier failed attempt of this same notebook
    if os.path.exists(f'{TAG_DIR}/ERROR_revision3.txt'):
        os.rename(f'{TAG_DIR}/ERROR_revision3.txt', f'{TAG_DIR}/ERROR_revision3_earlier.txt')
    LOG = f'{TAG_DIR}/run_log_{TAG}.txt'
    SMOKE_DIR = f'/content/smoke/{TAG}'
    shutil.rmtree(SMOKE_DIR, ignore_errors=True)
    try:
        print(f'=== {TAG}: building env {ENV_NAME} ===', flush=True)
        subprocess.run(['bash', '-c', INSTALL], check=True)

        print(f'=== {TAG}: smoke test with the cached-versus-full-sequence self-check '
              f'(2 requests each of {SMOKE_CONDS}) ===', flush=True)
        rc, dt = run_harness(SMOKE_CONDS, LOG, limit=2, answers_dir=SMOKE_DIR, check=100)
        errs, dmax = smoke_report(SMOKE_DIR)
        print(f'{TAG}: smoke {dt:.0f} s for {2 * len(SMOKE_CONDS)} requests including the model '
              f'load; largest self-check difference {dmax}', flush=True)
        if rc or errs:
            raise RuntimeError(f'{TAG}: smoke test or self-check failed (exit {rc}, '
                               f'{len(errs)} error lines, first: {errs[:1]}); see {LOG}')
        if dmax is None:
            raise RuntimeError(f'{TAG}: the smoke answers carry no self-check value; see {LOG}')
        n_req = sum(EXPECTED[c]['requests'] for c in CONDS)
        run_log.setdefault('models', {})[TAG] = {'smoke_s_incl_load': dt, 'requests': n_req,
                                                 'smoke_check_max_abs_dprob': dmax}

        print(f'=== {TAG}: full run, {len(CONDS)} conditions, {n_req} requests ===', flush=True)
        rc, dt = run_harness(CONDS, LOG)
        print(f'[{TAG}] one-process run: exit {rc}, {dt / 60:.1f} min', flush=True)
        run_log['models'][TAG]['full_min'] = dt / 60
        # a condition left incomplete (a crash, a disconnect) is retried on its own, so one
        # failing condition never blocks the others; finished requests are skipped
        failed = []
        for c in CONDS:
            if n_ok(c) < EXPECTED[c]['requests']:
                rc, dt = run_harness([c], LOG)
                print(f'[{TAG}] retry {c}: exit {rc}, {dt / 60:.1f} min', flush=True)
                if n_ok(c) < EXPECTED[c]['requests']:
                    failed.append(c)
        if failed:
            raise RuntimeError(f'{TAG}: incomplete conditions: {failed}')
        with open(f'{TAG_DIR}/DONE_revision3', 'w') as fh:
            fh.write(time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()) + '\n')
        print(f'=== {TAG}: DONE ===')
    except Exception:
        tb = traceback.format_exc()
        with open(f'{TAG_DIR}/ERROR_revision3.txt', 'w') as fh:
            fh.write(tb)
        print(f'=== {TAG}: ERROR, continuing with the next model (see {TAG_DIR}/ERROR_revision3.txt) ===')
        print(tb)
    finally:
        import gc
        gc.collect()
        subprocess.run(['nvidia-smi', '--query-gpu=memory.used', '--format=csv,noheader'])
'''

PART2_RUNNER = r'''import subprocess, time, json, os, traceback, shutil

ENV_NAME = 'vllm_env'
PYBIN = f'/content/envs/{ENV_NAME}/bin/python'
INSTALL = __INSTALL__
CONDS = __CONDS__
SMOKE_COND = CONDS[0]      # both smoke tests run on the new condition, so o151 is exercised
TAGS = COMPARATOR2_TAGS[COMPARATOR2_VARIANT]

def harness_env(answers_dir):
    env = dict(os.environ)
    env['HF_HOME'] = '/content/hf'
    env['P4_INPUTS'] = INPUTS_DIR
    env['P4_ANSWERS'] = answers_dir
    env['P4_REVISIONS'] = json.dumps(REVISIONS)
    env['VLLM_LOGGING_LEVEL'] = 'INFO'
    # FlashInfer JIT-compiles kernels with ninja, which lives in the env's bin folder;
    # greedy decoding does not need the FlashInfer sampler, so it is switched off as well
    env['PATH'] = f'/content/envs/{ENV_NAME}/bin:' + env.get('PATH', '')
    env['VLLM_USE_FLASHINFER_SAMPLER'] = '0'
    return env

def stream(cmd, log_path, env=None):
    with open(log_path, 'a', encoding='utf-8') as log:
        log.write(f'\n$ {" ".join(cmd)}\n'); log.flush()
        p = subprocess.Popen(cmd, cwd=SRC_DIR, env=env, stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT, text=True, bufsize=1)
        for line in p.stdout:
            print(line, end='', flush=True)
            log.write(line); log.flush()
        return p.wait()

def harness(tag, conds, limit=None, answers_dir=None):
    """One process per call: the engine starts fresh for each mode."""
    os.makedirs(f'{ANSWERS_DIR}/{tag}', exist_ok=True)
    cmd = [PYBIN, f'{SRC_DIR}/harness.py', '--model', tag, '--cond', ','.join(conds), '--rep', '1']
    if limit: cmd += ['--limit', str(limit)]
    t0 = time.time()
    rc = stream(cmd, f'{ANSWERS_DIR}/{tag}/run_log_{tag}.txt', env=harness_env(answers_dir or ANSWERS_DIR))
    return rc, time.time() - t0

def mark(tag, ok, detail=''):
    name = 'DONE_revision3' if ok else 'ERROR_revision3.txt'
    with open(f'{ANSWERS_DIR}/{tag}/{name}', 'w') as fh:
        fh.write(time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()) + '\n' + detail)

if not RUN_PART2:
    print('part 2 skipped (RUN_PART2 = False)')
else:
    os.makedirs(f'{ANSWERS_DIR}/{TAGS["verbal"]}', exist_ok=True)
    env_log = f'{ANSWERS_DIR}/{TAGS["verbal"]}/run_log_{TAGS["verbal"]}.txt'
    rc = stream(['bash', '-c', INSTALL + f'{PYBIN} -c "import vllm, torch; print(\'vllm\', vllm.__version__, \'torch\', torch.__version__)"'], env_log)
    if rc:
        print(f'=== vLLM env build failed (exit {rc}); part 2 stops here, see {env_log} ===')
    else:
        run_log.setdefault('part2', {}).update({'variant': COMPARATOR2_VARIANT, 'tags': TAGS})
        n_q = sum(EXPECTED[c]['requests'] for c in CONDS)
        # smoke tests first: 5 requests of each mode on the condition of the full run
        smoke_ok = True
        for mode in ('verbal', 'll'):
            tag = TAGS[mode]
            sd = f'/content/smoke/{tag}'
            shutil.rmtree(sd, ignore_errors=True)
            print(f'=== {tag}: smoke test, 5 requests of {SMOKE_COND} ===', flush=True)
            rc, dt = harness(tag, [SMOKE_COND], limit=5, answers_dir=sd)
            errs, _ = smoke_report(sd)
            print(f'{tag}: smoke {dt:.0f} s including the engine start (exit {rc}, '
                  f'{len(errs)} error lines)', flush=True)
            run_log['part2'][f'smoke_{mode}_s_incl_load'] = dt
            if rc or errs:
                smoke_ok = False
                mark(tag, False, f'smoke test failed (exit {rc}); {errs[:1]}')
                continue
            # engine time per question from the smoke answers (batch share, no engine start)
            per_q = []
            with open(f'{sd}/{tag}/{SMOKE_COND}__rep1.jsonl', encoding='utf-8') as fh:
                for l in fh:
                    j = json.loads(l)
                    if not j.get('error'):
                        for a in j['answers'].values():
                            r = a.get('raw') or {}
                            if r.get('batch_wall_s') is not None and r.get('n_requests'):
                                per_q.append(r['batch_wall_s'] / r['n_requests'])
            if per_q:
                s = sum(per_q) / len(per_q)
                print(f'{tag}: {s:.2f} s per question in the smoke batch -> about {s * n_q / 60:.0f} min '
                      f'for the {n_q} questions of {CONDS}; small smoke batches overstate batched time',
                      flush=True)
                run_log['part2'][f'smoke_{mode}_s_per_question'] = s
        if not smoke_ok:
            print('=== a comparator smoke test failed; see the run_log_*.txt files. If the log shows '
                  'out-of-memory on an L4, part 2 needs an A100 (or COMPARATOR2_VARIANT = "awq"). ===')
        else:
            for mode in ('verbal', 'll'):
                tag = TAGS[mode]
                print(f'=== {tag}: {CONDS} ===', flush=True)
                try:
                    rc, dt = harness(tag, CONDS)
                    missing = [c for c in CONDS
                               if answer_counts(f'{ANSWERS_DIR}/{tag}/{c}__rep1.jsonl')[0]
                               < EXPECTED[c]['requests']]
                    print(f'[{tag}] exit {rc}, {dt / 60:.1f} min, incomplete: {missing}', flush=True)
                    run_log['part2'][f'{mode}_min'] = dt / 60
                    ok = rc == 0 and not missing
                    mark(tag, ok, '' if ok else f'exit {rc}, incomplete {missing}')
                except Exception:
                    tb = traceback.format_exc()
                    mark(tag, False, tb)
                    print(tb)
    subprocess.run(['nvidia-smi', '--query-gpu=memory.used', '--format=csv,noheader'])
'''

STATUS = r'''import json, os, datetime, zipfile

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

variant = globals().get('COMPARATOR2_VARIANT', 'fp8')
T = COMPARATOR2_TAGS[variant]
planned = [('part 1a', t, OOS) for t in DECISION_TAGS]
if globals().get('RUN_COMPARATOR'):
    planned += [('part 1b', 'comparator-open', OOS)]
if globals().get('RUN_BACKBONE_DESC'):
    planned += [('part 1c', t, c) for t in DESC_TAGS for c in DESC_CONDS]
planned += [('part 2', T[m], c) for m in ('verbal', 'll') for c in PART2_CONDS]

status, problems = {}, []
for part, tag, cond in planned:
    want = EXPECTED[cond]['requests']
    path = f'{ANSWERS_DIR}/{tag}/{cond}__rep1.jsonl'
    key = f'{tag}/{cond}__rep1'
    if not os.path.exists(path):
        status[key] = f'MISSING ({part})'
        problems.append(key)
        continue
    ok, err, revs, ntok, trunc, errs = scan(path)
    pin = REVISIONS[TAG_REPO[tag]]
    rev_ok = revs == {pin}
    note = (f'{ok}/{want} answered, {err} error lines ({trunc} over the length limit), '
            f'revision {"ok" if rev_ok else revs}')
    if ntok:
        note += f', longest prompt {ntok} tokens'
    complete = ok >= want and rev_ok
    status[key] = ('OK ' if complete else 'INCOMPLETE ') + note
    if errs:
        status[key] += f', errors: {errs}'
    if not complete:
        problems.append(key)

for k, v in status.items():
    print(f'{k:62s} {v}')
run_log['end'] = datetime.datetime.utcnow().isoformat() + 'Z'
run_log['status'] = status
run_log['revisions_pinned'] = REVISIONS
with open(f'{ANSWERS_DIR}/run_log_revision3.json', 'w') as fh:
    json.dump(run_log, fh, indent=2)

if problems:
    print(f'\n{len(problems)} file(s) missing or incomplete. A part not run yet shows as MISSING; '
          'otherwise re-run the cell of that model: finished requests are skipped.')
else:
    with open(f'{ANSWERS_DIR}/ALL_DONE_revision3', 'w') as fh:
        fh.write(run_log['end'] + '\n')
    print('\nEvery planned answer file is complete. ALL_DONE_revision3 written.')

# the hand-back archive, next to the folder on Drive: the answer files, the DONE markers and
# run_log_revision3.json; console logs and tracebacks stay on Drive only
archive = f'{DRIVE_ROOT}/answers_revision3.zip'
n_files = 0
with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as z:
    for root, _dirs, files in os.walk(ANSWERS_DIR):
        for fn in sorted(files):
            if fn.endswith('.jsonl') or fn in ('DONE_revision3', 'run_log_revision3.json',
                                               'ALL_DONE_revision3'):
                full = os.path.join(root, fn)
                z.write(full, os.path.relpath(full, ANSWERS_DIR))
                n_files += 1
print(f'hand-back archive: {archive} ({n_files} files)')
'''


def _consistency(man):
    """Build-time checks on the plan, before anything is written."""
    assert [p[0] for p in PLAN] == DECISION_TAGS, [p[0] for p in PLAN]
    assert set(DESC_TAGS) == set(AD.BACKBONE_DESC_OF), DESC_TAGS
    assert man[OOS]["requests"] == 800 and man[OOS]["derived_from"] == "d2_k150"
    for t in DECISION_TAGS + ["comparator-open"] + DESC_TAGS:
        assert TAG_REPO[t] in REVISIONS, t
    for v in COMP_TAGS.values():
        for t in v.values():
            assert t in AD.COMPARATOR2_TAGS and TAG_REPO[t] in REVISIONS, t
    for t in DESC_TAGS:
        # the description backend loads the backbone repo of its key-scoring twin
        assert TAG_REPO[t] == R2.TAG_REPO[AD.BACKBONE_DESC_OF[t]], t
    for c in DESC_SMOKE:
        assert c in DESC_CONDS, c


def build(check=False):
    man = json.load(open(os.path.join(INPUTS, "manifest.json"), encoding="utf-8"))
    _consistency(man)
    for c in SHIP_INPUTS:
        assert sha256(os.path.join(INPUTS, man[c]["file"])) == man[c]["sha256"], c
    expected = {c: {"file": man[c]["file"], "sha256": man[c]["sha256"],
                    "requests": man[c]["requests"]} for c in SHIP_INPUTS}
    src_sha = {f: sha256(os.path.join(HERE, f)) for f in SRC_FILES}

    # ---------------------------------------------------------------- the upload zip
    with zipfile.ZipFile(OUT_ZIP, "w", zipfile.ZIP_DEFLATED) as z:
        for f in SRC_FILES:
            z.write(os.path.join(HERE, f), f"shared/src/{f}")
        for c in SHIP_INPUTS:
            z.write(os.path.join(INPUTS, man[c]["file"]), f"shared/colab/inputs/{man[c]['file']}")
        z.write(os.path.join(INPUTS, "manifest.json"), "shared/colab/inputs/manifest.json")
    zip_sha = sha256(OUT_ZIP)

    cells = []
    cells.append(md(
        "# Paper 4, third revision runs\n\n"
        "Two parts. Each can run in its own runtime; set the switches in the next cell.\n\n"
        "1. **Part 1 (L4).** In this order: (a) the open decision models `laya-ml`, `kev-0.8b`, "
        "`decider-2b`, `this-that-1.0`, `kev-9b` and `nimble-9b` on `d2_k150_oos`, the intent "
        "benchmark with an explicit out-of-scope option `o151`; (b) the Qwen3-14B generative "
        "comparator `comparator-open` on the same condition (switch `RUN_COMPARATOR`); (c) the "
        "untuned Qwen3.5 backbones scored on option descriptions, `backbone-desc-qwen35-*`, on "
        "`d1_neutral`, `d2_k150` and the four D3 tasks (switch `RUN_BACKBONE_DESC`). `laya-en` is "
        "not run: its English head refuses every 150-option question.\n"
        "2. **Part 2 (A100).** Qwen3.6-27B-FP8 through vLLM, as `comparator-open2` (verbalized "
        "JSON) and `comparator-open2-ll` (option-key likelihood), on `d2_k150_oos`.\n\n"
        "Before Run all, upload `revision3_upload.zip` to `My Drive/Jev/paper4/colab/`. The "
        "notebook unpacks it and checks every file against its SHA-256. Answers are written "
        "line by line to `My Drive/Jev/paper4/colab/answers_revision3/`, so a disconnect loses "
        "nothing: run all again and finished requests are skipped. A failing condition or model "
        "never stops the others. The last cell lists every planned file and writes "
        "`answers_revision3.zip` next to the folder for hand-back."))

    cells.append(code(
        "import subprocess as _sp, sys as _sys\n"
        "_sp.run([_sys.executable, '-m', 'pip', 'install', '-q', 'uv'], check=False)\n"
        "from google.colab import drive\n"
        "drive.mount('/content/drive')\n\n"
        "import os, json, time, datetime\n\n"
        "# ---- switches: part 1 on an L4 runtime, part 2 on an A100 runtime (or both on an A100)\n"
        "RUN_PART1 = True          # decision models, then the switches below\n"
        "RUN_COMPARATOR = True     # part 1b: comparator-open (Qwen3-14B-AWQ) on d2_k150_oos\n"
        "RUN_BACKBONE_DESC = True  # part 1c: the four description-scoring backbones\n"
        "RUN_DECISION_MODELS = True  # part 1a; False reruns only parts 1b and 1c\n"
        "DESC_ONLY = None          # or a list, e.g. ['backbone-desc-qwen35-9b-base', 'backbone-desc-qwen35-9b']\n"
        "RUN_PART2 = True          # Qwen3.6-27B comparator, both modes\n"
        "COMPARATOR2_VARIANT = 'fp8'   # 'fp8' on an A100; 'awq' is the L4 fallback (tags *-awq*)\n"
        "# compute units per hour, as Colab shows them in the Resources panel (assumptions until checked)\n"
        "UNITS_PER_HOUR = {'L4': 4.8, 'A100': 11.8}\n\n"
        f"LOCAL_ROOT = {NB_ROOT!r}\n"
        "SHARED_LOCAL = f'{LOCAL_ROOT}/shared'\n"
        "SRC_DIR = f'{SHARED_LOCAL}/src'\n"
        "INPUTS_DIR = f'{SHARED_LOCAL}/colab/inputs'\n"
        "os.environ['HF_HOME'] = '/content/hf'\n"
        "os.environ['USE_TF'] = '0'\n\n"
        "DRIVE_ROOT = '/content/drive/MyDrive/Jev/paper4/colab'\n"
        "UPLOAD_ZIP = f'{DRIVE_ROOT}/revision3_upload.zip'\n"
        "ANSWERS_DIR = f'{DRIVE_ROOT}/answers_revision3'\n"
        "os.makedirs(ANSWERS_DIR, exist_ok=True)\n"
        "# the run log accumulates across the two runtimes\n"
        "_rl = f'{ANSWERS_DIR}/run_log_revision3.json'\n"
        "run_log = json.load(open(_rl)) if os.path.exists(_rl) else {}\n"
        "run_log.setdefault('runtimes', []).append({'start': datetime.datetime.utcnow().isoformat() + 'Z',\n"
        "                                           'part1': RUN_PART1, 'comparator': RUN_COMPARATOR,\n"
        "                                           'backbone_desc': RUN_BACKBONE_DESC, 'part2': RUN_PART2})\n"
        "run_log['units_per_hour_assumed'] = UNITS_PER_HOUR\n"
        "print('answers on Drive:', ANSWERS_DIR, '| part 1:', RUN_PART1, '(comparator', RUN_COMPARATOR,\n"
        "      '| backbones', RUN_BACKBONE_DESC, ') | part 2:', RUN_PART2)"))

    cells.append(code(
        "import subprocess, shutil\n"
        "gpu_info = subprocess.run(['nvidia-smi', '--query-gpu=name,driver_version,memory.total',\n"
        "                           '--format=csv,noheader'], capture_output=True, text=True).stdout.strip()\n"
        "run_log['runtimes'][-1]['gpu'] = gpu_info\n"
        "if RUN_PART1: run_log['part1_gpu'] = gpu_info\n"
        "if RUN_PART2: run_log['part2_gpu'] = gpu_info\n"
        "print(gpu_info)\n"
        "print(f\"free disk under /content: {shutil.disk_usage('/content').free / 1e9:.0f} GB\")\n"
        "if RUN_PART2 and COMPARATOR2_VARIANT == 'fp8' and 'A100' not in gpu_info and 'H100' not in gpu_info:\n"
        "    print('WARNING: part 2 with the FP8 checkpoint needs 40 GB (an A100). On an L4 either '\n"
        "          'switch to an A100 runtime or set COMPARATOR2_VARIANT = \"awq\" (tags *-awq*).')\n"
        "if RUN_PART1 and not RUN_PART2 and 'L4' not in gpu_info:\n"
        "    print('note: part 1 was planned for an L4; latencies will not match the earlier runs.')"))

    cells.append(md("## Unpack the upload and verify every file"))
    cells.append(code(
        "import hashlib, zipfile, shutil\n\n"
        f"EXPECTED = {json.dumps(expected, indent=1, sort_keys=True)}\n"
        f"SRC_SHA256 = {json.dumps(src_sha, indent=1, sort_keys=True)}\n"
        f"ZIP_SHA256 = {zip_sha!r}\n\n"
        "def _sha256(path):\n"
        "    h = hashlib.sha256()\n"
        "    with open(path, 'rb') as fh:\n"
        "        for chunk in iter(lambda: fh.read(1 << 20), b''):\n"
        "            h.update(chunk)\n"
        "    return h.hexdigest()\n\n"
        "if not os.path.exists(UPLOAD_ZIP):\n"
        "    raise SystemExit(f'{UPLOAD_ZIP} not found: upload revision3_upload.zip to that Drive folder first.')\n"
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
        "if bad:\n"
        "    raise SystemExit(f'these files do not match the build: {bad} -- stopping.')\n"
        "print(f'{len(EXPECTED)} input files and {len(SRC_SHA256)} source files verified.')"))

    cells.append(md(
        "## Revisions, plan and helpers\n\nEvery checkpoint is pinned through `P4_REVISIONS`, "
        "which `adapters.py` reads: the decision models and Qwen3-14B-AWQ to the commits of "
        "their original answers (as in the first revision run), the backbones and Qwen3.6-27B "
        "to the commits of the second revision run. The description-scoring tags load the same "
        "backbone checkpoints as the key-scoring tags."))
    cells.append(code(
        f"REVISIONS = {json.dumps(REVISIONS, indent=1, sort_keys=True)}\n"
        f"TAG_REPO = {json.dumps(TAG_REPO, indent=1)}\n"
        f"OOS = {OOS!r}\n"
        f"DECISION_TAGS = {DECISION_TAGS!r}\n"
        f"DESC_TAGS = {DESC_TAGS!r}\n"
        f"DESC_CONDS = {DESC_CONDS!r}\n"
        f"PART2_CONDS = {PART2_CONDS!r}\n"
        f"COMPARATOR2_TAGS = {json.dumps(COMP_TAGS, indent=1)}\n"
        + HELPERS +
        "\nprint(json.dumps(REVISIONS, indent=1))"))

    cells.append(md(
        "## Part 1a: open decision models on d2_k150_oos\n\nEach cell builds (or reuses) its "
        "uv env, smoke-tests 5 requests (any error line stops that model), prints a time "
        "estimate, then runs the 800 requests. Output is streamed and appended to "
        "`answers_revision3/<tag>/run_log_<tag>.txt`. Look for `DONE_revision3` or "
        "`ERROR_revision3.txt` in each model folder."))
    for tag, env, pkgs, opt in PLAN:
        jobs = [(tag, OOS, 1)]
        src = (DECISION_RUNNER.replace("__TAG__", repr(tag)).replace("__ENV__", repr(env))
               .replace("__INSTALL__", repr(R1.install_script(env, pkgs, opt)))
               .replace("__JOBS__", repr(jobs)))
        cells.append(md(f"### {tag}"))
        cells.append(code(src))

    cells.append(md(
        "## Part 1b: generative comparator on d2_k150_oos\n\nQwen3-14B-AWQ through vLLM, tag "
        "`comparator-open`, with the settings of its earlier runs (greedy, thinking off, "
        "verbalized JSON). vLLM is pinned to 0.30.0, the version its first run logged. Switch "
        "`RUN_COMPARATOR` in the first code cell."))
    cells.append(code(COMPARATOR_RUNNER.replace("__INSTALL__", repr(VLLM_INSTALL))
                      .replace("__CONDS__", repr([OOS]))))

    cells.append(md(
        "## Part 1c: backbones scored on option descriptions\n\nEach cell builds (or reuses) "
        "the `backbone` uv env, runs a smoke test of 2 requests on each of `d2_k150`, "
        "`d1_neutral` and `d3_emotion` with the self-check on (every description is rescored by "
        "a plain full-sequence forward pass; the two option distributions must agree within "
        "0.15), then runs all six conditions in one process. A condition left incomplete is "
        "retried on its own. Switch `RUN_BACKBONE_DESC` in the first code cell."))
    notes = {"backbone-desc-qwen35-0.8b-base": "Qwen/Qwen3.5-0.8B-Base, the base of kev-0.8b.",
             "backbone-desc-qwen35-2b-base": "Qwen/Qwen3.5-2B-Base, the base of decider-2b and "
                                             "this-that-1.0.",
             "backbone-desc-qwen35-9b-base": "Qwen/Qwen3.5-9B-Base, the base of kev-9b.",
             "backbone-desc-qwen35-9b": "Qwen/Qwen3.5-9B (post-trained), the base of nimble-9b."}
    install = R2.install_script("backbone", R2.BACKBONE_PKGS, R2.BACKBONE_OPT)
    for tag in DESC_TAGS:
        cells.append(md(f"### {tag}\n\n{notes[tag]}"))
        cells.append(code(BACKBONE_DESC_RUNNER.replace("__TAG__", repr(tag))
                          .replace("__INSTALL__", repr(install))
                          .replace("__CONDS__", repr(DESC_CONDS))
                          .replace("__SMOKE__", repr(DESC_SMOKE))))

    cells.append(md(
        "## Part 2: stronger comparator on d2_k150_oos\n\nBuilds the `vllm_env` env (vLLM "
        f"{R2.VLLM_VERSION}), smoke-tests both modes on 5 requests of `d2_k150_oos`, then runs "
        "the verbalized mode and the likelihood mode, each in a fresh process."))
    cells.append(code(PART2_RUNNER.replace("__INSTALL__", repr(VLLM_INSTALL))
                      .replace("__CONDS__", repr(PART2_CONDS))))

    cells.append(md(
        "## Status and hand-back\n\nLists every planned answer file with its count of answered "
        "requests, error lines, the longest prompt in tokens (backbones) and the recorded "
        "revision against the pin. A part not run yet shows as MISSING. Then writes "
        "`answers_revision3.zip` into `My Drive/Jev/paper4/colab/`."))
    cells.append(code(STATUS))

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
    n_dec = len(DECISION_TAGS) * man[OOS]["requests"]
    n_comp = man[OOS]["requests"]
    n_desc = len(DESC_TAGS) * sum(man[c]["requests"] for c in DESC_CONDS)
    print(f"part 1a: {len(DECISION_TAGS)} files, {n_dec} requests; part 1b: 1 file, {n_comp} "
          f"requests; part 1c: {len(DESC_TAGS) * len(DESC_CONDS)} files, {n_desc} requests; "
          f"part 2: {2 * len(PART2_CONDS)} files, "
          f"{2 * sum(man[c]['requests'] for c in PART2_CONDS)} requests")
    if check:
        _check(nb, man)


def _check(nb, man):
    """Compile every code cell and the shipped source files, check the zip against the
    manifest, and look for names of the earlier runs left in the notebook."""
    n = 0
    for cell in nb["cells"]:
        if cell["cell_type"] != "code":
            continue
        src = "\n".join(l for l in cell["source"].splitlines() if not l.startswith(("%", "!")))
        with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8") as fh:
            fh.write(src)
            tmp = fh.name
        try:
            py_compile.compile(tmp, doraise=True)
            n += 1
        finally:
            os.unlink(tmp)
    for f in SRC_FILES:
        py_compile.compile(os.path.join(HERE, f), doraise=True)
    print(f"py_compile OK for {n} code cells and {len(SRC_FILES)} source files")

    with zipfile.ZipFile(OUT_ZIP) as z:
        names = set(z.namelist())
        want = ({f"shared/src/{f}" for f in SRC_FILES}
                | {f"shared/colab/inputs/{man[c]['file']}" for c in SHIP_INPUTS}
                | {"shared/colab/inputs/manifest.json"})
        assert names == want, sorted(names ^ want)
        for c in SHIP_INPUTS:
            got = hashlib.sha256(z.read(f"shared/colab/inputs/{man[c]['file']}")).hexdigest()
            assert got == man[c]["sha256"], c
        for f in SRC_FILES:
            got = hashlib.sha256(z.read(f"shared/src/{f}")).hexdigest()
            assert got == sha256(os.path.join(HERE, f)), f
    print(f"zip OK: {len(SHIP_INPUTS)} inputs match the manifest SHA-256, {len(SRC_FILES)} "
          f"source files match the working copy")

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
