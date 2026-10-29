# ha2026decision

arXiv 2610.31422v1 (cs.CL), 22 Oct 2026. "How Well Do Decision Models Transfer to Vietnamese? An Empirical Study of Text Classification." Authors Phat Huu Ha, Nguyen Xuan Phuc, Nong Nhut Quy, Trinh Tran Tran, Nguyen Minh Triet, Dang Van Thin, all University of Information Technology, Ho Chi Minh City, and Vietnam National University HCMC. Affiliation type: academic. (title block)

## Task and data
- Zero-shot text classification on 12 public Vietnamese datasets giving 13 settings across six task groups: topic (NEU-ESC, UIT-VSFC), emotion (UIT-VSMEC), hate speech (ViHSD, UIT-ViCTSD, UIT-ViOCD), sentiment (UIT-VSFC), intent (PhoATIS 28 labels, ViMQ), NLI (ViNLI, ViANLI, ViMedNLI, vnNLI). (Sec. 3.1)
- Test sizes (Table 9): NEU-ESC 6,613; UIT-VSFC 3,166; UIT-VSMEC 693; ViHSD 6,680; UIT-ViCTSD 1,000; UIT-ViOCD 549; PhoATIS 893; ViMQ 1,000; ViNLI 2,991; ViANLI 1,000; ViMedNLI 1,422; vnNLI 4,177; 33,350 setting-example pairs in total. (App. C.2, Table 9)
- Reference labels: the datasets' own gold labels (human annotated, single annotation per item in the original corpora; adjudication not described). Datasets are public and predate 2026 (citations 2018 to 2026); no contamination check. (Sec. 3.1)
- Primary metric macro-F1 over classes present in the gold test set, accuracy and weighted-F1 supplementary. No intervals, no significance tests, no seeds (decision models are run once). (Sec. 3.3)

## Decision models
- Jev, hosted API, "typesafe/jev-1.13 model version" (Sec. 3.2); no patch version, no run dates; TypeSafe docs accessed 2026-10-08 (reference list).
- Laya Multilingual 322M (convaiinnovations/laya-multilingual), GLiNER2.5-multi-Decide 287M (fastino), Quyet-1.0-Small 328M (chinhnc), open weights run locally. No revision hash; the reference entry for Laya carries the unresolved note "exact evaluation revision must be recorded". Hardware not stated. (Sec. 3.2, references)
- Quyet supports at most ten candidate labels and is excluded from PhoATIS (28 labels). Means cover the 12 settings shared by all four models. (Sec. 3.2, Table 1)
- Interface: Jev, Laya and Quyet receive typed-choice questions with instructions and criteria; GLiNER receives a classification schema with label descriptions. Label identities and order fixed across configurations. (App. B, Sec. 3.3)

## Comparators and tuning parity
- The four decision models are all frozen, zero-shot, same task text and label descriptions; no per-model prompt tuning described. (Sec. 3.3)
- LLM comparison (Gemma-3, Qwen3, Llama-3.3, GPT-4o, GPT-4.1) uses numbers from earlier work by Thin et al. (2024), on 11 overlapping settings, so prompts, label descriptions and run dates differ from the decision models' runs. GPT-4o and GPT-4.1 are missing for several datasets. (Sec. 4.2, Table 10)
- A supervised fine-tuned PhoBERT baseline is shown in Table 1 with dashes where unavailable; its source and training are not described in the text. (Table 1 caption)

## Results
Under English label descriptions Jev has mean macro-F1 69.22 over 12 shared settings versus Quyet 53.61, Laya 43.23, GLiNER 31.26; mean accuracy 76.37 versus 60.52, 50.99, 42.97. Jev is top in 11 of 13 settings (Quyet slightly higher on UIT-VSMEC and UIT-ViCTSD). Jev scores 79.26 on PhoATIS (28 labels) and 80.20 on ViMQ. Against published LLM scores Jev leads on five of 11 settings against the three open-weight LLMs, beats GPT-4.1 on UIT-VSFC sentiment (73.44 versus 73.14) and trails GPT-4.1 on UIT-VSMEC by 7.66, GPT-4o on ViMedNLI by 7.17, Llama-3.3-70B on ViMQ by 4.62. (Sec. 4.1, 4.2, Tables 1 and 10)

## Cost and latency
Not reported.

## Calibration
Not evaluated; no probabilities, ECE or Brier analysis. No post-hoc calibration.

## Cascade or escalation
None.

## Robustness
- Option-description language: English, Vietnamese, bilingual (Table 2). Jev mean macro-F1 changes -0.12 (VI) and +0.22 (EN+VI), varies by 0.35 points across configurations; Quyet +0.44 and -5.49; Laya +1.40 and -4.48; GLiNER -7.33 and -9.83. Task-dependent effects large for others (Quyet +21.06 on ViNLI, -14.23 on ViHSD). Option identities and order stay fixed; only descriptions change, so no option-name or cardinality test beyond PhoATIS. (Sec. 4.4, Table 2)
- Perturbations (teencode, typographical noise, diacritic removal) applied independently with original labels retained, generated with nom-vn v0.2.37 and pyvi v0.1.1, seed 42; labels not validated after perturbation. Mean macro-F1 change for Jev: no accents -9.51, teencode -1.10, typo -3.07; for the others no accents -13.77 (Laya), -14.75 (GLiNER), -15.47 (Quyet). Diacritic removal flips 19.57% of Jev decisions versus 40.60% (Quyet) and 54.29% (Laya). Each model's description language chosen as its best on the original data before perturbation (EN+VI for Jev), so the perturbation table uses a selected configuration. (Sec. 5.2, Tables 4 and 6, App. C)
- Error analysis: Jev PhoATIS 140 of 169 errors add an extra intent to the gold one; Jev misclassifies 80 of 132 UIT-VSMEC disgust items as anger; label concentration in GLiNER (692 of 693 UIT-VSMEC to other). (Sec. 4.3)

## Code and data
No code or output repository link found in the paper. Datasets are public. Model links given for the three open models.

## Authors' limitations
The conclusion states that results vary by task and configuration. No separate limitations section; no discussion of the missing intervals, single runs, or the cross-paper LLM comparison.
