# li2026beyond — Beyond Calibration: Do a Typed-Decision Model's Probabilities Obey the Probability Axioms?

arXiv:2609.33209v1 [cs.CL], 27 Sep 2026 (header). HTML retrieved 2026-10-28 from https://arxiv.org/html/2609.33209; saved as fulltext/2609.33209.html and .txt.

## Authors and affiliation

Keyi Li, Yihao He, Quanyi Li; Software College, Northeastern University, Shenyang, China (title block). Affiliation type: academic. (Key `li2026beyond` does not collide with existing `li2026fast`, `li2026jevasajudge`, `li2026kite`, `li2026replacing`.)

## Task and data

Label-free probabilistic coherence battery for typed decisions (§3). 160 items: 100 NLI items sampled from the 1,599 ChaosNLI items (built on MNLI) with entropy of 100 human labels per item, and 60 PubMedQA expert-labelled items (20 per final decision), conclusion paragraph withheld, answers renamed affirmative/negative/inconclusive (§4 Materials). Each item has a three-label partition; ten questions per item: S_k (label is X_k), N_k (label is not X_k), D_k (label is X_i or X_j), and one choice question (§3). 480 negation pairs (160 items x 3 labels). English, two domains. Nineteen of the 60 PubMedQA items belong to the public Jevals suite, reported separately (§4, Table 2).

## Decision models evaluated

- Jev: `typesafe/jev-1.13` through OpenRouter's decisions endpoint; "All 3,360 responses report the same version, jev-1.13-20260917"; each request repeated once a few minutes after the first pass; two-decimal probabilities; also a bundled request with all ten questions under opaque identifiers (§4 Systems). No calendar run date given.
- Qwen3.8-27B, official BF16 weights (mirror, hashes identical to Hugging Face), vLLM 0.19.1 on two RTX A6000 GPUs, thinking disabled, two readouts: first-token probability (normalised over yes/no or option letters among top 100 tokens) and verbalized JSON probabilities (collected for the 960 S_k and N_k questions only) (§4 Systems). The first-token readout is one forward pass over the declared answer set, so it is treated as a typed-decision readout of a general LLM.

## Comparators and tuning-budget parity

Same state, definitions and question text for both systems, preceded by a short system prompt for Qwen (Appendix A, per §4). No tuning or few-shot on either side stated. Comparator budget: same prompt.

## Reference labels

The coherence checks use no gold labels (label-free; §3). The only label-based check is that the top-scoring label matches the reference label in 63.8% of items for Jev and 56.3% for Qwen (§5.2); references are ChaosNLI majority labels and PubMedQA expert labels (type: human crowd for NLI, human expert for PubMedQA).

## n, sampling, intervals

160 items, 480 pairs. Percentile intervals from a paired item bootstrap stratified by domain, 5,000 resamples, seed 0; sign-flip permutation test with 10,000 permutations; correlations bootstrap over pairs or items (§4 Protocol). Items sampled with fixed seeds; option order of the choice question cycles through six permutations (§4). Repeat noise floor from asking every Jev question twice (Eq. 3).

## Test-set exposure

ChaosNLI/MNLI and PubMedQA are public pre-2026 datasets. "Both datasets are public, so memorization cannot be excluded, although the Jevals-suite items behaved like the others" (§7). 19 PubMedQA items are in the public Jevals suite on which Jev may have been evaluated or tuned (§4).

## Cost and latency

Jev calls cost US$0.076 in total for 3,360 calls (§4 Protocol). No latency reported.

## Calibration

No ECE or Brier. The paper argues coherence differs from calibration; a label-free decomposition by question form (Table 4) measures "calibration-in-the-large" errors, for example Jev's S_k mean probability 0.380 against target 1/3. Jev outputs lie on a two-decimal grid in [0.01, 0.99] (§6). No recalibration.

## Cascade or escalation

None evaluated. The paper notes that thresholds on P(yes) and expected-cost rules motivate coherence (§1).

## Option-name, cardinality, language and robustness tests

Robustness checks of the Jev-versus-Qwen gap (Table 2): confidence-matched pairs, removal of double-negation labels, averaging repeats, unrounded Qwen probabilities, logit scale. Bundling versus single requests (§5.3). Option order cycles through six permutations (§4). English only; three-label partitions only (§7).

## Code and data availability

Stimuli, raw request and response logs, analysis code and table/figure scripts at https://github.com/bro789/typed-decision-coherence (Data and code availability).

## Limitations stated by the authors

Small by design (160 items, 480 pairs, two English domains, one wording for negation and disjunction, no paraphrase control); per-label and subset estimates rest on 19 to 100 items; one comparison LLM with thinking disabled; one Jev version through one gateway; public datasets so memorization cannot be excluded; coherence is necessary but not sufficient (§7).
