# bru2026towards — Towards Adaptive and Real-Survey-Aligned Simulated Urban Mobility Behaviour of Generative Agents

arXiv:2610.22407v1 [cs.MA], 14 Oct 2026; CC BY-NC-SA 4.0. HTML from https://arxiv.org/html/2610.22407. Extractor: batch V15.

## Authors and affiliation
Yves Bru (UMR IRIT, Universite Toulouse Capitole), Kamaldeep Singh Oberoi (CESI, CESI LINEACT, Toulouse), Benoit Gaudou (UMR IRIT, Universite Toulouse Capitole) (title page). Affiliation type: academic. Funded by the Occitanie region MIDOC Key Challenge (Acknowledgements).

## Task and data
Mode choice in an agent-based simulation of daily multimodal mobility around Toulouse (453 municipalities), coupling GAMA, OpenTripPlanner and an LLM or other decision-maker (Section 3). Evaluation population: 1,000 synthetic personas (499 households) generated with the eqasim pipeline from census and national travel survey data, making 3,299 trips on one weekday; a disjoint training population is used for prompt tuning only (Sections 1, 4.1). Reference: the 2023 CEREMA household travel survey (10,783 households, 15,775 respondents, interviewed September 2022 to February 2023, 39,203 survey trips used to fit reference models) (Section 4.1). Trip-level agreement uses 9,621 reported trips by 2,930 respondents (Section 4.5). Aggregate scoring is a composite of Jensen-Shannon and Earth Mover's divergences in points over the overall split and five strata (Section 4.1).

## Decision models evaluated
Fifteen decision-makers: three baselines (uniform, all-car, fastest option), four survey-fitted reference models (MNL, LightGBM, KLR, RF), three LLMs (Gemini 3.1 Flash-Lite, Gemini 3.5 Flash-Lite, Mistral Large) each under minimal and tuned prompts, and "Jev (Jev-1.13 TypeSafe model, version jev-1.13.0)" under minimal and tuned prompts (Section 4.1). Jev reads the trip description and returns a probability for each itinerary option; the LLMs write probabilities in JSON text (Section 3.2). Run dates are not stated; API rates "recorded in 2026" (Section 6).

## Comparators and tuning budget
Reference models trained on 39,203 survey trips with 36 variables; text models read 21 core variables plus transport supply, weather and the rest of the day in different forms (Section 4.1). Prompts were tuned per model by an automatic loop of an LLM proposing criteria, scored on the training population and kept if the composite fell; the Gemini 3.5 prompt was tuned by "Claude Opus 5.5" (Section 4.3). "The prompt is not independent of the survey" because each wording was kept for bringing shares closer to the survey on the training population (Section 4.3). So tuned text models were optimised on aggregate survey targets, minimal-prompt models were not, and reference models were fitted on trip-level survey data. The tuning budget is a bounded, disclosed asymmetry. The number of tuning rounds is not stated in the main text ("a fixed number of rounds").

## Reference labels
Self-reported trips of household survey respondents (human, survey-based); aggregate shares weighted to the census (Section 4.1). Coded human_crowd; the paper does not call them adjudicated.

## n, sampling, intervals
Intervals resample persons, not trips; median half-width of a composite's 95% interval is 1.3 points ("population resolution"); three seeds, whiskers give min and max (Section 4.1, Figure 2). Paired differences with 95% intervals. Most composite values appear in text, without per-value intervals (intervals are in Figure 2). Differences below one point are not ordered by the authors (Section 4.4).

## Test-data exposure
Survey microdata distributed by PROGEDO-ADISP under a data-use agreement that forbids redistribution (Section 4.1); survey period 2022 to 2023, so the survey date predates 2026, but only access-restricted microdata, not text, was used. The text models saw the survey "only through aggregate gaps on the training population during tuning." Coded unclear (credentialed access).

## Cost and latency
No latency. Order of magnitude: thirty simulated days of 1,000 personas send about 170 million tokens to the LLM; one measured workload of route decisions costs about $1 with Jev and about $50 with Gemini 3.5 (tuned prompt), at API rates recorded in 2026 (Section 6). No hardware stated.

## Calibration
No calibration analysis (no ECE, Brier or reliability diagram). Decisions are drawn at random from the returned probability mass (Section 3.2); cross-entropy on the reported mode is reported for some models (Table 1). No post-hoc calibration.

## Cascade or escalation
None tested. The conclusion proposes hybrid architectures where a cheaper decision-maker handles the ordinary day and the generative agent is called when an event occurs (Section 6).

## Option-name, cardinality, language and robustness tests
Itineraries are numbered in random order so no option gains from appearing first (Section 3.2). Three seeds. No explicit option-order or language test. Event sensitivity (engine noise) is run with Gemini, not Jev (Section 5).

## Code and data
Protocol, code, seeds and the evaluation population released at https://github.com/Ytlse/generative-agents-urban-mobility; survey microdata not redistributable (Section 4.1).

## Authors' stated limitations
Aggregate modal split alignment does not establish individual realism; the event experiment is a single agent run once; findings hold for the Toulouse area under the survey's conditions; prompts are not independent of the survey; the ordinary-day benchmark does not establish an overall fidelity advantage over the best reference models (Sections 4.3, 5.2, 6). The Conclusion states the limitations, not a separate section.
