"""UT Austin AP credit scraper.

UT publishes a searchable exam list; each AP exam row embeds a nested score table.
"""

from __future__ import annotations

from ..models import Equivalency
from ..normalize import extract_courses
from .base import BaseScraper
from .scores import expand_scores


class UTAustinScraper(BaseScraper):
    code = "UTA"
    name = "The University of Texas at Austin"
    url = "https://testingservices.utexas.edu/search-undergraduate-exams?type=ap"

    def parse(self, html: str) -> list[Equivalency]:
        soup = self.soup(html)
        out: list[Equivalency] = []
        # Walk every nested score table under an "AP Exam in …" label.
        for tr in soup.find_all("tr"):
            cells = tr.find_all(["th", "td"], recursive=False)
            if not cells:
                continue
            exam_label = cells[0].get_text(" ", strip=True)
            if not exam_label.startswith("AP Exam"):
                continue
            exam = exam_label.replace("AP Exam in ", "").replace("AP Exam ", "").strip()
            nested = tr.find("table")
            if not nested:
                continue
            for nrow in nested.find_all("tr")[1:]:
                ncells = [c.get_text(" ", strip=True) for c in nrow.find_all(["th", "td"])]
                if len(ncells) < 2:
                    continue
                course, score_s = ncells[0], ncells[1]
                if not course or course.lower().startswith("ut austin"):
                    continue
                scores = expand_scores(score_s)
                if not scores:
                    continue
                courses = extract_courses(course)
                # Estimate credits: ~3 per course code when not stated.
                credits = float(3 * len(courses)) if courses else 3.0
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
