"""University of Georgia AP credit scraper.

UGA publishes one small table per exam (columns: AP Score, Credit Earned). Each
table is preceded by an ``<h4>`` heading naming the exam.
"""

from __future__ import annotations

import re

from ..models import Equivalency
from ..normalize import extract_courses, extract_credits
from .base import BaseScraper

# UGA awards look like "BIOL 1107 + BIOL 1107L (4 credit hours) and BIOL 1108 +
# BIOL 1108L (4 credit hours)". They also list 0-credit placement exemptions.
# We split on each "(N credit hours)" marker so every course in a credited
# segment is captured, sum the credit hours, and drop 0-credit exemptions.
_SPLIT_RE = re.compile(r"\((\d+)\s*credit[^)]*\)", re.I)


def _parse_award(award: str) -> tuple[list[str], float | None]:
    parts = _SPLIT_RE.split(award)
    if len(parts) < 3:  # no "(N credit hours)" markers
        return extract_courses(award), extract_credits(award)
    courses: list[str] = []
    seen: set[str] = set()
    total = 0
    # parts = [text0, cred0, text1, cred1, ..., tail]
    for i in range(0, len(parts) - 1, 2):
        segment_text = parts[i]
        credit = int(parts[i + 1])
        total += credit
        if credit <= 0:
            continue  # placement/exemption only
        for c in extract_courses(segment_text):
            if c not in seen:
                seen.add(c)
                courses.append(c)
    if not courses:  # everything was a 0-credit exemption; keep for context
        courses = extract_courses(award)
    return courses, float(total)


class UGAScraper(BaseScraper):
    code = "UGA"
    name = "University of Georgia"
    url = "https://reg.uga.edu/student-records/credit-from-testing/uga-ap-credit-equivalences/"

    def parse(self, html: str) -> list[Equivalency]:
        soup = self.soup(html)
        out: list[Equivalency] = []
        for table in soup.find_all("table"):
            header = [c.get_text(" ", strip=True).lower() for c in table.find_all(["th", "td"])[:2]]
            if len(header) < 2 or header[0] != "ap score":
                continue
            # At UGA each table appears immediately *before* its <h4> heading.
            heading = table.find_next("h4")
            exam = heading.get_text(" ", strip=True) if heading else ""
            if not exam:
                continue
            for tr in table.find_all("tr")[1:]:
                cells = [c.get_text(" ", strip=True) for c in tr.find_all(["th", "td"])]
                if len(cells) < 2:
                    continue
                try:
                    score = int(cells[0].strip())
                except ValueError:
                    continue
                award = cells[1].strip()
                if not award or award.lower().startswith("no credit"):
                    continue
                courses, credits = _parse_award(award)
                out.append(
                    self.make(
                        exam,
                        score,
                        award,
                        courses=courses,
                        credits=credits,
                    )
                )
        return out
