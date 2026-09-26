"""University of Florida AP credit scraper.

UF publishes a wide-format table: one row per exam with a column for the award
at each score (3, 4, 5) plus a Gen Ed column.
"""

from __future__ import annotations

from ..models import Equivalency
from ..normalize import extract_courses, extract_credits
from .base import BaseScraper

_DEFAULT_CREDITS = {3: 3.0, 4: 6.0, 5: 6.0}  # per UF header note


class UFScraper(BaseScraper):
    code = "UF"
    name = "University of Florida"
    url = "https://catalog.ufl.edu/UGRD/academic-advising/exam-credit/"

    def parse(self, html: str) -> list[Equivalency]:
        soup = self.soup(html)
        target = None
        for table in soup.find_all("table"):
            header = [c.get_text(" ", strip=True) for c in table.find_all(["th", "td"])[:1]]
            if header and header[0].strip().lower() == "ap exam":
                target = table
                break
        if target is None:
            raise ValueError("UF: could not find the 'AP Exam' table")

        out: list[Equivalency] = []
        rows = target.find_all("tr")
        for tr in rows[1:]:  # skip header
            cells = [c.get_text(" ", strip=True) for c in tr.find_all(["th", "td"])]
            if len(cells) < 4 or not cells[0].strip():
                continue  # note row or malformed
            exam = cells[0]
            gen_ed = cells[4] if len(cells) > 4 else None
            for idx, score in ((1, 3), (2, 4), (3, 5)):
                award = cells[idx].strip()
                if not award or award.lower().startswith("no credit"):
                    continue
                courses = extract_courses(award)
                credits = extract_credits(award)
                if credits is None and courses:
                    credits = _DEFAULT_CREDITS.get(score)
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
