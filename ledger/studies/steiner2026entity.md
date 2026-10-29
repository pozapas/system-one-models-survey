# steiner2026entity

arXiv 2610.34626v1 (cs.CL), 25 Oct 2026. "Entity Matching using Decision Models." Authors Aaron Steiner, Ralph Peeters, Christian Bizer, Data and Web Science Group, University of Mannheim. Affiliation type: academic. (title block)

## Task and data
- Entity matching as binary yes/no decision on a serialized record pair; match if p(yes) >= 0.5. Eight full benchmark test sets: Abt-Buy, Walmart-Amazon, WDC Products (80% corner cases, 100% unseen), DBLP-ACM, DBLP-Scholar, Dn7 Walmart-Amazon, billiger.de 100un (German), Semi-HETER; 3,073 positive and 27,152 negative test pairs (30,225 total). (Sec. 2.1, Table 1)
- Reference labels: benchmark gold match labels from the benchmark creators (no further description). (Sec. 2.1)
- Older benchmarks public for years, "models may have seen their test set labels"; billiger.de published September 2026, after the knowledge cutoff of all base models. (Sec. 2.1)

## Decision models
- Jev 1.13 (typesafe/jev-1.13-20260917), Cloudflare Clef (cloudflare/clef), Clef-flash, GPT-6 Luna Decisions API (openai/gpt-6-luna-decisions-20261006), Perplexity Decider v1.2 (perplexity/pplx-decider-v1.2-20261016), Kev-4B (jaredpalmer/kev-4b-20260924); all queried via OpenRouter with the identifiers in Table 2; no calendar run dates beyond identifier suffixes. Request: state = serialized pair, one yes/no question with option descriptions. (Sec. 2.2, Table 2)

## Comparators and tuning parity
- GPT-6 Luna generative (openai/gpt-6-luna-20260922, reasoning off, 64 tokens, JSON schema), Qwen3.8-27B generative (base of PPLX and Clef), Ditto (RoBERTa fine-tuned on full training sets, three seeds, values from the authors' earlier work). (Sec. 2.2, 3)
- Default prompt B0 for headline Table 4; three runs. Eleven other prompts, one run each; the "selected prompt" F0 is the per-model, per-benchmark prompt with the highest test-set F1, so F0 numbers are optimistically selected on test data (disclosed). One prompt (Astra rules) uses rules derived by GPT-6 Astra from 100 labelled development pairs per benchmark. Decision threshold and deferral threshold tuned on validation sets (69 validation pairs overlapping the rules sample removed). (Sec. 2, 4, 6.2)
- Published trained and zero-shot results in Table 12 are quoted from papers, not re-run. (Sec. 6.4)

## Results
Mean F1 with B0: PPLX v1.2 88.13, Luna Gen. 87.16, Jev 1.13 86.43, Clef 85.97, Luna Dec. 85.93, Kev 77.11, Clef-flash 72.72, Qwen3.8-27B 68.85, Ditto 80.62. Per-run SD at most 0.62 F1. PPLX exceeds Ditto on six of eight benchmarks; billiger.de F1 71.71 vs Luna Gen. 65.57. Selected-prompt F0 means: Jev 88.06, PPLX 89.13, Luna Gen. 88.92. (Table 4, Table 6) No intervals on headline means other than run SD; paired bootstrap (10,000 draws) for prompt, serialization and perturbation differences. (Sec. 2.4)

## Cost and latency
List-price cost per 1M pairs with selected prompts: PPLX 8.9 USD, Jev 31.9, Clef 126.5, Clef-flash 22.2, Luna Dec. 50.2, Kev 11.3, Luna Gen. 42.9, GPT-6.1 Sol 753 (B0), three-LLM ensemble 4,730. Throughput with 32 parallel API requests: Jev 26.9 pairs/s, Luna Gen. 15.0, Ditto 378.8 on one A40 GPU. API throughput and local GPU not directly comparable. (Table 13, 14)

## Calibration
Raw probabilities, selected prompt, 10 equal-width bins reliability diagrams over 30,225 pooled pairs, Brier decomposed into REL, RES; no recalibration. Brier x100: PPLX 1.68, Clef 1.88, Jev 1.94, Luna Dec. 2.12, Kev 3.68, Clef-flash 4.54; REL x100 0.10 to 0.22 for PPLX, Clef, Jev. Threshold tuning on validation gains nothing for Jev, Clef, PPLX; Clef-flash +4.46 F1. (Table 9, 10)

## Cascade or escalation
Chow-rule deferral: model keeps pair if min(p,1-p) <= t, t from validation at target selective risk 0.25/0.5/1%; deferred pairs go to majority of GPT-6.1 Sol, Claude Opus 5.5, Gemini 4 Argon (medium reasoning, no labels) or to Sol alone. At 0.5%: Jev 11.7% deferred, selective risk 0.28%, mean F1 88.06 to 91.01 (ensemble) and 90.70 (Sol); PPLX 10.3% deferred, 89.13 to 91.07 and 90.69; cascade costs 16 to 20% of the ensemble. With Luna Gen. as sole partner F1 falls below the decision model alone. (Sec. 6.3, Table 11, Table 13)

## Robustness
Prompt sensitivity (SD over 12 prompts 0.82 for Jev, 0.90 PPLX, 3.37 Clef-flash); four serializations (values only, JSON, attribute pairs, omit missing); five perturbations (entry swap, reversed attribute order, lowercase, attribute deletion, title typos) with flip rates. German-language benchmark billiger.de included (also aligned English translation exists but German variant used). No option-name or cardinality test (single binary question). (Sec. 4, 5, Tables 5-8)

## Code and data
Code, prompts and raw results: https://github.com/wbsg-uni-mannheim/decision-models-4-entity-matching. (Sec. 1)

## Authors' limitations
No dedicated limitations section. Stated caveats: bootstrap intervals hold decisions fixed and ignore run-to-run variation; older benchmarks may be in training data; Ditto numbers from earlier work; API and local throughput not comparable; selected prompts chosen on test data; calibration data of vendors undisclosed. (Sec. 2.4, 2.1, 7.2, 6.1)
