# panchal2026fundm: FunDM, Cheap & Label-Free Decision Models from Frozen Language Models

arXiv:2610.17175v1 [cs.LG], 12 Oct 2026. Full text: `fulltext/2610.17175.pdf` and `.txt` (arXiv HTML was not available for this ID, so the PDF was converted with pdftotext). Extractor batch V12.

## Authors and affiliation

Ujjawal K. Panchal, Fundamental AI (uj@fundamental.ai), single author (title page). Affiliation type: industry.

## Task and data

Own-model paper. A small decision head ("FunDM", "FunDM+1T") is trained on a frozen Qwen3-8B backbone to return a probability for every option of a multiple-choice question in one joint forward pass (Sec. 1, 3.1, 3.2). Jev is named only as an example of a decision model (Sec. 1); it is not evaluated. The paper tests two things.

1. Multiple-choice selection. Training pool of 38,067 rows from ARC, SciQ and MedMCQA, about half with distractors from other questions (up to ten options); question-grouped split gives 36,164 training and 1,903 validation rows (Sec. 4). Evaluation on MMLU-Pro (12,032 questions) plus MMLU, OpenBookQA, CommonsenseQA, PIQA, HellaSwag, WinoGrande and BoolQ, reported as accuracy and an equally weighted eight-benchmark mean (Sec. 4 Evaluation). Test splits for MMLU-Pro, MMLU, OpenBookQA; validation splits for the other five (App. A.4). Sizes of the seven other sets are not stated in the text.
2. Agentic run selection. CoderForge-Preview SWE-rebench subset; runs by Qwen3-Coder-480B with OpenHands. 100 held-out tasks with 799 runs (eight per task, one with seven); training on 1,600 runs of 200 tasks (Sec. 6). The student ranks runs by its yes-minus-no logit and is scored by tasks solved and within-task AUC.

## Decision models evaluated and versions

- FunDM (1.05M-parameter head) and FunDM+1T (5.38M, one extra bidirectional transformer layer), both on a frozen Qwen3-8B backbone cut at layer 24 of 36, LM head skipped (Sec. 3, 4). Exact Qwen3-8B checkpoint revision is not given in the text; "Dataset revisions ... will accompany the public implementation" (App. A.4). No run dates reported.
- Teacher: the same frozen Qwen3-8B at full depth with its LM head, option-letter probabilities renormalised over the K letters (Sec. 3.3). Thinking disabled (App. C.2).
- Released CLM-v0.1-8B (Contrastive Language Model), CLM fine-tuned on the authors' rows (three-seed mean), CLM-shaped heads trained from scratch (Sec. 4, Table 1).
- FunDM-CE and FunDM-CE+1T: supervised cross-entropy variants using all 36 layers and a different single-line prompt (Sec. 4, 7.1, App. B.1).

## Comparators and tuning-budget parity

Teacher and FunDM share a multi-line lettered prompt chosen because it gave the frozen model 0.744 versus 0.570 accuracy on 1,903 validation rows (difference 17.4 points, 95% bootstrap interval 15.4 to 19.5) (App. A.2). The CLM baselines use the authors' own input formats (separate encoding); the fine-tuned CLM uses a different random 90/10 row split (34,260 fitting rows) and validation-accuracy checkpointing, whereas FunDM uses a question-grouped 95/5 split and validation KL (Sec. 4, App. C.1). The authors state the agent comparisons "change inputs, supervision, and run scoring" (Sec. 6). CLM-shaped and FunDM heads use seed 0 in Table 1; trained agent heads use five seeds. Checkpoint selection never uses evaluation data (App. A.4).

## Reference labels

Multiple-choice: benchmark gold answers (human-authored keys) used only for evaluation; FunDM heads are trained on teacher probabilities with no correct-answer labels (Sec. 1, 3.3). Correct-answer labels are used only for evaluation, a training-pool prompt comparison and the CE ablations. Agent task: hidden-test pass/fail outcome of each run (task outcome), used only for evaluation (Sec. 6). The distillation target itself is an LLM teacher (full Qwen3-8B).

## n, sampling and intervals

MMLU-Pro n = 12,032 (Sec. 4). Efficiency measured on 500 MMLU-Pro questions shuffled with seed 0 (Sec. 5.2, App. E). Main MCQ results are a single seed (seed 0) with no interval; ablations give means with sample SD over seeds 0 to 2 (Tables 4, 5). Agent heads report five-seed mean and sample SD; the SD "does not measure task-sampling uncertainty". 95% paired task-bootstrap intervals for the difference from the judge include zero; for FunDM+1T they span -8.0 to +8.8 tasks and -0.059 to +0.033 AUC (Sec. 6). Random selection solves 54.9 tasks in expectation.

## Test-set exposure

All eight benchmarks are public and pre-2026. Normalised exact matching finds one MMLU question in the original training pool and none for the other evaluations; "paraphrases and backbone/CLM pretraining overlap are not checked" (App. A.4). 18 source questions sharing a 13-word span with an evaluation question were removed from the expanded pool.

## Cost, latency, hardware

Single NVIDIA DGX Spark (GB10 GPU) (Sec. 4). 500 MMLU-Pro questions, BF16 vLLM, 32,768-token KV pool, 16 active sequences for throughput and batch-one requests for latency (Table 2). FunDM+1T: 38.2 questions/s, 58.3 ms first decision, 13.8 GiB peak versus 24.5 questions/s, 93.7 ms and 20.5 GiB for the full model; released CLM 16.8 questions/s and 216.7 ms (0.69x). Caching teacher probabilities and states for 38k rows takes about 16 minutes; each head fits in under 30 seconds (Sec. 1). A separate PyTorch experiment gives FunDM 1.50x teacher throughput; with all 500 option vectors preloaded, CLM reaches 31.7 questions/s, above the teacher (14.0) and FunDM (21.0) (Sec. 5.2, App. E).

## Calibration

Calibration is not a headline analysis. ECE (15 equal-width bins, raw probabilities, top-option confidence) is reported only for the supervised CE heads on MMLU-Pro: FunDM-CE 0.194, FunDM-CE+1T 0.118, CLM-shaped MLPs 0.067 (Table 8, App. B.2, C.1). NLL is reported for the main heads (FunDM+1T 1.98 versus teacher 2.22 on MMLU-Pro, Sec. 5.1). No post-hoc recalibration.

## Cascade or escalation

None. Exit-depth sweep (Table 6): eight-benchmark mean for FunDM/FunDM+1T is 0.579/0.569 at 16 layers, 0.708/0.716 at 20, 0.747/0.750 at 24, 0.756/0.757 at 28, 0.753/0.755 at 32, teacher 0.757.

## Option-name, cardinality, order tests

Variable option count (up to ten) is supported by shared scoring weights (Sec. 3.2). Prompt sensitivity: teacher scores 45.2% on MMLU-Pro with original option order and 45.1% shuffled; the check "does not test whether student predictions are robust to option order" (App. A.2). Mean teacher agreement of heads about 88%, MMLU-Pro about 75% (Sec. 5.1). No language or option-name tests.

## Code and data availability

Code, figures, aggregate results and task/run identifiers released at https://github.com/Ujjawal-K-Panchal/FunDM under Apache 2.0; model weights, benchmark questions, trajectories and embeddings are not redistributed (App. A.1). The text says the release is "planned" (App. A.1) while the abstract gives the URL.

## Authors' stated limitations

Only Qwen3-8B tested; no larger models, adaptive exits or more seeds; no comparison to Tuned Lens-style objectives; teacher probabilities in agent selection are often near zero or one and task-bootstrap intervals are wide; DeepSWE comparison uses CLM's released embeddings without run text; efficiency measured on one GPU and one MCQ workload (Limitations section).
