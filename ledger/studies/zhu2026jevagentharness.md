# zhu2026jevagentharness — JevAgentHarness: Benchmarking, Deploying and Training Decision Models That Share Control with LLMs

arXiv:2610.21412v1 [cs.AI], 15 Oct 2026; CC BY-NC-SA 4.0. HTML from https://arxiv.org/html/2610.21412. Extractor: batch V15. The paper is long (about 2,640 lines of text with 30+ appendix tables); the main text and Appendices E, F and G.5 to G.7 were read, other appendices only searched.

## Authors and affiliation
Kunlun Zhu, Tao Feng, Xu Han, Heng Wang, Jiaxuan You, Heng Ji (University of Illinois Urbana-Champaign), Ling Yang (Princeton University), Xiangru Tang (Google) (title page). Affiliation type: academic (one Google co-author; coded academic as UIUC leads).

## Task and data
Delegating an agent's multiple-choice decisions (tool choice, arguments, stop, reflect, memory, routing, action) to a decision model, with an LLM deciding below a fitted confidence threshold (Sections 2, 4). AgentDecisionBench has three levels: L1 isolated questions (BFCL v4 1,114 tool-choice and 1,949 argument items, When2Call 928 items), L2 step level on recorded runs (5,314 common states of 200 new DecisionGym tasks), L3 task level with the decision model in control (tau^2-bench, ALFWorld, DecisionGym; SWE-bench Verified and Terminal-Bench through existing harnesses) (Section 3). DecisionGym is the authors' simulated customer-service desk with 68 tools plus finish and a scripted answer key at every reachable state; shifted (DecisionGym-Shift) and hard (DecisionGym-Hard) variants added after Stage 1 (Section 3; Appendices D.6, G.9).

## Decision models evaluated
Jev "pinned as typesafe/jev-1.13", "a closed typed decision API released on 15 September 2026", billed through OpenRouter at $0.042 per million input tokens, accessed September to October 2026 (Appendix F). Others: Intern-Decision (0.8B to 4B), StartLux-Decision (0.8B to 27B), OpenAI Decisions API, OpenJev, Clef-Flash and Clef, JevK5, CLM, Laya, Verdict, Imajev-4B, decider-4b, Bosun (Appendix G.7, each with vendor defaults on one L40S), and the authors' AgentDecision-4B (Qwen3-4B with LoRA) and AgentDecision-0.8B (StartLux-0.8B with their recipe) (Section 5; Table 3). AgentDecision-4B is trained with Jev's probabilities as soft labels mixed with the answer key (alpha 0.3) (Section 5), so Jev is also the teacher. Weights are "to be released".

## Comparators and tuning budget
LLM alone (Gemini 3.5 Flash, temperature 0, minimal thinking, native tool calls) is the reference; Flash-Lite as a cheaper agent LLM; keyword and rule controls (Section 6; Appendix F). Pre-registered protocol with Holm correction for eleven Stage-1 tests and four Stage-2 tests, non-inferiority margin 3 points (5 on tau^2-bench) (Section 6; Appendix E). Thresholds are fitted per decision point on 150 shadow-mode tasks per agent LLM (Section 2.1). Asymmetry: AgentDecision-4B is trained on the environment's generator and states; Jev and the other decision models are off the shelf ("served without tuning on our data", Appendix E). The paper discloses this; the "shifted" and "hard" tasks were added after Stage 1 and lie outside the registered families (Appendix E). The test environment (DecisionGym) is the authors' own.

## Reference labels
DecisionGym answer keys derive from scripted plans (synthetic). BFCL and When2Call use their own gold labels (not described here). Task success is judged by the environment (task_outcome for ALFWorld, SWE-bench, tau^2).

## n, sampling and intervals
200 to 500 tasks per test (Table 1 n column), paired task bootstrap (B=10,000) and Tango one-sided score test with Clopper-Pearson-bounded tail (Appendix E). Table 31 gives 95% CIs for differences versus Jev. Headline abstract numbers are point values.

## Test-data exposure
DecisionGym is new and authored for the paper; BFCL v4, When2Call, ALFWorld, tau^2-bench, SWE-bench Verified and Terminal-Bench are public. "Pilots on retired seeds fixed the suite settings" (Appendix E); training, threshold fitting and testing use disjoint random seeds (Section 3).

## Cost and latency
Cost = list prices on run dates applied to measured tokens; Jev $0.042 per million input tokens and nothing for output; GPU price for open models (Appendix F). In one recorded episode a Jev call took 28% of an LLM call's time and 2.6% of its price (Introduction). AgentDecision-4B median 31 ms per answer on one L4 GPU versus 809 ms for a Flash call (Section 7.3). The appendix reports the study's API spend and training cost; those are the authors' own costs and are not ledger rows.

## Calibration
ECE is the 10-bin top-label error (Appendix E). Jev ECE 0.043 on its own visited states; AgentDecision-4B v1 0.010; StartLux-27B 0.012; StartLux-2B 0.177 (Table 31). SFT loss includes a Brier term. Thresholds are fitted rather than assumed calibrated; fitted values with Jev and Flash were 1.00 for tools and 0.99 for arguments (Section 2.1).

## Cascade or escalation
Confidence-threshold cascade is the main mechanism: Jev decided 27.2% of tool choices and 20.8% of argument choices, saving 14.2% of cost with no change in the outcome of any of 500 tasks; a fixed threshold of 0.5 lost 21.5 points; with Flash-Lite the fitted threshold left every tool choice to the LLM (Sections 7.2; Table 2). Five integration modes (Replace, Cascade, Assist, Guard, Trigger) tested (Figure 5).

## Option-name, cardinality, language and robustness tests
Shifted tasks rename the tools and change request wording (DecisionGym-Shift); hard tasks add a rule; ALFWorld unseen rooms; 68 tools with 31 near-duplicates as distractors (Sections 3, 7). All tasks and prompts in English (Limitations). No option-order permutation test found in the text read.

## Code and data
Promised at https://github.com/JevAgentHarness/JevAgentHarness; weights and data derived from Jev or Gemini outputs released only where provider terms allow (Ethical Considerations; Appendix F). Coded partial.

## Authors' stated limitations
English only; mostly Gemini agent LLMs; non-inferiority rather than equivalence; thresholds and model must be refitted for new agents; coding agents gain little (7.0 to 10.5%); no comparison with learned routers such as RouteLLM; GRPO added nothing over SFT; no adversarial observations tested (Limitations; Ethical Considerations).
