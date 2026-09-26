"""University of Michigan AP credit scraper.

The live admissions site often returns HTTP 403 to automated clients, so
:meth:`scrape` falls back to a recent Wayback Machine snapshot when needed.
"""

from __future__ import annotations

import re

from ..http import FetchError, fetch
from ..models import Equivalency, ScrapeResult
from ..normalize import extract_courses, extract_courses_titlecase, extract_credits
from .base import BaseScraper
from .scores import expand_scores, parse_hours_token

_WAYBACK = (
    "https://web.archive.org/web/2024/"
    "https://admissions.umich.edu/apply/first-year-applicants/ap-ib-credit/ap-guidelines"
)


class UMichScraper(BaseScraper):
    code = "UMICH"
    name = "University of Michigan"
    url = "https://admissions.umich.edu/apply/first-year-applicants/ap-ib-credit/ap-guidelines"

    def scrape(self) -> ScrapeResult:
        result = ScrapeResult(school=self.code, school_name=self.name, source_url=self.url)
        html = None
        try:
            html = fetch(self.url)
        except FetchError:
            try:
                html = fetch(_WAYBACK)
                result.source_url = _WAYBACK
            except FetchError as exc:
                result.error = str(exc)
                return result
        try:
            result.equivalencies = self.parse(html)
        except Exception as exc:  # noqa: BLE001
            result.error = f"parse error: {exc}"
        return result

    def parse(self, html: str) -> list[Equivalency]:
        soup = self.soup(html)
        out: list[Equivalency] = []
        current_exam = ""
        for table in soup.find_all("table"):
            header = [c.get_text(" ", strip=True) for c in (table.find("tr").find_all(["th", "td"]) if table.find("tr") else [])]
            if not header:
                continue
            head0 = header[0]
            if head0 not in {"A.P. Exam", "AP Exam"} and not (
                "Exam" in head0 and any("Score" in h for h in header)
            ):
                continue
            for tr in table.find_all("tr")[1:]:
                cells = [c.get_text(" ", strip=True) for c in tr.find_all(["th", "td"])]
                if len(cells) == 1:
                    # Section heading row naming the exam / subject group.
                    maybe = cells[0].strip()
                    if maybe and not maybe.lower().startswith("contact") and "does not" not in maybe.lower():
                        current_exam = maybe
                    continue
                if len(cells) < 3:
                    continue
                if len(cells) >= 4 and cells[0]:
                    current_exam = cells[0]
                    score_s, course, hours = cells[1], cells[2], cells[3]
                else:
                    # Continuation: blank exam cell.
                    score_s = cells[0] if not cells[0] or cells[0][0].isdigit() or "or" in cells[0] else cells[1]
                    # Normalize common shapes: ["", "4 or 5", "Course", "5", ...]
                    if cells[0] == "" and len(cells) >= 4:
                        score_s, course, hours = cells[1], cells[2], cells[3]
                    elif len(cells) >= 4:
                        score_s, course, hours = cells[1], cells[2], cells[3]
                    else:
                        score_s, course, hours = cells[0], cells[1], cells[2]
                if not current_exam:
                    continue
                scores = expand_scores(score_s)
                if not scores or not course:
                    continue
                if course.lower().startswith("contact"):
                    continue
                courses = extract_courses(course) or extract_courses_titlecase(course)
                # "Chemistry 125(1)/126(1) & Chemistry 130(3)" style
                if not courses:
                    courses = [
                        f"{a} {b}"
                        for a, b in re.findall(
                            r"([A-Za-z][A-Za-z ]+?)\s+(\d{2,4}[A-Za-z]?)", course
                        )
                    ]
                credits = parse_hours_token(re.sub(r"[*]+$", "", hours)) or extract_credits(course)
                for score in scores:
                    out.append(
                        self.make(
                            current_exam,
                            score,
                            course,
                            courses=courses,
                            credits=credits,
                        )
                    )
        return out
