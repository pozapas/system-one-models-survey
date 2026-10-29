# hu2026jevguard: Jev-Guard, Fast Routing and Auditing Agent Actions over Editable Policy Trees

arXiv:2610.18326v1 [cs.CR], 13 Oct 2026 (license arXiv perpetual non-exclusive). Full text: `fulltext/2610.18326.html` and `.txt`. Extractor batch V12.

## Authors and affiliations

Wenbin Hu (equal contribution, project lead), Huihao Jing, Haochen Shi, Yuxuan Liu, Changxuan Fan, Sirui Zhang, Kawai Chung, Hanyu Yang, Zhenhuan Wang, Ziyi Chen, Haoran Li (corresponding), Yangqiu Song. Affiliations: HKUST (most authors), ModeIO (a company, shared by several authors), CUHK (Shenzhen) (author block). Affiliation type: mixed.

## Task and data

Own-model paper. Jev-Guard is a Qwen3.5-2B classifier with direct prediction heads (safety, choice/category, routing) that follows "the direct structured-decision paradigm of Jev" and the Open-Jev implementation family (Sec. 1, 2). It routes an agent action through an editable policy tree (85 nodes, 73 leaves; content moderation, cybersecurity, privacy, legal compliance) and then performs policy-conditioned safety classification; a separate permission head gates execution (Sec. 3, Figure 1). Training set 377,930 unified records from public datasets in four domains, label provenance recorded (original, mapped, weak labels at loss weight 0.25 never used in evaluation); LoRA rank 8, checkpoint at update 1,508, 16,384-token cap (Sec. 4.1, 5.1).

Evaluation sets: 7,033 matched test cases (content 2,180, cyber 3,694, privacy 655, compliance 504) comparing systems on identical text records (Table 1); native evaluation on 147,643 records across 109 views (Table 2); routing on 1,000 node-level records from 977 unique source cases; policy-edit probes (30 targets and 30 controls for rules, 24 actions for categories, 200 cases for tree edits); Hermes agent runs on AgentDojo with 16 normal and 16 injected tasks per suite over four suites, 512 episodes (Sec. 5).

## Decision models evaluated and versions

- Jev-Guard, one frozen checkpoint (update 1,508), Qwen3.5-2B base.
- "Official Jev 1.13 (API)": archived OpenRouter decisions requests specify typesafe/jev-1.13, and successful responses identify typesafe/jev-1.13-20260917; a choice question classifies policy compliance as safe or unsafe; three calls failed after retries (two email, one HTTP) and count as incorrect; "This version is not assumed to be currently served" (App. H, Official Jev). Archived predictions from older logs; exact run date not stated.
- Qwen3.5-2B SFT generative baseline "trained on earlier data mixtures with a different objective".
- Agent study: actor and LLM judge both deepseek-flash at temperature zero (Sec. 5.5).

## Comparators and tuning-budget parity

Not matched. "Prompts and training histories differ across systems, so the comparison does not isolate architecture" (Sec. 5.2, Table 1 caption). Official content inputs "retain earlier formatting", official Omni inputs "retain source-rule passages removed from local inputs", category vocabularies not aligned; the local SFT baseline differs in initialisation, objective, exposure and selection (App. H). Official Jev is therefore an external baseline given its own prompts and tasks while Jev-Guard and SFT were trained on this four-domain data (in-distribution training; Jev is zero-shot).

## Reference labels

Original dataset labels for most views (AEGIS, SafeMT, PrimeVul, DiverseVul, PhreshPhish, OPP-115, PrivaCI, Unfair-ToS, Omni etc.); mapped labels from source metadata by explicit rule; weak labels only in training. Evaluation uses original and mapped labels. Coded administrative_field for the headline matched-case accuracy (mix of dataset-assigned labels).

## n, sampling, intervals

7,033 matched cases for Table 1 with pooled overall accuracy (not the mean of domain percentages). Jev-Guard minus SFT +0.355 points, 95% hierarchical-cluster bootstrap interval [-0.327, 1.009]; McNemar p = 0.309; the authors "claim no accuracy advantage" (App. H, Sec. 5.2). Against official Jev +17.830 points, interval [16.795, 18.863]. Routing 93.10% versus flat 92.40%, gap 0.70 with interval [-0.10, 1.60]. Hermes completion rates 79.69% versus 89.06% with overlapping 95% intervals. Single frozen checkpoint, no training-seed variation.

## Test-set exposure

"The source datasets are not held out from training" for the tree study (Sec. 5.3), i.e. test records come from the same public sources as training, using test splits. No contamination analysis for the official Jev baseline.

## Cost and latency

Table 1 latency is local per-case median without routing or permission checks: SFT 513.94 ms, Jev-Guard 58.31 ms (8.81x), from archived end-to-end seconds with four GPU workers; "Official latency is not reported." Full review pipeline (Table 3): mean 239.64 ms in-process (routing 87.85, leaf review 71.32, permission judgment 74.50), 249.85 ms over HTTP, on one A800 80GB GPU, batch size one, bfloat16/SDPA, 200 recorded states. Agent runs: mean review time per normal task 1.33 s for the Jev-Guard gate versus 4.80 s for the LLM judge. These are archived native-task timings, not a controlled serving benchmark.

## Calibration

None. The permission threshold of 0.55 is fixed and "not a calibrated risk probability or a threshold optimized on these rollouts" (App. I).

## Cascade or escalation

Hierarchical routing then leaf review is a pipeline, not a confidence cascade. Permission gate: Jev-Guard completes 51 of 64 normal tasks and the LLM judge 57; both have zero covered policy violations and zero complete attacker goals, and the unguarded baseline also has none, so safety cannot be credited to either guard; 0 of 48 covered attacks has a Wilson upper bound of 7.41% (Sec. 5.5).

## Option-name, cardinality, order, robustness

Edit probes with a frozen model (Table 4): choice head correct on 21 of 30 rule-edit targets and 30 of 30 controls; safety head 30 of 30 targets and 24 of 30 controls; category edits: delete with fallback 50.00% (from 95.83%), reverse candidate order 75.00%, rename 83.33%; tree edits: inserting an intermediate group lowers routing accuracy from 95.00% to 86.00% (cyber 40 to 22 of 50). Candidate-order reversal affects category accuracy. Candidate lists limited to 512 in the HTTP interface. Tree versus full flat prompt: tree 3.53 times faster, full flat holds 73 leaves in 12,742 to 27,318 tokens and produces out-of-taxonomy categories on 115 of 128 cases (Sec. 5.4).

## Code and data availability

Project lead email given; no repository for Jev-Guard found. Linked repositories are third-party (Open-Jev, Hermes). Coded no.

## Authors' stated limitations

One checkpoint, limited set of policy edits, one actor API alias; edit cases constructed from explicit predicates, not independently annotated; five rule families and six category families give limited statistical power; the 200-case tree study is balanced across selected sources and does not estimate deployment prevalence; intervals exclude training-seed variation and future API changes (Limitations).
