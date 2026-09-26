"""Rutgers University (School of Engineering) AP credit scraper.

Columns: AP EXAM, SCORE, RUTGERS COURSE(S) GRANTED, TOTAL CREDITS. Rutgers only
awards credit for scores of 4 or 5, encoded as "4,5". Rutgers course codes look
like ``01:640:151``.
"""

from __future__ import annotations

import re

from ..models import Equivalency
from ..normalize import extract_courses, parse_scores
from .base import BaseScraper

_NO_CREDIT = ("no credit", "see ", "n/a", "upper level", "general elective", "elective credit")


def _first_number(text: str) -> float | None:
    m = re.search(r"\d+(?:\.\d+)?", text or "")
    return float(m.group()) if m else None


class RutgersScraper(BaseScraper):
    code = "RU"
    name = "Rutgers University (School of Engineering)"
    url = "https://soe.rutgers.edu/AP"

    def parse(self, html: str) -> list[Equivalency]:
        soup = self.soup(html)
        target = None
        for table in soup.find_all("table"):
            header = [c.get_text(" ", strip=True).lower() for c in table.find_all(["th", "td"])[:2]]
            if header and header[0].startswith("ap exam"):
                target = table
                break
        if target is None:
            raise ValueError("Rutgers: could not find the 'AP EXAM' table")

        out: list[Equivalency] = []
        for tr in target.find_all("tr")[1:]:
            cells = [c.get_text(" ", strip=True) for c in tr.find_all(["th", "td"])]
            if len(cells) < 4:
                continue
            exam, score_s, course, cred_s = cells[0], cells[1], cells[2], cells[3]
            scores = parse_scores(score_s)
            if not scores:
                continue
            low = course.lower()
            if any(m in low for m in _NO_CREDIT):
                continue
            credits = _first_number(cred_s)
            if credits == 0:
                continue
            courses = extract_courses(course)
            for score in scores:
                out.append(
                    self.make(
                        exam,
                        score,
                        course,
                        courses=courses,
                        credits=credits,
                    )
                )
        return out
