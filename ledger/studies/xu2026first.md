# xu2026first

A First Glance at Jev for Network Traffic Classification: Accuracy, Processing Time, and Cost. arXiv 2610.00376v1 (cs.LG), 2026-09-30. Extractor: batch V05. Ledger rows L1897 to L1907.

## Authors and affiliation
Shenghe Xu (Amazon.com, Inc.; footnote: work performed outside the author's role at Amazon) and Lifan Mei (Xi'an Jiaotong-Liverpool University, corresponding) (title block). Affiliation type: mixed (one industry-affiliated author acting independently, one academic).

## Task and data
Application classification of network flows into ten fixed classes (apple-privaterelay, facebook-graph, google-ads, google-gstatic, google-play, google-services, google-www, instagram, snapchat, youtube) from the first ten QUIC packets (inter-packet time, direction, payload size) of CESNET-QUICEXT-25, a public Parquet conversion of the CESNET DataZoo ORIG distribution (205 daily files, 110,511,231 records before filtering) (Sec. 3.1). Training: 8,000 records from weeks 1 to 4 (June 1-28, 2024) for Random Forest and Extra Trees; test: 52,000 records from weeks 5 to 30 (2,000 per week, June 29 to December 27, 2024) (Sec. 1, 3.1). Weekly selection: seeded hash of source ID (seed 2026092305), first 2,000 after excluding earlier IDs and exact prefix fingerprints, not class-balanced and not uniform over distinct prefixes; no disjointness of hosts or connections is claimed (Sec. 3.1). Extensions on week 5: Jev with 150 examples (2,000 records) and a paired 100-record subset against GPT-5.6 Sol (Sec. 3.2). The paper states the week-5 extensions reuse already-examined data and that hosted-model pretraining overlap is unknown (Sec. 5). The data are public and predate 2026.

## Decision model and version
Jev requested as `typesafe/jev-1.13` through OpenRouter, checked against returned identifier `typesafe/jev-1.13-20260917`; one choice question for one application per query; Jev-0 (zero examples), Jev-40 (40 fixed labeled examples, four per class, lowest-ranked training record in each week/class cell, no weight updates), Jev-150 (15 per class, 23,614 to 23,635 input tokens) (Sec. 3.2). Runs on September 23, 2026 (Sec. 3.3). Eight workers per main arm.

## Comparators and tuning-budget parity
Random Forest and Extra Trees (500 trees, sqrt features, scikit-learn 1.7.2, seed 2026092305) fitted once on 8,000 records, no test-based tuning (Sec. 3.2). GPT-5.6 Sol (deployment gpt-5.6-sol, returned identifier gpt-5.6-sol-2026-07-09) via Azure with high reasoning effort, 4,096 completion-token cap, JSON mode, 60 s deadline, same inputs and examples as Jev with a different API wrapper, 100 records chosen by salted SHA-256 ranking without labels (Sec. 3.2). The authors state the budgets are unequal (8,000 training records for trees versus 40 or 150 class-balanced examples for Jev and at most 40 for Sol), no matched-example tree control was run, and Sol is one configuration rather than an optimised baseline; lower reasoning effort was not tested (Sec. 4.3, 5).

## Reference labels
Labels are inherited from the dataset; the conversion documents SNI-derived label provenance (an administrative/derived field). The authors state this "verifies provenance, not every label's correctness" (Sec. 3.1).

## Sampling and intervals
Fixed deterministic samples (above), 52,000 test records, 100% valid coverage (Table 1). No confidence intervals on accuracies; an exploratory two-sided exact McNemar test on the paired 100 records gives p = 0.2005 (Sec. 4.4). Weekly accuracy trajectories are descriptive (Figure 1). Each request was run once; first valid answer retained regardless of correctness (Sec. 3.3).

## Headline results
Full-set accuracy: RF 69.95%, ET 66.80%, Jev-40 28.42%, Jev-0 9.80%, training-majority constant 22.79% (Table 1). RF and ET exceed Jev-40 in all 26 test weeks (Sec. 4.2). Jev-0, Jev-40 and Jev-150 on week 5: 10.30%, 25.90%, 34.50% (RF 72.70%, 38.20 points higher than Jev-150) (Sec. 4.2, 4.3). Paired 100 records: Jev-40 29, Sol-40 37, RF 65, ET 70 (Table 2). Zero-shot Jev predictions concentrate on google-www (45,010), youtube (6,958) and google-gstatic (32) (Sec. 4.1).

## Calibration
None; the paper states confidence calibration is outside the study (Sec. 2).

## Cascade and escalation
None.

## Option-name, cardinality, language and robustness tests
Ten fixed classes; candidate class names are visible as the output vocabulary and domain strings are withheld (Sec. 3.1). Context size 0, 40 and 150 examples; 26 collection weeks; one example selection only (Sec. 5). No option-name or order variation.

## Cost and latency
Median successful request time: Jev-40 0.750 s (P95 0.877 s) versus Sol-40 6.036 s (P95 37.791 s) on the paired 100 records; full-set Jev-0/40 medians 0.716/0.773 s (Table 2, Sec. 4.4). RF/ET local single-record prediction 0.027 to 0.034 s. Times include network, gateway and service processing and are not matched-load comparisons (Sec. 3.3). API charges for 100 paired responses: Jev-0/40 USD 0.002341/0.028234; Sol estimates USD 3.927254/5.613564 at conservative bookkeeping rates (Sec. 4.5). Full-set known Jev-40 cost USD 14.682004 for 52,000 requests (Table 3). Sol rates are budget estimates, not an invoice.

## Code and data availability
"Aggregate data accompany this paper" and frozen-source hashes support the tables, but this is not a public release of every raw response (Sec. 3.3, 5). No repository link seen in the text.

## Authors' stated limitations (Sec. 5)
One network, ten classes, one weekly selection and one fixed context family; earlier exploratory work influenced scope and week-5 extensions reuse examined data; ID/prefix isolation does not exclude near duplicates or shared hosts; hosted-model pretraining overlap unknown; labels inherited; timing and cost reflect specific service configurations that may change; packet-observation time, feature extraction and live deadlines not measured; no matched-label-budget tree control.
