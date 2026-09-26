# Synthesis notes for the curators and the §7 drafter (ledger v1.0 plus rows L900 to L933; guo2026just and dossantos2026calibrated added after the sweep fix)

Every number carries its `syn.` key or ledger `value_key`. Independence is counted in clusters: li2026fast and li2026replacing (same group and testbed) form one, giving 26 clusters [syn.ledgerClusters]. dossantos2026calibrated enters no analysis: its ECE and latency figures quote vendor documents, and its pentest arms have one run each (RoB D2, D3 high). Calibration error is never pooled across binning schemes. Estimands with fewer than 3 clusters get a range only. R1 census counts come from the census scripts.

## R1. The interface is the innovation

**Supported in part.** The best open model and Jev were scored on the same items in 6 clusters [syn.r1GapNStudies]. Gaps are best open minus Jev.
- The median gap is 0.4 points [syn.r1GapMedian], interval -4.0 [syn.r1GapCiLo] to 4.0 [syn.r1GapCiHi].
- The median absolute gap is 3.7 [syn.r1AbsGapMedian], so "come close" holds on magnitude.
- The sign does not hold. The open model is ahead in 3 clusters [syn.r1OpenAheadCount] and behind in 3 [syn.r1OpenBehindCount].

**The sign follows who measured.**
- **Parity.** Ibrahim & Zaki is the only comparison graded D4 low [syn.r1GapParityNStudies]. There the best open model trails by 4.4 macro-F1 [syn.r1GapIbrOpenBest], and Nimble trails by 5.6 [syn.r1GapIbrOpenNimble].
- **Nimble's own card.** It reports -3.1 [syn.r1GapNimble324], on synthetic labels that the ledger miscodes as human_adjudicated (contradicted_claims 11), revision original-2676.
- **Developer self-reports.** These are all D4 high. Their study values run from -3.5 [syn.r1GapSelfReportMin] to 4.1 [syn.r1GapSelfReportMax]:
  - Rev is ahead by 7.0 on its own holdout [syn.r1GapRev975].
  - Kev is ahead in distribution by 2.7 [syn.r1GapKevInDist] but behind out of domain by 3.5 [syn.r1GapKevOod].
  - Fine-tuned Laya is ahead by 3.9 [syn.r1GapLayaTypedDecisions], against LocalLLaMA's published Jev run.
  - Cheng's trained model is ahead by 4.1 on third-party captures [syn.r1GapCheng2250].
- **Human-labelled clusters.** They span -4.4 [syn.r1GapHumanRefMin] to 3.0 [syn.r1GapHumanRefMax].

**Within-backbone contrasts favour the interface reading.**
- A typed head adds 0.0 points over answer SFT [syn.r1ReadoutYuHeadVsSft].
- A typed readout adds 2.2 AUROC points over label-token fine-tuning [syn.r1ReadoutRenReadout].

**Robustness does not replicate.** Sun & Xu's open marker head leads Jev by 12.3 AUROC points with aligned option names [syn.r1GapSunAligned]. It trails by 34.9 under the polarity swap [syn.r1GapSunSwapped].

**RoB.** The open-leads results all come from D4-high sources. The one parity study is high only through D5.

**Proposed wording:** "Open label-conditioned heads on public backbones reproduce the typed contract and land within a few points of the hosted model on items their developers chose. They trail it by 4.4 points [syn.r1GapIbrOpenBest] under the one parity-controlled comparison, and they do not yet reproduce its robustness to option names."

## R2. Calibration is conditional

**Supported, and understated.** Jev's raw ECE runs from 0.023 [syn.r2JevEceMin] to 0.168 [syn.r2JevEceMax] across 7 clusters [syn.r2JevEceNStudies].
- Low end: rafe2026calibrated (exact grid). High end: guo2026just (median per benchmark), then ibrahim2026evaluating at 0.157 [syn.r2JevIbrJev]. Guo enters on its per-benchmark median, the estimand Ibrahim & Zaki also report.
- Each named scheme has one study:
  - 10 equal-width bins give 0.031 [syn.r2JevEceBinEqualWidth10BinsMin].
  - Unstated binning covers 4 studies [syn.r2JevEceBinNotSpecifiedNStudies], from 0.038 [syn.r2JevEceBinNotSpecifiedMin] to 0.168 [syn.r2JevEceBinNotSpecifiedMax].

**Binning does not explain the spread.** Within Ibrahim & Zaki, alternative schemes (Table 9) move Jev's ECE by 0.006 [syn.r2BinningSpan]. The between-study spread is 0.145 [syn.r2StudySpan], 24 times larger [syn.r2StudySpanOverBinningSpan]. **The estimand does matter.** In Guo et al. the per-benchmark median exceeds the pooled ECE (0.047 [syn.r2JevGuoJevPooled]) on the same decisions by 0.121 [syn.r2GuoEstimandGap], most of the between-study spread. Its excess over the perfect-calibration null (0.074 [syn.r2JevGuoJevNull]) is 0.094 [syn.r2GuoExcessOverNull], so part of any per-task ECE is finite-sample floor.

**Estimands still differ** (median over tasks, pooled, single benchmarks, LLM-teacher reference).
- Per-task records reach 0.538 on empathy [syn.r2JevEceRecordMax].
- Two rows are kept as context:
  - REFLEX's 0.129 [syn.r2JevReflexJev] covers non-escalated decisions only.
  - KITE's 0.027 [syn.r2JevKiteJev] scores predicted human response shares, and the contract was selected on that value.

**Recalibration depends on the fit set.**
- In-domain fits leave 0.17 [syn.r2RecalRatioInDomainMin] to 0.34 [syn.r2RecalRatioInDomainMax] of raw ECE.
- Transferred fits leave 0.40 [syn.r2RecalRatioTransferredMin] to 0.96 [syn.r2RecalRatioTransferredMax].
- For Jev the ratio is 0.30 in-domain [syn.r2RecalJevEceRafeJevPlatt] and 0.77 transferred [syn.r2RecalJevEceIbrJev].
- Nimble's temperature leaves its holdout ECE at 1.0 of raw [syn.r2RecalOpenEceNimble324].

**The native advantage is fragile.** Before scaling, 3 [syn.r2LlmBelowJevBefore] of 19 [syn.r2LlmCount] LLMs beat Jev on ECE. After the same pilot-task temperature, 15 do [syn.r2LlmBelowJevAfter].

**Confident-but-wrong regions.**
- **Empathy (Ibrahim & Zaki).** High-confidence accuracy is 0.012 above base rate [syn.r2CbwEmpathy].
- **Khmer (Laya).** Accuracy is 0.000 [syn.r2CbwKhmerAcc] at 0.952 confidence [syn.r2CbwKhmerConf].
- **Option-name polarity (Sun & Xu).**
  - The open head inverts to 0.232 AUROC [syn.r2CbwPolarityMarker].
  - Jev drops toward chance at 0.581 [syn.r2CbwPolarityJev].
- **Archer Hume's top bin.** Predicted 98.7 [syn.r2CbwTopBinPred] against observed 96.3 [syn.r2CbwTopBinObs].
- **Kev card.** Jev's out-of-domain confident-error rate is 3.7% [syn.r2CbwKevJevConfErr].
- **LocalLLaMA card.** A know-nothing Prior has the lowest ECE, 0.088 [syn.r2OpenLocalllamaPrior].

Li et al. show confidence still orders errors: 47.7% accuracy at low confidence [syn.r2CbwLiLowConf] against 95.8% at high [syn.r2CbwLiHighConf].

**RoB.** The low extreme is the authors' own paper (some concerns). guo2026just and ibrahim2026evaluating are high through D5.

**Proposed wording:** "Calibration belongs to the model and the task together. Raw error varies by a factor of 7.3 [syn.r2JevEceMaxOverMin] across studies. Binning does not explain this, but the estimand (pooled against per-task) explains much of it. In the records available, in-domain recalibration gave the largest cuts, and transferred fits ranged from substantial to negligible. It is no durable advantage over LLMs given one temperature."

## R3. The cascade wins

**Not supported as stated.** The estimate rests on 3 clusters [syn.r3RetainedNStudies] with different cost definitions:
- Li et al.: the fallback fee.
- Ibrahim & Zaki: a median task-cost fraction.
- REFLEX: per-episode cost on τ²-bench, with an unresolved success difference.

**Estimates.**
- Retained quality is 0.94 [syn.r3RetainedMin] to 0.99 [syn.r3RetainedMax] of the strong model alone.
- The fee fraction is 0.27 [syn.r3FeeFracMin] to 0.57 [syn.r3FeeFracMax], median 0.56 [syn.r3FeeFracMedian].
- With 3 clusters the interval equals the range.
- Only 2 clusters [syn.r3StrongFracNStudies] report the escalated share: 0.27 [syn.r3StrongFracMin] to 0.46 [syn.r3StrongFracMax].
- Thresholds were chosen differently (Li frozen on pilot pairs, Ibrahim selected, REFLEX unclear).

**Counter-evidence.**
- REFLEX's cheap generative cascade retains 1.0 [syn.r3RetainedB3Tau] at 0.19 of the strong model's cost [syn.r3FeeFracB3Tau], which is 0.72 of REFLEX's cost [syn.r3B3CostOverReflex].
- Ibrahim's cheap-partner cascade costs 0.84 of the partner alone [syn.r3FeeFracIbrGemma05], and 1.1 at a stricter threshold [syn.r3FeeFracIbrGemma08].

**Kept out of the estimates.**
- KITE's fixed anchors, on 0.017 of states [syn.r3StrongFracKiteEpstein], use a different design.
- Paper 1's review budget of 0.8% [rafe2026calibrated.reviewBudgetH90PooledHeldOut] is a precision-targeted deferral budget, not a cascade (contradicted_claims 19).

**RoB.** Li and Ibrahim are high only through D5. REFLEX has some concerns.

**Proposed wording:** "Confidence-gated escalation to a frontier model kept 0.94 to 0.99 of its quality [syn.r3RetainedMin, syn.r3RetainedMax] at 0.27 to 0.57 of its fee [syn.r3FeeFracMin, syn.r3FeeFracMax] in 3 studies [syn.r3RetainedNStudies]. The saving shrinks with the price gap to the partner, and it does not beat a cheap generative cascade where routing is already accurate."

## Accuracy gap, cost and speed

**Accuracy gap.** Jev trails its best frontier comparator in 4 [syn.gapJevBestNegCount] of 5 clusters [syn.gapJevBestNStudies], median -5.8 points [syn.gapJevBestMedian] (interval -11.6 [syn.gapJevBestCiLo] to 0.0 [syn.gapJevBestCiHi]).
- Ibrahim's -11.6 [syn.gapJevBestIbrGap] is against a per-task oracle.
- Li et al. by task family (contradicted_claims 15):
  - -3.0 on preference [syn.gapJevBestLiJudgeRewardBench]
  - -2.5 on grounded factuality [syn.gapJevBestLiJudgeHaluEval]
  - -16.0 on difficult correctness [syn.gapJevBestLiJudgeJudgeBench]
- Deng's 0.0 is a ceiling [syn.gapJevBestDengGap].
- Adding the li cluster's DeepSeek comparator gives -4.4 [syn.gapJevBestSensMedian].

**Cost ratio.** Comparator cost over Jev cost has a median of 51 [syn.costRatioMedian] over 7 clusters [syn.costRatioNStudies], interval 37 [syn.costRatioCiLo] to 260 [syn.costRatioCiHi]. Guo et al. add 63 against the benchmarks' own judges [syn.costRatioGuoCost], or 12 when repriced conservatively [syn.costRatioGuoCostConservative].
- Cluster values run from 1.9 [syn.costRatioMin] to 280 [syn.costRatioMax].
- The comparator is cheaper in 1 row [syn.costRatioRowsBelowOne]: li2026fast, at 0.59 [syn.costRatioRowMin].
- li2026replacing's Study A, which combines live fees with modeled execution, is context.

**Speed ratio.** The median is 3.6 [syn.speedRatioMedian], range 1.3 [syn.speedRatioMin] to 12 [syn.speedRatioMax]. Every row falls below the vendor range (f06). Vercel is not counted.

**Pareto.** The only case where Jev is dominated is a developer self-report: Rev's small replica, at 0.60 of Jev's cost [syn.costRatioRevCost] and 0.26 of its latency [syn.speedRatioRevSpeed].

## What the evidence does not yet show

- Only 1 study [syn.r1GapParityNStudies] compares an open replica with Jev under parity.
- 4 [syn.r2JevEceBinNotSpecifiedNStudies] of 7 [syn.r2JevEceNStudies] Jev ECE studies omit the binning.
- No cascade study shares a cost definition with another.
- No study tracks behaviour across Jev versions.
- Paper 3's inverted top-bin confidence is not in the ledger.

**Fewer than 3 clusters (range only).**
- R1: the parity, task-outcome and model-or-synthetic strata, the AUROC comparison (Sun), and the readout contrasts.
- R2: each named binning scheme, Jev recalibration, and the LLM temperature comparison.
- R3: the escalated share and KITE's error ratio.
- Accuracy gap: kappa -0.002 against a non-frontier scorer (Guo) [syn.gapJevBestGuoKappa], Kendall -0.131 [syn.gapJevBestHuangGap], PLCC -0.029 [syn.gapJevBestRobitzaGap] and distance -0.035 [syn.gapJevBestKiteGap].
- Type errors: 0 in both studies [sun2026typesafe.typeErrorRatePercent].
