# chen2026rsajev

arXiv 2610.15742v1 (cs.CV), 11 Oct 2026. "RSAJEV: Training-Free Abstaining Prototype Memory for Eliminating Silent Hallucination in JEV-Based Remote Sensing Classification."
Authors: Man Chen, Antai Chen, Shuai Xu, Chengjie Gu, Huaping Zhou, Kelei Sun, Tao Wu (Anhui University of Science and Technology, Huainan; Man Chen also Tianjin University; State Key Laboratory of Digital Intelligent Technology for Unmanned Coal Mining), Yongjie Huang (Guangxi Normal University). Affiliation type: academic. (title block)

Scope note: "JEV" in this paper is the remote-sensing one-pass decider RSJEV (Si et al. 2026, arXiv 2610.08539), not TypeSafe's hosted Jev. It is an open one-pass MLLM scene classifier: lettered options in the prompt, a registered [ANS] slot, class read out by scoring letter tokens (single forward pass, no free-text generation). I treat it as an open one-pass decision model. The paper never mentions TypeSafe or Jev-1.x. (Sec. I, III-A)

## Task and data
- Remote sensing scene classification: UCM (21 classes, 2,100 images, 50/50 split), AID (30 classes, 10,000 images, 20/80 split, n=8000 test), NWPU-RESISC45 (45 classes; unseen target vocabulary only). Seed-42 splits "released with the code". Open-set: UCM 14 seen/7 unseen; AID 20 seen/10 unseen (n=8000). (Sec. IV-A, Tables III-VI)
- Reference labels: standard benchmark class labels (single human annotation per scene; not described further). All three datasets public pre-2026.

## Models
- Backbone Qwen3.5-0.8B (multimodal) with LoRA letter-slot fine-tuning ("RSJEV" style). Evaluated: (a) official released AID weights of the original RSJEV paper evaluated under the released configuration; (b) the authors' own UCM weights trained under the official protocol (AdamW, 10 epochs; stopped at 1 epoch by validation accuracy). No version identifier or checkpoint hash is given. (Sec. III-A, IV-B, IV-C)
- RSAJEV (proposed): training-free prototype readout over cached slot representations (K = 16 references per class, mean aggregation) with shrinkage-Mahalanobis metric; lambda selected "once on a shared validation grid by per-setting accuracy" (default 0.02; held-out data) and some open-set tables report lambda values 0.05, 0.1, 0.5 chosen per table. Controls: letters (symbolic trained readout), cos_t2 (text template cosine), proto (cosine prototype). (Sec. III-B, IV-B, Tables III-VI)

## Comparators and tuning parity
All readouts run on the same cached forward pass. The proposed readout uses 16 labelled reference images per class from the training split (leakage assertion), plus a covariance estimated from the target-domain reference pool (336 references for UCM target), while the "letters" control receives no target-vocabulary data in cross-dataset directions. Lambda varies by setting (selection partly on test-setting grids; stated "no per-dataset tuning" for the closed-set table but per-table values for open-set). Comparator numbers for the official weights are re-evaluated by the authors; official report numbers also quoted. (Sec. IV-B, IV-D)

## Results
Closed set: official AID weights 97.39% OA / 97.16 F1 (official report 96.56/96.30; UCM official 97.71/97.72). Cross-dataset gate OA (Table II, letters vs maha): AID->UCM 21.52 vs 89.43; UCM->AID 96.40 vs 96.90; AID->NWPU 7.35 vs 78.52; UCM->NWPU 34.29 vs 77.99; UCM in-domain 78.10 vs 89.05; AID in-domain 97.39 vs 97.40 (proto 97.51). Single run, single seed, no intervals reported. (Table II)

## Open-set
AUROC of ID-ness: UCM 14/7 official (out-of-vocabulary) weights letters 0.3853, maha 0.9147; UCM retrained on 14 seen classes letters 0.7642, maha 0.9426; AID 20/10 UCM-trained weights letters 0.7323, proto 0.9936, maha 0.9865; AID retrained letters 0.9630, maha 0.9937 (proto 0.9911). No confidence intervals. (Tables III-VI)

## Calibration
No ECE or Brier. Confidence assessed as AUROC / FPR@95TPR / OSCR for open-set rejection and coverage-accuracy curves (Fig. 3). Thresholds "calibrated only on held-out in-domain data". Score fusion did not help. (Sec. IV-A, IV-E)

## Cost and latency
Full fp32 pipeline on RTX 4090, batch size 1: 232.49 ms mean per image (min 184.71, median 233.46), 4.3 FPS, 3.22 GiB peak memory; 30 UCM test images after 5 warm-ups. Original paper's comparison figure came from an A40 and is not directly comparable. All readouts share one forward pass, so no extra inference cost. (Sec. IV-G)

## Cascade or escalation
None (abstention via ID-ness threshold only; coverage-accuracy: AID->NWPU accuracy at 10% coverage 95.77 for maha, 87.30 cosine, 14.29 symbolic).

## Robustness
Column-pruning (21 to 14 classes): text and prototype readouts move at most 3.7 points; vocabulary-size changes across 21/30/45 classes; option-name and language tests not done.

## Code and data
Splits "released with the code"; no URL or repository given in the text. Weights: official RSJEV release. Treat as not stated.

## Authors' limitations
No dedicated limitations section. Conclusion notes remaining headroom lies in the representation, and extension to dense prediction and multi-label vocabularies is future work.
