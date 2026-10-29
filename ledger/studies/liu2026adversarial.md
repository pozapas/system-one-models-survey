# liu2026adversarial — Adversarial Cues in Decision Models Used as Judges: The Role of Request Presentation

- arXiv: 2610.11436v1 [cs.CL], 8 Oct 2026, CC BY 4.0 (header). Full text: fulltext/2610.11436.html and .txt (fetched 2026-10-28).
- Author: Hongliang Liu, Independent Researcher (header). Affiliation type: independent. Single author. Codex-assisted implementation, analysis and drafting disclosed (Acknowledgments, Appendix M).
- Code and data: no repository URL given. Appendix M states that frozen inventories, native responses, offline replay packets and the hypothesis registry are "retained" and that prepared offline packets cover the central studies; natural questions and passages are omitted and recoverable from content-hash-pinned public datasets (Appendix M). code_available coded "partial".

## Task and data
Reference-based final-answer grading by a decision model used as a judge (Section 3). Candidate = earlier reference-matching value, a short bridge, then an explicit wrong final value ("Final answer: Y."), so the required verdict is "incorrect" (Eq. 1, Section 3). The test is whether adding one colon after six source-seeded letters changes the verdict, under two request presentations (insertion order vs recursively sorted JSON keys) and two grading configurations (FINAL3 three labels correct/incorrect/no_answer; FINAL4 the published four-label instruction adding ambiguous, from the Jev-as-a-Judge paper, ref. [12]) (Section 3, Table 3).
Confirmation bank: 100 DROP training numeric questions and 100 GSM8K test questions, one question per passage cluster, plus 20 preflight clusters; 50 near (Y=X+1) and 50 far (Y=X+max(2|X|,40)) mutations per workload (Section 4.2). Source disjointness audited against 91 prior inventory/request files (Section 4.2). Public datasets (DROP 2019, GSM8K 2021) but candidates are constructed; the study treats source disjointness from its own earlier studies as the independence criterion.

## Decision models evaluated, exact versions
- Hosted Jev, both FINAL3 and FINAL4: "requested and returned jev-1.13.0" (Section 4.2). Observation window 00:29:32 to 00:50:52 UTC on 8 Oct 2026 (Appendix A, scheduling paragraph).
- Comparator: GPT-6 Sol, "requested and returned gpt-6-sol", default reasoning, Standard service tier, strict categorical JSON, no elicited confidence, FINAL3 only (Section 4.2). Window to 00:59:24 UTC.
- Open implementations (Appendix K, historical numeric cohort of 80 reused sources, fixed cues, no search): Laya English root checkpoint rev 55cf4c4e, SemIf-OpenJev with Qwen3.5-4B rev 851bf6e8 (NF4/fp16), NanoJev unified-games Choice head rev 047b927b (float32), CLM-v0.1-8B heads rev e939398d with Qwen3-8B encoder (intended rev b968826d, NF4), Clef-flash (Cloudflare) joint-schema head rev 17f0b0ad (NF4/fp16) (Appendix K.1). Run on an 8 GB RTX 2070 laptop GPU (K.1, Appendix M). Add-on runners have weaker revision verification (K.1).
- Earlier studies also used Liquid AI's decision interface (Section 1, Tables 13, 17, 18); not a headline.

## Comparators and tuning parity
Same instructions and criterion bindings for all configurations; Sol receives the same task with the sorted JSON embedded in its input string (Section 3). The cue string was discovered through adaptive search (Qwen3-4B likelihood proposals ranked on Jev development acceptance counts, manual scaffold ablations on hosted Jev feedback; Section 4.1, Appendix E), then frozen. The attack was therefore developed against Jev, not against Sol. Preserved earlier null: on a first fresh comparator (200 clusters, insertion presentation) all colon contrasts were null after correction, and Jev FINAL3 missed a control threshold (Section 4.1, Appendix L, Table 27).

## Reference labels
Numeric certificate: the wrong final value differs from every accepted reference, so "incorrect" is required (Section 3). Reference answers come from DROP and GSM8K gold. Candidates are synthetic constructions; no human adjudication. Earlier RAGTruth/HaluEval whole-answer studies use model-qualified labels, kept apart (Section 6, Appendix J).

## n, design, intervals
200 planned source clusters per condition; 16 calls per source/configuration (2 presentations x 2 cue conditions, 4 controls, 2 duplicates) (Section 4.3). Primary estimand: equal-weight DROP/GSM8K mean of paired source interactions D_i (Eq. 3). Null-centered workload-stratified cluster bootstrap, Holm over three configurations; pointwise 95% bootstrap intervals; exact McNemar secondary (Section 4.4). Jev panels complete; 6 unknown OpenAI responses leave 196 complete Sol sources (Section 4.3). Control gates: at least 190/200 for bare correct, bare wrong, wrong-final-only, 180/200 for valid revision (Section 4.3); Jev passes all under both presentations (Section 5.1, Table 4).

## Headline results
- Sorted presentation, FINAL3: false acceptance 2/200 to 52/200 (1.0% to 26.0%); FINAL4: 6/200 to 53/200 (3.0% to 26.5%). Insertion presentation: 0/200 in both cue conditions for both configurations (Section 5.1, Abstract).
- Interaction +25.0 pp [19.0, 31.0] (FINAL3) and +23.5 pp [18.0, 29.5] (FINAL4), Holm p = .00006 (simulation floor) (Section 5.1).
- Near mutations +2 pp, far +48 pp (FINAL3) and +45 pp (FINAL4) (Section 5.2).
- GPT-6 Sol: no observed cue-condition false acceptance; 196 complete interactions zero; planned-panel bound [-0.5, +1.5] pp with missing responses assigned least/most favorable values (Section 5.1).
- Duplicates under sorted presentation: FINAL3 2/200 and 48/200; FINAL4 6/200 and 59/200, accepted sources change between identical requests (Section 5.3, Table 6).
- Identical-request variability (Table 18): Jev verdict changes in 7 of 324 groups (numeric repeat, 29 Sep) and 1 of 192 (reference switch, 30 Sep); Liquid 0.
- Open implementations fail the competence gate (80-source numeric cohort, required 76/76/76/72): Laya 67/46/54/75, SemIf NF4 79/54/59/68, NanoJev 17/69/54/51, CLM NF4 38/0/0/59, Clef-flash NF4 65/64/68/51 (Table 22, column order correct value/wrong value/wrong final/valid revision).
- Earlier fresh comparator (Table 26/27): Jev FINAL3 wrong-final-only 189/200 vs 190 required (gate failed by one), FINAL4 191.

## Test-set exposure
Source questions from DROP training and GSM8K test, public before 2026; candidate strings are new constructions; audited disjoint from the authors' earlier inventories (Section 4.2). No pretraining-contamination check (Section 4.2: "entity, topic and pretraining dependence unverified").

## Cost, latency
Study cost reports ($2.22 and $3.20 conservative rate-policy charges, Appendix M) are the author's own spending and are not coded. No latency reported for Jev. Hardware: single laptop for open models; provider hardware unobserved (Appendix M).

## Calibration, cascade, language tests
Displayed-score interactions (mean +.19955 and +.17230) are descriptive; "rounding and calibration limits" noted (Section 5.3). No calibration analysis, no cascade, no option-name or language test in this paper (option-name binding is cited to ref. [23]).

## Paper's own limitations (Section 6)
Recursive sorting changes several request objects together so component attribution is unmeasured; generality limited to reference-aware numeric grammar, balanced source/mutation mixture and recorded service window; near/far confounded with question; natural prevalence and downstream consequences unmeasured; author-led computational verification only, no external human audit; vendors notified 30 Sep 2026 with no feedback (Appendix M).
