# khatri2026need — Do We Need an LLM to Know Why Sources Conflict? Decision Models for Knowledge-Conflict Typing in RAG

arXiv:2610.36915v1 [cs.CL], 27 Oct 2026. Full text: fulltext/2610.36915.html and .txt. Census-style evaluation of eleven gateway-served decision models, with cascade and end-to-end tests.

## Authors and affiliation
Parv Khatri, Harshul Jain, Mehak Kapoor, Tanya Sah; all Independent Researcher (title block). Affiliation type: independent.

## Task and data
Five-way knowledge-conflict typing on the Conflicts benchmark of Cattan et al. (2025): 458 queries with about 9.2 search results each, expert-assigned types (No conflict, Complementary information, Conflicting opinions, Outdated information, Misinformation). A stratified development split of 52 queries (settings only) and a test split of 406 queries; Misinformation has 4 test instances (Sec 3, Table 1, Table 3). Further tasks: yes/no decomposition (Sec 6.2), diagnostics for dates, source order and a planted false source (Sec 6.4), an end-to-end generation test with two LLM judges (Sec 6.5).

## Decision models evaluated
All 11 decision models served by one commercial gateway (Vercel AI Gateway) on the census day 25 October 2026, from 7 providers: Jev 1.13.0 and 1.14.0 (TypeSafe), Decider v1.2 and Decider Flash v1.2 (Perplexity), GPT-6 Luna Decisions (OpenAI), Liquid d1 and d1 Ultra, Microsoft Decision-1, Baseten Elephant-1 and Mammoth-1, ScaleDown Classify-1 (Sec 5). Pinned identifiers exist for some; several are unversioned. Laya excluded before any run because the task prompt exceeds its input limit; open-weight models not served by the gateway are out of scope. Classify-1 accepts a single text field only.

## Comparators and tuning parity
Gemini 2.5 Flash with the original paper's prompt verbatim (temperature 0, thinking off; thinking on as sensitivity) and Gemini 3.8 Flash (thinking low and default), rerun on identical inputs, paired comparisons (Sec 5). Decision models receive a choice question with the paper's instruction, definitions and examples word for word (test enforced in code). No tuning of any system; the only data-chosen setting is the decomposition tree v2, selected on development answers of Jev 1.13. Prompts, questions, inputs and split frozen before any test call; later additions specified in writing before running (Sec 5). Answers in other formats were parsed leniently for LLMs (10,527 of 14,470).

## Reference labels
Expert annotator types supplied by the benchmark (Cattan et al. 2025); the paper does not describe agreement or adjudication.

## n and intervals
406 test queries; 95% bootstrap intervals over queries (10,000 resamples) and exact McNemar tests, no multiplicity correction (Sec 5). The paper says intervals are about +/-4.8 points wide so differences under about five points are treated as ties.

## Test-data exposure
Conflicts (2025) is a public benchmark with released labels; its source datasets are older public sets. Rerun Gemini 2.5 Flash scores 60.7 percent in one place and 61.3 percent in Table 2 versus 65.3 percent published; the text notes the hosted model may have changed. No contamination check; the paper notes non-determinism up to 9.4 percent of predictions between identical requests.

## Cost and latency
Billed cost per 1,000 queries and mean latency per query through the gateway (Table 2): decision models $0.04 to $0.41 (two free during the runs) and 0.26 to 0.72 s; Gemini 2.5 Flash $1.66 and 1.55 s; Gemini 3.8 Flash $3.65 and 2.18 s. Prices may differ from provider list prices. These are the study's measured billed costs for classification of 1,000 queries and are comparative.

## Calibration
ECE of the top-class probability; across decision models 0.031 to 0.188 (Jev 1.13 0.103, Jev 1.14 0.113) (Table 2, Discussion). No post-hoc recalibration reported for the main table; a repair of the yes/no tree fitted on one model did not transfer.

## Cascade or escalation
Confidence-gated cascades: the least confident 25% (and 50%) of queries go to Gemini 3.8 Flash. 8 of 11 cascades tied with it at 25 to 37% of its cost; Jev 1.13 at 25%: 68.5% versus 70.0% (p=0.41) at 30% of cost; confidence AUROC 0.64 to 0.76 (Sec 6.3, Table 5). Random escalation is beaten for 10 of 11 models.

## Option-name, cardinality, robustness tests
Yes/no decomposition lowers accuracy for all 11 models (Sec 6.2). Pre-specified diagnostics: publication dates play no measurable role; sensitivity to source order varies widely; a planted false source is detected less reliably as hard labels but shows in probabilities (Sec 6.4). No option-name or language test.

## Code and data availability
Code, prompts, splits and all model outputs released at https://github.com/Parv17k/decision-models-conflict-typing (Abstract, Sec 1).

## Authors' limitations (Sec 7)
Small test set (differences under about five points not significant; cascades shown close to but not formally equivalent); label distribution reflects query selection, only five natural Misinformation queries; census covers one gateway on one day and hosted models change without notice; end-to-end test uses one generator and LLM judges validated on 100 answers; non-determinism of repeated requests.
