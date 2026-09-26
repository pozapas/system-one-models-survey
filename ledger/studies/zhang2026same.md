# Zhang et al. 2026 — Same Scores, Different Decisions: Evaluating JEV and Language Models for Legal Document Understanding

arXiv:2609.27678v1 [cs.CL], posted 23 Sep 2026. License CC BY 4.0. (fulltext.txt line 96; html line "arXiv:2609.27678v1 [cs.CL] 23 Sep 2026")

## Authors and affiliations

14 authors (fulltext.txt line 100):

1. Fan Zhang — affiliations 1,2 = The University of Tokyo; MBZUAI
2. Yankai Chen — 2,3 = MBZUAI; McGill University
3. Zhuohan Xie — 2 = MBZUAI
4. Yixi Zhou — 4 = Hong Kong Baptist University
5. Sijia Peng — 5 = Fudan University
6. Lei Fan — 6 = University of Illinois Urbana-Champaign
7. Xinhua Ji — 7 = UCloud (industry, cloud-computing provider)
8. Cunyuan Zheng — 8 = Columbia University
9. Huangyong Shan — 9,11 = The University of Hong Kong; Quantell Capital (industry, investment firm)
10. Philip S. Yu — 10 = University of Illinois Chicago
11. Xue Liu — 2,3 = MBZUAI; McGill University
12. Yu Chen — 1 = The University of Tokyo
13. Preslav Nakov — 2 = MBZUAI
14. Songwei He — 9,11 = The University of Hong Kong; Quantell Capital

Confirms both named authors: Philip S. Yu and Preslav Nakov are present, and the author count is exactly 14.

affiliation_type = **mixed**: the author list is dominated by academic institutions (University of Tokyo, MBZUAI, McGill, Hong Kong Baptist University, Fudan, UIUC, Columbia, University of Hong Kong, University of Illinois Chicago) but also includes two industry affiliations — UCloud (a commercial cloud-computing company, affiliation 7) and Quantell Capital (an investment firm, affiliation 11, shared by two authors) — so the list spans academic and industry, warranting "mixed" rather than a single dominant type.

Corresponding-author emails given for the MBZUAI cluster only: {fan.zhang, yankai.chen, zhuohan.xie, preslav.nakov}@mbzuai.ac.ae (fulltext.txt line 100).

## Task and data

Task: ContractNLI — document-level natural language inference over contracts (Koreeda and Manning, 2021), i.e. contract inference. For a contract *d*, a fixed hypothesis set H_d = {h1,...,h17} (17 original hypothesis types) with gold labels y ∈ {E(ntailment), C(ontradiction), N(ot mentioned)}. "Every prediction is scored against the existing annotations, without new human labeling or model-based judging." Evidence-span extraction is explicitly out of scope; only the classification component is evaluated (fulltext.txt lines 131, Section 2).

A **"judgment"** = one hypothesis-level label decision for one contract (one contract–hypothesis pair scored E/C/N or invalid).

**Controlled variables** (Section 2, "Controlled request conditions," lines 137–157): the stability study fixes one target "anchor" hypothesis per selected contract and varies:
- **A**: only the anchor is visible; only its label is requested.
- **B**: all 17 hypotheses visible; only the anchor label requested (varies *hypothesis visibility* vs A, output fixed).
- **C**: same catalog visible; all 17 labels requested, anchor first (varies *requested outputs*/output workload vs B).
- **D**: same catalog visible; all 17 labels requested, anchor last (varies *requested output order* vs C).
Each condition repeated three times. "A–B changes visible hypotheses at a fixed requested answer set; B–C changes output workload and structure at fixed visible content; C–D changes requested output order and structure."

**n**: Official test split = 123 contracts, 2,091 judgments (968 entailments, 220 contradictions, 903 not-mentioned; fulltext.txt line 179, Section 3.1). Stability panel = 30 test contracts (subset of the 123), one anchor per contract, 4 conditions × 3 repeats = 12 responses per anchor = 360 stability requests per model, 90 primary anchor judgments per condition (lines 179–181). Each model: 123 baseline requests + 360 stability requests.

## Decision model and comparators

Decision model: **Jev 1.13.0** (fulltext.txt line 187, "We compare Jev 1.13.0 with..."). Jev receives the contract as shared state and each requested hypothesis as a "native Choice question" (line 187).

Nine language-model comparators (all named/versioned in Section 3.2, line 187): Qwen3.5-4B, Qwen3.5-9B, Gemini 3.5 Flash-Lite, Gemini 3.1 Pro Preview, GPT-5.6 Luna, GPT-5.6 Terra, GPT-6 Astra, Claude Sonnet 5, Claude Haiku 4.5. This matches the abstract's "compare Jev with nine language models" (line 104) and the ten-model comparison total ("All ten models complete both evaluations," line 118).

Inference settings (line 189–191): Flash-Lite minimal thinking; Gemini Pro low thinking; Luna no reasoning; Astra high reasoning; Terra medium reasoning, 16,384-token allowance; Sonnet adaptive thinking medium effort, same allowance; Haiku disabled thinking, 8,192-token allowance. Terra/Sonnet/Haiku accessed via a "common third-party gateway" (named "Convert" in Appendix C, line 392); Luna and Astra via original OpenRouter route. Both Qwen models: BF16, thinking enabled, temperature 1, top-p 0.95, shared 32,768-token allowance for reasoning+answer, one GPU per model.

## Reference labels

reference_label_type = **human_adjudicated**. The paper scores every prediction "against the existing annotations" from ContractNLI (line 131), i.e. against ContractNLI's own original gold labels, which were produced by ContractNLI's human annotation/adjudication process (Koreeda and Manning, 2021) — this paper performs no new human labeling or model-based judging (line 131: "without new human labeling or model-based judging"). Justification for "human_adjudicated" rather than "human_crowd": ContractNLI is described in the Ethical Considerations section as data used "under its stated CC BY 4.0 license" with "existing data and annotations" (line 309), consistent with an expert/adjudicated legal-NLI labeling process rather than raw crowd labels; the paper itself treats these as ground truth ("gold labels").

## Sampling design and test_set_exposure

- Stability panel: 30 test contracts selected via seed 20260922, one anchor per contract chosen by document-specific anchor seeds, "independently of labels and model predictions" (line 179).
- Uncertainty: 5,000 whole-contract bootstrap resamples, seed 20260922, paired where applicable, "descriptive and unadjusted for multiple comparisons" (line 181).
- Model-selection timeline: Jev, both Qwen, both Gemini, Luna, Astra were fixed before test evaluation; Sonnet, Haiku, Terra were added after inspecting earlier results but "their configurations were fixed before collecting their test predictions" (line 183). The paper explicitly flags: "The ten-model comparison therefore does not constitute a wholly prospective model selection" (line 183).

test_set_exposure: ContractNLI was published in 2021 (Koreeda and Manning, 2021), predating this paper by five years, so it is **public-pre-2026** — the Limitations section explicitly notes this risk: "An official held-out split does not establish absence from model training data" (line 295).

## Cost, latency, hardware/provider

Table 1 (official-test baseline, 123 contracts, 2,091 judgments):
- **Jev 1.13.0: Accuracy 77.38%, cost $0.000228/contract, median response time 1.24 s** — lowest cost and lowest median time of all ten models (tables.txt Table 0).
- Next-lowest cost: GPT-5.6 Luna at $0.000931/contract (~4.1× Jev's cost); next-lowest latency: Gemini 3.5 Flash-Lite at 1.60 s.
- Text confirms: "Jev also has the lowest observed median baseline response time: 1.24 seconds, compared with 1.60 for Flash-Lite and 1.74 for Luna. Their P95 times are 1.59, 2.78, and 2.25 seconds, respectively." (line 229)
- Cost basis: for hosted models, provider-reported charges (Luna, Astra) or recorded token usage × public prices; for local models (Jev, Qwen), rental-equivalent GPU cost at **$2.00/GPU-hour**, one GPU per model (Eq. 1, line 199–205; Appendix C confirms $1.80–$2.09/hr range from Nebius/Verda/Runpod as of Sep 21 2026, line 416).
- Hardware: local models run on a "local Max-Q Workstation GPU" (line 416), one GPU per model; hosted models accessed via OpenRouter (Luna, Astra) or a third-party gateway called "Convert" (Terra, Sonnet, Haiku), or presumably native APIs for Gemini. All timing on "the same client machine, with one in-flight request per model and no retries" (line 207).
- At fixed 17-hypothesis visibility (B→C, requesting 17 labels instead of 1): Jev's median time changes 1.15→1.22 s (paired median increase +0.19 s, 95% CI [0.06, 0.24]); Flash-Lite 0.99→1.86 s (+0.49, [0.45,0.58]); Luna 1.10→1.78 s (+0.67, [0.59,0.71]) (line 233; Table 23/tables.txt Table 22).

## Baseline accuracy ranking (Jev vs hosted LLMs)

"Jev achieves 77.38% accuracy at $0.000228 per contract. All seven hosted language-model comparators have higher accuracy point estimates, ranging from 78.96% for Luna to 83.21% for Gemini Pro." (line 219) Gemini 3.1 Pro Preview has the highest baseline accuracy (83.21%). Qwen4B (74.22%) is the only comparator below Jev; Qwen9B (79.15%) is above Jev. Paired 95% intervals from Jev (Table 5) show Flash-Lite's +5.16-point gain has interval [+3.49, +6.98] (excludes zero — reliable), but Luna's +1.58-point gain has interval [-0.05, +3.11] (includes zero — not established).

## Accuracy-vs-correctness ranking divergence (RQ2/RQ3)

Headline framing (Abstract, line 104): "Rankings by baseline accuracy differ from rankings by correctness across every condition and repeat, although small differences in the latter do not establish a general stability advantage."

Specifics (Section 4.2, lines 235–247; Table 2):
- All-twelve-correct (persistent correctness across all 4 conditions × 3 repeats = 12 responses per anchor, out of 30 anchors): Sonnet 24/30 (highest), Jev 23/30 (second), Gemini Pro/Luna/Astra 22/30 each, Haiku 19/30, Terra 20/30, Qwen9B 18/30, Qwen4B 17/30, Flash-Lite 21/30.
- Sonnet−Jev difference = 1 target, paired 95% interval [−10.00, +16.67] points — "does not establish a general stability advantage."
- Jev exceeds Haiku, Qwen9B, Qwen4B by 4, 5, 6 targets respectively; intervals exclude zero for Haiku and Qwen4B, include zero for Qwen9B.
- On identical targets (360 anchor responses): Jev mean correctness 79.44% (286/360) vs Qwen9B 79.17% (285/360) — nearly identical means, but Jev has 23/30 persistently correct vs Qwen9B's 18/30. Paired mean difference (Qwen9B − Jev) = −0.28 points, 95% CI [−9.44, +10.00].
- Error distribution explains the divergence: Jev has 5 anchors stably wrong + 2 changing valid; Qwen9B has 2 stably wrong + 8 changing valid + 2 invalid (line 247).
- Agreement ≠ correctness: "Jev and Astra each repeat the same label on 28 of 30 targets, compared with Sonnet's 25. However, five of Jev's and six of Astra's consistent labels are wrong, compared with one for Sonnet." (line 247)
- RQ3 condition-level masking: "For Qwen4B, A and B have identical accuracy, yet nine of 90 paired responses change: four regressions, four corrections, and one switch between wrong labels." Terra: equal accuracy B vs C despite 7 changed responses (3 regressions, 3 corrections, 1 wrong-label switch) (line 253).
- Output-order sensitivity: "Haiku changes 14 of 90 paired responses from C to D, including twelve regressions and two corrections. Its accuracy falls by 11.11 percentage points (descriptive paired 95% interval: −23.33 to −1.11)." Jev shows **zero** C–D changes in this panel (line 255), though the paper cautions this doesn't establish invariance and Jev's question-key reordering differs from autoregressive output-position changes.

## Repeated-request stability analysis (compensating corrections/regressions, persistent errors)

Development diagnostics (Section 5 and Appendix B/D, lines 267–271, 364–374, 428–460):
- "Qwen4B changes 87 of 510 labels between joint and single-hypothesis requests, while its correct count changes by only four" (development, 30 contracts) — decomposed as 38 regressions, 34 corrections, 15 wrong-to-wrong switches (line 366, also Table 8 caption region).
- Disjoint development anchor panel: A and B have equal accuracy but 24/90 responses change (12 corrections, 12 regressions) (line 370, E.2).
- Reasoning-budget comparison (Appendix B "Additional computation and persistent correctness," line 374): moving Qwen from thinking-disabled/2,048-token to thinking-enabled/32,768-token raises mean anchor correctness (Qwen4B 76.67%→81.11%; Qwen9B 74.17%→82.50%) but all-twelve-correct counts barely move (17→17 for Qwen4B; 16→18 for Qwen9B) despite 68.30× and 63.51× more completion tokens; both paired intervals for the all-twelve change include zero.
- Test-panel unchanged-repetition reference (RQ3, "Variation without a changed condition," line 259): Qwen9B changes 15/90 valid pairs between A and B, alongside 12/90 repeat pairs within A and 6/90 within B; its C–D comparison changes 12/88 valid pairs while repeats within D change 11/86.
- Jev's own repeat variability (development, Appendix E.3, line 518): Jev's C–D condition difference is 4/90, "comparable to the observed repeat variability" of 4/90 within-arm disagreement in both C and D.

## Calibration analysis

Not present. The paper reports accuracy, Macro-F1, and validity/coverage, but no calibration metric (ECE, Brier score, reliability diagram) appears anywhere in the text or tables. No probability/confidence scores are elicited or scored — Jev returns typed Choice labels and the LLMs return JSON label maps, both treated as point predictions, not probabilistic outputs.

## Cascade / escalation result

Not present. There is no cascade, routing, or escalation experiment (no model calls another model, no confidence-gated fallback). The paper only cites cascade/routing literature (FrugalGPT, RouteLLM) as related work in Section 6 ("Joint quality and cost evaluation," line 285) but does not implement or evaluate a cascade itself.

## Option-name / robustness stress test

This paper's robustness manipulation is **not** an option-name-shuffle test (e.g., permuting multiple-choice option labels A/B/C/D); rather it controls three related but distinct request-design factors while holding the contract and target judgment fixed (Section 2 and Appendix E.1, lines 137–157, 468–496):
1. **Hypothesis visibility** (A vs B): whether only the anchor hypothesis or all 17 hypotheses are shown to the model.
2. **Requested outputs / output workload** (B vs C): whether only the anchor label or all 17 labels are requested, at fixed visible content.
3. **Requested output order** (C vs D): whether the anchor is requested first or last among the 17 labels, at fixed visible content and requested set.

A separate development-only condition varies **judgment-set size / batching** (K ∈ {1,4,8,17} hypotheses per request) and applies an explicit **hypothesis-order permutation** control (fixed random shuffle per document) plus an **unchanged-repeat** control, run on the same 30 development contracts (Appendix C.3, lines 394–401; Table 8/tables.txt Table 7). For Jev specifically: "Jev's C/D intervention changes question-key order; it is not equivalent to an autoregressive output-position intervention" (line 193), since Jev poses each hypothesis as a native Choice question against shared contract state rather than generating a single autoregressive sequence.

## Code / data availability

Code: **https://github.com/ZF-Utokyo/Jev-Benchmark** (abstract line 104, "Code: GitHub."; confirmed as the hyperlink target in the raw HTML, href="https://github.com/ZF-Utokyo/Jev-Benchmark"). Data: ContractNLI, used "under its stated CC BY 4.0 license" with attribution retained (Ethical Considerations, line 309); no new data collected.

## Paper's own stated limitations (verbatim summary, Section "Limitations," lines 293–305)

- Official test = 123 contracts, stability subset = 30 contract targets, all drawn from the same 17 hypothesis types; development analyses use 30 contracts (grouping) and 10 different contracts (anchor controls) — "these samples limit generalization to other legal questions and domains."
- Uses existing annotations "without a human performance comparison, new adjudication, or external-domain validation." "An official held-out split does not establish absence from model training data."
- Baseline accuracy and all-twelve correctness "use different target sets," so "ranking differences can therefore reflect both target composition and sensitivity to the tested conditions."
- "Three repeats provide limited information about possible responses, and bootstrap intervals may degenerate when no changes are observed. The small stability panel makes rankings sensitive to a few targets." Intervals are "descriptive and not corrected for multiple testing."
- "Inference settings, interfaces, instruction wording, hardware, providers, and collection times differ across models. Hosted models may change behind a fixed identifier." Jev's question-key ordering differs from autoregressive output ordering.
- The Qwen reasoning-configuration comparison "changes reasoning, temperature, and generation allowance together, so it cannot isolate the effect of reasoning alone." "Budget-exhausted answers are failures of the evaluated configuration, rather than evidence that a task is intrinsically beyond the model."
- Costs: "Local GPU costs use a declared rental equivalent" excluding "loading, idle allocation, and other non-inference expenditure," and "do not measure cloud throughput." "The frontier may change under other prices, serving methods, or reasoning budgets."
- Latency: "uses one client but different collection times, providers, routes, and inference settings, with uncontrolled provider caching." Cannot "isolate architecture-level efficiency, separate computation from network and queueing delays, or establish throughput under concurrent load."
- Model-selection staging: "Sonnet, Haiku, and Terra were added after earlier results were inspected... model selection itself is exploratory." Historical Astra development anchor coverage is incomplete.
- "Broader evidence would be required to assess suitability for legal practice or financial decision-making."

## Notable figure-only numbers not placed in ledger CSV (per constraints)

- Figure 1 panel 2/3 illustrative example (Qwen3.5-4B contract 595, hypothesis nda-2) — qualitative only, no numeric value extractable from unlabeled figure.
- Figure 2 (cost–accuracy frontier with bubble area = All-12-correct fraction) — bubble sizes are visual only; underlying numbers are already captured from Tables 1–2.
- Figure 3 (heatmap of label-change percentages) — cell percentages are visual/color-encoded in the figure; the same underlying counts appear in Table 6 (used in ledger instead).
- Figure 4 (development ten-model cost/accuracy/bubble plot) — green-region medians ($0.003767, 79.90%) are stated in the caption text and could be extracted, but the plot itself (bubble positions) is not numeric text.
- Figure 6 (bar/point plot of Table 23 data) — redundant with Table 23, already in ledger.
