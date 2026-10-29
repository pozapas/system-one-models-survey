# song2026premisecheck — PremiseCheck: Efficient Fact-Checking of Human and AI Peer Reviews

arXiv:2610.21046v1 [cs.CL], 15 Oct 2026; CC BY 4.0. HTML from https://arxiv.org/html/2610.21046. Extractor: batch V15.

## Authors and affiliation
Dingjie Song, Zhiling Yan, Ziqian Zhang, Lichao Sun (corresponding) at Lehigh University; Yuxuan Zhang at University of British Columbia and Vector Institute (title page). Affiliation type: academic.

## Task and data
Score how likely a single review comment misstates what the paper says (factual error; four ReviewCritique types) and output a score in [0,1]; evaluation is AUROC x100 with errors as the positive class, plus cost and latency per comment relative to the reference (Section 3.1). ReviewFact reuses three datasets (9,267 comments on 217 papers, Section 3.3): NLP reviews from ReviewCritique (6,466 comments, 308 factual errors, Table 6 caption), machine learning reviews from ReviewScore (arguments only), natural-science reviews from Phys. Rev. B (Section 3.2; Appendix A.1). Factual errors are 4.8% of NLP and 2.5% of natural-science comments (Section 3.3).

## Decision models evaluated
Jev as router and verifier in PremiseCheck: "We use gpt-5.5-2026-04-23, gpt-5.4-mini-2026-03-17, and jev-1.13-20260917" (Section 5, footnote). Jev reads the paper truncated to 24k tokens and is billed only for input tokens at $0.042 per million (Section 5). Also holistic Jev as a baseline. Other decision models as verifiers: Kev-27B (open weight, run on the authors' GPUs), Microsoft Decision-1, Perplexity Decider, MiniCheck-7B and MiniCheck-T5 (fact-checking models, not typed decision models) (Sections 6.2, 7.1; Appendices D.2, D.4). No run dates are stated for the decision model calls; the Jev identifier carries a date stamp (20260917).

## Comparators and tuning budget
Reference: holistic GPT-5.5 at medium reasoning. Baselines: holistic GPT-5.5 at low and no reasoning, GPT-5.4-mini, holistic Jev, and a Jev-to-GPT-5.5 cascade that escalates 70% of comments (Section 5). Holistic baselines and PremiseCheck use the same papers; LLMs see the paper truncated to 24k tokens on NLP and the full paper on natural science (Appendix B.3). Holistic judgment counts repeated paper input at the cached price, "which favors the baseline" (Section 5). The non-inferiority margin (-3 AUROC points) was fixed before the experiments (Section 5). The decomposition and verification prompts were designed by the authors with development choices scored on an earlier version of the NLP prompt (Table 17 caption); "Without development data on which to select a subset, we keep all 16" phrasings (Section 7.3). Prompts for the ML and natural-science parts are variants (Appendix B.1). PremiseCheck has had more design effort than holistic baselines; the holistic prompts are single prompts.

## Reference labels
NLP: ReviewCritique, 40 NLP experts label review sentences, two per paper, an area-chair-level expert resolves disagreements (Appendix A.1). Machine learning: ReviewScore, median of three graduate-student annotators on a five-point factuality scale (Appendix A.1). Natural science: Phys. Rev. B, 45 scientists judge correctness; GPT-5.5 decides from the expert rationale whether the error is factual, checked by two authors on 178 comments with Cohen's kappa 0.76 and 0.77 (Section 3.2; Table 2). Rows coded human_adjudicated (NLP), human_crowd (ML) and llm_teacher (natural science, label partly produced by GPT-5.5).

## n, sampling and intervals
95% paired bootstrap over papers, 2,000 resamples (Section 5). Table 1 headline AUROCs are point values with paired differences; intervals sit in Tables 6, 10, 12, 16 and figures. Number of comments in the ML and natural-science parts is only in Figure 3 (not read as text).

## Test-data exposure
Source datasets are public, 2024 to 2026 (ReviewCritique 2024, ReviewScore 2025, Phys. Rev. B 2026). Papers could be in LLM training data; no contamination check is reported. Coded public-pre-2026.

## Cost and latency
Cost = token usage at public list prices (GPT-5.5 $5.00 input, $0.50 cached, $30.00 output per million; GPT-5.4-mini $0.75, $0.075, $4.50); Jev cost as reported by the API; Kev-27B GPU time reported separately (Appendix B.3). All decision-model calls together cost $0.0015 per comment on NLP (Section 4); a Jev premise check reading the full paper costs $0.00044 with median latency 216 ms against 5.1 s for GPT-5.5 (Appendix D.1). Latency is mean wall-clock time per comment from recorded API calls, premises in parallel (Appendix B.3). Cost and latency figures are for the authors' reproduction runs; the paper's headline claim is relative.

## Calibration
No calibration metric (no ECE or Brier); the score is evaluated only by ranking (AUROC). Jev probabilities are combined by min over premises and averaged over 16 phrasings.

## Cascade or escalation
Jev to GPT-5.5 cascade with 70% escalation: NLP 59.1 (-4.2) at 74.0% of reference cost; ML 65.7 (-1.1) at 76.4%; natural science 66.7 (-1.1) at 69.2% (Table 1). PremiseCheck with medium decomposer is more accurate on every part at lower cost.

## Option-name, cardinality, language and robustness tests
16 phrasings of the verification question (8 supporting and 8 contradiction) averaged in one call: AUROC 63.1 to 65.7 (Table 18). Routing ablation and mean-versus-min aggregation (Section 7.3). Length-controlled comparison (Section 6.2, Table 9). Verifier swap across decision models (Section 7.1). No option-order or language test.

## Code and data
Code https://github.com/OpenLAIR/PremiseCheck (MIT); data https://huggingface.co/datasets/songdj/ReviewFact; the ML part is a rebuild script because ReviewScore states no license (Ethical Considerations).

## Authors' stated limitations
Targets factual errors only, not errors of judgment; main decision model Jev is API-served, and only one open-weight decision model (Kev-27B) was tested (Limitations). Most false alarms arise in decomposition (Section 7.5).
