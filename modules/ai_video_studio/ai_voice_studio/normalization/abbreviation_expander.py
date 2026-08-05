"""Abbreviation Expander — expands common abbreviations before synthesis."""
from __future__ import annotations

import re

ABBREVIATIONS: dict[str, str] = {
    "dr.": "doctor", "mrs.": "missus", "mr.": "mister", "ms.": "miss",
    "st.": "saint", "ave.": "avenue", "rd.": "road", "blvd.": "boulevard",
    "sq.": "square", "dept.": "department", "univ.": "university",
    "govt.": "government", "intl.": "international", "corp.": "corporation",
    "inc.": "incorporated", "ltd.": "limited", "co.": "company",
    "e.g.": "for example", "i.e.": "that is", "etc.": "etcetera",
    "vs.": "versus", "approx.": "approximately", "info": "information",
    "est.": "established", "jan.": "January", "feb.": "February",
    "aug.": "August", "sep.": "September", "sept.": "September",
    "oct.": "October", "nov.": "November", "dec.": "December",
    "mon.": "Monday", "tue.": "Tuesday", "tues.": "Tuesday",
    "wed.": "Wednesday", "thu.": "Thursday", "thur.": "Thursday",
    "fri.": "Friday", "sat.": "Saturday", "sun.": "Sunday",
    "kg.": "kilograms", "km.": "kilometers", "no.": "number",
}


def expand_abbreviations(text: str) -> str:
    """Replace known abbreviations (case-insensitive, word boundaries).

    Abbreviations ending in a period (``Dr.``) drop the trailing ``\b``
    because the period is already a non-word char — a boundary after it
    would sit between two non-word characters and never match.
    """
    for abbr, full in ABBREVIATIONS.items():
        tail = "" if abbr.endswith(".") else r"\b"
        text = re.sub(rf"\b{re.escape(abbr)}{tail}", full, text, flags=re.IGNORECASE)
    return text
