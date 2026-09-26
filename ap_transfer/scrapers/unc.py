"""UNC–Chapel Hill AP credit scraper."""

from __future__ import annotations

from ..models import Equivalency
from ..normalize import extract_courses, extract_credits
from .base import BaseScraper
from .scores import expand_scores, parse_hours_token


class UNCScraper(BaseScraper):
    code = "UNC"
    name = "University of North Carolina at Chapel Hill"
    url = "https://catalog.unc.edu/policies-procedures/credit-evaluation/"

    def parse(self, html: str) -> list[Equivalency]:
        soup = self.soup(html)
        target = None
        for table in soup.find_all("table"):
            for tr in table.find_all("tr")[:3]:
                cells = [c.get_text(" ", strip=True) for c in tr.find_all(["th", "td"])]
                if cells and cells[0] == "Exam" and any("Score" in c for c in cells):
                    target = table
                    break
            if target:
                break
        if target is None:
            raise ValueError("UNC: could not find the AP Exam table")

        out: list[Equivalency] = []
        started = False
        for tr in target.find_all("tr"):
            cells = [c.get_text(" ", strip=True).replace("\xa0", " ") for c in tr.find_all(["th", "td"])]
            if not cells:
                continue
            if cells[0] == "Exam":
                started = True
                continue
            if not started or len(cells) < 3:
                continue
            exam, score_s, award = cells[0], cells[1], cells[2]
            hours = cells[3] if len(cells) > 3 else ""
            if not exam or exam.startswith("Column"):
                continue
            scores = expand_scores(score_s)
            if not scores:
                continue
            courses = extract_courses(award)
            credits = parse_hours_token(hours) or extract_credits(award) or extract_credits(hours)
            # Skip pure 0-credit placement rows unless they name a real course.
            if (credits is None or credits == 0) and not courses:
                if "elective" not in award.lower() and "general" not in award.lower():
                    continue
            for score in scores:
                out.append(
                    self.make(
                        exam,
                        score,
                        award,
                        courses=courses,
                        credits=credits if credits and credits > 0 else (credits or None),
                    )
                )
        return out
