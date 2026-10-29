# saeed2026shift

arXiv 2610.34329v1 (cs.LG), 25 Oct 2026. "Shift-Jev: Certified Abstention and Gain-Gated Continual Adaptation for LLM-Based Decision Models under Distribution Shift." Authors Muhammad Atif Saeed, Azka Atiq, Akhtar Jamil (National University of Computer & Emerging Sciences, Islamabad), Adarsh Kumar (University of Arkansas at Little Rock, Data Engineer), Uzair Iqbal (University of Malaya), Roland Aydin (DFKI, Saarbrucken). Affiliation type: academic (one DFKI research institute, one data engineer). (title block)

## Task and data
- Decision models (probability over a fixed option set via numbered options, "Best answer: [" prefill, prefix-free trie scoring in one packed forward pass) under four shift types. ID tasks AG News, SST-2, BoolQ, ARC-Challenge (1,200 ID test items; train 500 or 250 per task, val 100, calibration 200, test 300); proxy shifts SciQ and Emotion (calibration only); test shifts: domain (Banking77 K=77, Twitter-Fin K=20, MMLU K=4; 500 each), class prior (AG News rho 10 and 100; 300 each), emerging classes (CLINC150 with none-of-the-above, 500, 50% out of scope), candidate set (rotation 204, paraphrase 153, near-duplicate distractor 204, gold removed); seven external benchmarks at base-paper sizes (6,456-7,456). (Sec. 4, Table 2)
- Reference labels: gold labels of public benchmarks (administrative); class-prior and candidate-set shifts are synthetic perturbations of those. (Sec. 4, 6.2)
- All public Hugging Face datasets, predating 2026; no contamination check. Fine-tuning mixture deliberately excludes the test shifts. (Sec. 4, 6.2)

## Decision models
- "LLM-as-Jev" recipe of Li and Wagle [7] (not the hosted Jev): Qwen3-0.6B, Qwen3-4B-Instruct-2507 (replaces the base paper's Qwen3.5-4B), frozen Phi-4-mini-instruct (one run). LoRA rank 16 alpha 32 all linear layers, AdamW lr 1e-4, one epoch, batch 8, anchor weight 1; three seeds (20260922, 13, 42) for the Qwen backbones. No model revision hashes except the 2507 tag; no run dates. TypeSafe Jev is cited but not evaluated; JevBench was not available. (Sec. 4, 6.2)
- Systems: B1 frozen, B2 fine-tuned with KL anchors, B3 plus temperature scaling, B4 uncertainty abstention with pooled Learn-then-Test (LTT), B5 full Shift-Jev reliability layer, B6 after continual adaptation. (Sec. 3.6)

## Comparators and tuning parity
- Abstention: max-softmax (MSP), energy, split-conformal LAC, all with the same pooled LTT certification except LAC; continual: naive sequential fine-tuning, EWC, Seq-FT+KL, experience replay, LwF; all start from the same B2 adapter with the same data, steps and LoRA capacity. (Sec. 3.6)
- Disclosed asymmetries: the method design was reached after earlier runs on the same benchmark exposed two failures; the stricter-of-two-thresholds rule is a post hoc finding; routing analysis re-certifies thresholds offline post hoc. (Sec. 5.3, 6.2)

## Results
Shift-averaged ECE: Qwen3-0.6B 0.289 (frozen) to 0.087 (B3), Qwen3-4B 0.182 to 0.078; 0.6B shift accuracy 57.5% to 64.2%; 4B unchanged (80.4% to 80.1%). Frozen 0.6B drops from 73.3% ID to 18.4% on Banking77 and 27.6% on Twitter-Fin (ECE 0.47, 0.58). Violations of alpha=0.10 in 27 environment-seed tests: B4 5 (0.6B) and 3 (4B), MSP 15 and 5, LAC 14 and 9, B5 4 and 6. At alpha=0.05 certified thresholds were mostly vacuous (abstain on everything). Continual adaptation final average accuracy: 0.6B Shift-Jev 70.48 +/- 0.88 versus LwF 68.10; 4B Shift-Jev 79.86 +/- 1.10 versus naive 81.22 (0.4 to 1.4 points behind). Label-shift chi-square test detects 95% (0.6B) and 99% (4B) of full-severity class-prior streams; confidence and embedding detectors 0 to 1%. (Sec. 5.2-5.5, Tables 4-14)

## Cost and latency
Packed trie scoring 72 ms per item (0.6B) and 92 ms (4B) on a T4; B2 fine-tuning 11.1 min (0.6B), 6.7 min (4B); four-stage Shift-Jev run 12.4 and 17.9 min. Kaggle sessions with two T4 GPUs, 8.1, 9.4 and 11.1 h for the three parts. (Sec. 4, 5.7)

## Calibration
ECE (equal-width bins, per-environment and shift-averaged), AURC, error AUROC; temperature scaling fitted on ID validation data; Learn-then-Test thresholds on a disjoint calibration half with Clopper-Pearson bound (delta 0.1). Even after fine-tuning, domain-shift ECE 0.08 to 0.17 versus ID 0.02 to 0.04. (Sec. 3.4, 5.2, Table 4)

## Cascade or escalation
No model cascade. Abstention coverage and realized risk at alpha=0.10: B5 answers 33.3% of shifted inputs at 5.2% risk (0.6B) and 60.1% at 6.2% (4B). (Table 5)

## Robustness
Option rotation, label paraphrase, near-duplicate distractor, gold-removed perturbations (near-duplicate distractor lowers 0.6B accuracy to 59.3% from 73.3%); candidate-set size sweep on Banking77; Phi-4-mini second family. Language not varied. (Sec. 5.2, Table 9, Table 17, Table 19)

## Code and data
Datasets public; implementation is a single Kaggle notebook "will be released with the camera-ready version" (not yet available). (Data and Code Availability)

## Authors' limitations (Sec. 6.2)
ID-only certification fails at alpha=0.05; routing by drift had little effect; 4B gate too conservative; gold-removed abstention varies across seeds; Phi-4-mini signals increased risk; three seeds and shared evaluation items limit statistical power; 4B comparison with the base paper uses a different checkpoint; class-prior and candidate-set shifts are synthetic; guarantees hold only under exchangeability; earlier designs were run on the same benchmark; only models up to 4B on single-GPU budgets.
