# kourtis2026type — Type-Safe Decision Frameworks for Agentic 5G Control: A Theory-Driven Testbed Characterization of Where They Can Be Applied

arXiv:2609.33689v1 [cs.NI], 27 Sep 2026 (header). HTML retrieved 2026-10-28 from https://arxiv.org/html/2609.33689; saved as fulltext/2609.33689.html and .txt.

## Authors and affiliation

Michail-Alexandros Kourtis and George Xilouris, National Centre for Scientific Research "Demokritos" (NCSRD), Athens, Greece (title block footnote). Affiliation type: academic (public research centre). Funded by the SHARC and PQ-NEXT EU projects (Acknowledgment). Key `kourtis2026type` is free.

## Task and data

Characterising three type-safe decision frameworks for agentic 5G control on an Open5GS 2.8.0 / UERANSIM testbed with an NWDAF to PCF to SMF to UPF core-policy loop (§V-A). Frozen "v2" corpus of 3,645 test items over eight known decision classes: handover target selection with k in {4, 8, 16, 32, 64} neighbours, SLA breach (yes/no), urgency (score), anomaly severity (score); labels generated from simulator rules; per-class test sizes 540 (handover k=4, 8, urgency, anomaly), 135 (k=16, 32, 64), 1,080 (SLA) (§V-B). Derived corpora: eight runtime-declared question templates (2,400 test items) keeping the state and options of a v2 item but asking a different question, and four rewordings. Calibration and shift partitions have the same per-class sizes. All endpoints pre-registered, with non-inferiority margin 3 points and 10,000 paired bootstrap resamples over items, 5 seeds for trained arms (§V-B).

## Decision models evaluated

- Jev `jev-1.13.0` queried zero-shot over the Internet; "the evaluated version (jev-1.13.0) is fixed only by its identifier" (§II-A, §V-A). Run dates are not stated. Jev's latency includes the wide-area network from the platform's site (TCP connection alone 199 ms median).
- Laya (421M, ModernBERT-large backbone), version 0.3.5, zero-shot ("base") and after full fine-tuning on the v2 training split (5 seeds) ("FT") (§V-A).
- AnyJev (Nokia Applied Research, commit 3cd8c6f) reading Qwen3-8B bf16: L0 zero-label (cyclic-order marginalisation plus label-free prior), L2 closed-form head trained on the training split (an extension) (§II-A, §V-A).
- Plain encoder reference: ModernBERT-base with a linear head per fixed-cardinality class (5 seeds).
- System-2 escalation target: Qwen3-8B (bf16 and AWQ 4-bit) served by vLLM 0.30.0 on the same NVIDIA L4 edge GPU. PyTorch 2.6.0, CUDA 12.4.

## Comparators and tuning-budget parity

Byte-identical items reach every framework; each cell states its label use (§V-B). Parity is intentionally not matched: Laya FT and the encoder are trained on the full training split; Jev and AnyJev L0 are zero-shot; Jev and AnyJev gates use 2-fold cross-fitting on the test split because those frameworks have no calibration run, a logged pre-registration deviation; Laya's and the encoder's direct classes use the held-out calibration partition (§V-A). The authors flag that Laya (ModernBERT-large) and the encoder (ModernBERT-base) differ in backbone size, a confound (Table IV discussion, Limitations 11).

## Reference labels

Simulator-rule labels ("Labels come from simulator rules", §IX item 5). Reference type: synthetic.

## n, sampling, intervals

3,645 test items; per-class n as above; 5 seeds for trained arms sharing one calibration and test split; paired bootstrap 10,000 resamples for endpoints (§V-B). Most Table II to V cells are point estimates without intervals; Table VI gives one interval (+0.138 [+0.114, +0.163]).

## Test-set exposure

Synthetic simulator-generated items built for this study (frozen v2 corpus), so new. Whether the corpus is public is not stated.

## Cost and latency

Latency on NVIDIA L4 with SM clock locked at 1050 MHz, batch 1, p50 and p99 from raw per-call samples; energy per decision = mean power x mean latency from 20 Hz power samples (§V-A). Table II (k=4 decision): p99 25.8 ms for Laya (FT and base), 23.5 ms encoder, 283 ms AnyJev-8B L0, 94 ms AnyJev-8B L2, 596 ms Jev end to end warm; energy per decision 1.10 J Laya, 0.55 J encoder, 19.6 J AnyJev L0, 6.6 J AnyJev L2, not measurable for Jev. Jev warm p50 281 ms at k=4, cold 726 ms (§VII). The abstract's "11 to 29 times slower" for Jev is not tied to a single table cell in the text read. No dollar cost for Jev.

## Calibration

No ECE or Brier. The gate uses conformal risk control (CRC) on each framework's top-option probability max p (§V-A, Theorem 2); the trace-driven replay uses fine-tuned Laya with isotonic-calibrated confidence as System-1 (§V-A). Certified gate at alpha = 0.05 (Table III): the risk promise holds in distribution for every framework; what differs is the act rate.

## Cascade or escalation

Trace-driven replay with Laya FT (isotonic) as System-1 and Qwen3-8B as System-2: the Theorem 1 rule R1 changed nothing at up to 2x the class deadlines and at 60x reduced SLA violations from 0.068 to 0.044, escalating only SLA-breach items (14.2 per 3,645 decisions); the R1-optimal gate abstains more (coverage 0.629 vs 0.861) (§VI-D, Fig. 4). Free-text escalation to the 8B System-2 at or below 1 s is infeasible: decode 22.1 ms per token after a 94 ms first token leaves 41 tokens at 1 s versus a shortest answer of 47 tokens (§VI-D). Co-location breaks a 20 Hz batch-1 loop unless catch-up batching is used (Fig. 3).

## Option-name, cardinality, language and robustness tests

Cardinality k = 4 to 64; Laya's option budget truncates each option at k >= 16 so direct choice there is at chance, and the paper uses a group-and-final reduction (groups of 8) (§VI-E). Rewordings: fine-tuned Laya's accuracy moved by at most 0.4 points; the encoder fell from 0.948 to 0.263 when the rule was written into the question; Jev gained (anomaly 0.347 to 0.880) (§VI-F). Renamed option keys template included (Table V). English only.

## Code and data availability

No release of the paper's own code or corpus is stated in the text read (only third-party repositories, such as AnyJev commit 3cd8c6f, are cited). Recorded as no.

## Limitations stated by the authors

Twelve items in §IX: label-efficiency claim held in 2 of 4 families; Laya FT is question-blind; Plane A (E2/near-RT RIC) not closed; no real RAN; labels from simulator rules; one 8B LLM is both System-2 and accuracy ceiling; weak shift split; Jev hosted so behaviour may change; two analyses deferred to an extended version; no MPS or question-contrastive fine-tuning; backbone confound; certified-robustness radii bounded by n=100.
