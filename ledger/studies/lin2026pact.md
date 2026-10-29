# lin2026pact — PACT: Pairwise-Anchored Calibrated Tuning for Single-Token Typed Decisions

arXiv:2609.35865v1 [cs.CL], 26 Sep 2026 (header). HTML retrieved 2026-10-28 from https://arxiv.org/html/2609.35865; saved as fulltext/2609.35865.html and .txt. The batch file lists the published date as 2026-09-26.

## Authors and affiliation

Yida Lin, Victoria University of Wellington, Wellington, New Zealand (title block). Affiliation type: academic. Single author.

## Task and data

A training objective for single-token typed-decision models, built on the open Nimble recipe (Bespoke Labs, Bespoke-Nimble-9B): the model reads the logits of one-letter answer codes at one position and normalises over them (§I, §III-A). Fields are Choice, Boolean or Score (C between 2 and 6 on the holdout) (§III-A, §V-A). Training file: 2,676 records, 1,338 contrastive pairs, 34 source families, 10 domains; splits disjoint at family level: training 2,334 records, selection 116, calibration 226, frozen holdout 324 records (162 pairs, 6 source families, 6 domains), used only for final numbers (§V-A, Table I).

## Decision models evaluated

Qwen3.5-9B base at the revision pinned by the published Nimble recipe, BF16, 2,048-token limit; LoRA rank 16 (alpha 32, dropout 0.05), rsLoRA, LoRA+ ratio 8 (§V-B). Runs (Table II): Base model (adapter off, no seeds); Nimble recipe reproduced in the authors' harness (CE, 1 epoch, linear schedule, plain LoRA; seeds 17/18/19); CE-only (same optimiser as PACT, cross-entropy only; 3 seeds); PACT (4 terms plus contextual temperature; 3 seeds); leave-one-out ablations (1 seed each, seed 17). The exact Qwen revision hash is not stated in the text; no Jev, Laya, or hosted model is evaluated.

## Comparators and tuning-budget parity

The three arms share data, prompt, adapter family and checkpoint selection (selection split NLL every 146 steps). Optimiser differs between the published recipe (Opt. A) and PACT/CE-only (Opt. B); the CE-only control isolates the objective, and Nimble vs CE-only isolates the optimiser (§V-C). Loss weights (0.5, 0.5, 0.2, 0.3) "chosen for scale comparability and not tuned on any evaluation data" (§IV-G). Hypotheses H1 to H5 were pre-specified (§V-E). Selection noise acknowledged (Fig. 10, §VII).

## Reference labels

Holdout is "324 synthetic, model-labelled items ... its labels come from the same family of models as the training labels" (§VIII). Reference type: synthetic.

## n, sampling, intervals

n = 324 items, 162 pairs on the frozen holdout, three seeds; metrics are mean and s.d. over seeds (Table III). Paired exact McNemar tests and 10,000-resample paired bootstrap CI per seed (Table IV, §V-D). Ablations are single-seed, "read colours as directions, not as significance" (Table VI).

## Test-set exposure

The training file is described as "released" (Nimble data); whether the six holdout families were public before the model's training is not discussed. The base model Qwen3.5-9B may have seen related text; no contamination check. Treat as unclear.

## Cost and latency

Training cost (Table VIII): wall-clock per run 1.37 h PACT, 0.50 h CE-only, 0.26 h Nimble recipe; peak GPU memory 28.8, 21.8, 21.8 GiB; one 48 GB GPU per job (two 48 GB GPUs). "Serving cost is unchanged" (§VII); no inference latency is reported. A local 4-bit evaluation is used for the base model and K sweep (Table IV note, §VI-B).

## Calibration

NLL, multiclass Brier, ECE with 15 equal-width bins, AURC (§V-D). Contextual temperature T(x) = softplus(a + b log C + c log(L/1000)) fitted by L-BFGS on a 226-record calibration split (§IV-F). ECE lower after T(x) in all nine multi-seed runs: PACT 10.8 to 7.9, Nimble recipe 9.5 to 5.4, CE-only 14.3 to 10.3 (§VI-C, Table III). Caveats: slopes unstable across runs (log C slope from -1.60 to +2.73), calibration-split ECE unchanged (5.5 to 5.7), AURC worsens (3.95 to 4.21) (§VI-C).

## Cascade or escalation

None. Risk-coverage curves and AURC are reported (Fig. 5b); no escalation to another model.

## Option-name, cardinality, language and robustness tests

Answer-code position bias is a core test: K=4 relabelling ensemble, TV and flip rate (Table V, §VI-B). Cardinality: C from 2 to 6 (§V-A). Per-kind and per-domain accuracy differences (Fig. 8, §VI-E). English not stated; no language test.

## Code and data availability

Code, data splits, trained adapters and run records at https://github.com/BennyLinntu/PACT-Pairwise-Anchored-Calibrated-Tuning-for-Single-Token-Typed-Decisions (Abstract).

## Limitations stated by the authors

Narrow 324-item synthetic, model-labelled holdout from six families; shared errors with training labels undetectable; certificate trust; single-seed ablations; loss weights not tuned; one base model, one scale, one adapter rank (§VIII).
