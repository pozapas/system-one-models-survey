# liu2026decisionb — Decision Models as Judges for Hallucination Detection

Key has suffix b because studies/liu2026decision.md already belongs to a different paper (arXiv 2610.34124). This note covers arXiv:2610.37229v1 [cs.CL], 27 Oct 2026. Full text: fulltext/2610.37229.html and .txt.

## Authors and affiliation
Haozheng Liu (New York University), Zhaoqian Xue (University of Arizona), Zhongyin Wang (University of Illinois Urbana-Champaign), Junting Mu (University of California, Irvine), Zihui Ma (Emory University), Shuya Feng (University of Alabama at Birmingham), and others including Lingyao Li (University of Arizona) (title block; one affiliation line lacks a name in the extracted HTML). Affiliation type: academic.

## Task and data
Binary hallucination detection, one task per type, using six public benchmarks: factual contradiction FC (FAVABench, HADTest; n=1,621), factual fabrication FF (n=1,616), context inconsistency CI (RAGTruth; n=2,675), logical inconsistency LI (ContraDoc, ROSCOE; n=1,646), instruction inconsistency II (IF-RewardBench English; n=2,294); 9,852 items in total, 3,764 positive and 6,088 negative, not rebalanced (Sec 3.1, Table 1). An N item may contain another hallucination type (Sec 3.1). Dataset-to-label mapping is in Appendix A.3-A.4.

## Decision models evaluated
Five hosted decision models: jev (version 1.13.0), d1 (Liquid AI, unversioned alias), clef (Cloudflare, 27B, unversioned), pplx (pplx-decider-v1.1-27b, via OpenRouter, snapshot suffix recorded), gpt-6-luna (OpenAI, unversioned) (Sec 3.2, Table 5). Where only an alias was logged the checkpoint is "not reported". Evaluation dates are not stated beyond the 2026 list prices.

## Comparators and tuning parity
Generative judge gpt-6-sol, asked for a structured verdict with its own probability estimates and no explanation. All models receive the same criterion and input; no gold labels or spans shown; one prompt design per task, prompt sensitivity untested (Sec 3.2, Limitations). No fine-tuning of any system. Cascade components, ordering and deferral rates are chosen on the same items evaluated (optimistic); five-fold cross-fitting is offered as a check (Sec 3.4).

## Reference labels
Source-benchmark annotations mapped to H or N: human span-level annotations (FAVABench), GPT-4o-injected single factual errors validated by two annotators (HADTest), annotated RAG spans (RAGTruth), inserted self-contradictions (ContraDoc), annotated reasoning steps (ROSCOE), constraint checks (IF-RewardBench). Mixed label sources; mapping may introduce mismatches (Limitations).

## n and intervals
Balanced accuracy and macro-F1 pooled per type, 95% bootstrap intervals, paired bootstrap tests over items (2,000 resamples), Holm correction over 25 comparisons for some claims (Sec 3.2, Sec 4.1). Table 2 shows point values; intervals appear in Figure 2.

## Test-data exposure
All six benchmarks are public pre-2026 items; HADTest and IF-RewardBench are recent (2026 citations). No contamination check reported.

## Cost and latency
List-price cost from recorded token usage (jev $0.042, d1 $0.04, clef $0.24, pplx $0.02, gpt-6-luna $0.10 per million input tokens; gpt-6-sol $2 input and $10 output) and mean API latency per call. Decision models cost 0.5% (pplx) to 10% (clef) of gpt-6-sol per item and answer in 0.22 to 0.62 s against 1.6 to 2.6 s (Sec 4.1). Latency is end-to-end API time, not hardware-controlled. Dollar totals are the benchmark's own spend and are not recorded as findings.

## Calibration
ECE with 10 equal-width bins, logistic calibration slope, conf-AUROC, share of errors at confidence of at least 0.9 (Sec 3.3). Overconfidence mild for jev, pplx, clef, d1 (gap 0.04 to 0.12, ECE 0.083 to 0.136), larger for gpt-6-luna (ECE 0.187) and gpt-6-sol (ECE 0.157); conf-AUROC 0.67 to 0.73 averaged over types; lowest for II (0.64) (Sec 4.2). No post-hoc recalibration. Confidence values of gpt-6-sol are self-reported and not fully comparable (Limitations).

## Cascade or escalation
Confidence cascade over the top-3 decision models per type with label-free deferral rates: BAcc 82.2, 84.6, 84.6 on FC, FF, CI, i.e. 0.6, 2.6, 1.9 points above gpt-6-sol at 1.2 to 3.3% of its cost; no useful gain on LI and II (Sec 4.3). Majority voting and arbitration are also tested and are worse than the cascade.

## Option-name, cardinality, robustness tests
Binary option only; no option-order or name test. Source-dataset breakdown shows type and source are confounded (e.g. HADTest FF minus FC gap 12 to 18 points for all judges, no gap on FAVABench) (Sec 4.1, Appendix C). English text only.

## Code and data availability
No code or data link found in the extracted text.

## Authors' limitations
Uneven coverage (CI and II rely on a single source each), cross-dataset confounds, binary mapping from heterogeneous annotations, non-comparable confidences, one prompt per task, fixed model versions, offline replay of cascades with selection on the full sample (final paragraphs of Sec 5 and Limitations).
