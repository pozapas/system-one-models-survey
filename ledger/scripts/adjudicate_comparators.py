"""Adjudicated comparator classes: comparator_class.csv from the first coding plus the decisions below.

The first coding is comparator_class_first.csv and the blind recoding comparator_class_blind.csv; the ten lines
where they differ are settled here against the class definitions in PROTOCOL.md (version 1.2 section).
"""
import csv
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as K

DECISIONS = {
    ("r1Gap", "entityF1Selected"): ("task_trained", "the prompt was selected per benchmark on test data, and selection on the target counts as training"),
    ("r1Gap", "kevMmluPro"): ("task_trained", "a development set of the developer's own suite, used for selection"),
    ("r1Gap", "kevOod"): ("task_trained", "a development set of the developer's own suite, used for selection"),
    ("r1Gap", "revDecisionIndex"): ("task_trained", "the training pool covers the benchmark families the index draws on"),
    ("r1Gap", "rubrixQagsCnn"): ("task_trained", "RubriX is trained on rubric judging, the task of these benchmarks"),
    ("r1Gap", "rubrixQagsXsum"): ("task_trained", "RubriX is trained on rubric judging, the task of these benchmarks"),
    ("r1Gap", "rubrixSummEval"): ("task_trained", "RubriX is trained on rubric judging, the task of these benchmarks"),
    ("gapJevBest", "dingGap"): ("other_llm", "JET is a likelihood readout of an untuned pretrained LLM, not a typed decision model"),
    ("gapJevBest", "geuterGapHeldOut"): ("decision_model", "Jeff is scored zero-shot on held-out datasets outside its training data"),
    ("gapJevBest", "muLlmE1"): ("frontier_llm", "the paper calls deepseek-v4-pro the best frontier reasoning LLM"),
}


def main():
    rows = list(csv.DictReader(open(os.path.join(K.LEDGER, "comparator_class_first.csv"), encoding="utf-8-sig")))
    blind = {(r["analysis"], r["record"]): r["class"] for r in
             csv.DictReader(open(os.path.join(K.LEDGER, "comparator_class_blind.csv"), encoding="utf-8-sig"))}
    unsettled = []
    for r in rows:
        k = (r["analysis"], r["record"])
        if k in DECISIONS:
            r["class"], why = DECISIONS[k]
            r["reason"] = "Adjudicated: " + why
        elif blind.get(k) != r["class"]:
            unsettled.append(k)
    if unsettled:
        sys.exit(f"disagreements without a decision: {unsettled}")
    with open(os.path.join(K.LEDGER, "comparator_class.csv"), "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"comparator_class.csv: {len(rows)} lines, {len(DECISIONS)} adjudicated")


if __name__ == "__main__":
    main()
