# liu2026retijev

arXiv 2610.30947v1 (cs.CL), 22 Oct 2026. "RetiJev: Fast and Source-Grounded Ophthalmic Decision Models." (title block)
Authors: Bo Liu, Lianyu Wang, Meng Wang, Ching-Yu Cheng, Huazhu Fu. Affiliations: National University of Singapore (Yong Loo Lin School of Medicine; Centre for Innovation and Precision Eye Health), Singapore Eye Research Institute, Duke-NUS, University of Washington, A*STAR. Affiliation type: academic. (title block)

## Task and data
RetiJev-Data: 78,158 clinical-decision and diagnosis questions derived from PubMed Central articles and a 531-disease MeSH vocabulary (LLM-extracted rules, LLM-generated synthetic patients, labels cross-verified by a different model family and two further families for disputes) and 50,074 guideline-grading questions over 11 grading systems (labels computed by code from sampled parameters; notes rendered by an LLM and checked by parameter re-extraction). Splits: 94,561 train, 9,009 development, 24,662 test. Test sets: Decision-Unseen 4,625, Decision-Seen 3,106, Diagnosis-Unseen 164, Diagnosis-Seen 224, Grading-OOD 3,983, Grading-Hard 4,230 (plus grading reference sets 8,330). Unseen means rule families excluded from training. (Sec. 3, Table 1)
Reference labels: model-verified (not clinician-adjudicated) for decisions; synthetic code-computed for grading. All patient states synthetic; no prospective evaluation. (Sec. 6)

## Models
Own model: RetiJev 0.8B, 2B, 9B (Qwen3.5 backbones, LoRA, shared pointer head, one prefill per case, training objective with cross-entropy, RPS, teacher distillation from Qwen3.8-27B, paraphrase consistency). Comparators: Qwen3.8-27B zero-shot with letter scoring (reasoning disabled), MedJev 0.8B zero-shot, and Jev 1.13 zero-shot via API ("typesafe/jev-1.13-20260917, served through OpenRouter" in the reference list), one question per request. No exact run dates stated. Comparators are not fine-tuned; RetiJev is trained on in-domain data (stated as the benefit of targeted supervision). (Sec. 4, 5.1, references)

## Results (Table 2, micro accuracy, 2,000 bootstrap resamples over cases, paired 95% tests)
Jev 1.13: Decision-Unseen 79.5, Decision-Seen 77.4, Diagnosis-Unseen 84.8, Diagnosis-Seen 90.2, Grading-OOD 83.0, Grading-Hard 79.4. RetiJev-9B: 84.9, 83.9, 84.8, 91.5, 97.3, 96.3. RetiJev-0.8B: 80.3, 80.5, 68.9, 86.2, 95.9, 89.8. Qwen3.8-27B: 79.5, 77.8, 84.8, 90.6, 77.6, 73.3. Gains on grading 10.4 to 23.0 points; diagnosis sets are small. Per-cell intervals are not given in the main text. (Sec. 5.2)

## Cost and latency
Median per-case latency on one H200, batch size 1 (2.65 questions per case): RetiJev 133 ms (0.8B), 136 (2B), 158 (9B); 27B letter scoring 247 ms; 27B short answer 546 ms; 27B with reasoning 74,489 ms; Jev API latency not measured (marked API). 0.8B on 8 CPU cores 347 ms. (Sec. 5.3, Table 3)

## Calibration and deferral
Decision-Unseen ECE 0.033 (0.8B), 0.016 (9B), against 0.033 and 0.027 for the two zero-shot baselines (order of baselines not stated in the sentence); risk-coverage areas 0.072 and 0.045 versus 0.079 and 0.080; at 80% coverage accuracy 87.8% and 92.1%, with 51% and 58% of errors in the deferred 20%. ECE binning not stated. No post-hoc recalibration. (Sec. 5.4)

## Robustness
Paraphrase augmentation ablation (Table 10), unseen-renderer OOD, threshold-hard cases; option-order tests not reported in main text.

## Test-data exposure
New synthetic benchmark; MeSH and PMC sources public. Teacher queries confined to training data.

## Code and data
Models released at https://github.com/Awenbocc/RetiJev.

## Authors' limitations (Sec. 6)
Labels source-grounded and cross-verified but not clinician-adjudicated; all patient states synthetic; no prospective evaluation.
