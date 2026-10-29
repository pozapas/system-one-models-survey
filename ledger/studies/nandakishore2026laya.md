# nandakishore2026laya — Laya as a Typed Probabilistic Assessor: An Independent Reproduction and a Preregistered Study of Calibration and Selective Escalation

arXiv:2609.33843v1 [cs.AI], 27 Sep 2026 (header; "September 2026"). HTML retrieved 2026-10-28 from https://arxiv.org/html/2609.33843; saved as fulltext/2609.33843.html and .txt. Ancillary files (per-decision predictions, run manifests, frozen preregistration) are on arXiv and were not downloaded.

## Authors and affiliation

Gowthamkumar Nandakishore, no institution given; "The author has no affiliation with the model's publisher, the dataset's publisher, or TypeSafe" (Abstract, §13). Affiliation type: independent.

## Task and data

Typed Decisions benchmark (LocalLLaMA/typed-decisions, dataset revision f7a2487e, accessed 2026-09-26): four synthetic workflow subsets (agent_trace_observability, customer_service, invoice_processing, security_incidents), 300 train and 100 test cases each, five typed questions per case (choice, noul, score) over one shared state: 6,000 train and 2,000 test decisions (§3.2). Primary evaluation: full official test split (400 cases, 2,000 decisions; 600 noul, 600 choice, 800 score). Track A (released checkpoint): test split halved at case level into calib (200 cases, 1,000 decisions) and eval (200 cases, 1,000 decisions), seed 20260926. Track B (clean replication): re-train from the pinned base on 960 fine-tune / 240 validation cases, test split used once (§3.3). Exploratory OOD probe (E10): 24 fictional documents and 120 typed claims, 60 supported / 60 not (§9.1). Preregistered external set (E9) descoped.

## Decision models evaluated

- Laya Typed-Decisions released checkpoint (421M, ModernBERT-large), HF model card revision 1a793eb5 (accessed 2026-09-26), laya package 0.3.20 predict_batch, F16 weights under bf16 autocast on MPS; as shipped with the inherited per-option-count temperature table (§1, §3.1, §4). Run manifest 20260926T120855Z.
- Track B replication (own re-training with the card's RLCD recipe); ModernBERT-base specialist trained by the author; laya base (zero-shot); laya-multilingual (mmBERT-base, 322M); trivial baselines (majority, training prior, uniform) (§3.4).
- Third-party context only (not run): TypeSafe JEV 1.13.0 measured by the dataset card's maintainers via the public API on 2026-09-18 (all 400 test cases): accuracy 0.727, soft accuracy 0.580, Brier 0.148, ECE 0.144, score MAE 0.391, p50 latency 710 ms/case; meraGPT Decider 1 at 0.768 accuracy (dataset card measurement dated 2026-09-22) (§3.4). "We run nothing against JEV."

## Comparators and tuning-budget parity

No strong judge or generative LLM was run (author-directed constraint in the frozen plan), so cascade end-to-end accuracy is an oracle-escalation bound with symbolic escalation target cost (§3.4, §7). Comparators are grouped as specialists, zero-shot generalists, trivial baselines and reference rows and never ranked as interchangeable. The ModernBERT-base specialist receives the Track B recipe, but the dataset card's own base specialist row (0.646) used a different training method, flagged by the author (§5).

## Reference labels

Gold is the mean of three samples from a roughly 4B-class teacher endpoint at temperature 0.7 (dataset card) with a label_agreement field; "Every number in this paper measures teacher agreement on synthetic cases" (§3.2). Teacher self-agreement ceiling 0.735 (card) with recomputed bracket 0.594 floor to 0.865 estimate (Table 3). Reference type: llm_teacher. The released checkpoint exceeds the ceiling (0.767 vs 0.735).

## n, sampling, intervals

All CIs are case-level cluster bootstrap (resample 400 cases, keep five decisions per case), n_boot 10,000, seed 0; BCa primary for single metrics, percentile for paired differences; add-one bootstrap p-values; Benjamini-Hochberg FDR q=0.05 over a frozen 24-test family (20 of 22 executed reject; two not executed) (§3.6). Preregistration frozen 2026-09-26 15:50 UTC; E1 reproduction was retrospective, E2 to E8 prospective; one acceptance-gate timing item recorded as a disclosed failure (§3.7).

## Test-set exposure

The test split of a September 2026 benchmark; the released checkpoint was fine-tuned on all 1,200 training cases, so any calibration fitted on training data is contaminated. Track A's calib half is carved from the official test split as mitigation (Limitation 8). Post-freeze test exposure is enumerated in §3.7.

## Cost and latency

Apple M5 Max (64 GB, mps), laya 0.3.20, batch size 1, max sequence length 1024: per-case p50/p90/p99 95.9/124.1/195.4 ms (five decisions per case), p50 per decision 19.2 ms, 54.3 decisions/s; amortised cost about 18.4 ms per decision; batching does not help on this MPS path (51.9/42.9/37.8/38.7 decisions/s at batch 1/8/32/64) (§4.4, §7). The card's T4 figures are on different hardware. No dollar cost.

## Calibration

ECE with 10 (card convention), 15, 20 equal-width bins and equal-mass bins; classwise ECE; signed confidence-accuracy gap; NLL, Brier, RPS (§3.5). Released checkpoint signed gap -0.2142 (mean confidence 0.553 vs accuracy 0.767); every occupied bin is under-confident, so every binned ECE variant equals 0.21423 (§4.2). Six calibration methods fitted on calib only (Table 4): single temperature T=0.469 takes held-out ECE15 from 0.2035 to 0.0372 and NLL from 0.7027 to 0.5364; the frozen selection rule picked isotonic regression, which overfit (held-out NLL 0.7738 [0.626, 1.030], worse than identity), so H2 is not supported (§6).

## Cascade or escalation

Confidence-gated escalation from Laya to a symbolic stronger model, threshold tau chosen on calib (tau* = 0.70, accepted error 0.0916 on calib). On eval: coverage 0.672 [0.637, 0.704], accepted-set accuracy 0.8601 [0.831, 0.886], oracle-bounded end-to-end accuracy 0.906, escalation rate 0.328, accepted error 0.1399 vs frozen 0.10 target (H3a fails); confidence beats random escalation at matched rate by +0.0646 [0.0502, 0.0785] (§7). Track B: tau 0.75, accepted error 0.0866 on validation, 0.1028 on test; beats random by +0.0757 [0.0661, 0.0851] (§8.1). Case-level gating collapses to coverage 0.055.

## Option-name, cardinality, language and robustness tests

Option-order permutations (four seeds, 300 choice decisions x 4 runs): 6.75% of predictions flip; accuracy 0.727 to 0.763 vs 0.747 original (§8). Surface perturbations (lowercase/punctuation strip, neutral prefix) flip 1.7% and 1.4%. Dropping a load-bearing state field changes 49% to 66% of predictions and lowers mean confidence. Cardinality: benchmark choice questions have at most 5 options; the shipped temperature table's choice:11+ entry is never used (§4.3). English only; no language test. Paraphrase test substituted by surface transforms (deviation D2).

## Code and data availability

Per-decision predictions, run manifests, metric code with unit tests and the frozen preregistration released as arXiv ancillary files (Abstract, §4.5, Appendix B). Code: partial (ancillary files; no external repository URL found in the text).

## Limitations stated by the authors

Single checkpoint; synthetic teacher-labelled benchmark; no compute-matched comparison; no TypeSafe JEV access; external-validity set descoped; no independent annotators; single hardware; Track A fitting data contaminated; small fitting and evaluation splits (n=200); soft accuracy did not reproduce (0.509 vs 0.471) (§11).
