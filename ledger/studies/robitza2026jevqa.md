# robitza2026jevqa — JEVQA: Video Quality from Metadata, Bitstream, and Pixel Features with a General-Purpose Decision Model

arXiv:2609.24395v1 [eess.IV], submitted 21 Sep 2026. HTML retrieved from https://arxiv.org/html/2609.24395v1.

## Authors and affiliation

Werner Robitza (werner.robitza@aveq.info). "AVEQ GmbH, Vienna, Austria." Sole author; affiliation type: **industry**.

## Task and data

Zero-shot no-reference video-quality prediction using Jev as a general-purpose decision model, called **JEVQA** by the author to distinguish the application from the upstream Jev model (§I, §III-D). Jev is queried with the "score" question type (a position + probability distribution over an ordered answer scale); the prediction is the probability-weighted expected value over bin centers (Eq. 1). Two studies:
- **Study A** — 22 AOM Common Test Conditions class A2 source clips (1080p, 130 frames, mixed 8/10-bit), each encoded into an 88-encode CRF ladder across 4 resolutions × 4 encoders (x264, x265, libvpx-vp9, SVT-AV1), yielding 1,936 processed video sequences (PVS). Ground truth: VMAF v1.0.16 (per-sequence mean of per-frame scores), a full-reference *computed* metric, not a human/LLM/administrative label (§III-A; flagged below).
- **Study B** — AVT-VQDB-UHD-1 [Rao et al. 2019], a public 4K database, tests 1–3 (x264/x265/libvpx-vp9, two-pass ABR, 4:2:2, 360p–2160p, 60 fps), 562 PVS after excluding test 4 (frame-rate variation) and two processing-error encodes, rated by 24–29 participants per test on 65"/55" 4K screens — ground truth is MOS on a 1–5 scale (§III-B). AVT-VQDB-UHD-1 was also one of the databases used to train the ITU-T P.1204 series, so the standards-based comparator "may have had an advantage" there (§III-B, §V-C limitation).

## Decision model evaluated

**Jev** — accessed via "OpenRouter's Decisions API" at `https://openrouter.ai/typesafe/jev-1.13` (§III-D); not trained or fine-tuned by the author ("we only built the inputs for it"). Five iteratively improved input-state versions (S1–S5) are described (§III-D); headline results use S4 unless stated otherwise (S5's decomposed-question variant did not improve accuracy). Four information levels: Mode 0 (metadata only: codec/bitrate/width/height/fps), Pixel (decoded-frame no-reference measures only), Bitstream (adds `videoparser-ng` per-frame bitstream stats to metadata), Combined (bitstream + pixel).

## Comparators and baselines

- **ITU-T P.1204.1** (Mode 0) and **P.1204.3** (full-bitstream, H.264/HEVC only — VP9/AV1 unsupported by the reference implementation or excluded for reliability) — trained/fitted standardized models, run on the same inputs as JEVQA.
- **Trained regression baselines** fitted by the author on the *same* feature tables for comparison: Ridge (bitrate-only; normalized-QP + bits/pixel), ExtraTrees/RandomForest/HistGradientBoosting (full bitstream/pixel/combined tables), all with leave-one-source-out cross-validation (§III-E). These quantify how much signal the feature tables contain versus what the zero-shot Jev model extracts.
- **Göring et al. (2025)** [ref 7] — 17 prompted text-generating LLMs on metadata-only prompts, compared on AVT-VQDB-UHD-1 test-1's 180-PVS subset (§IV-D).

Tuning-budget parity: JEVQA is zero-shot throughout; P.1204.1/.3 and the trained Ridge/tree baselines are fitted/trained models — `comparator_tuning_budget = not applicable` for these rows (fundamentally different budget class, not a matched ablation).

## Reference labels

Study A: VMAF, a full-reference *computed* metric (libvmaf, VMAF v1.0.16 model), not a human, LLM, administrative, or task-outcome label in the schema's sense — the closest available `reference_label_type` value is **`none`**, and this mismatch is flagged explicitly per the extraction brief's instruction to note when no category fits cleanly. Study B: MOS from 24–29 human raters per test — coded `human_crowd`.

## n, sampling design

Study A: 1,936 PVS (22 sources × 88-encode ladder). Frame-level sub-study: every 8th frame of 352 PVS from 4 sources (5,792 requests). Pairwise sub-study: 288 adjacent-CRF pairs from 64 ladders (Study A), 371 adjacent-bitrate pairs from 174 ladders (Study B). Study B: 562 PVS (190 H.264, 216 HEVC, 156 VP9); P.1204.3-supported subset 406 H.264/HEVC PVS; Göring-comparable subset 180 PVS (test 1 only).

## Test-set exposure

AOM CTC class A2 source clips are a public pre-existing test-condition set; AVT-VQDB-UHD-1 is a public database released in 2019 (Rao et al.) — both coded `public-pre-2026`. Jev itself (released August 2026, per the paper's own citation of Almeida et al.) postdates AVT-VQDB-UHD-1's 2019 publication, so the *database* cannot be Jev-specific training contamination in the usual direction, but the paper notes P.1204 itself was partly trained on this same database (a different contamination concern, affecting the P.1204 comparator rather than JEVQA).

## Cost and latency

Provider: OpenRouter (`typesafe/jev-1.13`). Headline: "All Jev requests of both studies together, including every state version, frame-level, and pairwise run, cost about $4; the Mode 0 run over all 1,936 PVS of Study A completed in 39 s" (Conclusion). No per-request latency breakdown beyond this aggregate.

## Calibration analysis

Not framed as calibration in the ECE/Brier sense; instead the paper reports **correlation-based accuracy** (PLCC, SROCC, RMSE raw and linearly rescaled per ITU-T P.1401) and a **pairwise Brier score** for the adjacent-encode ranking test (mean squared error of the returned probability against the correct pairwise answer; Table IV) — e.g., Study A bitstream pairwise Brier 0.0001 (near-certain, correct), Study A pixel pairwise Brier 0.582 (near-total miscalibration, actively wrong direction). No post-hoc recalibration (temperature/Platt/isotonic) applied anywhere.

## Cascade / escalation results

None — no routing or confidence-threshold escalation design.

## Option-name / robustness stress tests

Extensive input-state robustness testing (§IV-A, "state versions had a larger effect than the information level"): raw per-codec quantizer values (S2) let the model read a VP9 quantizer index of 150 as if on the H.264 0–51 scale, collapsing accuracy to PLCC 0.30 (AV1) / 0.19 (VP9) while H.264/HEVC stayed at 0.82; mapping all quantizers to one normalized 0–51 scale (S4) recovered AV1 to 0.69 and VP9 to 0.83 without touching H.264/HEVC. The pixel-only state is not merely uninformative but **actively inverted**: it "picks the lower-quality encode in 78% of pairs" (§IV-C), attributed to the model reading rising high-frequency energy/noise/spatial-temporal-information at higher resolutions as a quality signal rather than a compression-removal artifact (§V-B). Frame-level tracking fails even where sequence-level pooling succeeds: pooled frame-level PLCC 0.800 but median within-PVS PLCC only 0.32 (§IV-C) — the model separates clips but does not track quality within a clip. Bitstream-level input helps in Study A (CRF-controlled) but *degrades* accuracy in Study B (bitrate-controlled): the author attributes this to the model conflating low QP with high quality regardless of resolution, a confound that trained models "would typically learn" but a zero-shot model cannot infer from feature names alone (§V-A).

## Code and data availability

Study A encoding scripts and scores: https://github.com/slhck/vmaf-v1-vs-v0. Bitstream analyzer (third-party tool used, not released by this paper): https://github.com/aveq-research/videoparser-ng. The proprietary pixel-feature tool `video-analyzer` is explicitly **not** released ("Our proprietary tool," §III-C). No JEVQA-specific code/prompt repository is given. `code_available = partial` in the ledger.

## Paper's own stated limitations (§V-C, six numbered points)

(1) Study A used VMAF, not MOS, as ground truth, and "we know VMAF does not perfectly replace MOS." (2) P.1204 models were partly trained on AVT-VQDB-UHD-1, so Study B compares zero-shot predictions against in-sample references — "a fair comparison would need a database unseen by either side." (3) Neither dataset covers adaptive-streaming artifacts (loading delay, stalling, quality variation). (4) No user-generated content tested for pixel-based features. (5) "Jev is a commercial service with closed weights; later releases may behave differently from the version we recorded, and alternatives are likely to be released soon." (6) The P.1204.3 comparison covers only H.264/HEVC, a reference-implementation limit the author "plans to address."

## Notes on seed claims (see also parts/seed_check_B.csv)

- Zero-shot video quality evaluated on 1,936 encodes: **confirmed** (§III-A, "1,936 processed video sequences (PVS)").
- Pearson r = 0.737 (JEVQA) vs 0.733 (ITU-T P.1204.1): **confirmed** exactly (§IV-B, Table II: "JEVQA is slightly ahead on all three metrics, but the difference is small (PLCC 0.737 vs. 0.733)").
- Trained models stay ahead: **confirmed** — explicit in the Abstract ("trained models on the same features remain clearly ahead in both studies") and substantiated by ExtraTrees (PLCC 0.957, Study A; 0.951, Study B) versus JEVQA's best zero-shot correlations (0.824 combined, Study A; 0.879 Mode 0, Study B).
