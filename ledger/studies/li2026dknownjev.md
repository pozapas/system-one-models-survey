# li2026dknownjev — DKnown-Jev: Fine-Tuning and Evaluation of a JEV-Style Model for Tasks Involving Normative Knowledge

arXiv:2610.24358v1 [cs.AI], 17 Oct 2026. HTML retrieved 2026-10-28 (fulltext/2610.24358.html, .txt). Coder: batch V16.

## Authors and affiliation

Qi Li, Jianjun Xu, Pingtao Wei. Beijing Caizhi Tech, Beijing, China (liqi@czkj1010.com). Industry. Own-model paper; license CC BY-NC-ND 4.0.

## Task and data

Binary classification of normative usability of a candidate paragraph for a user question: Answer Evidence (AE) vs Non-answer Evidence (NE), from the question and its conditions, article metadata, and the paragraph (§3). Training: 26,064 human-verified records (11,788 AE, 45.23%; 14,276 NE, 54.77%) (§4.2, Table 2). Test: a fixed set of 1,120 human-verified examples (378 AE, 742 NE), policy and public-service questions (abstract, §5.1). Language of the data is not stated (likely Chinese; field names "translated from descriptive Chinese", §3.3).

## Models evaluated

Commercial Jev (version not reported; initialization source "Not publicly confirmed", Table 3); DKnown-Jev A1 (2B, 1 domain epoch) and A2 (2B, 2 epochs) fine-tuned from Qwen3.5-2B; B1 (27B, 1 epoch) and B2 (27B, 2 epochs) from "Qwen3.8-27B" (model cards accessed 2026-10-13). Architecture: shared scalar scoring head over the last-position hidden state of each candidate prompt, softmax across candidates, LoRA on attention projections, loss = cross-entropy + 0.1 x Brier (§3.4). LoRA rank, learning rate and hardware are not reported in the text.

## Comparators and tuning parity

Jev is used as-is through its commercial service with no description of prompting; the DKnown-Jev models are fine-tuned on 26,064 in-domain records. Strong asymmetry (fine-tuned vs not tuned); the authors acknowledge the comparison "concerns complete configurations" (§6.1). Whether Jev received the same candidate definitions and metadata is not stated explicitly beyond "same 1,120 examples" and identical AE/NE scheme (§5.2).

## Reference labels

"Human-verified" labels for both training and test; the number of annotators, adjudication and agreement are not reported. Coded human_single.

## n, sampling, intervals

n = 1,120, class counts given; no confidence intervals, bootstrap or significance test. The authors note A1's gain over Jev is "only two additional correct predictions, which is insufficient to establish a stable advantage" (abstract, §6.1). Single run per configuration; the one vs two epoch comparison is "not directly generalizable".

## Test-set exposure

Test set appears private and domain-specific; no statement about overlap with training or with pretraining data, and no leakage check. Coded private.

## Cost and latency

None reported.

## Calibration and cascade

Brier term in the loss only; no ECE, reliability or temperature analysis; no cascade.

## Robustness

None (no option-order, language or cardinality tests). Class-level recall and confusion counts only (Table 5): Jev AE 89.95 / NE 94.07; B1 97.88 / 99.19; B2 99.47 / 91.51; A1 93.92 / 92.32.

## Code and data

None stated; data not released; models not linked.

## Own limitations (§7)

Single test set of 1,120 examples; decision boundary hard for definition-like paragraphs; applications weigh AE recall vs NE recall differently; no claim that more epochs lowers performance; scale and model family differ across configurations, so effects cannot be attributed to size alone.
