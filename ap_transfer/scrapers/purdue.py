"""Purdue University AP credit scraper."""

from __future__ import annotations

import re

from ..models import Equivalency
from ..normalize import extract_courses
from .base import BaseScraper
from .scores import expand_scores

# Purdue uses 5-digit course numbers and undistributed codes like AAS 1XUND / MA 15555.
_PURDUE_COURSE_RE = re.compile(
    r"\b([A-Z]{1,5}&?[A-Z]{0,4})\s?(\d{1,5}[A-Z]{0,4})\b"
)


def _purdue_courses(text: str) -> list[str]:
    text = text.replace(" and ", ", ")
    # densify "BIOL 11000 and 11100" / "BIOL 11000, 11100"
    text = re.sub(
        r"\b([A-Z&]{1,5})\s?(\d{3,5}[A-Z]*)((?:\s*,\s*\d{3,5}[A-Z]*)+)",
        lambda m: " ".join(
            [f"{m.group(1)} {m.group(2)}"]
            + [f"{m.group(1)} {n}" for n in re.findall(r"\d{3,5}[A-Z]*", m.group(3))]
        ),
        text,
    )
    found = extract_courses(text)
    if found:
        return found
    out: list[str] = []
    seen: set[str] = set()
    for subj, num in _PURDUE_COURSE_RE.findall(text):
        code = f"{subj} {num}"
        if code not in seen:
            seen.add(code)
            out.append(code)
    return out


class PurdueScraper(BaseScraper):
    code = "PU"
    name = "Purdue University"
    url = "https://admissions.purdue.edu/become-student/transfer/credit/ap/"

    def parse(self, html: str) -> list[Equivalency]:
        soup = self.soup(html)
        out: list[Equivalency] = []
        for table in soup.find_all("table"):
            header = [c.get_text(" ", strip=True) for c in (table.find("tr").find_all(["th", "td"]) if table.find("tr") else [])]
            if not header or "AP Exam Score" not in header[0]:
                continue
            exam = _exam_name(table)
            if not exam:
                continue
            for tr in table.find_all("tr")[1:]:
                cells = [c.get_text(" ", strip=True) for c in tr.find_all(["th", "td"])]
                if len(cells) < 2:
                    continue
                scores = expand_scores(cells[0])
                award = cells[1]
                if not scores or not award:
                    continue
                courses = _purdue_courses(award)
                # Heuristic credits: ~3 per concrete course unless undistributed-only.
                credits = float(3 * max(1, len(courses))) if courses else 3.0
                for score in scores:
                    out.append(
                        self.make(
                            exam,
                            score,
                            award,
                            courses=courses,
                            credits=credits,
                        )
                    )
        return out


def _exam_name(table) -> str:
    # Purdue wraps each exam in an accordion: button (title) + content (table).
    for parent in table.parents:
        classes = parent.get("class") or []
        if "purdue-accordion" in classes or "accordion" in classes:
            btn = parent.find("button")
            if btn:
                strong = btn.find("strong")
                text = (strong or btn).get_text(" ", strip=True)
                if text:
                    return text
        # Also accept a preceding heading/button as a sibling of an ancestor.
        prev = parent.find_previous(["button", "h2", "h3", "h4", "strong"])
        if prev:
            text = prev.get_text(" ", strip=True)
            if text and "AP Exam" not in text and len(text) < 80:
                return text
    return ""
