# weng2026our

arXiv 2610.29052v1 (cs.CL), 21 Oct 2026. "Our Own Jev: Typed Decisions in One Forward Pass, from an In-House Judge to Open LoRA Models." The HTML rendering omits Sections 3 and 4 (Part I), so the saved .txt was rebuilt from the PDF; the HTML-derived text is in the V19 scratch folder. (title block)
Authors: Yuchuan Weng, Chi Liu, Xin Chen, Srinivasan Manoharan; PayPal.AI. Affiliation type: industry. (title block)

## Part I: in-house judge (Sec. 3-4)
- Task: triage about 148K agentic coding session records with three typed questions (coding, in-domain, eight-way domain). Fixed bank of 1,000 sessions (250/250/500 strata), split 800/200; evaluation on 200 held-out sessions, 56 of which overlap training records (144 clean). (Sec. 4.3, 4.5)
- Reference labels: a single frontier LLM judge (also confirmed the strata); that judge disagreed with its own earlier pass on 8.5% of binary answers. (Sec. 4.3, 4.8)
- Models: kev fork (frozen Qwen3.5-4B-Base or an in-house 27B fine-tune of Qwen3.6-27B, rank-16 LoRA, pointer head); comparators: released kev-4b zero-shot, rule baseline. No version hashes beyond backbone names; fork not released. (Sec. 4.1)
- Results (Table 2): 4B coding 85.0 [79.3, 89.6], in-domain 91.0 [86.1, 94.6], 8-way 68.0 [61.1, 74.4]; 27B 83.0, 92.5, 69.5; zero-shot kev-4b 72.5, 81.5, 52.5; clean subset 1.5 to 3.8 points lower (Table 16). Exact Clopper-Pearson intervals, exact McNemar.
- Calibration: ECE (10 bins) coding 0.116 zero-shot to 0.062 (4B) and 0.068 (27B); Brier 0.196 to 0.095. No post-hoc calibration. (Sec. 4.4, Fig. 3)
- Cost and latency: 4B on one A100-40GB median server-side 176 ms per session, 27B on three A100-40GB 596 ms; GPU priced at an assumed US$1.25 per A100-hour: US$0.06 (4B) and US$0.62 (27B) per 1,000 sessions versus about US$6.30 for the frontier judge (1.77 s per session, agent batching about 7.5 sessions per call). Hosted decision API not used because of data boundary. (Sec. 3.3, 4.6, Fig. 4)
- Test data: private internal sessions. Code: not released.

## Part II: open letter-readout models (Sec. 5-9)
- Recipe, corpus (eikos-decisions, about 25K rows, cloned 2026-09-24) and seven-suite battery (7,371 items) are Eikos's; authors train LoRA (rank 64) adapters for MiniCPM5-1B, MiniCPM5-2B and Qwen3.6-35B-A3B, one seed each, no tuning of recipe. Readout is the frozen output layer at the answer-letter position, up to 26 options. (Sec. 5)
- Benchmark: 231 public JevBench items (v1.4.2.2, commit fd54ea7): 111 hard items; sealed half not scored. Competitors recomputed from published per-item records, 15 selected by the authors from 52. Jev 1.13.0 appears only through board records (73.0 hard tier), not run by the authors. (Sec. 6, 7.1)
- Hard-tier accuracy: 35B 79.3 (vs Jev 1.13.0 73.0; +6.3, unadjusted p 0.119, not significant); 2B 61.3; 1B 54.1; retrained 2B 73.0 (+11.7 [+2.6, +17.6], McNemar p 0.011, differs in more than seed). Statistics: exact McNemar, Clopper-Pearson, Holm-Bonferroni within comparisons the authors chose. (Sec. 7.1, 8, Table 3)
- Calibration: hard-tier ECE 0.084 (35B), 0.090 (1B), 0.120 (2B; bootstrap 95% [0.079, 0.208]); fitted temperature below one worsened ECE on held-out halves. Selective decisions at confidence 0.9 on the battery: 35B decides 42.3% with 1.9% error; up to 31% of the battery is template siblings of training data. Jev's 5.9% confident-error figure is Eikos's on other suites and the paper says it is not comparable. (Sec. 7.2, Table 4)
- Speed: single-question latency on one H100, 2B 20.5 ms, 35B 83.2 ms; 35B needs about 80 GB. (Sec. 11, 10)
- Exposure and selection: 1B and 35B developed with public items visible; 2B trained before benchmark download; contamination 8-gram check found no overlap; 1,994 retracted FinEntity-derived rows were in all models' training data. Test items public, answer keys released.
- Code: released 2B merged model only (Kailune-AI); 1B and 35B adapters and per-item scores not released.

## Authors' limitations (Sec. 10)
Part I judged against a single frontier judge on 200 sessions with 56 overlapping training; borrowed recipe and battery; no matched pointer-head comparison and no untrained baselines of their own; no sealed measurement; one seed and selection effects (hard-tier floor about ten points); retracted rows; template-sibling battery suites.
