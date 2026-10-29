# azizi2026one — One Word Opens the Gate: The Option-Channel Attack on Typed Decision Models as Agent Guardrails

- arXiv: 2610.12292v1 [cs.AI], 8 Oct 2026, CC BY 4.0 (header). Full text: fulltext/2610.12292.html and .txt.
- Authors (header): Seyedarmin Azizi, Erfan Baghaei Potraghloo, Massoud Pedram, University of Southern California. Affiliation type: academic.
- Code: "Code is available at github.com/ArminAzizi98/option-channel-attack" (Abstract). code_available = yes. No data statement for GuardBench beyond that.
- Not a Jev paper. Jev is mentioned as the commercial model that introduced the interface; "We study open-weight models only and do not measure the commercial model" (Section 10). It still evaluates typed probabilistic decision models (open reimplementations) on allow/block decisions with a finite option space, so rows are coded.

## Task and data
Allow-or-block gating of agent tool calls and messages (Sections 1, 5).
- GuardBench (authors' synthetic suite): proposed tool calls generated from six attributes; six policies (exfil, secret, escape, exfil_secret, unauth_irrev, escape_or_exfil); ground truth computed from attributes, classes exactly balanced; each trace ends with an attacker-controlled tool-output span; "cannot overlap with any model's training data" (Section 5). Per-policy n not stated in the main text (for example 150 correctly blocked items for laya-td on unauth_irrev, Section 6.2).
- Three public screening sets, balanced to equal block and allow items: prompt injection (deepset/prompt-injections, n = 406), jailbreak (jackhhao/jailbreak-classification, n = 1,034), toxic content (n = 768, ref. Lin et al. 2023) (Table 2; references). Qwen readouts use 300 items per task (Table 2).

## Models, versions
Five typed decision models plus a Qwen baseline (Section 2): laya-td and laya-en (ModernBERT-large, 421M), laya-ml (multilingual, 322M), von (ModernBERT, 395M), rlcd (GLiClass, 151M, can return "insufficient evidence"); Qwen2.5-Instruct 1.5B and 7B scored by log-probability of the option name (a "readout"). No checkpoint revisions, hashes or run dates are given (searched: none). Hardware not stated.
Label visibility: laya-en, laya-ml, laya-td and Qwen place the option label in the model input; von and rlcd build the sequence from definitions only and are label-invariant (Section 6.3).

## Metrics
Fail-open (FO, prohibited action allowed) and fail-closed (FC) rates reported separately; attack success asr_open measured only on items the gate decided correctly before the attack; percentile bootstrap over items, 4,000 resamples, clean and attacked resampled together (Section 5). Most tables carry no intervals.

## Main results
- Clean public-screening accuracy 36.4 to 71.7 against chance 50 (Table 2). laya-td: injection 60.8 (FO 76.8, FC 1.5), jailbreak 68.0 (FO 60.7, FC 3.3), toxic 59.2 (FO 77.1, FC 4.4). laya-ml: 49.3, 36.4, 47.1; toxic FC 96.1. von 61.8, 58.8, 65.5. rlcd 71.7, 70.5, 63.4. Qwen2.5-1.5B 49.7, 39.3, 49.7 (FC 97.3 to 100); Qwen2.5-7B 59.7, 63.3, 67.3 (FO 63.3 to 80.7).
- Text attacks (Section 6.2, Table 3): six lines of server-log text raise laya-td fail-open on unauth_irrev from 0% to 63%; three unverified assertions raise it to 70%; a 17-word closing on toxic screening makes 88.6% [81.4, 94.8] of 88 correctly blocked messages pass.
- Option-channel attack (Section 6.3): renaming only the permissive option raises FO to 93 to 100% on the four label-visible models; Table 4 examples laya-td unauth_irrev 0.0 to 100.0 (label "escalate"), Qwen2.5-7B secret 0.0 to 100.0 (label "remediate"), laya-en escape 96.0 to 100.0; von and rlcd unchanged by construction. 198-label sweep, Table 5 (mean over six policies, honest / k=10 / best): laya-en 59.7/88.7/99.8, laya-ml 82.0/85.9/100.0, laya-td 60.0/89.5/98.2, Qwen2.5-7B 4.7/89.1/100.0, rlcd 10.0 flat, von 20.0 flat. Table 7 (public tasks): laya-td 72.4/86.9/97.1, laya-ml 55.1/62.5/85.1. Labels found on one model transfer partly (Table 6).
- Margins (Section 6.4): laya-td correct block decisions (n = 338) median P(block) 0.57, 97.0% below 0.70, maximum 0.82. Threshold change 0.50 to 0.40 raises clean FC from 26.0% to 70.7% on unauth_irrev.
- Escalation of low-margin cases (Section 6.5, Table 8): 1,410 reversed decisions have pooled margin 0.149 before and 0.151 after; at 10% review budget attacked FO falls only from 60.1% to 53.8%; at 46.4% review it is 25.3%, versus 0.0% for an oracle.
- Defenses (Section 7, Tables 9 to 13): over 72 cells, defenses win 45, tie 21, lose 6 against a matched fail-closed baseline; D5 (field-structured) wins 16, ties 2, but raises clean FC to 68.7% on unauth_irrev and is defeated by an adaptive attack (median adaptive FO 87.4 to 99.3% on three models, Table 12). D8 (instruction to ignore option names) leaves laya-td attacked FO at 99% vs 98% undefended. Parsed-value gate input removes field injection (53% to 0%) but a deterministic rule on the same values is 100% correct on all six policies.

## Comparators and tuning parity
Qwen2.5-1.5B and 7B log-probability readouts are the generative-family comparison; all models receive the same traces and policy text. No tuning of any model. Defenses are compared against the same model with a decision threshold biased toward blocking until clean FC matches (Section 7).

## Reference labels
GuardBench: synthetic, computed from generating attributes. Public sets: the dataset labels (not described in the paper); coded human_single.

## Test-set exposure
GuardBench new; public sets public before 2026 (deepset 2023, jackhhao 2023), no contamination check beyond the statement that models are small encoders.

## Cost, latency, calibration, cascade
No cost or latency. Calibration: the returned probability is shown to be unusable as a risk threshold (Section 6.4); no ECE or reliability analysis. Confidence-based escalation is tested directly (Section 6.5, Table 8) and found ineffective under attack.

## Paper's own limitations (Section 10)
GuardBench is synthetic and template-generated; only open-weight models, commercial model not measured (relies on Sun et al. 2026); attacks are cheap black-box attacks from fixed pools so rates are lower bounds. The authors also state that a deterministic rule solving GuardBench is a property of its construction (Section 7.1).
