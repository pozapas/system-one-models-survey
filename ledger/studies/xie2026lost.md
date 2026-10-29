# Xie et al. 2026, Lost in the Fallback: How Reliably Do Typed Decision Models Use Fallback Options?

arXiv:2610.19856v1 [cs.CR], 14 Oct 2026, CC BY 4.0 (fulltext/2610.19856.txt, header).

## Authors and affiliations

Yuanbo Xie and Mingli Zhu (equal contribution), Haixiao Xiong: System Security Team, Li Auto Inc, China (industry). Tianyun Liu (corresponding), Yingjie Zhang, Tingwen Liu (corresponding): Institute of Information Engineering, Chinese Academy of Sciences, and School of Cyber Security, University of Chinese Academy of Sciences (academic). The HTML author block is garbled so the exact author to affiliation mapping beyond Li Auto for the first two authors is uncertain. Affiliation type: mixed.

## Task and data

Paired Fallback Robustness (PFR) Test: for each input, four requests cross two category-to-output assignments (gold category regular vs moved into the fallback) with two logically equivalent fallback definitions (Union lists fallback categories, Complement excludes regular categories); the option count and inventory stay fixed (Section 3.1, Figure 2). Main sets: class-balanced CLINC150 (450 texts), BANKING77 (385), full TREC50 test split (500), with fifteen regular options and one fallback (Section 3). Diagnostic and development panels use 128 additional texts per dataset from validation or training data, with exact and normalised matches to test excluded (Appendix A). "Labels" are the benchmark category labels; the required output is constructed from them (synthetic procedure, ledger label type synthetic). The benchmarks predate 2026 (public); no contamination analysis. Metrics: A+ regular accuracy, A- fallback recall, F+ false fallback rate, J joint correctness, DR U/C disagreement, P4 pass on all four requests (Section 3.1). Intervals: 95% paired text-bootstrap (10,000 draws); Holm-corrected exact McNemar tests over 42 tests (Appendix A); Table 1 headline cells carry no intervals in the table itself (paired intervals in Figure 16).

## Decision models

Four 4B choice-selection configurations (Section 3, Appendix A): Intern-Decision (InternLM Team 2026, symbol scoring, native limit 62 options), Kev-4B (Palmer 2026b, model card "Kev 1.0", option-pointer head on Qwen3.5-4B-Base, limit 255), JevK5 v0.3 (Serikbay 2026, answer-letter scoring, an open-weight Jev alternative), SemIf (TheoLeeCJ 2026, Qwen3.5-4B). Score temperatures 1, 1.22 (JevK5), 2.40605 (Kev). Parameter sweeps: Intern 0.8B/2B/4B, Kev 0.8B/4B. Cross-backbone: Laya (revision 55cf4c4ebb4e, accessed 9 Oct 2026) and OpenJev (Open-Jev-DeBERTa-v3-Large, revision 188ee67a5c93, accessed 9 Oct 2026). Hosted Jev is not evaluated. Revisions for the four main models are not given beyond JevK5 v0.3 and "Kev 1.0" and access date 9 Oct 2026.

## Comparators and tuning parity

All models receive identical requests and options; no prompt tuning; no external LLM baseline. Classify-then-map and membership/threshold interventions are diagnostics on the same scores (Section 5, Appendix E). Threshold fitting uses separate development and calibration pools (Appendix E).

## Headline results

P4 (all four requests correct, Table 1): CLINC150 Intern 52.0, Kev 80.2, SemIf 58.2, JevK5 40.9; BANKING77 50.6, 81.0, 57.7, 33.5; TREC50 18.2, 64.0, 45.6, 20.8 (Section 3.2 says the range is 18.2 to 81.0 across twelve settings). Intern on 329 reference-correct TREC inputs: accuracy under Complement falls from 97.9% (gold regular) to 23.1% (gold fallback) (Section 3.2). Supplying the correct category does not fix it: JevK5 fallback recall 71.1% and 14.8% under U and C (Section 3.3); OpenJev perfect regular accuracy but 43.4% and 41.0% fallback recall (matched 256-text task). Kev reaches 99.2% and 98.4% joint correctness in a sixteen-option category-only BANKING77 task. JevK5 on CLINC: fallback recall differs by only 1.8 points between U and C yet 33.3% of choices change; gold-fallback disagreement exceeds 10% in ten of twelve pairs (Section 4.1). Fast/Defer policy task: joint policy correctness zero for all four models (Section 4.3, Table 4).

## Calibration

No ECE or Brier. Scores used for threshold analyses: development-selected and shared thresholds; individually recoverable errors exceed shared-threshold recovery in every setting (Section 5.3, Figure 12). Score temperatures per model are the native readout settings (Appendix A).

## Cascade and escalation

Fast/Defer (System 1 deferring to System 2) is the application framing (Figure 7b) and is tested as a policy decision with supplied quality estimates (Section 4.3). No cascade cost measured.

## Option-name, cardinality, language and robustness tests

Central: equivalent definitions (three wording pairs), fallback position (four positions, three choice sets), fallback names, length and category-mention matching, replacement categories and list layout, 16 options versus 4 (Appendix C, Sections 3.3, 4.2). Number of options fixed at 16 in main runs. English only.

## Cost and latency

Not reported. One repeat of 384 matched requests per 4B configuration gave identical choices (Appendix A).

## Code and data availability

"We will make all code and data publicly available upon acceptance" (footnote on the abstract); no URL.

## Paper's own limitations

Focuses on identifying failures not mitigations; experimental settings may not capture real-world complexity (Limitations).
