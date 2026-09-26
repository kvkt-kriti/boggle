"""Normalization helpers for AP exam names, course codes, and credits.

Universities name the same AP exam in many ways ("Calc BC", "Mathematics -
Calculus BC", "Calculus BC"). To compare across schools we map each published
name to a canonical College Board exam name.
"""

from __future__ import annotations

import re

# Canonical College Board AP exam names. Keys are matching aliases (already
# normalized by ``_slug``); values are the canonical display name.
_CANONICAL: dict[str, str] = {}


def _slug(text: str) -> str:
    """Lowercase, drop punctuation/footnotes, collapse whitespace."""
    t = text.lower()
    t = t.replace("&", " and ")
    t = re.sub(r"\(.*?\)", " ", t)  # drop parentheticals
    t = re.sub(r"[^a-z0-9]+", " ", t)  # punctuation -> space
    t = re.sub(r"\s+", " ", t).strip()
    return t


def _register(canonical: str, *aliases: str) -> None:
    _CANONICAL[_slug(canonical)] = canonical
    for a in aliases:
        _CANONICAL[_slug(a)] = canonical


# Order matters only for readability; lookup is exact-or-substring.
_register("Calculus AB", "calc ab", "mathematics calculus ab", "ap calculus ab")
_register("Calculus BC", "calc bc", "mathematics calculus bc", "ap calculus bc")
_register("Calculus BC/AB Subscore", "calculus ab subscore", "bc calculus ab subscore",
          "calc ab subscore", "ab subscore")
_register("Precalculus", "pre calculus", "mathematics precalculus")
_register("Statistics", "stats", "mathematics statistics")
_register("Biology", "bio")
_register("Chemistry", "chem")
_register("Physics 1", "physics 1 algebra based", "physics 1 algebra-based")
_register("Physics 2", "physics 2 algebra based", "physics 2 algebra-based")
_register("Physics C: Mechanics", "physics c mechanics", "physics c part i mechanics",
          "physics c part i")
_register("Physics C: Electricity & Magnetism", "physics c electricity and magnetism",
          "physics c e and m", "physics c part ii elect and magnetism",
          "physics c electricity magnetism", "physics c part ii")
_register("Environmental Science", "env science", "apes")
_register("Computer Science A", "comp sci a", "cs a")
_register("Computer Science Principles", "computer science principles", "cs principles",
          "computer science: principles")
_register("English Language and Composition", "english language and composition",
          "english language composition", "eng lang")
_register("English Literature and Composition", "english literature and composition",
          "english literature composition", "eng lit")
_register("Macroeconomics", "economics macroeconomics", "econ macro", "macro economics",
          "economics macro")
_register("Microeconomics", "economics microeconomics", "econ micro", "micro economics",
          "economics micro")
_register("Psychology", "psych")
_register("Human Geography", "geography human", "geog human")
_register("US Government and Politics", "united states government and politics",
          "government and politics u s", "government and politics us", "us gov",
          "gov and pol u s", "u s government and politics",
          "govt and pol u s", "govt and pol united states",
          "government and politics united states")
_register("Comparative Government and Politics", "government and politics comparative",
          "comparative government", "gov and pol comp", "comparative government and politics",
          "govt and pol comparative")
_register("US History", "united states history", "u s history", "us history",
          "united states american history")
_register("European History", "euro history")
_register("World History", "world history modern", "world history: modern")
_register("Art History")
_register("Studio Art: Drawing", "studio art drawing", "art drawing", "drawing")
_register("Studio Art: 2-D Design", "2 d art and design", "studio art 2 d design",
          "art 2 d art and design", "2d art and design")
_register("Studio Art: 3-D Design", "3 d art and design", "studio art 3 d design",
          "art 3 d art and design", "3d art and design")
_register("Music Theory", "music theory")
_register("Spanish Language and Culture", "spanish language", "spanish language and culture")
_register("Spanish Literature and Culture", "spanish literature", "spanish literature and culture")
_register("French Language and Culture", "french language", "french language and culture")
_register("German Language and Culture", "german language", "german language and culture")
_register("Italian Language and Culture", "italian language", "italian language and culture")
_register("Chinese Language and Culture", "chinese language", "chinese language and culture")
_register("Japanese Language and Culture", "japanese language", "japanese language and culture")
_register("Latin", "latin vergil", "latin literature")
_register("Seminar", "ap seminar", "capstone seminar")
_register("Research", "ap research", "capstone research")
_register("African American Studies", "african american studies")


def normalize_exam(raw: str) -> str:
    """Return the canonical AP exam name for a published exam string.

    Falls back to a cleaned title-cased version when no alias matches, so the
    pipeline never drops data just because an exam is not in the alias table.
    """
    raw = re.sub(r"\s+", " ", raw or "").strip()
    # strip leading "AP " and trailing footnote markers/asterisks
    cleaned = re.sub(r"^ap\s+", "", raw, flags=re.I)
    cleaned = re.sub(r"[\*\u2020\u2021]+$", "", cleaned).strip()
    cleaned = re.sub(r"\s+\d+$", "", cleaned)  # trailing footnote digit
    s = _slug(cleaned)
    if not s:
        return cleaned or raw
    if s in _CANONICAL:
        return _CANONICAL[s]
    # substring match against known aliases (longest alias wins)
    for alias in sorted(_CANONICAL, key=len, reverse=True):
        if alias and (alias in s or s in alias):
            return _CANONICAL[alias]
    return cleaned.title()


# Matches course codes like "MAC 2311", "BSC 2005L", "MATH 1551",
# "01:640:151" (Rutgers), "Math 1271", "HTS 1XXX".
_COURSE_RE = re.compile(
    r"""(?:
        \d{2}:\d{3}:\d{3}          # Rutgers 01:640:151
        |
        [A-Z]{2,5}\s?\d{3,4}[A-Za-z]?   # MAC 2311, BSC 2005L, ARTS 149
        |
        [A-Z]{2,5}\s?\d[A-Z]{2,4}\d?    # HTS 1XXX style blanket credit
    )""",
    re.VERBOSE,
)

_NO_CREDIT_MARKERS = (
    "no credit",
    "see academic advisor",
    "see advisor",
    "general elective",
    "elective credit",
    "upper level",
    "n/a",
    "na",
)


def _densify(text: str, subject_pattern: str) -> str:
    """Expand "MATH 151 and 152" into "MATH 151 MATH 152".

    Universities often list a subject once followed by several bare course
    numbers joined by commas / "and" / "&". This attaches the subject to each
    number so every course is captured, while leaving parentheticals like
    "(8 credits)" untouched.
    """
    pat = re.compile(
        rf"({subject_pattern})\s?(\d{{3,4}}[A-Za-z]?)"
        rf"((?:\s*(?:,|and|&)\s*\d{{2,4}}[A-Za-z]?)+)"
    )

    def repl(m: "re.Match[str]") -> str:
        subject, first, rest = m.group(1), m.group(2), m.group(3)
        nums = re.findall(r"\d{2,4}[A-Za-z]?", rest)
        return f"{subject} {first} " + " ".join(f"{subject} {n}" for n in nums)

    return pat.sub(repl, text)


def extract_courses(text: str) -> list[str]:
    """Best-effort extraction of course codes from an award string."""
    if not text:
        return []
    text = _densify(text, r"[A-Z]{2,5}")
    found = _COURSE_RE.findall(text)
    # normalize internal spacing ("MAC2311" -> "MAC 2311")
    out: list[str] = []
    seen: set[str] = set()
    for c in found:
        c = re.sub(r"([A-Z]{2,5})\s?(\d)", r"\1 \2", c).strip()
        if c not in seen:
            seen.add(c)
            out.append(c)
    return out


# Title-cased course names such as "Math 1271", "Art History 1001",
# "Computer Science 1XXX" (used by e.g. University of Minnesota).
_COURSE_TITLECASE_RE = re.compile(
    r"([A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+)*)\s+(\d[\dX]{2,3}[A-Za-z]?)"
)


def extract_courses_titlecase(text: str) -> list[str]:
    """Extract "Subject 1234" style course names (title-cased subjects)."""
    if not text:
        return []
    text = _densify(text, r"[A-Z][A-Za-z]+(?:\s[A-Z][A-Za-z]+)*")
    out: list[str] = []
    seen: set[str] = set()
    for subject, number in _COURSE_TITLECASE_RE.findall(text):
        code = f"{subject} {number}".strip()
        if code not in seen:
            seen.add(code)
            out.append(code)
    return out


def extract_credits(text: str) -> float | None:
    """Pull a credit-hour count from award text such as "(4 credits)"."""
    if not text:
        return None
    m = re.search(r"(\d+(?:\.\d+)?)\s*(?:credit|semester\s*hour|hour|hr)", text, re.I)
    if m:
        try:
            return float(m.group(1))
        except ValueError:
            return None
    return None


def is_no_credit(text: str) -> bool:
    t = _slug(text)
    if not t:
        return True
    return any(marker in t for marker in _NO_CREDIT_MARKERS) and not _COURSE_RE.search(text)


def parse_scores(text: str) -> list[int]:
    """Extract AP scores (3-5) from strings like "4,5" or "4 or 5" or "3"."""
    if not text:
        return []
    # Require the digit to stand alone (not part of a larger number like "52",
    # which appears when a footnote marker is glued to a score, e.g. "4,52").
    nums = [int(n) for n in re.findall(r"(?<!\d)([1-5])(?!\d)", text)]
    return sorted({n for n in nums if 1 <= n <= 5})
