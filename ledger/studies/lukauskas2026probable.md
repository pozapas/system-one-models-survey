# lukauskas2026probable

arXiv 2610.14912v1 (cs.AI), 10 Oct 2026. "Probable but Not Valid: A Psychometric Audit of Decision Models as Synthetic Survey Respondents."
Authors: Mantas Lukauskas (Hostinger; Kaunas University of Technology; AI Insight Lab), Viktorija Sarkauskaite (AI Insight Lab; independent researcher). Affiliation type: mixed (industry plus academic plus independent). (title block)

## Task and data
- Synthetic survey respondents. Human reference is an open sample of n=263 Lithuanian employees, 68 items in 4 instruments (IWPQ 18, Dunham 18, change engagement 15, UWES-17), 13 reverse-keyed items. Data public since 2020. (Sec. 3, Sec. 7 Memorisation)
- Headline sample: 100 respondents stratified by gender and position, fixed seed, the 100 IDs of the original audit's gpt-5.4-mini C3 cell. Model sees 11 profile fields (condition C3). (Sec. 3)
- Metric: Psychometric Similarity Score (PSS) = 0.25 D + 0.25 C + 0.20 R + 0.20 M + 0.10 G (distribution, correlation, reliability, mediation, demographic contrasts), scored against all 263 humans. (Eq. 1)
- Reference labels: real survey answers of human respondents (human crowd, self-report, non-probability online sample). (Sec. 3, Sec. 6)

## Decision models (all via OpenRouter decisions endpoint, listed 7 and 10 Oct 2026; Table 13 resolved versions)
Jev 1.13 (typesafe/jev-1.13-20260917), Decider v1 27B (pplx-decider-v1-27b-20261001), Decider v1.1 27B (20261006), Liquid d1 (20260930), Kev 4B (20260924), Tev1 4B (20260923), Mercury Decide (20260930), Solar Decide Flash (20261008), Clef and Clef Flash (cloudflare/clef, cloudflare/clef-flash, no date suffix), Clef Omni (20261009), GPT-6 Luna Decisions (20261006), Microsoft-Decision-1 (20261009), Drex v1.5 (20261009). Solar Decide excluded (46 of 100 complete). jev-latest excluded as alias for Jev 1.13. Span-01 excluded (chat-message state only). (Sec. 4, Table 13)
- One request carries all 68 score questions (Clef models and Drex v1.5 split 64+4). English JSON profile, Lithuanian items. Endpoint exposes no temperature or seed. (Sec. 4 Requests)
- Readouts: R rounded expected score (default), A most probable category, S sampled (mean of 5 draws). (Sec. 4 Readouts)

## Comparators and tuning parity
- 47 generative LLMs: 36 cells from the original audit (single call, minimal reasoning) plus 11 new releases run with the original generator and prompt, temperature 0.7 requested where accepted, minimal reasoning. Same 100 respondents and scoring. Generative prompt fully Lithuanian, decision request English JSON state; different routes; authors state the design cannot separate these factors. No tuning of either class; no few-shot. (Sec. 4 Generative models, What differs)
- Statistical baselines: Gaussian copula in-sample (0.927) and out-of-sample fit on 163 other people (0.824), oracle (same 100 humans, 0.886), held-out human split (0.825), independent marginals (0.430), profile regression. (Table 1)

## Headline results (PSS, rounded readout)
Best generative MiniMax M3 0.813; Jev 1.13 0.681 (best decision model, SE 0.036), 13 of 14 decision models below gpt-5.4-mini (0.743). Jev with A readout 0.786, mostly via the noisy mediation component. Correlation component: decision models at most 0.667 under deterministic readouts, 33 of 47 generative cells above. (Tables 1-3, Sec. 5.2, 5.12)

## Uncertainty
Paired bootstrap, 200 draws, resampling 100 respondents and 263 humans; intervals are point estimate plus or minus 1.96 bootstrap SE of the difference. Study not preregistered; four hypotheses, control grids, swaps, forecast scores added after first results and called exploratory; no multiplicity correction. Best generative cell is a selected maximum of 47 so differences to it are biased. (Sec. 4 Uncertainty, Analysis plan)

## Calibration and probability quality
Vectors scored as forecasts of the same 100 people with ranked probability score (RPS, scaled by K-1) and log score, mixed with 1% uniform. Skill = 100(1 - RPS/RPS_pop), RPS_pop = 0.128. All 14 decision models worse than the population distribution of 163 other people (skill -6 to -55%, median -20%). Jev -18 [-25, -12]. No binned ECE. Recalibration by mixing with the population distribution (weight 0.05 to 0.25 on the vector, leave-one-respondent-out cross-fitting) gives skill -0.5 to 0.9%, close to profile regression (1.0 [0.1, 1.8]). (Sec. 5.9, Table 8)

## Robustness
- Run-to-run (20 respondents re-sent): same rounded answers Jev 95%, Microsoft-Decision-1 95%, Liquid d1 92%, Solar Decide Flash 89%; others 98-100%. (Table 6)
- No-profile (C0) grid: sampled PSS 0.39-0.43 at C0 vs C3 values (Jev 0.40 to 0.70). (Table 6)
- Counterfactual swaps (education, role, gender): decision models shift about half the human size on role (median 0.22 vs human 0.46 SD). (Table 7)
- Version successor: Decider v1.1 27B vs v1 27B PSS 0.660 vs 0.659, 98% rounded answers agree. (Sec. 5.10)
- Interface comparison: GPT-6 Luna generative PSS 0.621 vs as decision model 0.547 (R) / 0.568 (A); correlation component 0.566 vs 0.339. Endpoint weights equality unverifiable. (Sec. 5.3)
- Language: Lithuanian items, English JSON state; mixed-language effect untested. No option-name or cardinality tests.
- Acquiescence: Jev +1.01 human SD, Microsoft-Decision-1 +2.68 (misresponse to reverse-keyed items). (Table 10)

## Cost and latency
Cost per synthetic respondent (68 items, one request): Jev 1.13 0.33e-3 USD (7,800 input tokens, 0.042 USD per million input tokens), Clef 3.03e-3, Mercury Decide 0.00. C3 grid for the 14 scored models cost 1.27 USD total; 11 new generative models 15.05 USD at list prices; control grids 4.33 USD. Latency: only noted qualitatively (Solar Decide about two minutes per respondent). (Table 13, Sec. 4)

## Cascade or escalation
None.

## Test-data exposure
Human data public since 2020; decision models not tested for memorisation. Authors argue against simple recall since C0 vectors are further from human marginals than C3 averages for 12 of 13 models. (Sec. 7 Memorisation)

## Code and data
De-identified human data CC BY-NC 4.0 (original audit). Code, raw outputs and tables available from corresponding author on reasonable request. (Data and code availability)

## Authors' limitations (Sec. 7)
One language, country, instrument set, self-reports; n=100 noise (mediation especially); selection among 47 cells; minimal reasoning only; new and old models queried months apart; request design differs between classes; alpha endpoint without seed, same-day retest only; no measurement invariance; no memorisation test.
