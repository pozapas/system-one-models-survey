# Pan et al. 2026, The World Won't Wait: Evaluating and Teaching Agents Under a Live Clock

arXiv:2610.20665v1 [cs.AI], 14 Oct 2026, arXiv perpetual non-exclusive licence (fulltext/2610.20665.txt, header). Borderline inclusion: decision models score predefined legal actions as fast game actors; the abstract does not state the probability output, Section 5.1 states "Decision models score choices; LLMs return a choice".

## Authors and affiliations

Ningxin Pan, Hanyu Li, Wentao Zhang (Peking University); Yeqing Shen, Ning Ding, Yehui Tang (Samsung Research, Beijing). Affiliation type: mixed (academic plus industry).

## Task and data

RealtimeBench: 180 tasks over six game types (Mario, Snake, Tetris, Temple, River, Bird), 30 per type split ten feedback, ten validation, ten test (Section 3.2). Models receive structured text states and choose from legal actions; the game keeps running during inference (live clock), with Paused, Current, 1.5x and 2x clock conditions (Section 3.4). Score is normalised peak in-game progress, 0 to 100, against a per-game reference target (Eq. 2). Reference label type: task outcome. Tasks are newly built from open-source game implementations (Appendix C) so no test-set exposure to model training is expected. Table 1 reports test scores over ten test tasks per game type; Table 2 scores are means of three runs; no intervals are reported anywhere in the main text; dates of runs are not stated.

## Decision models

Jev (version not reported; "Jev costs estimated at $0.042/M input tokens, free output", Appendix B.3), Clef 27B and Clef-flash 9B, StartLux 4B and StartLux-Decision-27B, JevK5 4B (alibiserikbay/JevK5), Open-Jev-2B (ZefanCai), mini-Jev (samatv256), GLiClass 0.4B Instruct-Large v1.0 (knowledgator), decision-model-preview (served by Alibaba Cloud) (Table 1, Appendix B.4). No revision hashes are given for the decision models.

## Comparators and tuning parity

LLMs GPT-6.1-sol (medium reasoning effort), MiMo v2.6 Ultra Speed, DeepSeek v4.1 Flash with the same state, legal choices, clocks and budgets; MiMo uses an action-selection adapter (Sections 5.1, 5.4). Adaptation comparison: TORSI vs ACE, AHE, GEPA adapted to the same Jev student, GPT-6.1-sol teacher, splits and validation gate; "Editable components and search configurations differ ... without matched budgets" (Section 5.3), so tuning parity is not established. TORSI practice budgets are also not matched across ablation variants (Section 5.2).

## Headline results

Table 1 (live clock, average score): Jev 13.51 (latency 0.52 s, US$0.0111 per task), Clef 27B 16.34, StartLux 27B 16.62, StartLux 4B 12.22, Clef-flash 9B 7.66, JevK5 7.42, GLiClass 4.42, mini-Jev 4.01, decision-model-preview 3.80, Open-Jev-2B 1.65; GPT-6.1-sol 1.51 (18.97 s, US$0.5109), MiMo 5.95, DeepSeek v4.1 Flash 2.44. GPT-6.1-sol beats Jev in five game types when paused (Section 3.4). TORSI: Jev 13.51 to 24.19 after two validation-gated rounds (Table 2); frozen guidance lifts StartLux 4B 12.22 to 25.05 and StartLux 27B 16.62 to 20.43 with game-specific regressions (Table 5). Alternatives: ACE 13.22, AHE 16.59, GEPA 14.52 (Table 4).

## Calibration

None; probabilities are used only to pick the action.

## Cascade and escalation

TORSI is a two-timescale arrangement: slow teacher offline, fast student online, no teacher calls during play (Section 4). Not a confidence-based cascade.

## Option-name, cardinality, language, robustness

Clock manipulations only; no option order or naming test.

## Cost and latency

Mean response latency Li and mean API fee per task (Table 1); decision models below one second mean latency; local inference on single NVIDIA L20Y GPUs; GPT-6.1-sol medians 5 to 31 s per game type (Appendix B.2). The authors' own adaptation spending (Table 4 totals) is not recorded in the ledger.

## Code and data availability

No release statement found in the main text; third-party game sources listed with revisions in Appendix C.

## Paper's own limitations

Structured observations only, no raw visual input; TORSI needs resettable environments for offline practice; six game types, two rounds, guidance developed per game type, no unseen-environment transfer (Limitations).
