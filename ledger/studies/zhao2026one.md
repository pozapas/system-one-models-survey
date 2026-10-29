# zhao2026one

arXiv 2610.30777v1 (cs.LG), 22 Oct 2026. "One Pretrained Decision Model Is Enough for Training-Free Generalist Graph Anomaly Detection." (title block)
Authors: Xinyu Zhao, Qingyun Sun, Ziwei Zhang, Tianchen Zhu, Daqing Li, Jianxin Li; Beihang University. Affiliation type: academic. (title block)

## Task and data
Node-level graph anomaly detection on seven attributed graphs: ACM, CiteSeer, Cora (citation), BlogCatalog, Facebook, Weibo (social), Amazon (co-review). Anomaly labels are the benchmark labels (injected anomalies on several graphs, real on others); used only for metrics. Metrics AUROC and AUPRC with seven-dataset macro averages. (Sec. 5.1)

## Decision model
Not the TypeSafe Jev. The method named Jev-GAD builds semantically labeled node-evidence states (Graph-to-State), asks a binary anomalous-versus-normal question, and reads the option logits of a single frozen Qwen3-4B (no exact revision) at two fixed single-token options; the score is sigma(logit_anomalous - logit_normal). The decision score is fused by equal-weight rank fusion with four statistical scores (aggregation, ECOD-style, Isolation Forest over five seeds, OCSVM), so the headline numbers describe a fused system. Decision-only ablations (Fig. 3) are the clean decision-model quantities. No hosted version or API. (Sec. 4.2, 5.1, 5.3)

## Comparators and tuning
15 baselines: supervised (GCN, GAT, BWGNN, GHRN), unsupervised (AnomalyDAE, CoLA, TAM), generalist (ARC 10-shot with target labels, UNPrompt, AnomalyGFM, IA-GGAD, ARCzero, GAD-MoRE), training-free (TFGAD, FreeGAD). Previously reported and reproduced results follow their own protocols, so budgets are not matched; Jev-GAD is training-free. Strongest baseline macro-averages: GAD-MoRE AUROC 82.09, AUPRC 36.96. (Sec. 5.1, Tables 1, 2)

## Results
Jev-GAD average AUROC 89.18% and AUPRC 52.40% (mean over runs, standard deviations in Tables 1, 2). Decision-only AUPRC CiteSeer 74.04, Cora 51.89 versus Statistical-only 71.06, 67.34; fused 88.02 and 76.10. Anonymous Fields drop Decision-only CiteSeer AUPRC from 74.04 to 19.79 (Mismatched Semantics 41.90). Prompt and option-order variants on CiteSeer fused AUPRC 86.81, 88.20, 85.01 versus 88.02. (Sec. 5.2-5.6)

## Cost and latency
Amazon (10,224 nodes) about 116 s (31 s CPU, 85 s decision inference); Cora (2,708 nodes) about 31 s; frozen Qwen3-4B readout about 120 nodes per second, 9.6 GiB peak GPU memory (GPU model not stated in the text). (Sec. 5.7, Fig. 6)

## Calibration, cascade
No calibration analysis. No escalation cascade (rank fusion only).

## Test-data exposure
Public benchmarks released before 2026.

## Code and data
https://github.com/zhaoxinyu2002/Jev-GAD

## Authors' limitations
No limitations section; the text names language-model inference as the main cost relative to numerical training-free scoring (Sec. 5.7).
