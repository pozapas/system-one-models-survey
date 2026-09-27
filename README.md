# System One models: census, evidence ledger, harness and results

This repository accompanies two manuscripts by Amir Rafe and Subasish Das (Texas State University):

- *System One Decision Models: A Survey from Calibrated Classifiers to Decision Contracts* (the survey), and
- *Benchmarking System One decision models against trained classifiers and language models for automated decision gates* (the benchmark paper).

A typed probabilistic decision model maps a state and a caller-declared typed question to a probability distribution over a finite answer space, without generating text.

## Contents

| Folder | What it holds |
|---|---|
| `census/` | One YAML decision-model card per implementation (closed and open), plus datasets and harnesses. Every field has a source URL and an access date |
| `ledger/` | The evidence ledger (`ledger.csv`), its schema and protocol, the risk-of-bias ratings (`rob.csv`) and the pooled synthesis (`synthesis.json`) |
| `harness/` | The same-harness evaluation code of the benchmark paper |
| `results/` | Per-analysis result files and `numbers.json`, from which every number in both manuscripts is generated |

## Cutoff and versioning

The literature and ecosystem cutoff is **2026-09-24**. The manuscripts describe tag `v1.1`, which keeps that cutoff and adds the second rating and the benchmark revisions listed in `CHANGELOG.md`. Tag `v1.0` is the first release at the cutoff. Later sweeps are released as new minor versions, each with its own cutoff date recorded in `ledger/PROTOCOL.md` and in `CHANGELOG.md`. Ledger values are never edited in place. A correction is a new row that supersedes an old one and carries its identifier, and an adjudicated risk-of-bias rating records the adjudication in its reason. Model cards record the exact model revision (commit SHA or version string) that they describe.
