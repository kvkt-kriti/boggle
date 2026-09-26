"""University of Minnesota (Twin Cities) AP credit scraper.

Columns: Area/Test, Score, Award, Liberal Education Award. The exam name spans
multiple score rows (blank Area/Test on continuation rows). Award text is
title-cased, e.g. "4 credits in Math 1271 (Calculus I)".
"""

from __future__ import annotations

from ..models import Equivalency
from ..normalize import extract_courses_titlecase, extract_credits, parse_scores
from .base import BaseScraper


class UMNScraper(BaseScraper):
    code = "UMN"
    name = "University of Minnesota (Twin Cities)"
    url = "https://admissions.tc.umn.edu/advanced-placement-course-awards"

    def parse(self, html: str) -> list[Equivalency]:
        soup = self.soup(html)
        target = None
        for table in soup.find_all("table"):
            first = table.find(["th", "td"])
            if first and first.get_text(" ", strip=True).lower().startswith("area"):
                target = table
                break
        if target is None:
            raise ValueError("UMN: could not find the 'Area/Test' table")

        out: list[Equivalency] = []
        current_exam = ""
        for tr in target.find_all("tr")[1:]:
            cells = [c.get_text(" ", strip=True) for c in tr.find_all(["th", "td"])]
            if len(cells) < 3:
                continue
            exam = cells[0].strip() or current_exam
            current_exam = exam
            score_s, award = cells[1].strip(), cells[2].strip()
            gen_ed = cells[3].strip() if len(cells) > 3 else None
            if not award or award.lower().startswith("no credit"):
                continue
            # Rows keyed on an "AB subscore" condition are conditional awards that
            # belong to Calculus AB, not to the exam in this row; skip them here.
            if "subscore" in score_s.lower():
                continue
            scores = [s for s in parse_scores(score_s) if s >= 3]
            if not scores:
                continue
            courses = extract_courses_titlecase(award)
            credits = extract_credits(award)
            for score in scores:
                out.append(
                    self.make(
                        exam,
                        score,
                        award,
                        courses=courses,
                        credits=credits,
                        gen_ed=gen_ed,
                    )
                )
        return out
