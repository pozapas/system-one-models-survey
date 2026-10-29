# bailo2026system — System Switch: When Should a Fast Decision Model Stop and Think?

arXiv:2610.09683v1 [cs.AI], 7 Oct 2026. HTML retrieved from https://arxiv.org/html/2610.09683 (fulltext/2610.09683.html and .txt).

## Authors and affiliation

Gianluca Bailo, Independent Researcher, Recco (Genoa), Italy (title block). Affiliation type independent. AI assistant (Claude) used for code, analysis and a first draft, disclosed in the Acknowledgements.

## Task and data

Closed-loop Doom (Freedoom 2 in ViZDoom 1.3.1 through doomLaya, commit b25edd3). Every 0.5 s of game time the agent receives a text state and two choice questions: command (7 options: attack, collect, open door, exit, retreat, explore, wait) and weapon (Sec. 3). Labels come from doomLaya's rule-based oracle, which never labels explore, retreat or wait. Held-out test set: 900 questions (600 command, balanced over attack, collect, open door and exit; 300 weapon) from 42 MAP01 games on seeds 45 to 53, capped at 150 per (question, category) group; validation split 130 questions (Sec. 3, Table 1 caption). Intervals resample games, not questions.

## Decision models evaluated

Zero-shot open System One models served through llama.cpp /v1/systemone (commit cb7934c): Julia-1 0.15B, Laya 0.4B (two released revisions, typed-decisions and English base, also run through doomLaya's PyTorch server), Kev 0.8B, 4B, 9B, Lev 4B, Clef-Flash 9B; Strands Decider 2B through its own server. Task-trained references: Laya-v3 (doomLaya fine-tune) and doomGemma (Gemma-4-E2B LoRA, 979 examples) (Sec. 3 "Actors"). No exact revision hashes for the models and no run dates are given; only the llama.cpp commit and doomLaya commit are pinned. Hosted Jev is not evaluated; the paper names the Jev Decision Index and JevBench as related benchmarks (Sec. 2).

## Comparators and tuning parity

Reasoning "thinkers": Qwen3.6-35B-A3B (4-bit GGUF) and Gemma 4 26B-A4B-it, each with and without reasoning, constrained to option keys by JSON schema, reasoning capped at 4,000 tokens (unanswered counts as wrong; Qwen3.6 13 of 600, Gemma 4 199). Thinkers saw the fixed option order only and a text state without the frame offline (Sec. 3, 6). Task-trained actors have training advantage by design; the zero-shot actors and thinkers use the same questions. No prompt tuning on test data is described for the actors.

## Reference labels

Rule-based oracle (synthetic procedure), a single policy that "a reasonable player can disagree" with (Sec. 6 limitations). Coded synthetic.

## n, sampling, intervals

n = 600 command and 300 weapon questions; 95% intervals resample games (Table 1 to 3). Closed loop: 33 games, three seeds per variant, no exit reached (Sec. 5.4, Table 4). Held-out selection check: 500 random half-splits of the 42 games choose actor (by AUROC) and rate on one half and measure on the other (Sec. 5.3). The headline Laya-base and 30% rate are chosen on the same 600 questions on which gain is measured, out of nine actors and several rates (Sec. 5.3, Sec. 6).

## Test-set exposure

The test set was built by the authors from seeds never used for training; Doom, ViZDoom and Freedoom are public but the question set is new. Coded new.

## Cost and latency

Actor median 29 ms per decision on a GPU, 350 decisions per 180 s game (Sec. 5.4); Qwen3.6 reasoning thinker writes a median of 1,300 tokens per decision offline and 9 to 29 s per thought in the loop, busy for 38 to 70% of game time (Sec. 5.3, 5.4). Hardware: game and actors on RTX 4070 / RTX 3060, Qwen3.6 on 2x RTX 5060 Ti, Gemma 4 on the RTX 4070 / 3060, baselines on Ryzen 9 CPU or 2x RTX 2070 SUPER (Sec. 3). No dollar costs.

## Calibration

ECE with 15 bins on the top probability, and AUROC of top probability for right vs wrong, overall and within category (Sec. 5.2, Table 2). The models ship temperature-scaled probabilities stored in the model file and applied by the server; Strands stores one temperature per question type (Sec. 5.2). No additional recalibration by the author. Findings: accuracy, ECE and AUROC are distinct; typed-decisions Laya, Strands and Kev 9B are under-confident; ECE 0.10 for Clef-Flash and Kev 4B, 0.29 for typed-decisions Laya.

## Cascade or escalation results

Offline confidence-gated deferral to a reasoning thinker (Table 3, Fig. 1): Laya base 0.56 alone to 0.75 [0.63, 0.82] with 30% deferred, thinker alone 0.69, perfect selector 0.76; gain over random +0.15 [0.11, 0.19]; Kev 9B and Strands gain nothing (-0.01, -0.02). With actor and rate chosen on held-out games the gain is +0.13 [0.08, 0.18] (fixed order) and +0.08 [0.02, 0.14] (shuffled), and the combination does not beat the better component (+0.05 [-0.12, 0.11] over the better of actor and thinker). Rank correlation between AUROC and gain 0.87 over 18 actor-option-order pairs. Reasoning carries about half the gain (+0.07 without reasoning).

## Option-name, order, robustness tests

Option order shuffled per question: Strands 0.59 to 0.38, Kev 9B 0.60 to 0.50, Laya base 0.56 to 0.49, Clef-Flash unaffected, Kev 0.8B improves; Kev 4B weapon 0.97 to 0.62 (Sec. 5.1). Over-choice of collecting persists at 1.6 to 1.8 times chance with shuffled options (Sec. 5.1). llama.cpp conversion checked faithful against PyTorch (Sec. 5.1). Closed loop, no variant reaches the exit; a fixed explore rule behind the same gate covers as much ground and dies twice as often (Sec. 5.4).

## Code and data availability

https://github.com/dexmac221/system-switch (code, prompts, test set in both option orders, per-question records, game logs) (Reproducibility section).

## Paper's own limitations (Sec. 6)

Oracle encodes one policy; fixed option order affects accuracy and sensitivity; headline actor and rate chosen on the test set; thinkers see text only offline; closed loop small (33 games, one map, no exit); pilot used an abliterated Qwen3.6 variant; thought faithfulness unmeasured; reasoning latency.
