# shi2026multi — Multi-Dimensional Comparative Scale Construction for Efficient Personalized Subjective Judgment in High-Traffic Applications

arXiv:2609.33282v1 [cs.AI], 27 Sep 2026 (header). HTML retrieved 2026-10-28 from https://arxiv.org/html/2609.33282; saved as fulltext/2609.33282.html and .txt. The text never mentions Jev; it calls its own SubJudge "a System One model" (Abstract, §4).

## Authors and affiliation

Xianglong Shi, Shifeng Liu, Sirui Zhao, Shengming Yuan, Enhong Chen (corresponding). University of Science and Technology of China; Shengming Yuan at University of Electronic Science and Technology of China (title block). Affiliation type: academic.

## Task and data

Personalized subjective scoring. Each input is a case plus a person profile; the model returns a continuous score. PluriHarms (Li et al., 2026, ICLR 2026): 150 harm prompts, 15,000 ratings from 100 annotators, 0 to 1 harm scale (§3). iNews (Hu & Collier, 2025, ACL): 2,899 multimodal Facebook news posts rated by 291 UK participants, Arousal, Dominance, Valence on a 1 to 7 scale; test split 579 records, personalization test 1,641 (Table 2, Table 5). A binary safety set of 2,994 items (586 positive, 2,408 negative, human-verified) is used for the Elo budget study (§3.2).

## Decision models evaluated

- SubJudge (own model): Qwen3.5-9B (backbone revision c202236235762e1c871ad0ccb60c8ee5ba337b9a, App. B.6) with LoRA, two-stage training (digit SFT then Batchwise Preference Optimization with Bradley-Terry comparisons). At inference it takes the logits of ASCII digits 0 to 9 at the first response position, normalises over those ten tokens and returns the probability-weighted expectation in [0, 9]; no text is sampled; one forward pass per dimension (App. B.5). Separate models per iNews dimension and input variant (T+P or I+P) (§3). Closed-set readout, so it qualifies as a typed score decision model although it is not a Jev-compatible API.
- Comparators: GPT-4o, GPT-5.4, GPT-5.6-sol, Gemini-2.5-Pro, Kimi-K3, DeepSeek-4.1-Flash, GLM-5.3, Qwen3.5-9B with thinking on and off; PluriHarms baselines (GPT 4.1, GPT 5, Claude models, Qwen3-14B/32B, WildGuard 7B, SafetyAnalyst 8B) copied from Li et al. (2026) Table 1 and marked as reproduced where an asterisk appears (Table 1 caption, Table 2 caption).

## Comparators and tuning-budget parity

Baselines are prompted (K-shot on PluriHarms; zero-shot-style API calls on iNews, "Section A baselines in Table 2 receive no calibration labels") while SubJudge is fine-tuned with teacher-panel supervision and has thresholds fitted on a 600-record calibration pool (App. B.5). A matched-calibration check (Table 14) refits both Qwen3.5-9B and SubJudge thresholds on the same records and SubJudge keeps the lowest MAE on all three dimensions. So the asymmetry is disclosed: tuned vs prompted baselines.

## Reference labels

Evaluation labels are individual human annotator ratings (PluriHarms; iNews). Training labels for the comparative scale are LLM-judge Elo scores from five-judge panels (GPT-5.6-sol, Gemini 2.5-Pro, GPT-5.5, GPT-5.4, Gemini 3.5-Flash, etc.; Table 3, Table 5); a GT-label arm trains directly on human ratings (Table 3). Reference type for evaluation: human_single (individual annotators), training teacher: llm_teacher.

## n, sampling, intervals

PluriHarms MAE with 95% intervals (Table 1: Individual 0.1659 ± 0.0078; Aggregated 0.2278 ± 0.0150). iNews MAE and accuracy without intervals (Table 2). Efficiency: 50 held-out questions on one H100 80GB, BF16 Transformers with SDPA (§3.3).

## Test-set exposure

PluriHarms was published at ICLR 2026 and iNews at ACL 2025 (§3); both public. No contamination check described for the API baselines.

## Cost and latency

Mean latency 0.503 s for SubJudge vs 0.649 s (Qwen3.5-9B thinking off), 8.809 s (256-token budget) and 131.173 s (4,096-token budget); 1 response token vs 4.98, 264.00, 4051.08; throughput at batch 64 4.095 req/s vs 3.878, 1.558, 0.119; peak memory 67.36 GiB vs 75.06, 75.04, 75.04 (Table 6, §3.3). Training: SFT 1.24 h and BPO 3.08 h for iNews Arousal on eight H100 GPUs (Table 15). Offline judge work: 1,160,045 pair judgments for iNews and 975,800 for PluriHarms (App. B.6); no dollar cost reported.

## Calibration

No ECE or Brier. Ordinal thresholds fitted on a 600-record calibration pool map the continuous score to seven levels (App. B.5); this is a post-hoc mapping, not probability calibration.

## Cascade or escalation

None.

## Option-name, cardinality, language and robustness tests

Judge-panel composition (Table 3, Table 5), Elo comparison budget (Fig. 3, optimum about 50 to 60 comparisons per item), input mode text versus screenshot (Table 2). No option-name or language tests.

## Code and data availability

Abstract says "The code is available at this url" without a recoverable URL in the text; Reproducibility Statement: "We will release our code and api datasets on pairwise comparison as well." Code: partial.

## Limitations stated by the authors

The paper has no separate limitations section; the AI Use Statement discloses generative AI use. Section 3.2 notes that the all-judge advantage over a single judge is small (0.86 and 1.46 points).
