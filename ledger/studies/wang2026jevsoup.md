# Wang, Cheng, Li, Cheng, Deng, Bai & Li (2026), "JevSoup: System-One Routing for Training-Free LoRA Composition"

## Identification
- arXiv 2609.30922v1 [cs.AI], 25 Sep 2026 (header). License arXiv perpetual non-exclusive. Full text fulltext/2609.30922.html and .txt.
- Authors Xiuying Wang, Jiahua Cheng, Shuotian Li, Yufan Cheng, Bowen Deng, Zhexuan Bai, Yichen Li; affiliations Beijing University of Posts and Telecommunications, University of Malaya, Georgian College, Huazhong University of Science and Technology (address block). affiliation_type = academic. No funding; no competing interests (Acknowledgment).

## Task and data
- Training-free LoRA expert composition: Jev selects an ordered Top-2 pair of LoRA experts from the input and description-only expert cards (typed choice over expert identifiers); the second LoRA update is orthogonally projected against the row space of the first, then the two are combined with equal weights (Section 2).
- Evaluation: PorTAL benchmark (portallib 0.2.0), 14 tasks, 19,477 multiple-choice examples from the released validation split with development prompts excluded; task-macro and sample-micro accuracy; Qwen3-1.7B, 4B and 8B backbones with 14 frozen rank-8 LoRA experts each (Section 3.1). Gold answers and task labels are unavailable to routing.

## Decision model
- Jev jev-1.13.0 (footnote to docs.typesafe.ai/models), card ordering fixed by seed 42. Used only as a router; decision made once per input and shared across matrices and candidates. No run dates; blog and docs accessed 2026-09-23.

## Comparators and tuning parity
- Base, Adaptive Minds (AM; LLM-based router on the unadapted Qwen3 backbone with keyword fallback, equal weights), LoGo, AdapterSoup (retrieval with Qwen3-Embedding-0.6B and 100 training examples per expert), Arrow. All routing methods Top-2, same backbone, expert library and scoring protocol; "task adaptations, not replications of the original absolute scores" (Section 3.1). AdapterSoup uses 100 training examples per expert, so comparators are not all training-free (asymmetry favouring neither side clearly). No tuning on test stated, but lambda chosen at 1 and results reported on the same evaluation examples used for ablation and sensitivity.

## Reference labels
- PorTAL gold answers for multiple-choice items (task outcome).

## n, sampling, intervals
- 19,477 examples, single run per configuration (model seed 42). No confidence intervals or significance tests; Random Top-2 reports mean ± SD over three routing seeds (72.43 ± 0.34 macro, 71.77 ± 0.16 micro; Table 2). Gains over baselines are small (0.21 to 1.19 points) relative to no reported uncertainty.

## Key results
- Table 1 (macro / micro): Qwen3-1.7B JevSoup 70.91 / 67.40, AM 69.79 / 67.15, Base 58.05 / 61.79; Qwen3-4B JevSoup 75.30 / 73.81, AM 74.11 / 72.49, AdapterSoup 73.61 / 72.60, Base 64.05 / 69.76; Qwen3-8B JevSoup 77.29 / 78.73, AM 77.07 / 78.54, Base 68.15 / 74.41.
- Ablation (4B, Table 2): Jev Top-2 equal-weight no projection 74.64 / 73.49 vs Random Top-2 72.43 / 71.77 vs AM Top-2 74.11 / 72.49 vs Jev Top-1 73.24 / 71.83; JevSoup 75.30 / 73.81. Projection strength sweep 75.01 to 75.34 macro (Section 3.4).

## Calibration
- Not evaluated. Routing probabilities used for ordering; probability weighting underperforms equal weights (Table 2).

## Cost and latency
- Not reported. No Jev latency or price figures.

## Cascade, option-name, cardinality, robustness
- Card ordering fixed by seed; Random routing seeds 42 to 44; 14 expert options. No option-order or language tests beyond that.

## Test-set exposure
- Public PorTAL validation split; development prompts excluded; no contamination check. Qwen3 backbones' exposure unknown.

## Code and data
- https://github.com/Leowang980/JevSoup (abstract).

## Paper's own limitations
- No dedicated limitations section. Conclusion claims highest accuracy "among the evaluated methods" and "completed results" only; PorTAL only; Top-2 only.
