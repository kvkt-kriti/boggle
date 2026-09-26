"""University of Georgia AP credit scraper.

UGA publishes one small table per exam (columns: AP Score, Credit Earned). Each
table is preceded by an ``<h4>`` heading naming the exam.
"""

from __future__ import annotations

import re

from ..models import Equivalency
from ..normalize import extract_courses, extract_credits
from .base import BaseScraper

# Matches "MATH 2250 (4 credit hours)" pairs; UGA lists 0-credit placement
# exemptions alongside real credit, so we sum credits and drop 0-credit courses.
_PAIR_RE = re.compile(r"([A-Z]{2,5}\s?\d{3,4}[A-Za-z]?)\s*\((\d+)\s*credit", re.I)


def _parse_award(award: str) -> tuple[list[str], float | None]:
    pairs = _PAIR_RE.findall(award)
    if not pairs:
        return extract_courses(award), extract_credits(award)
    courses = [re.sub(r"([A-Z]{2,5})\s?(\d)", r"\1 \2", c).strip()
               for c, n in pairs if int(n) > 0]
    total = float(sum(int(n) for _, n in pairs))
    if not courses:  # all exemptions (0 credit); keep names for context
        courses = [re.sub(r"([A-Z]{2,5})\s?(\d)", r"\1 \2", c).strip() for c, _ in pairs]
    return courses, total


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
