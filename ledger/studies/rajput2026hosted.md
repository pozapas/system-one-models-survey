# rajput2026hosted

arXiv 2610.16655v1 (cs.AI), 12 Oct 2026. "Does a Hosted Decision Model Respect Irrelevant Alternatives? A Pre-Registered Test of Option-Set Dependence in Jev."
Authors: Dushyant Rajput, Nirdesh Chauhan, Siddharth Kosaraju, AltSlate Labs LLP. Affiliation type: industry (independent small company; no stated tie to TypeSafe). (title block)

## Task and data
- Independence of irrelevant alternatives (IIA) test: how added options change the log-odds between the gold label A and the strongest wrong label B. BANKING77 (77 intents, 1,000 test items from the mteb/banking77 copy), CLINC150 (150 intents, out-of-scope removed, 1,000 items), AG News (4 topics, 500 items, control outside the Holm family). Selection run (full label set, two random orderings) fixed A (gold) and B (wrong label with highest mean probability); selection-run accuracy 0.82 / 0.91 / 0.87. "Contested" items (A and B both >= 0.05): 319 BANKING77, 254 CLINC150, 74 AG News (647 total). Shift analyses use contested items; accuracy and flip rates use all items. (Sec. 3.2)
- Reference labels: benchmark gold labels (human-annotated public datasets). Option names are label names in plain words. All datasets public pre-2026; no contamination check.

## Decision model
- jev-1.13.0, hosted, POST /v1/systemone, Choice questions (and Noul yes/no questions in Exp 4). Version pinned on every call; any other returned version aborted the run; all 299,463 calls returned jev-1.13.0. Probabilities on a 0.01 grid; API not deterministic. Run dates not stated (document dated October 2026). (Sec. 3.1)
- Experiments: Exp 1 one added option (five decoys: far, random, near-A, near-B, B-clone; 2,500 items; 115,000 calls); Exp 1n neutral names (200 items, 4,800 calls); Exp 2 option count K in {2,4,...,128,255} with off-domain or in-domain padding (96,000 calls); Exp 3 question isolation (30,000 calls); Exp 4 yes/no per option (38,663 calls). Total 284,463 calls plus a 15,000-call drift check = 299,463 calls; a 200-item pilot (4,900 calls) excluded. (Table 1)

## Comparators and tuning
Local baselines on contested items only (exploratory): Kev-4B (scores each option independently then normalises; run through its TypeSafe-compatible server) and a Qwen3.5-4B-Base label-probability readout (all options listed in the prompt). Both deterministic, bf16 on one NVIDIA GB10. No tuning of any system. (Sec. 4.6)

## Design and uncertainty
Pre-registered five hypotheses; items, decoys, padding, companions and analysis code frozen (sha256) before first measurement call. Unbiased squared-excess statistic separates systematic shift from noise (every option set run twice). Item-level bootstrap, 10,000 resamples stratified by dataset; Holm correction; TOST equivalence at 90% interval. An independent reviewer (a Claude model, no human reviewer) recomputed headline numbers. (Sec. 3.3, 3.5, Acknowledgments, Sec. 6)

## Headline results
- H1 supported in 10/10 cells: RMS systematic shift 0.20 to 0.52 nats vs RMS run-to-run noise 0.15 to 0.17; far off-domain option (at most 0.1% of mass) shifts 0.20 to 0.23; near-A 0.26 to 0.31, near-B 0.24 to 0.32, clone 0.43 to 0.52 (AG News clone 0.56). (Sec. 4.1, Table 3)
- Direction: near-B +0.099 [0.073, 0.124], near-A +0.008 [-0.019, 0.035]; larger when listed first (near-B +0.18, clone +0.57). Clone test intermediate between Luce and elimination by aspects: delta L pair +0.365 [0.335, 0.396], delta L clone -0.110 [-0.163, -0.060]. (Sec. 4.1, 4.2)
- Option count: RMS shift 0.26 at K=4, 0.68 at 32, 1.02 at 255 (off-domain); 0.26, 0.54, 0.80 (in-domain). Slope 0.134 [0.113, 0.157] nats squared per doubling of K. Off-domain padding at K=255 takes 6.8% of mass and lowers accuracy 0.853 -> 0.814 (all items). (Sec. 4.3)
- Top choice differs from base in 5 to 6% of items for far, random or near decoys and 15% for a clone (all BANKING77 items); on contested items 14 to 16% and 31%. (Sec. 4.1)
- Question isolation: nine conditions all pass TOST; mean change in P(A) below 0.0006. (Sec. 4.4)
- Yes/no per option removes set dependence (RMS under 0.02) but accuracy -0.087 [-0.105, -0.070] vs Choice (0.693 vs 0.849 at K=128). (Sec. 4.5)

## Calibration
Expected calibration error 0.077 at base (binning not stated); accuracy 0.855 base. ECE not otherwise analysed; no recalibration. (Sec. 4.1)

## Robustness
Option-name tests: neutral names ("Option 37", label moved to description) leave the effect the same or larger (near-B 0.100 vs 0.085 named). Order: positions manipulated, full permutations. Option cardinality 2 to 255. Epsilon 0.01 sensitivity unchanged. Language: English only. (Sec. 4.1, 4.7)

## Run-to-run noise
Median |delta L| 0.09 to 0.11 for Jev, 0 for baselines; in 39.5% of items three identical repeats are not all equal; about 1% of top choices flip between identical calls. End-of-run drift check null (mean delta L -0.001). (Table 4, Sec. 4.4, 5)

## Cost and latency
Main run used 161.7M input tokens at 0.042 USD per million (6.79 USD total for 284,463 calls plus drift check), about 47 requests per second at concurrency 16. No per-call latency. (Sec. 1, Appendix C)

## Cascade or escalation
None.

## Code and data
Pre-registration, frozen items (sha256 cd5db21b...), analysis code and raw responses "available from the authors on request." (Appendix C)

## Authors' limitations (Sec. 6)
One model version, one task family (single-label text classification with label names only); LLM-reviewed materials (no human reviewer; near-decoy check by Claude flagged 4 of 300); contested items only (about a quarter); run paused once (HTTP 402 after 210,505 of 284,463 calls, six hours); baselines exploratory; one post-run analysis correction; BANKING77 loaded from a copy.
