"""Build colab/run_revision.ipynb and colab/revision_upload.zip for the revision runs.

What the notebook runs, on one Colab L4 runtime, for the open models of the benchmark:

  1. every open decision model (laya-en, laya-ml, kev-0.8b, decider-2b, this-that-1.0, kev-9b,
     nimble-9b) on the eight new permutation conditions d2_k{5,20,50,150}_p{2,3} at rep 1
     (reviewer point 1; frozen by s00c_freeze_permutations.py)
  2. this-that-1.0 under the description-only rendering, tag this-that-1.0-desc, on d1_neutral
     and d2_k150 at rep 1 (reviewer point 2; adapters.thisthat_render)
  3. a rep-2 retest of every open model on the two aligned binary D3 naming conditions,
     e2_d3_conv_go_awry_kny and e2_d3_wiki_corpus_kny, so that each binary set has a measured
     run-to-run floor for the open models as it already has for Jev (switch RUN_D3_RETEST)
  4. optional, off by default: the open generative comparator on the eight permutation
     conditions plus the p1 files d2_k5 and d2_k50 it did not answer in the first run
     (switch RUN_COMPARATOR)

Conventions follow run_open.ipynb (build_notebook.py) and run_comparator.ipynb: one uv env per
model family built with --extra-index-url for the CUDA 12.8 torch wheels and
--index-strategy unsafe-best-match, shlex-quoted package specs, repr-embedded install scripts,
a smoke test before each model, a failed condition never aborting the others, DONE or
ERROR.txt per model, the env's bin folder on PATH (ninja for FlashInfer JIT) and the FlashInfer
sampler off for vLLM, answers flushed line by line to Drive, and a final status cell that lists
every missing or incomplete answer file. Two differences, both deliberate: the inputs are not
rebuilt from public sources but shipped in revision_upload.zip and checked against the embedded
SHA-256 of manifest.json, and every model is pinned through P4_REVISIONS to the exact revision
its original answers record (run_log.json of the first run holds no revisions; the pins below
were read from the "revision" field of shared/answers/<tag>/*.jsonl).

Answers go to My Drive/Jev/paper4/colab/answers_revision/<tag>/<cond>__rep<k>.jsonl, the same
layout as shared/answers, so the hand-back zip unpacks straight into shared/answers.

Usage: python build_revision_notebook.py [--check]
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

HERE = os.path.dirname(os.path.abspath(__file__))
SHARED = os.path.dirname(HERE)
COLAB = os.path.join(SHARED, "colab")
INPUTS = os.path.join(COLAB, "inputs")
OUT_NB = os.path.join(COLAB, "run_revision.ipynb")
OUT_ZIP = os.path.join(COLAB, "revision_upload.zip")

SRC_FILES = ["common.py", "harness.py", "adapters.py"]
PERM_CONDS = [f"d2_k{k}_{p}" for p in ("p2", "p3") for k in (5, 20, 50, 150)]
DESC_CONDS = ["d1_neutral", "d2_k150"]
D3_RETEST_CONDS = ["e2_d3_conv_go_awry_kny", "e2_d3_wiki_corpus_kny"]
COMPARATOR_CONDS = PERM_CONDS + ["d2_k5", "d2_k50"]
SHIP_INPUTS = sorted(set(PERM_CONDS + DESC_CONDS + D3_RETEST_CONDS + COMPARATOR_CONDS))

OPEN_TAGS = ["laya-en", "laya-ml", "kev-0.8b", "decider-2b", "this-that-1.0", "kev-9b",
             "nimble-9b"]
# the revision recorded in every original answer line of each model (shared/answers/<tag>/)
REVISIONS = {
    "convaiinnovations/laya": "55cf4c4ebb4ebe31b2550e8bdf3bd21b99753851",
    "jaredpalmer/kev-0.8b": "9a45d25eb2ab761841196625383fa1dff0e56c1e",
    "jaredpalmer/kev-9b": "2629c06a5aeb0feb3b9783bafed17ed8f39ecf5c",
    "Mapika/decider-2b": "d61c1c16089572df5d180329b9fea4997a90090c",
    "flock-io/this-that-model-1.0": "3d927195c4f9845efe66c5715883a7a0f42b1239",
    "bespokelabs/Bespoke-Nimble-9B": "bd792f44ec8e265be861bfcdf4e05967ffe0e858",
    "Qwen/Qwen3-14B-AWQ": "31c69efc29464b6bb0aee1398b5a7b50a99340c3",
}
TAG_REPO = {"laya-en": "convaiinnovations/laya", "laya-ml": "convaiinnovations/laya",
            "kev-0.8b": "jaredpalmer/kev-0.8b", "kev-9b": "jaredpalmer/kev-9b",
            "decider-2b": "Mapika/decider-2b", "this-that-1.0": "flock-io/this-that-model-1.0",
            "this-that-1.0-desc": "flock-io/this-that-model-1.0",
            "nimble-9b": "bespokelabs/Bespoke-Nimble-9B", "comparator-open": "Qwen/Qwen3-14B-AWQ"}

KEV_GIT = "kev @ git+https://github.com/jaredpalmer/kev@73504e51f6ce2ade19c7819d4a5f2d84363cd40f"
THISTHAT_GIT = ("thisthat @ git+https://github.com/FLock-io/this-that-model@"
                "542d445efa5f68b14bfbd1f8ed25aacd8379d839")
TORCH_CU128 = ("--extra-index-url https://download.pytorch.org/whl/cu128 "
               "--index-strategy unsafe-best-match")
BASE = ["torch==2.8.0", "transformers>=5.17,<6", "peft>=0.21", "accelerate>=1.15",
        "huggingface_hub", "python-dotenv", "httpx", "pydantic", "numpy", "scipy"]
LAYA_PKGS = ["torch==2.8.0", "laya==0.3.20", "python-dotenv", "httpx", "numpy"]
NIMBLE_PKGS = ["torch==2.8.0", "transformers==5.17.0", "peft==0.21.0", "accelerate==1.15.0",
               "sentencepiece==0.2.2", "pillow==12.3.0", "huggingface_hub>=0.34",
               "python-dotenv", "httpx", "numpy"]

# model cells: (tag, env, packages, optional packages, [(run tag, conds, rep)])
PLAN = [
    ("laya-en", "laya", LAYA_PKGS, []),
    ("laya-ml", "laya", LAYA_PKGS, []),
    ("kev-0.8b", "kev_decider_tt", BASE + [KEV_GIT], ["flash-linear-attention"]),
    ("decider-2b", "kev_decider_tt", BASE + [KEV_GIT], ["flash-linear-attention"]),
    ("this-that-1.0", "kev_decider_tt", BASE + [KEV_GIT, THISTHAT_GIT],
     ["flash-linear-attention"]),
    ("kev-9b", "kev_decider_tt", BASE + [KEV_GIT], ["flash-linear-attention"]),
    ("nimble-9b", "nimble", NIMBLE_PKGS, ["flash-linear-attention"]),
]
NB_ROOT = "/content/p4"


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def md(t):
    return nbf.v4.new_markdown_cell(t)


def code(t):
    return nbf.v4.new_code_cell(t)


def install_script(env_name, pkgs, optional=()):
    """Bash for one uv env, identical in form to build_notebook.install_script."""
    py = f"/content/envs/{env_name}/bin/python"
    pre = "export UV_CACHE_DIR=/content/uv-cache; "
    lines = [pre + f"uv venv /content/envs/{env_name} --python 3.12 -q --allow-existing",
             pre + f"uv pip install --python {py} -q {TORCH_CU128} "
             + " ".join(shlex.quote(p) for p in pkgs)]
    for o in optional:
        lines.append("(" + pre + f"uv pip install --python {py} -q {TORCH_CU128} "
                     + shlex.quote(o) + " || echo 'optional package failed: " + o + "')")
    return "set -e\n" + "\n".join(lines) + "\n"


RUNNER = r'''import subprocess, sys, time, json, os, traceback

TAG = __TAG__
ENV_NAME = __ENV__
PYBIN = f'/content/envs/{ENV_NAME}/bin/python'
INSTALL = __INSTALL__
JOBS = __JOBS__            # [(run tag, condition, rep), ...]
TAG_DIR = f'{ANSWERS_DIR}/{TAG}'
os.makedirs(TAG_DIR, exist_ok=True)
LOG = f'{TAG_DIR}/run_log_{TAG}.txt'
SMOKE_DIR = f'/content/smoke/{TAG}'
os.makedirs(SMOKE_DIR, exist_ok=True)

def harness_env(answers_dir):
    env = dict(os.environ)
    env['HF_HOME'] = '/content/hf'
    env['P4_INPUTS'] = INPUTS_DIR
    env['P4_ANSWERS'] = answers_dir
    env['P4_REVISIONS'] = json.dumps(REVISIONS)
    # ninja and any other console script of the env must be on PATH (FlashInfer JIT, Triton)
    env['PATH'] = f'/content/envs/{ENV_NAME}/bin:' + env.get('PATH', '')
    return env

def run_harness(run_tag, cond, rep, limit=None, answers_dir=None):
    """One condition in its own process; every output line goes to the cell and the Drive log."""
    cmd = [PYBIN, f'{SRC_DIR}/harness.py', '--model', run_tag, '--cond', cond, '--rep', str(rep)]
    if limit: cmd += ['--limit', str(limit)]
    t0 = time.time()
    with open(LOG, 'a', encoding='utf-8') as log:
        log.write(f'\n$ {" ".join(cmd)}\n'); log.flush()
        p = subprocess.Popen(cmd, cwd=SRC_DIR, env=harness_env(answers_dir or ANSWERS_DIR),
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
        for line in p.stdout:
            log.write(line); log.flush()
            print(line, end='', flush=True)
        rc = p.wait()
    return rc, time.time() - t0

failed = []
try:
    print(f'=== {TAG}: building env {ENV_NAME} ===', flush=True)
    subprocess.run(['bash', '-c', INSTALL], check=True)

    print(f'=== {TAG}: smoke test (5 requests of {JOBS[0][1]}) ===', flush=True)
    rc, dt = run_harness(JOBS[0][0], JOBS[0][1], 1, limit=5, answers_dir=SMOKE_DIR)
    if rc:
        raise RuntimeError(f'{TAG}: smoke test failed (exit {rc}); see {LOG}')
    n_req = sum(EXPECTED[c]['requests'] for _t, c, _r in JOBS)
    print(f'{TAG}: {dt / 5:.2f} s per request including the model load -> at most '
          f'{dt / 5 * n_req / 60:.0f} min for {n_req} requests, '
          f'~{dt / 5 * n_req / 3600 * 4.8:.1f} compute units at 4.8/h on an L4 (assumption)', flush=True)
    run_log['models'][TAG] = {'smoke_s_per_request_incl_load': dt / 5, 'requests': n_req}

    for run_tag, cond, rep in JOBS:
        rc, dt = run_harness(run_tag, cond, rep)
        print(f'[{run_tag}] {cond} rep{rep}: exit {rc}, {dt / 60:.1f} min', flush=True)
        if rc:
            failed.append(f'{run_tag}/{cond}__rep{rep}')
    if failed:
        raise RuntimeError(f'{TAG}: conditions failed: {failed}')
    with open(f'{TAG_DIR}/DONE_revision', 'w') as fh:
        fh.write(time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()) + '\n')
    print(f'=== {TAG}: DONE ===')
except Exception:
    tb = traceback.format_exc()
    with open(f'{TAG_DIR}/ERROR_revision.txt', 'w') as fh:
        fh.write(tb)
    print(f'=== {TAG}: ERROR, continuing with the next model (see {TAG_DIR}/ERROR_revision.txt) ===')
    print(tb)
finally:
    import gc
    gc.collect()
    subprocess.run(['nvidia-smi', '--query-gpu=memory.used', '--format=csv,noheader'])
'''

COMPARATOR = r'''import subprocess, sys, time, json, os, traceback

RUN_COMPARATOR = False     # set to True to run the comparator (about 1.5 h on an L4)
TAG = 'comparator-open'
ENV_NAME = 'vllm_env'
PYBIN = f'/content/envs/{ENV_NAME}/bin/python'
CONDS = __CONDS__
TAG_DIR = f'{ANSWERS_DIR}/{TAG}'
LOG = f'{TAG_DIR}/run_log_{TAG}.txt'

def stream(cmd, env=None):
    with open(LOG, 'a', encoding='utf-8') as log:
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

if not RUN_COMPARATOR:
    print('comparator skipped (RUN_COMPARATOR = False)')
else:
    os.makedirs(TAG_DIR, exist_ok=True)
    try:
        print('=== comparator-open: building env ===', flush=True)
        rc = stream(['bash', '-c',
                     'set -e; export UV_CACHE_DIR=/content/uv-cache; '
                     f'uv venv /content/envs/{ENV_NAME} --python 3.12 -q --allow-existing; '
                     f'uv pip install --python {PYBIN} -q '
                     'vllm huggingface_hub python-dotenv httpx numpy ninja; '
                     f'{PYBIN} -c "import vllm, torch; print(\'vllm\', vllm.__version__, \'torch\', torch.__version__)"'])
        if rc:
            raise RuntimeError(f'env build failed (exit {rc})')
        print('=== comparator-open: smoke test, 5 requests ===', flush=True)
        rc = stream([PYBIN, f'{SRC_DIR}/harness.py', '--model', TAG, '--cond', CONDS[0],
                     '--rep', '1', '--limit', '5'], env=harness_env('/content/smoke/comparator-open'))
        if rc:
            raise RuntimeError(f'smoke test failed (exit {rc}); see {LOG}')
        print('=== comparator-open: full run (one process, model loaded once) ===', flush=True)
        t0 = time.time()
        rc = stream([PYBIN, f'{SRC_DIR}/harness.py', '--model', TAG, '--cond', ','.join(CONDS),
                     '--rep', '1'], env=harness_env(ANSWERS_DIR))
        print(f'full run exit {rc}, {(time.time() - t0) / 60:.1f} min', flush=True)
        if rc:
            raise RuntimeError(f'full run failed (exit {rc}); see {LOG}')
        with open(f'{TAG_DIR}/DONE_revision', 'w') as fh:
            fh.write(time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()) + '\n')
        print('=== comparator-open: DONE ===')
    except Exception:
        tb = traceback.format_exc()
        with open(f'{TAG_DIR}/ERROR_revision.txt', 'w') as fh:
            fh.write(tb)
        print('=== comparator-open: ERROR; the full log is in ' + LOG + ' ===')
        print(tb)
'''

STATUS = r'''import json, os, datetime

def n_ok_lines(path):
    ok = err = 0
    revs, models = set(), set()
    with open(path, encoding='utf-8') as fh:
        for line in fh:
            try:
                j = json.loads(line)
            except json.JSONDecodeError:
                continue
            if j.get('error'):
                err += 1
            else:
                ok += 1
                revs.add(j.get('revision')); models.add(j.get('model'))
    return ok, err, revs, models

expected = list(PLANNED)
if RUN_D3_RETEST:
    expected += PLANNED_D3
if globals().get('RUN_COMPARATOR'):
    expected += PLANNED_COMPARATOR
status, problems = {}, []
for tag, cond, rep in expected:
    path = f'{ANSWERS_DIR}/{tag}/{cond}__rep{rep}.jsonl'
    want = EXPECTED[cond]['requests']
    if not os.path.exists(path):
        status[f'{tag}/{cond}__rep{rep}'] = 'MISSING'
        problems.append(path)
        continue
    ok, err, revs, models = n_ok_lines(path)
    pin = REVISIONS[TAG_REPO[tag]]
    rev_ok = revs == {pin}
    note = f'{ok}/{want} answered, {err} error lines, revision {"ok" if rev_ok else revs}'
    # Laya's English head refuses K=150 by design (its option text exceeds the head budget):
    # error lines there are the expected outcome, recorded exactly as in the first run
    expected_refusal = tag == 'laya-en' and cond.startswith('d2_k150')
    complete = (ok + err >= want) if expected_refusal else (ok == want)
    status[f'{tag}/{cond}__rep{rep}'] = ('OK ' if complete and (rev_ok or expected_refusal and ok == 0)
                                         else 'INCOMPLETE ') + note
    if not (complete and (rev_ok or expected_refusal and ok == 0)):
        problems.append(path)

for k, v in status.items():
    print(f'{k:55s} {v}')
run_log['end'] = datetime.datetime.utcnow().isoformat() + 'Z'
run_log['status'] = status
run_log['revisions_pinned'] = REVISIONS
with open(f'{ANSWERS_DIR}/run_log_revision.json', 'w') as fh:
    json.dump(run_log, fh, indent=2)

if problems:
    print(f'\n{len(problems)} file(s) missing or incomplete. Re-run the cell of that model: '
          'finished requests are skipped, only the rest is computed.')
else:
    with open(f'{ANSWERS_DIR}/ALL_DONE_revision', 'w') as fh:
        fh.write(run_log['end'] + '\n')
    print('\nEvery planned answer file is complete. ALL_DONE_revision written.')

# the hand-back archive, next to the folder on Drive: the answer files, the DONE markers and
# run_log_revision.json; the per-model console logs and tracebacks stay on Drive only
import zipfile
archive = f'{DRIVE_ROOT}/answers_revision.zip'
n_files = 0
with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as z:
    for root, _dirs, files in os.walk(ANSWERS_DIR):
        for fn in sorted(files):
            if fn.endswith('.jsonl') or fn in ('DONE_revision', 'run_log_revision.json',
                                               'ALL_DONE_revision'):
                full = os.path.join(root, fn)
                z.write(full, os.path.relpath(full, ANSWERS_DIR))
                n_files += 1
print(f'hand-back archive: {archive} ({n_files} files)')
'''


def build(check=False):
    man = json.load(open(os.path.join(INPUTS, "manifest.json"), encoding="utf-8"))
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

    planned, planned_d3 = [], []
    cells = []
    cells.append(md(
        "# Paper 4, revision runs of the open models\n\n"
        "Choose an **L4** runtime (Runtime, Change runtime type), then Runtime, Run all. Before "
        "that, upload `revision_upload.zip` to `My Drive/Jev/paper4/colab/` (the folder of the "
        "first run). The notebook unpacks it, checks every file against its SHA-256, and runs:\n\n"
        "1. each open decision model on the eight permutation conditions "
        "`d2_k{5,20,50,150}_p{2,3}` (rep 1);\n"
        "2. this-that-1.0 with description-only option text (`this-that-1.0-desc`) on "
        "`d1_neutral` and `d2_k150`;\n"
        "3. a rep-2 retest of each open model on `e2_d3_conv_go_awry_kny` and "
        "`e2_d3_wiki_corpus_kny` (switch `RUN_D3_RETEST`);\n"
        "4. optional and off by default: the generative comparator (switch `RUN_COMPARATOR` in "
        "its cell).\n\n"
        "Every model is pinned to the revision of its original answers. Answers are written line "
        "by line to `My Drive/Jev/paper4/colab/answers_revision/`, so a disconnect loses nothing: "
        "run all again and finished requests are skipped. A failing condition or model never "
        "stops the others. The last cell lists every missing or incomplete file and writes "
        "`answers_revision.zip` next to the folder for hand-back."))

    cells.append(code(
        "import subprocess as _sp, sys as _sys\n"
        "_sp.run([_sys.executable, '-m', 'pip', 'install', '-q', 'uv'], check=False)\n"
        "from google.colab import drive\n"
        "drive.mount('/content/drive')\n\n"
        "import os, json, time, datetime\n\n"
        f"LOCAL_ROOT = {NB_ROOT!r}\n"
        "SHARED_LOCAL = f'{LOCAL_ROOT}/shared'\n"
        "SRC_DIR = f'{SHARED_LOCAL}/src'\n"
        "INPUTS_DIR = f'{SHARED_LOCAL}/colab/inputs'\n"
        "os.environ['HF_HOME'] = '/content/hf'\n"
        "os.environ['USE_TF'] = '0'\n\n"
        "DRIVE_ROOT = '/content/drive/MyDrive/Jev/paper4/colab'\n"
        "UPLOAD_ZIP = f'{DRIVE_ROOT}/revision_upload.zip'\n"
        "ANSWERS_DIR = f'{DRIVE_ROOT}/answers_revision'\n"
        "os.makedirs(ANSWERS_DIR, exist_ok=True)\n"
        "RUN_D3_RETEST = True      # rep-2 retest of the open models on the two aligned binary D3 sets\n"
        "run_log = {'start': datetime.datetime.utcnow().isoformat() + 'Z', 'models': {}}\n"
        "print('answers on Drive:', ANSWERS_DIR)"))

    cells.append(code(
        "import subprocess\n"
        "gpu_info = subprocess.run(['nvidia-smi', '--query-gpu=name,driver_version,memory.total',\n"
        "                           '--format=csv,noheader'], capture_output=True, text=True).stdout.strip()\n"
        "run_log['gpu'] = gpu_info\n"
        "print(gpu_info)\n"
        "if 'L4' not in gpu_info:\n"
        "    print('WARNING: this is not an L4; latencies will not match the first run.')"))

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
        "    raise SystemExit(f'{UPLOAD_ZIP} not found: upload revision_upload.zip to that Drive folder first.')\n"
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
        "## Revisions\n\nThe commit each model's original answers record. `adapters.py` reads "
        "`P4_REVISIONS` and loads exactly these commits instead of the current head."))
    cells.append(code(
        f"REVISIONS = {json.dumps(REVISIONS, indent=1)}\n"
        f"TAG_REPO = {json.dumps(TAG_REPO, indent=1)}\n"
        "print(json.dumps(REVISIONS, indent=1))"))

    cells.append(md(
        "## Open decision models\n\nEach cell builds (or reuses) its uv env, smoke-tests 5 "
        "requests, prints a time estimate, then runs its conditions one process per condition. "
        "Output is streamed and also appended to `answers_revision/<tag>/run_log_<tag>.txt`. "
        "Look for `DONE_revision` or `ERROR_revision.txt` in each model folder."))
    for tag, env, pkgs, opt in PLAN:
        jobs = [(tag, c, 1) for c in PERM_CONDS]
        if tag == "this-that-1.0":
            jobs += [("this-that-1.0-desc", c, 1) for c in DESC_CONDS]
        planned += jobs
        d3 = [(tag, c, 2) for c in D3_RETEST_CONDS]
        planned_d3 += d3
        src = (RUNNER.replace("__TAG__", repr(tag)).replace("__ENV__", repr(env))
               .replace("__INSTALL__", repr(install_script(env, pkgs, opt)))
               .replace("__JOBS__", repr(jobs) + " + (" + repr(d3) + " if RUN_D3_RETEST else [])"))
        title = f"### {tag}"
        if tag == "this-that-1.0":
            title += ("\n\nAlso runs `this-that-1.0-desc`: the same checkpoint with each choice "
                      "option and score level given as its description alone, on `d1_neutral` "
                      "and `d2_k150`.")
        if tag == "laya-en":
            title += ("\n\nOn the K=150 conditions this model refuses every request (its option "
                      "text exceeds the head budget), exactly as in the first run; those error "
                      "lines are the expected result, not a failure.")
        cells.append(md(title))
        cells.append(code(src))

    cells.append(md(
        "## Optional: generative comparator\n\nOff by default. Set `RUN_COMPARATOR = True` in "
        "the cell to run Qwen3-14B-AWQ through vLLM on the eight permutation conditions plus "
        "`d2_k5` and `d2_k50` (which it did not answer in the first run), so every K has three "
        "permutations."))
    cells.append(code(COMPARATOR.replace("__CONDS__", repr(COMPARATOR_CONDS))))

    cells.append(md(
        "## Status and hand-back\n\nLists every planned answer file with its count of answered "
        "requests and checks the recorded revision against the pin. Then writes "
        "`answers_revision.zip` into `My Drive/Jev/paper4/colab/`."))
    cells.append(code(
        f"PLANNED = {planned!r}\n"
        f"PLANNED_D3 = {planned_d3!r}\n"
        f"PLANNED_COMPARATOR = {[('comparator-open', c, 1) for c in COMPARATOR_CONDS]!r}\n"
        + STATUS))

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
    print(f"{len(planned)} model runs + {len(planned_d3)} D3 retests planned")
    if check:
        _check(nb)


def _check(nb):
    """Compile every code cell (IPython magics stripped) and the shipped source files."""
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    build(check=ap.parse_args().check)


if __name__ == "__main__":
    main()
