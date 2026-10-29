# antunes2026narrow — Narrow Decision Models: A System-1 Architecture for Calibrated, Typed Decisions

arXiv:2610.25553v1 [cs.AI], 18 Oct 2026. Full text: fulltext/2610.25553.html and .txt (arXiv HTML). Primarily an architecture and protocol paper; Section 10 is a "minimal validation".

## Authors and affiliation
Carlos André Antunes, Aldry Albuquerque, Gabriel de Melo Schmith, Natã Batista, Pedro Oziel Escobar da Silva, Stefano Benko Rossi, Lingrid Dietrich Lorenz da Silva, Flávia Cristina da Costa, Thiago Bertotto, Luis Fernando Fausto, all Softplan (title block). Affiliation type: industry. Authors used Claude to draft text, implement code, produce figures, and to draft the synthetic seed material, which has not been reviewed by a domain expert (Sec 10, Use of generative AI).

## Task and data
Own architecture: Narrow Decision Model, NDM-Block, a ModernBERT/mmBERT bidirectional encoder over a prefix-tree serialization with block attention mask and logical positions, so that option-permutation invariance and question isolation hold by construction (Abstract, Sec 4). Running case: routing Brazilian court communications. Validation data: public Portuguese intent datasets (MASSIVE, Banking77 test splits, n=2,974 and 3,080), four fictitious organization charts (165 communications), synthetic selection partition (905 Choice questions, 627 with abstention), and one real-data run on about 840 thousand legal documents with a 9,092-document held-out test (Sec 10.1 to 10.6). The real-data evaluation is deferred to a companion paper.

## Decision models evaluated
ndm-base = mmBERT-base through training stages 0, 1 and 2a; no release identifier or checkpoint link (Sec 10). NDM-Pair (pairwise cross-encoder) is the architecture ablation (Sec 10.5). Hosted Jev is described but not measured; the paper cites an independent Jev comparison [33] only in the introduction.

## Comparators and tuning parity
Lexical retrieval BM25, first-option baseline, fallback-to-parent baseline; Qwen3-0.6B-Base scoring options by log-likelihood for the option-order test; TF-IDF plus logistic regression trained on the same real-data split; NDM-Pair at equal padded-token budget, three seeds per arm (Sec 9, 10). Block and pair see different numbers of questions at equal compute (about 27,600 vs 4,300).

## Reference labels
Public intent labels (human); synthetic labels for fictitious charts and the selection partition; real-data labels are those of the production LLM-based classifier, so the measure is agreement with that classifier, not accuracy against human annotation (Sec 10.6).

## n and intervals
Bootstrap intervals over communications or scenarios (Sec 9 states bootstrap over scenarios for the pre-registered protocol); public datasets: 95% bootstrap intervals within +/-0.02 (Table 3). Real run: one run, bootstrap over cases for the difference in agreement (+1.0 point, [0.2, 1.9]) (Sec 10.6).

## Test-data exposure
Public intent datasets in Portuguese (pre-2026 sources); fictitious charts new; legal documents private. Seed material for synthetic data was drafted with a language model (Sec 10).

## Cost and latency
State encoding 6.5 ms at 256 tokens and 59 ms at 4,096 tokens, extra cached question 0.8 to 4.9 ms; all measurements in 49 minutes on one RTX PRO 6000; real-data fine-tuning 50 minutes on one A100 (Sec 10.1, 10.6). No monetary cost and no hosted-model latency comparison.

## Calibration
Temperature scaling per question type; Choice ECE 0.188 to 0.033 on the selection partition (binning not stated); Noul ECE worsens from 0.012 to 0.030; a synthetic temperature raises NLL on public data (Sec 10.3). Real run: ECE 0.011 vs 0.053 for TF-IDF baseline (Sec 10.6).

## Cascade or escalation
Abstention via explicit none-of-these option, adequacy head, and parent fallback; hierarchical descent with greedy, beam and exhaustive search (Sec 6, 10.4). Explicit abstention AUROC 0.79, recall 0.25, false alarms 0.025.

## Option-name, cardinality, robustness tests
Option permutation: argmax unchanged on 905 questions, largest probability change 1.9e-6, vs a decoder that changes 41% of answers (Sec 10.1). Cardinality: accuracy falls slowly from K=4 to K=60/77 (Table 3). Abstention paraphrase robustness and robustness to context additions are untested (Sec 12). Language: Portuguese data.

## Code and data availability
No repository or checkpoint link found in the text. Data are partly private (court documents).

## Authors' limitations (Sec 12)
Synthetic-to-real gap; rubric quality; compounding depth errors; calibration under shift; state-content robustness untested; floating-point tolerance; fixed abstention wording; empirical thresholds; narrow by design; only text states exercised; not a reasoning system.
