# wang2026chinese

Chinese-Jev: Bringing System One Model to Chinese-Language Tasks. arXiv 2609.36965v1 (cs.CL), 2026-09-29. Extractor: batch V05. Ledger rows L1821 to L1836.

## Authors and affiliation
Zexiao Wang, Zihao Zhang, Xudong Wang, Pan Wang, Ziyi Ye, Haoyu Zhao, Zuxuan Wu, Shuicheng Yan. Fudan University, National University of Singapore, University of Chinese Academy of Sciences (title block). Affiliation type: academic. Owner of the proposed model (own-model paper): the authors train Chinese-Jev and compare it with hosted Jev.

## Task and data
Chinese-language decisions (choice, noul, score) across a general domain and medical, legal and finance domains. Training corpus: 10 million general decisions in eight task categories, plus domain corpora (medical 3,000,000 decisions; legal and finance 24,000 each) (Sec. 4.1). Benchmark CJ-Bench: held-out test partitions only, General 100,000, Medical 200,000, Legal 4,300, Finance 3,600 decisions (Sec. 4.1, Appendix A.1); the abstract and intro cite 307,900 decisions in total (Sec. 1). Source data are public Chinese datasets converted into probability targets (C3, T2Ranking, ASAP, USTS, CMB, LeCaRDv2, FinRE and others, Sec. 3.1); 10,700 template-generated rule decisions (0.107% of the general corpus) are synthetic (Appendix A.3). Decisions that share source material are placed in one partition and a near-duplicate screen against held-out text is applied; the paper states the screen is limited to held-out text available when a candidate is checked (Appendix A.2). Because the test items come from public datasets released before 2026, the hosted Jev model could have seen them; no contamination check for Jev is reported.

## Decision models evaluated
Chinese-Jev General (mmBERT-base encoder, 22 layers, hidden size 768, plus two decision Transformer layers and a shared scorer, about 322M parameters, initialised from Laya Multilingual, one epoch on the general corpus) and three domain specialists (four epochs each, started from the General checkpoint) (Sec. 3.2, 4.1). Training: RLCD objective of Laya (cross-entropy plus policy-gradient term), four logit perturbations per decision, eight NVIDIA H200 GPUs (Sec. 3.2, 4.1, Appendix A.5). Hosted Jev is accessed through its API; no model version string (no jev-1.x identifier) is reported anywhere in the text; the Jev reference is dated "accessed September 27, 2026" in the reference list (docs.typesafe.ai/models, release announcement accessed 2026-09-27). Open comparators with repository revisions in the references: Open-Jev (Zefan Cai, revision 3308a15), SemIF (revision 23cf1f3), Laya Multilingual (Laya repository version 0.3.11, commit 1e28ac2, per the references), Qwen3.5-2B in non-thinking mode by scoring candidate labels (Sec. 4.1, references).

## Comparators and tuning-budget parity
All models receive the same retained context and candidates and are evaluated on the same eligible examples (Sec. 4.1). The paper does not state whether comparator open models were fine-tuned on Chinese data; Chinese-Jev is trained on 10 million Chinese decisions and domain corpora, whereas Jev is used zero-shot through its API (inferred; the paper does not describe Jev prompts or instructions). Tuning budget for comparators: not reported. Each comparator "supplies a candidate distribution" (Sec. 4.1).

## Reference labels
Gold labels are the source dataset annotations (human annotations of public Chinese datasets, some soft targets from multiple raters, e.g. 19 ratings in USTS, Figure 3) with a small synthetic rule-based portion in training (Appendix A.3). ACC and ECE use single-label examples only; soft targets are excluded (Sec. 4.1). Label provenance of the Medical, Legal and Finance test sets is described in Appendix A.4 (not extracted in detail).

## Sampling and intervals
Full held-out partitions; no confidence intervals, no repeated runs, no seeds reported (Sec. 4.1, Tables 1 and 2).

## Headline results
General: Chinese-Jev General 69.20% accuracy and 3.78% ECE versus hosted Jev 68.35% and 11.45%; Laya Multilingual 40.22% and 23.04% (Table 1). Domains (accuracy %): specialist Medical 87.65 vs Jev 84.29; Legal 60.10 vs 68.35; Finance 64.72 vs 78.39; average 70.82 vs 77.01, i.e. 92.0% of Jev's average (Table 2, Sec. 4.2). Specialist average ECE 12.08% vs Jev 5.57%; ECE rose on Legal from 15.37% to 17.45% after specialisation (Sec. 4.2).

## Calibration
ECE over 15 equal-width bins on top-candidate probability; each checkpoint's native probability transformation retained, no additional calibration (Sec. 4.1).

## Cascade or escalation
None.

## Cost and latency
Median end-to-end latency per decision on one H200 at batch size one after warm-up, including input preparation (Sec. 4.1). Chinese-Jev 14 ms (General) and 15 ms (specialists); Jev hosted API 284 ms (General), 256.33 ms domain average, measured client-side with one decision per request including network round trip; the paper itself notes the comparison reflects end-to-end response time, not model inference speed (Sec. 4.2). Speedups: 20.3x (general) and 17x (domains). Qwen3.5-2B 280 ms. On-device INT8 prototype about 1 s per decision on iPhone 15 Pro (Sec. 4.3). No dollar cost reported for Jev API use.

## Option-name, cardinality, language and robustness tests
None reported (no option-name or permutation tests; single language, Chinese).

## Code and data availability
"We will release the models, training data, benchmark, and data construction code" (abstract, Sec. 5). Project page https://gulucaptain.github.io/Chinese-Jev/. No released artefact verified by the extractor.

## Authors' stated limitations
Stated as future work in the conclusion only: remaining accuracy gaps in law and finance and uneven calibration gains after specialisation (Sec. 5). The paper also notes that the latency comparison with the hosted API includes network round-trip time (Table 1 note, Sec. 4.2).
