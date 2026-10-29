# Zhang et al. 2026, Typed Decision Models on Tabular Data

arXiv:2610.19536v1 [cs.CL], 14 Oct 2026, CC BY 4.0 (fulltext/2610.19536.txt, header).

## Authors and affiliations

Baowen Zhang (University of Wisconsin-Madison), Hangting Ye (corresponding; School of Artificial Intelligence, Jilin University), Hongyuan Zha (School of Data Science, Chinese University of Hong Kong, Shenzhen). Affiliation type: academic (title block).

## Task and data

Three tabular decision tasks (Section 2.2, Table 2). Row classification: 10 datasets of TabLLM and FeatLLM, 3,481 rows, Macro-F1 averaged over datasets. Fact verification: TabFact, 2,000 claims, accuracy. Anomaly detection: ReTabAD, 20 sources, 5,059 samples, AUROC averaged over sources. The paper does not describe how the benchmark labels were made; they are the public benchmark labels (TabFact is crowd-annotated in its original paper, an inference not stated here). Subsets of each benchmark are used because every request is sent under every rewrite to seven models (Limitations). Sampling design for the subsets is not described. All three benchmarks predate 2026 (Table 2 cites Hegselmann 2023, Han 2024, Chen 2020, Yoon 2026 ICLR); no contamination check is reported.

Each request is sent in its original form and under 21 types of information-preserving rewrite (question: option names, order, yes/no, paraphrase; table: format, row and column order, in-context example presentation) (Section 2.3, Tables 12 to 14, Figure 1). Rewrite validity was checked by recovering the original request (Section 2.3). A decision flips when it differs from the original decision, invalid output counts as a flip, and a re-send rate is reported from identical re-sent requests (Section 2.3).

## Decision models (Appendix A, Table 7; Section 2.2)

- Jev: typesafe/jev-1.13 revision 20260917, TypeSafe API through OpenRouter, runs 1 to 5 Oct 2026 (Tables 7, 8).
- Clef: Cloudflare/clef commit 2f3de3dd, own implementation of release code, A800 and RTX 6000D, 1 to 9 Oct. Trained from Qwen3.8-27B. Clef sorts the options (Section 4).
- Kev-27B: jaredpalmer/kev-27b revision 28be62e9, official server bf16 on 4 A800, 6 to 9 Oct. Trained from Qwen3.8-27B.
- GPT-6 Luna Decisions: openai/gpt-6-luna-decisions snapshot gpt-6-luna-decisions-20261006, OpenAI Decisions API (public beta) through OpenRouter, 12 Oct. Probability computation undocumented (Section 2.2).

## Comparators and tuning parity

GPT-6 Luna (snapshot gpt-6-luna-20260922, temperature 1, reasoning off), Qwen3.8-27B and Llama-3.3-70B (vLLM, greedy). Decision models get identical requests and the LLM prompts are built from them (Section 2.2). No prompt tuning is described; the LLMs receive no option descriptions in row classification and no options in anomaly detection (Table 13 caption), which is an interface asymmetry. Supervised references: best of eight classifiers trained on the whole training split (LightGBM) and best of five anomaly detectors (k-nearest neighbours), plus TabPFN-3.5 (Table 3 notes, Section 3, Figure 2). Decision models run 16 rows per request in classification, LLMs one row.

## Headline results

Performance (Table 3): Macro-F1 / accuracy / AUROC. Jev 52.1 / 89.7 / 74.6; Clef 58.4 / 85.0 / 74.7; Kev-27B 55.2 / 88.8 / 81.2; GPT-6 Luna Decisions 61.2 / 78.7 / 80.5; GPT-6 Luna 62.5 / 79.0 / 77.3; Qwen3.8-27B 52.2 / 82.5 / 71.0; Llama-3.3-70B 44.0 / 80.5 / 61.0; trained 80.0 / n/a / 78.8. No intervals for these headline cells in the main text (Appendix C is said to give every result with intervals, Section 2.3, but Table 3 shows none).

Latency and price (Table 4, Section 3): Jev 0.08, 1.33, 0.09 s per decision and US$10, 38, 16 per million; GPT-6 Luna 1.62, 1.59, 0.73 s and US$81, 62, 68. GPT-6 Luna costs 1.6 to 8 times Jev per decision (Section 3). Latency timed only for closed models.

Robustness (Sections 4 and 5): option renaming or reordering flips 2 to 8% for Jev, Clef, Kev-27B versus 14 to 30% for open-weight LLMs; GPT-6 Luna Decisions flips 23% (classification), 12% (TabFact), 22% (anomaly) when options are reversed, 92 to 100% of flips move to the option now listed first (Section 4). Items changed by at least one table rewrite (Table 5): Jev 33.8 / 19.3 / 21.1 %, GPT-6 Luna 42.8 / 60.8 / 63.4 %.

Confidence (Section 6, Tables 6, 9, 10, Figures 4 to 7): confidence = max option probability for decision models, share of ten temperature-1 draws for LLMs. Flip AUROC for Jev 0.87 [0.86, 0.88], 0.89 [0.89, 0.90], 0.89 [0.88, 0.91] (95% cluster bootstrap, Table 9); error AUROC far lower (0.59, 0.65, 0.82). Of the 25% most confident items, 0.1 to 5% change under a table rewrite (Table 6). Re-querying the 25% least confident rows recovers 79 to 89% of the full re-query Macro-F1 gain for decision models (Figure 4).

## Calibration

No ECE, no reliability analysis, no recalibration. The paper uses the probability as a ranking signal for rewrite sensitivity (flip AUROC), not calibration. It defines "confidence" as max probability, not the API confidence field (Section 6).

## Cascade and escalation

Selective re-query of low-confidence rows in other formats (Section 6, Figure 4); the Discussion proposes a decision model deciding most items and an LLM reviewing low-confidence ones as future work (Section 8).

## Option-name, cardinality, language and robustness tests

Central topic (RQ2 and RQ3): option names (A/B, synonyms), order, yes/no question, paraphrase, table format, row and column order, in-context example presentation (Sections 4 and 5, Tables 12 to 14). No language or cardinality sweep.

## Cost, hardware

Appendix B, Table 8: closed models via API; open models on four or six NVIDIA A800 80GB PCIe and four RTX 6000D; trained methods and TabPFN on CPU. Dates 1 to 12 Oct 2026.

## Code and data availability

No code or data release statement found in the text. Kev repository URL cited (reference Palmer 2026), not the paper's own code.

## Paper's own limitations (Limitations section)

Each of seven models tested in one version; closed services may change and Decisions API is public beta; three kinds of tabular decision, benchmark subsets; 21 rewrite types omit column renaming and unit conversion. Main stated weakness of decision models: not robust to table organization (Section 8).
