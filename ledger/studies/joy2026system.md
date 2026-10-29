# Joy (2026), "Do System One Decisions Add Up? A Study of Probabilistic Coherence"

## Identification
- arXiv 2609.33971v1 [cs.CL], 27 Sep 2026 (header). License CC BY 4.0.
- Single author Saman Sarker Joy, "Faculty of Computer Science and Information Technology, Universiti Malaya, Kuala Lumpur, Malaysia" (byline). affiliation_type = academic.
- Code and recorded results: https://github.com/samanjoy2/system-one-coherence (Introduction, footnote 1). API reproduction "remains subject to request variability" (Appendix C).

## Task and data
- Hierarchical (two-level) closed-set text classification, used to test probabilistic coherence between a direct fine-label question, a broad-category question, and conditional fine-label questions per parent (Section 3). Three datasets (Table 1): TREC question classification, all 500 test items, 6 parents, 50 fine labels; CLINC150 in-scope test, 1,000 items (6 or 7 per intent), 10 domains, 150 intents; MASSIVE en-US test, 1,000 items, 18 scenarios, 60 intents. Sampling seed 42 (Section 4.2). 2,500 matched inputs per system, 5,000 model-example records, 72,000 classification questions (36,000 per system) (Section 4.1).
- Gold labels are the datasets' own annotations (TREC annotated class labels, CLINC150 and MASSIVE crowd-collected intent annotations); ledger codes TREC as human_adjudicated and CLINC150, MASSIVE as human_crowd (the paper does not describe label provenance). All public, released before 2026; "Training exposure is unknown" (Section 8), no contamination check.
- Out-of-scope CLINC150 items excluded to keep a closed-set partition (Section 4.2). Label text: raw descriptions only, no demonstrations; TREC fine labels use unexpanded suffixes such as "Entity: cremat", a stated label-interpretability limitation (Section 4.2).

## Models evaluated
- Jev `jev-1.13.0` through the TypeSafe API, native categorical Choice interface, probabilities recorded to 2 decimals, precision and training undisclosed (Table 2, Section 4.3). Run dates not stated beyond "Accessed September 28, 2026" for references.
- Laya: English root checkpoint `convaiinnovations/laya`, pinned in a source lock, runtime 0.3.20, local FP32, about 421M parameters (ModernBERT-large), token budgets raised to 1,088/960 from 512/192; released option-count temperatures retained (stored temperature for 11 or more choices clamped by runtime to 0.5) (Section 4.3). Laya is a second decision model; ledger rows include it.
- No generative LLM comparator. Neither system fitted to study examples (Table 2 caption). Same templates, same examples, same shuffled order for both systems (Section 4.4), so tuning parity is "same prompt".

## Design and statistics
- Three decision structures from the same outputs: flat, hard routing, full marginalization (Eqs. 4-7). Metrics: accuracy, macro F1 over all declared classes (absent classes score 0), Brier (summed classwise squared error, range 0-2), 15-bin equal-width top-label ECE, parent total variation (TV), Jensen-Shannon divergence in bits, gold-probability drift (Sections 4.6, 4.7).
- Intervals: 10,000 stratified percentile-bootstrap resamples within gold label groups, seed 44, paired differences, unadjusted for multiple comparisons (Section 4.8).
- Order audit: 90 examples (30 per dataset), four extra permutations, 120 comparisons per dataset-model but only 30 distinct examples, descriptive only (Section 4.9). Repeated-request audit for Jev only: two additional identical requests on the audit examples (Section 4.9, Table 11).
- Post-hoc checks: ECE at 10 and 20 bins, exact-tie recount, de-duplication (Section 4.9, Appendix B). Sign of marginal-minus-flat ECE difference unchanged across 10, 15 and 20 bins (Section 5.2).
- Scope narrowed after pilots and partial results (Section 8).

## Calibration
- Released calibration only, no recalibration (post_hoc_calibration none): "We retain each system's released calibration settings" (Section 2.2). Jev flat ECE 0.058 / 0.020 / 0.036 (TREC / CLINC150 / MASSIVE) (Table 5).

## Cost, latency, cascade, cardinality
- Cost and latency are out of scope: "latency and cost remain outside scope" (Appendix C). Hard routing and marginalization both need K+2 questions per input (Section 4.1), so reconstruction multiplies queries, but no cost number is reported.
- No escalation or cascade analysis.
- Cardinality and option-order: Laya's temperature depends on option count; high-cardinality (50, 60, 150 labels) acknowledged as outside Laya's intended use (Section 4.3). Order sensitivity: flat label flips Jev 20.0 / 5.8 / 5.8 percent versus Laya 62.5 / 61.7 / 76.7 percent (Table 7).

## Authors' stated limitations (Section 8)
- Two configurations, three English closed-set datasets, fixed hierarchies; instructions, choices, ordering and calibration change together, limiting causal interpretation; training exposure unknown; systems differ in architecture and precision; Laya expanded input budget qualifies comparison; approximately balanced sampling; order audit small and reuses examples; repeated-request checks cover Jev only; rounded outputs.
