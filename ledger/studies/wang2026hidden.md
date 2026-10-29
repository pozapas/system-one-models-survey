# wang2026hidden — Hidden Risks of Jev: An Empirical Study of Security, Privacy, and Dual Use

arXiv:2610.04985v1 [cs.CR], 04 Oct 2026. HTML from https://arxiv.org/html/2610.04985 (fulltext/2610.04985.html and .txt).

## Authors and affiliation
Shang Wang, Tianqing Zhu, Huajie Chen, Jiayang Li, Meng Yang, Bo Liu. School of Computer Science, University of Technology Sydney (Wang, Li, Yang, Liu); Faculty of Data Science, City University of Macau (Zhu, Chen) (front matter). Affiliation type: academic.

## Task and data
Security, privacy and dual-use study of Jev as an application decision layer (§I). Three typed tasks: support routing (Choice), subscription cancellation (Noul), issue severity (Score) with GPT-4o-generated application states (200 per task for attacks; 1,000 clean training and 200 test samples for backdoor and membership tests, §III-A3, III-B3, IV-A3). Input manipulation: six attacks (context ignoring, fake completion, role spoofing, persuasive appeals, Jev-specific injection, universal adversarial suffix optimised on a Qwen1.5-7B-Chat surrogate with 500 Alpaca contexts) (§III-A). Backdoor: NanoJev poisoned at 5% and 10% with triggers "cf" and "james bond" (§III-B). Membership inference (600 members, 150 non-members; §IV-A3), internal knowledge inference (100 factual, 100 fabricated; §IV-A4), private attribute inference (§IV-B), defensive detection on eight public benchmarks (Tensor Trust, BIPIA, WildJailbreak, JailbreakBench, HarmBench, HC3, M4; balanced test sets 90 to 500 per class, Table VI), and misuse (jailbreak refinement of 100 queries; model extraction with 200 queries) (App. C).

## Decision models evaluated
"The official Jev API" (hosted) and NanoJev, "a separate local model" built on the public Eve-RLCD checkpoint (Qwen3-0.6B-Base, SFT then RLCD) whose training data and updates the authors control (Abstract, §II-C). No Jev version string, model ID, or query dates are given in the text read (only "as of September 2026" for a Hugging Face download count). Jev's output is read through its Choice, Noul and Score interfaces (decision rules in §III-A3: argmax; Noul at 0.5; Score bins).

## Comparators, tuning-budget parity
No comparator LLM for the attack measurements (Jev versus NanoJev only; the two differ in scale, training and data). NanoJev is fine-tuned on task data for backdoor and membership tests while the official Jev is used as-is, so the clean accuracies are not matched in budget (Jev 100.0 clean on all three tasks vs NanoJev 93.8, 94.0, 71.7; Table I). Detection uses a fixed Noul question per task; threshold calibration on small held-out calibration sets (10 to 50 per class) is reported separately from the default 0.5 threshold (§V-A, V-B).

## Reference labels
Attack tasks: ground-truth decisions of GPT-4o-generated application states (constructed so that truth differs from the attacker target; synthetic). Detection: benchmark labels of the eight public datasets (administrative/benchmark labels). Knowledge inference: GPT-4o-generated and checked statements. Model extraction uses Jev's own answers as reference labels (agreement, not accuracy).

## n, sampling, intervals
Each attack evaluation repeated three times and the mean reported (§III-A3, III-B3); no variance or confidence intervals shown in the tables. Tasks use 200 states per task. Several evaluation sets are small (membership: 150 non-members; calibration sets 10 to 50 per class). Figure 8 numbers (ROC-AUC, accuracy) appear in text only as ranges.

## Test-data exposure
Attack states are newly generated. Detection benchmarks are public, pre-2026 (Tensor Trust, BIPIA, WildJailbreak, JailbreakBench, HarmBench, HC3, M4); no contamination check; Jev's training data are undisclosed. Internal knowledge test finds Jev recognises 2024 news events but not selected 2025 and 2026 events (§IV-A4, Fig. 5).

## Cost, latency, hardware
Not reported.

## Calibration
No ECE or reliability analysis. Threshold calibration for binary detection (task-specific threshold on small held-out set) raises average accuracy on HC3 and M4 from 78% to 89% (§V-B). The paper treats the returned probabilities as attack signals (membership features: max probability and returned confidence) (§IV-A2).

## Cascade
None.

## Robustness / attack findings
Jev: context ignoring 96.5% ASR on support routing, role spoofing 0% ASR on cancellation but 93.5% on routing, Jev-specific injection 100.0, 100.0, 97.2% ASR; universal suffix 100.0, 100.0, 97.0% (Table I). NanoJev backdoor ASR 76.1% to 100% depending on poison rate and trigger (Table II). Membership inference ROC-AUC 55.3 to 74.6 (Table III). Jev internal knowledge accuracy 97.5, ROC-AUC 99.6 (Table IV). Private attributes recovered with 100% coverage and accuracy from Jev labels alone (Table V). Misuse: refinement raises harmfulness 2.3 to 4.5 (100% success); surrogate agrees with Jev on 92% after 200 queries (App. C).

## Code and data
https://github.com/shihe98/Security_Privacy_Jev (Abstract).

## Paper's own limitations
No limitations section. Statements: defence effectiveness "remain[s] to be evaluated for Jev" (§VI-A); results rest on three tasks and GPT-4o-generated states; accuracy/F1 of membership inference may overstate effectiveness given imbalance (§IV-A3).

## Notes for the grader
Adversarial robustness study, not an accuracy benchmark. Quantities entered in the ledger are attack success rates, clean accuracy, privacy-inference scores and detection quality. Jev version and query dates are unrecorded; Jev-vs-NanoJev comparisons are confounded by scale and training.
