# gan2026sansi

arXiv 2610.07730 (v2, 10 Oct 2026; first version 2026-10-06). "SanSi: A Looped Typed Decision Model for System 1.5 Thinking". Full text: fulltext/2610.07730.html and .txt. Extractor batch V08.

**Authors and affiliation.** Shuyu Gan, Young-Jun Lee, Dongyeop Kang, University of Minnesota (title page). Academic.

**Task and data.** Typed decisions over a suite of public datasets rendered in one prompt format (state, question, up to 26 lettered options). 12,800 training items from 20 sources, 2,471 development items, 10,027 test items from 59 sources (in-distribution 2,116; near transfer 1,871; far transfer 5,809; includes 231 public JevBench items); 382 test items are unanswerable (key evidence removed, target uniform) and 766 carry a crowd distribution (Table 1, Section 4, Appendix A). Item types: classification, multi-step reasoning, uncertain evidence, long documents, sentence pairs, knowledge. Also two program-generated depth-controlled tasks (liar chains, object swaps; 120 items per depth, depths up to 16, 1,920 items per task for the Jev API) (Section 5.4, Appendix G) and a verifier case study on 2WikiMultiHopQA (3,000 test questions) (Section 8).

**Decision models.** SanSi: Ouro-1.4B (pre-trained looped LM, frozen) with LoRA rank 64 (60.6M parameters) and per-loop readouts (0.27M), trained 1,000 steps of 16 items with cross-entropy plus Brier at every loop, T=8 loops; SanSi-2.6B on Ouro-2.6B (Section 3, Appendix B). Single-pass comparators trained with the same recipe, data, seeds: Ouro-1.4B one loop, SmolLM2-1.7B, Qwen3.5-2B, Qwen3.5-4B (Base checkpoints); Kev-4B (our data) uses Kev's own code and recipe (Section 4, Models). Released references not trained on the authors' data: Kev-4B (released) and the commercial Jev API, jev-1.13.0 (Appendix D.9). The paper does not state API access dates for Jev; it states jev-1.13.0 and a single run on the main suite and three calls per item on the depth tasks (Table 7, Appendix G.6).

**Tuning-budget parity.** Same data, order, LoRA rank, readout, loss, three seeds for all fine-tuned models (Section 4). Jev API not trained on the suite and used as offered; the authors call it a reference only and give a fairer cut on items whose sources neither side trained on (6,040 items: Jev 83.5% vs SanSi-2.6B 71.9%, Table 14). The Qwen3.5 models are described as references, not controlled comparisons (Section 5.1). Kev's recipe additionally fits one temperature on the development split (Appendix B).

**Reference labels.** Public dataset gold labels (mixed human-written and curated labels), a crowd label distribution for 766 items, a synthetic uniform target for 382 unanswerable items, program-generated labels for depth tasks. Verifier study graded by Claude Sonnet 5.5 against gold answers (97.4% label stability on 500 re-graded answers) (Section 8, Appendix I.2). Ledger uses human_crowd for main-suite rows.

**n, sampling, intervals.** Means plus or minus standard deviation over three training seeds; 95% bootstrap intervals over groups of related items; released Kev-4B and Jev API are single runs (Tables 2, 7). Test items split from development by connected components of related items (Appendix A).

**Exposure.** All data are public benchmarks; the authors say they cannot exclude that a backbone has seen some of them in pre-training (Limitations). Leakage controls: no shared state or 80% sentence overlap between test and train items; no duplicate text (Appendix A). 721 Kev-source in-distribution test items are training items for the released Kev-4B (Appendix D.9).

**Cost and latency.** GPU time of one test pass relative to Ouro-1.4B one loop on one RTX A6000: SanSi loop 8 7.7, loop 3 2.9, SanSi-2.6B 14.8, Qwen3.5-4B 2.4; peak memory 6.2 GB (8 loops) and 5.3 GB (1 loop) vs 12.9 GB Qwen3.5-4B (Table 6, Section 5.1). Training 9.5 times one loop. No milliseconds or dollar costs; Jev API not timed.

**Calibration.** Top probability confidence; ECE over ten equal-width bins on answerable items; Brier; evidence AUROC on 786 items; selective prediction in Appendix F (Section 4 Metrics). ECE: SanSi loop 8 0.093, loop 3 0.082, averaged loops 0.044; Qwen3.5-4B 0.113; Kev-4B (our data) 0.119; SmolLM2-1.7B 0.069; Jev API 0.066; released Kev-4B 0.036 (Tables 2, 7). Fitting one temperature on development data brings four models to ECE 0.022 to 0.029 (Appendix B discussion after Table 27). Confidence rises on right and wrong answers alike; AUROC for right versus wrong 0.760 to 0.795 (Section 5.3). Jev API gives a hard answer on 62.8% of unanswerable items (Table 7).

**Cascade or escalation.** No model cascade; early exit with Ouro's frozen exit gate at cumulative exit probability 0.5 keeps loop-8 accuracy with 4.5 loops on average, 44% fewer, falling to about 25% fewer in static batches (Section 5.2, Limitations). 11.7% of items are right at some loop but wrong at loop 8.

**Robustness and depth.** Liar chains: SanSi holds depth 11 after four loops, 72.6% on unseen depths 9 to 16 vs Qwen3.5-4B 50.0% (Section 5.4). Jev API on liar chains: 100% at depth 1, 86.4% at depth 2, 62.5% at depth 3, around chance from depth 6; on object swaps 77.5% at one swap, 42.5% at two (Appendix G.6, Table 35). Option shuffle each draw in training; running beyond trained loops lowers accuracy (72.0 to 70.1 at loop 16) (Section 7). English only.

**Verifier use case.** SanSi probability as sole GRPO reward for SmolLM2-1.7B on 2WikiMultiHopQA: correct share 37.0% to 52.1% when read at loop 8, unchanged (37.5%) at loop 1 (Section 8).

**Code and data.** Project page https://minnesotanlp.github.io/Sansi/ in the header; the text does not state a code repository (recorded as partial).

**Authors' limitations.** One backbone family pre-trained to loop; 3.3 times Qwen3.5-4B GPU time; memory advantage holds for one decision per call; stopping rules tested only on stored probabilities; depth analysis uses two program-generated tasks; verifier study uses one dataset and one generator; English suite assembled from existing datasets; possible backbone exposure; three seeds so small-group differences need intervals (Limitations).
