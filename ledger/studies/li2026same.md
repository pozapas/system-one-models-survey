# li2026same: Same Attack, Different Judge, A First Controlled Adversarial Comparison of Jev, LLM Judges, and Purpose-Built Safety Classifiers

arXiv:2610.17820v1 [cs.CR], 13 Oct 2026 (license: arXiv perpetual non-exclusive). Full text: `fulltext/2610.17820.html` and `.txt`. Extractor batch V12. The key `li2026same` is new (other Li 2026 keys in `studies/` are `li2026fast`, `li2026jevasajudge`, `li2026kite`, `li2026replacing`).

## Authors and affiliations

Xiang Li, Aichun Huang, Zheli Liu (Nankai University), Mingming Zhang (Zhongguancun Laboratory) (author block). Affiliation type: academic.

## Task and data

Independent evaluation of Jev as a safety judge under attack. Harness sends the same payload to every system under one routing policy (Sec. 4). Four tasks (Sec. 4.2): T1 input moderation using the cookbook INPUT_BATTERY (four yes/no Nouls for jailbreak, harmful request, medical advice, self-harm, plus a severity Score), 100 harmful JailbreakBench requests and 100 benign paired requests; T2 indirect-injection detection, 100 of the 510 direct-harm InjecAgent cases sampled with a fixed seed, each with a clean control; T3 two-option routing rebuilt from the same InjecAgent cases; T4 phishing detection (Choice phishing / legitimate) on 100 emails from a public corpus of 18,650 messages (7,328 phishing; zefang-liu/phishing-email-dataset). Attack matrix: 13 families, 50 variants (plus one probe), nine aimed at Jev's interface (Sec. 4.3). 64,478 judge calls in total (Sec. 5). Strict routing policy: block at hazard probability 0.70, review at 0.35, severity at least 2 upgrades review to block (Sec. 4.4).

## Decision models evaluated and versions

Jev "jev-1.13.0, the latest release at the time of our experiments"; "We pin every version" (Sec. 4.1). LLM judges via one commercial relay: GPT-6 Astra, GPT-5.6 Sol, GLM-5.3, GLM-5.2, GLM-5.1 (no logprobs, so each judge writes a probability in its answer). Local classifiers: Llama Guard 3 8B, Llama Prompt Guard 2 (86M and 22M). The vendor documentation was accessed 2026-10-12 (references 27 to 29). Experiment run dates are not stated; the bootstrap seed 20260927 is the only date-like token. Only Jev and the LLM judges are typed or probabilistic decision outputs; the two local classifiers emit a single label.

## Comparators and tuning-budget parity

Same payload, policy and 0.5 binarisation threshold for all systems, not tuned on the authors' data except Prompt Guard 2 (threshold adjusted, App. A). LLM judges self-report probability (weaker evidence of confidence than logprobs, Sec. 4.1, 9). The adaptive-search phrase pool comes mostly from attacks that already work on LLM judges, which the authors say favours Jev (Sec. 8.2, 9). No fine-tuning anywhere.

## Reference labels

T1: JailbreakBench harmful/benign labels; T2 and T3: InjecAgent construction (attacker instruction versus benign filler); T4: public corpus phishing/legitimate labels. All dataset labels, human-curated or constructed (not adjudicated within this study).

## n, sampling and intervals

n = 100 cases per condition for every task (same 100 cases to all eight systems), except the adaptive searches and the option-count probe (50 cases) (Sec. 4.5). Two-sided 95% percentile bootstrap, 10,000 resamples. ASR and gate-bypass rate are computed only over clean-flagged (or clean-correct) samples, e.g. 79 requests flagged by Jev on T1 and 62 phishing emails flagged on T4 (Sec. 4.5, 7.2). Repeat-query stability: 200 T1 and 200 T4 cases queried twice more (Sec. 5.2, Table 4).

## Test-set exposure

JailbreakBench (2024), InjecAgent (2024) and the public phishing corpus all predate 2026; no contamination check for any system (not discussed). Jev's cookbook example battery is used verbatim (Sec. 4.2).

## Cost and latency

Jev median latency 0.7 s versus 3.9 to 23.9 s for the LLM judges on T1 (Table 2); vendor-published price $0.042 per million input tokens, the cheapest (Sec. 5.1). Adaptive search against Jev took about 200 seconds and $0.05; the identical search against GPT-6 Astra about 1,600 seconds (Sec. 8.2, App. G). Local classifiers run on the authors' own hardware (not specified).

## Calibration

No calibration analysis (no ECE, Brier or reliability diagram). Confidence is used operationally: the gate-bypass rate counts attacks that lower the routed action while Jev's severity confidence stays at least 0.7 (Sec. 4.5, 8.1). Raw severity value changes on 75.0% [70.8, 79.2] of repeated queries while the routed action changes on 1.0% (App. B).

## Cascade or escalation

Confidence gate: any verdict below 0.7 confidence goes to human review (Sec. 3, 4.5). On A5a, 19 of 79 clean-flagged requests loosen; 12 move block to review and 7 reach pass; exactly one of the 19 keeps severity confidence at least 0.7, and that one is in the review group, so none of the 7 passes was a confident escape (Sec. 8.1).

## Option-name, cardinality, language, robustness

Option count: irrelevant options added to T3 for 8, 16 and 32 total options; Jev never picks the attacker's action at any size (Sec. 7.3, App. H). Language and encoding attacks (A7): Chinese translation ASR 0.08 to 0.14 for all six judges, homoglyph 0.00 for Jev (Sec. 6.3). Context dilution A4 inconclusive (App. F). Placement attack A11 in the instructions field: 0.00 on Jev (Sec. 7.3).

## Code and data availability

No release statement for code, payloads or results is found in the text (checked the whole file for "github", "released", "available"); datasets used are public. Code availability coded no.

## Authors' stated limitations

One Jev version; LLM judges reached through one relay without logprobs (may understate their robustness); ASR measures passing a message, not harm; the judgment-based conclusion rests on one task, one corpus, English only, single-turn; A4 inconclusive; phrase pool favours Jev; provider safety filters dropped inputs (three GLM calls refused; a first A7 run silently lost 43% of translations) (Sec. 9 Limitations).
