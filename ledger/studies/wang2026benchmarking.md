# wang2026benchmarking

arXiv 2610.33410v1 (cs.AI), 24 Oct 2026. "Benchmarking System One Models for Time-Series Decision Making: A Case Study of Jev." Authors Jianye Wang, Kexin Zhang, Jiayin Xiong, Hao Xue (corresponding), The Hong Kong University of Science and Technology (Guangzhou). Affiliation type: academic. (title block)

## Task and data
- Jev 1.13.0 is applied to time-series decisions serialized as a state plus a fixed question per task: UCR univariate classification (127 datasets used: 41 binary, 86 multiclass, of the 128 in the 2018 archive), UEA multivariate classification (17 datasets with scores, of 30), event type prediction on EasyTPP (Amazon, Retweet, StackOverflow, Taobao, Taxi), direction prediction on ETT (oil temperature at a 24-hour horizon, univariate S and multivariate MS inputs, 8 settings) and binary stock direction for AAPL, BA, CAT (daily records from Al Ridhawi et al. 2026). (Sec. 4.1, Tables 1 to 6)
- Per-dataset sample counts, train/test splits, window lengths and the number of Jev calls per dataset are not reported in the text. Why 11 UCR and 13 UEA datasets have no scores is not explained ("datasets with available scores"). Anomaly detection is formalized in Sec. 2.3 but not evaluated. (Sec. 2.3, 4.1)
- Reference labels: archive class labels (UCR, UEA), observed next event type (EasyTPP) and realized future direction (ETT, stocks, a task-outcome label). Public archives that predate 2026; the stock dataset runs through 2025 and was released in 2026, so overlap with training data is unclear. No contamination discussion. (Sec. 4.1, references)

## Decision model
Jev 1.13.0 via its public decision interface; binary questions use Noul (probability the statement is true), multiclass use Choice. One fixed question template per task. No run dates or returned model string; TypeSafe blog accessed 2026-10-21. The architecture description (BERT-style) is illustrative only, as the paper says Jev's internals are not public. (Sec. 3, 4.2, references)

## Comparators and tuning parity
No comparator system. Chance level is the implicit reference; the paper does not give majority-class or classical baselines, so accuracy figures are not set against class priors. Fixed templates, no tuning described. (Sec. 4.2)

## Results
Mean accuracy / mean AUC over datasets: UCR binary 0.5411 / 0.5341 (41); UCR multiclass 0.1874 / 0.5187 (86; 63 of 86 AUCs between 0.45 and 0.55; excluding SyntheticControl and SmoothSubspace mean AUC 0.5075); UEA 0.1566 / 0.5172 (17); EasyTPP 0.5127 / 0.7028 (5; AUC 0.6466 to 0.8241); ETT 0.5137 / 0.5900 (8); stocks 0.5034 / 0.5040 (3). Strong cases: SyntheticControl AUC 0.9978 (accuracy 0.8100), SmoothSubspace 0.9815 (0.9000), Wafer 0.8056; AUC below chance on ECG200 0.4696, ECGFiveDays 0.4434, TwoPatterns 0.3224. Ranking-versus-decision gap: GunPoint AUC 0.7215 with accuracy 0.5200, BasicMotions 0.7671 with 0.3000. No confidence intervals, no repeated runs, no significance tests. (Tables 1 to 6, Sec. 4.3)

## Cost and latency
Not reported (the introduction motivates low latency and cost but none is measured).

## Calibration
Not evaluated; the authors list probability calibration and threshold selection as needed future work. AUC and accuracy only.

## Cascade or escalation
None.

## Robustness
None (no option-order, wording, language or cardinality tests). Label granularity contrast: DodgerLoopWeekend AUC 0.6953 (binary) versus DodgerLoopDay 0.5056 (seven classes). (Sec. 4.3)

## Code and data
No repository link; the paper states the framework "standardizes sample construction, model calls, and result recording" but gives no release location. Datasets public.

## Authors' limitations
No separate limitations section. The conclusion notes uneven performance, near-chance numerical tasks and the ranking-versus-accuracy gap, and calls for temporal representation, domain adaptation and decision-score alignment.
