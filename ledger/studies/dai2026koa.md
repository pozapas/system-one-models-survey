# Dai, Pentyala, Liu, Mehrotra, Banerjee, Zhu, Bi, Asur & Mui (2026), "Koa-decision: Fast and Consistent Structured Decision Making with Generative LLMs"

Coder: batch V04. Full text: fulltext/2609.36115.html and .txt. The text read is arXiv **v2** (10 Oct 2026); the first public version is 2026-09-28 (batch file). Whether Jev appeared in v1 was not checked; the Jev rows come from v2.

## Identification
- arXiv 2609.36115v2 [cs.LG]. Footnote: "An earlier version of this work was made available on OpenReview in September 2025."
- Authors (9): Shenghong Dai (Salesforce AI and University of Wisconsin-Madison), Shiva Kumar Pentyala, Yingchi Liu, Shubham Mehrotra, Suman Banerjee (University of Wisconsin-Madison), James Zhu, Bin Bi, Sitaram Asur, Phil Mui (Salesforce AI) (author block). Affiliation type: mixed.

## Task and data
- Single-token (atomic label token) classification for latency-critical decisions, framed as System 1 typed decisions (Introduction). Benchmarks: MIntRec 2.0 official test split (30 intents, text plus video; n not stated), SST-2 (872), Amazon Reviews Polarity (5k of the test set), a de-identified production intent-routing set (587 utterances, evolving label inventory, not releasable), a voice turn-taking / endpointing set (353 binary examples, described as synthetic), plus DBpedia, TweetTopic, Banking77, MTOP in Appendix B (Section 4.1).
- Test exposure: SST-2 and Amazon are public and pre-2026; intent-routing is private; voice endpointing is new/synthetic.

## Decision models
- Koa-decision: SFT of Gemma-3-4B/27B, Gemma-4-26B, Mistral-3-24B and GPT-OSS-20B with up to 500 reserved control tokens and randomized label-to-token assignment; the decision is the argmax of a restricted softmax over control tokens; multi-label supervision uses a soft target (Section 3). Checkpoint identifiers are "given with each results table" but tables name only model families and sizes. Training corpus described in Appendix E.
- Jev (TypeSafe): listed as "External evaluator (public + synthetic only)" in Table 2; "Jev is not run on the intent-routing set (internal data)". No version, no dates, no description of how Jev was prompted, and the text does not say who ran it or whether it went through the same serving harness; the Figure 3 caption implies it did for the voice-latency comparison. Jev cells were not produced under a stated parity protocol.

## Comparators and tuning parity
- Frontier panel zero-shot: GPT-4o, GPT-4.1, GPT-4.1-mini, GPT-5, Claude-4-Sonnet, Claude-5-Sonnet, Claude-4.8-Opus, Gemini-2.5-Pro, Gemini-Pro-3.1; prompts in Appendix G. Koa models are fine-tuned on a separate corpus and applied zero-shot to the evaluation sets ("all reported evaluation datasets are disjoint from any data used for adaptation", Section 4.1), except the MIntRec 2.0 models, which are trained on MIntRec 2.0 data ("fine-tuned models trained on the challenging MIntRec 2.0 dataset", Section 4.4.1). Encoder baselines (BERT, RoBERTa linear head, LM-BFF, MAG-BERT, MulT) are task-specific fine-tuned. Tuning asymmetry: Koa fine-tuned, Jev and frontier models zero-shot.

## Results
- Table 2 accuracy (%): SST-2: Jev 96.10, Koa Gemma-4-26B 95.76, Koa GPT-OSS-20B 92.89, Gemini-Pro-3.1 96.79 (best). Amazon: Jev 96.80, Koa 96.60 and 95.34, Gemini-Pro-3.1 97.42. Voice: Jev 93.20, Koa 94.33 and 96.90, best frontier Claude-4-Sonnet 97.17. Intent routing: Koa 81.43 (Gemma-4-26B) and 85.52 (GPT-OSS-20B), Claude-4.8-Opus 87.73, Gemini-Pro-3.1 87.05, GPT-4.1 86.03.
- Table 1 (MIntRec 2.0): Koa Gemma-3-27B 62.72, Gemma-3-4B 55.19, Mistral-3-24B 49.34; Gemini-Pro-3.1 55.93; MAG-BERT 60.58; MulT 60.66.
- Latency (Section 4.4.3, Figures 2 to 4): all models through one serving interface, one request at a time, round robin, end-to-end wall clock, no batching. Koa p50 0.53 s, p95 0.63 s on intent routing, 1.9x to 7.5x faster than the frontier panel at the median; on voice endpointing Jev p50 0.55 s, p95 0.69 s, Koa 0.53 s, frontier 0.98 to 2.88 s. Latency in Figures is read from captions; individual frontier medians are in figures only.
- Hardware for Koa serving and for Jev is not stated in the text beyond "our own vLLM-based inference framework" for batch scaling (Section 4.3).

## Sampling design and intervals
- Single evaluation per cell; no confidence intervals, no seeds, no repeated runs reported. Latency percentiles only.

## Calibration and cascade
- Koa's restricted softmax is described as giving a distribution, and the multi-label extension is said to give "calibrated probability mass", but no calibration metric is reported. No cascade.

## Robustness
- Label-set cardinality, model scaling, label-token remapping at inference and batch scaling are in Appendices D.1 to D.4 (not extracted). Jev is not part of those tests.

## Code and data
- No code or model release statement found; the intent-routing set cannot be released (Section 4.1 footnote).

## Authors' stated limitations
- No limitations section; the Conclusion lists extension beyond text and vision and multilingual generalization as future work.

## Coder notes
- Jev's SST-2 and Amazon accuracies are higher than the best Koa models and lower than Gemini-Pro-3.1; Jev's voice accuracy is below both Koa models. Rows report this as published.
