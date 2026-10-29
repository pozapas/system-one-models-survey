# tran2026can — Can Multimodal Decision Models Classify Breast Ultrasound Images? Benchmarking CLEF and CLEF-Flash Across Prompts and Datasets

- arXiv: 2610.13675v1 [eess.IV], 9 Oct 2026, CC BY 4.0 (header). Full text: fulltext/2610.13675.html and .txt.
- Authors (header, listed as printed): Tran Cao Minh (Research and Development Center, VNSO Technology JSC, Ho Chi Minh City), Hai Tran (Ho Chi Minh University of Education), Ha Minh Tan (University of Information Technology, Vietnam National University, Ho Chi Minh City). The cited self-reference is "Cao Minh et al. (2026)", so the first author's surname is ambiguous (Vietnamese name order); key uses "tran" as the first word of the byline, as in the screening list (first_author "Tran Cao Minh"). Affiliation type: mixed (one industry R&D centre, two universities).
- Code: "The designated repository for the study code is https://github.com/CaoMinhh/clef-breast-ultrasound" (Code Availability). Data: three public datasets, Dataset B needs a licence agreement (Data Availability).

## Task and data
Image-level breast ultrasound classification with a multimodal decision model (Section 3). Datasets: Dataset B (163 images: 109 benign, 54 malignant), BUSI (780: 133 normal, 437 benign, 210 malignant; three classes), BUS-BRA (1,875: 1,268 benign, 607 malignant); total 2,818 images (Table 1, Section 3.2). Reference labels are the datasets' own labels; the paper does not describe how they were produced (coded human_single as "dataset labels, process not described"). Ground-truth labels never appear in the input (Section 3.1).

## Decision models, versions
Cloudflare CLEF (backbone Qwen3.8-27B, ~27B parameters) and CLEF-Flash (Qwen3.5-9B, ~9B), "publicly released pretrained weights", no fine-tuning, no preprocessing (Section 2, 3.1). Model cards and source accessed 2026-10-04 (references; code revision a20e258 refers to the CLEF response implementation, not model weights). No model revision hash or run dates given. Inference: one NVIDIA A100 80 GB, Ollama 0.35.1, FP16; GPU memory 22,364 MiB (CLEF) and 13,741 MiB (CLEF-Flash) (Section 3.3). Probability of each label taken from the choice question; argmax is the prediction (Eq. 5).

## Design and comparators
3 datasets x 2 models x 3 prompts (P1 minimal labels, P2 task-guided, P3 sonographic criteria) = 18 configurations (Section 3.1, Table 2; prompts in Section 7). Comparators are the other CLEF model and the prompt variants; no supervised ultrasound model, biomedical foundation model or radiologist under the same protocol (Section 5.4). The majority-class predictor on BUS-BRA gives 67.63% accuracy (Section 5.2). Prompt selection is shown for all three prompts, not tuned on a separate set, but each is evaluated on the same test images, so "best prompt" is post hoc.

## Main results (Table 3)
Accuracy / macro F1 / balanced accuracy / macro precision / latency (ms per image):
- Dataset B (n = 163): CLEF-Flash P3 74.85 / 73.70 / 76.52 / 73.65 / 2185.08; CLEF P1 70.55 / 68.76 / 70.51 / 68.54 / 7971.36; CLEF P3 65.03 / 64.95 / 71.52 / 70.23 / 7959.96.
- BUSI (n = 780): CLEF-Flash P3 66.28 / 63.49 / 66.60 / 67.85 / 3272.62; CLEF P2 65.13 / 64.51 / 68.72 / 67.42 / 6221.19; CLEF P1 65.77; CLEF P3 59.87.
- BUS-BRA (n = 1,875): CLEF-Flash P3 51.63 / 51.39 / 61.79 / 63.64 / 2746.68; CLEF P3 40.32 / 37.04 / 55.23 / 63.26 / 3782.60.
- BUS-BRA recalls (Section 4.2): CLEF P3 malignant recall 97.53% (592/607) and benign recall 12.93% (164/1,268); CLEF-Flash P3 malignant 90.61% (550) and benign 32.97% (418).
- CLEF-Flash speedups over CLEF 3.30 to 3.64 fold (Dataset B), 1.85 to 1.91 (BUSI), 1.30 to 1.38 (BUS-BRA) (Section 5.3).
- Clinical prompt P3 improves CLEF-Flash accuracy on all three datasets relative to P1 but reduces CLEF accuracy on all datasets (Section 5.1).

## Intervals, calibration, cascade
No confidence intervals or paired tests (Section 5.4). Probability calibration and confidence-based selection are explicitly not assessed; the paper also notes that the CLEF confidence field is p_max, whereas TypeSafe defines a normalised confidence (Section 2). No cascade, no option-name or language test.

## Cost and latency
Throughput (FPS 0.125 to 0.458) and latency per image on the A100/Ollama setup (Table 3). No monetary cost.

## Test-set exposure
Public datasets (Dataset B 2018, BUSI 2020, BUS-BRA 2024); "The evaluation does not determine whether related images appeared in the models' original training data" (Section 5.4).

## Limitations (Section 5.4)
Descriptive point estimates only; no calibration; image-level, not patient-level, and no accounting for within-patient dependence; no matched baselines; training-data exposure unknown.
