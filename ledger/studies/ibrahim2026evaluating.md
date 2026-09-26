# ibrahim2026evaluating — Evaluating Decision Models for Text Annotation in Computational Social Science

arXiv:2609.24574v1 [cs.CL], submitted 21 Sep 2026. HTML retrieved from https://arxiv.org/html/2609.24574v1.

## Authors and affiliation

Hazem Ibrahim (corresponding, hazem.ibrahim@nyu.edu) and Yasir Zaki. Affiliation: Computer Science, New York University Abu Dhabi, Abu Dhabi, UAE (title-page affiliation line). Affiliation type: **academic**.

## Task and data

Mirrors the evaluation suite of Ziems et al. (2024), *Can Large Language Models Transform Computational Social Science?* (Computational Linguistics 50(1)). 18 closed-choice CSS classification tasks, "the same released test splits (class-stratified samples of at most 500 instances per task; 7,977 items in total)" (§3.1). Ten utterance-level tasks, six conversation-level tasks, two document-level tasks. Three tasks (stance, implicit hate, discourse acts) are pilot tasks excluded from headline comparisons; 15 "evaluation tasks" carry the headline comparisons (§3.4). Gold labels are Ziems et al.'s released gold labels from the underlying source datasets (human-coded in the original studies) — coded here as `human_adjudicated`.

## Decision models evaluated

Three decision-class models are run on the full registered grid (§3.2):
- **Jev** (TypeSafe), commercial, "via the OpenRouter decisions endpoint." Resolved version per Table 5 (Appendix A.5): `jev-1.13-20260917`, access route "decisions API", provider column shows "–" (not disclosed/not applicable).
- **Qwen3-0.6B-RLCD**, "an open-weight 0.6B RLCD-trained decision model built on Qwen3-0.6B-Base (local inference on university HPC)." Resolved version (HF snapshot hash, Table 5): `b327ec5efb5fdbf8bfafa3b369720ac5f6434b05`. HF id (from page hyperlink): `huggingface.co/anthonym21/qwen3-0.6b-rlcd-decision`.
- **Qwen3-0.6B base**, "a no-training ablation that applies the identical letter-token constrained-decoding pattern to the same vanilla base model, isolating the effect of RLCD training." Resolved version: `Qwen3-0.6B-Base` (Qwen's own release).

Five further open-weight decision systems, "released in the week of Jev's launch," are run post-registration on a 17-task local grid under each system's own released inference code (Appendix B.14, "The open decision-model ecosystem"; the text calls this set "six open-weight counterparts" when it includes the RLCD-0.6B model alongside these five, and separately "five open-weight decision systems" for this appendix batch):
- **Laya** — "a 0.4B ModernBERT-large encoder answering in one forward pass" [ref 31, Nandha Kishor M.]. GitHub: `github.com/NandhaKishorM/laya`. No HF id found in the paper's hyperlinks.
- **decider-0.8b** and **decider-2b** — "decoders trained for typed decisions on Qwen3.5 bases" [ref 30, Mapika]. GitHub: `github.com/Mapika/decider` ("Trained decision models on Qwen3.5-0.8B/2B/35B bases" per the reference entry — only the 0.8B and 2B variants appear in Table 25; a 35B variant is mentioned in the citation but not run). No HF id found.
- **SemIf** — "a frozen Qwen3.5-4B with a logit readout over option letters and no training" [ref 28, Theo Lee]. GitHub: `github.com/TheoLeeCJ/SemIf`. No HF id found. SemIf's 16 answer slots exclude the 23-option dialect task (marked "–" in Table 25).
- **Bespoke-Nimble-9B** — "a LoRA adapter on Qwen3.5-9B trained on roughly 3,000 contrastive examples" [ref 29, Bespoke Labs]. HF: `huggingface.co/bespokelabs/Bespoke-Nimble-9B`.

**Seed-check note on names "Von", "Verdict", "OpenDecision":** none of these three strings appear anywhere in the paper's full text (checked via full-text grep of the HTML-derived text and the reference list). They are not decision models evaluated, mentioned, or cited in this paper.

**Count of open decision models:** the registered grid runs 2 open decision models (Qwen3-0.6B-RLCD and its Qwen3-0.6B-base no-training ablation); Appendix B.14 adds 5 more (Laya, decider-0.8b, decider-2b, SemIf, Bespoke-Nimble-9B) for a total of **7** open decision models evaluated on some part of the grid (or 6 if the untrained base ablation is not counted as a "counterpart," which is the paper's own Discussion phrasing: "one commercial decision model, six open-weight counterparts between 0.4B and 9B parameters," §5). This is well short of a claim of "13 open decision models."

## Comparators (LLM baselines)

19 LLM baselines via OpenRouter, "spanning the GPT-5.6, Claude, Gemini, Llama, Qwen, DeepSeek, Mistral, GLM, Kimi, and Gemma families" (§3.2), listed with resolved versions in Table 5 (Appendix A.5): claude-fable-5.1, claude-haiku-4.5, claude-opus-5, claude-sonnet-5, deepseek-v3.2, gemini-3.1-pro-preview, gemini-3.5-flash-lite, gemini-3.8-flash, gemma-4-31b-it, llama-4-maverick, llama-4-scout, mistral-medium-3-5, kimi-k2.6, gpt-5.6-luna, gpt-5.6-sol, gpt-5.6-terra, gpt-oss-120b, qwen3-235b-a22b-2507, glm-5.3. All LLM baselines run at temperature zero except OpenAI and Gemini baselines (reasoning effort "low") and Kimi K2.6 (reasoning disabled) and GLM 5.3 (reasoning effort "low"), the latter two adjusted after "widespread empty completions from reasoning-token exhaustion in a first pass" (§3.2). LLM baselines receive Ziems et al.'s released prompts verbatim plus one appended line eliciting verbalized confidence 0–100; decision models receive equivalent instructions restated as a typed decisions-API question. Tuning-budget parity: same zero-shot prompt for all systems (comparator_tuning_budget = "same prompt").

## Reference labels

Gold labels are Ziems et al.'s (2024) released gold labels for each task's source dataset (`human_adjudicated`, per the original studies' annotation procedures; the paper itself does not re-adjudicate). One grid task (politeness) has released per-annotator scores tested directly in Appendix B (Table 23, Spearman correlation between stated confidence and the standard deviation of five human annotator scores).

## n, sampling design

7,977 items total across 18 tasks; "class-stratified samples of at most 500 instances per task" (§3.1), reusing Ziems et al.'s released test splits.

## Test-set exposure

"All tasks are public benchmarks that predate the evaluated models, so training-data contamination cannot be excluded" (§5, Discussion) — classified `public-pre-2026`.

## Cost and latency

Table 3 (Appendix A, "Measured cost per 1,000 items and total cost for the full 18-task grid"): Jev $0.027/1,000 items, $0.21 total for the full 7,977-item × 18-task grid; local models (Qwen3-0.6B-RLCD, Qwen3-0.6B base) $0.000 metered ("local models run on university hardware and carry no metered cost; their prices are hosting-dependent rather than zero," caption); LLM baselines range $0.043 (OSS 120B) to $7.897 (Fable 5.1) per 1,000 items, i.e., $0.34–$62.99 total. Total inference spend for the full grid: $244.54 (§6, Ethics and Limitations). Provider/hardware per Table 5 (Appendix A.5): mix of first-party (Anthropic, Google, OpenAI/Azure) and aggregator routes (OpenRouter) for LLMs; local HPC for the two 0.6B decision models; Jev's provider column is undisclosed ("–").

## Calibration analysis

Expected calibration error (ECE) with 15 equal-width bins is the primary metric (§3.3, Table 2 caption); decision models are scored on their returned confidence, LLMs on elicited verbalized confidence (labeled as such). Sensitivity checks in Appendix B: Table 9 reports median evaluation-task ECE under alternative binning schemes; Table 10 reports post-hoc scalar temperature scaling fit on the three pilot tasks, with the Discussion noting "a scalar temperature fit on the three pilot tasks moves several inexpensive LLMs ahead of the decision model on evaluation-task calibration" (§5) — i.e., `post_hoc_calibration = temperature` was tested as a robustness/exploratory analysis, not applied to headline numbers. Table 12 checks Jev's scalar confidence field against the probability of its chosen option (Appendix B).

## Cascade / escalation results

§4.5 and Figure 3: Jev-confidence-based routing to three partner LLMs across six thresholds (0.5–0.95). At the 0.8 threshold, cascading to Gemini 3.8 Flash (best frontier LLM by median macro-F1, 0.669) reaches median task accuracy 0.674 against 0.678 for Gemini alone, at 56% of Gemini's cost. Cascading to Gemma 4 31B (best LLM under $0.50/1,000 items) at the 0.5 threshold reaches 0.638 against 0.626 for Gemma alone — the cascade **exceeds** the partner outright, "because the two systems err on different items." Cascading to Haiku 4.5 (best closed model under the same price cap) reaches 0.639 against 0.622 alone, at 27% of Haiku's cost. Table 18 (Appendix B) reports median cascade cost as a fraction of partner-alone cost under ±2× price-assumption sensitivity; Table 19 reports Jev-plus-human-review pricing.

## Option-name / robustness stress tests

Table 6 (robustness check, Appendix A): appending the verbalized-confidence elicitation line changes accuracy by a median of +0.2 points across the 48 pilot-task cells (median absolute change 1.7 points), ruling out the elicitation line as a driver of the accuracy comparison. Table 11: option-position bias (total variation distance between predicted and gold position distributions) on multi-choice tasks. Table 24 (Appendix B, "interface control"): Gemini 3.8 Flash under the registered free-text protocol vs. a JSON-schema-constrained rerun on identical items — structured output moved accuracy by less than a point and still let a handful of invalid answers through where the decisions endpoint allowed none (§5).

## Code and data availability

"the complete per-call records and analysis scripts are released for replication at https://github.com/hazemibrahim97/decision-models-css" (§6). `code_available = yes (https://github.com/hazemibrahim97/decision-models-css)`.

## Paper's own stated limitations (§5, Discussion, final paragraph)

"This study is a 2026 snapshot of one commercial decision model, six open-weight counterparts between 0.4B and 9B parameters, and 18 English-language classification tasks, and it does not establish that decision models are calibrated on social science text in general, that the empathy failure is specific to that construct, or that frontier verbalized confidence will remain well calibrated as vendors change post-training recipes." All tasks are public pre-existing benchmarks, so contamination cannot be excluded. The dialect-robustness result is a single task/single dialect and "does not certify fairness elsewhere" (§6). Post-hoc calibration of competitor LLMs was not systematically explored and "the class's native-calibration advantage may not survive even minimal tuning of its competitors" (§5). The open-ecosystem comparison (Appendix B) is unregistered, run once each system was released, and "enters no registered comparison" (Appendix B.14).

## Notes on seed claims (see also parts/seed_check_A.csv)

- 18 tasks, 7,977 items, 19 LLMs: **confirmed** (§3.1, §3.2, Abstract).
- "13 open decision models": **contradicted**. Only 7 open decision models are evaluated (2 registered + 5 in Appendix B.14); the paper's own Discussion phrase is "six open-weight counterparts."
- Jev trails per-task best LLM on 14/15 tasks, median −11.6 macro-F1: **confirmed** (§4.1, Abstract).
- 44× lower cost: **confirmed**, but precisely "the per-task best LLM costs a median 44 times more than Jev" (§4.5), i.e., a median ratio across per-task best comparators, not a blanket 44× versus every model.
- Better calibrated than 16 of 19 LLMs: **confirmed** (Abstract, §4.2/§5 — three Claude frontier models, Opus 5/Fable 5.1/Sonnet 5, beat Jev's ECE).
- ECE 0.157 against 0.066 for "the best frontier model": **imprecise**. 0.157 is Jev's median ECE (confirmed, Table 2); 0.066 belongs specifically to Opus 5, one of "three frontier models" (Claude family) with lower ECE than Jev — not a generic "best frontier model" label, since Opus 5 is not the single best model on macro-F1.
- Near chance at high confidence on empathy: **confirmed** — accuracy 0.383 in the ≥0.9-confidence subset (78% coverage) against a 0.371 base rate, ECE 0.538 (§4.4, §5).
- Routing low-confidence items to an LLM matches the LLM at 25–50% of its cost: **imprecise**. The paper reports cascade cost fractions of 56% (Gemini, 0.8 threshold), 27% (Haiku, price-capped), and the Gemma cascade *exceeds* rather than merely matches its partner at the 0.5 threshold; the Abstract's own phrasing is "at a quarter to half of its cost," which is closer to the seed but the specific reported fractions (56%, 27%) only partly fall in a strict 25–50% band.
