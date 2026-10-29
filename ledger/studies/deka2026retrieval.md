# deka2026retrieval — From Retrieval to Typed Decisions: Calibrated System One Models from Biomedical Sentence Encoders

arXiv:2610.02486v1 [cs.CL], 01 Oct 2026. HTML from https://arxiv.org/html/2610.02486 (saved as fulltext/2610.02486.html and .txt). Key: first surname + year + first content word ("Retrieval").

## Authors and affiliation
Pritam Deka, Queen's University Belfast, Belfast, United Kingdom (front matter). Affiliation type: academic (single author).

## Task and data
Biomedical typed decisions (choice, score, noul) over a text state. Benchmark BioDecide, converted from existing public datasets (PubMedQA, SciFact, HealthVer, PUBHEALTH, DDI-2013, HoC, ADE, Druglib, BIOSSES, MTSamples; knowledge track MedQA, MedMCQA, MMLU-medical) plus MEDLINE-S1 (242,986 training decisions, 30,522 test decisions; 5k test abstracts from files disjoint from training) and a PhysioNet-credentialed clinical track (MedNLI, MIMIC-III trial-eligibility questions, MIMIC-IV name gate). Counts per task are in Table 1 (§4). Totals 371,425 train, 70,753 test decisions (Table 1).

## Decision models evaluated
The authors convert eleven base-size Sentence-Transformers/MLM encoders (PubMedBERT, S-PubMedBERT-MS-MARCO, MedCPT-Query, MPNet, all-MPNet-base-v2, ModernBERT-base, modernbert-embed-base, gte-modernbert-base, BioClinical-ModernBERT and its embedder, BGE-base-v1.5; §5) into four heads: Z (frozen bi-encoder), B (trained bi-encoder), C (cross head, replicates Laya's head), PFR (prior-fused residual) (§3.2). Released model: pritamdeka/S1-PubMedBERT (S-PubMedBERT-MS-MARCO + C head + CE; seen 70.5, three-seed mean 70.2 +/- 0.4; App. L). No dated revision hash is reported for any checkpoint. Comparators: Laya-large (421M), zero-shot and fine-tuned with the same recipe; Qwen3.8-27B and Gemma-4-31B scoring option letters in one forward pass with thinking disabled (§5, App. J). Jev itself is not evaluated; the typed request schema is the one shared by Jev and Laya (§3.1).

## Comparators, tuning-budget parity
All trained models share one budget: 8,000 steps, batch 32, AdamW, three seeds, hyperparameters inherited from Laya, objectives not tuned separately (§5, App. K, Limitations). Laya-large is fine-tuned on the authors' mixture with the same recipe. LLMs are zero-shot with a fixed prompt (App. J); all systems are temperature-scaled on the same calibration splits (§5). The head x objective grid was run on one encoder only (Limitations).

## Reference labels
Source-dataset gold labels converted to gold distributions (§4); PubMedQA-L etc. human-annotated; MEDLINE-S1 labels derived from NLM indexing (human-curated, weak labels; "rather than an LLM teacher", §1, §4); MIMIC-III trial questions human-reviewed (§4). Label type coded human_adjudicated / administrative_field depending on task; headline rows mix tasks.

## n, sampling, intervals
Headline metric chance-normalised accuracy averaged over (question, K) groups, then over tasks. Table 2 reports mean +/- sd over 3 seeds. Paired bootstrap (10,000 draws) over document clusters within each task and Holm correction within each RQ (§5, App. F). LLM rows are single runs (no sd).

## Test-data exposure
Test sets are public datasets mostly pre-2026 (PubMedQA, SciFact, MedQA, MMLU, etc.); LLM contamination on exams "unmeasured" (Limitations), LLM exam scores treated as descriptive (§5). A small exact-input overlap between training and calibration/test splits was found; removing it lowers seen-task scores 0.3-0.4 points without changing rankings (§5, App. I). MEDLINE-S1 test PMIDs excluded from BioDecide; clinical track credentialed.

## Cost, latency, hardware
A ten-question request takes 6.6 ms for C, 15.2 ms for PFR and 22.7 ms for Laya-large (forward pass, batch 1, MI300X) (§6.2). Training on AMD MI300X; the initial campaign took about 36 GPU-hours (App. K). No LLM latency or price comparison reported.

## Calibration
Top-label ECE and NLL before and after temperature scaling; one temperature per type and option-count bucket, fitted by NLL on a calibration split carved from training data (§3.4). After scaling, all RLCD/CE objectives lie between 3.6 and 4.4 ECE; PG has lowest raw ECE (7.0 vs 9.3 for CE with PFR) but no advantage after scaling (§6.3). Fine-tuned encoders ECE 3.8-4.3 vs LLMs 8.5-9.1 (§6.4). On held-out tasks several models are poorly calibrated (Limitations).

## Cascade
Retrospective routing of the 20% least-confident questions to Gemma-4-31B raises macro accuracy over seen and held-out tasks from 59.5 to 68.4 (S-PubMedBERT C, CE) and from 64.3 to 69.1 (Laya-large), against 62.1 for Gemma alone; "a retrospective fixed budget on the test set, not a validated deployment threshold" (§6.4, Fig. 3).

## Robustness
Option-order permutation flips 15.7% of C answers vs 0.3% for PFR (§6.2); cross heads flip 10-17% including Laya-large (App. H). Long-note strategies near chance for base encoders (App. H).

## Code and data
Code https://github.com/pritamdeka/sbert2s1, data https://huggingface.co/datasets/pritamdeka/MEDLINE-S1, model https://huggingface.co/pritamdeka/S1-PubMedBERT (§1). Code under Apache 2.0, model CC BY-NC 2.0 (App. L). Clinical data under PhysioNet DUA, not released.

## Paper's own limitations (Limitations section)
Base-size encoders only, one budget, hyperparameters inherited, grid on one encoder; six parent-retriever pairs not independent; weak MEDLINE labels; exact duplicates not refit; exam contamination of LLMs unmeasured; low seen-task ECE does not imply calibration under shift; clinical tests small, one hospital, surrogate names; not a clinical device.

## Notes for the grader
The headline PG-vs-CE result (2.5-3.0 points) is a controlled in-paper ablation on one encoder (Table 4). Several quantities appear only in figures (routing curves, Fig. 3 beyond the quoted endpoints).
