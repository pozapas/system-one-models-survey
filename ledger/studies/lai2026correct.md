# lai2026correct

arXiv 2610.16191v1 (cs.AI), 12 Oct 2026. "Correct Choices, Failed Sequences: Choice2Seq Benchmarks Correctness Retention Across Output Interfaces."
Authors: Tianyou Lai (Carnegie Mellon University), Wentao Yue (Shenzhen University), Zhiying Deng (Central China Normal University), Qilei Li (Central China Normal University; corresponding). Affiliation type: academic. (title block)

## Task and data
- Choice2Seq: for each item (problem, target of length 3 to 8, eight equal-length candidates), compare Native (select a complete candidate) with Serial (append one character per position, each step a fresh typed decision with the current prefix as state). Sequence Composition Rate (SCR) = share of Native-correct items also solved by Serial. (Sec. 3.1)
- Domains: arithmetic (multiplication) and lexical retrieval (English nouns from WordNet definitions with wordfreq metadata); 384 test items per domain, disjoint development data; arithmetic and lexical items matched on correct-prefix candidate ambiguity. Lexical items screened and human reviewed for sense-specific acceptability. Additional: Schema-Guided Dialogues (public, CC BY-SA 4.0), semantic Boolean-field panel (128 records), COPY/REVERSE panel, 12-character reversals. (Sec. 3.2, 3.3, Ethical Considerations)
- Reference labels: synthetic/programmatic gold (computed arithmetic answers, WordNet target nouns) with partial human review of lexical acceptability; dialogue gold from SGD annotations. (Sec. 3.2)
- Test exposure: generated problems and constructed candidate sets (new items); WordNet and SGD resources are public.

## Models
- Jev pinned to jev-1.13.0 with SDK 0.7.0 (App. A.7). Formal construction scores the choice returned by the service; readout/plan diagnostics use probability argmax. Hosted-call dates not stated ("collection windows").
- StartLux-Decision-4B (open decision model): BF16 revision 9302aedb7f7bd889994336f2ae919dffbf5dbee1, code revision c61bfab3bb4fa3ae9d155d457247a7fd0a299a24.
- Comparators (generative): Qwen3-8B (full BF16, thinking off, code-token contract), Qwen3.5-27B (BF16 revision fc05daec..., code and direct character contracts, thinking off). Same problems and candidates, but different output contracts (legal codes vs direct characters) with separate Native denominators. (Sec. 3.4, A.7)
- Hosted and local runs use different hardware.

## Comparators and tuning
No tuning; prompts per model/contract with prompt-variant robustness reported (3 templates for Qwen direct). Interventions (Union, Trie, Indexed evidence) are controls on the controller rather than model tuning. Qwen repeats use a frozen stratified 192-item subset in some panels. (Sec. 3.3, 4)

## Uncertainty
Length-stratified item bootstrap 95% CIs (whole items or source clusters); exact binomial for zero-success cells; exact McNemar with Holm correction for primary tests; whole-dialogue bootstrap for dialogue; exploratory GEE. (Sec. 3.4)

## Headline results (Table 1, n=384 per domain)
Jev Native EM 97.1 (math) and 99.5 (lexical); Serial EM 32.0 and 2.1; SCR 33.0 [29.0, 37.0] and 2.1 [0.8, 3.7]. StartLux SCR 3.4 and 0.3. Qwen3.5-27B direct SCR 10.3 and 34.7. Every original paired decrease survives Holm correction. Candidates alone yield near-chance selection. (Table 1, Sec. 4)

## Controls
Lexical Jev EM: Full 1.8%, UnionCall 24.0%, TrieCall 82.0% (matched items); only 26.3% of UnionCall outputs belong to candidates. TrieFill reduces calls from 5.5 to about 2 per item. Indexed evidence improves copying fidelity even for incorrect selections. (Sec. 5.1, Fig. 12)

## Calibration
Chosen-path Product, geometric mean and minimum top-choice probability scored with Brier, ECE, AUROC and AP. Product improves arithmetic AUROC over a length baseline by 0.068 [0.051, 0.086]; lexical independent evaluation has 13/2,347 successes (0.55%) so gains span zero; at 10% coverage Product precision 3.8% [1.7, 6.4]. Table D14 (lexical, Equal-length mixture, original cohort): Product Brier 0.019, ECE 0.010, AUROC 0.936; Geometric mean ECE 0.286; Minimum ECE 0.183. ECE binning and bin count not stated in the main text. Table caption does not name the model; App. A.7 says independent calibration studies score the choice returned by the service (Jev). No recalibration. (Sec. 6.1, Tables D12, D14)

## Cost and latency
Jev costs computed from recorded token usage at a frozen rate of USD 0.042 per million input tokens (estimated charges). Dialogue: Jev Joint 576 calls and 822,825 input tokens vs Independent or Serial 1,716 calls and about 1.65 to 1.69 million input tokens. Serial adds requests, tokens and recorded request time relative to Native. Request timing recorded separately for hosted and local runs; no single latency headline. (A.7, Table C5, Sec. 6.1)

## Cascade or escalation
None.

## Dialogue (Schema-Guided Dialogues, 96 dialogues per arm)
Jev mean-turn EM Joint 76.0 [71.0, 80.7], Independent 76.0, Serial 75.5 [70.8, 80.0]; final-state Joint 55.2, Serial 52.1; retention under Serial 420/429 turns (97.9 [96.6, 99.2]). Qwen3.5-27B Joint 75.4, Independent 70.6, Serial 72.3. Semantic Boolean fields: Jev Native/Serial EM 89.8/90.6 (SCR 96.5), Qwen3-8B 21.9/28.9 (SCR 21.4), StartLux 51.6/71.1 (SCR 77.3). (Tables C4, C5, 2)

## Robustness
Option-name conflicts, option order, prompt variants, digit/letter encodings tested in appendices (named vs binary fields; extra conflict losses significant for StartLux arithmetic and Qwen3-8B lexical readout). English and arithmetic only; no multilingual tests. (Fig. 5, Sec. 3.3)

## Code and data
"Code and data will be released soon" (abstract); not available at time of writing.

## Authors' limitations (Limitations section)
Short constrained construction (lengths 3 to 8, eight candidates) not long-form or multilingual; Full and Union admit non-candidate outputs; matching correct-prefix geometry leaves off-path branching and vocabulary task-specific; natural generation comparisons are distinct interface configurations, not mechanisms; indexing controls confound addressability and salience; human judgments cover only reviewed population; fresh-plan fidelity uses 30 plans per model and domain; confidence and cost findings tied to evaluated mixtures.
