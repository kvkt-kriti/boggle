"""University of Illinois Urbana-Champaign AP credit scraper."""

from __future__ import annotations

import re

from ..models import Equivalency
from ..normalize import extract_courses, extract_credits
from .base import BaseScraper
from .scores import expand_scores, parse_hours_token

# UIUC publishes elective placeholders like "LAS 1 - -" / "ART 1--".
_UIUC_COURSE_RE = re.compile(
    r"\b([A-Z]{2,5})\s*(\d)\s*[-–—]+\s*[-–—]*\b|\b([A-Z]{2,5})\s+(\d{2,3})\b"
)


def _uiuc_courses(text: str) -> list[str]:
    courses = extract_courses(text.replace(" - -", "00").replace("--", "00"))
    if courses:
        return courses
    out: list[str] = []
    for m in _UIUC_COURSE_RE.finditer(text):
        if m.group(1):
            out.append(f"{m.group(1)} {m.group(2)}XX")
        else:
            out.append(f"{m.group(3)} {m.group(4)}")
    return out


class UIUCScraper(BaseScraper):
    code = "UIUC"
    name = "University of Illinois Urbana-Champaign"
    url = "https://citl.illinois.edu/advanced-placement-ap-credit-2025"

    def parse(self, html: str) -> list[Equivalency]:
        soup = self.soup(html)
        out: list[Equivalency] = []
        for table in soup.find_all("table"):
            header_cells = [c.get_text(" ", strip=True) for c in (table.find("tr").find_all(["th", "td"]) if table.find("tr") else [])]
            if not header_cells or header_cells[0] != "Score":
                continue
            exam = _exam_for_table(table)
            if not exam:
                continue
            for tr in table.find_all("tr")[1:]:
                cells = [c.get_text(" ", strip=True) for c in tr.find_all(["th", "td"])]
                if len(cells) < 3:
                    continue
                score_s, course, hours = cells[0], cells[1], cells[2]
                scores = expand_scores(score_s)
                if not scores or not course:
                    continue
                courses = _uiuc_courses(course)
                credits = parse_hours_token(hours) or extract_credits(hours)
                gen_ed = cells[3] if len(cells) > 3 and cells[3] not in {"", "-", "Not Applicable"} else None
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


def _exam_for_table(table) -> str:
    # Accordion title on the UIUC page.
    for parent in table.parents:
        title = parent.find(class_=re.compile(r"accordion-title"))
        if title:
            return title.get_text(" ", strip=True)
        # Sometimes the exam name is a preceding heading inside the card.
        heading = parent.find(["h2", "h3", "h4", "strong"])
        if heading:
            text = heading.get_text(" ", strip=True)
            if text and text.lower() not in {"score", "placement message", "course credited"}:
                return text
    return ""
