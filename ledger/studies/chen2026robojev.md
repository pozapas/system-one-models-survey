# chen2026robojev

arXiv 2610.33718v1 (cs.RO), 24 Oct 2026. "RoboJev: An Open Vision-Language Judge for Robot Success Detection." Single author Josef (Liyanjun) Chen, Independent Researcher. Affiliation type: independent. (title block)

## Task and data
- Robot manipulation success detection: task instruction + 10 evenly spaced primary-camera frames (+ final frame of auxiliary cameras) -> P(success). Binary decision (false/true) read from two answer-token logits in one forward pass. (Sec. 3.1, Eq. 1)
- Three test settings, 862 binary-labelled episodes of 927 (65 community clips ambiguous, excluded): SO-101 held-out ArmnetBench rollouts n=268 (111 success, 157 failure; 80 of them from two withheld tasks); unseen lab/robot domains from RBM-1M OOD n=459 (8 domains); community LeRobot videos n=135 clear (60/75). (Sec. 4.1, Table 1)
- Reference labels: SO-101 and RBM-1M OOD labels are benchmark-supplied success/failure fields (provenance of ArmnetBench labelling not described); community test labels by one human annotator, no inter-annotator agreement. Training labels for community data are an LLM-teacher consensus (GPT-6 Astra, GPT-6.1 Sol, Claude Opus 5.5) that overlaps the API baseline panel. (Sec. 4.1, 7, App. C)
- Test data public Hugging Face datasets, 2026 dated releases; pretraining overlap cannot be excluded; test sets "were inspected while creating the released models", not a one-shot blind test. (Sec. 3.3, 7)

## Decision models
- RoboJev-27B: LoRA rank 32 on language model of JEV-27B-VL (autotrust, Qwen3_5 architecture class), 52,598 training episodes, source-specific KL anchor, temperature T=0.9; pinned commit e089a9b69a365744b80765057d86583647af95a9 released 23 Oct 2026. (Sec. 3, App. A Table 2)
- Decision-model comparators (4 primary-camera frames, clip-v1): TypeSafe Jev 1.14, TypeSafe Jev 1.13, Perplexity Decider (pplx-decider-v1.2) and Flash v1.2, Liquid D1 and D1 Ultra, Mercury Decide, Cloudflare Clef, Clef Flash, Clef Omni, Intern-Decision-4B, GPT-6 Luna Decisions, Respan Span-02, Robometer-4B (full video). Identifier strings in Table 5; no run dates given for the recorded API calls. (App. B Table 3, Table 5)
- Chat frontier baselines GPT-6 Astra (medium reasoning), GPT-6.1 Sol, Claude Opus 5.5, Claude Sonnet 5.5 returned a requested numeric probability. (App. B.2)

## Comparators and tuning parity
- Non-like-for-like: RoboJev and the matched-input base JEV-27B-VL get 10 frames plus auxiliary views; API baselines get 4 primary-camera frames; Robometer gets full video. Only the base-model row is input-matched (identical image hashes). (Abstract, Sec. 4.2, 5.2)
- RoboJev adapter scale and temperature were chosen on held-out validation sources; one training run, no seeds. (Sec. 3.3, 5.4)

## Results
SO-101 n=268: RoboJev balanced accuracy 95.2%, AUROC 0.993, ECE 0.032; base JEV-27B-VL (10 frames) 88.1%, 0.979, ECE 0.114; paired difference +7.08 pp [3.04, 11.45]. GPT-6 Astra 93.3% (paired +1.91 pp [-1.56, 5.21]). Jev 1.14 82.9% BA / 0.975; Jev 1.13 79.4% / 0.936. Held-out tasks n=80: RoboJev 92.5%, four-frame Astra and Sol 96.3%. Unseen domains n=459: RoboJev 78.2% / 0.890, base 79.4% / 0.900 (AUROC diff -0.0092 [-0.0218, 0.0026]); Jev 1.14 72.1% / 0.841. Community n=135: RoboJev 93.3% accuracy, Opus 94.1%. (Sec. 5.1-5.3, Tables 3-4)

## Cost and latency
Median 0.257 s per answer serial on one H100, about 0.192 USD per 1,000 predictions at 2.69 USD per GPU-hour, GPU only; bf16 checkpoint about 55 GB; API response times from different infrastructure, not a controlled speedup. (Sec. 6, Fig. 4)

## Calibration
Ten equal-width bins ECE, Brier, reliability diagram with Wilson intervals; temperature scaling fitted on validation sources (NLL). ECE 0.032 SO-101, 0.148 unseen domains, 0.027 community; Brier 0.033, 0.162, 0.052. (Sec. 4.3, 5.5, Fig. 5)

## Cascade or escalation
None.

## Robustness
Ten-frame vs four-frame vs final-frame only (final-frame AUROC 0.776 on unseen domains); anchored (0.890) vs unanchored (0.847) variant. Instruction-paraphrase sensitivity not checked. No option-name, cardinality or language tests (binary only). (Sec. 5.4, 7)

## Code and data
Weights Apache-2.0 on Hugging Face (josefchen/RoboJev-27B), 20,628 predictions in 29 model/protocol entries (josefchen/RoboJev-evals), inference and metric code; author reproduced all 118 table numbers from released predictions. Note App. A also says model weights and private training videos are not in the artifact bundle. (Abstract, Sec. 4.3, App. A, D)

## Authors' limitations (Sec. 7, App. D)
Observability limits; training labels model-generated with possibly correlated errors; single human annotator for community test labels; possible overlap with foundation-model pretraining; benchmarks examined in earlier exploratory runs; 8 test domains; calibration not guaranteed in new domains; paraphrase sensitivity untested; unresolved 28-record count discrepancy in community loader; training harvest not pinned to a repository revision.
