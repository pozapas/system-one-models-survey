# yang2026graphdecisionbench — GraphDecisionBench: Benchmarking System One Models on Graph Tasks

arXiv:2610.06354, first submitted 2026-10-05 (batch CSV). No HTML version exists for this paper ("HTML is not available for the source"), so the PDF (fulltext/2610.06354.pdf, 888,297 bytes) was downloaded and converted with pdftotext -layout to fulltext/2610.06354.txt. The arXiv abs page lists v1 to v3 (checked 2026-10-28); the PDF fetched at that date is the then-current version, presumed v3. Several figures and tables (Fig. 2 heatmap, Table 2 matrix, Fig. 3) extract as scrambled text, so only values stated in prose were used.

## Authors and affiliation
Xianliang Yang (Microsoft), Yapu Zhang (Beijing University of Technology), Li Zhao (Microsoft) (front matter). Affiliation type: mixed (industry and academic).

## Task and data
Benchmark with three task families (§3.1). RQ1 graph cognition: six query tasks (adjacency, exact degree, cycle existence, pairwise connectivity, distance thresholds, articulation points) on induced subgraphs of 8 to 12 vertices from Facebook, ca-GrQc, Power Grid and Human PPI; 800 queries (400 degree, 80 for each other task), 200 per source; references by independent graph algorithms. RQ2 graph-text decisions: 40-class ogbn-arxiv node classification (100 test targets per condition) and STaRK-Prime biomedical entity selection from 40 candidates (100 test queries per condition, any native correct answer accepted); five matched input conditions T, G, TG, BAG, A or A*; a separate 200-target ogbn-arxiv cohort in appendices. RQ3 sequential decisions: TSP (TSPLIB EUC_2D, 76 to 225 cities, proven optima), signed MaxCut (OPTSICOM Set2, 125 vertices, historical best-known values), deterministic LT influence maximisation (SNAP email-Eu-core subgraphs, exhaustive optima), binary modularity (ca-GrQc subgraphs, MILP-certified optima); ten instances per task, two construction modes (direct vs heuristic-proposal selection), 80 trajectory units per configuration (§3.1, 3.2).

## Decision models evaluated
Fourteen model-interface configurations (§4.1, App. B.1 Table B.1): Jev-1.13.0 (provider typesafe, served model jev-1.13.0), Decider-2B v11 (Mapika/decider-2b), Kev-4B (jaredpalmer/kev-4b), Laya (convaiinnovations/laya-typed-decisions) as native choice-based models; Qwen3.5-0.8B/2B/4B/9B/27B, Qwen3.8-27B, Qwen2.5-72B-Instruct (no-thinking generation via vLLM), Qwen3.5-4B candidate-token scoring, GPT-5.4 (reasoning none) and GPT-6-Astra (medium reasoning observed in metadata) as comparators. The Jev blog is cited with access date 2026-10-01; no per-run dates. Temperature, seed and related sampling parameters for GPT models are unset (provider defaults).

## Comparators, tuning-budget parity
Common task data and prompt-construction rules via model adapters; settings per configuration in Table B.1; unsupported interfaces recorded as unsupported (not zero). Heuristic-proposal mode supplies candidate actions, numerical features and rule identities together, so its benefit cannot be attributed to a single factor; comparison with classical and fixed-rule controls (§4.4). No fine-tuning; no tuning on test data described.

## Reference labels
RQ1: algorithmically computed ground truth (task_outcome-like, deterministic); RQ2: ogbn-arxiv official class labels and STaRK-Prime native correct answers (dataset labels); RQ3: proven or best-known optima (task_outcome). Ledger codes administrative_field for RQ2 and task_outcome for RQ1 and RQ3.

## n, sampling, intervals
800 queries (RQ1); 100 targets or queries per condition (RQ2) with paired 95% bootstrap intervals that preserve the pairing of conditions; ten graphs per task (RQ3). Intervals are pointwise and unadjusted for multiple comparisons; single executions per unit, so no estimate of within-instance stochastic variation (§5.2). Point estimates in Fig. 2 and Table 2 are mostly heatmap or matrix cells.

## Test-data exposure
Public datasets (Facebook, ca-GrQc, ogbn-arxiv, STaRK-Prime, TSPLIB, OPTSICOM, SNAP) all pre-2026; no contamination check reported. Held-out classification labels are excluded from training-label anchors (§3.3).

## Cost, latency, hardware
Not measured ("the benchmark assesses decision quality, not a general efficiency advantage", §3). GPU candidate-scoring implementation in App. F.1 (not extracted).

## Calibration
No calibration analysis (probabilities not evaluated; only choices).

## Cascade
None. Heuristic-proposal selection is a candidate-pool control, not a model cascade.

## Robustness
Matched input conditions (T, G, TG, BAG, A or A*) are a controlled contrast on information use. No option-name or order permutation; candidate set sizes vary by task (40 classes, 40 candidates, many-option TSP).

## Code and data
Code and aggregate results at https://github.com/VictorYXL/GraphDecisionBench (Abstract).

## Paper's own limitations (§5.2)
Limited public instances, small graph-cognition inputs and specific construction tasks; shared context and label anchors induce dependence between targets in ogbn-arxiv; STaRK-Prime evaluates selection within answer-containing candidate pools, not end-to-end retrieval; comparisons concern model-interface configurations and do not isolate architecture, scale or reasoning; proposal assistance changes several things at once; classical controls may revise solutions; single executions; pointwise unadjusted intervals.

## Notes for the grader
Jev-1.13.0 is pinned by served model name but there is no run date. Many headline numbers sit in figures; the ledger uses only values stated in text.
