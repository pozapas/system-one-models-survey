# azizi2026labels — Labels Override Definitions in Jev-Style Typed Decision Models

arXiv:2610.02586v1 [cs.AI], 01 Oct 2026. HTML from https://arxiv.org/html/2610.02586 (fulltext/2610.02586.html and .txt).

## Authors and affiliation
Seyedarmin Azizi (corresponding), Erfan Baghaei Potraghloo, Massoud Pedram; University of Southern California, USA (front matter). Affiliation type: academic.

## Task and data
Tests whether the probability a typed decision model returns follows the written option definitions or the option labels ("option-label bias"). Two suites. (1) Natural classification: eleven public tasks (SST-2, RTE, CB as fixed-label choice, n = 500/277/56, pooled n = 833; seven yes/no tasks BoolQ, WiC, yes/no SST-2 and RTE, three UNFAIR-ToS clause types; ordinal SST-5) (§4.2, App. B Table 13). (2) PolicyBench, a synthetic templated support-ticket routing suite introduced here, in which the rule is stated only in the option definition and the correct answer is computed from generating attributes; headline suite is PolicyBench-XF (explicit false branch); n = 3500 for typed heads, n = 2100 for the Qwen readouts (§4.3, §5.2, §5.3). The authors state that a first, uncontrolled PolicyBench version produced an artifact and report the controlled XF suite throughout (§5.2.1).

## Decision models evaluated
Open-weight Jev-interface implementations only; Jev itself is not measured ("We do not measure Jev itself", §1 Scope, §7). laya-typed-decisions (421M, "laya-td"), laya (421M, "laya-en"), laya-multilingual (322M, "laya-ml"), all ModernBERT-based, Apache-2.0, and von (395M, ModernBERT-based) (§2.4). Language-model readouts for comparison: Qwen2.5 0.5B/1.5B/7B, Llama-3.1-8B-Instruct, Mistral-7B-Instruct-v0.3, read three ways (length-normalised label log-probability, first-token, generate-then-parse) (§2.3, §4.4). No checkpoint revision hashes or evaluation dates are given; only short names and parameter counts (version pin: not reported beyond that).

## Comparators, tuning-budget parity
No tuning of any system. All systems receive the same requests (same rewritten variants, same items, paired bootstrap); LM readouts use a fixed prompt rendering. Mitigation M3 adds an instruction sentence (§6). Parity is therefore same prompt for all systems.

## Reference labels
Natural tasks: the public benchmarks' gold labels (source and annotation process not described in the paper; coded human_adjudicated in the ledger as a benchmark gold standard, an assumption flagged here). PolicyBench: synthetic, ground truth computed from generating attributes, classes exactly balanced (§4.3) (reference_label_type synthetic).

## n, sampling design, intervals
Per-task item counts and class prevalence in Table 13 (UNFAIR-ToS balanced before use). Percentile bootstrap over items, 4,000 resamples, paired when comparing conditions on the same items (§4.5). Headline contrasts carry 95% intervals. No seeds (inference only, deterministic readouts).

## Test-data exposure
SST-2, RTE, CB, BoolQ, WiC, UNFAIR-ToS, SST-5 are public pre-2026 benchmarks; no contamination check reported for them. PolicyBench is newly generated ("immunity to contamination", §7).

## Cost and latency
Not measured ("We did not measure latency or cost", §5.7). No hardware reported.

## Calibration / confidence
No calibration analysis (no ECE or temperature scaling). Confidence-score AUROC for ranking correct versus incorrect answers is reported: laya-td 0.8123 under aligned labels, 0.2433 under misleading labels (Table 6, §5.8). Null-state prior correction (contextual calibration, Eq. 6) evaluated as mitigation M2 (Table 7).

## Cascade
No cascade experiment. The authors argue that confidence-gated escalation fails under label/definition conflict because the AUROC falls below 0.5 (§5.8).

## Robustness findings
Option label ablations, both-direction patch of the rendering expression (laya removes label: contrast +0.0000; von with label added: accuracy 0.8511 to 0.2281 when label contradicts definition) (§5.5, Table 5); negated yes/no questions flip decisions on 0.9656-0.9825 of items for typed heads (§5.7, Table 10); two-call test and four mitigations (§5.6, §6).

## Code and data availability
"Code, the PolicyBench generator, and the raw per-item model outputs for every grid cell are released" (Reproducibility statement); no URL in the text read. Coded `partial` (released, URL not given in the HTML text).

## Paper's own limitations (§7)
Jev not measured; PolicyBench synthetic and templated; misleading condition arguably under-specified; definitions are the authors' wording; laya-multilingual near chance on PolicyBench so no conclusion drawn.

## Notes for the grader
Synthetic ground truth for the headline suite. No version pin or run date for evaluated checkpoints. Uncontrolled first-version PolicyBench artifact disclosed and corrected.
