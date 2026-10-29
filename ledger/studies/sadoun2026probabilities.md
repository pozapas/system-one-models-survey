# sadoun2026probabilities

arXiv 2610.09188 (v1, 06 Oct 2026). "From Probabilities to Decisions: Search and Multi-Teacher Distillation with Jev". Full text: fulltext/2610.09188.html and .txt. Extractor batch V08.

**Authors and affiliation.** Mohamad Yazan Sadoun, Sarah Sharif, Yaser Mike Banad; INQUIRE Lab, School of Electrical and Computer Engineering, University of Oklahoma (title page). Academic.

**Task and data.** Two applications of Jev judgments (Abstract, Sections 2 to 6). (1) Bullet chess: Jev pairwise move judgments distilled into a 443-weight evaluator for Stockfish 17.1 search; 63,135 candidate pairs from 13,000 positions in 2,042 source games (1,835 Lichess database games August 2026, both players at least 2200, and 207 lab-bot games), each pair queried in both orders (126,270 Jev probabilities); evaluator strength measured by games at 60 s per side (Section 4, Appendix L). (2) Passage reranking: 80,000 MS MARCO training pairs labelled in both orders, MiniLM-L6-H384 rerankers (10,000 steps, five seeds), evaluated on BM25 top 100 for 97 human-judged TREC DL 2019 and 2020 queries; label accuracy on 500 human-graded TREC DL 2019 pairs (Section 6, Appendix N). Transfer to Breakthrough, Othello and Connect-4 in Appendix G.

**Decision models.** Jev through the TypeSafe API with the Choice interface (Appendix M). No version string is given (documentation accessed 2026-09-26 per the reference list); recorded as not reported. Jev is a labeller only; the deployed evaluator and reranker are small distilled models. Live Jev call median 177 ms (Section 2.2). Comparators as judges: Qwen3-32B (reasoning off, normalized probabilities of the two answers), OLMo-2-0325-32B-Instruct, DiffusionGemma-26B via the djev service (Section 3).

**Comparators and tuning parity.** Evaluators share code, features, split rule and candidate penalties; weights chosen by validation log loss; scale selection with 200 validation games per setting for each evaluator with the same calibration budget (Sections 3 and 4). Equal-budget controls: 252,540 responses per evaluator, twice the pairs for Jev-only and Qwen-only, two averaged answers per judge, recalibrated Qwen (fitted temperature T near 18), Jev replaced by 0.5, shuffled Jev probabilities (Tables 1 and 2). Baselines H_m (mobility) and H_s (Simplified Evaluation Function). Lambda selection rule matters: lead over Qwen on twice the pairs is +9.6 Elo with full-data settings but +2.2 [-2.4, 6.8] when lambda is selected per subset (Section 5.4).

**Reference labels.** Chess: game results between engines (task outcome) and Stockfish preferences for label-level scores (an engine-generated reference; ledger marks synthetic). Passage pairs: TREC human relevance judgments (single assessor per judgment; not adjudicated here).

**n, sampling, intervals.** 95% percentile intervals from 10,000 bootstrap resamples of opening clusters (colours kept together), seed 20260928; normal intervals for one test; fresh openings for each comparison, scale selection on a reserved set; five seeds for rerankers; queries resampled (Sections 4 and 6, Appendix L).

**Exposure.** Chess games are play-time matches with fresh generated openings, so recorded as new; source games from Lichess August 2026 (after Jev's 2026-09 release, so pre-release data are not in play), but positions are public. TREC DL 2019 and MS MARCO are public pre-2026; contamination of Jev or Qwen not discussed.

**Cost and latency.** Table 4: effective ms per response Jev 7.6 (20 concurrent, API), Qwen3-32B 54.6 (sequential, 1x H200, 1.91 GPU-h), OLMo-2-32B 35.6 (1.25 GPU-h), DiffusionGemma 7.9 (32 concurrent, RTX 5090, 0.28 GPU-h) for 126,270 responses. TypeSafe stated price $0.042 per million input tokens, output free, 372.3 billed tokens per call (Section 8). Reported labeling outlay for the 126,270 Jev responses: $1.97 and about 16 minutes of API time (Section 8); recorded here as a measured cost per decision, about 0.0000156 dollars per response, not as research spend. Collecting 160,000 Jev passage answers took about 21 minutes of API time versus about 5.1 GPU-hours for Qwen (Section 6).

**Calibration.** Expected calibration error against Stockfish preferences on 12,280 held-out pairs: Jev 0.081, DiffusionGemma 0.159, OLMo 0.176, Qwen 0.260; binning not stated (Section 5.5). Label-level agreement with Stockfish is similar across judges (52.9 to 54.5%). Qwen recalibrated with a fitted temperature as a control only. No recalibration applied to Jev.

**Cascade or escalation.** Retrieval gate: asking Qwen only about Jev's least certain pairs loses to Jev alone at 80,000 answers and does not beat it at 160,000; splitting orders between judges is similar; two judges on half the pairs versus Jev on all loses 0.032 NDCG@10 (Section 6, Appendix N). No inference-time escalation.

**Option-name, order, robustness.** Both presentation orders always queried and averaged; Jev same answer in both orders on 94.8% of 500 human-graded pairs vs Qwen 90.6%; 86.7% vs 72.0% on 80,000 training pairs (Appendix N). Two Jev answers on a chess pair agree on 92.1% of pairs (Section 5.2). Transfer: evaluator trained on Jev labels helps chess and Breakthrough but hurts Othello and Connect-4 (Section 7, Appendix G, K).

**Code and data.** No repository URL; Appendices A, L, M and N describe splits, features, prompts and training; stockfish source tag sf_17.1 cited.

**Authors' limitations.** Not collected into a limitations section; stated caveats include that the complete bot's trajectory uses all components, Jev-derived evaluation weakens play in Othello and Connect-4, the lead over alternative partners shrinks when lambda is chosen per subset, and a label-level score does not explain play strength (Sections 2.1, 5.4, 5.5, 7).
