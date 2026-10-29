# Imperatrice et al. 2026, Are AI Decision Models Biased? A Case Study of Jev

arXiv:2610.19619v1 [cs.AI], 14 Oct 2026, CC BY 4.0 (fulltext/2610.19619.txt, header).

## Authors and affiliations

Ilaria Imperatrice, Taisia Kameneva, Adam Eric Greenberg, Alessandro Romano; the title block lists Bocconi University (affiliation lines are partly garbled in the HTML, only Bocconi is legible). Affiliation type: academic.

## Task and data

Behavioural-economics style audit of one decision model with 41,500 responses (Section 3.1, Table 1): cognitive reflection (4,500; 9 items, 500 responses each, Section 4), anchoring (5,500; dice-sum cue in a shoplifting sentencing case, 500 per dice sum), conjunction (1,000), framing (2,000), sunk cost (2,000), zero risk (1,500), social bias in car pricing (25,000; 125 names in six demographic groups, 100 responses per name and condition, Section 7.1). Plus 15,000 responses on 30 extra conjunction scenarios (Section 6). Every task except anchoring has an original formulation from the classic study and an edited version; Choice tasks are run in forward and reversed answer order (Section 3.1). Answer keys are normative (logical or classic-study answers); there are no external human labels. Original items are public and pre-2026 (CRT, Tversky and Kahneman, Arkes and Blumer, Baron et al.), edited versions are new. Authors state the strong original-versus-edited contrast "does not establish that the model has memorized the original example" (Section 8). Tasks are not aggregated into one score (Section 1). Intervals: Wilson 95% for proportions, normal-approximation simultaneous CIs with Bonferroni, bootstrap across names for group means (Sections 5, 7.2, figure captions). Original and edited versions and the name-only and explicit conditions were collected in separate runs (Limitations).

## Decision model

Jev 1.13.0, responses collected 30 September to 5 October 2026 through the TypeSafe API (Section 3.1). Choice and Score primitives; output fields probabilities, score (probability-weighted level index), choice, confidence (Table 2, Eqs. 1 to 4). Confidence for Choice is (n pmax - 1)/(n - 1).

## Comparators

None run; human findings from the original studies are the benchmark (Sections 5.1, 5.3, 7.2). No tuning budget applies.

## Headline results

CRT: Jev correct in 500 of 500 responses for each of nine items; mean probability on the correct option 90.54 to 100.00% (Table 3, Section 4). Conjunction: original 500 of 500 correct, edited 500 of 500 incorrect, mean confidence on the wrong edited answer 94.28% and 95.42% (Section 5.2); across 30 extra scenarios 53.96% incorrect, 39.79% accuracy with conjunction listed first vs 52.29% second, nine scenarios all wrong and eleven all right (Section 6). Anchoring: mean implied sentence difference 0.302 months between dice sums 3 and 9 (simultaneous 95% CI 0.287 to 0.318) versus 2.53 months in the human study (Section 5.1). Framing: choice almost always the certain option; returned probability on the risky option rises 34.31 points on average under loss framing in the original and falls 10.67 in the edited (Section 5.3). Sunk cost: all 2,000 responses reject investment; probability of investing rises by 6.12 and 4.92 points under sunk cost in the original (Section 5.4). Zero risk, edited: share choosing the larger-reduction program falls from 99.6% to 65.6% when answer order reverses (diff 34.0 points, 95% CI 28.10 to 40.09); confidence falls from 33.7% to 10.8% (Section 5.5). Pricing: probability-weighted group means within $29,529.28 to $29,539.90 (name only) and $29,540.71 to $29,560.75 (explicit); only Black-White explicit has a CI excluding zero, $12.30 on a $2,145 range (Section 7.2).

## Calibration

No ECE or reliability diagram. The paper reports that returned probabilities and confidence move with irrelevant manipulations while the selected answer does not, and that high confidence accompanies wrong answers (edited conjunction). Discussion uses a threshold example (80% automation threshold) to show the consequence of probability shifts (Section 8).

## Cascade and escalation

None run; illustrative only (Section 8).

## Option-name, cardinality, language and robustness tests

Answer-order reversal in all Choice tasks (Sections 4 to 6). Conjunction robustness varies domain, plausibility, wording, grammatical quality and language (Section 6). No option-name, cardinality sweep.

## Cost and latency

Not reported.

## Code and data availability

All data and code at https://github.com/ilariaimperatrice27/JevBehavior (Data and code availability, "working-draft note").

## Paper's own limitations (Section 9)

One original and one edited scenario per paradigm, so results characterise those prompts; derived indices (implied sentence, probability-weighted price) depend on the response grid and Jev 1.13 documentation cautions Score outputs have limited numerical calibration; separate runs for conditions cannot rule out service-state differences.
