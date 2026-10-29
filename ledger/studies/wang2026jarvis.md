# wang2026jarvis — Jarvis: Coordination Deserves a Brain of Its Own in Agentic Interactive Models

arXiv:2610.23804v1 [cs.SD], 16 Oct 2026. HTML retrieved 2026-10-28 (fulltext/2610.23804.html, .txt). Coder: batch V16. Application paper: JEV is the "Decision Brain" inside a voice-agent harness; only Table 6 isolates the decision model.

## Authors and affiliation

Yuxiang Wang, Shengbo Cai, Zhixian Zhao, Yingda Shen, Yuancheng Wang, Xueyao Zhang, Liqiang Zhang, Teddy Sun, Steve Yves, Zhizheng Wu. The Chinese University of Hong Kong, Shenzhen; Tencent Hunyuan; Amphion Technology Co., Ltd. (title block). Affiliation type: mixed. The authors build Jarvis; they are not the vendor of JEV.

## Task and data

Jarvis is a coordination harness for full-duplex voice agents: a Native Gate (LoRA on the front model's control tokens, trained with GRPO on 264 authored bilingual scenarios) decides when to hand a turn to the slow brain; JEV (Choice, Noul and Score typed questions) reads the turn against live tasks and picks among runtime-built operations; code checks task and version before applying (§3). Benchmarks: tau-Voice (278 regular tasks), Full-Duplex-Bench v3 (100 recordings), Full-Duplex-Bench v2 (200 multi-turn tasks at two paces), ContextDialog (80 fixed questions) (§5.1). Direct decision-model test (§5.4, Table 6): JEV vs DeepSeek-V4-Flash and Gemini-3.5-Flash as controllers on 192 new bilingual cases from 24 scenario families, each called three times (576 calls); thresholds chosen on 240 development cases to accept the most control operations while keeping wrong controls at or below 1% (JEV 0.43, DeepSeek 0.95, Gemini 1.00); then replay of the measured decisions in the runtime on 64 cases at four worker completion times (256 replays; 224 cancel or refine).

## Decision models and versions

"JEV" (typesafe.ai); no version string and no access dates in the text read. Jev-Omni is described as a 12B multimodal member built on Gemma 4 with a 256-way decision head and about 8.5M-parameter HUD adapters; it is used in Jarvis-Omni (§4.2) and not benchmarked against comparators here. Front models: Realtime-Venus-Audio 9B, MiniCPM-o 4.5, VoiceChat-11B; shared back end DeepSeek-V4-Flash (§5.1).

## Comparators and parity

Harness comparison holds front model, admission path and back end fixed (Table 2). Controller comparison: same options and context, threshold per controller tuned on 240 development cases (tuned vs tuned, bounded). No tuning of JEV beyond the threshold is described. Baselines QAA run from pinned upstream code; Gander, MoshiRAG and the Venus native harness also run (§5.1).

## Reference labels

Test cases authored by the authors (labels for the correct control operation); coded human_single. System benchmarks use official rewards (tau-Voice database state, FDB scoring with a shared judge). Task outcomes for replays.

## n, sampling, intervals

Table 6: 576 calls, 256 and 224 replays, no intervals for the controller comparison. Table 5 (race suite, 80 scripts x 3 runs) carries 95% bootstrap intervals clustered by template. Single run per condition otherwise.

## Test-set exposure

tau-Voice, FDB and ContextDialog are public benchmarks; the control-decision test cases are new and authored for this study (test_set_exposure new for Table 6).

## Cost and latency

Median JEV request 0.30 s vs 1.57 s (DeepSeek-V4-Flash) and 3.14 s (Gemini-3.5-Flash) (Table 6a); hardware or provider for JEV not stated in the text read. In recorded sessions the fast path starts speaking about 2.2 s after the user finishes (§4.3). No monetary cost reported.

## Calibration and cascade

No calibration metrics. JEV's confidence is used as a threshold (0.43 on dev) with a conservative ANSWER fallback at the 3.5 s deadline; this is a confidence-gated escalation (when JEV is unsure, no task changes and a worker answers or asks the user to clarify, §1). Results: 91.0% correct and confident within 1 s, 94.4% with fallback by 3.5 s.

## Robustness

Race suite with timing variants (Table 5), FDB-v3 by difficulty and disfluency (App. D). No option-order, language or cardinality tests of JEV itself; test cases are bilingual.

## Code and data

Code link and project page (https://amphionteam.github.io/Jarvis-Demo/); JEV is hosted by TypeSafe, Jev-Omni on Hugging Face (akhilaaa3/Jev-Omni).

## Own limitations

No dedicated limitations section in the extracted text. The paper notes that the proprietary tau-Voice leaderboard entries use different reasoning back ends (Figure 1 note) and that the Native Gate is trained on authored speech.
