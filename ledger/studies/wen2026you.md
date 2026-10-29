# wen2026you — You Only Edit Once: Incentivizing In-Context Capability of LLMs via Local Demonstration Refinement

arXiv:2609.33609v2 [cs.LG], v2 dated 10 Oct 2026 (header); HTML retrieved 2026-10-28 from https://arxiv.org/html/2609.33609, saved as fulltext/2609.33609.html and .txt.

## Decision: not an evaluation of a typed probabilistic decision model. No ledger rows written.

Authors: Jiarong Wen, Qi Wang (equal contribution), Yun Qu, Yixiu Mao, Heming Zou, Haoang Chi, Lizhou Cai, Yiqin Lv, Kaiyu Zhang, Yuhang Jiang, Xiangyang Ji; affiliation marker 1 (institution name not extracted by the HTML conversion). Affiliation type: academic (inferred; not verified in the text).

Reason for exclusion. "Jev-LDE" is a small generative LLM fine-tuned with reinforcement learning with verifiable rewards to emit one JSON edit action (Keep, Delete or Replace) on a retrieved demonstration set for in-context learning (Abstract, §1, §3.1, Fig. 4). At test time "Jev-LDE samples one completion o ~ pi_phi(.|s), which is parsed into an action" (§3.2 area). It does not return a probability distribution over a caller-declared finite answer set in one forward pass, and the paper reports no probability, calibration or typed-decision quantities. The "Jev" in the name is a label, and the paper only calls the editor "System-1" in the Kahneman sense (§1). The measured quantity is the accuracy of target LLMs after editing demonstrations (Fig. 1: one-shot accuracy averaged over TREC, DBPedia and Banking77 rises from 81.2% with Semantic TopK to 88.1%). The target LLMs are ordinary generative models used with ICL.

Not recorded further per brief item 4.
