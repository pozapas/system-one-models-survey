# khezresmaeilzadeh2026claim — Claim Laundering: When Agent Decision Models Trust Records Over Reality

arXiv:2610.25947v1 [cs.AI], 19 Oct 2026. Full text: fulltext/2610.25947.html and .txt (arXiv HTML). CC BY 4.0.

## Authors and affiliation
Tina Khezresmaeilzadeh, Seyedarmin Azizi, Erfan Baghaei Potraghloo, Mehdi Kamal, Massoud Pedram, University of Southern California (title block). Affiliation type: academic.

## Task and data
Agent decision layers read a state with a goal, the agent's own record of actions, and the latest observation. The paper builds paired counterfactual states varying the observation, the logged action and an explicit success claim, in three domains: real Android screen descriptions from AndroidControl (245 apps, 3,200 states), ALFWorld (1,475 states, unseen tasks), WebShop (1,500 states): 6,175 states from 1,235 decision points (Sec 3, Table 1). Five variants per set: Done, Done+claim, Honest, Logged, Logged+claim. Terminal decisions are complete (phones), proceed (ALFWorld) and buy now (WebShop). Live agents: text phone simulator (24 tasks, 11 apps, 30 seeds), 134 ALFWorld tasks, 200 WebShop goals, each with injected silent failures (Sec 8).

## Decision models evaluated
Four models in all domains: decider-4b, Kev-4B, decider-12b, and hosted Jev (jev-1.13-20260917) (Sec 3). On phones also decider-2b, Kev-0.8B, Kev-9B, Laya and base/chat Qwen3.5-4B (Sec 4, App. Table 8, 11). Hosted Jev is closed-weight and was measured only through its outputs; no run dates given. Request formats follow Ling et al. (2026b) verbatim (Sec 2, App. A). Open model revisions are not given in the text.

## Comparators and tuning parity
Detectors compared: model's own score with a tuned threshold, an added second yes/no question, contrastive decoding, random veto at matched rate, 9B LLM judge (App. G), EviGate (a linear readout on an intermediate layer, fit on labelled states) (Sec 7, 8, Table 4, 5). EviGate is fit on target-domain states for the live tests; the gate fit on offline contrast sets fails in live agents (Sec 8). Hosted Jev cannot be probed or fine-tuned (Sec 9, 11). Fine-tuning arm: decider-4b LoRA rank 16 on paired states (Table 6).

## Reference labels
Environment outcome (selected option, "Nothing happens.", screen change). For phones, the dataset's final action is assumed to complete the task (Sec 3). LLM-written step summaries were classified by the same LLM, not verified by humans (App. A).

## n and intervals
Bootstrap over episodes or evaluation groups; live agents paired by task and seed, 95% CIs over tasks; ALFWorld and WebShop one run per task (Sec 3, 8). Phone simulator uses 24 tasks.

## Test-data exposure
AndroidControl, ALFWorld and WebShop are public pre-2026 sources, used as templates for constructed states; no contamination analysis.

## Cost and latency
EviGate adds 0.04 to 2.0% serving latency (no extra forward pass), against 56 to 98% for a second question or contrastive decoding; measured in decider's production engine and Kev's serving path (Sec 7, App. F). No monetary cost.

## Calibration
Not a calibration study; the model's own probability is used as a score (AUROC, balanced accuracy). Thresholds chosen to maximise balanced accuracy on held-out calibration states (Sec 7).

## Cascade or escalation
EviGate veto of terminal options and fall-back to the best non-terminal option; best-of-16 verifier use (App. I). Live ALFWorld success 42.5% (no gate) to 61.2%; WebShop 8.5% to 13.5%; phone simulator 77.2% to 82.4% (Table 5).

## Option-name, cardinality, robustness tests
Twelve phone action options (T3A); record removal test (App. D); activation patching (Fig 2). No option-name perturbation, no language test.

## Code and data availability
No repository stated in the extracted text.

## Authors' limitations (Sec 11)
Injected silent failures in live agents; phone agent is a text simulator; ALFWorld and WebShop failures leave explicit traces; mitigation needs labelled target states and model internals; hosted Jev can only be measured.
