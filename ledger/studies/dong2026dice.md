# dong2026dice — DICE: Tilting the Odds through Interface Attacks on System One Model

- arXiv: 2610.14404v2 [cs.CR], v2 dated 19 Oct 2026 (the HTML text is v2; first submission 9 Oct 2026 per the screening list). License CC BY-SA 4.0. Full text: fulltext/2610.14404.html and .txt (fetched 2026-10-28, v2). Ledger date set to 2026-10-09.
- Authors (header): Ben Dong, Zhonghao Guo, Qian Wang (University of California, Merced); Tianyi Lu (Stevens Institute of Technology). Affiliation type: academic.
- Code and data: no repository or data statement found in the text. code_available = no.

## Task and data
Security study of a Jev-based decision pipeline with three LLM adapters: state extraction E, question generation Q, output interpretation I, with Jev and the final decision rule protected (Section III-A, Figure 1). One adapter at a time is compromised with bounded substitutions (Table I). The attack success criterion requires the wrong final decision while Jev correctly answers the request it actually received (Eq. 2, Section IV-D). Three small synthetic studies (authored cases, not a benchmark):
- State: eligibility records, six prespecified denial targets among 12 originals; one extracted expiry advances, at most five days and five proposals per target; clean baseline 36 related representations (paraphrases and renewals, not independent) (Table I, Table III).
- Question: 12 authored domains with a failed policy prerequisite; a permission question becomes a denial-form question (Table I).
- Output: 12 records eligible earlier but ineligible after an update; the interpreter selects an authentic earlier answer (Table I).
- Cross-pillar transfer set: the same 36 actions under six rule structures, labels from "blinded-by-packet AI review, not human adjudication"; five exact-request repeat rounds (Section V-A, Table IV).
Reference labels: independently specified task decisions, authored by the researchers; coded synthetic.

## Decision model, versions
Jev jev-1.13.0, decision threshold 0.5, all pillars (Table II, Section V-A). Other stack components: DeepSeek Flash (question-equivalence check) and GPT-4.1 mini 2025-04-14 (question check, transfer labels) (Table II). Run dates not given.

## Comparators and tuning
No accuracy comparator. Checks compared: canonical question and direct output use without source check, source-state consistency check, semantic policy-equivalence check, explicit yes-to-approval check, response-byte authenticity, exact binding to the current request, corrected full-trace audit (Table V). Several checks were specified after defects in initial versions were found, so their clean results are not independent held-out confirmations (Section VII).

## Results (Tables III to V)
- State: Jev correct on 36/36 clean related representations and 6/6 selected target requests; 6/6 targets granted (wrong final decision).
- Question: 12/12 clean current-state requests correct; 11/12 denial-form requests correct; 11/12 wrong approvals from locally correct answers.
- Output: 12/12 current and 12/12 archived requests correct; 12/12 wrong current grants.
- Transfer: wrong decisions 36/36 for each pillar; repeats over five rounds: state 100% +- 0 pp, question 95.0% +- 4.6 pp (variation from one answer near the threshold), output 100% +- 0 pp (Table IV).
- Defenses (Table V): combined source-state check 0/6 wrong decisions allowed, 33/36 clean accepted; semantic policy-equivalence check 11/12 allowed, 10/12 clean accepted; explicit yes-to-approval check 0/12 allowed, 12/12 clean; response-byte authenticity 12/12 allowed; exact binding to current request 0/12; corrected full-trace audit 0/12.

## Intervals, calibration, cascade, cost
No confidence intervals except SD over five repeat rounds. Counts are not pooled across studies (Section V). No calibration analysis (a fixed 0.5 threshold is used), no cascade, no cost or latency.

## Test-set exposure
Authored synthetic cases; new.

## Limitations (paper)
Pilot demonstrates mechanisms and "does not estimate the prevalence of these failures in deployed systems" (Abstract); authored flip-capable tasks, small denominators, adapter boundary imposed by the experimental interface rather than process isolation (Section IV-E); source verification rejected some faithful clean extractions (33/36 accepted); defense clean controls partly not held out (Section VII).
