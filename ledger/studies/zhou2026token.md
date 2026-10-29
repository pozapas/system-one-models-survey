# zhou2026token

arXiv 2610.08155 (v1, 06 Oct 2026). "Token-Efficient Multi-Agent Collaboration via System One-Guided Computational Division of Labor". Full text: fulltext/2610.08155.html and .txt. Extractor batch V08.

**Authors and affiliation.** Zihan Zhou, Xinzhe Hu, Hanxu Yang, Liangjian Wen, Zhao Kang; University of Electronic Science and Technology of China and Southwestern University of Finance and Economics (title page). Academic.

**Task and data.** Multi-agent collaboration for question answering, math and code: MMLU, GSM8K, AQuA, MultiArith, SVAMP, HumanEval (main comparison), WebSRC (structured webpage QA with HTML only) (Section 5.1). Test-set sizes are not stated in the text.

**Decision model.** Laya (Convai Innovations 2026) as the System One controller, model card convaiinnovations/laya revision 1c5edc17a7acd8701df6fc341c0d179f1c62c982, accessed 2026-09-29 (reference list; Section 5.1). It selects an inspection condition, the next task among compiler-feasible tasks (Solve, Decompose, Reverse, Review, Repair, Contrast) and finish; target pairs are scored in forward and reverse menu orders and averaged by target identity (Section 4.1). A reader, Qwen3-0.6B (greedy, non-thinking), localizes evidence. No task-specific training. Laya is not evaluated by itself for decision accuracy; it is evaluated as the coordination component in the S1-MAS pipeline with end-task accuracy, tokens and latency, and an ablation in which the controller is replaced (Table 3).

**Comparators and parity.** Twelve baselines without task-specific training (Vanilla, CoT, SC-CoT, Chain, Tree, Complete, Random topologies, AgentVerse, MACNET, SelfOrg, MAD-M2(S), DyLAN); all methods use the same task-solving model (GPT-4o for main and WebSRC, GPT-4o-mini for ablations), questions, response formats and scoring; worker temperature 1.0, B_out 2,048, T_max 4, B_src 2,048 (Section 5.1). Ablation arms: w/ Random (uniform over legal menus), w/ GPT (GPT-4o-mini routes), w/o Reader. Parity is stated as equal worker model and settings; no tuning disclosed for baselines (reported configurations from their frameworks).

**Reference labels.** Benchmark gold answers and HumanEval unit tests (task outcome). HumanEval delivery checks only public interface, not hidden tests (Section 4.4).

**n, sampling, intervals.** Three random seeds; means with standard deviations in Table 1; WebSRC and ablation as seed means without intervals (Tables 3 and 4). Reduction ranges are min and max over 21 benchmark-baseline pairs (Section 5.1). Gaps are small (0.85 points over DyLAN) against standard deviations up to about 1.5 and no significance test is reported.

**Exposure.** All benchmarks are public pre-2026 with released answers (MMLU, GSM8K etc.); no contamination check. Laya is a frozen English encoder and sees no task-specific training.

**Cost and latency.** GPT-4o tokens per question: S1-MAS averages 455 input and 392 generation tokens vs DyLAN 8,006 and 2,220, AgentVerse 7,667 and 3,869, SelfOrg 9,128 and 4,932 (Table 2). Token reductions 78.3 to 94.0% on six benchmarks against five baselines, 44.9 to 97.2% over seven benchmarks against AgentVerse, DyLAN and SelfOrg; mean latency 16.8 s per question, 58.2 to 91.7% lower (Section 5.2, Figure 3). WebSRC 4,847 tokens and 9.47 s vs DyLAN 9,927 and 15.22 s (Table 4). The controller and reader hardware and latency are not reported separately; token accounting counts only GPT calls ("Token accounting includes every GPT call"), so Laya and Qwen3-0.6B compute is not priced.

**Calibration.** None reported; controller scores are used as ranking and stopping signals.

**Cascade or escalation.** Adaptive stopping: finish selected by the controller or fallback when eligible; enforced stop at four worker executions (Section 4.4). Controller replaced by random routing loses 1.83 average accuracy points; replaced by GPT-4o-mini routing loses 1.03 points and uses 2.19 million vs 0.54 million tokens (Table 3).

**Option-name, order, cardinality, robustness.** Forward and reverse menu-order averaging is built into the controller; no separate order-sensitivity test; no language tests.

**Code and data.** No repository URL in the text.

**Authors' limitations.** Only a brief future-work note on multi-page Web retrieval; no explicit limitations section.
