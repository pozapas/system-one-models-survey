# Kwartler, Aqrawi & Abbasi (2026), "Harness Tokenomics: A Router for the Enterprise Agentic Control Plane"

## Identification
- arXiv 2609.28919v2 [cs.AI], v2 dated 26 Sep 2026 (header); first version date 2026-09-24 per sweep list. License CC BY-NC-SA 4.0. Full text fulltext/2609.28919.html and .txt (the saved copy is v2).
- Authors Ted Kwartler (Accenture; Harvard Faculty of Arts and Sciences), Alan Aqrawi (Accenture), Arian Abbasi (Accenture) (byline). affiliation_type = industry. Paper includes an Accenture disclaimer that spend and prices do not represent Accenture's own.

## Task and data
- Cache-safe model router for AI coding-agent harnesses; Jev labels each prompt against a four-axis bring-your-own taxonomy (action 13 labels, domain 12, ordinal complexity trivial to expert, history dependence) plus a correction flag (Sections 4.5, 4.6; Appendix A). Policy moves a turn only when Jev's calibrated probability that a cheaper tier suffices and that the turn is history-independent clear a threshold (base 0.8).
- Emulation (Section 4.9): authored catalogue of 46 conversations, 109 turns, 11 job types, ground-truth tags by the authors alone; each conversation expanded into 200 Monte Carlo variants using behaviour from about 10,000 real Claude Code sessions in two public corpora (TraceLab, SWE-chat); cache-exact cost simulator at Anthropic list prices of 21 Sep 2026 (OpenAI, Google 23 Sep 2026); 10,000-seat, 14-segment population.
- Headline: routed spend saving 13.4% with Jev labels and 20.8% with perfect labels; $3.3M to $5.1M a year (Section 5.1; Table 3).

## Decision model
- Jev, "model string jev-1.13.0" verified live (Section 4.6). No call dates; vendor description cited from TypeSafe blog and documentation. Classifier-agnostic interface; self-hosted encoder named as fallback.

## Comparators and tuning parity
- No alternative classifier is run. Comparator is a perfect-label oracle and the pinned (no-router) and naive-switch policies in the cost simulator. Threshold 0.8 chosen as base; the authors state choosing the best tested threshold (0.9) on this corpus "would tune on the test set" (Section 5.4).

## Reference labels
- Ground-truth tags written by the authors alone, no inter-rater agreement, "no ablations" for the taxonomy (Limitations, Section 8). reference_label_type = human_single.

## n, sampling, intervals
- Classifier accuracy on 109 turns: action 74%, domain 80%, complexity 63%, history 82% (Section 5.3; Table 3). No confidence intervals on accuracy or on the savings; savings reported as a band between today's labels and perfect labels. Monte Carlo variants are not independent test items.

## Calibration
- Calibration is relied on by the policy but not measured on the 109 turns. The only calibration figure is a cited independent test [46] (not ledgered here to avoid double counting with that source): 60 hand-labelled agent tool-call risk cases, 91.7% accuracy, "calibration error near 0.07", median latency about 420 ms (Section 4.6), secondary report. No binning stated, no recalibration.

## Cost and latency
- Own timing of all 109 catalogue prompts from a laptop over the public internet: median 250 ms, at most 366 ms once connection open, first call 0.7 s (Section 4.6). Classifier cost about $179 a month for 1.3 million routed turns in the emulated enterprise; router overhead $5k a month (Section 5.2). Vendor-reported: 70 to 500 ms end to end, about $0.04 per million input tokens, output free (Section 4.6, from TypeSafe).

## Cascade or escalation
- The policy is a confidence-gated hold: 42% of routable turns held, 12.5% of moved turns are false downgrades; threshold 0.5 gives 10% saving, 0.8 gives 13.4%, 0.9 gives 13.7% while holding half of routable turns (Sections 5.3, 5.4). Corrections never moved down (rule R10); classifier flagged every generated correction.

## Option-name, cardinality, language, robustness
- Sensitivity of saving to cache lifetime, price sheet, agentic intensity, threshold (Section 5.4; Table 8, Figure 9). No option-name or language tests on Jev.

## Test-set exposure
- Authored private scenarios; new.

## Code and data
- "The authors' simulator, scenario catalogue and cached classifier labels are not released" (Reproducibility, Appendix B Reproduction). Taxonomy and cost model specified in Appendices A and B.

## Paper's own limitations (Section 8)
- Synthetic scenarios with author-only tags; taxonomy still in development (complexity levels least crisp, cause most holds); session shape; usage intensity; scale; non-engineer model choice; two developer-only corpora; list prices only; prices move; other vendors' ceilings assume equal quality.
