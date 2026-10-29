# cheng2026metaencoder — MetaEncoder: Exploring the Limit of Bi-Encoders for Multimodal System One Decision Making with Natural Language Interface

arXiv:2610.11316v1 [cs.CL], 8 Oct 2026. HTML retrieved from https://arxiv.org/html/2610.11316 (fulltext/2610.11316.html and .txt).

## Authors and affiliation

Jianpeng Cheng, Guangyu Sun, Aashu Singh, Benyu Zhang, Haixing Dai, Hossein Mansour, Jiangfan Zhang, Shlok Kumar Mishra, Wei Sun, Xuanming Cui, Yanli Liu, Qi Guo, Max Xiangjun Fan, Jun Xiao; all Meta AI (title block). Affiliation type industry.

## Task and data

A natural-language "System One" interface in which the request and each candidate are free text with optional image or video; the model returns a softmax over cosine similarities to the candidates (Sec. 3.1, 3.2). 11 benchmark suites, 190 tasks (Table 1): decision making (JevBench 231 text rows in original 72, easy 48, hard 111 splits; ImaJev-Bench 173 dev entries), understanding (MMLU, MMMU, Video-MMMU, NaturalBench 4,000 rows, TempCompass) and retrieval (NanoBEIR, MMEB-V3 image, video, visdoc) (Sec. 4.1). Closed-set accuracy is Hit@1; retrieval uses nDCG (Sec. 4.2). Retrieval rows are not decision-model evaluations and are not in the ledger.

## Decision models evaluated

MetaEncoder, a bi-encoder fine-tuned from a pre-trained Muse-Glimmer 30B multimodal decoder with a unidirectional (request-to-candidate) InfoNCE loss, last-token representation, option lists optionally in the prompt (Sec. 3). Released at huggingface.co/facebook/meta-encoder; evaluation code at github.com/facebook/meta-encoder-eval (front matter). No dated revision or run date stated. Comparators: OpenJev-27B ("SOTA System One model" with a decision scoring head; Wortega and Contributors, 2026), WeMM-Embedding-9B, Qwen3-VL-Embedding-8B, and the Muse-Glimmer 30B constrained decoder (Table 2, Table 6). The hosted TypeSafe Jev is not evaluated; "Jev Intelligence" is a JevBench aggregate score.

## Comparators and tuning parity

Baselines are reported from or run under the same prompts per benchmark (App. A), but how OpenJev-27B and the embedding models were prompted, whether results were run by the authors or copied, and their versions are not stated in the text read. MetaEncoder is trained with contrastive data targeting the scoring task, whereas the decoder baseline is a generically pretrained model prompted for a single constrained decoding step (Sec. 4.3.5). Tuning-budget parity is therefore not reported.

## Reference labels

Not stated for JevBench or ImaJev (benchmark gold labels from their maintainers: Standhartinger and Contributors, 2026; Mohit and Contributors, 2026); MMLU, MMMU, etc. use published answer keys. Left empty in the ledger.

## n, sampling, intervals

n = 72 / 48 / 111 JevBench rows, 173 ImaJev dev entries. No confidence intervals or seeds for the headline Table 2. Option-order robustness: 10 random permutations on MMLU, SD 0.0014 (C2), 0.0030 (C0), 0.0028 (C1) (Sec. 4.3.3).

## Test-set exposure

JevBench, ImaJev, MMLU, MMMU and others are public benchmarks with answer keys; no contamination check described in the text read. JevBench's training exposure for Muse-Glimmer or MetaEncoder is not discussed. Coded public-pre-2026.

## Cost and latency

No latency or dollar cost; the efficiency argument is caching of candidate embeddings (Sec. 1, 3.2). Hardware not reported.

## Calibration

None reported for MetaEncoder; the paper mentions probability distributions from softmax over cosine scores (temperature tau) but no ECE or Brier.

## Cascade or escalation

None; reasoning traces from Muse-Glimmer prepended to the encoder prompt raise MMMU from 0.5730 to 0.7155 (0.6871 with labels truncated) (Sec. 4.3.6).

## Option-name, order, cardinality robustness

Options in prompt: MMLU 0.5645 to 0.7456, MMMU 0.4875 to 0.5629 (Table 3). Candidate rendering: bare label C1 0.6512 vs label+description C2 0.7767 on MMLU; C1 deficit widens with option count (from +0.0281 at three options to -0.1725 at ten on MMMU) (Table 4). Option-order permutations barely matter (Sec. 4.3.3). Video frame count 8 to 64 (Fig. 2).

## Code and data availability

https://huggingface.co/facebook/meta-encoder and https://github.com/facebook/meta-encoder-eval (front matter). Training data not described in the text read.

## Paper's own limitations (Sec. 4.3.6, 5)

Bi-encoder trails OpenJev-27B on text decision making (JevBench orig 0.9444 vs 0.9861, MMLU 0.7767 vs 0.8601) and is weaker on complex comprehension and adaptation; no explicit reasoning (about 20% gap on MMMU to an unconstrained decoder with chain of thought).
