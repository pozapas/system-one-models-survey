# ma2026worldstream

arXiv 2610.28827v1 (cs.CV), 20 Oct 2026. "WorldStream: Streaming Interactive 3D Worlds with Hierarchical Planning and Persistent State." (title block)
Authors: Xiaoxiao Ma, Weiyang Jin, Yanwen Ma, Haoran Li, Zhixiang Wei, Songchun Zhang, Yaowei Li, Junhao Zhuang, Zeyue Xue, Yuming Li, Zheming Fu, Haoyang Huang, Nan Duan, Feng Zhao. Affiliations: University of Science and Technology of China; Joy Future Academy, JD. Affiliation type: mixed (university plus company lab). (title block)

## Task and data
Application paper: an open-ended 3D world generator in which a hierarchical Macro and Micro planner built on a typed decision model emits typed fields (preferred value plus probability distribution over permitted alternatives), then a bounded resolver searches those distributions for a jointly feasible assignment before deterministic code builds geometry. (Abstract; Sec. 1; Sec. 3.2)
Only one measurement concerns the decision model: 100 probability distributions "produced by the decision model" were retained and evaluated under two resolution rules (independent argmax per quadrant versus a joint solver over terrain, water, biome, Macro-role and adjacency constraints). Success means all hard constraints hold. (Sec. 6.1, Table 3)

## Decision model
"Jev" is cited only as "Decision model documentation, 2026" accessed 2026-10-02 (ref. 33). No version, no run date, no API or cost detail reported. The text says "Jev produces decisions under a typed schema in which every field returns a preferred value together with a distribution over the permitted alternatives" (Sec. 1). Weak measurement: the 100 distributions come from the paper's own pipeline, the number of fields or constraint checks per plan is not stated, and the constraint checks are programmatic.

## Comparators and tuning
Comparator is the same probabilities resolved by independent argmax (no second model). No tuning-budget issue. (Sec. 6.1)

## Reference labels
Programmatic constraint checks (terrain, water, biome, Macro role, adjacency); no human labels.

## Results used
Independent maximum-probability selection leaves 63% of plans invalid (37% overall success); joint resolution makes all 100 plans executable without changing the probabilities. Table 3 gives per-constraint success for independent selection (overall 37%, then 55%, 69%, 74%, 82%, 84%, 88% across the six constraint columns, as the extracted cell order shows) against 100% for the joint solver; the extracted text of Table 3 is garbled, so column names were not matched and only the overall figures are recorded. (Sec. 3.2, Sec. 6.1, Table 3)

## Intervals, calibration, cascade, robustness
No intervals, no calibration analysis, no cascade, no option-name or language tests for the decision model. Streaming readiness experiments (Sec. 6.2) measure the runtime scheduler, not the decision model.

## Test-data exposure
New, generated map tiles and route traces.

## Cost and latency
Not reported for the decision model (wall-clock results in Sec. 6.2 are for tile preparation).

## Code and data
Project page and demo listed (https://krennic999.github.io/WorldStream/); no code release stated in the text.

## Authors' limitations (Sec. 7.1)
Bounded generation vocabulary, local controllers, curated geographic rules, reconstruction depends on retained records and compatible generator and asset versions; storage and simulation policies for long-running worlds left open.
