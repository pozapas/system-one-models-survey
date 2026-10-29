# paramasivam2026rubrix

arXiv 2610.34875v1 (cs.CL), 26 Oct 2026. "RubriX: A Fast, Fine-Tunable Non-Autoregressive Rubric Judge." Authors Balamurugan Paramasivam, Sudalai Rajkumar, CobuildX. Affiliation type: industry. (title block)

## Task and data
- Rubric-level judging: choose which level of a rubric a response meets; probability over the rubric's own K levels. Held-out test set 6,749 judgments (Feedback Collection 4,999, proprietary 1,172, HelpSteer3 principles 378, HelpSteer 100, HelpSteer2 100) with criteria and level descriptions never in training; eight human-labelled benchmark sets: HealthBench 29,511, BiGGen 3,194, ELLIPSE 45,374, SummEval 6,400, JudgmentBench binary 17,365, JudgmentBench multi-level 2,782, QAGS-CNN 235, QAGS-XSUM 239. (Sec. 4.2, 5.1, Table 2)
- Reference labels: held-out set labels are LLM-generated (Feedback Collection, proprietary data generated with an LLM and filtered by blind re-grading); benchmark sets use physicians, human raters, trained raters, experts, lawyers, crowd workers; gold level is the level nearest the raters' mean, halves to the lower level. (Sec. 4.1, 4.4, Table 2)
- Public benchmarks (2020 to 2026) with no contamination check; held-out set is from training sources, split by criterion; validation partly shares criteria with training. Generic level descriptions were added where benchmarks lack them, same for all judges. (Sec. 4.1, 4.2)

## Decision models
- RubriX-8B: Qwen3-8B encoder with LoRA (rank 16) and two projection heads, scaled cosine similarity softmax over levels; trained 1 epoch on 34,261 examples (2,284 criteria), checkpoint step 1,068; HF CobuildX-AI/RubriX-8B, no hash. (Sec. 3, 4.5)
- Jev (hosted TypeSafe): one score question per judgment; version and access dates not reported; at most 10 options per question. Qwen3-8B zero-shot judge (thinking off, first-token letter softmax) as a non-decision-model baseline; G-Eval results copied from its paper. (Sec. 2, 4.3)

## Comparators and tuning parity
- RubriX is fine-tuned on in-distribution rubric sources while Jev is used zero-shot and not tuned, so the held-out comparison favours RubriX (authors note the held-out rubrics come from training sources and measure generalisation to new criteria of a familiar kind). Benchmarks are out-of-distribution formats for RubriX. Qwen3-8B judge gets the same inputs. (Sec. 5.1, 6)

## Results
Held-out: exact accuracy RubriX 75.4%, Jev 57.1%, Qwen3-8B judge 49.8%; within one level 97.6%, 89.6%, 88.4%. Benchmarks: Jev highest exact accuracy on six of eight sets; QAGS-CNN Jev 82.1 vs RubriX 80.4, QAGS-XSUM 78.7 vs 75.7, SummEval gap 11.6 points, JudgmentBench binary gap 14.1; JudgmentBench multi-level within-one RubriX 96.4 vs Jev 42.4. Ranking: Jev SummEval Spearman rho 0.541, RubriX 0.483, G-Eval-4 0.514; QAGS average Jev 0.684, RubriX 0.620. Most per-benchmark accuracies appear only in Figures 3 and 4. No confidence intervals, single run. (Sec. 5.1-5.3, Table 3)

## Cost and latency
Median per-judgment latency, one request at a time, 110 judgments per setting, dummy text: RubriX with cached level embeddings 27.5 to 28.3 ms in every setting (H100, vLLM); Jev 73.1 to 199.7 ms from 2 to 10 levels and 44.0 to 210.9 ms with level length 10 to 3,000 tokens, with an approximate 232.6 ms network time subtracted; Qwen3-8B judge 108.5 to 1,241.3 ms. RubriX cache miss 108.2 to 4,090.2 ms. Training 2.8 h on one H100 (10,212 s, 32.4M tokens). Jev timed through its API, so infrastructure differs. (Sec. 5.4)

## Calibration
No calibration analysis (no ECE or Brier); ranked probability score used as a training loss; temperature fixed at 100. (Sec. 3.2)

## Cascade or escalation
None.

## Robustness
Level count 2 to 100 and level length 10 to 3,000 tokens (latency only). No option-name or language tests. (Sec. 5.4)

## Code and data
RubriX-8B weights and loading code on Hugging Face; training data partly proprietary. (Sec. 1, 4.1)

## Authors' limitations (Sec. 6)
Separate encoding of input and levels; 8B encoder capacity; strong dependence on fine-tuning data, trails Jev on benchmarks of other formats; second epoch raised validation log-loss.
