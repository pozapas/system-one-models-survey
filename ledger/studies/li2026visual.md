# li2026visual — Visual Jev Rewards: Reference-Bound Verification for Multi-Subject Image Generation

arXiv:2610.09328v1 [cs.CV], 7 Oct 2026. HTML retrieved from https://arxiv.org/html/2610.09328 (fulltext/2610.09328.html and .txt). Screened as borderline: the model is the authors' own Qwen-based verifier that follows the Jev decision interface, not hosted Jev.

## Authors and affiliation

Baoteng Li, Wenzhuo Wu, Kongming Liang, Zhanyu Ma. School of Artificial Intelligence, Beijing University of Posts and Telecommunications; Beijing Key Laboratory of Multimodal Data Intelligent Perception and Governance (title block). Affiliation type academic.

## Task and data

Reward design for multi-subject image generation (reference images plus a prompt). A verifier answers fixed yes/no "atomic" questions per generated image; the mean of the Yes probabilities is a GRPO reward for Qwen-Image-Edit-2511 (Sec. 3, Eq. 5 and 7). Data: atomic verification set of 3,972 binary examples (2,477 train, 360 dev, 199 calibration, 936 test; Sec. 4.1); GRPO set of 200 MICo-150K training tasks, 549 reference images, 1,634 questions (Sec. 4.1); downstream evaluation on a manually screened 897-task subset of MICo-Bench (Sec. 4.3); offline human preference set of 21 valid tasks and 126 strict pairs (dev: 8 tasks, 48 pairs) (Sec. 4.3, Tables 3 and 4).

## Decision models evaluated

"Visual Jev" verifier = Qwen3.5-4B with LoRA trained with binary cross-entropy, Yes/No logits read from the LM head, temperature one, threshold 0.5 (Sec. 3.4, 4.2). The paper says it is "a local Qwen-based visual implementation inspired by Jev's decision interface" and uses BCE rather than TypeSafe's RLCD (Sec. 2.2, 3.4). No hosted Jev version is called; the version pin is the base model name plus checkpoint update (136 for rewards, selected on dev balanced accuracy; 544 for the fixed-budget table, Sec. 4.2). No run dates are given.

## Comparators and tuning parity

Untuned Qwen3.5-4B with the same binary readout; answer-token SFT; BCE plus Brier (Table 2). Direct Qwen3.5-4B and Qwen3.5-27B scoring as offline controls (Table 3). The GRPO control uses Qwen3.5-27B scoring instruction following and subject consistency 0 to 5 each, same training data and main hyperparameters (Sec. 4.2, 5.1). The Visual Jev verifier is task-trained (LoRA on 2,477 examples) while the direct scorers are zero-shot, so the comparison is between a tuned and an untuned scorer (the paper says it "does not separate the contributions of verifier fine-tuning, question decomposition, and aggregation", Sec. 5.1).

## Reference labels

Verifier labels: "A teacher model provides initial annotations, followed by consistency checks and human verification" (Sec. 3.4); GPT-5.4 annotation with human verification (Sec. 4.1). Coded llm_teacher in the ledger because the first-pass labels come from GPT-5.4 and the paper does not report agreement or adjudication. Human preference rankings are "blinded human rankings" (Sec. 4.3), number of annotators not stated, coded human_single. The downstream generation score is a GPT-5.4 composite, and GPT-5.4 also builds the questions and annotations, so "shared model preferences may influence the results" (Sec. 7).

## n, sampling design, intervals

See Task and data. Table 1 reports one run per method, no intervals. The only interval is a paired bootstrap over parent tasks for the agreement difference: [-8.33, 16.67] against 27B and [-2.38, 11.51] against 4B (Sec. 5.3). The 897-task subset is human-screened "higher-quality tasks" (Sec. 4.3).

## Test-set exposure

MICo-Bench and MICo-150K are 2025 public resources (ref. 12, arXiv 2512.07348); the verifier test split was built by the authors. The tasks are image tasks and the models are Qwen3.5 and Qwen-Image-Edit-2511, so exposure for the headline atomic test set is coded new.

## Cost and latency

Not reported. Hardware for verifier or GRPO is not stated in the text read.

## Calibration

Brier on the 936 test examples: 0.1332 untuned, 0.0356 BCE and SFT, 0.0391 BCE plus Brier (Table 2). The paper states "its normalization alone does not establish probability calibration" (Sec. 3.4) and "a lower value alone does not isolate improved calibration" (Sec. 5.2). No ECE or reliability diagram. A 199-example calibration split is listed (Sec. 4.1) but no use of it is described; temperature is fixed at one. Post-hoc calibration none.

## Cascade or escalation

None.

## Option-name, cardinality, language, robustness

None beyond reference-replacement examples in the verifier set (Sec. 4.1). No option-order or language tests.

## Code and data availability

No repository or data link found in the text; coded no.

## Paper's own limitations (Sec. 7)

One run per method and 30 updates; 21 valid human-validation tasks; preference intervals cross zero; severe identity risk not reduced; the comparison does not isolate verifier training, decomposition, identity labels and aggregation; arithmetic mean lets other conditions compensate; GPT-5.4 used for construction, annotation and evaluation; screened subset limits conclusions; composite is not the official MICo-Bench protocol.
