"""University of Washington (Seattle) AP credit scraper."""

from __future__ import annotations

from ..models import Equivalency
from ..normalize import extract_courses, extract_courses_titlecase
from .base import BaseScraper
from .scores import expand_scores, parse_hours_token


class UWASHScraper(BaseScraper):
    code = "UW"
    name = "University of Washington"
    url = "https://admit.washington.edu/apply/first-year/exams-for-credit/ap/"

    def parse(self, html: str) -> list[Equivalency]:
        soup = self.soup(html)
        out: list[Equivalency] = []
        for table in soup.find_all("table"):
            header = [c.get_text(" ", strip=True) for c in (table.find("tr").find_all(["th", "td"]) if table.find("tr") else [])]
            if not header or header[0] != "Name":
                continue
            for tr in table.find_all("tr")[1:]:
                cells = [c.get_text(" ", strip=True) for c in tr.find_all(["th", "td"])]
                if len(cells) < 4:
                    continue
                exam, score_s, course, hours = cells[0], cells[1], cells[2], cells[3]
                gen_ed = cells[4] if len(cells) > 4 else None
                scores = expand_scores(score_s)
                if not scores or not exam:
                    continue
                courses = extract_courses(course) or extract_courses_titlecase(course)
                # "BIOL 161, 162" style with shared subject already densified by extract_courses.
                if not courses and course:
                    # Keep multi-word department names like "Arabic 201".
                    courses = extract_courses_titlecase(course.replace(",", " "))
                credits = parse_hours_token(hours)
                for score in scores:
                    out.append(
                        self.make(
                            exam,
                            score,
                            course,
                            courses=courses,
                            credits=credits,
                            gen_ed=gen_ed,
                        )
                    )
        return out
