# qian2026soma: SOMA: Continuous Monitoring and Intervention for System Two Reasoning with System One Models

arXiv:2610.26793v1 [cs.AI], 19 Oct 2026 (HTML title block; fulltext/2610.26793.html and .txt). Extractor batch V18.

## Authors and affiliation
Ruizhi Qian, Lei Shi, Tianyu Hu, Bo Yan, Song Wang, Yu Tian, University of Central Florida (title block). Affiliation type: academic. No code or data release statement was found in the text (no repository URL for SOMA).

## What is measured
An application-level study. Jev serves as the "S1" monitor of a running reasoning model ("S2"). At every pause (every 256 thinking tokens plus up to 128 tokens to the next line break) Jev receives the task, the reasoning so far and a natural-language monitor statement and returns a probability that the statement holds (§3.2, App. A.2). A one-sided cumulative sum of logit(p) minus logit(0.5) triggers a reminder and then a takeover (§3.3). The paper never reports Jev's own accuracy, AUROC or calibration against labelled monitor judgments; it reports the downstream accuracy, abstention and token count of the S2 model with and without SOMA. Ledger rows are therefore system-level outcomes with a Jev monitor in the loop, not model-level agreement. Thresholds are "calibrated" (chosen to minimise harm on 200 questions per scenario) but this is controller tuning, not probability calibration (§3.4).

## Task and data
Scenario 1 overthinking: GSM8K (1,319), MATH-500 (500), AIME 2024-2025 (60), AMC 2023 (40), GPQA-Diamond (198) (§4.1). Scenario 2 unanswerable questions: SUM test set (284 unanswerable + 284 answerable) and UMWP (300 + 300), following Liu et al. 2026 (§4.1). Math answers checked with Math-Verify; GPQA-D official labels; SUM and UMWP official answerability labels; abstentions identified by the rule of Liu et al. (2026) (App. A.1). Each question sampled once per method (§4.1).

## Decision models evaluated
- Jev as S1, "accessed through its API", the only S1 model (§4.1, App. A.1, Limitations). The run-time version is not stated; the reference list cites "Online documentation Model jev-1.13.0; accessed 5 October 2026". The authors note Jev "is a hosted proprietary model whose behavior may change across versions" and that they test no other S1 model.
- S2 models: Qwen3-8B (thinking mode, temperature 0.6, top-p 0.95, top-k 20) and DeepSeek-R1-Distill-Llama-8B (no top-k), served with vLLM, generation limit 32,768 tokens (§4.1).

## Comparators and tuning-budget parity
Vanilla S2; for overthinking: budget forcing, DEER, Dynasor-CoT; for unanswerable questions: DEER, Dynasor-CoT, AbstentionBench prompt, statistical early stopping (SES), Answering the Unanswerable (AtU, a hidden-state probe trained per S2 model). All baselines reproduced from released code with the same decoding and data; tunable parameters selected "with each paper's own procedure on the same calibration sets as SOMA's thresholds" (§4.1, App. E). SOMA's thresholds h: overthinking 0.25 (Qwen3-8B) and 1.5 (R1-Distill-Llama-8B); unanswerable 4 and 3, chosen with tolerance delta=0 on 100 easier and 100 harder questions per scenario disjoint from test sets (§4.1, App. C). Single-run readout: SOMA is run once without takeovers and takeover outcomes are read off at the first pause where evidence reaches h (§4.1, App. B), so reported SOMA outcomes are simulated from one run rather than executed.

## Reference labels
Benchmark answer keys and official answerability labels (administrative_field).

## n and sampling
2,117 overthinking questions (1,319 + 500 + 60 + 40 + 198) and 1,168 unanswerable-scenario questions (568 + 600); one sample per question; no confidence intervals, no repeated seeds, no significance tests. Differences such as 91.0 to 91.3 average accuracy are within sampling noise given AIME has 60 and AMC 40 questions. Ablations use a fixed hashed subset (MATH-500, AIME, 100 SUM pairs, 200 UMWP questions) (App. C).

## Test-set exposure
All benchmarks public and pre-2026 (GSM8K, MATH-500, AIME 2024-2025, AMC 2023, GPQA-D, SUM, UMWP); no contamination check reported.

## Cost and latency
Only S2 tokens are reported (mean tokens per question). S1 is called at every pause through a paid API; "we do not measure wall-clock latency" and no money cost or S1 call counts are reported (Limitations). Scanning every 128 tokens costs "about 1.5-2 times as many S1 calls"; every 512 tokens roughly halves them (App. D).

## Calibration
None for Jev. The cumulative-sum controller treats Jev's p as calibrated evidence on the log-odds scale, but no calibration test of Jev on this task is reported.

## Cascade or escalation
Not a cascade. The two-stage reminder-then-takeover rule is ablated: remind-only (never take over) leaves abstention near vanilla (Qwen3-8B 74 vs vanilla 72 vs SOMA 92 on the ablation subset); no-reminder variant needs a much higher overthinking threshold (Table 4).

## Option-name, cardinality, language, robustness
Scan-interval sensitivity (Table 6). Monitor statements are fixed English sentences (Table 1); no paraphrase or option-name tests.

## Code and data
No release statement for SOMA; benchmarks are public.

## Authors' own limitations (Limitations)
Two scenarios on mathematical and scientific reasoning with two 8B S2 models; only Jev tested as S1 and its behaviour may change across versions; paid API call at every pause and no latency measured; takeovers are irreversible and raise false abstentions on answerable questions.

## Notes for the grader
Headline numbers: overthinking token cuts of 36% (Qwen3-8B) and 16% (R1-Distill-Llama-8B) with average accuracy 91.0 to 91.3 and 84.4 to 84.8; abstention 70.5 to 87.2 (Qwen3-8B) and 38.2 to 59.4 (R1-Distill-Llama-8B). On R1-Distill-Llama-8B SOMA's average abstention (59.4) is below SES (62.7) and AtU (67.6) (Table 3), and false abstention rises from 2.1 to 4.8 and from 2.4 to 8.0. The abstract's "up to 36%" and "70.5% to 87.2%" are the best of two S2 models.
