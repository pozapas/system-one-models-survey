# Zhou, Yang & Zhao (2026), "From Text Decisions to Pixels: An Study of Jev-Style Visual Choice Model" (PixelJev)

## Identification
- arXiv 2609.29283v1 [cs.AI], 24 Sep 2026 (header). License CC BY 4.0. Full text fulltext/2609.29283.html and .txt.
- Authors Xunlan Zhou (School of Intelligence Science and Technology, Nanjing University, Suzhou; intern at Microsoft Research Asia), Xianliang Yang and Li Zhao (Microsoft Research Asia) (byline, affiliation notice). affiliation_type = mixed.
- Note: the paper's own model is a Jev-style open implementation, not Jev. Jev is cited only for motivation (Introduction, Related Work).

## Task and data
- PixelJev: image + instruction + runtime candidate schema to a choice and candidate-conditioned probabilities, read from candidate-letter token logits at the first assistant position of Qwen3.5 (extended thinking disabled), 2 <= K <= 52 slots (Sections 3.1, 3.2). No generated text.
- Seven benchmark evaluations (Section 4): Oxford-IIIT Pets (37 breeds, 3,669 test), CIFAR-10, EuroSAT (fixed mirrored partition), CIFAR-10.1 v6 (2,000), DTD partition-1 test (1,880 images, 47 labels, no target fitting), A-OKVQA public validation (1,145 multiple-choice questions), ScienceQA image-containing test (2,017 of 4,241).
- Adaptation: one shared LoRA (rank 16, scale 32, dropout 0.05, three AdamW epochs, lr 1e-4) on 16 or 64 fitting images per class across the three source tasks (912 or 3,648 images), 684 development and 684 calibration images; seeds 7, 8, 9 (Section 3.3, 4.1). Pets development accuracy selects the checkpoint, which is reused for all tasks.

## Decision models
- PixelJev on Qwen/Qwen3.5-2B and Qwen/Qwen3.5-4B (References note Hugging Face URLs). No revision hash or run dates in the text. Runtime NGC PyTorch 25.11, Transformers 5.17.0, PEFT 0.18.1, NVIDIA GB10 shared system (Appendix B.1).
- Not evaluated: Jev itself and Visual Jev (Yu and Yao, 2026); "we have not run its system under a matched protocol" (Related Work).

## Comparators and tuning parity
- Frozen 2B, frozen 4B (same user-message interface and pixel budget 65,536 to 262,144), CLIP ViT-B/16 zero-shot, CLIP and DINOv2 ViT-B logistic-regression probes with 64 fitting examples per source class, regularization chosen on development data; frozen CLIP question-answer matching for VQA (Section 4.2, 4.4). Authors state per-task shots match but total supervision, trainable parameters and compute do not; "not compute-matched architectural ablations".
- Matched prompt-only follow-up on Pets and ScienceQA crossing frozen/adapted checkpoints with ordinary greedy generation (fixed parser, 128-token cap) versus direct candidate readout; common system format cue chosen on eight Pets development images by format compliance, not accuracy (Section 4.3).

## Reference labels
- Benchmark labels (Pets, CIFAR, EuroSAT, DTD, A-OKVQA, ScienceQA) as supplied; A-OKVQA multiple-choice scoring follows official answer-text scoring (Section 4.4). Coded human_single for single-annotator-style benchmark labels and human_crowd for A-OKVQA.

## n, sampling, intervals
- Full test sets. LoRA rows report mean ± sample SD over three optimization seeds (not uncertainty over training splits). Method differences use 2,000 paired bootstrap resamples of image-similarity groups; intervals are descriptive 95% without multiplicity correction (Section 4.5).
- Perceptual-hash grouping removes training groups touching test data from adaptation; all test images stay in the denominator.

## Key results
- Pets: frozen 2B 60.13, frozen 4B 70.65, 2B+LoRA 92.40±0.26, CLIP probe 91.99, DINOv2 probe 95.67 (Table 1). EuroSAT 49.63 to 88.31±1.57 (DINOv2 92.13). CIFAR-10.1 95.05±0.13 vs DINOv2 93.75. DTD 58.28±0.98 vs frozen 2B 45.85 and frozen 4B 64.79.
- A-OKVQA: frozen 2B 80.61, frozen 4B 85.07, LoRA 83.32, CLIP 59.21. ScienceQA: 81.51, 89.34, 82.35, 41.99 (Table 9).
- Matched follow-up: Pets 56.36 on both readout paths (frozen) and 91.63 on both (adapted); ScienceQA adapted 78.93 generation vs 80.81 readout, difference +1.88 pp [1.13, 2.86], entirely from 55 invalid generated outputs (Table 2; Section 5.4).

## Calibration
- Held-out scalar temperature fitted by NLL on a 684-image calibration split; source CIFAR-10 temperature transfers to CIFAR-10.1; no DTD or VQA temperature (Section 3.3). 15-bin ECE reported (Section 4.5); reliability plots use occupied equal-width bins (Figure 3). Pets 2B frozen ECE 0.1373 to 0.0684 after temperature; LoRA 0.0290 to 0.0143; DINOv2 probe worsens (0.0055 to 0.0101) (Table 5). DTD adaptation lowers NLL (2.6985 to 1.9253) but raises mean raw ECE (0.1905 to 0.2040) (Section 5.5). Authors: accuracy gains do not ensure calibrated target probabilities.

## Cost and latency
- Warm batch-one timing on fixed 64 images, three repetitions: direct readout 94.7 to 133.5 ms mean (P95 112.2 to 154.6 ms); ordinary generation 1.32 to 1.44 times direct (about two tokens per response); constrained one-token path 1.03 to 1.04 times direct (Table 11; Section 5.4). Authors: no intrinsic speedup from omitting the token; implementation-specific, not an optimized engine benchmark.
- Adapter 7,382,016 trainable parameters; 64-shot summed optimizer-step time 3,220.25 to 3,373.94 s on a shared GB10 (Appendix Table 7).

## Cascade, option-name, cardinality, robustness
- No cascade. Candidate reversal, alternate instruction and different-class image substitution diagnostics in Appendix D (not extracted). Cardinality: DTD 47 labels exceed the 37-slot adaptation vocabulary (ten slots never positive during fitting). No language tests.

## Test-set exposure
- All benchmarks are public, released before 2026; "None establishes exclusion from unknown foundation-model pretraining" (Related Work). Perceptual-hash overlap check of adaptation data vs CIFAR-10.1 and DTD flags no images (Section 5.2).

## Code and data
- No repository or artifact link found in the text.

## Paper's own limitations (Section 6)
- One adaptation split, three seeds, one VQA adapter seed; pretraining overlap unknown; DTD changes several factors together; EuroSAT spatial correlation; VQA answerable from text alone; native processors and supervision differ; fixed nonthinking interface not each backbone's best; candidate confidence is not a trust decision; no matched comparison with Visual Jev.
