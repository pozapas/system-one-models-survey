# yang2026tuplebench — TUPLE-Bench: Evaluating and Mitigating Privacy-Utility Trade-offs in Typed Decision Models

arXiv:2610.23668v1 [cs.CR], 16 Oct 2026. HTML retrieved 2026-10-28 (fulltext/2610.23668.html, .txt). Coder: batch V16. Study key: `yang2026tuplebench` (first content word of the title is the benchmark name).

## Authors and affiliation

Yiqu Yang, Qiaoyuan Zheng (equal contribution), Yang Tian, Yu Fan, Elliott Ash. ETH Zurich (1) and The University of Hong Kong (2). Academic. Independent of all nine model vendors.

## Task and data

A privacy and utility audit of what typed decision interfaces release. TUPLE-Bench has 720 counterfactual pairs (1,440 worlds) across three synthetic domains (delivery, equipment service, IT operations), each with four authorized coarse categories T and sixteen protected fine mechanisms S (four per class); split 432/144/144 pairs (864/288/288 worlds), pairs kept together (§4.1). Cases are AI-generated; quality control by three LLM judges (Gemini gemini-3.1-pro-preview, Claude claude-opus-5, GPT gpt-5.6-sol) in three stages, repaired until every pair passed (§4.3, App. B.4). Two experiments. (1) Refusal probe: sixteen mechanisms plus "withhold" listed; measures label-level compliance and recovery by direct selection or residual scores, 1,440 valid responses per model (Table 2). (2) Coarse-to-fine audit: model chooses only among four coarse candidates; five release views (no output, choice, choice+confidence, full probabilities, full native) derived from the same saved response; a supervised secret-inference decoder (closed-set, two hypotheses, 50% chance) per system, domain and view; three downstream tasks (selective routing, one-step clarification, asymmetric-cost routing) with authored costs (§5). Proposed mitigation WCPQ (workflow-constrained privacy quantization) evaluated on TypeSafe, OpenJev, Clef (§6, §7.5).

## Decision models and versions (Table 9)

TypeSafe jev-1.13.0; OpenJev openjev-0.1; JevK5 jevk5-0.2; Clef; Clef-flash; Perplexity Decider pplx-decider-v1.1-27b; Sage levanto-sage-v1.3; Liquid d1; Mercury Decide inception/mercury-decide-20260930. Identifiers are "recorded response versions, not claims about a system's latest release". Docs accessed October 2026 (some October 11). Seed 20261009 is a construction seed, not an API seed; no temperature or seed set on the calls (E.1); one saved response per world.

## Comparators and parity

Nine models compared on identical typed requests (JSON body with model, state, questions); providers differ (TypeSafe AI, Codiv, Cloudflare Workers AI, Perplexity, Levanto, Liquid, OpenRouter), with service-default decoding and no retries (Table 10, E.1). Parity: same prompt across all. WCPQ is compared with independent probability-field defenses (quantization 0.1, temperature smoothing tau=2, Gaussian noise sigma=0.05, top-two) using the same decoder protocol (Table 3).

## Reference labels

Synthetic: AI-generated worlds with registered protected mechanisms; authored cost units (wrong route 10, trusted review 2, clarification check 0.4). Decoder attacker given the authorized T and the two hypotheses (strong prior; limitation).

## n, sampling, intervals

288 test worlds per model for the coarse-to-fine audit (144 pairs); 1,440 responses per model for the refusal probe. 95% pair-clustered bootstrap, 2,000 resamples; intervals condition on fixed decoders and responses and exclude refitting and selection uncertainty (§5.4, Limitations). Paired non-inferiority tolerance delta = 0.1 cost units. Whole-dataset refusal rates carry no intervals.

## Test-set exposure

New synthetic benchmark generated for this paper (construction seed 20261009); no training-contamination concern for labels, though LLM judges with unknown relations to the evaluated models were used.

## Cost and latency

Authored benchmark cost units only (utility). No API cost or latency reported in the text read.

## Calibration

Calibration not assumed: "We do not assume that either is calibrated" (§3); confidence semantics vary across providers (Limitations). The paper shows confidence fields raise recovery without consistently lowering cost (TypeSafe selective-routing cost 0.278 to 0.285 with choice+confidence).

## Cascade or escalation

Selective routing (route automatically or pay for trusted review) is a downstream policy: TypeSafe full native raises automatic coverage from 87.85% to 94.79% and cuts clarification frequency from 27.08% to 15.28% (§7.3). Full native lowers cost vs choice in all 27 model-task comparisons by 9.52 to 75.68% (§7.3).

## Robustness

Hypothesis-order and attacker-input checks (App. F.1); six cost-profile sensitivity (F.2); sixteen mechanisms vs two-hypothesis tasks not comparable (§7.1). No language, option-name or cardinality tests.

## Code and data

Artifacts on Hugging Face and GitHub (links in the title block; URLs not captured in the extracted text); license in App. K.

## Own limitations

Synthetic AI-generated cases and authored costs; strong attacker prior (known T and H); few domains; automated checks do not establish semantic validity or statistical independence across pairs; one saved response per world so repeated-call variability unmeasured; intervals exclude refitting uncertainty; passive closed-set attacks only; recovery reflects the attacker library, not a confidentiality guarantee; idealized checks and constructed costs.
