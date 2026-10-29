# Messoudi and Mansar 2026, Calibration and Risk-Budgeted Decisions with System One Models

arXiv:2610.19811v1 [stat.ML], 14 Oct 2026, arXiv perpetual non-exclusive licence (fulltext/2610.19811.txt, header).

## Authors and affiliations

Soundouss Messoudi, Heudiasyc (UMR CNRS 7253), Université de Technologie de Compiègne; Youness Mansar, Independent Researcher, France (title block). Affiliation type: mixed (academic plus independent).

## Task and data

Binary forced-action decisions under an asymmetric risk budget: controlling the false omission rate (FOR) among inputs given the utility-maximising action (allow or discard), with block or retain as conservative fallback (Sections 1, 3). Six datasets (Table 1, Section 5.2): WildGuardMix (fit 2000, cal 849, test 850, 44.4% positive), Aegis (2000/579/579, 67.0%), S-Labs prompt injection (2000/1051/1050, 50.0%), ATBench trajectory safety (500/250/250, 47.6%), SciDocs (2000/1000/1000, 50.8%) and StackOverflow (2000/1000/1000, 50.1%) reranking framed as binary filtering. Single seed, label-stratified fit/calibration/test splits; grouped by repeated prompts for moderation and safety; reranking pairs separated by query ID (Appendix B.2). Labels are the public benchmark annotations (the paper calls them normative judgments, Ethical Considerations); their provenance is not described, ledger label type is therefore administrative_field. All datasets public and pre-2026 (ATBench Li et al. 2026b is the exception to check); the paper says it "cannot guarantee the absence of training-data contamination for externally supplied APIs" (Ethical Considerations).

## Decision models

Typed decision models (Section 5.1, Appendix B.1): Jev typesafe/jev-1.13; GPT-6-Luna typed-decisions endpoint (openai/gpt-6-luna-decisions); Span-01 (respan/span-01); Solar-Decide (upstage/solar-decide); Kev-0.8B as released (Kev-base, jaredpalmer/kev-0.8b) and Kev-ft (rank-16 LoRA plus 256-dim pointer head on frozen Qwen3.5-0.8B-Base, two epochs, seed 0, 9,988 pooled fit records including BeaverTails, 37 minutes on an RTX 5090). Experiments and cost calculations conducted late September to early October 2026 (Appendix B.6).

## Comparators and tuning parity

Qwen3Guard-Gen-0.6B (softmax mass on Unsafe tokens), Voyage rerank-2.5-lite (score clipped to [0,1], not an advertised probability), PCA-Ridge (logistic regression on 100-dim PCA of frozen Qwen3-Embedding-8B, fit per dataset) (Section 5.1, Appendix B.1). Parity is not matched: PCA-Ridge and Kev-ft use the fit splits (supervised), Jev and other general models are zero-shot; Table 2 marks supervised models with an asterisk. Threshold policies compared: Naive (tau = alpha), Empirical (lowest FPR with calibration FOR at most alpha), LTT (Learn Then Test fixed-sequence binomial certification, delta 0.10), at alpha 5, 10, 15, 20, 40, 50% (Section 5.3).

## Headline results

Jev score diagnostics (Table 2, ECE 10-bin / Brier / AUROC): WildGuardMix 0.034/0.073/0.963; Aegis 0.183/0.151/0.936; S-Labs 0.185/0.158/0.947; ATBench 0.076/0.200/0.768; SciDocs 0.290/0.236/0.917; StackOverflow 0.099/0.196/0.790. The text concludes calibration is dataset-dependent and "a bounded interface alone does not guarantee calibration" (Section 6.1). 95% intervals are in Appendix C.1 (not extracted).

Policy results (Tables 3, 4): across 47 model-dataset pairs and six budgets, Naive exceeds the budget in 105 settings (42.0%, mean excess 7.09 pp, max 73.26), Empirical in 108 (51.7%), LTT in 12 (7.8%, mean excess 0.10) but LTT returns no certificate in 129 settings (21.3% availability at alpha 0.05, 76.6% at 0.5; Section 6.2). Jev on WildGuardMix at alpha 0.15: naive utility 68.7 at risk 3.3, LTT utility 96.8 at risk 12.8 (Section 6.2). Kev-ft availability 31/36 vs Kev-base 13/36 (Section 6.3).

Cost and latency (Table 5, USD per 1,000 examples and ms per example): Jev 0.0216 and 383 (WildGuardMix) up to 0.0757 and 261 (SciDocs); GPT-6-Luna 0.0375 and 320; Kev-ft 0.0030 and 98; PCA-Ridge 0.0026 and 5,247. Latency figures are recorded historical overheads, not controlled microbenchmarks (Appendix B.6).

## Calibration

10-bin ECE (equal width) and Brier reported for every model and dataset (Table 2, Section 5.4). LTT is explicitly not probability recalibration (footnote 1 in Section 4.1). Proposition 1 links conditional policy risk to calibration error inside the selected region. No temperature or isotonic recalibration of scores.

## Cascade and escalation

Not run; future work proposes LTT certification for multi-model cascades (Section 7). The "fallback to a local fine-tuned model if the general model is too conservative" strategy is a recommendation (Section 6.3).

## Option-name, cardinality, language and robustness

None; six English-language benchmarks (Limitations).

## Code and data availability

No repository link found in the text. Artifact terms listed in Appendix B.7 (open-weight licences Apache-2.0).

## Paper's own limitations

i.i.d. assumption between calibration and deployment, no adversarial or shift test; ATBench is retrospective classification of truncated trajectories and the reranking tasks use a constructed mixture; exact binomial certification needs large calibration samples so LTT often returns non-deployment at strict budgets; Kev-ft requires labelled fit data (Limitations).
