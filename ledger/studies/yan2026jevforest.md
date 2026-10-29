# yan2026jevforest — JevForest: Path Voting for Budgeted Feature Acquisition

arXiv:2610.10615v1 [stat.ML], 7 Oct 2026. HTML retrieved from https://arxiv.org/html/2610.10615 (fulltext/2610.10615.html and .txt).

## Authors and affiliation

Yu Yan, University of Chinese Academy of Sciences. Sole author. AI use disclosed (OpenAI Codex assisted with implementation, experiments, analysis and drafting). Affiliation type academic.

## Task and data

JevForest: a feature-acquisition policy (bootstrapped information-gain trees vote on the next question, weighted by global gain) feeding a shared masked predictor. Offline: MiniBooNE (50 features, 2,000 train, 500 test rows per run, three seeds) and a synthetic Cube task; neither invokes Jev (Sec. 2, 4.1). Online: Jev answers eight fixed semantic questions per text for AG News (4 classes; 64 training examples, 48 held-out, 12 per class) and TREC question classification (6 classes; 96 training, 24 held-out, 4 per class), seed 20261007; balanced subsets, AG News drawn from the first 2,000 training and 500 test rows (Sec. 4.5).

## Decision models evaluated

Jev through OpenRouter's Decisions endpoint, model selector typesafe/jev-1.13, "every successful experimental response identifies snapshot typesafe/jev-1.13-20260917" (Sec. 3.5). The Noul interface returns a score in [0,1] per true/false question, thresholded at 0.5 into binary features (Sec. 3.5). A "direct" workflow uses one multiclass Jev choice request (Sec. 4.5). 1,168 successful responses (160 training extraction, 1,008 held-out evaluation). Run date not stated beyond the snapshot string and seed.

## Comparators and tuning parity

Static training-information-gain ranking and seeded random question order, all with the same fitted masked matching-based predictor; an all-question batch (8 questions, one call); direct Jev choice (changes predictor as well as question format). Forests: sixteen trees, two random features per tree, depth six, forest seed zero; global-gain weighting fixed "without test-based tuning" for the online study, but the offline vote rule and square-root subset were chosen after exploratory comparisons (Sec. 4.3, 4.5). All conditions same Jev, same budget of questions; each condition makes its own live requests, so Jev answer variability is not separated from policy effects (Sec. 5.3).

## Reference labels

Public benchmark class labels (AG News category field; TREC question-class annotation). Coded administrative_field for AG News and human_single for TREC.

## n, sampling, intervals

n = 48 (AG News), 24 (TREC). Exploratory paired bootstrap over example IDs within class strata (10,000 resamples): forest minus static +0.0625 [-0.0625, 0.1875] AG News and -0.0833 [-0.1667, 0.0417] TREC; forest minus random +0.1458 [0.0208, 0.2708] and -0.1667 [-0.2917, -0.0417]. No multiplicity adjustment, no confirmatory claim (Sec. 4.6). No intervals on the Jev direct and batch accuracies.

## Test-set exposure

AG News (2015) and TREC (2002) are public benchmarks with answer keys released before 2026; no contamination check. Coded public-pre-2026.

## Cost and latency

Provider-reported USD, mean per held-out example (x10^-6) and median end-to-end seconds (Table 5), training extraction excluded. AG News: forest 66.03 and 3.525 s, batch 38.07 and 0.863 s, direct 17.99 and 0.846 s. TREC: forest 57.93 and 3.537 s, batch 36.66 and 0.811 s, direct 18.06 and 0.836 s. Held-out total USD 0.017668014; three training transport failures have unknown cost (Sec. 4.6). Latency includes network overhead; two concurrent workers.

## Calibration

None; the paper states the 0.5 threshold "is not a calibrated stopping rule" and lists calibrated uncertainty as future work (Sec. 3.5, 5.3). Post-hoc calibration none.

## Cascade or escalation

Not a cascade. Sequential four-question forest queries are less accurate, more costly and slower than an eight-question batch on both tasks; direct Jev classification matches batch accuracy at lower cost (Sec. 4.6, Conclusions).

## Option-name, order, language, robustness

None beyond fixed question wording set before held-out evaluation; question context differs between batch training extraction and sequential testing, which may change answers (Sec. 5.3).

## Code and data availability

https://github.com/qzqdz/jevforest (and jevtree, jevgboost repositories cited). MiniBooNE (UCI), AG News and TREC public.

## Paper's own limitations (Sec. 5.2, 5.3)

Exploratory; one forest seed online; small balanced samples; vote rule and subset selected after exploratory comparisons; paired predictions not retained for ablations; hand-specified questions and binary thresholding discard probability information; Jev answer variability not separated; JevBoost study preliminary; no claim of superiority over existing acquisition methods. (The offline MiniBooNE and Cube results do not use Jev and are not ledger rows.)
