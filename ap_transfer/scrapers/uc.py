"""University of California campus AP credit scrapers.

UC Admissions publishes a prose summary per campus (not HTML tables). We split
that prose on known AP exam titles and extract score → unit/course awards.
Policies can differ by college within a campus; we keep the first/default award
described for each exam+score (typically Letters & Science / non-Engineering).
"""

from __future__ import annotations

import re

from ..models import Equivalency
from ..normalize import extract_courses, extract_credits, normalize_exam
from .base import BaseScraper
from .scores import expand_scores

# Longest-first so "Calculus BC" wins over "Calculus".
_EXAM_ALIASES: list[tuple[str, str]] = sorted(
    [
        ("Mathematics – Calculus BC", "Calculus BC"),
        ("Mathematics - Calculus BC", "Calculus BC"),
        ("Mathematics – Calculus AB", "Calculus AB"),
        ("Mathematics - Calculus AB", "Calculus AB"),
        ("Calculus BC", "Calculus BC"),
        ("Calculus AB", "Calculus AB"),
        ("Computer Science Principles", "Computer Science Principles"),
        ("Computer Science A", "Computer Science A"),
        ("Computer Science AB", "Computer Science A"),
        ("English Language and Composition", "English Language and Composition"),
        ("English Literature and Composition", "English Literature and Composition"),
        ("Government and Politics – Comparative", "Comparative Government and Politics"),
        ("Government and Politics - Comparative", "Comparative Government and Politics"),
        ("Government and Politics – United States", "US Government and Politics"),
        ("Government and Politics - United States", "US Government and Politics"),
        ("History – European", "European History"),
        ("History - European", "European History"),
        ("History – United States", "US History"),
        ("History - United States", "US History"),
        ("History – World", "World History"),
        ("History - World", "World History"),
        ("Art History", "Art History"),
        ("Art (Studio)", "Studio Art: 2-D Design"),
        ("Biology", "Biology"),
        ("Chemistry", "Chemistry"),
        ("Economics Microeconomics", "Microeconomics"),
        ("Economics Macroeconomics", "Macroeconomics"),
        ("Macroeconomics", "Macroeconomics"),
        ("Microeconomics", "Microeconomics"),
        ("Environmental Science", "Environmental Science"),
        ("French Language", "French Language and Culture"),
        ("French Literature", "French Language and Culture"),
        ("German Language", "German Language and Culture"),
        ("Human Geography", "Human Geography"),
        ("Italian Language and Culture", "Italian Language and Culture"),
        ("Japanese Language and Culture", "Japanese Language and Culture"),
        ("Chinese Language and Literature", "Chinese Language and Culture"),
        ("Chinese Language and Culture", "Chinese Language and Culture"),
        ("Latin", "Latin"),
        ("Music Theory", "Music Theory"),
        ("Physics C: Electricity and Magnetism", "Physics C: Electricity & Magnetism"),
        ("Physics C: Mechanics", "Physics C: Mechanics"),
        ("Physics C, both tests", "Physics C: Mechanics"),
        ("Physics 1", "Physics 1"),
        ("Physics 2", "Physics 2"),
        ("Physics", "Physics 1"),
        ("Psychology", "Psychology"),
        ("Spanish Language", "Spanish Language and Culture"),
        ("Spanish Literature", "Spanish Literature and Culture"),
        ("Statistics", "Statistics"),
        ("Precalculus", "Precalculus"),
        ("African American Studies", "African American Studies"),
        ("History United States", "US History"),
        ("History European", "European History"),
        ("History World", "World History"),
        ("English Language & Composition", "English Language and Composition"),
        ("English Literature & Composition", "English Literature and Composition"),
        ("English", "English Language and Composition"),
        ("Seminar", "Seminar"),
        ("Research", "Research"),
    ],
    key=lambda kv: len(kv[0]),
    reverse=True,
)

_SCORE_AWARD = re.compile(
    r"(?:a\s+)?score(?:s)?\s+of\s+([1-5](?:\s*(?:[-–—,orand\s]+)\s*[1-5])*)"
    r"[^.;]{0,60}?(?:earns?\s+(?:course\s+equivalency\s+)?(?:credit\s+)?(?:for\s+)?"
    r"|exempt(?:s)?\s+|satisfies\s+)"
    r"([^.;]+)",
    re.I,
)
_BARE_CREDIT = re.compile(
    r"(?:Credit\s+for|earns?\s+course\s+equivalency\s+(?:credit\s+)?for)\s+([^.;]+?)(?:\.|$)",
    re.I,
)
_UNITS = re.compile(r"\((\d+(?:\.\d+)?)\s*units?\)", re.I)

# Also capture "Microeconomics earns course equivalency for Economics (ECN) 001A"
_EARNS_EQUIV = re.compile(
    r"earns?\s+course\s+equivalency\s+(?:credit\s+)?for\s+([^.;]+)",
    re.I,
)


def _split_sections(blob: str) -> list[tuple[str, str]]:
    """Return (canonical_exam, section_text) pairs from a UC prose blob."""
    matches: list[tuple[int, str, str]] = []
    for alias, canonical in _EXAM_ALIASES:
        for m in re.finditer(re.escape(alias), blob):
            matches.append((m.start(), canonical, alias))
    matches.sort(key=lambda t: t[0])
    # Dedupe overlapping starts (keep longest alias already ordered by find).
    cleaned: list[tuple[int, str]] = []
    used_spans: list[tuple[int, int]] = []
    for start, canonical, alias in matches:
        end = start + len(alias)
        if any(start < e and end > s for s, e in used_spans):
            continue
        used_spans.append((start, end))
        cleaned.append((start, canonical))
    cleaned.sort(key=lambda t: t[0])
    sections: list[tuple[str, str]] = []
    for i, (start, canonical) in enumerate(cleaned):
        stop = cleaned[i + 1][0] if i + 1 < len(cleaned) else len(blob)
        sections.append((canonical, blob[start:stop]))
    return sections


def _awards_from_section(section: str) -> list[tuple[list[int], str, list[str], float | None]]:
    """Return list of (scores, award_raw, courses, credits)."""
    # Prefer non-Engineering paragraphs when both are present.
    preferred = section
    for marker in (
        "School of Engineering and Applied Science:",
        "College of Engineering:",
        "Engineering:",
    ):
        if marker in section:
            preferred = section.split(marker)[0]
            break

    found: list[tuple[list[int], str, list[str], float | None]] = []
    for m in _SCORE_AWARD.finditer(preferred):
        scores = expand_scores(m.group(1))
        award = m.group(2).strip()
        units = _UNITS.search(award)
        credits = float(units.group(1)) if units else extract_credits(award)
        if credits is None:
            credits = 4.0  # UC quarter-unit default when unstated
        courses = extract_courses(award)
        if scores:
            found.append((scores, award, courses, credits))
    if found:
        return found
    m = _BARE_CREDIT.search(preferred) or _EARNS_EQUIV.search(preferred)
    if m:
        award = m.group(1).strip()
        units = _UNITS.search(award) or _UNITS.search(preferred)
        credits = float(units.group(1)) if units else 8.0
        return [([3, 4, 5], award, extract_courses(award), credits)]
    # "exempt COURSE" with an earlier score mention in the section
    m2 = re.search(
        r"score\s+of\s+([1-5](?:\s*(?:[-–—,orand\s]+)\s*[1-5])*).{0,40}?exempt\s+([^.;]+)",
        preferred,
        re.I,
    )
    if m2:
        scores = expand_scores(m2.group(1))
        award = m2.group(2).strip()
        return [(scores or [3, 4, 5], award, extract_courses(award), 4.0)]
    return []


class UCCampusScraper(BaseScraper):
    """Base for UC campus prose pages on admission.universityofcalifornia.edu."""

    slug: str = ""

    @property
    def url(self) -> str:  # type: ignore[override]
        return (
            "https://admission.universityofcalifornia.edu/admission-requirements/"
            f"ap-exam-credits/ap-credits/{self.slug}.html"
        )

    def parse(self, html: str) -> list[Equivalency]:
        soup = self.soup(html)
        blobs = [
            p.get_text(" ", strip=True)
            for p in soup.find_all("p")
            if "Credit" in p.get_text() or "score" in p.get_text().lower()
        ]
        blob = " ".join(blobs)
        if len(blob) < 200:
            blob = soup.get_text(" ", strip=True)
        out: list[Equivalency] = []
        for exam, section in _split_sections(blob):
            for scores, award, courses, credits in _awards_from_section(section):
                for score in scores:
                    out.append(
                        self.make(
                            exam,
                            score,
                            award,
                            courses=courses,
                            credits=credits,
                            normalized=normalize_exam(exam),
                        )
                    )
        return out


class UCBScraper(UCCampusScraper):
    code = "UCB"
    name = "University of California, Berkeley"
    slug = "berkeley"


class UCLAScraper(UCCampusScraper):
    code = "UCLA"
    name = "University of California, Los Angeles"
    slug = "ucla"


class UCSDScraper(UCCampusScraper):
    code = "UCSD"
    name = "University of California, San Diego"
    slug = "san-diego"


class UCDScraper(UCCampusScraper):
    code = "UCD"
    name = "University of California, Davis"
    slug = "davis"


class UCIScraper(UCCampusScraper):
    code = "UCI"
    name = "University of California, Irvine"
    slug = "irvine"


class UCSBScraper(UCCampusScraper):
    code = "UCSB"
    name = "University of California, Santa Barbara"
    slug = "santa-barbara"
