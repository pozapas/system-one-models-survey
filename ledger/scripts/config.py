"""Paths and frozen protocol constants for Session B (the survey and the literature).

Session B writes only under shared/census, shared/ledger, shared/references and
survey/. It reads shared/results/ and never writes to it.
"""
import os

PAPER4 = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SHARED = os.path.join(PAPER4, "shared")
SURVEY = os.path.join(PAPER4, "survey")

CENSUS = os.path.join(SHARED, "census")
LEDGER = os.path.join(SHARED, "ledger")
REFS = os.path.join(SHARED, "references")
RESULTS_RO = os.path.join(SHARED, "results")          # read-only for Session B

MANUSCRIPT = os.path.join(SURVEY, "manuscript")
FIGURES = os.path.join(SURVEY, "figures")
TABLES = os.path.join(SURVEY, "tables")
NOTES = os.path.join(SURVEY, "notes")

# The first cutoff was frozen on 2026-09-24 (ledger versions 1.0 and 1.1). The second sweep of
# version 1.2 moves the cutoff to 2026-10-28, as recorded in shared/ledger/PROTOCOL.md.
CUTOFF = "2026-10-28"
LEDGER_VERSION = "1.2"

MAILTO = "system-one-survey-refcheck@example.org"      # non-personal polite-pool address
