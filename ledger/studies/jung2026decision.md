# jung2026decision — Where Can a Decision Model Diagnose HVAC Faults? Reasoning Demand, Physical Representation, and Robustness Under Shift

arXiv:2610.09937v1 [cs.AI], 7 Oct 2026 (journal template: Energy and Buildings). HTML retrieved from https://arxiv.org/html/2610.09937 (fulltext/2610.09937.html and .txt).

## Authors and affiliation

Wooyoung Jung, University of Arizona, Tucson, AZ, USA. Sole author. Declares no relationship with TypeSafe AI or Alibaba and "paid for all use of Jev personally" (Declaration of competing interest). Affiliation type academic.

## Task and data

Fault diagnosis for HVAC air-side equipment. Each input is a 60-minute window (15-minute stride, occupied hours) of operating data; three typed questions per window: "Which condition best explains this window?" (4 to 15 named options), a yes/no fault question, and a four-level severity scale (Sec. 3.2, 3.6, Table 4). 128 fault days from four public datasets of real equipment with imposed faults: ORNL rooftop unit (48 fault days, 14 fault-free), RP-1312 paired AHUs (49, 49), FLEXLAB (21, 5), Nesbitt Hall occupied building (10, 22) (Table 2). Faults graded by reasoning level L1 to L4 and U (unobservable): 5 L1, 66 L2, 52 L3, 5 L4 (Table 3). Four representations: R0 raw, R1 53 physical features computed in code, R1b named levels, R2 features plus Brick topology and latest point values (Sec. 3.4). Nine shift tests (season x ORNL 4 folds, season x RP-1312 3 folds, FLEXLAB control configuration, building RP-1312 to Nesbitt AHU-2) (Sec. 3.7).

## Decision models evaluated

Jev (TypeSafe AI, version jev-1.13.0), closed, accessed through OpenRouter at US$0.042 per million input tokens "at the time of the study"; every request and the model version Jev reports were stored (Sec. 3.5, 3.6). No run dates are stated. One version, one provider (Sec. 5.5). Jev receives all three questions in one request; no fixed seed available; three passes over the ORNL winter split gave the same top answer on 97 to 99% of windows (Sec. 4.7). Qwen2.5-Instruct 7B and 72B (4-bit, Ollama, local) as open language models with answer words' next-token probabilities read from the 20 most likely alternatives and rescaled; temperature 0, fixed seed (Sec. 3.6). LightGBM supervised model (fixed hyperparameters, not tuned); APAR rule set (detection only).

## Comparators and tuning parity

Same question wording and text input for every model. The question wording was tried once and revised once with Qwen2.5 7B on 100 ORNL trial windows (not set aside, 2.8% of ORNL map windows); Jev never saw the trial wording (Sec. 3.6). The frozen wording was not the best for Jev: paraphrasing class descriptions raised ORNL winter context accuracy from 13% to 43% (Sec. 4.1). LightGBM is trained on source data, the training-free models are not, and LightGBM hyperparameters were fixed on purpose. Letters replaced by words after the 7B model answered by position (Sec. 3.6).

## Reference labels

Faults were imposed on real equipment, so each fault day has known ground truth; labels are whole-day labels for three lab datasets and documented override windows for Nesbitt (Sec. 3.3). Observability flags and reasoning levels were assigned by one person before any model run. Coded task_outcome.

## n, sampling, intervals

n = 128 fault days; windows from one day are not independent, so 95% intervals come from resampling days 1,000 times (Sec. 3.8). Many intervals are wide (each fault intensity ran on one day).

## Test-set exposure

Public datasets collected 2007 to 2022 (ORNL RTU 2020 to 2022, RP-1312 2007 to 2008, FLEXLAB 2017, Nesbitt field data via ghalamsiah2026data). The author notes the datasets "may have appeared in the training data of the language models" (Sec. 5.5). Coded public-pre-2026. Harmonized splits and labels "available from the author on request"; no code repository stated.

## Cost and latency

190,582 requests to Jev; about US$0.0001 per request, 0.19 s mean, 0.26 s p95, two failed; about US$3.40 per unit-year at one check every 15 minutes. Qwen2.5 72B about 2 s per window for three questions and the 7B about 0.6 s on two NVIDIA RTX 5000 Ada GPUs (Sec. 4.7). (The study total spend is reported in the paper; not carried into the ledger.)

## Calibration

ECE with 15 equal-count bins (equal-width also reported, changes pooled values by at most 0.011), class-wise ECE, Brier, reliability diagrams (Sec. 3.8, 4.4, Fig. 4). Shifted-set ECE: Jev 0.27 (0.21 to 0.36) with features and 0.28 with R2, Qwen2.5 72B 0.43, 7B 0.60, LightGBM 0.36. Jev's ECE did not drift under shift (+0.01, -0.09 to 0.09) while LightGBM's rose by 0.25. Temperature scaling fitted on in-domain windows and applied unchanged: Jev R2 0.28 to 0.17; overshoots into underconfidence; raised Jev's ECE from 0.10 to 0.30 on RP-1312 summer. Isotonic regression for the fault probability did not improve detection (Sec. 4.4). Windows Jev answered at 0.94 mean probability were right 62% of the time (Fig. 4 discussion).

## Cascade or escalation

None; the paper recommends a division of work (physics in code, model ranks candidates, operator decides) and top-3 lists (Jev's top-3 contains the true fault on 65% of observable fault windows with R2, chance 46%; Sec. 4.1, 5.4).

## Option-name, order, robustness tests

Reversed or shuffled answer-option order lowered open models' macro-F1 by 0.03 to 0.05 (Sec. 4.3); Jev gets options as a named set; shuffling the state field order changed 3% of ORNL and 13% of RP-1312 Jev answers and made the yes/no answer flag 94% of fault-free RP-1312 windows; question paraphrase changed 3 to 6% of answers; irrelevant fields 2 to 6% (Sec. 4.1). Jev's yes/no answer contradicted its own condition answer on fault-free ORNL windows (84% "yes" vs 95% "normal"; Sec. 4.2). Window length 30/120 min, Brick form, 1-min step changed macro-F1 by at most 0.03.

## Code and data availability

Four public datasets; harmonized splits, labels and level assignments from the author on request (Intro, Conclusion, Data availability). No code link found. Coded partial.

## Paper's own limitations (Sec. 5.5)

Air-side faults in occupied hours only; one Jev version from one provider; no energy or comfort cost; possible LLM training exposure; no rule-tree baseline; answer-set size confounded with fault type and equipment; in-domain reference shares day conditions with training; prompt wording sensitivity; scarce fault days with wide intervals; one person assigned levels; part of consistency accuracy from logged-command faults.
