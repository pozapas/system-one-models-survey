# Madrid-Garcia and Merino-Barbancho (2026), "Jev in Medicine: A Benchmark Evaluation"

## Identification
- arXiv 2609.34024, read as v4 ("arXiv:2609.34024v4 [cs.AI] 10 Oct 2026", header); first public version 2026-09-27 per batch file. License CC BY 4.0. Abstract carries a NOTE that findings are preliminary, pending independent replication, clinical adjudication of reference answers and run-to-run stability checks.
- Authors: Alfredo Madrid-Garcia (corresponding) and Beatriz Merino-Barbancho, both "Independent researcher, Madrid, Spain" (byline). Conflict of interest: first author employed by Roche, work stated to be independent (Declarations). affiliation_type = independent.
- Data and code: Zenodo record 23008156 (code, dataset revisions, sample identifiers, preprocessing, shareable outputs); NEJM case texts not redistributed (Data availability). Generative AI (Claude Opus 5.5, GPT-6 Astra) used extensively for workflow, analysis and drafting (Generative AI statement).

## Task and data
- Four medical multiple-choice benchmarks, single Choice question per item (Section 2.2, Table 1): MetaMedQA 1,373 USMLE-style items, 6 options including "None of the above" and "I don't know or cannot answer", 277 without a correct substantive option; PubMedQA 500 expert-annotated test items, 3 options (conclusions removed from abstracts); DiagnosisArena-MCQ 915 publicly released cases, 4 options; NEJM Case Challenges 34 scored cases (35 retrieved May 2020 to September 2026, 33 with closed reader poll), 6 options, retrieved by personal subscription, figures replaced by captions, tables transcribed.
- Reference labels: the benchmarks' published answer keys, "reference answers were not re-adjudicated"; NEJM correct option matched by hand to the published final diagnosis (Section 2.2). Ledger codes as human_adjudicated (published expert keys, not re-adjudicated here).
- Exposure: public benchmarks published before the models; "data contamination cannot be excluded"; NEJM final diagnoses online; training data of neither model disclosed (Section 4.3). Coded public-pre-2026.

## Models and comparators
- Jev 1.13 accessed through OpenRouter, which forwards to TypeSafe; "Each model and condition was run once per benchmark, between 26 and 27 September 2026" (Sections 2.3, 2.4). The exact string jev-1.13.0 is not given; version pin "Jev 1.13 via OpenRouter". Used out of the box, one question per item, without the developer-recommended decomposition (Section 2.4).
- Comparator GPT-6 Sol (knowledge cut-off 20 April 2026) via OpenAI API at reasoning effort medium (primary) and none; output constrained by JSON schema to one option plus a verbalised probability per option; same instruction, content and options in one user message, no system prompt, no examples; "Prompts were not optimised" (Sections 2.3, 2.4). Tuning parity: same prompt, with the authors acknowledging GPT-6 Sol was run at two of its six effort levels with a single unoptimised prompt (Section 4.3). GPT-6 Sol probabilities are verbalised, Jev's native, so probability-quality differences are "differences between the systems as deployed" (Section 2.3).

## Statistics
- Wilson 95% CIs on accuracy; paired difference with 2,000 bootstrap resamples; exact McNemar test with Holm adjustment across four benchmarks; ECE with ten equal-width bins; AUROC; multiclass Brier (0-2); selective prediction at fixed thresholds 0.5, 0.8, 0.9 (not tuned on test data) plus AURC (Section 2.5). ECE, AUROC, selective prediction not computed for NEJM (n = 34). ECE insensitive to binning (at most 0.005 change) (Section 3.3). No post-hoc recalibration applied (post_hoc_calibration none); authors recommend per-task recalibration (Section 4.2, Conclusion).
- All 8,469 requests valid on first attempt; two Jev responses and one GPT-6 Sol (none) response returned an option other than the highest-probability one (Section 3.1).

## Cost and latency
- Jev median client-side latency 0.27-0.31 s, p95 0.35-0.38 s; GPT-6 Sol 1.68-3.82 s (medium) and 1.19-1.62 s (none). Evaluating all 2,823 items cost US$0.082 with Jev, US$6.87 with GPT-6 Sol medium, US$3.94 none (Section 3.5, Supplementary Table S7). Jev one request at a time, GPT-6 Sol four concurrent requests, "not compared head to head" (Section 2.5). Jev latency includes the OpenRouter hop (Section 4.3).

## Cascade, option-name, cardinality, robustness
- No escalation cascade, but selective prediction (accept at probability >= 0.9, defer rest) is analysed; on MetaMedQA GPT-6 Sol is as accurate at similar coverage (Section 3.3).
- Option order not varied: "each model and condition was run once, with options in their original order, so repeatability and sensitivity to option order were not assessed" (Section 4.3). Unanswerable-question handling (Q3) is an option-set design test: Jev chose "I don't know" for only 10.5 percent of questions where it was correct (Section 3.4).

## Authors' stated limitations (Section 4.3)
- Text only; recognition rather than generation of diagnoses; contamination cannot be excluded; single run, no option-order test; GPT-6 Sol probabilities verbalised, two of six effort levels, one unoptimised prompt; Jev accessed via intermediary; not designed to show equivalence; NEJM reader comparison descriptive.
