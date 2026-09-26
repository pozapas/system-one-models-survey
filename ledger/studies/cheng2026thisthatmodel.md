# cheng2026thisthatmodel — this-that-model-1.0: A typed decision model that decides in 30 ms, for a millionth of a cent

arXiv:2609.23886v1 [cs.CL], submitted 20 Sep 2026. HTML retrieved from https://arxiv.org/html/2609.23886v1.

## Authors and affiliation

Zehua Cheng (University of Oxford and FLock.io), Wei Dai (FLock.io), Jiahao Sun (FLock.io); correspondence ai@flock.io. Mixed academic/industry author list (one author dual-affiliated with a university, two with an industry lab) — coded affiliation type **mixed**.

## Task and data

Introduces and evaluates **this-that-model-1.0**, a 2B-parameter (1.88B exact, §1) typed decision model whose answer is read directly from the hidden state at a designated position (softmax over declared option-label tokens only, Eq. 2), never generating free text. Three evaluations:
- **§4.1** — a third party's (NanoJev's) recorded cohort of 68 local-geometry decision questions over 17 states, with the hosted Jev service's replies already captured; this-that-model-1.0 and 9 hosted LLMs are scored on the identical recorded inputs (Table 1).
- **§4.2** — a stochastic-actuator environment where the true answer distribution q is *computed* (not sampled) from a known reliability parameter ρ, allowing calibration to be checked against ground truth rather than only against a sampled label (Eq. 12; Table 2), plus a "context ladder" (windowed vs. whole-map state) run identically across 10 hosted systems (Figs. 4–5).
- **§4.3** — an internal 7,305-question, 15-family, two-environment benchmark built and released by the authors (`this-that-spatial-bench`), each answer computed by a simulator rather than annotated; scored zero-shot by 9 hosted LLMs, Jev (run by a third party on the authors' behalf — the authors "hold no key for that endpoint"), and this-that-model-1.0 (in-distribution: trained on all 15 families, though on different items/maze windows than the eval set) (Table 3).

## Decision models evaluated

- **this-that-model-1.0** (the paper's own model) — adapted from `decider-2b` (Apache-2.0 public typed-decision checkpoint/inference stack); a full-parameter fine-tune shipped as a single interpolation scalar λ=1 (§3.4); released at https://huggingface.co/flock-io/this-that-model-1.0 (MIT), code at https://github.com/FLock-io/this-that-model. No explicit dated version string beyond "1.0"; `version_pin` recorded as the model name plus base checkpoint.
- **Jev** — the hosted TypeSafe commercial service. Critically, *the paper's authors never called Jev directly*: the 68-question comparison (Table 1) reuses NanoJev's already-published Jev replies, and the 2,250-question benchmark comparison (Table 3, marked †) was "run for us on the released benchmark ... by a third party," because "we hold no key for that endpoint" (§4.3, Conclusion "Against Jev"). This materially affects `version_pin`/tuning-budget parity: no version string for Jev is given anywhere in this paper.
- **NanoJev-0.6B** — an open 0.6B reproduction of the typed-decision interface (MIT), used as a baseline in Table 1 only; not timed by the authors (blank cost/latency cells).
- Nine to ten hosted frontier LLMs as generative comparators across the three studies: claude-fable-5-1, glm-5.3, qwen3.8-max, kimi-k3, deepseek-v4.1-flash, gpt-5.6, claude-opus-5, claude-sonnet-5, gpt-5, deepseek-v4-pro (composition varies slightly by table).

## Reference labels

All three evaluations use environment-computed or simulator-computed ground truth rather than human/LLM-teacher annotation — coded `task_outcome` throughout (per the paper: "Ground truth is computed from the environment rather than annotated, so the top of the scale is exact rather than nominal," §4.1; "every answer computed from the simulator rather than annotated," §4.3).

## n, sampling design

68 questions / 17 states (Table 1); stochastic-actuator and local-geometry question sets of unspecified exact n (Table 2, "9 hosted systems and this-that-model-1.0 on identical questions"); 7,305-question / 15-family / 6,525-state internal benchmark (§4.3), with a 2,250-question equal-per-family identical subset (Table 3) and a 60,200-question fresh retraining set fingerprinted (sha256) against 97,133 training questions to rule out contamination.

## Test-set exposure

All three evaluation sets were newly constructed or newly recorded for/around this paper (2026) — coded `new`. The authors explicitly flag an in-distribution asymmetry in Table 3: this-that-model-1.0 was trained on all 15 families of its own released benchmark (different items/maze windows, but the same question shapes), whereas "every hosted system met these fifteen question shapes for the first time at test" — "a real product fact and a weak scientific one" (§4.3).

## Cost and latency

Hardware: this-that-model-1.0 runs on "one 16 GB laptop GPU" (Table 1 caption; electricity costed at 80 W, $0.30/kWh); comparators are hosted APIs. Headline numbers: 30.9 ms per decision, 32 decisions/second sustained on one consumer GPU, zero generated output tokens (Abstract, §1). Cost of one 68-question pass: this-that-model-1.0 $0.000014 (electricity only) — Jev's per-pass cost is not measured by the authors (blank cell, Table 1); Jev's *published* per-token rate ($0.042/million input tokens, output free) and claimed 70–500 ms end-to-end response are quoted from the vendor's own materials, not independently measured (Conclusion "Against Jev"). Internal-suite pass: this-that-model-1.0 32 s / $0.000217 vs. "the most accurate hosted model we measured" 155.2 minutes / $10.636 (Abstract).

## Calibration analysis

Brier score reported for this-that-model-1.0 and any hosted endpoint that exposes token probabilities (Table 1: 0.042 vs Jev's 0.133; a dash where an endpoint returns no token probabilities — "not that [Brier/NLL] are poor," just unobservable, §4.1 caption). No ECE/binning analysis; instead the paper uses the *computed* ground-truth probability q (Eq. 12) to score squared distance to true probability (q L2, Table 2) — a stronger calibration test than binned ECE against sampled labels, and the paper explicitly derives (Eq. 13) why a single Brier number on sampled labels cannot say how far a model is from truth in absolute terms. No post-hoc recalibration (temperature/Platt/isotonic) is applied to this-that-model-1.0; its probabilities are trained directly against a convex combination of cross-entropy and Brier loss (§3.3).

## Cascade / escalation results

None — this is a single-model deployment paper, not a routing/cascade paper.

## Internal consistency note (table vs. body text)

Like `jiang2026jevmem`, this paper has a small table/text discrepancy on the stochastic-actuator calibration result. §1 (Abstract-adjacent) and §5 ("What the measurements actually support") both state the model "lands at 0.750 against a ceiling of 0.746 that no predictor can exceed," but Table 2 lists this-that-model-1.0's stochastic-actuator **accuracy** as **0.745**, not 0.750 (the accuracy ceiling row itself is correctly 0.746 in both places). The ledger's `thisThatStochasticActuatorQL2` row (`parts/ledger_B.csv`) uses the Table 2 value (0.745) as `value` since it is the calibration-relevant q_L2 row, not the accuracy figure the 0.750/0.746 sentence describes — but the curators should note this ±0.005 inconsistency if pooling this number.

## Option-name / robustness stress tests

Extensive surface/format robustness testing in §4.3: the internal benchmark renders the same maze window three ways (ASCII block / JSON / prose) at random within each family. Before the targeted retraining round, this-that-model-1.0 was "at chance when the same maze window was written as JSON" (0.373 vs 0.394 chance); after retraining, JSON rises to 0.936 (from-chance to near-ceiling), matching ASCII (0.779) and prose (0.942) — table reproduced in Section 4.3, "What that training fixed, it fixed completely." A targeted second training round "improved the five task families it was written for and transferred to none of the other 13" (Abstract) — i.e., no cross-family transfer. A search-vs-lookup robustness probe (§4.3, "The same quantity, asked two ways"): on 300 mazes, asking for the same shortest-path distance as a 5-way band (trained readout) vs. as an even/odd parity (an unseen readout) shows the model gets the band right but is at chance (0.513 vs 0.500) on parity when the band is right — evidence the model recognizes a picture-like band rather than computing the underlying distance.

## Code and data availability

Model weights: https://huggingface.co/flock-io/this-that-model-1.0 (MIT). Inference code and reproduction scripts: https://github.com/FLock-io/this-that-model. Released benchmark (7,305 questions, 6,525 states): https://huggingface.co/datasets/limberc/this-that-spatial-bench (MIT). `code_available = yes` throughout this paper's rows.

## Paper's own stated limitations

Stated directly in the Abstract/Conclusion rather than a separate limitations section: "it is not a claim to be more accurate than a frontier model: on the harder half of our suite it is not, and on a benchmark we built and released for this paper it is the least accurate system we measured" (§1). The 68-question Jev comparison rests on "a small cohort," "wording [that] is theirs rather than ours," and "an accuracy gap of 18 percentage points [that] rests on 12 questions" (Conclusion). The Table-3 Jev comparison is "not a clean one, because we trained on these fifteen question shapes and it had no reason to" (Conclusion). Search-requiring families (first_move, reachable_within, distance_band — 21% of the released benchmark, mean 0.574) remain unsolved by one forward pass and "no amount of data of that shape moved it" (§5, "What does not").

## Notes on seed claims (see also parts/seed_check_B.csv)

- "2B" parameter model: **confirmed** (abstract states 2B; body text gives the more exact 1.88B — not a contradiction, a rounding).
- Hidden-state readout (no generated text): **confirmed** verbatim (§1, Eq. 2).
- 30.9 ms decision latency: **confirmed** exactly (Abstract, §1, Table 1).
- this-that-model 0.941 / Brier 0.042 vs Jev 0.765 / 0.133 on the third party's 68 questions: **confirmed** exactly on all four numbers (Table 1) — but note the Jev numbers were measured by NanoJev, not by this paper's authors, which bears on the seed's implicit framing of a head-to-head "measurement" and is called out in the ledger's `comparator_tuning_budget` field.
- Fails multi-step arithmetic, scoring 0.560: **confirmed** exactly, against a stated hosted-model range of 0.98–1.00 (Abstract).
