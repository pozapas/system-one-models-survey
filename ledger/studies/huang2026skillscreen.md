# huang2026skillscreen: SkillScreen, High-Recall Screening of Malicious Agent Skills with Decision Models

arXiv:2610.17727. v1 on 2026-10-13 (screen list); the saved HTML is v2, 14 Oct 2026, CC BY 4.0. Full text: `fulltext/2610.17727.html` and `.txt`. Extractor batch V12. The study key `huang2026skillscreen` is distinct from the existing `huang2026can`.

## Authors and affiliations

Jerrold Huang, Junwei Quan, Saiyue Lyu (University of British Columbia), Zihan Guo (University of Toronto), Yingqiang Ge (Rutgers University); equal contribution footnote. Affiliation type: academic.

## Task and data

Screen malicious agent skills (SKILL.md) in a single forward pass. SkillScreen is OpenJev-2B (a Qwen3.5-2B NLI checkpoint) fine-tuned with rank-8 LoRA (alpha 16, 2.19M trainable parameters incl. head) for one epoch, premise = skill Markdown, fixed hypothesis "This AI agent skill is malicious", score = softmax entailment probability from three NLI logits (Sec. 3). Inputs capped at 8,192 tokens. Threshold for 99% recall chosen on validation after a positive-sigmoid calibration, frozen before test (Sec. 3.3).

Data: MaliciousSkillBench (Wang et al. 2026), 9,740 labelled skills from eleven sources, 4,575 structural families; five records with unavailable text excluded (Sec. 1, 2). Protocols: MSD (malicious-structural-disjoint; 6,814 train / 974 validation / 1,947 test, 1,500 malicious and 447 benign test skills), SD (source-disjoint; 7,510 / 833 / 1,384, 839 malicious and 545 benign), SBR (source-balanced random; 6,812 / 973 / 1,950) (Sec. 4).

## Decision models evaluated and versions

- SkillScreen (five seeds per split), from "a pinned OpenJev-2B checkpoint": Hugging Face AlexWortega/OpenJev qwen3.5-2b-nli-v5, revision a20448012c213128955ca0c693e7c943865cab77 (reference list). MIT licence.
- Untuned OpenJev-2B with the same hypothesis (zero-shot).
- TypeSafe Jev 1.13, "a commercial NLI API", queried with the same hypothesis and visible text prefix (Sec. 4 Baselines). Run dates not stated.
- Ablations: plain Qwen3.5-2B base, paraphrased/unrelated/empty hypotheses, OpenJev-0.8B (Table 2).

## Comparators and tuning-budget parity

ModernBERT-large (395.8M parameters, fully fine-tuned, one epoch, five seeds, six on SD; learning rate 2e-5) is the supervised encoder; Word-SVM (TF-IDF unigram and bigram, class-balanced linear SVM); SkillSpector 2.12.0 static scanner at risk threshold 50; four LLM judges (GPT-5.5, Grok 4.3 via a reseller, Claude Haiku 4.5, GPT-5.4 mini) with one shared prompt, one answer per record, malicious if reported probability at least 0.5, plus GPT-5.5 with eight labelled examples and with medium reasoning (Sec. 4). Judge prompts fixed before test requests. Judge coarse probabilities (13 to 60 distinct values) cap high-recall operation; no log-probabilities or repeated sampling (Limitations). Trained detectors receive training data, judges do not (except the 8-shot condition); the encoder results use the stronger of two five-seed sets on MSD, with two collapsed runs reported (Limitations, App. H). TypeSafe Jev 1.13 and untuned OpenJev are not fine-tuned.

## Reference labels

Official benchmark labels kept; authors note "some of which depend on package code or behaviour absent from SKILL.md" (Limitations). Coded administrative_field (benchmark-assigned labels, mix of marketplace collections and red-team sets).

## n, sampling, intervals

MSD test 1,947 skills; SD test 1,384. Means and SDs across seeds (Table 1). 95% paired bootstrap intervals from 2,000 stratified resamples of test records, recomputing the matched-recall threshold in every replicate (Sec. 4 Metrics, App. K). Example MSD FPR at 99% recall: SkillScreen 22.6 [13.5, 37.0], ModernBERT-large 30.4 [21.2, 51.4], Word-SVM 45.6 [30.0, 66.2], GPT-5.5 91.1 [88.4, 100.0] (Table 10). SD FPR at 99% recall: SkillScreen 50.5 [42.1, 59.9], ModernBERT 74.7 [69.8, 79.7] (Table 10 caption). Table 1 itself gives no per-cell intervals for the Jev row.

## Test-set exposure

Public benchmark released in 2026. Text of skills is public; authors note deployment estimates "depend on ... the model's pretraining overlap with public skills" (Limitations). No contamination check of Jev 1.13 or the LLM judges reported.

## Cost and latency

SkillScreen scores 1,000 skills in about 4.5 minutes on a single 10 GB MIG slice at no API cost; judges cost USD 4.3 to 8.8 per 1,000 skills for GPT-5.5 and Grok conditions and USD 0.8 to 1.2 for the smaller models (Sec. 5.2). OpenJev-0.8B runs only 10 to 20% faster than 2B (Sec. 5.4). Scanner context adds 817 s of runtime on the MSD test set (Sec. 5.4). No latency or cost figure for TypeSafe Jev 1.13 is reported.

## Calibration

SkillScreen: validation calibration (positive sigmoid on validation log-odds, i.e. Platt-style scaling) lowers 10-bin ECE on MSD from 0.029 to 0.037 to 0.009 to 0.022 across five seeds and NLL from 0.13 to 0.16 to 0.09 to 0.11; on SBR ECE 0.009 to 0.015 to 0.006 to 0.009; on SD ECE is 0.12 to 0.16 before and 0.14 to 0.16 after (App. E). No calibration reported for Jev 1.13.

## Cascade or escalation

Review routing: a score at or above the frozen threshold goes to human review (Sec. 3.3). At 99% recall (FPR about 21%) precision is 34% at 10% malicious prevalence and 4.5% at 1% (Limitations). Combination of SkillScreen with GPT-5.5 (a judge consulted only where it changes a decision) is analysed in App. K and listed as future work; its numbers were not extracted.

## Option-name, cardinality, robustness tests

Hypothesis ablations: empty hypothesis adds 22.1 FPR points at 99% recall (CI +2.0 to +40.4); paraphrase and plain base stay within noise (Table 2, Sec. 5.4). Paraphrasing 200 malicious test skills leaves recall essentially unchanged; moving commands into a referenced script and neutralising the prose lowers SkillScreen recall at the frozen gate from 99.8% to 87.0% and at 0.5 from 96.6% to 67.5% (Limitations, App. L; applied to SkillScreen only). Benign source shift: SD false positives concentrate in two unusual benign sources (Sec. 5.3).

## Code and data availability

Code, model and per-skill predictions on the project page https://jerroldh.github.io/SkillScreen-webpage/; release recomputes Table 1 offline from 66 prediction files (App. O). Skill texts not redistributed; scripts retrieve them from the pinned benchmark release (Ethics statement).

## Authors' stated limitations

Reads SKILL.md only (evidence in bundled code is invisible); fixed rewrites rather than an adaptive attack; official labels sometimes depend on code absent from SKILL.md; recall varies by source (macro-average 79% versus 95.6%); one prompt and one demonstration set for judges; one-epoch schedule varies update count with data size; several ablations use one seed; at 99% recall SkillScreen is a triage stage, not an alarm (Limitations).
