"""Ohio State University AP credit scraper."""

from __future__ import annotations

import re

from ..models import Equivalency
from ..normalize import extract_courses, extract_courses_titlecase, extract_credits
from .base import BaseScraper
from .scores import expand_scores

_PAREN_HOURS = re.compile(r"\((\d+(?:\.\d+)?)\)")


class OSUScraper(BaseScraper):
    code = "OSU"
    name = "The Ohio State University"
    url = (
        "https://registrar.osu.edu/prior-learning-assessment/"
        "examination-credit/advanced-placement-ap/"
    )

    def parse(self, html: str) -> list[Equivalency]:
        soup = self.soup(html)
        target = None
        for table in soup.find_all("table"):
            first = table.find(["th", "td"])
            if first and "exam subject" in first.get_text(" ", strip=True).lower():
                target = table
                break
        if target is None:
            raise ValueError("OSU: could not find the Exam subject table")

        out: list[Equivalency] = []
        current_exam = ""
        for tr in target.find_all("tr")[1:]:
            cells = [c.get_text(" ", strip=True) for c in tr.find_all(["th", "td"])]
            if len(cells) >= 3:
                exam, score_s, award = cells[0], cells[1], cells[2]
                if exam:
                    current_exam = exam
            elif len(cells) == 2:
                score_s, award = cells[0], cells[1]
                exam = current_exam
            else:
                continue
            if not current_exam:
                continue
            scores = expand_scores(score_s)
            if not scores or not award:
                continue
            courses = extract_courses(award) or extract_courses_titlecase(award)
            hours = [float(h) for h in _PAREN_HOURS.findall(award)]
            credits = sum(hours) if hours else extract_credits(award)
            for score in scores:
                out.append(
                    self.make(
                        current_exam,
                        score,
                        award,
                        courses=courses,
                        credits=credits,
                    )
                )
        return out
