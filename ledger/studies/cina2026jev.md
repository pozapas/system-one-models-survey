# cina2026jev — Jev Matches 7B Language Models for Speech-Neuroprosthesis Rescoring

arXiv:2609.33538v1 [cs.CL], 27 Sep 2026 (header). HTML retrieved 2026-10-28 from https://arxiv.org/html/2609.33538; saved as fulltext/2609.33538.html and .txt.

## Authors and affiliation

Gabriele Cinà, a Gmail address and no stated institution (title block). Affiliation type: independent.

## Task and data

Rescoring the 100-best candidate sentences of a speech neuroprosthesis decoder (Brain-to-Text benchmark, participant T15 with ALS, 256 electrodes). The published Kaldi decoder with an OpenWebText 3-gram produced 100-best lists for the 1,397 validation sentences (oracle word error 2.5%, truth in list 89%). A seeded split gives 419 development and 978 test sentences; lists are cached so all arms score identical candidates (§4). Typed rescoring: the whole list is sent once, candidate h_i under label i, and the model returns a distribution over labels, scored as r(h_i) = log max(p_i, 1e-6) (§3). Combined with the decoder score by z-standardised interpolation with weight alpha (Eq. 2).

## Decision models evaluated

- Jev, `jev-latest` in September 2026, via the hosted API, one Choice request per list (§4 Arms, Appendix A). The text states "our results are for jev-latest in September 2026" (§5.4). No exact version string (such as jev-1.13.0) is given.
- Laya, "an open 421M typed-decision model", same request as Jev (§4, Table 3).
- Controls: OPT-6.7b and Qwen2.5-7B given the same task as a text prompt, reading each label's next-token probability; and as per-candidate likelihood scorers, each candidate scored as a standalone sentence on one NVIDIA L40S in bfloat16, batches of 32 (§4).

## Comparators and tuning-budget parity

Every arm is untuned apart from the interpolation weight: alpha tuned per arm over 21 values in [0, 1]; under the re-tuned protocol the acoustic weight lambda is searched jointly over 17 values in [0, 5]; both on the development split only, test scored once (§4 Tuning). Statement: "Every arm here is therefore untuned, Jev included" (§2). Same decoder, same candidates; budget parity is good. The matching margin of 0.2 points was fixed after seeing the results (§4, §5.4).

## Reference labels

The sentences the participant attempted to say (benchmark transcripts); word error rate is corpus-level Levenshtein distance over words (jiwer 4.0) (§4 Statistics). Reference type: task_outcome (cued target sentences).

## n, sampling, intervals

978 test sentences, 419 development; percentile bootstrap over sentences (2,000 resamples) for marginal intervals; one-sided paired bootstraps (5,000) with Holm correction over three arm-versus-baseline tests per protocol (§4). Paired Jev-versus-7B differences in Table 2.

## Test-set exposure

Brain-to-Text benchmark data; benchmark date not stated in the text. "83 test sentences also occur, as text, in the phoneme network's training split, a property of the benchmark; excluding them changes no conclusion" (§5.4). Jev has no access to neural data, only the candidate text; text may nonetheless be public.

## Cost and latency

Jev list price $0.042 per million input tokens, no output charge; mean 1,631 input tokens per list (95% CI 1,398 to 1,868) read from the usage field of 140 random test lists, giving $0.069 per 1,000 sentences (Table 4). OPT-6.7b on an on-demand L40S at $1.82 per hour: $0.029 per 1,000 sentences at full utilisation, $43.68 per day dedicated; break-even above 43% utilisation, about 640,000 sentences a day (§5.3). Latency per list from one data centre in Finland: Jev median 282 ms, p95 346 ms; OPT-6.7b 27 and 134 ms; Qwen2.5-7B 32 and 158 ms (Table 4). From London on 80 lists: 262 ms end to end for a full list, 253 ms for a two-option request, provider proxy 62 ms (p95 102 ms) (§5.3).

## Calibration

No ECE or Brier; probabilities are used as log scores. No recalibration. Abstract describes Jev as "a hosted model trained for calibrated decisions."

## Cascade or escalation

None.

## Option-name, cardinality, language and robustness tests

Position bias is discussed: open general models "favour positions over contents" and place answers on the decoder's top candidate label A; Table 3 shows label usage (Jev 57 of 100 labels, share on A 72%). Permutation self-consistency was tried on an earlier decoder and did not beat the top candidate (§2). Candidate order is the decoder's order; no option-order shuffle for Jev. One prompt wording only (§5.4). English only.

## Code and data availability

Cached lists, per-arm scores, latency logs and code at https://github.com/gabrycina/how-much-language-model (footnote 1). Jev itself is hosted and not reproducible (§5.4).

## Limitations stated by the authors

One closed model; post-hoc margin; one participant with limited power; cloud dependence and privacy; one prompt wording (§5.4).
