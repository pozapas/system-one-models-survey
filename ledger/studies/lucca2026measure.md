# lucca2026measure

arXiv 2610.32955v1 (cs.CL), preprint v1.1 dated 22 Oct 2026, arXiv listing 23 Oct 2026. "Measure Before You Train: Typed Decision Models vs. a Classical Baseline vs. a Generative LLM for Routing a Personal Multilingual Inbox." Single author Federico Lucca, independent researcher, Trento, Italy. Affiliation type: independent. (title block)

Note: the batch screening line says 739 emails; the paper reports a v2 corpus of 231 emails (system comparisons) and a v3 corpus of 722 emails (adversarial stress test, pre-registered hypotheses). (Sec. 5)

## Task and data
- A self-hosted personal inbox agent (Foyer) must decide message type (6 classes), urgency (3 levels), three booleans (needs-reply, action-within-48h, is-noise) and project (16 projects plus none). Emails are Italian and English from the owner's production database. (Sec. 3, 5)
- v2 corpus: 231 emails in 207 threads from rounds 1 and 2 (119 on 20 Oct 2026, 120 on 21 Oct, minus ignored rows), sampled stratified by the type predicted by the production rules; the rules' own accuracy is therefore not a production estimate. v3: 722 emails in 698 threads, round 3 (500 emails, 491 kept) sampled adversarially on emails where models saw offerta or spam, disagreed on action-48h, or random by baseline prediction; used for pre-registered hypotheses only. System comparisons are on v2. (Sec. 5, Table 1)
- Reference labels: a single human reviewer (the owner), who confirmed or corrected proposals made by two model annotators in round 1 (110 of 115 type and 104 of 115 urgency proposals survived) and labelled from a model proposal in round 2, after which the whole set was revised jointly with an assistant; no second annotator, so labels are anchored on model proposals (the authors name this anchoring). Production prediction hidden from the reviewer. (Sec. 5, 8, App. C)
- Data are private (emails not released), new for 2026; thread-grouped splits and secret redaction. Body truncated to 1,500 characters. (Sec. 4)

## Decision models
- Tev1 0.8B on CPU (i5-1245UE), Tev1 4B and Nimble 9B (Q8) on a Kaggle free T4, all via Ollama /v1/systemone (Ollama 0.40; tags tev1:0.8b, tev1, nimble); Bespoke Nimble v4-max through its API. No revision hashes; run dates only inferable (20 to 22 October 2026). Zero-shot, run once on all 231 rows. (Sec. 5, 9)
- Jev was not run "for lack of an API key". (Sec. 6)
- Request shape: one choice question per call with instructions and criteria (Italian question and one-line class definitions) against /v1/systemone. (App. B.3)

## Comparators and tuning parity
- Trained TF-IDF word and character n-grams plus logistic regression with balanced class weights, thread-grouped 5-fold CV on the 231 rows (about 185 training rows per fold); decision models and generative LLMs zero-shot. A few-shot run (three examples per class) for Qwen and Gemma 4 26B showed no gain. (Sec. 5, 6)
- Generative LLMs: Qwen2.5-7B-Instruct, Gemma 4 26B-A4B and 31B through OpenRouter, JSON mode, temperature 0; hosted Gemma 26B is not deterministic (0.774, 0.800, 0.791 on round 1 type), so hosted figures are single runs. Same Italian question and definitions for all systems. (Sec. 5, App. B.4)
- The trained baseline sees labels from the same inbox (a different information regime from zero-shot systems); the comparison is disclosed as such. Production rules are scored but not tuned.

## Results (v2, n=231)
Type accuracy: TF-IDF+LR 0.788 [.74-.84], Gemma 4 26B 0.740, Gemma 4 31B 0.732, Nimble v4-max 0.701 [.65-.76], Tev1 4B (T4) 0.688, Tev1 0.8B 0.623, Nimble 9B Q8 0.619, Qwen2.5-7B 0.571, production rules 0.277, majority 0.571. Urgency: TF-IDF+LR 0.736, Nimble v4-max 0.714 [.66-.78], Gemma 31B 0.645, Gemma 26B 0.628; local decision models 0.251 to 0.450, below the 0.697 majority. Switches: Nimble v4-max needs-reply 0.805, action-48h 0.805, is-noise 0.857; TF-IDF+LR 0.831, 0.931, 0.900. Project assignment (names only): Nimble v4-max 0.303, TF-IDF+LR 0.697. McNemar: LR beats Nimble on type (chi2=4.1, p<0.05) but not Gemma 4. Composed actions: false noise (reply or task needed but ignored, of 68) Nimble v4-max 8 (12%), TF-IDF+LR 12 (18%), Gemma 26B 3 (4%), Tev1 0.8B 25 (37%). v3: baseline lead over Nimble on every switch significant; Nimble type 0.56 below 0.58 majority. Seven of eleven pre-registered hypotheses confirmed, four refuted. (Tables 2, 3, 6, 7; Sec. 6)

## Cost and latency
Median latency per decision: Tev1 0.8B CPU 3.8 s; Tev1 4B T4 0.35 s; Nimble 9B Q8 T4 0.58 s; Nimble v4-max hosted 0.50 s; Gemma 26B 0.76 s; baseline under 1 ms. Cost per 1,000 emails from provider usage: Nimble v4-max about $0.02, Gemma 26B $0.03; few-shot prompting costs six to eight times more per email. Free Kaggle T4 for local GPU runs. (Table 2, Sec. 6)

## Calibration
Hosted Nimble v4-max best calibrated: ECE 0.04 to 0.11 on v2, 0.04 to 0.09 on v3 (binning not stated), deterministic (491/491 identical on a repeat). Trained baseline under-confident (type ECE 0.47); Platt or isotonic recalibration inside CV cuts ECE 4 to 17 times (type 0.47 to 0.11), at five accuracy points on type for 231 rows. Local decision models over-confident on errors (Tev1 4B 0.81 right vs 0.70 wrong). Cost-chosen threshold on the baseline's noise probability halves false noise. (Sec. 6)

## Cascade or escalation
None as a cascade; the paper explores cost-weighted thresholds and the composition of labels into actions only.

## Robustness
Question language (English instead of Italian): Tev1 4B 0.69 to 0.64, Nimble 9B 0.62 to 0.64. Question wording for urgency: rephrasing as an action lifts Tev1 4B from 0.45 to 0.56. Quantisation or serving stack: local Nimble 9B Q8 0.62 vs hosted v4-max 0.70 on type. No option-name or cardinality tests. Sender-removal ablation applies to the baseline only. (Sec. 6, Table 4)

## Code and data
Protocol, harness and pre-registration released; emails stay private; scripts named (dataset_email.py, bench_cv_pilota.py and others), README and result JSONs in docs/paper, but no repository URL in the text. (Abstract, Sec. 9)

## Authors' limitations (Sec. 8)
Single user, single inbox, two languages; owner reviewed model-proposed labels, no independent second annotator; 231 labels give intervals of about +/-6 points, so differences under eight points are not significant; stratified sample not a production estimate; round 3 sampled on LLM errors with the baseline proposal shown first; local runs on free Kaggle T4 with the Q8 build; hosted generative model not deterministic at temperature 0.
