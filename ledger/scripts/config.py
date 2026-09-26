"""Paths and frozen protocol constants for the survey and the literature.

The survey writes only under shared/census, shared/ledger, shared/references and
survey/. It reads shared/results/ and never writes to it.
"""
import os

PAPER4 = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SHARED = os.path.join(PAPER4, "shared")
SURVEY = os.path.join(PAPER4, "survey")

CENSUS = os.path.join(SHARED, "census")
LEDGER = os.path.join(SHARED, "ledger")
REFS = os.path.join(SHARED, "references")
RESULTS_RO = os.path.join(SHARED, "results")          # read-only for the survey

MANUSCRIPT = os.path.join(SURVEY, "manuscript")
FIGURES = os.path.join(SURVEY, "figures")
TABLES = os.path.join(SURVEY, "tables")
NOTES = os.path.join(SURVEY, "notes")

# Frozen on 2026-09-24. A single Sunday re-sweep is allowed only as a
# versioned addendum (ledger v1.1), recorded in shared/ledger/PROTOCOL.md.
CUTOFF = "2026-09-24"
LEDGER_VERSION = "1.0"

MAILTO = "system-one-survey-refcheck@example.org"      # non-personal polite-pool address
