# dinzinger2026system

arXiv 2610.32318v1 (cs.CL), 23 Oct 2026. "System One Models Are Not Better Rerankers." Authors Michael Dinzinger (University of Passau), Kanishka Ghosh Dastidar (Interdisciplinary Transformation University Austria, IT:U), Michael Granitzer (University of Passau and IT:U). Affiliation type: academic. Funded by a German federal ministry (BMLEH/BLE); no competing interests declared; generative AI used for code and language editing. (title block, Acknowledgements, Disclosure)

## Task and data
- Passage reranking of the BM25 top-100 (Pyserini) candidates for TREC DL 2019 to 2023 (MS MARCO v1 and v2 passages) and five BEIR collections (TREC-COVID, NFCorpus, SciFact, Touche, DBPedia); ten collections in total. Zero-shot subset (ZS) is TREC-COVID, Touche, DBPedia (no fine-tune trained on them). Per-collection query counts not reported. (Sec. 4)
- Decision question per passage: "Does document {doc} answer the query?", fixed before the runs but "not chosen on development data"; one alternative wording (S1Rank: "Is document {doc} relevant to the query? ...") also run. (Sec. 4 The question)
- Reference labels: the collections' human relevance judgments (TREC assessor qrels, BEIR qrels); on TREC DL a passage is relevant from grade 2. Single judgment per pair; adjudication not discussed. (Sec. 4)
- Datasets public and predate 2026. MS MARCO seen in training by Qwen3-Reranker, Prism and the authors' fine-tunes; Kev training data contain neither MS MARCO nor BEIR; Clef's data not stated. Zero-shot subset used to separate this. No explicit contamination check for the base Qwen models. (Sec. 4, 5, 7)
- Calibration is measured only on the judged query-passage pairs of TREC DL 2019 to 2023 (the only collections judging many non-relevant passages). (Sec. 4)

## Decision models
- Six Qwen backbones from 0.6B to 27B (Qwen3-0.6B, Qwen3-8B, Qwen3.5-0.8B/4B/9B, Qwen3.8-27B). Decision fine-tunes: Kev on every backbone (LoRA up to 9B; Kev-27B a full fine-tune of the released chat model), Clef-Flash (9B) and Clef (27B), each in isolated and joint mode (joint: all 100 candidates in one state). (Sec. 4)
- Revisions: Clef 2f3de3dd (27B) and Clef-Flash 17f0b0ad (9B), accessed 2026-10-07; Laya revision 7b928d82, accessed 2026-10-07; jaredpalmer/kev-4b@6cfce5c2, kev-27b@af0e6d55 (other Kev sizes referenced to model cards accessed 2026-10-09). Hosted Jev "1.13.0" (closed, both modes); no run dates given for Jev. (Sec. 4, references)
- Context-only systems: Laya (isolated only), monoT5-3B, bge-reranker-v2-m3, Set-Encoder, RankZephyr (run on TREC DL), RankGPT-4 (published numbers). Published numbers used for several BEIR cells (Table 2 dagger). (Sec. 4, Table 2)

## Comparators and tuning parity
- Each backbone is studied as a triplet: untuned model asked the same question, decision fine-tune, reranker fine-tune (Qwen3-Reranker 0.6B/8B, Prism 0.8B/4B/9B, and two authors' own: Ours-9B and Ours-27B). Reranker fine-tunes keep their own prompt; decision and untuned models share one question. (Sec. 3, 4)
- Authors' reranker fine-tunes: LoRA r=32, one epoch over 100k MS MARCO queries (one relevant plus 15 hard negatives), InfoNCE plus binary cross-entropy, checkpoint chosen on 200 MS MARCO dev queries by a pre-fixed rule, trained once, no hyperparameter search, training queries matching test or dev topics removed. (Sec. 4)
- Asymmetries disclosed: the released fine-tunes differ in training data as well as objective; Kev uses different base checkpoints than Prism; Qwen3-Reranker is built on the same pretrained checkpoints as Kev. (Sec. 7)
- Sanity checks: BM25, monoT5-3B and RankZephyr reproduce published numbers within 0.2 nDCG@10; Jev joint with S1Rank's question reproduces S1Rank within 0.5 on four of five collections (1.5 below on TREC-COVID). (Sec. 4)

## Results
Averaged over ten collections: reranker fine-tune beats the better decision mode on every backbone from 0.6B to 9B by 5.2 (Prism-9B 59.0 vs Clef-Flash 53.8) to 28.8 points (Qwen3-Reranker-0.6B 56.1 vs Kev-0.6B 27.3); significant on 48 of 60 pairs by paired t-test over queries with Holm correction, never significantly in favour of the decision fine-tune; Ours-9B 59.4 matches Prism-9B 59.0. At 27B they tie (Ours-27B 59.6 vs Kev-27B 60.1; Clef 54.8 joint). Up to 9B decision fine-tunes sit within -2.5 and +0.7 points of the untuned model. Jev (1.13.0, joint) averages 59.1, level with Qwen3-Reranker-8B 59.4 and the Set-Encoder 59.0; Laya isolated 43.5 equals BM25 43.2. Joint mode costs Kev-0.6B 12.2 and Kev-8B 13.0 points. (Sec. 5, Tables 1, 2)

## Cost and latency
Only Jev's mean API cost: 1.11 USD per 1,000 queries (Table 2). No latency or hardware reported for local models.

## Calibration
ECE with 15 equal-width bins and Brier on judged TREC DL pairs. Asked the authors' question: Jev 0.075, Kev-27B 0.076, Kev-8B 0.113 vs Qwen3-Reranker-8B 0.257; untuned Qwen3-8B 0.231, so the advantage partly comes from the question wording. With S1Rank's wording Jev joint ECE is 0.224 and decision models lose the advantage. Fixed cutoff p>=0.5: Jev F1 54.7, regret 1.7; a reranker fine-tune keeps the better set up to 9B. Count test: Jev 6.3 passages mean absolute error versus 8.6 for the median guess. Post-hoc: temperature and Platt scaling fitted on 1,000 MS MARCO dev queries applied to reranker fine-tunes only; Platt backfires (F1@.5 8.1 or less). (Sec. 4, 6, Tables 3, 4)

## Cascade or escalation
None.

## Robustness
Question-wording ablation (Table 4): ranking changes by -2.5 to +2.6 nDCG@10, calibration changes severalfold (ECE up to 0.152 for Qwen3-8B). No option-name or cardinality tests (binary yes/no only), no language tests.

## Code and data
Code, model outputs (a probability per query and passage) and all results public at https://github.com/KanishkaGD/decision-rerank (footnote 1).

## Authors' limitations (Sec. 7)
Released models differ in training data as well as objective; results describe decision fine-tuning as available today, not RLCD; controlled comparison rests on own reranker fine-tunes at 9B and 27B trained once with one recipe; calibration measured only on TREC DL at one grade and one threshold; question fixed before runs but only one other wording tried; all decision models at most a month old.
