# demir2026commit

arXiv 2610.29961v1 (cs.AI), 21 Oct 2026. "Commit or Abstain? System One Decision Models, LLMs, and Missing Legal Authority." (title block)
Author: M. Mikail Demir, Department of Information Science, University at Albany, SUNY. Affiliation type: academic. (title block)

## Task and data
CaseHOLD test split (5,314 items: excerpt plus five candidate holdings). Abstain condition: in a random 31% (1,670 items) the correct holding is replaced by a real holding from another case (highest TF-IDF similarity, cap 0.75; mean similarity 0.28) and a sixth option "none of the listed holdings" becomes correct; in the other 3,644 items the sixth option is wrong. Metrics: accuracy, macro F1, wrong-pick rate (picked a holding when none correct), false-abstention rate, ECE (ten bins), AUROC of the none probability. 95% percentile bootstrap (2,000), exact McNemar. (Sec. 3.1, 3.2, 3.5)
Reference labels: court-stated holdings taken from opinions (CaseHOLD gold), abstain condition built programmatically.

## Models
Decision models: Jev 1.14 (TypeSafe), pplx-decider v1.2 (Perplexity), d1-ultra (Liquid AI), GPT-6 Luna Decisions (OpenAI), via OpenRouter decisions interface; no further version strings or run dates beyond "October 2026". Generative LLMs: Gemini 3.8 Flash, Claude Haiku 5.5, GPT-6 Luna, Mistral Small 2603, GLM 5.3 Flash, GPT-4o-mini, temperature 0 at the lowest reasoning setting above none, one-sentence identical instruction, structured JSON key output, no confidence requested. Claude Haiku 5.5 abstain results cover 5,313 items (one refusal). Batch versus sync billing differs by model. (Sec. 3.3, 3.4, Table 1)

## Results (Table 2; cost per 1,000 questions in original condition)
Accuracy original/abstain: Jev 1.14 78.3/63.9 (US$0.035), pplx-decider 88.1/73.1 (0.012), d1-ultra 84.9/73.6 (0.021), GPT-6 Luna Decisions 72.2/58.2 (0.058), Gemini 3.8 Flash 88.2/78.4 (0.659), others lower. Wrong-pick: Jev 30.1 [27.8, 32.3], d1-ultra 41.0, pplx 56.5, GPT-6 Luna Decisions 60.8, Gemini 37.8, GPT-4o-mini 85.6. False abstention: Jev 26.2, every generative LLM under 8%. AUROC of none probability 0.726 to 0.887. pplx-decider ties Gemini on the original task at about 1/55 of the cost. (Sec. 4.1, 4.2)

## Calibration
ECE (ten bins) reported for decision models and the distilled student; Jev 0.056 on abstain condition; no post-hoc temperature for decision models. (Table 3)

## Cascade
Veto, agreement gate, System-One-first policies; thresholds tuned on a random 30% and results on the remaining 70% (3,720 items). Agreement gate (Gemini 3.8 Flash with pplx-decider): wrong citations 18.4% to 9.4%, reviews 3.0% to 12.7%, correct answers 78.5% to 78.0%, extra cost about 1%. GLM 5.3 Flash gated by pplx-decider gives 12.8% wrong citations at about one-ninth of Gemini's cost. Cost weights k=1, 5, 10 are illustrative. (Sec. 4.3)

## Distillation
Qwen3-8B LoRA on 10,000 abstain-condition training items using Jev's probabilities only: accuracy 63.8 (teacher 63.9), ECE 0.025 (teacher 0.056; untuned 0.504), AUROC 0.777; gold-label student 74.9. One run each, one A6000. (Sec. 4.5, Table 3)

## Robustness and exposure
Contamination checks (anonymization, citation only) in Appendix C; CaseHOLD built from public opinions before 2021, training data of closed models undisclosed. One prompt per model type, English US case law only. No option-order test reported in main text.

## Code and data
https://github.com/mmikaildemir/commit-or-abstain (code, data, outputs of every model).

## Authors' limitations (Sec. 6)
Contamination cannot be excluded; constructed form of absence; k values illustrative; one task, one prompt per model kind, results describe October 2026 versions; distillation single run.
