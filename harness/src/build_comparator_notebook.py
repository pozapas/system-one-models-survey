"""Build colab/run_comparator.ipynb: the generative comparator alone, as a second Colab run.

The first Colab run (2026-09-24) finished every decision model but the comparator cell failed
at its smoke test, and the cell captured the subprocess output, so the cause was not kept. This
notebook reuses the setup and input-verification cells of run_open.ipynb unchanged (built from
the same sources by build_notebook.build), replaces the model cells with one comparator cell,
and streams every line of the comparator's output live to the cell and to a log file on Drive,
so any failure is visible and recoverable.

Usage: python build_comparator_notebook.py
"""
import json
import os

import nbformat as nbf

import build_notebook as B

OUT = os.path.join(os.path.dirname(B.OUT_PATH), "run_comparator.ipynb")

COMPARATOR_CELL = r'''import subprocess, sys, time, os, traceback
TAG = 'comparator-open'
PYBIN = '/content/envs/vllm_env/bin/python'
ANS_TAG_DIR = f'{ANSWERS_DIR}/{TAG}'
os.makedirs(ANS_TAG_DIR, exist_ok=True)
LOG = f'{ANS_TAG_DIR}/comparator_log.txt'
CONDS = ['d1_neutral', 'd1_calib', 'd2_k150', 'd2_k20',
         'd3_conv_go_awry', 'd3_wiki_corpus', 'd3_emotion', 'd3_wiki_politeness']

def stream(cmd, env=None):
    """Run a command, echoing every output line to the cell and appending it to the Drive log."""
    with open(LOG, 'a', encoding='utf-8') as log:
        log.write(f'\n$ {" ".join(cmd)}\n'); log.flush()
        p = subprocess.Popen(cmd, cwd=SRC_DIR, env=env, stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT, text=True, bufsize=1)
        for line in p.stdout:
            print(line, end='', flush=True)
            log.write(line); log.flush()
        return p.wait()

def harness_env():
    env = dict(os.environ)
    env['HF_HOME'] = '/content/hf'
    env['P4_INPUTS'] = INPUTS_DIR
    env['P4_ANSWERS'] = ANS_TAG_DIR
    env['VLLM_LOGGING_LEVEL'] = 'INFO'
    # FlashInfer JIT-compiles kernels with ninja, which lives in the env's bin folder;
    # greedy decoding does not need the FlashInfer sampler, so it is switched off as well
    env['PATH'] = '/content/envs/vllm_env/bin:' + env.get('PATH', '')
    env['VLLM_USE_FLASHINFER_SAMPLER'] = '0'
    return env

if os.path.exists(f'{ANS_TAG_DIR}/ERROR.txt'):
    os.replace(f'{ANS_TAG_DIR}/ERROR.txt', f'{ANS_TAG_DIR}/ERROR_first_run.txt')
failed = []
try:
    print('=== comparator-open: building env ===', flush=True)
    rc = stream(['bash', '-c',
                 'set -e; export UV_CACHE_DIR=/content/uv-cache; '
                 'uv venv /content/envs/vllm_env --python 3.12 -q --allow-existing; '
                 'uv pip install --python /content/envs/vllm_env/bin/python -q '
                 'vllm huggingface_hub python-dotenv httpx numpy ninja; '
                 '/content/envs/vllm_env/bin/python -c "import vllm, torch; '
                 'print(\'vllm\', vllm.__version__, \'torch\', torch.__version__)"'])
    if rc:
        raise RuntimeError(f'env build failed (exit {rc})')
    print('=== comparator-open: smoke test, 5 requests of d2_k20 ===', flush=True)
    env = harness_env()
    env['P4_ANSWERS'] = '/content/smoke/comparator-open'
    rc = stream([PYBIN, f'{SRC_DIR}/harness.py', '--model', TAG, '--cond', 'd2_k20',
                 '--rep', '1', '--limit', '5'], env=env)
    if rc:
        raise RuntimeError(f'smoke test failed (exit {rc}); see {LOG}')
    print('=== comparator-open: full run (one process, model loaded once) ===', flush=True)
    t0 = time.time()
    rc = stream([PYBIN, f'{SRC_DIR}/harness.py', '--model', TAG, '--cond', ','.join(CONDS),
                 '--rep', '1'], env=harness_env())
    print(f'full run exit {rc}, {(time.time() - t0) / 60:.1f} min', flush=True)
    if rc:
        raise RuntimeError(f'full run failed (exit {rc}); see {LOG}')
    with open(f'{ANS_TAG_DIR}/DONE', 'w') as fh:
        fh.write(time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()) + '\n')
    with open(f'{ANSWERS_DIR}/COMPARATOR_DONE', 'w') as fh:
        fh.write(time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()) + '\n')
    print('=== comparator-open: DONE ===')
except Exception:
    tb = traceback.format_exc()
    with open(f'{ANS_TAG_DIR}/ERROR.txt', 'w') as fh:
        fh.write(tb)
    print('=== comparator-open: ERROR; the full log is in ' + LOG + ' ===')
    print(tb)
'''

INTRO = (
    "# Paper 4: generative comparator only (second Colab run)\n\n"
    "Open on an **L4** runtime and choose Runtime, then Run all. It mounts Drive, rebuilds and "
    "verifies the frozen inputs exactly as the first notebook did, then runs the open generative "
    "comparator (Qwen3-14B-AWQ through vLLM) on its eight conditions. Every output line is also "
    "written to `My Drive/Jev/paper4/colab/answers/comparator-open/comparator_log.txt`. The "
    "decision-model answers from the first run are not touched. Expected time is well under "
    "an hour; answers are written line by line, so a rerun resumes."
)


def main():
    B.build(check=True)                       # refresh run_open.ipynb with the current sources
    nb = nbf.read(B.OUT_PATH, as_version=4)
    cells = nb["cells"]
    cut = next(i for i, c in enumerate(cells)
               if c["cell_type"] == "markdown" and c["source"].startswith("## Run each model"))
    keep = [c for c in cells[1:cut]]
    out = nbf.v4.new_notebook()
    out["cells"] = ([nbf.v4.new_markdown_cell(INTRO)] + keep +
                    [nbf.v4.new_markdown_cell("## Comparator"),
                     nbf.v4.new_code_cell(COMPARATOR_CELL)])
    out["metadata"] = nb["metadata"]
    nbf.validate(out)
    with open(OUT, "w", encoding="utf-8") as fh:
        nbf.write(out, fh)
    print(f"wrote {OUT} ({len(out['cells'])} cells)")


if __name__ == "__main__":
    main()
