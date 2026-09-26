# guo2026just — Just Ask Jev: Reinforcement Learning for Calibrated Decisions as a Zero-Shot Detector of AI Alignment Failures

arXiv:2609.29429v1 [cs.AI], submitted 24 Sep 2026. HTML retrieved from https://arxiv.org/html/2609.29429v1.

## Authors and affiliation

Ruoqi Guo (ruoqi.guo@griffithuni.edu.au) and Leo Yu Zhang (corresponding), Griffith University; Yi Liu, Griffith University; Gelei Deng, Nanyang Technological University; Yuekang Li, UNSW; Lida Zhao, Independent Researcher; Yutao Wu, Deakin University; Simin Chen, George Mason University; Ying Zhang, Wake Forest University (title-page affiliation block). Affiliation type: **academic** (seven of eight authors are university-affiliated; one, Lida Zhao, is listed as "Independent Researcher" with no institutional email, but the paper is otherwise a standard academic multi-university collaboration, so it is coded academic rather than mixed).

## Task and data

`RLCDAlignBench`, a benchmark that recasts existing AI-alignment-failure benchmarks as binary detection tasks for a decision model. "The result is ten failure types with 44 benchmarks and 7,193 detection instances (Table 1)" (§3.1): sycophancy, jailbreaks, deception, prompt injection, hallucination, privacy violation, social bias, reward hacking, concealing uncertainty, and power seeking. For each failure type the authors "run one open 2–7B target model and replay the reference scorer on its outputs" (§3.1). Items come from five target models: Qwen3.5-2B, Phi-4-mini, Gemma-2-2B, Llama-3.2-3B, and Olmo-3-7B (Table 1 caption). "The scorer is a rule for 20 benchmarks and an LLM judge for 24" (§3.1); some of the 24 are further split into "judge" and "multi-turn" scorer subtypes (§4.1). Eleven labels are validated (against gold or measured human agreement), 25 are unvalidated, and the authors' own audit changes eight; one defect benchmark (AbstentionBench) has too few negatives to score, "so seven of the eight enter the aggregates," leaving 38 "usable" benchmarks, of which 31 admit the generic question (§3.1, §3.4). Two benchmarks additionally carry human labels: the HarmBench validation set (three annotators, 578 items, Mazeika et al. 2024) and the StrongREJECT human set (1,360 of 1,361 responses from four generators — dolphin-mixtral, GPT-3.5, Llama-2-70B, GPT-4 — five annotators each, Souly et al. 2024), both "separate from the 100-item StrongREJECT benchmark on Phi-4-mini outputs" (§3.1).

## Decision models evaluated

**Jev** (TypeSafe), commercial, accessed through "TypeSafe's public API" (Ethics Statement). "All runs use `jev-1.13.0` (TypeSafe AI, 2026)" (§3.3). Reproducibility Statement: "All runs requested `jev-latest`, which resolved to `jev-1.13.0`. As of 2026-09-20, the API accepts this versioned ID even when the `jev-latest` alias moves to a newer release" — this is a documentation-access-style note, not a stated run/collection date for the study's own calls. No other decision model (Laya, Kev, etc.) is evaluated in this paper.

## Comparators

Three baselines "bound the task" (§3.4): all-positive (base-rate F1), response length (sign chosen by cross-validation), and an in-domain TF-IDF logistic regression on word/character n-grams, "trained by 5-fold cross-validation on in-domain labels" — i.e. the TF-IDF baseline sees labels Jev never sees, so the comparison favors it (comparator_tuning_budget = "tuned" for TF-IDF, "not applicable/no training" for length). On the two human-labelled sets, the comparator is each benchmark's own reference scorer (GPT-4o-mini rubric for StrongREJECT; a single human annotator / inter-annotator agreement for HarmBench validation). **Llama Guard is cited only in Related Work (§5, as background on classifier-style guard models) and is never run as an empirical comparator in this paper.**

## Reference labels

Per-benchmark "scorer labels" from each source benchmark's existing reference scorer (rule-based for 20, LLM judge for 24, further split into judge/multi-turn), classified `llm_teacher` for the modal aggregate rows in this ledger (most pooled headline rows mix rule- and judge-scored benchmarks; individual rows are coded to the more specific `human_adjudicated` where the comparison is directly against StrongREJECT/HarmBench human annotations).

## n, sampling design

7,193 detection instances across 44 benchmarks (Table 1). Six benchmarks have fewer than five minority-class items and are excluded from aggregates, leaving 38 "usable" benchmarks (31 admit the generic question). 95% CIs come from 1,000 bootstrap resamples of item groups (§3.4). HarmBench validation: 578 items. StrongREJECT human set: 1,360 of 1,361 responses.

## Test-set exposure

"`RLCDAlignBench` covers one RLCD model (`jev-1.13.0`), English benchmarks, 2–7B targets, and mostly scorer labels" (§6, Limitations). The underlying alignment benchmarks (StrongREJECT, HarmBench, etc.) are public and predate Jev's release, so classified `public-pre-2026`; no contamination check is reported for the target-model outputs specifically, since these are freshly generated by the 2–7B target models on public prompts.

## Cost and latency

Appendix H: "Over the study we made 23,411 calls (duplicates excluded) with 11.4 questions per call, a 0.12% error rate, a median of 2,095 input tokens, and a median client latency of 0.313 s (p90 0.55 s, p99 1.86 s)." Pricing: "USD 0.042 per million input tokens (output tokens are free) (TypeSafe AI, 2026). The whole study cost USD 2.27." On the 19 API-judge benchmarks, "at list prices the pooled ratio is 62.9× (USD 18.96 vs. 0.30)" — reported in the Abstract/§4.5 as "costs 63× less than LLM-judge scorers" and "one Jev pass at list prices costs $0.30 against $18.96 for the judges." A conservative repricing with every judge priced at GPT-4o-mini rates and Jev asked only the generic question gives "12× cheaper pooled, with a median of 3.3×" (§4.5). Hardware/provider: Jev via TypeSafe's cloud API; reference LLM judges via their respective API providers (token counts computed post hoc with `o200k_base` on recorded text, priced at list prices, Appendix H).

## Calibration analysis

Expected calibration error, equal-width binning (implied by "reliability curve," Figure 6, Appendix E; the paper does not name a specific bin count for the main ECE figures). "Pooled over benchmarks, the generic Noul's reliability curve is close to the diagonal (ECE 0.047). Its median per-benchmark ECE, however, is 0.168 against 0.074 under perfect calibration, and 24 of 31 benchmarks exceed the null's 95th percentile" (§4.4). No post-hoc recalibration is applied to headline numbers; label-free EM prior-shift correction (Saerens et al., 2002) is tested and found to lower F1 (0.571–0.690), i.e. it does not fix the mismatch (§4.4, `post_hoc_calibration = none` for headline rows). Threshold analysis: "The median F1-optimal threshold of 0.35" vs. default t=0.5; median F1 rises "from 0.706 at t=0.5 to 0.822 with a cross-validated threshold and to 0.793 with 10 labelled items" (§4.4). Confidence-based selective accuracy: "keeping the half of decisions with the largest |p−0.5| raises the median accuracy from 0.793 to 0.933" (§4.4, Figure 6(c)).

## Cascade / escalation results

No explicit cascade/escalation experiment routes Jev to a second model in this paper (unlike ibrahim2026evaluating). The nearest analogue is the confidence-based selective-detection result above (§4.4): "so a monitor can route Jev's least confident decisions to a judge or a human" — a proposed use, not a measured cascade with a partner system's post-cascade accuracy/cost.

## Option-name / robustness stress tests

§4.2 (Question Design): Argmax readouts "lose almost everywhere" versus soft probability readouts (Choice 2/0/28, Score 5/2/24 losses/ties/wins). Rubrics that threshold each Jev answer at 0.5 before combining lose to the best direct targeted question on 9 of 10 benchmarks (median −0.137). §4.3 (Context): a deployable reference absent from the state raises AUROC with a CI above zero on only 1 of 4 benchmarks (DeceptionBench, +0.050 [+0.029, +0.077]); label-key context (part of the label's own definition, not something a deployed monitor would hold) raises AUROC on 4 of 11 benchmarks (median +0.053), illustrating that "these gains measure the label's construct rather than the failure."

## Code and data availability

"Code and data: https://github.com/sumleo/RLCDAlignBench" (Abstract). Reproducibility Statement: cached Jev responses, detection-instance files and scripts released under CC BY 4.0 (data) / MIT (code); items carrying harmful content (StrongREJECT, HarmBench derivatives) are gated behind a research-only access request. `code_available = yes (https://github.com/sumleo/RLCDAlignBench)`.

## Paper's own stated limitations (§6, Conclusion)

"`RLCDAlignBench` covers one RLCD model (jev-1.13.0), English benchmarks, 2–7B targets, and mostly scorer labels. Extending it to other detectors, larger targets, and other languages is future work." Ethics Statement notes the benchmark is dual-use (a detector's blind spots could guide evasion) and that all human labels are pre-existing StrongREJECT/HarmBench annotations, not new human-subjects data.

## Notes on seed claims

No seed claims were pre-registered for this paper in the planning documents (it was added to the sweep late, per the task brief); this extraction is a first pass, not a seed-check.
