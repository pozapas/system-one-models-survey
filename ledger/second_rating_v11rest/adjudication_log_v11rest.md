# Adjudication of the second rating of the first-sweep studies

Source: Adjudication_v11rest_returned.xlsx. Every disagreement between the first rating and the second rating was decided by the author against the saved full text that the ledger extracted at the first cutoff. Rows whose final value equals the first rating are not listed.

## Rules

| rule | domain | decision | note |
|---|---|---|---|
| G6 | Version pinning and run dates | accept | Accept G6 for incomplete version names. Use high only when the saved source identifies an unresolved alias, latest, preview or free-tier tag. The preview examples follow this clause. Exact versions with run dates remain eligible for low without a mandatory hash. This preserves the earlier G1 decision. Rechecked RB008, RB015 and RB029. |

## Risk of bias

| id | study | domain | first | second | final | reason |
|---|---|---|---|---|---|---|
| RB002 | rafe2026calibrated | 2 | unclear | low | low | Retain low. The saved text describes the draw and weights. Section 4.3 gives the headline F1 interval [0.871, 0.936]. Source: Sections 3.3 and 4.3, Table 6. |
| RB003 | wu2026reflex | 1 | low | unclear | unclear | Retain unclear. Terminal-state success and stored RF-5C or BFCL answers are different reference types. Source: Abstract, Sections 4, 5.2 and 5.4. |
| RB004 | wu2026reflex | 2 | low | unclear | unclear | Retain unclear. The saved Table S14 leaves success intervals blank. The text also does not describe selection of the 100 tasks. Source: Section 4, Table S14. |
| RB006 | grey_laya | 4 | high | unclear | unclear | Retain unclear. The saved card reports unequal supervision, third-party Jev results and temperature fitting. It does not establish tuning on scored items. Source: Laya vs TypeSafe Jev, Honest Limits. |
| RB009 | grey_localllama_typed_decisions | 4 | low | unclear | unclear | Retain unclear. The specialists use the benchmark train split. Their configuration uses held-out training data and never test. Source: Specialist and generalist, Reproducing the specialist rows. The unequal supervision remains unclear under C2. |
| RB011 | zhang2026same | 1 | low | unclear | unclear | Retain unclear. The saved study describes existing ContractNLI annotations but does not report their production or adjudication. Source: Section 2, Limitations. C3 gives unclear without outside assumptions about the dataset. |
| RB012 | zhang2026same | 4 | low | high | high | Retain high. The saved text explicitly adds Sonnet, Haiku and Terra after inspection of earlier results. Fixed later configurations do not remove that model-selection step. Source: Sections 3.1 and 3.2, Limitations. Retain high under C2. Appendix N is absent from this copy. |
| RB013 | ma2026jevstar | 4 | high | unclear | unclear | Retain unclear. The separate 33-map summary excludes both development maps. It preserves all wins and increases the reported gain. The candidate catalogs and execution handling still differ. Source: Section 4.1, Table 3, Appendix E. Retain unclear, consistent with the earlier RB100 reading. |
| RB014 | ma2026jevstar | 5 | low | unclear | unclear | Retain unclear. Public scenarios enter through structured observations during live games. There is no stored answer key at this interface. Source: Sections 3.1 and 4.1. The derived-feature exposure anchor gives unclear. |
| RB015 | ibrahim2026evaluating | 3 | low | high | high | Retain high. The saved Table 5 identifies the comparator as gemini-3.1-pro-preview without resolving the preview tag further. Source: Appendix A.5, Table 5. Retain high under G6. The later Kev example is unnecessary for this decision. |
| RB016 | ibrahim2026evaluating | 4 | low | high | high | Retain high. The saved paper selects the per-task best LLM on the same test items. This alone meets C2. Source: Section 4.1. The first-pass configuration changes in Section 3.2 provide additional evaluation feedback. |
| RB018 | ren2026openjev | 1 | unclear | high | high | Retain high. Every test prefix receives its scenario ground truth. The calls are synthetic and the references precede the model decisions. Source: Section 4 Data, Appendix B. G5 gives high. |
| RB019 | dossantos2026calibrated | 1 | unclear | low | low | Retain low. Scenario hits are outcomes of harness actions. Severity and runtime counts need no external reference label. Source: Tables VI and VIII. Vendor calibration figures in Section VIII-B are contextual information. |
| RB020 | dossantos2026calibrated | 4 | low | high | high | Retain high. The reported re-test uses salvage and classification fixes chosen after failures on the same target. Source: Sections IX-C, IX-E and IX-H, Table VIII. The earlier matched setup does not remove this C2 trigger. |
| RB023 | grey_bespoke_nimble | 4 | high | unclear | unclear | Retain unclear. The 324 examples are frozen final evaluation data. Nimble receives training while comparison models run untuned with different precision. Source: README, Current dataset and Evaluation. Retain unclear under C2. |
| RB025 | guo2026just | 4 | unclear | high | high | Retain high. The saved text uses the in-sample best generic readout and selects a shared question on both evaluated states. Source: Sections 3.4 and 4.2, Figure 4. Split-half selection elsewhere does not remove these C2 triggers. |
| RB026 | guo2026just | 5 | high | unclear | unclear | Retain unclear. The evaluation mixes newly generated target-model responses with older public human-label sets. Source: Section 3.1. Retain unclear under the mixture rule. |
| RB029 | li2026replacing | 3 | low | unclear | unclear | Retain unclear. The saved appendix resolves Jev and pins Qwen, with a September 18 run date. DeepSeek remains an incomplete version name. Source: Appendix A-A. Retain unclear under G6 without assumptions about provider routing. |
| RB031 | li2026jevasajudge | 4 | low | unclear | high | Change unclear to high under C2. The saved text adds model families after earlier results were known and evaluates them on the same 1,312 items. This matches the model-selection trigger retained for RB012. Source: Section 3, What was frozen and when. Separate threshold-selection pairs do not remove that trigger. |
| RB032 | li2026jevasajudge | 5 | high | unclear | unclear | Retain unclear. The saved source mixes public benchmark items with 64 new synthetic evidence controls. Source: Section 3, Table 7. Retain unclear under C4. |
| RB033 | deng2026jev | 2 | high | unclear | unclear | Retain unclear. The saved text describes 20 Choices, ten cases, five repetitions and fifty planned requests per configuration. The received counts reconcile, but no headline interval appears. Source: Sections 2.1 and 2.3, Table 1, Appendix C. Retain unclear. |
| RB035 | deng2026jev | 5 | unclear | low | low | Retain low. The authors construct new Choices and claim targets from published scientific material. References stay outside model inputs. Source: Section 2.1, Appendix A.2. Public source literature alone does not make these verbatim benchmark items. Retain low under G3. |

## Extraction

| id | item | first | second | final | reason |
|---|---|---|---|---|---|
| EX01 | wu2026reflex item 4 | 0.95 | 95 | 0.95 | Retain 0.95. The saved Table 1 directly prints 0.95 in the Success column. Section 5.1 prints the same value as 95%. The ledger success_rate field uses a proportion. No conversion of the Table 1 value is necessary. |
