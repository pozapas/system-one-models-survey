# han2026niocis: NIOCIS: Typed-Decision Next-Hop Routing with Node-Conditioned Option Spaces for Tool-Use Agents

arXiv:2610.25985v1 [cs.CR], 19 Oct 2026 (HTML title block; fulltext/2610.25985.html and .txt). Extractor batch V18.

## Authors and affiliation
Jin Han, Mingfeng Xin, Feng Liang, Jingtao Yu (title block). The only affiliation printed is "Independent Researcher"; the HTML title block attaches "Affiliation:" labels oddly, so the mapping of authors to affiliation is ambiguous. Affiliation type: independent (title block). The data come from a "production SOC agent fleet" served "behind our gateway" (§5), so an industry link is plausible but is not stated. Code at https://github.com/geilihan/niocis (Reproducibility statement).

## Task and data
Next-hop routing for a tool-use agent fleet. The decision is "which declared option at a state, plus stop, does the fleet take next" (abstract, §3). Data are a Langfuse export of 22,328 records (22,192 tool calls) over 1,656 traces from a production security-operations-centre agent fleet, September 2026 (§5). Folding gives 1,615 episodes, a 154-name tool catalog, 18,068 decision states split 12,613 / 1,580 / 3,875 by trace hash 70/10/20 (Table 1, §5). Held-out test: 345 episodes, 3,875 decisions. Median 46 declared options per state, mean 40.2 (§1, §6). 7.9% of test targets fall outside the declared option set, a 92.1% ceiling for masked readouts (§5). Tool-result bodies are stripped, so state is structural only (§9). Public replication streams (BPIC'12, BPIC'17, helpdesk, receipt, roadtraffic, statechart, ToolBench, API-Bank) are reported in §6 E5 and App. B, but they use feature MLPs, logistic regression and Markov tables, not a typed decision model, so no ledger rows use them.

## Decision models evaluated
- Laya 0.3.21, "an open non-autoregressive typed-decision engine built on the ModernBERT-large encoder" (421M parameters), checkpoint convaiinnovations/laya via ModelScope, pypi package laya (§5, Reproducibility). Used four ways: (i) zero-shot typed choice over the declared options with one scalar temperature refit on validation NLL (T=3.0, the ceiling of the grid; the authors say this arm's calibration "is not to be read as calibrated confidence", §6 E2); (ii) frozen-encoder hidden-state linear probe, CE or CE+Brier (Table 2); (iii) the "typed encoder, fine-tuned" for 3 epochs, seed 0, and a frozen-encoder variant (Table 9); (iv) probe rows in the escalation hybrid (Table 5).
- No Jev, Kev or Nimble is run. Related typed models (this-that-model-1.0, JevLite) are cited for latency (§2).

## Comparators and tuning-budget parity
- Per-node majority arm 26.8%, logistic regression 32.3%, feature MLP 32.8% (5 seeds), edge-ID readouts (Table 2). These are trained on 12,613 logged decisions.
- jpt-4b (4B general checkpoint): zero-shot all options 9.0% on a seeded 200-decision sample, 9.9% on a random 800 sample; zero-shot top-20 / 10 / 5 candidate shortlists 12.1 / 14.4 / 19.9%; LoRA-tuned one epoch on the training fold 31.9% on the full fold (Tables 9, 13, §7). The authors state that LoRA-tuned jpt-4b "is the like-for-like opponent for the typed encoder" (Table 13 caption). Zero-shot rows are not budget matched to the tuned typed encoder; the paper says so ("Tuning is what separates the two families", §7).
- MIMO Pro V2.6 (production reasoning model behind the authors' gateway), re-prompted zero-shot, one call per hop, tool results stripped, 2,048-token completion budget; 66 replies (1.7%) unparsed and scored as errors (§6 E3). The authors call 9.6% "a transfer-floor number for a stripped stand-in" and note the asymmetry with a readout trained on 12,613 decisions.
- No version or revision date is given for MIMO Pro V2.6 or DS V4.1 Flash (labeling judge). Laya is pinned by version number 0.3.21 but no run dates are given beyond "September 2026" for the logs.

## Reference labels
The deployed fleet's own logged next hop at the same realized state (§3, §5). This is teacher-forced behavioral agreement, not a correctness label (coded administrative_field here). Task outcomes (completed 66.3% of episodes) are derived by a convention (close-out call update_goal), checked by an LLM judge given the convention, plus a 30-episode manual re-reading adjudicated "by an AI assistant from session logs rather than a separate human auditor" (§5). The paper itself calls these labels "weak".

## n and sampling
Test n = 3,875 decisions in 345 episodes (Table 2). Trace-disjoint hashed split. Table 3 reports 95% CIs from 2,000 trace-clustered bootstrap resamples for paired differences (for example feature MLP CE + Brier minus majority +5.70, CI [+4.60, +6.90]). Headline accuracies in Table 2 carry only a 5-seed standard deviation (±0.001 to ±0.007), not CIs. The E3 replay is single-seed (seed 0). Zero-shot LM rows use samples of 200 or 800 decisions, not the full fold (Table 9 caption, §7).

## Test-set exposure
Private production logs from September 2026 (§5). New / private. The derived pseudonymized corpus is released under CC BY 4.0; the raw export cannot be redistributed (Reproducibility). Public replication corpora (BPIC etc.) predate 2026 but are not used for decision-model rows.

## Cost and latency
Typed-choice predict 19.5 ms p50 including the encoder pass (17 declared options measured); encoder pass alone 10 ms; zero-shot arm 0.30 s p50 in-vivo CPU (§5, §6 E3, App. B). MIMO Pro V2.6 2.2 s p50, 7.4 s p90 (§6 E3). jpt-4b 0.22 s zero-shot, 0.24 s LoRA-tuned per decision (Table 13). Hardware: 2x NVIDIA H20, nvcr.io/nvidia/pytorch:26.03-py3 container, batch-1 GPU wall clock (Reproducibility). No token or currency cost is reported (the stripped export records no per-call usage, §6 E3).

## Calibration
ECE-15 ("the 15-bin convention"; binning scheme not stated). Feature MLP CE 0.045; probe CE+Brier 0.122; edge-ID probe 0.458; Laya zero-shot 0.031 at fitted T=3.0 (0.010 at T=1000, grid-dependent) (Table 2, §6). Temperature scaling used only on the zero-shot arm; trained arms report raw masked-renormalized confidence. CE vs CE+Brier ablation in Table 6. AURC 0.409 to 0.432 for feature arms; 0.426 for the fine-tuned typed encoder (Table 12). Selective accuracy 96.9 / 93.6 / 91.9 / 82.2% at 5 / 10 / 15 / 20% coverage (Table 12).

## Cascade / escalation
Confidence-gated accept/escalate with the probe at tau 0.55 / 0.75 / 0.9 and MIMO Pro V2.6 as escalation arm: match 20.9 / 19.1 / 16.5% at 74.1 / 80.2 / 85.0% LLM calls, strictly below the pure probe row (30.7% at 0% calls) and above the pure LLM (9.6%); the authors call it "a negative one for confidence-gated cascade calibration on this stream" (§6 E3, Table 5). Alternative threshold scales close at most 1.8 of a 9.8-point gap. Containment: the fine-tuned model ranks the realised hop in its top 20 for 90.7% of decisions (§7 E23c, E23f).

## Option-name, cardinality, robustness
Zero-shot Laya picks the first-printed candidate 22% of the time against a 5% uniform rate although option order was shuffled per decision (§7 E23a). Branch-factor buckets (Table 4): <=3 options 92.0 to 93.9%; 11+ options 21.5 to 27.6%. Option-space ablation (Table 8): node-conditioned graph space +3.5 points over a flat 155-class catalog, +1.4 over a size-matched global-frequency space, +0.13 [0.00, +0.27] for no traversal. Edge identifiers vs class names: class space better at the SOC catalog size (§6). Label-corruption stress E4 at 12/30/50% is not a decision-model accuracy test.

## Code and data
Code and pseudonymized derived corpus at https://github.com/geilihan/niocis with MANIFEST.sha256 (Reproducibility). Raw export and label mapping withheld.

## Authors' own limitations (§9)
Replay is teacher-forced against a realized fleet policy, so a better policy cannot show gains; graph traversal adds nothing measurable over node-conditioned options; derived outcome labels certify declared completion, not report quality; tool-result bodies stripped; one deployment, four stage slices; edge IDs do not beat class space at this catalog size.

## Notes for the grader
The reference is the fleet's own behavior, so agreement is bounded at about 25.6 to 44.9% by the state (§7 E23e, Table 11). Absolute accuracy of the typed model is therefore not comparable to correctness-labelled benchmarks. The abstract gives 32.2% on 3,875 held-out decisions and 10 ms; the introduction says the feature readouts reach 32.8%.
