"""Georgia Institute of Technology AP credit scraper.

Georgia Tech's catalog table has columns: Subject, Course, Hours. The Course
cell encodes the score inline, e.g. "AP Score: 4 or 5 = MATH 1551". Language
exams use continuation rows whose Subject cell is blank.
"""

from __future__ import annotations

import re

from ..models import Equivalency
from ..normalize import extract_courses, parse_scores
from .base import BaseScraper

_SCORE_CLAUSE = re.compile(r"AP\s*Score[:\s]*([1-5](?:\s*(?:or|,|-|&|and)\s*[1-5])*)", re.I)


class GeorgiaTechScraper(BaseScraper):
    code = "GT"
    name = "Georgia Institute of Technology"
    url = "https://catalog.gatech.edu/academics/undergraduate/credit-tests-scores/advanced-placement-exams/"

    def parse(self, html: str) -> list[Equivalency]:
        soup = self.soup(html)
        target = None
        for table in soup.find_all("table"):
            first = table.find(["th", "td"])
            if first and first.get_text(" ", strip=True).lower() == "subject":
                target = table
                break
        if target is None:
            raise ValueError("GT: could not find the 'Subject' table")

        out: list[Equivalency] = []
        current_subject = ""
        for tr in target.find_all("tr")[1:]:
            cells = [c.get_text(" ", strip=True) for c in tr.find_all(["th", "td"])]
            if len(cells) < 2:
                continue
            subject = cells[0].strip() or current_subject
            current_subject = subject
            course_cell = cells[1].strip()
            hours_cell = cells[2].strip() if len(cells) > 2 else ""
            if not course_cell or "no credit" in course_cell.lower():
                continue
            m = _SCORE_CLAUSE.search(course_cell)
            if not m:
                continue
            scores = parse_scores(m.group(1))
            if not scores:
                continue
            # Course codes come after the score clause.
            remainder = course_cell[m.end():]
            courses = extract_courses(remainder) or extract_courses(course_cell)
            try:
                credits = float(re.sub(r"[^\d.]", "", hours_cell)) if hours_cell else None
            except ValueError:
                credits = None
            for score in scores:
                out.append(
                    self.make(
                        subject,
                        score,
                        course_cell,
                        courses=courses,
                        credits=credits,
                    )
                )
        return out
