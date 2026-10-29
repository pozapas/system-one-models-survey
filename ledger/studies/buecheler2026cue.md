# buecheler2026cue — A Cue's Hidden Price: Auditing Seller Influence on AI Shoppers

arXiv:2610.25843v1 [cs.AI], 19 Oct 2026. Full text: fulltext/2610.25843.html and .txt (arXiv HTML). CC BY 4.0.

## Authors and affiliation
Felix Buecheler (Adelaide University), Gerardo Berbeglia (Melbourne Business School), Mingyu Guo (Adelaide University) (title block). Affiliation type: academic. AI assistance used for writing, code and as part of the method (App. P).

## Task and data
Price-equivalent (PE) auditing: in a counterbalanced, position-controlled two-alternative forced choice between two product cards, the price of the cued product is raised until it is chosen half the time; that premium is the cue's PE (Sec 1, 3). Single-sentence cues: social proof at four intensities, domain-matched authority, scarcity, gain/loss framing, number-preserving reframings, neutral and presence controls. Main audit 113,472 trials over 107 conditions, seven models, two product categories (headphones, coffee machines), six product pairs per category (App. O, Table 24). Jev audit: 49,824 queries plus 20,736 for phrasing robustness (App. O). Stimuli are synthetic and released.

## Decision models evaluated
Jev queried through OpenRouter as typesafe/jev-1.13-20260917 on 30 September 2026, prompt identical to the chat models' prompt, 24 queries per pair and price point, argmax choice used in the PE estimator (Sec 4.7, App. K, App. O). Other models (text, not decision models): GPT-4o and GPT-4o mini (rolling aliases, not pinned snapshots), Claude Sonnet and Haiku, Nova Micro, Llama-3.3-70B (and Llama-3.1-8B excluded as position-driven, Nova Pro excluded for 21% non-response) (Sec 4.4, App. O). No other decision models.

## Comparators and tuning parity
Same prompt and counterbalancing for all models; GPT-4o is the reference for Jev. Jev's price sensitivity matches GPT-4o (0 of 144 cue-free trials keep the pricier product at +10%) (Sec 4.7). Not an accuracy comparison.

## Reference labels
None. The quantity is a susceptibility threshold, not agreement with a reference.

## n and intervals
Six product pairs per category, 24 repeats per cell; 95% bootstrap intervals clustered by product pair (2,000 resamples); the authors warn that with six pair clusters intervals may understate product-level uncertainty and report leave-one-pair-out sensitivity (Limitations, App. F, O).

## Test-data exposure
Synthetic stimuli written for this paper; not applicable to training exposure.

## Cost and latency
Not reported.

## Calibration
Not measured. The paper states it does not equate Jev's stated probabilities with choice frequencies and reports vendor calibration claims "as claims"; crossings of Jev's stated probability agree closely with argmax crossings (Sec 4.7, App. K).

## Cascade or escalation
None.

## Option-name, cardinality, robustness tests
Option order is a core design element: each cue appears in both slots. Jev picks the first-listed card in 60.1% of battery trials (GPT-4o 56.3%), chooses the first card in every equal-price trial for several cue-free conditions, and cue effects are realized mostly in the first slot (slot-specific crossings, Table 21, Fig 5). Input-format dependence: passing cards as a structured object raised strong social proof from 2.0 to 10.8% (headphones). Four task phrasings: ranking stable, strong cues drift more than GPT-4o (App. J, K). Off-domain authority never chosen at equal price (0 of 144). Length and presence controls do not transfer to Jev (filler sentence dispreferred).

## Code and data availability
Stimuli, prompts, seeds, per-trial logs and code released at github.com/Flexxbo/price-equivalent-auditing (App. O). Closed APIs may not reproduce identical outputs.

## Authors' limitations (Sec 6)
Controlled synthetic two-alternative choice; no human baseline; single formulation per construct (one scarcity sentence); PE conflates cue pull with price sensitivity; some PEs censored or unidentified; six product pairs per category; two durable-goods categories; audited models are a convenience sample.
