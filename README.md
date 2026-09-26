# System One models: census, evidence ledger, harness and results

This repository accompanies two manuscripts by Amir Rafe and Subasish Das (Texas State University):

- *From Calibrated Classifiers to Decision Contracts: A Survey of System One Models* (the survey), and
- *Six Decision Models, One Harness: Benchmarking System One Models on Accuracy, Calibration, Cardinality and Option Naming* (the benchmark paper).

A typed probabilistic decision model maps a state and a caller-declared typed question to a probability distribution over a finite answer space, without generating text.

## Contents

| Folder | What it holds |
|---|---|
| `census/` | One YAML decision-model card per implementation (closed and open), plus datasets and harnesses. Every field has a source URL and an access date |
| `ledger/` | The evidence ledger (`ledger.csv`), its schema and protocol, the risk-of-bias ratings (`rob.csv`) and the pooled synthesis (`synthesis.json`) |
| `harness/` | The same-harness evaluation code of the benchmark paper |
| `results/` | Per-analysis result files and `numbers.json`, from which every number in both manuscripts is generated |

## Cutoff and versioning

The literature and ecosystem cutoff is **2026-09-24**. The census and ledger in this repository at tag `v1.0` are the versions the manuscripts describe. Later additions are released as new minor versions (`v1.1`, `v1.2`, and so on), each with its own cutoff date recorded in `ledger/PROTOCOL.md` and in a changelog entry. Rows are never edited in place. A correction is a new row that supersedes an old one and carries its identifier. Model cards record the exact model revision (commit SHA or version string) that they describe.
