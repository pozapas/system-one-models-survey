# xu2026same

arXiv 2610.08675 (v2, 16 Oct 2026; first version 2026-10-06). "Same-Number Citation Swaps: Stress-Testing Jev as a Financial Evidence Judge". Full text: fulltext/2610.08675.html and .txt. Extractor batch V08.

**Authors and affiliation.** Chuhong Xu (Sofia University), Bo Su (Indiana University), Ziyao Chen (UC San Diego), Ruiyang Xu and Xinyu Qiu (Northeastern University), Shimeng Dai (Michigan State University) (title page). Academic.

**Task and data.** Source-support verification of LLM-generated financial calculations. Bank: 96 single-operation FinQA test questions (FinQA revision 0f16e286; 243 of 1,147 test records pass a structural screen; first 96 accepted by source-only assistant review, 96 pages, 88 company/year reports) with two GPT-4.1-mini traces each, 192 natural records (Section II-A). Same-number citation swaps: 15 distinct contrasts over 14 questions (six clear wrong-role, six equivalent-fact, three boundary) (Section III-B). Explicit-column rerun on 7 column-only contrasts (Section III-C). Fresh-source follow-up: 36 questions on 36 pages from the pinned FinQA train split, program-derived constructed records (Section III-D). Original release endpoint: Jev Choice among five numerical candidates for the 96 questions (Section IV).

**Decision model.** Jev, every call returned typesafe/jev-1.13-20260917 through OpenRouter with the TypeSafe provider (Section II-C). Choice for numerical selection; one independently specified binary Noul event for source support (same fixed instruction in all 590 saved evaluation requests). Native confidence statistic excluded. GPT-4.1-mini is the trace generator, not a comparator; served alias openai/gpt-4.1-mini, temperature 0, top-p 1, 1,024 output tokens.

**Comparators.** Deterministic literal quotation check ("literal/unit rule"); a post hoc relaxed signed-number-at-pointer rule (zero calls) added after inspecting verifier results; random none. Table II compares Jev source gates at 0.5, 0.8, 0.9 and 0.95 and a literal-OR-Jev policy. Parity: the same inputs, same release guards (available execution and matching unit) for all rules; the verifier predicate was written after inspecting retained labels and tested in four development checks (Section III-A), so the natural-record evaluation is retrospective.

**Reference labels.** Natural-record support labels come from unblinded assistant (LLM) review of all 192 traces, with documented adjudications and two unresolved; independent human confirmation incomplete (Section II-B). The fresh-source follow-up uses one non-author human reviewer who declared blindness; reviewer and corrected assistant labels agree on 64 of 72 arm labels; no inter-human agreement (Section III-D). Numerical correctness: FinQA-derived rounded key (task outcome).

**n, sampling, intervals.** Question bootstrap 2,000 resamples for verifier metrics and 20,000 for the release endpoint (Section II-C); descriptive means over two repeats for swaps; small contrast counts (four negative rendering contrasts over three source questions). Counts describe selected cases, not prevalence (Section VI).

**Exposure.** FinQA 2021 public test and train splits with answer keys; training contamination and historical information cutoffs are stated to be outside scope (Section VI). The fresh-source pages are new to the authors' local experiments, not to model training.

**Cost and latency.** Recorded provider billing is reported for each collection (e.g. USD 0.14781 for the 288-call natural-bank collection) but is the authors' own spend and not extracted; no latency reported.

**Calibration.** Brier 0.03378 and AUROC 0.98587 on 190 binary labels with mean probability 0.7975 vs support rate 0.8053; largest bin (146 records) mean 0.9375 vs observed 0.9932 (Section III-A); no formal ECE and no recalibration. Probabilities are reported to two decimals and analysed unmodified. Exact repeat variation: largest identical-input range 0.05 (original column test) and 0.18 (follow-up) (Sections III-C, III-D).

**Cascade or escalation.** Original release policy consults the GPT-4.1-mini trace only when max Choice probability is strictly below 0.8; no correction opportunity in this bank, executed-number fallback net change -1.56 points [-4.1667, 0] (Section IV, Table III). Source-probability gates at 0.5 to 0.95 in Table II.

**Option-name, order, cardinality, robustness.** Same-number swaps keep operand values, arithmetic and executed result fixed while moving one citation; wrong-period and wrong-status B citations near 0.95 support probability are accepted in 4 of 6 wrong-role contrasts; 2 of 6 equivalent-fact controls are withheld (Section III-B). Explicit column header text lowers all 8 wrong-role B calls below 0.8 but also lowers some equivalent-fact support (Section III-C). Fresh source: accept A and withhold B 8/15 (original) vs 9/15 (explicit); accept both of 19 both-supported pairs 5/19 vs 6/19 (Fig. 3). The paper cites Sun et al. on option-name binding but does not test option names itself.

**Code and data.** Inspection artifacts (inputs, responses, label reasons, blinded packet, ledger) retained privately; public access pending (Section VI). No repository.

**Authors' limitations (Section VI).** Natural bank selected for single-operation calculations with overlapping reports; primary selector's 95/96 leaves little room for the gate; historical labels from unblinded assistant review; single reviewer; temporal interpretation and header defects need judgment; exploratory sequence with post hoc steps; four negative rendering contrasts over three questions; one Jev identity and one generative alias; serving variability; failure prevalence unmeasured; Codex (OpenAI) was used for editing, experiment running and scripts (Acknowledgment).
