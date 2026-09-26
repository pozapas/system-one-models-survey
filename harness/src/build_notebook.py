"""Generates SHARED/colab/run_open.ipynb from the current source files.

The notebook is self-contained (Colab receives no files except through the notebook itself): it
embeds the current contents of common.py, s00_freeze_inputs.py, harness.py, adapters.py and
s00b_prepare_d3.py (if present) as %%writefile cells, plus an embedded copy of
colab/inputs/manifest.json for the post-freeze SHA-256 check.

Usage:
    D:/p4env/venv/Scripts/python.exe build_notebook.py
    D:/p4env/venv/Scripts/python.exe build_notebook.py --check   # also nbformat-validates the
                                                                  # result and py_compiles every
                                                                  # embedded .py file

Re-run this any time common.py / s00_freeze_inputs.py / harness.py / adapters.py / manifest.json
change; the notebook always reflects whatever those files currently say, nothing is hand-maintained
inside run_open.ipynb itself.
"""
import argparse
import gzip
import base64
import json
import os
import py_compile
import tempfile

import nbformat as nbf

HERE = os.path.dirname(os.path.abspath(__file__))
SHARED = os.path.dirname(HERE)
OUT_PATH = os.path.join(SHARED, "colab", "run_open.ipynb")
MANIFEST_PATH = os.path.join(SHARED, "colab", "inputs", "manifest.json")
D3_DATA_DIR = os.path.join(SHARED, "data", "d3")

SRC_FILES = ["common.py", "s00_freeze_inputs.py", "harness.py", "adapters.py"]
D3_SCRIPT = "s00b_prepare_d3.py"
D3_EMBED_LIMIT_BYTES = 1_500_000

# The concrete Colab paths the notebook's own first cell sets LOCAL_ROOT/SRC_DIR/DATA_DIR/
# INPUTS_DIR to (see the "mount + paths" cell below). Bash (%%writefile, %%bash) cells cannot see
# a Python variable from an earlier cell, so anywhere this script builds literal shell text it
# must use these build-time constants -- kept equal to the runtime cell's own construction by
# inspection (both derive from '/content/p4'), not by sharing code, since one runs now (in this
# script) and the other runs later (in the notebook kernel).
NB_LOCAL_ROOT = "/content/p4"
NB_SHARED_LOCAL = f"{NB_LOCAL_ROOT}/shared"
NB_SRC_DIR = f"{NB_SHARED_LOCAL}/src"
NB_DATA_DIR = f"{NB_SHARED_LOCAL}/data"
NB_INPUTS_DIR = f"{NB_SHARED_LOCAL}/colab/inputs"

D1_REPO = "LocalLLaMA/typed-decisions"
D1_REVISION = "c76749ec58bd8c3d2ea706b31c333a9059c38f90"
CLINC_REPO = "clinc/oos-eval"
CLINC_COMMIT_PATH = os.path.join(SHARED, "data", "d2", "CLINC_COMMIT")

# Every decision-model condition, at rep 1, plus a rep-2 retest of d1_neutral only (see the
# "--retest" branch below). "--cond all" already means every condition harness.all_conditions()
# finds in the (regenerated) manifest, so nothing further needs to be listed here.
SMALL_MODELS = ["laya-en", "laya-ml", "kev-0.8b", "decider-2b", "this-that-1.0"]
BIG_MODELS = ["kev-9b", "nimble-9b"]
COMPARATOR_MODEL = "comparator-open"

# harness.py caps a batched gather at 500 records; a 5-request smoke test is comfortably inside
# that and writes into its own answers dir so it never collides with the real run's resume logic.
SMOKE_N = 5


def read_src(name):
    with open(os.path.join(HERE, name), encoding="utf-8") as fh:
        return fh.read()


def gz_b64(path):
    with open(path, "rb") as fh:
        return base64.b64encode(gzip.compress(fh.read())).decode("ascii")


def md(text):
    return nbf.v4.new_markdown_cell(text)


def code(text):
    return nbf.v4.new_code_cell(text)


def writefile_cell(path, content):
    """A %%writefile cell that embeds `content` verbatim at `path`, one line per source line so a
    diff against the source .py file is readable."""
    return code(f"%%writefile {path}\n{content}")


def uv_env_cell(env_name, packages, extra_setup=""):
    return code(
        f"%%bash\n"
        f"set -e\n"
        f'echo "--- building uv env {env_name} ---"\n'
        f"UV_CACHE_DIR=/content/uv-cache uv venv /content/envs/{env_name} --python 3.12 -q\n"
        f"UV_CACHE_DIR=/content/uv-cache uv pip install --python /content/envs/{env_name}/bin/python -q \\\n"
        f"    {packages}\n"
        f"{extra_setup}"
    )


def build(check=False):
    manifest = json.load(open(MANIFEST_PATH, encoding="utf-8"))
    manifest_json_literal = json.dumps(manifest, indent=1, sort_keys=True)

    d3_script_path = os.path.join(HERE, D3_SCRIPT)
    have_d3_script = os.path.exists(d3_script_path)
    d3_embed = None
    if not have_d3_script:
        total = sum(os.path.getsize(os.path.join(D3_DATA_DIR, f))
                   for f in os.listdir(D3_DATA_DIR) if f.endswith(".jsonl")) if os.path.isdir(D3_DATA_DIR) else None
        if total is not None and total < D3_EMBED_LIMIT_BYTES:
            d3_embed = {f: gz_b64(os.path.join(D3_DATA_DIR, f))
                       for f in sorted(os.listdir(D3_DATA_DIR)) if f.endswith(".jsonl")}
        else:
            print(f"D3: s00b_prepare_d3.py is absent and data/d3 is missing or >= "
                 f"{D3_EMBED_LIMIT_BYTES} bytes ({total}); the notebook will skip D3 and say so.")

    cells = []

    # ------------------------------------------------------------------ 0. title / plan
    cells.append(md(
        "# Paper 4 -- open decision models, full benchmark run\n\n"
        "Run all cells top to bottom once (Runtime > Run all) on a Colab Pro **L4** runtime. "
        "Resuming after a disconnect is safe: every model writes its answers straight to Drive, "
        "one flushed JSONL line per request, and re-running a model's cell skips whatever keys "
        "are already in its output file.\n\n"
        "Order: small models first (laya-en, laya-ml, kev-0.8b, decider-2b, this-that-1.0), then "
        "the two 9B models (kev-9b, nimble-9b), then the vLLM comparator last. Each model loads "
        "in its own uv virtual environment and its own subprocess, so one model's failure (or "
        "dependency conflict) cannot take another down; look for `answers/<tag>/DONE` or "
        "`answers/<tag>/ERROR.txt` per model."
    ))

    # ------------------------------------------------------------------ 1. mount + paths
    cells.append(code(
        "import subprocess as _sp, sys as _sys\n"
        "_sp.run([_sys.executable, '-m', 'pip', 'install', '-q', 'uv'], check=False)\n"
        "from google.colab import drive\n"
        "drive.mount('/content/drive')\n\n"
        "import os, json, time, datetime\n\n"
        "# Local (fast) storage: source, HF cache, regenerated inputs. Only answers live on Drive\n"
        "# -- everything else is cheap to regenerate and would just slow every read/write down if\n"
        "# it lived on the mounted filesystem instead.\n"
        "LOCAL_ROOT = '/content/p4'\n"
        "SHARED_LOCAL = f'{LOCAL_ROOT}/shared'      # mirrors the project's shared/ layout exactly\n"
        "SRC_DIR = f'{SHARED_LOCAL}/src'            # so common.py's ROOT-relative INPUTS path,\n"
        "DATA_DIR = f'{SHARED_LOCAL}/data'          # and harness.py's SHARED-relative default,\n"
        "INPUTS_DIR = f'{SHARED_LOCAL}/colab/inputs'  # resolve to this same directory with no\n"
        "                                            # env-var override needed for either.\n"
        "os.environ['HF_HOME'] = '/content/hf'\n"
        "os.environ['USE_TF'] = '0'\n\n"
        "DRIVE_ROOT = '/content/drive/MyDrive/Jev/paper4/colab'\n"
        "ANSWERS_DIR = f'{DRIVE_ROOT}/answers'\n"
        "os.makedirs(SRC_DIR, exist_ok=True)\n"
        "os.makedirs(DATA_DIR, exist_ok=True)\n"
        "os.makedirs(ANSWERS_DIR, exist_ok=True)\n"
        "run_log = {'start': datetime.datetime.utcnow().isoformat() + 'Z', 'models': {}}\n"
        "print('local root:', LOCAL_ROOT)\n"
        "print('answers on Drive:', ANSWERS_DIR)"
    ))

    # ------------------------------------------------------------------ 2. GPU / driver info
    cells.append(code(
        "%%bash\n"
        "nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv\n"
        "python3 -c \"import torch; print('torch', torch.__version__, 'cuda', torch.version.cuda)\" 2>/dev/null || true"
    ))
    cells.append(code(
        "import subprocess\n"
        "gpu_info = subprocess.run(['nvidia-smi', '--query-gpu=name,driver_version', '--format=csv,noheader'],\n"
        "                          capture_output=True, text=True).stdout.strip()\n"
        "run_log['gpu'] = gpu_info\n"
        "print(gpu_info)"
    ))

    # ------------------------------------------------------------------ 3. embedded source files
    cells.append(md("## Write the source files\n\nEmbedded verbatim from the repository at build time (`build_notebook.py`)."))
    for name in SRC_FILES:
        cells.append(writefile_cell(f"{NB_SRC_DIR}/{name}", read_src(name)))
    if have_d3_script:
        cells.append(writefile_cell(f"{NB_SRC_DIR}/{D3_SCRIPT}", read_src(D3_SCRIPT)))

    # ------------------------------------------------------------------ 4. embedded manifest (for the SHA check)
    cells.append(md("## Embedded manifest\n\nThe checked-in `colab/inputs/manifest.json` this notebook must reproduce byte-for-byte per file (SHA-256), built at the same time as the source files above."))
    cells.append(code(
        "EXPECTED_MANIFEST = json.loads(" + repr(manifest_json_literal) + ")\n"
        "print(len(EXPECTED_MANIFEST), 'entries in the embedded manifest')"
    ))

    # ------------------------------------------------------------------ 5. D3 preparation
    cells.append(md("## D3: rebuild the human-labelled social-science tasks"))
    if have_d3_script:
        cells.append(code(
            "%%bash\n"
            "set -e\n"
            "pip install -q requests\n"
            f"python3 {NB_SRC_DIR}/{D3_SCRIPT} --out {NB_DATA_DIR}/d3\n"
        ))
    elif d3_embed is not None:
        cells.append(md(
            "`s00b_prepare_d3.py` was not present when this notebook was built; D3 is restored "
            "from an embedded gzip+base64 copy of `data/d3/*.jsonl` instead (total under 1.5 MB)."
        ))
        cells.append(code(
            "import gzip, base64, os\n"
            f"os.makedirs('{NB_DATA_DIR}/d3', exist_ok=True)\n"
            "_D3_EMBED = " + repr(d3_embed) + "\n"
            "for fn, b64 in _D3_EMBED.items():\n"
            f"    with open(f'{NB_DATA_DIR}/d3/{{fn}}', 'wb') as fh:\n"
            "        fh.write(gzip.decompress(base64.b64decode(b64)))\n"
            "print('wrote', list(_D3_EMBED))"
        ))
    else:
        cells.append(md(
            "**D3 could not be included.** `s00b_prepare_d3.py` was absent when this notebook was "
            "built and `data/d3/*.jsonl` was missing or too large to embed (>= 1.5 MB). The D3 and "
            "E2-D3 conditions will not exist in this run; rebuild the notebook once "
            "`s00b_prepare_d3.py` exists."
        ))

    # ------------------------------------------------------------------ 6. D2 (CLINC) fetch
    clinc_commit = open(CLINC_COMMIT_PATH, encoding="utf-8").read().strip() if os.path.exists(CLINC_COMMIT_PATH) else None
    cells.append(md("## D2: fetch CLINC-150 at the pinned commit"))
    cells.append(code(
        "import os, requests\n"
        f"os.makedirs('{NB_DATA_DIR}/d2', exist_ok=True)\n"
        f"CLINC_COMMIT = {clinc_commit!r}\n"
        "for fn in ('data_full.json', 'domains.json'):\n"
        "    url = f'https://raw.githubusercontent.com/clinc/oos-eval/{CLINC_COMMIT}/data/{fn}'\n"
        "    r = requests.get(url, timeout=60); r.raise_for_status()\n"
        f"    with open(f'{NB_DATA_DIR}/d2/{{fn}}', 'wb') as fh:\n"
        "        fh.write(r.content)\n"
        f"with open('{NB_DATA_DIR}/d2/CLINC_COMMIT', 'w') as fh:\n"
        "    fh.write(CLINC_COMMIT + '\\n')\n"
        "print('fetched CLINC at', CLINC_COMMIT)"
    ))

    # ------------------------------------------------------------------ 7. freeze inputs (deterministic)
    cells.append(md(
        "## Freeze the inputs\n\n"
        "Determinism across machines: `datasets.load_dataset(\"" + D1_REPO + "\", ...)` is pinned "
        "to revision `" + D1_REVISION + "` (the same commit `s00_freeze_inputs.py`'s own "
        "`_sources` manifest entry already names) by a small monkeypatch below, not by editing "
        "s00_freeze_inputs.py itself -- that file also runs on the original workstation, where the "
        "unpinned call already happens to resolve that same revision (it is the dataset's current "
        "HEAD there), so pinning it only here keeps both call sites correct without duplicating "
        "the constant. Output files are written with `newline=\"\\n\"` (s00_freeze_inputs.py's own "
        "`write()`), so line endings cannot differ across OSes either."
    ))
    cells.append(code(
        "%%bash\n"
        "set -e\n"
        "pip install -q datasets huggingface_hub\n"
    ))
    cells.append(code(
        "import sys, os, datasets as _hf_datasets\n"
        "sys.path.insert(0, SRC_DIR)\n"
        "os.chdir(SRC_DIR)\n"
        "os.environ['HF_HOME'] = '/content/hf'\n\n"
        "_orig_load_dataset = _hf_datasets.load_dataset\n"
        f"_D1_REPO, _D1_REVISION = {D1_REPO!r}, {D1_REVISION!r}\n"
        "def _pinned_load_dataset(path, *a, **kw):\n"
        "    if path == _D1_REPO and 'revision' not in kw:\n"
        "        kw['revision'] = _D1_REVISION\n"
        "    return _orig_load_dataset(path, *a, **kw)\n"
        "_hf_datasets.load_dataset = _pinned_load_dataset\n\n"
        "import s00_freeze_inputs\n"
        "s00_freeze_inputs.main()"
    ))

    # ------------------------------------------------------------------ 8. SHA-256 check
    cells.append(md("## Verify every frozen file against the embedded manifest"))
    cells.append(code(
        "import hashlib, json, os\n\n"
        "def _sha256(path):\n"
        "    h = hashlib.sha256()\n"
        "    with open(path, 'rb') as fh:\n"
        "        for chunk in iter(lambda: fh.read(1 << 20), b''):\n"
        "            h.update(chunk)\n"
        "    return h.hexdigest()\n\n"
        "with open(f'{INPUTS_DIR}/manifest.json', encoding='utf-8') as fh:\n"
        "    got_manifest = json.load(fh)\n\n"
        "mismatches = []\n"
        "for cond, meta in EXPECTED_MANIFEST.items():\n"
        "    if cond.startswith('_'):\n"
        "        continue\n"
        "    path = f'{INPUTS_DIR}/' + meta['file']\n"
        "    if not os.path.exists(path):\n"
        "        mismatches.append((cond, 'missing file', None, None))\n"
        "        continue\n"
        "    got = _sha256(path)\n"
        "    if got != meta['sha256']:\n"
        "        mismatches.append((cond, 'sha mismatch', meta['sha256'], got))\n\n"
        "if mismatches:\n"
        "    for cond, why, expect, got in mismatches:\n"
        "        print(f'MISMATCH {cond}: {why} expected={expect} got={got}')\n"
        "    raise SystemExit(f'{len(mismatches)} condition(s) did not reproduce the pinned inputs -- stopping.')\n"
        "print(f'{len(EXPECTED_MANIFEST)} manifest entries verified against freshly frozen files.')"
    ))

    # ------------------------------------------------------------------ 9. per-model runners
    cells.append(md(
        "## Run each model\n\n"
        "Every model cell: build a uv env, smoke-test 5 requests on `d1_neutral` and `d2_k5`, "
        "print a time/compute-unit estimate (assuming **4.8 compute units/hour on an L4** -- a "
        "*stated assumption*, not a measurement), then the full run (every condition at rep 1, "
        "plus a rep-2 retest of `d1_neutral`), writing `answers/<tag>/DONE` on success or "
        "`answers/<tag>/ERROR.txt` with a traceback on failure. GPU memory is freed between models "
        "because each subprocess exits before the next model's cell starts."
    ))

    KEV_GIT = "kev @ git+https://github.com/jaredpalmer/kev@73504e51f6ce2ade19c7819d4a5f2d84363cd40f"
    TORCH_CU128 = ("--extra-index-url https://download.pytorch.org/whl/cu128 "
                   "--index-strategy unsafe-best-match")

    def install_script(env_name, pkgs, optional=()):
        """Bash for one uv env. pkgs are quoted with shlex so any spec is safe; optional
        packages are attempted separately and allowed to fail (speed-only extras)."""
        import shlex
        py = f"/content/envs/{env_name}/bin/python"
        pre = "export UV_CACHE_DIR=/content/uv-cache; "
        lines = [pre + f"uv venv /content/envs/{env_name} --python 3.12 -q --allow-existing",
                 pre + f"uv pip install --python {py} -q {TORCH_CU128} "
                 + " ".join(shlex.quote(p) for p in pkgs)]
        for o in optional:
            lines.append("(" + pre + f"uv pip install --python {py} -q {TORCH_CU128} "
                         + shlex.quote(o) + " || echo 'optional package failed: " + o + "')")
        return "set -e\n" + "\n".join(lines) + "\n"

    def runner_cell(tag, env_name, pkgs, optional=(), extra_env=""):
        script = install_script(env_name, pkgs, optional)
        return code(
            "import subprocess, sys, time, json, os, traceback\n\n"
            f"TAG = {tag!r}\n"
            f"PYBIN = '/content/envs/{env_name}/bin/python'\n"
            f"INSTALL = {script!r}\n"
            "ANS_TAG_DIR = f'{ANSWERS_DIR}/{TAG}'\n"
            "os.makedirs(ANS_TAG_DIR, exist_ok=True)\n"
            "SMOKE_DIR = f'/content/smoke/{TAG}'\n"
            "os.makedirs(SMOKE_DIR, exist_ok=True)\n\n"
            "def run_harness(cond, rep, limit=None, retest=False, answers_dir=None):\n"
            "    env = dict(os.environ)\n"
            "    env['HF_HOME'] = '/content/hf'\n"
            "    env['P4_INPUTS'] = INPUTS_DIR\n"
            "    env['P4_ANSWERS'] = answers_dir or ANS_TAG_DIR\n"
            f"    {extra_env or 'pass'}\n"
            "    cmd = [PYBIN, f'{SRC_DIR}/harness.py', '--model', TAG, '--cond', cond, '--rep', str(rep)]\n"
            "    if limit: cmd += ['--limit', str(limit)]\n"
            "    if retest: cmd += ['--retest']\n"
            "    t0 = time.time()\n"
            "    r = subprocess.run(cmd, cwd=SRC_DIR, env=env, capture_output=True, text=True)\n"
            "    return r, time.time() - t0\n\n"
            "failed = []\n"
            "try:\n"
            "    print(f'=== {TAG}: building env ===', flush=True)\n"
            "    subprocess.run(['bash', '-c', INSTALL], check=True)\n\n"
            "    print(f'=== {TAG}: smoke test (5 requests x 2 conditions) ===', flush=True)\n"
            "    r1, dt1 = run_harness('d1_neutral', 1, limit=5, answers_dir=SMOKE_DIR)\n"
            "    r2, dt2 = run_harness('d2_k5', 1, limit=5, answers_dir=SMOKE_DIR)\n"
            "    print(r1.stdout[-2000:], r1.stderr[-3000:])\n"
            "    print(r2.stdout[-2000:], r2.stderr[-3000:])\n"
            "    if r1.returncode or r2.returncode:\n"
            "        raise RuntimeError(f'{TAG}: smoke test failed (exit {r1.returncode}/{r2.returncode})')\n"
            "    per_req = (dt1 + dt2) / 10.0   # includes model load, so an upper bound\n"
            "    n_all = sum(v['requests'] for k, v in EXPECTED_MANIFEST.items() if not k.startswith('_'))\n"
            "    est_s = per_req * (n_all + 40)\n"
            "    print(f'{TAG}: ~{per_req:.2f}s/request incl. load -> est. full run <= {est_s/60:.0f} min, '\n"
            "          f'~{est_s/3600*4.8:.1f} compute units at 4.8/h on an L4 (assumption)', flush=True)\n"
            "    run_log['models'][TAG] = {'smoke_s_per_request_incl_load': per_req,\n"
            "                              'estimated_full_run_min_upper': est_s / 60}\n\n"
            "    print(f'=== {TAG}: full run ===', flush=True)\n"
            "    for cond in sorted(k for k in EXPECTED_MANIFEST if not k.startswith('_')):\n"
            "        r, dt = run_harness(cond, 1)\n"
            "        print(f'[{TAG}] {cond}: exit {r.returncode}, {dt/60:.1f} min', flush=True)\n"
            "        if r.returncode:\n"
            "            failed.append(cond)\n"
            "            print(r.stdout[-1500:], r.stderr[-3000:])\n"
            "    r, dt = run_harness('d1_neutral', 2, retest=True)\n"
            "    print(f'[{TAG}] retest: exit {r.returncode}', flush=True)\n"
            "    if r.returncode:\n"
            "        failed.append('d1_neutral_retest')\n"
            "        print(r.stdout[-1500:], r.stderr[-3000:])\n"
            "    if failed:\n"
            "        raise RuntimeError(f'{TAG}: conditions failed: {failed}')\n"
            "    with open(f'{ANS_TAG_DIR}/DONE', 'w') as fh:\n"
            "        fh.write(time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()) + '\\n')\n"
            "    print(f'=== {TAG}: DONE ===')\n"
            "except Exception:\n"
            "    tb = traceback.format_exc()\n"
            "    with open(f'{ANS_TAG_DIR}/ERROR.txt', 'w') as fh:\n"
            "        fh.write(tb)\n"
            "    print(f'=== {TAG}: ERROR, continuing with the next model (see ' + ANS_TAG_DIR + '/ERROR.txt) ===')\n"
            "    print(tb)\n"
            "finally:\n"
            "    import gc\n"
            "    gc.collect()\n"
            "    subprocess.run(['nvidia-smi', '--query-gpu=memory.used', '--format=csv,noheader'])"
        )

    BASE = ["torch==2.8.0", "transformers>=5.17,<6", "peft>=0.21", "accelerate>=1.15",
            "huggingface_hub", "python-dotenv", "httpx", "pydantic", "numpy", "scipy"]

    cells.append(md("### laya-en / laya-ml"))
    cells.append(runner_cell("laya-en", "laya", ["torch==2.8.0", "laya==0.3.20", "python-dotenv",
                                                 "httpx", "numpy"]))
    cells.append(runner_cell("laya-ml", "laya", ["torch==2.8.0", "laya==0.3.20", "python-dotenv",
                                                 "httpx", "numpy"]))

    cells.append(md(
        "### kev-0.8b / decider-2b / this-that-1.0\n\n"
        "One shared env. `flash-linear-attention` supplies fast kernels for the Qwen3.5 linear-"
        "attention layers; it is optional, and if it fails to install the models still run, "
        "more slowly."
    ))
    cells.append(runner_cell("kev-0.8b", "kev_decider_tt", BASE + [KEV_GIT],
                             optional=["flash-linear-attention"]))
    cells.append(runner_cell("decider-2b", "kev_decider_tt", BASE + [KEV_GIT],
                             optional=["flash-linear-attention"]))
    cells.append(runner_cell("this-that-1.0", "kev_decider_tt",
                             BASE + [KEV_GIT, f"thisthat @ git+https://github.com/FLock-io/this-that-model@{THISTHAT_SHA}"],
                             optional=["flash-linear-attention"]))

    cells.append(md("### kev-9b / nimble-9b"))
    cells.append(runner_cell("kev-9b", "kev_decider_tt", BASE + [KEV_GIT],
                             optional=["flash-linear-attention"]))
    cells.append(runner_cell("nimble-9b", "nimble",
                             ["torch==2.8.0", "transformers==5.17.0", "peft==0.21.0",
                              "accelerate==1.15.0", "sentencepiece==0.2.2", "pillow==12.3.0",
                              "huggingface_hub>=0.34", "python-dotenv", "httpx", "numpy"],
                             optional=["flash-linear-attention"]))

    cells.append(md(
        "### comparator-open (vLLM, batched, last)\n\n"
        "Runs the comparator's own conditions "
        "(`d1_neutral, d1_calib, d2_k150, d2_k20, d3_conv_go_awry, d3_wiki_corpus, d3_emotion, "
        "d3_wiki_politeness`), not the full manifest, and at rep 1 only (no retest -- greedy, T=0 "
        "decoding is already deterministic)."
    ))
    cells.append(code(
        "import subprocess, sys, time, json, os, traceback\n\n"
        "TAG = 'comparator-open'\n"
        "PYBIN = '/content/envs/vllm_env/bin/python'\n"
        "ANS_TAG_DIR = f'{ANSWERS_DIR}/{TAG}'\n"
        "os.makedirs(ANS_TAG_DIR, exist_ok=True)\n"
        "SMOKE_DIR = f'/content/smoke/{TAG}'\n"
        "os.makedirs(SMOKE_DIR, exist_ok=True)\n"
        "COMPARATOR_CONDS = ['d1_neutral', 'd1_calib', 'd2_k150', 'd2_k20',\n"
        "                    'd3_conv_go_awry', 'd3_wiki_corpus', 'd3_emotion', 'd3_wiki_politeness']\n\n"
        "def run_harness(cond, limit=None, answers_dir=None):\n"
        "    env = dict(os.environ)\n"
        "    env['HF_HOME'] = '/content/hf'\n"
        "    env['P4_INPUTS'] = INPUTS_DIR\n"
        "    env['P4_ANSWERS'] = answers_dir or ANS_TAG_DIR\n"
        "    cmd = [PYBIN, f'{SRC_DIR}/harness.py', '--model', TAG, '--cond', cond, '--rep', '1']\n"
        "    if limit: cmd += ['--limit', str(limit)]\n"
        "    t0 = time.time()\n"
        "    r = subprocess.run(cmd, cwd=SRC_DIR, env=env, capture_output=True, text=True)\n"
        "    return r, time.time() - t0\n\n"
        "try:\n"
        "    print('=== comparator-open: building env ===', flush=True)\n"
        "    subprocess.run(['bash', '-c',\n"
        "        'set -e; UV_CACHE_DIR=/content/uv-cache uv venv /content/envs/vllm_env --python 3.12 -q --allow-existing '\n"
        "        '&& UV_CACHE_DIR=/content/uv-cache uv pip install --python /content/envs/vllm_env/bin/python -q '\n"
        "        'vllm huggingface_hub python-dotenv httpx'], check=True)\n\n"
        "    print('=== comparator-open: smoke test (5 requests x 2 conditions) ===', flush=True)\n"
        "    smoke_conds = ['d1_neutral', 'd2_k20']  # d2_k5 is not a comparator condition; d2_k20 stands in\n"
        "    smoke_t0 = time.time()\n"
        "    rs = [run_harness(c, limit=5, answers_dir=SMOKE_DIR) for c in smoke_conds]\n"
        "    for r, _dt in rs:\n"
        "        print(r.stdout[-2000:], r.stderr[-2000:])\n"
        "        if r.returncode:\n"
        "            raise RuntimeError(f'comparator-open: smoke test failed (exit {r.returncode})')\n"
        "    per_req = sum(dt for _r, dt in rs) / (5 * len(smoke_conds))\n"
        "    n_total = sum(EXPECTED_MANIFEST[c]['requests'] for c in COMPARATOR_CONDS)\n"
        "    est_s = per_req * n_total\n"
        "    est_cu = est_s / 3600 * 4.8\n"
        "    print(f'comparator-open: ~{per_req:.2f}s/request -> est. full run {est_s/60:.1f} min, '\n"
        "         f'~{est_cu:.2f} compute units at 4.8/h on an L4 (assumption)')\n"
        "    run_log['models'][TAG] = {'smoke_s_per_request': per_req, 'estimated_full_run_min': est_s / 60,\n"
        "                              'estimated_compute_units': est_cu}\n\n"
        "    print('=== comparator-open: full run ===', flush=True)\n"
        "    failed = []\n"
        "    for cond in COMPARATOR_CONDS:\n"
        "        r, _dt = run_harness(cond)\n"
        "        print(f'[comparator-open] {cond}: exit {r.returncode}, {_dt/60:.1f} min', flush=True)\n"
        "        if r.returncode:\n"
        "            failed.append(cond)\n"
        "            print(r.stdout[-1500:], r.stderr[-3000:])\n"
        "    if failed:\n"
        "        raise RuntimeError(f'comparator-open: conditions failed: {failed}')\n\n"
        "    with open(f'{ANS_TAG_DIR}/DONE', 'w') as fh:\n"
        "        fh.write(time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()) + '\\n')\n"
        "    print('=== comparator-open: DONE ===')\n"
        "except Exception:\n"
        "    tb = traceback.format_exc()\n"
        "    with open(f'{ANS_TAG_DIR}/ERROR.txt', 'w') as fh:\n"
        "        fh.write(tb)\n"
        "    print('=== comparator-open: ERROR (see ERROR.txt) ===')\n"
        "    print(tb)"
    ))

    # ------------------------------------------------------------------ 10. final wrap-up
    cells.append(md("## Finish: ALL_DONE + run_log.json"))
    cells.append(code(
        "import subprocess, json, datetime, os\n\n"
        "def env_versions(pybin):\n"
        "    try:\n"
        "        out = subprocess.run([pybin, '-c',\n"
        "            \"import json,importlib;\"\n"
        "            \"mods=['torch','transformers','peft','vllm'];\"\n"
        "            \"print(json.dumps({m: getattr(importlib.import_module(m), '__version__', None) \"\n"
        "            \"for m in mods if importlib.util.find_spec(m)}))\"],\n"
        "            capture_output=True, text=True, timeout=60)\n"
        "        return json.loads(out.stdout.strip() or '{}')\n"
        "    except Exception as e:\n"
        "        return {'error': str(e)}\n\n"
        "checked = {}\n"
        "all_tags = ['laya-en', 'laya-ml', 'kev-0.8b', 'decider-2b', 'this-that-1.0',\n"
        "           'kev-9b', 'nimble-9b', 'comparator-open']\n"
        "n_done = n_error = 0\n"
        "for tag in all_tags:\n"
        "    d = f'{ANSWERS_DIR}/{tag}'\n"
        "    done = os.path.exists(f'{d}/DONE')\n"
        "    err = os.path.exists(f'{d}/ERROR.txt')\n"
        "    checked[tag] = 'DONE' if done else ('ERROR' if err else 'MISSING')\n"
        "    n_done += done; n_error += err\n\n"
        "run_log['end'] = datetime.datetime.utcnow().isoformat() + 'Z'\n"
        "run_log['status'] = checked\n"
        "run_log['env_versions'] = {\n"
        "    'laya': env_versions('/content/envs/laya/bin/python'),\n"
        "    'kev_decider_tt': env_versions('/content/envs/kev_decider_tt/bin/python'),\n"
        "    'kev9b': env_versions('/content/envs/kev9b/bin/python'),\n"
        "    'nimble': env_versions('/content/envs/nimble/bin/python'),\n"
        "    'vllm_env': env_versions('/content/envs/vllm_env/bin/python'),\n"
        "}\n"
        "with open(f'{ANSWERS_DIR}/run_log.json', 'w') as fh:\n"
        "    json.dump(run_log, fh, indent=2)\n\n"
        "print(json.dumps(checked, indent=2))\n"
        "if n_error == 0 and n_done == len(all_tags):\n"
        "    with open(f'{ANSWERS_DIR}/ALL_DONE', 'w') as fh:\n"
        "        fh.write(run_log['end'] + '\\n')\n"
        "    print('ALL_DONE written.')\n"
        "else:\n"
        "    print(f'{n_done}/{len(all_tags)} models finished cleanly, {n_error} errored; '\n"
        "         'ALL_DONE NOT written (see run_log.json / each ERROR.txt).')"
    ))

    nb = nbf.v4.new_notebook()
    nb["cells"] = cells
    nb["metadata"] = {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "pygments_lexer": "ipython3"},
        "accelerator": "GPU",
        "colab": {"provenance": [], "gpuType": "L4"},
    }
    nbf.validate(nb)

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as fh:
        nbf.write(nb, fh)
    print(f"wrote {OUT_PATH} ({len(cells)} cells)")

    if check:
        _check(nb)
    return OUT_PATH


def _check(nb):
    """Compile every embedded .py file (the %%writefile cells) to catch a syntax error before it
    reaches Colab."""
    import re
    n_checked = 0
    for cell in nb["cells"]:
        if cell["cell_type"] != "code":
            continue
        src = cell["source"]
        m = re.match(r"%%writefile\s+(\S+)\n", src)
        if not m or not m.group(1).endswith(".py"):
            continue
        body = src[m.end():]
        with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8") as fh:
            fh.write(body)
            tmp_path = fh.name
        try:
            py_compile.compile(tmp_path, doraise=True)
            n_checked += 1
        finally:
            os.unlink(tmp_path)
    print(f"py_compile OK for {n_checked} embedded .py files")


THISTHAT_SHA = "542d445efa5f68b14bfbd1f8ed25aacd8379d839"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="also validate + py_compile the result")
    a = ap.parse_args()
    build(check=a.check)


if __name__ == "__main__":
    main()
