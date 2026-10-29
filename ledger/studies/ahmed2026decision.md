# ahmed2026decision

arXiv 2610.15029v2 (cs.CL), v1 10 Oct 2026, v2 21 Oct 2026 (read v2). "Is a 9B Decision Foundation Model Needed for Symptom-to-Disease Classification? Fine-Tuning Clef-Flash Against TF-IDF Baselines." Single author S. M. Mahbub Uddin Ahmed, Department of Computer Science and Engineering, United International University. Affiliation type: academic. (title block)


## Task and data
- 24-class symptom-to-disease classification on Symptom2Disease (Kaggle, Barman 2023), 1,200 short first-person narratives (50 per class, 12-55 words, mean 30.73). Stratified 80/20 split, 960 train and 240 test (10 per class), seed 42. (Sec. 3.1, 3.3)
- Reference labels: dataset class labels; provenance of narratives undocumented, authors do not assume real patients (administrative/dataset field; possibly synthetic). (Sec. 3.1, Sec. 6.2 item 1)
- Test data public (Kaggle) and predate 2026; no contamination check. (Sec. 3.1)

## Decision model
- Clef-Flash (9B, Qwen3.5-9B backbone + JointSchemaHead, Cloudflare), Hugging Face Cloudflare/clef-flash; no revision hash or API model version string given. Also Clef 27B (Qwen3.8-27B + head) zero-shot via Cloudflare Workers AI. (Sec. 1, Table 1)
- Zero-shot run two ways: local 4-bit weights (65.00%) and remote Workers AI API (62.92%); zero-shot with MedlinePlus criteria in prompt 61.67% (Clef-Flash) and 67.92% (Clef 27B). Dates of API runs not given. (Sec. 4.1)
- Fine-tuned Clef-Flash: 4-bit QLoRA, rank 16, alpha 32 on q,k,v,o; head lr 3e-4, backbone adapter lr 1e-4; 5 epochs; effective batch 16; single run. 34.58 min on one RTX 4090; adapter 247.31 MB. (Sec. 3.6, App. G)
- Decision schema: state = narrative, one choice question with 24 options; criteria set to None. (Sec. 3.2)

## Comparators and tuning parity
- TF-IDF (uni/bigram) linear SVM, logistic regression, random forest trained on the same 960 and tested on the same 240; hyperparameters chosen by 5-fold CV on training data only; evaluated once. (Sec. 3.4)
- Asymmetry: the fine-tuned decision model was checkpoint-selected on test accuracy (epoch 4, no validation set), so its 95.42% is optimistically biased; baselines were evaluated once after CV tuning. Single training run. (Sec. 3.3)
- Literature numbers (CLIN-LLM 98%, TF-IDF+LSTM 98.8%, FDSDD-LCEHOA 98.37%) are on other splits and not comparable. (Table 1 Panel B)

## Results
Fine-tuned Clef-Flash 95.42% accuracy (229/240; Wilson 95% CI 91.98-97.42), macro F1 0.9551, 11 errors; TF-IDF linear SVM and LR 98.75% (237/240; CI 96.39-99.57; macro F1 0.9876), RF 96.67%. Zero-shot 62.92% API, 65.00% local, Clef 27B zero-shot 66.25% API. No paired test (per-case predictions not retained). (Table 1, Sec. 4.1)

## Cost and latency
Baseline CPU latency 0.7 ms (SVM), 0.8 ms (LR), 45 ms (RF) on AMD Ryzen 7 250 laptop CPU. Zero-shot API latency 0.80 s (Clef-Flash), 0.92 s (Clef 27B) per request including network. Fine-tuned model local latency and memory not measured. (Table 1, App. G)

## Calibration
Not evaluated ("Probability calibration was not evaluated"). (Sec. 6.2 item 6)

## Cascade or escalation
None.

## Robustness
Leave-One-Symptom-Out clause ablation on four author-written narratives (not from dataset): psoriasis hallmark clause removal drops probability from above 99.99% to 0.12% and flips to impetigo; secondary clauses change by under 0.001 points (psoriasis) and up to 0.67 points (arthritis). Case studies only, clause categories author-assigned. (Sec. 5, Table 3). No option-name, cardinality or language tests.

## Code and data
Code, splits, rubrics and scripts at https://github.com/hrid0yyy/clef-clinical-triage. Dataset public on Kaggle. (Sec. 1 contributions)

## Authors' limitations (Sec. 6.2)
Small corpus with undocumented provenance; short narratives; closed 24-class ontology; no external validation; checkpoint selected on test accuracy, single run, no paired significance test, no local latency, calibration not evaluated; ablation on four author-written narratives without clinician review.
