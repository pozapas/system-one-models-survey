# Yılmaz, Taşdemir & Gözay (2026), "LAVOIR: Teaching a Single-Pass Decision Encoder When and What to Ask with Amortized Value of Information"

## Identification
- arXiv 2609.30706v1 [cs.AI], 25 Sep 2026 (header). License CC BY 4.0. Full text fulltext/2609.30706.html and .txt.
- Authors Furkan Yılmaz, Habibe Aleyna Taşdemir, Muhammed Faruk Gözay; byline lists only personal gmail addresses and no institution. affiliation_type = independent. Compute from EuroHPC JUPITER (Jülich) via an AI Factories access call (Acknowledgments).
- The paper's own model is an open Laya extension; Jev appears only as a reported comparator on one benchmark table.

## Task and data
- Adds a value-of-information (VOI) head and a slot block to Laya (ModernBERT-large): one forward pass returns the decision distribution and, per candidate question slot, the expected gain in probability of the correct decision; a Gini-impurity cap bounds predicted VOI (Sections 3, 4).
- Controlled study: twelve authored customer-service schemas (eight train, four held-out zero-shot); gold units from schema rules, messages and answers verbalized by Qwen3.6-35B-A3B, texts checked by Gemma-4-26B-A4B for leakage and fidelity; 21,601 training, 5,379 seen-schema and 5,432 zero-shot test examples (Section 5). Exact Bayes ceiling computed by enumeration.
- Real conversations: 918 ABCD test dialogues (ten flows), 3,812 SGD first user turns (20 services, 2,766 from unseen services) (Section 5). External benchmarks: Laya's twelve (typed-decisions, Banking77, MASSIVE-en, ToxicChat jailbreak and toxicity, model routing on GSM8K/MBPP, RAG relevance, spam, phishing, AG News, DAIR Emotion, support triage), 400 cases per task, seed 13 (Table 3).

## Decision models
- LAVOIR (controlled arms RL0/RL1, per-type or per-group temperature; broad model; final model with Gini cap), single seed, ModernBERT-large. Trained 28 to 48 min on 8 to 16 GH200 GPUs. No version or date beyond the released weights moganai/lavoir (CC BY-NC 4.0).
- Laya and Jev numbers in Table 3 "are those reported by Laya (Jev's are third-party measurements); apart from Figure 1 we did not run Laya's checkpoints" (Section 6). Jev Banking77 uses 72 labels and n = 100.

## Comparators and tuning parity
- Question policies share the decision head: B2 never asks, B3 random slot when uncertain, B5 conformal-style prediction-set trigger, ORACLE greedy exact VOI (Section 6). Policy thresholds swept for all policies.
- External comparison to Laya and Jev is not matched: different training mixtures, Laya's numbers from its repository, latencies on different hardware (GH200 vs T4 vs API) (Table 3 caption; Limitations).

## Reference labels
- Controlled study: synthetic (rule-defined gold with exact posterior). ABCD flows and SGD intents are dataset annotations. Laya benchmarks use public benchmark labels; model routing derives from task outcomes.

## n, sampling, intervals
- Gap to Bayes ceiling with bootstrap 95% CI (case-clustered); ABCD gains with 10,000-resample paired bootstrap over cases. External benchmark accuracies are single-seed point estimates (400 cases) with no intervals. All runs use one seed (Limitations).

## Key results
- Seen schemas accuracy .653 vs ceiling .659, gap -.006 [-.016, .004]; zero-shot .517 vs ceiling .667 (Table 1). VOI policy AUC .799 vs ORACLE .797 (final); b0.5 .751 vs .610 never asking vs .663 random (Section 7.2); 14.1 points over never asking (Abstract).
- Gini cap: SGD question rate .93 to .086 at c = .02, SGD accuracy .948 to .942; ABCD gain where asks +8.3 [4.9, 11.7], where it does not ask -0.3 [-1.5, 1.0] (Table 2).
- Table 3: above Laya on seven of twelve sets, tied on spam, below on four (e.g. typed-decisions .774 vs Laya .766 vs Jev .727; AG News .905 vs .953 vs Jev .910; Banking77 .533 vs .492 vs Jev .870).

## Calibration
- ECE and KL to the posterior reported (Naeini et al. 2015; binning not stated). Temperatures fitted by L-BFGS on a 5% held-out slice; per-type temperature (Laya's recipe) made seen-schema KL ten times worse (0.004 to 0.04-0.06); per-group temperatures improve seen ECE five-fold but not zero-shot ECE (0.070-0.071 to 0.099-0.130). ABCD ECE .186 for LAVOIR, .222 uncapped (Table 2). Authors note calibration out of distribution is weak.

## Cost and latency
- LAVOIR p50 31 ms per question on GH200; Laya 33 to 40 ms (T4); Jev 236 ms (API, as reported by Laya) (Table 3; not comparable hardware). Independent third-party Jev median latency 236 to 276 ms cited from AbdelStark 2026 and nibzard 2026 (Related Work).

## Cascade or escalation
- Hand-off policy: with c_h = 0.3 the model hands off 18% of conversations and is 0.973 accurate on the rest (c = 0.02, RL0, seen schemas) (Section 7.1). Asking policy compared against oracle (above).

## Option-name, cardinality, language, robustness
- Option and slot orders are re-shuffled on every read (Section 4). Banking77 has 77 options. English only. Yes/no collapse on benchmarks with question-form instructions (spam 0.480 to 0.993 after adding question-form items) (Section 7.3).

## Test-set exposure
- Controlled test data new; benchmarks public; some benchmark training splits are in both LAVOIR's and Laya's training data (starred in Table 3); all 4,447 benchmark texts removed from yes/no training items (Section 5).

## Code and data
- Code https://github.com/moganai/lavoir (Apache-2.0); model https://huggingface.co/moganai/lavoir (CC BY-NC 4.0); general single-turn mixture not redistributed (Code and Data Availability).

## Paper's own limitations
- Synthetic dialogues and simulated answers; real-data tests are single exchanges; zero-shot decisions 15 points below ceiling; weak out-of-distribution calibration; 22% message rejection in the privacy schema; missing baselines (slow VOI, LLM agent, ablation of self-referential target); one seed; English; Laya numbers from its repository (Limitations).
