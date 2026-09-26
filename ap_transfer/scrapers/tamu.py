"""Texas A&M University AP credit scraper.

TAMU's AP table has columns: AP Examination, Required Score, Texas A&M
Course(s), Credit Hours. The exam name spans multiple score rows via a rowspan,
so continuation rows have only 3 cells and inherit the previous exam name.
"""

from __future__ import annotations

from ..models import Equivalency
import re

from ..normalize import extract_courses, extract_credits, parse_scores
from .base import BaseScraper


def _parse_hours(hours: str) -> float | None:
    """TAMU's Credit Hours column is often a bare number ("3") or "up to 3 hours"."""
    credits = extract_credits(hours)
    if credits is not None:
        return credits
    m = re.search(r"\d+(?:\.\d+)?", hours)
    return float(m.group()) if m else None


class TAMUScraper(BaseScraper):
    code = "TAMU"
    name = "Texas A&M University"
    url = "https://testing.tamu.edu/credits/index.html"

    def parse(self, html: str) -> list[Equivalency]:
        soup = self.soup(html)
        target = None
        for table in soup.find_all("table"):
            first = table.find(["th", "td"])
            if first and first.get_text(" ", strip=True).lower() == "ap examination":
                target = table
                break
        if target is None:
            raise ValueError("TAMU: could not find the 'AP Examination' table")

        out: list[Equivalency] = []
        current_exam = ""
        for tr in target.find_all("tr")[1:]:
            cells = [c.get_text(" ", strip=True) for c in tr.find_all(["th", "td"])]
            if len(cells) >= 4:
                current_exam, score_s, course, hours = cells[0], cells[1], cells[2], cells[3]
            elif len(cells) == 3:
                score_s, course, hours = cells[0], cells[1], cells[2]
            else:
                continue
            if not current_exam:
                continue
            scores = parse_scores(score_s)
            if not scores:
                continue
            score = scores[0]
            if not course or course.lower().startswith("no credit"):
                continue
            credits = _parse_hours(hours) or extract_credits(course)
            out.append(
                self.make(
                    current_exam,
                    score,
                    course,
                    courses=extract_courses(course),
                    credits=credits,
                )
            )
        return out
