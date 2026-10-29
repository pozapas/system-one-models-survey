# wang2026unijev — UniJev: Separating Accuracy from Calibration in Trimodal System One Decision Models

arXiv:2610.25784v1 [cs.CV], 19 Oct 2026. Full text: fulltext/2610.25784.html and .txt (arXiv HTML). Key uses first author Jianing Wang (a second Wang paper in this batch is wang2026truncated).

## Authors and affiliation
Jianing Wang, Youwen Jian, Derong Wang, Jinyang Yu and others (Fudan University); Qingyi Si, Chuanyu Qin, Yanghua Xiao, Hongcheng Guo (corresponding authors; JD.com and Institute of Information Engineering, Chinese Academy of Sciences listed) (title block). The extracted author block does not reliably map each name to an affiliation. Affiliation type: mixed. Code https://github.com/wjnwjnwj/UniJev (abstract).

## Task and data
Own model plus method. UniJev scores candidate answers with a shared head over a Qwen3.5 multimodal backbone for text, image and video decisions, trained first with supervised candidate selection (SFT, optional label smoothing rho=0.9) then CORA (Confidence-Outcome Reliability Alignment), which sets each confidence bin's empirical accuracy as the target for its members' confidence (Sec 3). Training mixture: Kev decision-v7 text, Valen-Training-General-100k images, JeV video multiple-choice; 157,656 records after source-group splitting (Sec 4.1). Test suite 3,124 questions: text 764 (Kev transfer-v4 split: 444 Choice, 280 Noul, 40 Score), image 1,858, video 502; train and test disjoint by source group (Sec 4.1, App. B).

## Decision models evaluated
Own: SFT (2B, 9B, hard and soft label), CORA (2B, 9B), five local RLCD adaptations at 2B (Shaped RLCD, GRPO, CtR/OpenJev-RLCD, RLCD-lite, Rewarding Doubt) from one shared soft-label SFT checkpoint, 500 steps, one seed (Sec 4, App. A). Released models run with native weights and preprocessing: TypeSafe Jev (text only, version not reported), Laya, Laya Vision, Von, Verdict, NIRNAY, Dohnuts, OneJev, OmniJev, Open-Jev, RLCR-hotpot, OpenJev, Astro-RLCD, Kev, decider, decider-vision, NanoJev, Valen (Table 2); selected source revisions for Kev, Decider, Decider-Vision, NanoJev and Valen are recorded in a registry, not in the text (App. A). Jev probability-mass errors up to 0.02 are renormalized, larger rejected (App. A). General-purpose multimodal models (Qwen3.5-2B/9B, Qwen3.8-27B, InternVL3.5-8B, Gemma4-26B-A4B) with a shared prompt (App. D).

## Comparators and tuning parity
Local RLCD arms share initialization and budget; released models are not retrained and include differences in preprocessing and pretraining (App. A). The hosted Jev was probed on text only. No tuning of released models.

## Reference labels
Source-dataset labels from the training mixtures' pools; text questions come from Kev's transfer-v4 split; image and video test questions randomly selected from their source pools (App. B). Label provenance beyond that is not described, coded administrative_field.

## n and intervals
764/1,858/502 test questions; no confidence intervals; one seed per local recipe (Limitations).

## Test-data exposure
"Released-model pretraining and source overlap are uncontrolled" (Limitations). Source pools are 2026 releases for several sets.

## Cost and latency
No monetary cost or latency; training on four or eight GPUs (App. B).

## Calibration
Accuracy, mean max probability, 15-bin equal-width ECE, NLL and multiclass Brier, reliability diagrams in App. F (Sec 4.1). CORA is a training-time calibration (10 bins, group of 256 questions, minimum support 20, 100 updates); inference uses the model's probabilities directly, no post-hoc map (Sec 3.3, App. B). CORA 2B image ECE 0.060 to 0.030, video 0.077 to 0.052; 9B image 0.061 to 0.031, video 0.077 to 0.063; CtR image 0.025 (Sec 4.2, 4.3). Valen (released) reaches image ECE 0.007 at 93.7% accuracy (Table 2).

## Cascade or escalation
None.

## Option-name, cardinality, robustness tests
Candidate order reshuffled across epochs in training; CORA ablations over bins, group size, support and scope (Table 3). No option-name, language or cardinality test.

## Code and data availability
Code released; training and test sources are public datasets; baseline registry records checkpoint identifiers (abstract, App. A).

## Authors' limitations
CORA evidence limited to image and video on this suite and two scales; group-accuracy targets include each question's own outcome; calibration updates can change answers; local RLCD comparisons use a 2B backbone and one seed; reinforcement-plus-supervision recipes do not isolate reinforcement; overlap uncontrolled; single-step labeled decisions only (Limitations).
